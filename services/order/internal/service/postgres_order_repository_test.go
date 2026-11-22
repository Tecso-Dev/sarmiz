package service

import (
	"context"
	"database/sql"
	"os"
	"testing"
	"time"

	"github.com/Tecso-Dev/sarmiz/services/order/internal/domain"
)

func TestPostgresOrderRepository_Create(t *testing.T) {
	dsn := os.Getenv("TEST_DATABASE_URL")
	if dsn == "" {
		t.Skip("TEST_DATABASE_URL is not set; skipping PostgreSQL integration test")
	}

	db, err := sql.Open("pgx", dsn)
	if err != nil {
		t.Fatalf("open database: %v", err)
	}
	defer db.Close()

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := db.PingContext(ctx); err != nil {
		t.Fatalf("connect to PostgreSQL: %v", err)
	}

	repo := NewPostgresOrderRepository(db)

	// Use a dedicated test venue so the test does not touch real venue data.
	order := domain.Order{
		VenueID:       "11111111-1111-4111-8111-111111111111",
		BusinessDate:  time.Date(2026, 11, 22, 0, 0, 0, 0, time.UTC),
		Type:          domain.OrderTypeDineIn,
		Status:        domain.OrderStatusPending,
		PaymentMethod: domain.PaymentMethodCounter,
		PaymentStatus: domain.PaymentStatusUnpaid,
		SubtotalRial:  150000,
		TotalRial:     150000,
		Locale:        "fa",
	}

	items := []domain.OrderItem{
		{
			VenueID:         order.VenueID,
			ItemID:          "22222222-2222-4222-8222-222222222222",
			NameSnapshot:    map[string]string{"fa": "چای"},
			UnitPriceRial:   50000,
			Quantity:        3,
			OptionsSnapshot: map[string]any{},
			LineTotalRial:   150000,
		},
	}

	created, err := repo.Create(ctx, order, items)
	if err != nil {
		t.Fatalf("create order: %v", err)
	}

	if created.ID == "" {
		t.Fatal("expected PostgreSQL to return the order ID")
	}
	if created.Code <= 0 {
		t.Fatalf("expected a positive daily order code, got %d", created.Code)
	}
	if created.CreatedAt.IsZero() {
		t.Fatal("expected PostgreSQL to return created_at")
	}

	var itemCount int
	err = db.QueryRowContext(ctx, `
		SELECT COUNT(*)
		FROM order_items
		WHERE order_id = $1
	`, created.ID).Scan(&itemCount)
	if err != nil {
		t.Fatalf("count order items: %v", err)
	}
	if itemCount != len(items) {
		t.Fatalf("expected %d order items, got %d", len(items), itemCount)
	}

	var outboxCount int
	err = db.QueryRowContext(ctx, `
		SELECT COUNT(*)
		FROM outbox
		WHERE venue_id = $1
		  AND subject = $2
		  AND payload->>'order_id' = $3
	`, order.VenueID, "order.created.v1", created.ID).Scan(&outboxCount)
	if err != nil {
		t.Fatalf("count outbox events: %v", err)
	}
	if outboxCount != 1 {
		t.Fatalf("expected one outbox event for order %s, got %d", created.ID, outboxCount)
	}
}
