package service

import (
	"testing"

	"github.com/Tecso-Dev/sarmiz/services/order/internal/model"
)

func TestChangePaymentStatus(t *testing.T) {
	tests := []struct {
		name    string
		current model.PaymentStatus
		next    model.PaymentStatus
		method  model.PaymentMethod
		wantErr bool
	}{
		{"online starts payment", model.PaymentStatusUnpaid, model.PaymentStatusPending, model.PaymentMethodOnline, false},
		{"counter payment", model.PaymentStatusUnpaid, model.PaymentStatusPaid, model.PaymentMethodCounter, false},
		{"online payment cannot skip verification", model.PaymentStatusUnpaid, model.PaymentStatusPaid, model.PaymentMethodOnline, true},
		{"counter cannot become pending", model.PaymentStatusUnpaid, model.PaymentStatusPending, model.PaymentMethodCounter, true},
		{"pending becomes paid", model.PaymentStatusPending, model.PaymentStatusPaid, model.PaymentMethodOnline, false},
		{"pending becomes failed", model.PaymentStatusPending, model.PaymentStatusFailed, model.PaymentMethodOnline, false},
		{"failed can retry", model.PaymentStatusFailed, model.PaymentStatusPending, model.PaymentMethodOnline, false},
		{"failed cannot become paid directly", model.PaymentStatusFailed, model.PaymentStatusPaid, model.PaymentMethodOnline, true},
		{"paid is final", model.PaymentStatusPaid, model.PaymentStatusPending, model.PaymentMethodOnline, true},
		{"refunded is manually managed", model.PaymentStatusRefunded, model.PaymentStatusPaid, model.PaymentMethodOnline, true},
		{"same status rejected", model.PaymentStatusPending, model.PaymentStatusPending, model.PaymentMethodOnline, true},
		{"unknown current rejected", model.PaymentStatus("unknown"), model.PaymentStatusPaid, model.PaymentMethodOnline, true},
		{"unknown next rejected", model.PaymentStatusPending, model.PaymentStatus("unknown"), model.PaymentMethodOnline, true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			order := model.Order{
				PaymentStatus: tt.current,
				PaymentMethod: tt.method,
			}

			err := ChangePaymentStatus(&order, tt.next)
			if (err != nil) != tt.wantErr {
				t.Fatalf("ChangePaymentStatus() error = %v, wantErr %v", err, tt.wantErr)
			}

			wantStatus := tt.current
			if !tt.wantErr {
				wantStatus = tt.next
			}
			if order.PaymentStatus != wantStatus {
				t.Errorf("payment status = %s, want %s", order.PaymentStatus, wantStatus)
			}
		})
	}
}

func TestChangePaymentStatus_NilOrder(t *testing.T) {
	if err := ChangePaymentStatus(nil, model.PaymentStatusPending); err == nil {
		t.Fatal("expected error for nil order")
	}
}
