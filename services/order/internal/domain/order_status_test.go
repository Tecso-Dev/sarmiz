package domain

import "testing"

func TestChangeStatus(t *testing.T) {
	tests := []struct {
		name    string
		current OrderStatus
		next    OrderStatus
		wantErr bool
	}{
		{
			name:    "pending to accepted",
			current: OrderStatusPending,
			next:    OrderStatusAccepted,
			wantErr: false,
		},
		{
			name:    "accepted to preparing",
			current: OrderStatusAccepted,
			next:    OrderStatusPreparing,
			wantErr: false,
		},
		{
			name:    "preparing to ready",
			current: OrderStatusPreparing,
			next:    OrderStatusReady,
			wantErr: false,
		},
		{
			name:    "ready to served",
			current: OrderStatusReady,
			next:    OrderStatusServed,
			wantErr: false,
		},
		{
			name:    "pending cannot go directly to served",
			current: OrderStatusPending,
			next:    OrderStatusServed,
			wantErr: true,
		},
		{
			name:    "cancelled is final",
			current: OrderStatusCancelled,
			next:    OrderStatusPending,
			wantErr: true,
		},
		{
			name:    "awaiting payment cannot go to preparing",
			current: OrderStatusAwaitingPayment,
			next:    OrderStatusPreparing,
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			order := Order{
				Status: tt.current,
			}

			err := order.ChangeStatus(tt.next)

			if (err != nil) != tt.wantErr {
				t.Fatalf(
					"ChangeStatus() error = %v, wantErr %v",
					err,
					tt.wantErr,
				)
			}

			if tt.wantErr {
				if order.Status != tt.current {
					t.Errorf(
						"status changed after rejected transition: got %s, want %s",
						order.Status,
						tt.current,
					)
				}
				return
			}

			if order.Status != tt.next {
				t.Errorf(
					"status = %s, want %s",
					order.Status,
					tt.next,
				)
			}
		})
	}
}
