package service

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"strings"
	"time"

	"github.com/Tecso-Dev/sarmiz/services/order/internal/domain"
)

type CreateOrderItemInput struct {
	ItemID   string
	Quantity int32
	Note     string
}

type CreateOrderInput struct {
	VenueID       string
	BranchID      string
	TableID       string
	TableLabel    string
	Type          domain.OrderType
	PaymentMethod domain.PaymentMethod
	Note          string
	Locale        string

	IdempotencyKey string

	Items []CreateOrderItemInput
}

type CatalogItem struct {
	ID            string
	NameSnapshot  map[string]string
	UnitPriceRial int64
}

type Catalog interface {
	GetItems(
		ctx context.Context,
		venueID string,
		itemIDs []string,
	) (map[string]CatalogItem, error)
}

type OrderRepository interface {
	Create(
		ctx context.Context,
		order domain.Order,
		items []domain.OrderItem,
	) (domain.Order, error)
}

type CreateOrderService struct {
	catalog Catalog
	repo    OrderRepository
	now     func() time.Time
}

func NewCreateOrderService(
	catalog Catalog,
	repo OrderRepository,
) *CreateOrderService {
	return &CreateOrderService{
		catalog: catalog,
		repo:    repo,
		now:     time.Now,
	}
}

func hashCreateOrderRequest(input CreateOrderInput) (string, error) {
	type hashItem struct {
		ItemID   string `json:"item_id"`
		Quantity int32  `json:"quantity"`
		Note     string `json:"note"`
	}

	type hashRequest struct {
		VenueID       string     `json:"venue_id"`
		BranchID      string     `json:"branch_id"`
		TableID       string     `json:"table_id"`
		TableLabel    string     `json:"table_label"`
		Type          string     `json:"type"`
		PaymentMethod string     `json:"payment_method"`
		Note          string     `json:"note"`
		Locale        string     `json:"locale"`
		Items         []hashItem `json:"items"`
	}

	canonical := hashRequest{
		VenueID:       input.VenueID,
		BranchID:      input.BranchID,
		TableID:       input.TableID,
		TableLabel:    input.TableLabel,
		Type:          string(input.Type),
		PaymentMethod: string(input.PaymentMethod),
		Note:          input.Note,
		Locale:        input.Locale,
		Items:         make([]hashItem, 0, len(input.Items)),
	}

	for _, item := range input.Items {
		canonical.Items = append(canonical.Items, hashItem{
			ItemID:   item.ItemID,
			Quantity: item.Quantity,
			Note:     item.Note,
		})
	}

	data, err := json.Marshal(canonical)
	if err != nil {
		return "", fmt.Errorf("marshal idempotency request: %w", err)
	}

	sum := sha256.Sum256(data)
	return hex.EncodeToString(sum[:]), nil
}

