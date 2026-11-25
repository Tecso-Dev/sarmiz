-- +goose Up

CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    venue_id UUID NOT NULL,
    branch_id UUID,
    table_id UUID,
    table_label TEXT,
    business_date DATE NOT NULL,
    code BIGINT NOT NULL,
    type TEXT NOT NULL DEFAULT 'dine_in',
    status TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    payment_status TEXT NOT NULL DEFAULT 'unpaid',
    subtotal_rial BIGINT NOT NULL,
    total_rial BIGINT NOT NULL,
    note TEXT,
    locale TEXT,
    guest_session_id UUID,
    order_token_hash TEXT,
    idempotency_key TEXT,
    idempotency_request_hash TEXT,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT orders_type_check
        CHECK (type IN ('dine_in', 'pickup', 'delivery')),

    CONSTRAINT orders_status_check
        CHECK (status IN (
            'awaiting_payment',
            'pending',
            'accepted',
            'preparing',
            'ready',
            'served',
            'cancelled'
        )),

    CONSTRAINT orders_payment_method_check
        CHECK (payment_method IN ('online', 'counter')),

    CONSTRAINT orders_payment_status_check
        CHECK (payment_status IN (
            'unpaid', 'pending', 'paid', 'failed', 'refunded'
        )),

    CONSTRAINT orders_amounts_check
        CHECK (subtotal_rial >= 0 AND total_rial >= 0),

    CONSTRAINT orders_venue_date_code_unique
        UNIQUE (venue_id, business_date, code),

    CONSTRAINT orders_idempotency_pair_check
        CHECK (
            (idempotency_key IS NULL AND idempotency_request_hash IS NULL)
            OR
            (idempotency_key IS NOT NULL AND idempotency_request_hash IS NOT NULL)
        ),

    -- Required as the referenced key for the composite venue/order foreign key.
    CONSTRAINT orders_venue_id_unique
        UNIQUE (venue_id, id)
);

CREATE INDEX idx_orders_venue_created_at
    ON orders (venue_id, created_at DESC);

CREATE INDEX idx_orders_venue_status
    ON orders (venue_id, status);

CREATE UNIQUE INDEX idx_orders_venue_idempotency_key
    ON orders (venue_id, idempotency_key)
    WHERE idempotency_key IS NOT NULL;


CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL,
    venue_id UUID NOT NULL,
    item_id UUID NOT NULL,
    name_snapshot JSONB NOT NULL,
    unit_price_rial BIGINT NOT NULL,
    quantity INTEGER NOT NULL,
    options_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    line_total_rial BIGINT NOT NULL,
    note TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT order_items_quantity_check
        CHECK (quantity > 0),

    CONSTRAINT order_items_amounts_check
        CHECK (unit_price_rial >= 0 AND line_total_rial >= 0),

    CONSTRAINT order_items_line_total_check
        CHECK (line_total_rial = unit_price_rial * quantity),

    CONSTRAINT order_items_order_venue_fk
        FOREIGN KEY (venue_id, order_id)
        REFERENCES orders (venue_id, id)
        ON DELETE CASCADE
);

CREATE INDEX idx_order_items_venue_order
    ON order_items (venue_id, order_id);

CREATE INDEX idx_order_items_venue_item
    ON order_items (venue_id, item_id);


CREATE TABLE daily_counters (
    venue_id UUID NOT NULL,
    day DATE NOT NULL,
    last_code BIGINT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (venue_id, day),

    CONSTRAINT daily_counters_last_code_check
        CHECK (last_code >= 0)
);


CREATE TABLE outbox (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    venue_id UUID NOT NULL,
    subject TEXT NOT NULL,
    payload JSONB NOT NULL,
    sent_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_outbox_venue_created_at
    ON outbox (venue_id, created_at);

CREATE INDEX idx_outbox_unsent
    ON outbox (created_at)
    WHERE sent_at IS NULL;


CREATE TABLE processed_events (
    event_id UUID PRIMARY KEY,
    processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    venue_id UUID NOT NULL,
    user_id UUID,
    action TEXT NOT NULL,
    target TEXT NOT NULL,
    meta JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_log_venue_created_at
    ON audit_log (venue_id, created_at DESC);


-- +goose Down

DROP TABLE IF EXISTS audit_log;
DROP TABLE IF EXISTS processed_events;
DROP TABLE IF EXISTS outbox;
DROP TABLE IF EXISTS daily_counters;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
