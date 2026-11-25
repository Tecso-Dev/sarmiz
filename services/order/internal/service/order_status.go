package service

import (
	"fmt"

	"github.com/Tecso-Dev/sarmiz/services/order/internal/model"
)

func ChangeOrderStatus(o *model.Order, next model.OrderStatus) error {
	if o == nil {
		return fmt.Errorf("order is nil")
	}
	if !isKnownOrderStatus(o.Status) {
		return fmt.Errorf("unknown current order status: %s", o.Status)
	}
	if !isKnownOrderStatus(next) {
		return fmt.Errorf("unknown next order status: %s", next)
	}
	if o.Status == next {
		return fmt.Errorf("order is already in status %s", o.Status)
	}

	allowed := map[model.OrderStatus]map[model.OrderStatus]bool{
		model.OrderStatusAwaitingPayment: {
			model.OrderStatusPending:   true,
			model.OrderStatusCancelled: true,
		},
		model.OrderStatusPending: {
			model.OrderStatusAccepted:  true,
			model.OrderStatusCancelled: true,
		},
		model.OrderStatusAccepted: {
			model.OrderStatusPreparing: true,
			model.OrderStatusCancelled: true,
		},
		model.OrderStatusPreparing: {
			model.OrderStatusReady: true,
		},
		model.OrderStatusReady: {
			model.OrderStatusServed: true,
		},
		model.OrderStatusServed:    {},
		model.OrderStatusCancelled: {},
	}

	if allowed[o.Status][next] {
		o.Status = next
		return nil
	}

	return fmt.Errorf("transition from %s to %s is not allowed", o.Status, next)
}

func isKnownOrderStatus(status model.OrderStatus) bool {
	switch status {
	case model.OrderStatusAwaitingPayment,
		model.OrderStatusPending,
		model.OrderStatusAccepted,
		model.OrderStatusPreparing,
		model.OrderStatusReady,
		model.OrderStatusServed,
		model.OrderStatusCancelled:
		return true
	default:
		return false
	}
}
