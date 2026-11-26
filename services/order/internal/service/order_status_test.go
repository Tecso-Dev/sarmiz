package service

import (
	"testing"

	"github.com/Tecso-Dev/sarmiz/services/order/internal/model"
)

func TestChangeOrderStatus_AllTransitions(t *testing.T) {
	statuses := []model.OrderStatus{
		model.OrderStatusAwaitingPayment,
		model.OrderStatusPending,
		model.OrderStatusAccepted,
		model.OrderStatusPreparing,
		model.OrderStatusReady,
		model.OrderStatusServed,
		model.OrderStatusCancelled,
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

	for _, current := range statuses {
		for _, next := range statuses {
			name := string(current) + "_to_" + string(next)

			t.Run(name, func(t *testing.T) {
				order := model.Order{Status: current}
				err := ChangeOrderStatus(&order, next)

				wantErr := !allowed[current][next] || current == next
				if (err != nil) != wantErr {
					t.Fatalf(
						"ChangeOrderStatus(%s -> %s) error = %v, wantErr %v",
						current, next, err, wantErr,
					)
				}

				wantStatus := current
				if !wantErr {
					wantStatus = next
				}

				if order.Status != wantStatus {
					t.Errorf("status = %s, want %s", order.Status, wantStatus)
				}
			})
		}
	}
}

func TestChangeOrderStatus_RejectsUnknownStatus(t *testing.T) {
	tests := []struct {
		name    string
		current model.OrderStatus
		next    model.OrderStatus
	}{
		{
			name:    "unknown current status",
			current: model.OrderStatus("mystery"),
			next:    model.OrderStatusPending,
		},
		{
			name:    "unknown next status",
			current: model.OrderStatusPending,
			next:    model.OrderStatus("mystery"),
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			order := model.Order{Status: tt.current}
			err := ChangeOrderStatus(&order, tt.next)
			if err == nil {
				t.Fatal("expected error for unknown status")
			}
			if order.Status != tt.current {
				t.Fatalf("status changed: got %s, want %s", order.Status, tt.current)
			}
		})
	}
}

func TestChangeOrderStatus_NilOrder(t *testing.T) {
	if err := ChangeOrderStatus(nil, model.OrderStatusPending); err == nil {
		t.Fatal("expected error for nil order")
	}
}
