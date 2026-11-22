# 8. Order business date and idempotency retention

| | |
|---|---|
| Status | Proposed for implementation |
| Scope | Order service, W1-ORD-1 |
| Related | SPEC.md section 7.3, docs/decisions/0004-nats-jetstream-and-outbox.md |

## Context

Order codes restart daily for each venue at midnight in Asia/Tehran.
The order schema must identify the business date associated with each code.

Create-order idempotency keys are scoped to a venue and retained for 24 hours.
Reusing a key with a different request body during that period must return a conflict.

## Decision

### Daily order code

- Add `business_date DATE NOT NULL` to `orders`.
- Calculate the business date in `Asia/Tehran`.
- Enforce `UNIQUE (venue_id, business_date, code)`.
- Allocate the next code atomically using `daily_counters`, keyed by
  `(venue_id, day)`.
- Keep `table_id` and `item_id` as UUID values without cross-service foreign keys.

### Idempotency

- Scope create-order idempotency keys to `(venue_id, idempotency_key)`.
- Keep the key reserved for 24 hours after order creation.
- Store a SHA-256 request fingerprint in `idempotency_request_hash`
  so a repeated key with a different request body can be rejected.
- Add a partial unique index on `(venue_id, idempotency_key)` for non-null keys.
- After 24 hours, the request path must be able to release an expired key
  transactionally before accepting it for a new request. A background cleanup
  may also release expired keys.
- When releasing a key, clear both `idempotency_key` and
  `idempotency_request_hash`. Preserve the order itself.
- Concurrent requests using the same active key must be serialized by the
  database uniqueness constraint and transaction handling.

## Consequences

- `business_date` is an intentional addition to the base schema.
- `idempotency_request_hash` is an intentional addition to support the
  documented same-key/different-body conflict behavior.
- Application code must calculate a stable fingerprint from the validated
  request, excluding transport-only data.
- Expired-key cleanup and concurrent duplicate handling require tests.

## Review

This decision records the implementation proposal for W1-ORD-1.
Obtain mentor review before treating the schema changes as approved.
