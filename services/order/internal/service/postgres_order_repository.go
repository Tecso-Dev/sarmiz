package service

import (
	"context"
	"database/sql"
	"encoding/json"
	"errors"
	"fmt"
	"strings"
	"time"

	_ "github.com/jackc/pgx/v5/stdlib"

	"github.com/Tecso-Dev/sarmiz/services/order/internal/domain"
)

var ErrIdempotencyConflict = errors.New(
	"idempotency key was already used with a different request",
)

// PostgresOrderRepository stores orders in PostgreSQL.
type PostgresOrderRepository struct {
	db *sql.DB
}

func NewPostgresOrderRepository(db *sql.DB) *PostgresOrderRepository {
	return &PostgresOrderRepository{db: db}
}

func (r *PostgresOrderRepository) Create(
	ctx context.Context,
	order domain.Order,
	items []domain.OrderItem,
) (domain.Order, error) {
	tx, err := r.db.BeginTx(ctx, nil)
	if err != nil {
		return domain.Order{}, fmt.Errorf("begin order transaction: %w", err)
	}
	defer func() {
		_ = tx.Rollback()
	}()

	if key := strings.TrimSpace(order.IdempotencyKey); key != "" {
		// Serialize requests that use the same key for the same venue.
		lockKey := order.VenueID + ":" + key

		if _, err := tx.ExecContext(ctx, `
        SELECT pg_advisory_xact_lock(hashtextextended($1, 0))
    `, lockKey); err != nil {
			return domain.Order{}, fmt.Errorf("lock idempotency key: %w", err)
		}

		var existing domain.Order
		var existingHash string
		var createdAt time.Time

		err := tx.QueryRowContext(ctx, `
        SELECT
            id,
            venue_id,
            COALESCE(branch_id::TEXT, ''),
            COALESCE(table_id::TEXT, ''),
            COALESCE(table_label, ''),
            business_date,
            code,
            "type",
            status,
            payment_method,
            payment_status,
            subtotal_rial,
            total_rial,
            COALESCE(note, ''),
            COALESCE(locale, ''),
            created_at,
            updated_at,
            COALESCE(idempotency_request_hash, '')
        FROM orders
        WHERE venue_id = $1
          AND idempotency_key = $2
        FOR UPDATE
    `,
			order.VenueID,
			key,
		).Scan(
			&existing.ID,
			&existing.VenueID,
			&existing.BranchID,
			&existing.TableID,
			&existing.TableLabel,
			&existing.BusinessDate,
			&existing.Code,
			&existing.Type,
			&existing.Status,
			&existing.PaymentMethod,
			&existing.PaymentStatus,
			&existing.SubtotalRial,
			&existing.TotalRial,
			&existing.Note,
			&existing.Locale,
			&createdAt,
			&existing.UpdatedAt,
			&existingHash,
		)

		switch {
		case err == nil:
			if time.Since(createdAt) < 24*time.Hour {
				if existingHash != order.IdempotencyRequestHash {
					return domain.Order{}, ErrIdempotencyConflict
				}

				// Return the original order without creating another one.
				// The deferred rollback closes this read-only transaction.
				return existing, nil
			}

			// The key has expired. Release it within this transaction.
			_, err = tx.ExecContext(ctx, `
            UPDATE orders
            SET idempotency_key = NULL,
                idempotency_request_hash = NULL,
                updated_at = NOW()
            WHERE venue_id = $1
              AND id = $2
        `, order.VenueID, existing.ID)
			if err != nil {
				return domain.Order{}, fmt.Errorf("release expired idempotency key: %w", err)
			}

		case errors.Is(err, sql.ErrNoRows):
			// First use of this key; continue with normal order creation.

		default:
			return domain.Order{}, fmt.Errorf("check idempotency key: %w", err)
		}
	}

	// 1. Allocate a daily order number atomically for this venue.
	err = tx.QueryRowContext(ctx, `
		INSERT INTO daily_counters (venue_id, day, last_code)
		VALUES ($1, $2, 1)
		ON CONFLICT (venue_id, day)
		DO UPDATE SET
			last_code = daily_counters.last_code + 1,
			updated_at = NOW()
		RETURNING last_code
	`, order.VenueID, order.BusinessDate).Scan(&order.Code)
	if err != nil {
		return domain.Order{}, fmt.Errorf("allocate daily order code: %w", err)
	}

	// 2. Insert the order and retrieve its database-generated fields.
	err = tx.QueryRowContext(ctx, `
		INSERT INTO orders (
			venue_id,
			branch_id,
			table_id,
			table_label,
			business_date,
			code,
			"type",
			status,
			payment_method,
			payment_status,
			subtotal_rial,
			total_rial,
			note,
			locale,
			idempotency_key,
    		idempotency_request_hash
		)
		VALUES (
			$1,
			NULLIF($2, '')::UUID,
			NULLIF($3, '')::UUID,
			$4,
			$5,
			$6,
			$7,
			$8,
			$9,
			$10,
			$11,
			$12,
			$13,
			$14,
			NULLIF($15, ''),
			NULLIF($16, '')
		)
		RETURNING id, created_at, updated_at
	`,
		order.VenueID,
		order.BranchID,
		order.TableID,
		order.TableLabel,
		order.BusinessDate,
		order.Code,
		order.Type,
		order.Status,
		order.PaymentMethod,
		order.PaymentStatus,
		order.SubtotalRial,
		order.TotalRial,
		order.Note,
		order.Locale,
		order.IdempotencyKey,
		order.IdempotencyRequestHash,
	).Scan(&order.ID, &order.CreatedAt, &order.UpdatedAt)
	if err != nil {
		return domain.Order{}, fmt.Errorf("insert order: %w", err)
	}

	// 3. Insert all item snapshots.
	for _, item := range items {
		nameSnapshot, err := json.Marshal(item.NameSnapshot)
		if err != nil {
			return domain.Order{}, fmt.Errorf("marshal item name snapshot: %w", err)
		}

		optionsSnapshot := item.OptionsSnapshot
		if optionsSnapshot == nil {
			optionsSnapshot = map[string]any{}
		}

		optionsJSON, err := json.Marshal(optionsSnapshot)
		if err != nil {
			return domain.Order{}, fmt.Errorf("marshal item options snapshot: %w", err)
		}

		_, err = tx.ExecContext(ctx, `
			INSERT INTO order_items (
				order_id,
				venue_id,
				item_id,
				name_snapshot,
				unit_price_rial,
				quantity,
				options_snapshot,
				line_total_rial,
				note
			)
			VALUES (
				$1, $2, $3, $4::JSONB, $5, $6, $7::JSONB, $8, $9
			)
		`,
			order.ID,
			order.VenueID,
			item.ItemID,
			string(nameSnapshot),
			item.UnitPriceRial,
			item.Quantity,
			string(optionsJSON),
			item.LineTotalRial,
			item.Note,
		)
		if err != nil {
			return domain.Order{}, fmt.Errorf("insert order item: %w", err)
		}
	}

	// 4. Store an event in the transactional outbox.
	// Publishing to the message broker happens separately.
	eventPayload := struct {
		OrderID       string               `json:"order_id"`
		VenueID       string               `json:"venue_id"`
		Code          int64                `json:"code"`
		BusinessDate  string               `json:"business_date"`
		Status        domain.OrderStatus   `json:"status"`
		PaymentStatus domain.PaymentStatus `json:"payment_status"`
		TotalRial     int64                `json:"total_rial"`
	}{
		OrderID:       order.ID,
		VenueID:       order.VenueID,
		Code:          order.Code,
		BusinessDate:  order.BusinessDate.Format("2006-01-02"),
		Status:        order.Status,
		PaymentStatus: order.PaymentStatus,
		TotalRial:     order.TotalRial,
	}

	payloadJSON, err := json.Marshal(eventPayload)
	if err != nil {
		return domain.Order{}, fmt.Errorf("marshal order-created event: %w", err)
	}

	_, err = tx.ExecContext(ctx, `
		INSERT INTO outbox (venue_id, subject, payload)
		VALUES ($1, $2, $3::JSONB)
	`, order.VenueID, "order.created.v1", string(payloadJSON))
	if err != nil {
		return domain.Order{}, fmt.Errorf("insert outbox event: %w", err)
	}

	// 5. Commit only after the order, items and outbox event all succeed.
	if err := tx.Commit(); err != nil {
		return domain.Order{}, fmt.Errorf("commit order transaction: %w", err)
	}

	return order, nil
}
