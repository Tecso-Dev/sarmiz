package service

import (
	"fmt"
	"math"

	"github.com/Tecso-Dev/sarmiz/services/order/internal/model"
)

func ValidateOrderItem(i model.OrderItem) error {
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

	quantity := int64(i.Quantity)

	// Check before multiplying so int64 overflow cannot corrupt the result.
	if quantity > 0 && i.UnitPriceRial > math.MaxInt64/quantity {
		return fmt.Errorf("line total overflows int64")
	}

	expectedTotal := i.UnitPriceRial * quantity
	if i.LineTotalRial != expectedTotal {
		return fmt.Errorf("line total does not match unit price and quantity")
	}

	if i.NameSnapshot["fa"] == "" {
		return fmt.Errorf("item name in Persian is required")
	}

	return nil
}
