package domain

import "fmt"

func (o *Order) ChangeStatus(next OrderStatus) error {
	if o.Status == next {
		return nil
	}

	switch o.Status {
	case OrderStatusAwaitingPayment:
		if next != OrderStatusPending &&
			next != OrderStatusCancelled {
			return fmt.Errorf(
				"cannot change order status from %s to %s",
				o.Status,
				next,
			)
		}

	case OrderStatusPending:
		if next != OrderStatusAccepted &&
			next != OrderStatusCancelled {
			return fmt.Errorf(
				"cannot change order status from %s to %s",
				o.Status,
				next,
			)
		}

	case OrderStatusAccepted:
		if next != OrderStatusPreparing &&
			next != OrderStatusCancelled {
			return fmt.Errorf(
				"cannot change order status from %s to %s",
				o.Status,
				next,
			)
		}

	case OrderStatusPreparing:
		if next != OrderStatusReady {
			return fmt.Errorf(
				"cannot change order status from %s to %s",
				o.Status,
				next,
			)
		}

	case OrderStatusReady:
		if next != OrderStatusServed {
			return fmt.Errorf(
				"cannot change order status from %s to %s",
				o.Status,
				next,
			)
		}

	case OrderStatusServed, OrderStatusCancelled:
		return fmt.Errorf(
			"order status %s is final",
			o.Status,
		)

	default:
		return fmt.Errorf("unknown order status: %s", o.Status)
	}

	o.Status = next
	return nil
}
