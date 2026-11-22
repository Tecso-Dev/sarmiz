package domain

import "testing"

func TestOrderItemValidate(t *testing.T) {
	tests := []struct {
		name    string
		item    OrderItem
		wantErr bool
	}{
		{
			name: "valid item",
			item: OrderItem{
				ItemID:        "coffee-1",
				NameSnapshot:  map[string]string{"fa": "قهوه"},
				UnitPriceRial: 80000,
				Quantity:      2,
				LineTotalRial: 160000,
			},
		},
		{
			name: "missing item ID",
			item: OrderItem{
				NameSnapshot:  map[string]string{"fa": "قهوه"},
				UnitPriceRial: 80000,
				Quantity:      1,
				LineTotalRial: 80000,
			},
			wantErr: true,
		},
		{
			name: "zero quantity",
			item: OrderItem{
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
			item: OrderItem{
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
			item: OrderItem{
				ItemID:        "coffee-1",
				NameSnapshot:  map[string]string{"fa": "قهوه"},
				UnitPriceRial: 80000,
				Quantity:      2,
				LineTotalRial: 150000,
			},
			wantErr: true,
		},
		{
			name: "missing Persian name",
			item: OrderItem{
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
			err := tt.item.Validate()

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
