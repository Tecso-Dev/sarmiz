package service

import (
	"math"
	"testing"

	"github.com/Tecso-Dev/sarmiz/services/order/internal/model"
)

func TestOrderItemValidate(t *testing.T) {
	tests := []struct {
		name    string
		item    model.OrderItem
		wantErr bool
	}{
		{
			name: "valid item",
			item: model.OrderItem{
				ItemID:        "coffee-1",
				NameSnapshot:  map[string]string{"fa": "قهوه"},
				UnitPriceRial: 80000,
				Quantity:      2,
				LineTotalRial: 160000,
			},
		},
		{
			name: "missing item ID",
			item: model.OrderItem{
				NameSnapshot:  map[string]string{"fa": "قهوه"},
				UnitPriceRial: 80000,
				Quantity:      1,
				LineTotalRial: 80000,
			},
			wantErr: true,
		},
		{
			name: "zero quantity",
			item: model.OrderItem{
				ItemID:        "coffee-1",
				NameSnapshot:  map[string]string{"fa": "قهوه"},
				UnitPriceRial: 80000,
				Quantity:      0,
				LineTotalRial: 0,
			},
			wantErr: true,
		},
		{
			name: "negative price",
			item: model.OrderItem{
				ItemID:        "coffee-1",
				NameSnapshot:  map[string]string{"fa": "قهوه"},
				UnitPriceRial: -100,
				Quantity:      1,
				LineTotalRial: -100,
			},
			wantErr: true,
		},
		{
			name: "incorrect line total",
			item: model.OrderItem{
				ItemID:        "coffee-1",
				NameSnapshot:  map[string]string{"fa": "قهوه"},
				UnitPriceRial: 80000,
				Quantity:      2,
				LineTotalRial: 150000,
			},
			wantErr: true,
		},
		{
			name: "multiplication overflow",
			item: model.OrderItem{
				ItemID:        "coffee-1",
				NameSnapshot:  map[string]string{"fa": "قهوه"},
				UnitPriceRial: math.MaxInt64,
				Quantity:      3,
				LineTotalRial: math.MaxInt64 - 2,
			},
			wantErr: true,
		},
		{
			name: "missing Persian name",
			item: model.OrderItem{
				ItemID:        "coffee-1",
				NameSnapshot:  map[string]string{"en": "Coffee"},
				UnitPriceRial: 80000,
				Quantity:      1,
				LineTotalRial: 80000,
			},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := ValidateOrderItem(tt.item)

			if (err != nil) != tt.wantErr {
				t.Fatalf(
					"Validate() error = %v, wantErr %v",
					err,
					tt.wantErr,
				)
			}
		})
	}
}
