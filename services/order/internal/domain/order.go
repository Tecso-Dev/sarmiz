package domain

import (
	"fmt"
	"time"
)

type OrderType string

const (
	OrderTypeDineIn   OrderType = "dine_in"
	OrderTypePickup   OrderType = "pickup"
	OrderTypeDelivery OrderType = "delivery"
)

type OrderStatus string

const (
	OrderStatusAwaitingPayment OrderStatus = "awaiting_payment"
	OrderStatusPending         OrderStatus = "pending"
	OrderStatusAccepted        OrderStatus = "accepted"
	OrderStatusPreparing       OrderStatus = "preparing"
	OrderStatusReady           OrderStatus = "ready"
	OrderStatusServed          OrderStatus = "served"
	OrderStatusCancelled       OrderStatus = "cancelled"
)

type PaymentMethod string

const (
	PaymentMethodOnline  PaymentMethod = "online"
	PaymentMethodCounter PaymentMethod = "counter"
)

type PaymentStatus string

const (
	PaymentStatusUnpaid   PaymentStatus = "unpaid"
	PaymentStatusPending  PaymentStatus = "pending"
	PaymentStatusPaid     PaymentStatus = "paid"
	PaymentStatusFailed   PaymentStatus = "failed"
	PaymentStatusRefunded PaymentStatus = "refunded"
)

type Order struct {
	ID         string
	VenueID    string
	BranchID   string
	TableID    string
	TableLabel string

	BusinessDate time.Time
	Code         int64

	Type          OrderType
	Status        OrderStatus
	PaymentMethod PaymentMethod
	PaymentStatus PaymentStatus

	SubtotalRial int64
	TotalRial    int64

	Note   string
	Locale string

	CreatedAt time.Time
	UpdatedAt time.Time

	IdempotencyKey         string
	IdempotencyRequestHash string
}
type OrderItem struct {
	ID      string
	OrderID string
	VenueID string
	ItemID  string

	NameSnapshot    map[string]string
	UnitPriceRial   int64
	Quantity        int32
	OptionsSnapshot map[string]any
	LineTotalRial   int64

	Note string
}

func (i OrderItem) Validate() error {
	if i.ItemID == "" {
		return fmt.Errorf("item ID is required")
	}

	if i.Quantity <= 0 {
		return fmt.Errorf("quantity must be greater than zero")
	}

	if i.UnitPriceRial < 0 {
		return fmt.Errorf("unit price cannot be negative")
	}

	if i.LineTotalRial < 0 {
		return fmt.Errorf("line total cannot be negative")
	}

	if i.LineTotalRial != i.UnitPriceRial*int64(i.Quantity) {
		return fmt.Errorf("line total does not match unit price and quantity")
	}

	if i.NameSnapshot["fa"] == "" {
		return fmt.Errorf("Persian item name is required")
	}

	return nil
}