func (s *CreateOrderService) Create(
	ctx context.Context,
	input CreateOrderInput,
) (domain.Order, error) {
	if input.VenueID == "" {
		return domain.Order{}, fmt.Errorf("venue ID is required")
	}

	if len(input.Items) == 0 {
		return domain.Order{}, fmt.Errorf("order must contain at least one item")
	}

	if input.Type != domain.OrderTypeDineIn &&
		input.Type != domain.OrderTypePickup &&
		input.Type != domain.OrderTypeDelivery {
		return domain.Order{}, fmt.Errorf("invalid order type")
	}

	if input.PaymentMethod != domain.PaymentMethodOnline &&
		input.PaymentMethod != domain.PaymentMethodCounter {
		return domain.Order{}, fmt.Errorf("invalid payment method")
	}

	itemIDs := make([]string, 0, len(input.Items))
	seen := make(map[string]bool, len(input.Items))

	for _, item := range input.Items {
		if item.ItemID == "" {
			return domain.Order{}, fmt.Errorf("item ID is required")
		}
		if item.Quantity <= 0 {
			return domain.Order{}, fmt.Errorf("quantity must be greater than zero")
		}
		if seen[item.ItemID] {
			return domain.Order{}, fmt.Errorf("duplicate item ID: %s", item.ItemID)
		}

		seen[item.ItemID] = true
		itemIDs = append(itemIDs, item.ItemID)
	}
	now := s.now()

	tehran, err := time.LoadLocation("Asia/Tehran")
	if err != nil {
		return domain.Order{}, fmt.Errorf("load Tehran timezone: %w", err)
	}

	businessDate := now.In(tehran)

	order := domain.Order{
		VenueID:    input.VenueID,
		BranchID:   input.BranchID,
		TableID:    input.TableID,
		TableLabel: input.TableLabel,
		BusinessDate: time.Date(
			businessDate.Year(),
			businessDate.Month(),
			businessDate.Day(),
			0, 0, 0, 0, tehran,
		),
		Type:          input.Type,
		PaymentMethod: input.PaymentMethod,
		PaymentStatus: domain.PaymentStatusUnpaid,
		Status:        domain.OrderStatusPending,
		Note:          input.Note,
		Locale:        input.Locale,
		CreatedAt:     now,
		UpdatedAt:     now,
	}

	idempotencyKey := strings.TrimSpace(input.IdempotencyKey)

	if idempotencyKey != "" {
		requestHash, err := hashCreateOrderRequest(input)
		if err != nil {
			return domain.Order{}, err
		}

		order.IdempotencyKey = idempotencyKey
		order.IdempotencyRequestHash = requestHash
	}

	catalogItems, err := s.catalog.GetItems(ctx, input.VenueID, itemIDs)
	if err != nil {
		return domain.Order{}, fmt.Errorf("get catalog items: %w", err)
	}

	if input.PaymentMethod == domain.PaymentMethodOnline {
		order.Status = domain.OrderStatusAwaitingPayment
	}

	items := make([]domain.OrderItem, 0, len(input.Items))

	for _, requestedItem := range input.Items {
		catalogItem, exists := catalogItems[requestedItem.ItemID]
		if !exists {
			return domain.Order{}, fmt.Errorf(
				"catalog item not found: %s",
				requestedItem.ItemID,
			)
		}

		if catalogItem.UnitPriceRial < 0 {
			return domain.Order{}, fmt.Errorf("catalog returned a negative price")
		}

		if catalogItem.NameSnapshot["fa"] == "" {
			return domain.Order{}, fmt.Errorf(
				"catalog item %s has no Persian name",
				requestedItem.ItemID,
			)
		}

		quantity := int64(requestedItem.Quantity)
		if catalogItem.UnitPriceRial > 0 &&
			quantity > int64(^uint64(0)>>1)/catalogItem.UnitPriceRial {
			return domain.Order{}, fmt.Errorf("item total overflows int64")
		}

		lineTotal := catalogItem.UnitPriceRial * quantity

		item := domain.OrderItem{
			VenueID:       input.VenueID,
			ItemID:        catalogItem.ID,
			NameSnapshot:  catalogItem.NameSnapshot,
			UnitPriceRial: catalogItem.UnitPriceRial,
			Quantity:      requestedItem.Quantity,
			LineTotalRial: lineTotal,
			Note:          requestedItem.Note,
		}

		if err := item.Validate(); err != nil {
			return domain.Order{}, fmt.Errorf("validate item %s: %w", item.ItemID, err)
		}

		if order.SubtotalRial > int64(^uint64(0)>>1)-lineTotal {
			return domain.Order{}, fmt.Errorf("order total overflows int64")
		}

		order.SubtotalRial += lineTotal
		items = append(items, item)
	}

	order.TotalRial = order.SubtotalRial

	created, err := s.repo.Create(ctx, order, items)
	if err != nil {
		return domain.Order{}, fmt.Errorf("create order: %w", err)
	}

	return created, nil
}
