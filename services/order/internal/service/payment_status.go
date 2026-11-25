package service

import (
	"fmt"

	"github.com/Tecso-Dev/sarmiz/services/order/internal/model"
)

func ChangePaymentStatus(o *model.Order, next model.PaymentStatus) error {
	if o == nil {
		return fmt.Errorf("order is nil")
	}

	switch o.PaymentStatus {
	case model.PaymentStatusUnpaid:
		switch next {
		case model.PaymentStatusPending:
			if o.PaymentMethod != model.PaymentMethodOnline {
				return fmt.Errorf("only online payments can become pending")
			}
		case model.PaymentStatusPaid:
			if o.PaymentMethod != model.PaymentMethodCounter {
				return fmt.Errorf("unpaid online payment must be verified before becoming paid")
			}
		default:
			return fmt.Errorf(
				"payment transition from %s to %s is not allowed",
				o.PaymentStatus, next,
			)
		}

	case model.PaymentStatusPending:
		if next != model.PaymentStatusPaid && next != model.PaymentStatusFailed {
			return fmt.Errorf("payment transition from %s to %s is not allowed", o.PaymentStatus, next)
		}

	case model.PaymentStatusFailed:
		if next != model.PaymentStatusPending {
			return fmt.Errorf("payment transition from %s to %s is not allowed", o.PaymentStatus, next)
		}

	case model.PaymentStatusPaid, model.PaymentStatusRefunded:
		return fmt.Errorf("payment status %s cannot be changed through this state machine", o.PaymentStatus)

	default:
		return fmt.Errorf("unknown current payment status: %s", o.PaymentStatus)
	}

	if !isKnownPaymentStatus(next) {
		return fmt.Errorf("unknown next payment status: %s", next)
	}

	o.PaymentStatus = next
	return nil
}

func isKnownPaymentStatus(status model.PaymentStatus) bool {
	switch status {
	case model.PaymentStatusUnpaid,
		model.PaymentStatusPending,
		model.PaymentStatusPaid,
		model.PaymentStatusFailed,
		model.PaymentStatusRefunded:
		return true
	default:
		return false
	}
}
