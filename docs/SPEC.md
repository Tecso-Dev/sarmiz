# Sarmiz technical specification

Status: baseline v1, 2026-11-10. Owner: the mentor. Language: English on purpose, so that AI assistants and tools read it precisely.

**This file is the technical source of truth.** The Persian guide in `docs/guide/` explains it. If a guide chapter, a handoff or an issue disagrees with this file, this file wins and the other one gets fixed. Change this file only through a pull request that also adds a decision record in `docs/decisions/`.

Words used: **venue** = a cafe or restaurant account. **branch** = one physical location of a venue. **guest** = a customer who scans a QR code. **panel** = the web app the venue staff use. **R1 / R2 / R3** = release 1, 2, 3 (see `docs/roadmap.md`).

## 1. Product

Sarmiz is a QR menu and table-ordering service for cafes and restaurants. An owner signs up with a phone number, builds a menu, and prints one QR code per table. A guest scans the code, reads the menu in their language, orders, and pays online or at the counter. The kitchen sees the order live. No guest account and no app install.

Selling points: AI translation of the menu into five languages, AI menu import from a photo of the paper menu, an AI waiter that answers only from the real menu, and payments that go to the venue rather than to Sarmiz.

## 2. Release 1 scope

| Area | In release 1 |
|---|---|
| Menu | categories, items, photos, item options (size, extras), allergen and diet tags with filters, badges (popular, new, chef), time-based menus, sold-out switch |
| Languages and AI | menu content in `fa`, `en`, `ar`, `ckb`, `azb`; AI translation; AI menu import from photo (fallback: Excel); AI waiter |
| Ordering | order from the table, call waiter, ask for the bill, live order status, "goes well with" suggestions |
| Payment | online through Zarinpal, or pay at the counter |
| Owner tools | live kitchen screen, QR designer with logo, venue branding, public menu link for Instagram, sales dashboard |
| Guests | rating after an order |
| Platform | landing page, pricing page, demo cafe and demo restaurant, Tecso admin panel |

Stretch items (first to move after week 6 if time runs out): AI waiter, AI photo import, sales dashboard, time-based menus, pairings.

Not in R1: guest accounts, loyalty, split bill, tips, pickup, reservation, kitchen stations, printers, staff management UI, multi-branch UI, delivery, POS links, custom domains. Never: native mobile apps, Tecso holding venue money.

The data model and contracts must already leave room for R2 and R3 (branches, roles, order types, optional guest identity).

## 3. System design targets

These are the numbers the design is sized for. They are starting targets; the team measures and adjusts them.

| Target | Value |
|---|---|
| Venues | 50 active |
| Concurrent guests | 500 |
| Peak orders | 20 per minute |
| WebSocket connections | 100 panel plus 500 guest |
| Public menu latency | p95 under 300 ms at the gateway |
| Create order latency | p95 under 800 ms |
| Order reaches kitchen screen | under 2 s |
| Guest page on 4G | Largest Contentful Paint under 2 s, guest route JavaScript at most 150 KB gzipped |
| Availability of guest paths | 99.5% per month |
| Recovery point (RPO) | 24 h in R1 (nightly backup) |
| Recovery time (RTO) | 4 h |

## 4. Architecture

Microservices. One public entry point. Each service owns its data.

| Service | Language | Responsibility | Database | Talks to the outside by |
|---|---|---|---|---|
| `gateway` | Go | public REST entry, REST to gRPC translation, JWT check, permissions per route, rate limiting, CORS, request id | none (uses Redis) | HTTPS `/api/v1/*` |
| `identity` | Go | panel users, OTP login, tokens, memberships and roles, platform admins | `identity` | gRPC, plus internal JWKS over HTTP |
| `catalog` | Go | venues, branches, tables and QR, branding, menu, images, public menu read model, import jobs, stored translations | `catalog` | gRPC |
| `order` | Go | orders, service requests, ratings, payments, venue payment config, sales reports | `orders` | gRPC |
| `realtime` | Go | WebSocket hub for kitchen screens and guest order pages | none | WSS `/ws` |
| `ai` | Python (FastAPI) | translation, menu import, AI waiter (RAG) | `ai` (pgvector) | internal HTTP only |
| `web` | React, TypeScript | guest app, owner panel, kitchen screen, landing, admin | none | static files behind Nginx |

Shared infrastructure: PostgreSQL (one server, one database and one role per service), Redis (rate limits, caches, OTP codes), NATS JetStream (events), S3-compatible object storage (MinIO in local development), Ollama (models).

### 4.1 Communication rules

1. The browser talks only to `gateway` (REST) and `realtime` (WebSocket).
2. Service to service, synchronous: gRPC with Protobuf. Every call has a deadline (default 2 s). Retry only idempotent reads, with jitter. Long operations such as translating a whole menu are asynchronous or use a longer, explicitly set deadline (decided in W3-CORE-3), never the 2 s default. Wrap clients in a circuit breaker.
3. Service to service, asynchronous: NATS JetStream events. Publish through a transactional outbox. Consumers are idempotent and deduplicate by event id.
4. No service reads or writes another service's database. Cross-service references are plain UUIDs without foreign keys.
5. The `ai` service is called over internal HTTP (FastAPI) and also consumes events.
6. Allowed synchronous dependencies, nothing else without a decision record:

| Caller | May call |
|---|---|
| `gateway` | `identity`, `catalog`, `order` |
| `catalog` | `identity` (grant membership), `ai` (translate, assistant) |
| `order` | `catalog` (resolve table, price items) |
| `ai` | `catalog` (read a menu snapshot for indexing) |
| `realtime` | `identity` JWKS over internal HTTP only, to verify stream tickets (cached 10 minutes). Alternative: read the public key from a secret. W1-ORD-3 picks one |
| `identity` | nobody |

### 4.2 Why these boundaries

- `order` owns payments too. Marking an order paid and recording the verified payment must happen in one database transaction. Splitting them would need a saga that a junior team should not own in six weeks. A separate payment service is an R3 option.
- `catalog` owns venues and tables together with the menu, because guests read them together on every scan.
- `realtime` has no database and its only synchronous need is `identity`'s public keys (JWKS, cached), so it can restart or scale freely.
- `gateway` is generated with grpc-gateway from HTTP annotations in the proto files, plus hand-written middleware. It holds no business logic.
- `gateway` sets and clears the `sz_at` and `sz_rt` cookies from the tokens that `identity` returns; `identity` itself speaks only gRPC (plus JWKS).
- Guest stream tickets: `gateway` calls `order.ValidateOrderToken` first, then `identity.IssueStreamTicket` with scope `order:<order_id>`.
- Every pair that adds an endpoint also adds its `gateway` route and role rule in the same pull request; the platform pair reviews it. W2-PA-1 builds the routing for weeks 1 to 3, later routes follow this rule.

### 4.3 Main flows

Guest opens a menu: browser, `gateway` `GET /public/t/{qr_token}`, `catalog.GetPublicMenuByTable` (Redis cache), response with ETag.

Guest orders: browser, `gateway` `POST /public/t/{qr_token}/orders`, `order.CreateOrder`, which calls `catalog.ResolveTable` and `catalog.PriceItems`, saves the order with a price snapshot and an outbox row in one transaction, then the outbox relay publishes `order.created`, `realtime` pushes it to the venue's kitchen screens.

Online payment: browser, `gateway`, `order.StartPayment`, redirect to Zarinpal, Zarinpal redirects to `GET /public/payments/zarinpal/callback`, `order.HandleCallback` verifies with the stored amount, marks payment and order in one transaction, publishes `order.paid`, redirects the guest to the result page.

Menu change: `catalog` bumps `venues.menu_version`, writes the outbox row `menu.changed`, the `ai` service re-indexes that venue.

## 5. Repository layout

```
sarmiz/
├── AGENTS.md  CLAUDE.md  README.md  CONTRIBUTING.md
├── services/
│   ├── gateway/    Go, generated grpc-gateway plus middleware
│   ├── identity/   Go
│   ├── catalog/    Go
│   ├── order/      Go
│   ├── realtime/   Go
│   └── ai/         Python, FastAPI
├── libs/go/kit/    shared Go chassis: config, logging, gRPC server, db, events, auth, errors, test helpers
├── proto/          sarmiz/<service>/v1/*.proto, events/*.schema.json, buf.yaml
├── web/            React app
├── deploy/         compose/, helm/, grafana/, alerts/
├── tests/          e2e/ (Playwright), load/ (k6), isolation/
├── scripts/
└── docs/
```

Each Go service follows the layout the interns already know from the course:

```
services/<name>/
├── cmd/server/main.go
├── internal/
│   ├── config/
│   ├── handler/      gRPC handlers, no business rules
│   ├── service/      business rules, unit tested
│   ├── repository/   SQL with pgx, every method takes venue_id where the data is venue-owned
│   └── model/
├── migrations/       goose SQL files
├── Dockerfile
└── README.md
```

Go workspace (`go.work`) with one module per service and one for `libs/go/kit`.

## 6. Contracts

### 6.1 REST through the gateway

Base path `/api/v1`. JSON only. `snake_case` field names. Times in RFC 3339 UTC. Money as integer Rial in fields ending with `_rial`. IDs are UUID strings. Lists use cursor pagination: `?limit=` (default 20, max 100) and `?cursor=`, response `{"items": [...], "next_cursor": "..."}`.

Error format, same for every endpoint:

```json
{
  "error": {
    "code": "validation_failed",
    "message": "price_rial must be zero or more",
    "fields": {"price_rial": "must be zero or more"},
    "request_id": "01JC..."
  }
}
```

Error codes: `validation_failed` (400), `unauthenticated` (401), `permission_denied` (403), `not_found` (404), `conflict` (409), `failed_precondition` (422), `rate_limited` (429), `not_implemented` (501), `unavailable` (503), `internal` (500). gRPC codes map in one place in the kit: `InvalidArgument` to `validation_failed`, `Unauthenticated` to `unauthenticated`, `PermissionDenied` to `permission_denied`, `NotFound` to `not_found`, `AlreadyExists` and `Aborted` to `conflict`, `FailedPrecondition` to `failed_precondition`, `ResourceExhausted` to `rate_limited`, `Unimplemented` to `not_implemented`, `Unavailable` and `DeadlineExceeded` to `unavailable`, anything else to `internal`. Never leak SQL, stack traces or internal names.

Route groups:

| Group | Auth | Examples | Backing service |
|---|---|---|---|
| `/auth/*` | none or cookie | `POST /auth/otp/request`, `POST /auth/otp/verify`, `POST /auth/refresh`, `POST /auth/logout`, `GET /me` | `identity` |
| `/venues` and `/venues/{venue_id}/*` | panel user with a role in that venue | venue, branding, tables, categories, items, option groups, schedules, pairings, uploads, imports, translate | `catalog` |
| `/venues/{venue_id}/orders*`, `/service-requests*`, `/reports/*`, `/payment-config` | panel user | list orders, change status, mark paid at counter, sales summary | `order` |
| `/public/t/{qr_token}*`, `/public/m/{slug}` | none | public menu by table, public menu by slug | `catalog` |
| `/public/t/{qr_token}/orders`, `/public/orders/{order_id}*`, `/public/payments/zarinpal/callback`, `/public/t/{qr_token}/service-requests` | none, order token where needed | create order, get order, start payment, rate | `order` |
| `/public/t/{qr_token}/assistant` | none | AI waiter | `catalog`, which calls `ai` |
| `/stream-tickets` | panel user or order token | ticket for the WebSocket | `identity` |
| `/admin/*` | platform admin | list venues, activate, suspend, set payment mode | `catalog`, `order` |

Unsafe methods accept an `Idempotency-Key` header on `POST /public/t/{qr_token}/orders` and `POST /public/orders/{order_id}/pay`. Keys are unique per venue and stored for 24 h; the same key with a different body returns `conflict`. The guest's order token travels in the `X-Order-Token` header, never in a URL.

The OpenAPI document is generated from the proto files and committed to `docs/api/openapi.yaml`. The web client types are generated from it.

### 6.2 gRPC

Packages `sarmiz.<service>.v1`. Lint and breaking-change checks with `buf` in CI. Field validation with `protovalidate`.

| Service | gRPC services (main methods) |
|---|---|
| `identity` | `AuthService` (RequestOtp, VerifyOtp, RefreshToken, Logout, GetMe, IssueStreamTicket), `AccessService` (GrantMembership, RevokeMembership, ListMemberships) |
| `catalog` | `VenueService` (CreateVenue, GetVenue, UpdateVenue, ListMyVenues, AdminListVenues, AdminSetVenueStatus), `TableService` (CRUD, RegenerateQrToken, GetTableQr, ResolveTable), `MenuService` (categories, items, option groups, schedules, pairings, SetItemAvailability, reorder), `PublicMenuService` (GetPublicMenuByTable, GetPublicMenuBySlug), `PricingService` (PriceItems, internal), `MediaService` (UploadImage), `ImportService` (CreateImportJob, GetImportJob, ApplyImportJob), `TranslationService` (TranslateMenu), `AssistantService` (Ask), `SnapshotService` (GetMenuSnapshot, internal) |
| `order` | `OrderService` (CreateOrder, GetOrder, ListOrders, UpdateOrderStatus, MarkPaidAtCounter, CancelOrder, ValidateOrderToken), `ServiceRequestService` (Create, List, Resolve), `PaymentService` (GetPaymentConfig, SetPaymentConfig, StartPayment, HandleCallback, AdminSetPaymentMode), `RatingService` (CreateRating), `ReportService` (GetSalesSummary, GetTopItems, GetBusyHours) |

`gateway` passes trusted metadata on every call: `x-request-id`, `x-user-id`, `x-venue-id`, `x-role`, `x-guest-session`, plus W3C trace context. Services trust this metadata only because nothing except `gateway` can reach them (network policy), and they still scope every query by venue.

### 6.3 Events

Stream `SARMIZ` on NATS JetStream. Subject pattern `sarmiz.<service>.<entity>.<event>`.

| Subject | Published by | Consumed by | Payload (`data`) |
|---|---|---|---|
| `sarmiz.catalog.menu.changed` | `catalog` | `ai` | `venue_id`, `menu_version` |
| `sarmiz.catalog.venue.updated` | `catalog` | none in R1 | `venue_id` |
| `sarmiz.catalog.import.requested` | `catalog` | `ai` | `job_id`, `venue_id`, `kind`, `file_key`, `locale_hint` |
| `sarmiz.ai.import.completed` | `ai` | `catalog` | `job_id`, `status`, `draft` or `error` |
| `sarmiz.order.order.created` | `order` | `realtime` | order summary: ids, code, table label, lines, totals, status |
| `sarmiz.order.order.status_changed` | `order` | `realtime` | `order_id`, `venue_id`, `from`, `to` |
| `sarmiz.order.order.paid` | `order` | `realtime` | `order_id`, `venue_id`, `amount_rial`, `method` |
| `sarmiz.order.service_request.created` | `order` | `realtime` | `request_id`, `venue_id`, `table_label`, `type` |
| `sarmiz.order.service_request.resolved` | `order` | `realtime` | `request_id`, `venue_id` |

Envelope for every event:

```json
{
  "id": "uuid",
  "type": "sarmiz.order.order.created",
  "version": 1,
  "time": "2026-11-10T12:00:00Z",
  "venue_id": "uuid",
  "traceparent": "00-<trace-id>-<parent-span-id>-01",
  "data": {}
}
```

JSON Schema for each event lives in `proto/events/`. Outbox: the service writes the event row in the same transaction as the business change; a relay loop publishes rows and marks them sent. Metric `outbox_lag_seconds` must stay under 60.

### 6.4 WebSocket

`wss://<host>/ws?ticket=<ticket>`. A ticket is a 60-second JWT from `POST /api/v1/stream-tickets` with a scope of `venue:<venue_id>` (panel) or `order:<order_id>` (guest). Server messages are the event envelopes above, filtered by scope. Heartbeat ping every 25 s. Clients reconnect with backoff.

The WebSocket is only a notification channel. The panel loads the real state from `GET /venues/{venue_id}/orders` when it connects, after every reconnect, and every 30 s as a safety net. A lost event must never lose an order.

## 7. Data model

One PostgreSQL server. Databases `identity`, `catalog`, `orders`, `ai`, each with its own role that can reach only its own database. Migrations with goose, one folder per service, expand-then-contract so a rollback of the code is always safe. Every table has `id uuid primary key`, `created_at`, `updated_at` unless noted. Every venue-owned table has `venue_id uuid not null` and an index that starts with it.

Text shown to guests is stored as JSONB keyed by locale, for example `{"fa": "<Persian name>", "en": "Latte"}`. `fa` is required. Read fallback: requested locale, then `venues.default_locale`, then `fa`.

Money is `bigint` Rial. The UI shows Toman (Rial divided by 10).

### 7.1 `identity`

| Table | Key columns |
|---|---|
| `users` | `phone` unique (E.164), `name`, `is_platform_admin` |
| `memberships` | `user_id`, `venue_id`, `role` (`owner`, `manager`, `staff`), unique on (`user_id`, `venue_id`) |
| `refresh_tokens` | `user_id`, `token_hash`, `family_id`, `expires_at`, `revoked_at`, `user_agent`, `ip` |
| `audit_log` | `user_id`, `action`, `target`, `meta` jsonb |

OTP codes live in Redis only: key `otp:{phone}`, value a hash of the code plus an attempt counter, TTL 120 s.

### 7.2 `catalog`

| Table | Key columns |
|---|---|
| `venues` | `slug` unique, `name` jsonb, `kind` (`cafe`, `restaurant`), `logo_media_id`, `cover_media_id`, `theme_color`, `default_locale`, `enabled_locales` text[], `status` (`pending`, `active`, `suspended`; a new venue starts `active` in R1 and a platform admin may suspend it; `pending` is reserved for an approval step later), `is_demo`, `menu_version` bigint |
| `branches` | `venue_id`, `name`, `address`, `phone`, `is_default`. R1 creates exactly one per venue |
| `dining_tables` | `venue_id`, `branch_id`, `label`, `qr_token` unique random, `is_active` |
| `menu_categories` | `venue_id`, `name` jsonb, `sort_order`, `schedule_id` nullable, `is_active` |
| `menu_items` | `venue_id`, `category_id`, `name` jsonb, `description` jsonb, `price_rial`, `media_id`, `is_available`, `badges` text[], `diet_tags` text[], `allergens` text[], `sort_order`, `is_active`, `ai_translated_locales` text[] |
| `option_groups` | `venue_id`, `item_id`, `name` jsonb, `min_select`, `max_select`, `sort_order` |
| `options` | `venue_id`, `group_id`, `name` jsonb, `price_delta_rial`, `is_available`, `sort_order` |
| `menu_schedules` | `venue_id`, `name`, `days_of_week` int[], `start_time`, `end_time` |
| `item_pairings` | `venue_id`, `item_id`, `paired_item_id`, `sort_order` |
| `media` | `venue_id`, `storage_key`, `content_type`, `width`, `height`, `bytes` |
| `import_jobs` | `venue_id`, `kind` (`photo`, `excel`), `file_key`, `status` (`queued`, `processing`, `ready`, `applied`, `failed`), `draft` jsonb, `error` |
| `outbox` | `event_id`, `subject`, `payload` jsonb, `sent_at` |
| `processed_events` | `event_id` primary key, `processed_at` (dedupe for `ai.import.completed`) |
| `audit_log` | `venue_id`, `user_id`, `action`, `target`, `meta` jsonb |

Allowed tag values. `diet_tags`: `vegetarian`, `vegan`, `gluten_free`, `sugar_free`, `spicy`, `caffeine_free`. `allergens`: `gluten`, `dairy`, `egg`, `nuts`, `peanut`, `soy`, `sesame`, `fish`, `shellfish`. `badges`: `popular`, `new`, `chef`.

Any change to a venue's menu, availability, schedule or branding (logo, cover, theme color, enabled locales) bumps `venues.menu_version` in the same transaction.

Time-based menus change with the clock, not with an edit. The public menu read model therefore includes the active schedule window: the cache key gets a `schedule_window` part (the start of the current window, in `Asia/Tehran`), and the cached entry's TTL is capped at the next schedule boundary.

### 7.3 `orders`

| Table | Key columns |
|---|---|
| `orders` | `venue_id`, `branch_id`, `table_id`, `table_label` snapshot, `code` (short number, restarts daily per venue at midnight `Asia/Tehran`), `type` (`dine_in`; `pickup` and `delivery` reserved), `status`, `payment_method` (`online`, `counter`), `payment_status`, `subtotal_rial`, `total_rial`, `note`, `locale`, `guest_session_id`, `order_token_hash`, `idempotency_key`, `expires_at` |
| `order_items` | `order_id`, `venue_id`, `item_id`, `name_snapshot` jsonb, `unit_price_rial`, `quantity`, `options_snapshot` jsonb, `line_total_rial`, `note` |
| `payments` | `order_id`, `venue_id`, `provider`, `mode` (`sandbox`, `live`), `amount_rial`, `authority` unique, `ref_id`, `status` (`initiated`, `verified`, `failed`), `provider_response` jsonb, `verified_at` |
| `payment_configs` | `venue_id` primary key, `provider`, `mode` (`off`, `sandbox`, `live`), `credentials_enc` bytea, `settlement` jsonb, `updated_by` |
| `service_requests` | `venue_id`, `branch_id`, `table_id`, `table_label`, `type` (`waiter`, `bill`), `status` (`open`, `done`) |
| `ratings` | `order_id` unique, `venue_id`, `stars` 1 to 5, `comment` |
| `daily_counters` | `venue_id`, `day`, `last_code` |
| `outbox`, `processed_events`, `audit_log` | as in `catalog` |

Order status machine: `awaiting_payment` to `pending` to `accepted` to `preparing` to `ready` to `served`. `cancelled` is reachable from `awaiting_payment`, `pending` and `accepted`. An order paid at the counter starts at `pending`. An online order starts at `awaiting_payment`, moves to `pending` only when its payment is verified, and is cancelled automatically after 15 minutes without payment. The kitchen never sees `awaiting_payment` orders: `order.created` is published for every order, but `realtime` does not forward an `awaiting_payment` order to venue channels, and the panel's order list excludes that status by default. An online order reaches the kitchen through `order.paid`.

Payment status machine: `unpaid` to `pending` to `paid` or `failed`; `failed` may go back to `pending` on a retry; `MarkPaidAtCounter` moves `unpaid` straight to `paid`. `refunded` is set by hand in R1.

The expiry job never cancels an order whose payment status is `pending`; the reconciliation job (section 9) settles it first, and only then may the order expire.

Order lines always store a snapshot of names, prices and options, so later menu edits never change an old order.

### 7.4 `ai`

| Table | Key columns |
|---|---|
| `menu_chunks` | `venue_id`, `item_id`, `locale`, `content`, `embedding` vector, `menu_version` |
| `outbox`, `processed_events` | as in `catalog` (for `import.completed`, and dedupe of consumed events) |

### 7.5 Object storage

Bucket `sarmiz-media`: images, public read through the CDN, key `v/{venue_id}/{sha256}-{width}.webp`. Bucket `sarmiz-imports`: uploaded menu photos and Excel files, private, deleted after 30 days.

Upload rule: at most 5 MB, JPEG, PNG or WebP checked by content, decoded and re-encoded to WebP in widths 320, 800 and 1600. Re-encoding removes metadata such as GPS location.

## 8. Auth and permissions

Panel users log in with a phone number and a one-time code.

| Item | Rule |
|---|---|
| OTP | 6 digits, valid 120 s, at most 5 verify attempts per code, resend after 60 s, stored in Redis as an HMAC-SHA256 of phone and code with a key from a secret (a plain hash of 6 digits is reversible) |
| Access token | JWT signed with Ed25519, lifetime 15 min, claims `sub`, `adm`, `mem` (list of `{v: venue_id, r: role}`), `exp`, `jti` |
| Refresh token | random 256 bits, lifetime 30 days, rotated on every use, stored hashed, reuse of an old token revokes the whole family |
| Cookies | `sz_at` and `sz_rt`, `HttpOnly`, `Secure`, `SameSite=Lax`, `Max-Age` equal to each token's lifetime. `sz_at` has `Path=/api/v1`, `sz_rt` has `Path=/api/v1/auth`. The CDN ignores cookies on `/api/v1/public/*` |
| CSRF | `SameSite=Lax` plus an Origin allowlist check in `gateway` on every unsafe method |
| Keys | signing key from a Kubernetes secret, public keys published as JWKS by `identity`, cached 10 min by `gateway` |

Permission matrix. It is enforced from week 1 even though the R1 UI only creates owners.

| Action | owner | manager | staff |
|---|---|---|---|
| See orders, change order status, mark paid at the counter, resolve service requests, toggle sold-out | yes | yes | yes |
| Edit menu, tables, QR, branding, schedules, import, translate | yes | yes | no |
| See sales reports | yes | yes | no |
| See or change payment config, manage members | yes | no | no |

Platform admins (`adm` claim) may use `/admin/*`: list venues, activate or suspend a venue, set a venue's payment mode to `live`.

Roles are read from the `mem` claim of the access token. After a membership changes (for example right after `CreateVenue`), the web app calls `POST /auth/refresh` to get a token with the new claim; `GET /me` always reads memberships from the database.

`gateway` checks the token and the role for the route. Every service checks again that the resource belongs to the venue in the trusted metadata. A wrong venue returns `not_found`, not `permission_denied`, so ids cannot be probed. This includes a `venue_id` in the path that is not in the token's `mem` claim: `gateway` answers `not_found` (a known member with too low a role gets `permission_denied`).

System jobs that work across all venues (expiring unpaid orders, payment reconciliation, outbox relay) are the only code allowed to query without `venue_id`; each such query carries a comment saying so.

Guests have no account. The browser keeps a random `guest_session_id` and sends it in `X-Guest-Session`; it is used for rate limits and for "my orders on this device". An order is readable only with its `order_token`, a random 128-bit value returned once at creation and stored hashed.

Service-to-service trust in R1: private cluster network plus NetworkPolicy. Only `gateway` and `realtime` are reachable from the ingress. Internal HTTP calls to `ai` carry a shared secret header. Mutual TLS and a service mesh are out of scope for R1.

## 9. Payments

The settlement model is an **open decision** (`docs/decisions/0006-payment-settlement-model.md`) that the mentor must confirm with Zarinpal before week 4:

- Model A: each venue enters its own Zarinpal merchant id. Zarinpal ties a merchant id to a registered website, so this may be rejected for callbacks on the Sarmiz domain.
- Model B: one Sarmiz merchant account, and Zarinpal's split-settlement feature sends each payment to the venue's bank account directly.

In both models Tecso never holds venue money. The code is written behind a `PaymentProvider` interface, with a fake provider for tests and local work, so either model fits.

Rules that hold in both models:

1. Amounts are integer Rial. The server computes the amount from the stored order. Nothing from the browser or from callback query parameters is trusted.
2. `StartPayment` is allowed only for an order with `payment_method = online` and `payment_status` in (`unpaid`, `failed`). It creates a `payments` row, calls the provider, stores the unique `authority`, and returns the redirect URL.
3. `HandleCallback` loads the payment by `authority` and locks the row. If it is already verified it returns the same result again. Otherwise it calls the provider's verify with the stored amount. On success it marks the payment `verified`, sets the order to `paid` and `pending`, and writes the `order.paid` outbox row, all in one transaction.
4. A reconciliation job runs every 5 minutes and re-checks payments that stayed `initiated` for more than 2 minutes, because a guest may close the browser after paying.
5. Sandbox mode until the week-6 security review. Only a platform admin can set a venue to `live`.
6. Credentials are encrypted at rest with AES-256-GCM using a key from a secret. They are never logged and never returned in full by any API.
7. Refunds are manual in R1: the owner refunds in the provider's own panel and marks the order `refunded`.
8. Every change to payment config writes an audit log row.
9. All payment and auth code needs the mentor's review before merge.

Zarinpal endpoints, request and response fields must be taken from Zarinpal's current official documentation in week 4, not from memory or from an AI assistant.

## 10. Rate limiting

Enforced in `gateway` with a sliding window in Redis. A blocked request gets `429`, the `rate_limited` error code and a `Retry-After` header. These are starting values to tune after the load test.

| Scope | Limit |
|---|---|
| Any IP, all routes | 300 per minute |
| OTP request, per phone | 1 per 60 s and 5 per hour |
| OTP request, per IP | 20 per hour |
| OTP verify, per phone | 10 per 10 minutes, and 5 attempts per code |
| Public menu, per IP | 120 per minute |
| Create order, per guest session | 5 per 5 minutes |
| Create order, per table | 20 per 5 minutes |
| Create order, per IP | 300 per hour (many guests share one cafe Wi-Fi; tune after the load test) |
| Service request, per table and type | 1 per 60 s |
| AI waiter, per guest session | 10 per 5 minutes |
| AI waiter, per venue | 200 per day |
| Uploads, per user | 30 per hour |
| Panel API, per user | 600 per minute |

Limits that need data `gateway` does not have are enforced in the owning service with the same Redis helper from the kit: per table for service requests (`order`), per venue for the AI waiter (`catalog`).

Body limits: 1 MB for JSON, 6 MB for uploads. If Redis is down: fail closed for OTP routes; fail open for every other route (requests pass without rate limiting, an alert fires, and the public menu is served without its cache).

## 11. Caching and CDN

| What | Where | Rule |
|---|---|---|
| Public menu read model | Redis in `catalog` | key `menu:{venue_id}:{locale}:{menu_version}:{schedule_window}`, TTL 24 h or until the next schedule boundary, whichever is sooner. A new `menu_version` makes old keys unused |
| Public menu HTTP response | browser and CDN | `ETag` from `menu_version` and locale, `Cache-Control: public, max-age=30, stale-while-revalidate=300` |
| `qr_token` to table | Redis in `catalog` | TTL 5 minutes |
| JWKS | memory in `gateway` | 10 minutes |
| Images | CDN | content-hashed keys, `Cache-Control: public, max-age=31536000, immutable` |
| Web assets | CDN | hashed file names cached forever, `index.html` not cached |
| Server state in the browser | TanStack Query | `staleTime` set per resource |

Never cached: auth responses, orders, payments, anything under `/venues/*`. A stale menu is acceptable for 30 s because `PriceItems` is the authority when the order is created.

## 12. Observability

| Signal | Tooling | Rule |
|---|---|---|
| Logs | JSON on stdout (`log/slog` in Go, `structlog` in Python), collected into Loki | fields `time`, `level`, `service`, `env`, `request_id`, `trace_id`, `venue_id`, `user_id`, `msg`. Phone numbers masked. No OTP, token, credential or card data. Retention 14 days |
| Errors | GlitchTip, self-hosted, with the Sentry SDKs in Go, Python and web | release is the git SHA, source maps uploaded for web |
| Metrics | Prometheus, `/metrics` on every service | rate, errors and duration per method, plus `orders_created_total`, `payments_verified_total`, `payments_failed_total`, `otp_sent_total`, `ws_connections`, `outbox_lag_seconds`, `ai_request_duration_seconds` |
| Traces | OpenTelemetry to Tempo | W3C trace context from `gateway` through gRPC and inside event envelopes |
| Dashboards | Grafana | overview, one per service, business (orders and payments), infrastructure |
| Health | every service | `/healthz` for liveness, `/readyz` for dependencies, gRPC health service |

Alerts go from Alertmanager to the team's messenger group. Prefer Bale, because the Telegram API may not be reachable from a server inside Iran; test delivery in W3-PA-2:

| Alert | Condition |
|---|---|
| Service down | no healthy pod for 2 minutes |
| Error rate | 5xx above 2% for 5 minutes |
| Latency | p95 above 1 s for 10 minutes |
| Payments | more than 3 failed verifications in 10 minutes |
| Outbox | `outbox_lag_seconds` above 60 |
| Database | connections above 80% of the limit |
| Disk | above 80% |
| Certificate | expires in under 14 days |
| Backup | nightly job failed |
| Outside probe | public menu of the demo venue not reachable from outside |

## 13. Testing

| Level | What | Tools |
|---|---|---|
| Unit | business rules in `service` packages: pricing, state machines, permission matrix. Target 70% coverage there | `go test` table-driven with `-race`, Vitest and Testing Library, pytest |
| Integration | each service against real PostgreSQL, Redis and NATS | testcontainers-go, or Compose in CI |
| Contract | proto lint and breaking-change check, event JSON Schemas, generated OpenAPI diff | `buf`, schema tests |
| End to end | three flows: owner signs up and publishes a menu; guest orders with pay-at-counter and the kitchen updates the status; guest pays online in sandbox | Playwright |
| Security | tenant isolation suite: two venues, every panel endpoint tried across venues must fail; role matrix; rate limits | Go tests in `tests/isolation/` |
| Load | public menu, create order, WebSocket fan-out against the targets in section 3 | k6 |
| AI | translation sample set, import accuracy on 5 real menus, assistant question set of 30 including off-topic and prompt-injection questions | pytest with fixtures, model mocked in unit tests |

A task is done only when its tests are in the same pull request.

## 14. CI/CD and version control

- One repository. Trunk-based: `main` is always deployable. Short-lived branches named `<prefix>/<task-id>-<slug>`, prefix one of `core`, `order`, `web`, `platform`, `docs`, for example `core/W2-CORE-1-menu-items`.
- Pull request required, at least one review, squash merge. Payment and auth changes need the mentor.
- Because squash merge uses the pull request title as the commit message, the title is a Conventional Commit ending with the task id: `feat(catalog): menu categories and items (W2-CORE-1)`.
- Conventional Commits, for example `feat(order): expire unpaid online orders`.
- CI on every pull request, with path filters so only changed services run: lint (golangci-lint, ESLint, Ruff), tests, `buf` checks, build, secret scan (gitleaks), document checks (`scripts/check-markdown.py`, `scripts/check-links.py`).
- On merge to `main`: build images tagged with the git SHA, deploy to `staging` with Helm automatically.
- Production: a SemVer tag `vX.Y.Z` plus manual approval in a GitHub environment. Required reviewers on environments may need a paid plan for a private repository (open decision 6); until then only the mentor tags releases.
- Migrations run as a Helm pre-upgrade job per service. Rollback is `helm rollback`.
- Dependency and image scanning weekly and on pull requests (govulncheck, npm audit, pip-audit, Trivy).

## 15. Hosting and environments

| Environment | Where | Notes |
|---|---|---|
| `local` | Docker Compose for PostgreSQL, Redis, NATS, MinIO and optionally Ollama; services run from source | fake SMS that prints the code, fake payment provider |
| `staging` | namespace on the cluster | Zarinpal sandbox, seeded demo data, deployed on every merge |

Demo venues in `production` stay in payment `sandbox` mode. `is_demo` lives only in `catalog`; demo orders are cleaned up by a nightly job in `order` that deletes orders of venues the `catalog` snapshot lists as demo (exact method decided in W5-CORE-2 with the order pair). The panel polls every 5 s while `realtime` is down, and every 30 s as a safety net otherwise (section 6.4).
| `production` | namespace on the cluster | demo venues live here with `is_demo = true` |

Start with one server inside Iran running k3s, suggested 8 vCPU, 16 GB RAM, 160 GB SSD, so venues keep working when international connectivity drops. Object storage and CDN from an Iranian cloud provider. TLS with cert-manager. The model server may need its own machine; decide after the week-1 AI evaluation. Image registry reachability from the server is checked in week 1.

Growth path: three nodes, managed PostgreSQL with a replica, Redis with a replica, three NATS nodes.

Backups (W4-PA-1): nightly dump per database into a private bucket `sarmiz-backups`, encrypted with a public key so the backup job cannot decrypt, kept 7 daily and 4 weekly. The mentor stores the payment-credential AES key and the backup decryption key offline; without them restored payment credentials are unreadable. NATS and Redis are not backed up. The runbook lives in `deploy/RUNBOOK.md` (W5-PA-2).

## 16. Scaling and resilience

- All Go services are stateless. In production run at least 2 replicas of `gateway`, `catalog`, `order`, `realtime` and `identity` (1 is acceptable for `ai`), with a HorizontalPodAutoscaler on CPU at 70%.
- `realtime`: every pod subscribes to NATS and serves its own connections, so no sticky sessions are needed.
- Database: a small pgx pool per pod (start with 10), indexes that begin with `venue_id`, PgBouncer and read replicas later.
- Timeouts on every outgoing call. Circuit breakers on gRPC and HTTP clients.
- Heavy AI work runs through a NATS work queue with a concurrency limit.

Behaviour when a part is down:

| Down | What still works | What the user sees |
|---|---|---|
| `ai` | menu, ordering, payment | AI waiter says it is unavailable; translate and import buttons show a retry message |
| `catalog` | existing orders, kitchen screen | menu and new orders unavailable with a clear message |
| `realtime` | everything else | panel falls back to polling every 5 s |
| NATS | orders are still saved | events wait in the outbox; kitchen relies on polling |
| Redis | menu served without cache | OTP login unavailable |
| Payment provider | pay at counter | online payment button shows a retry message |
| PostgreSQL | nothing that writes; cached public menus for up to their TTL | clear "temporarily unavailable" message. Accepted single point of failure in R1; mitigated by backups (RPO 24 h, RTO 4 h) and a managed or replicated database in the growth path |

## 17. Security baseline

- Validate input at the edge (`protovalidate`) and again in the service. SQL only with parameters.
- React escapes output by default; never render user or model text as HTML.
- Headers from the ingress and web server: HSTS, Content-Security-Policy, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `frame-ancestors 'none'`.
- CORS allowlist of the Sarmiz origins only.
- Secrets only in Kubernetes secrets and GitHub secrets. `.env` files are git-ignored; `.env.example` holds names without values.
- Least privilege: one database role per service, NetworkPolicy between pods, non-root containers, read-only root filesystem where possible.
- Audit log for sensitive actions: login, membership change, payment config change, venue status change.
- Personal data: only the owner's name and phone. Guests leave no personal data in R1.
- AI: menu text and guest messages are untrusted input. The assistant has no tools and no side effects, answers only from the venue's menu, and its output is shown as plain text.
- No service fetches a URL supplied by a user.
- Never paste secrets, credentials, production data or real customer data into an AI assistant.

## 18. AI service

Internal HTTP API, protected by a shared secret header and NetworkPolicy:

| Endpoint | Purpose |
|---|---|
| `POST /v1/translate` | input `venue_id`, `source_locale`, `target_locales`, `texts` (each with `key`, `text`, `context`); output translations per key and locale |
| `POST /v1/assistant` | input `venue_id`, `locale`, `message`, `history` (at most 6 turns); output `answer`, `cited_item_ids`, `refused` |
| `GET /healthz`, `GET /readyz`, `GET /metrics` | health and metrics |

Menu import is asynchronous: `ai` consumes `sarmiz.catalog.import.requested`, reads the file from `sarmiz-imports`, extracts a draft menu (categories, items, prices, options) with a confidence score and warnings, and publishes `sarmiz.ai.import.completed`. The owner always reviews the draft before it is applied.

Indexing for the assistant: `ai` consumes `sarmiz.catalog.menu.changed`, reads the menu through `catalog.SnapshotService.GetMenuSnapshot`, and re-embeds changed items into `menu_chunks`. Retrieval combines vector similarity and keyword match, filtered by `venue_id`.

All model access goes through one `LLMProvider` interface (chat, vision, embeddings) with an Ollama implementation. Every model output is validated with Pydantic. Unit tests use a mocked provider. The models are chosen after the week-1 evaluation; the result is recorded in `docs/ai/`.

## 19. Frontend

One Vite app with React and TypeScript in strict mode, Tailwind CSS, React Router, TanStack Query. Route groups are loaded lazily:

| Route | Audience |
|---|---|
| `/` and `/pricing` | landing, prerendered for search engines |
| `/t/:qrToken`, `/m/:slug`, `/o/:orderId` | guest: menu at a table, public menu link, order status |
| `/panel/*` | owner panel, including `/panel/kitchen` |
| `/admin/*` | Tecso admin |

Rules: the API client types are generated from `docs/api/openapi.yaml`; no `any`; Tailwind logical utilities (`ms-`, `me-`, `ps-`, `pe-`, `text-start`) and never left or right; the cart lives in `localStorage` keyed by table; UI languages `fa` (default) and `en`; text direction comes from the locale (`fa`, `ar`, `ckb`, `azb` are right to left); numbers and prices are formatted with `Intl.NumberFormat`; prices are shown in Toman; touch targets at least 44 px; visible focus; WCAG AA contrast; error boundaries report to GlitchTip. Brand tokens are in `docs/brand/README.md`.

## 20. Open decisions

| # | Decision | Needed by |
|---|---|---|
| 1 | Final product name and domain | before week 0 ends |
| 2 | Payment settlement model (section 9) | before week 4 |
| 3 | Hosting provider, and managed PostgreSQL or in-cluster | week 0 |
| 4 | SMS provider | week 0 |
| 5 | Models for translation, vision and embeddings | end of week 1 |
| 6 | Whether the repository stays private (branch protection needs a paid plan for private repositories) | week 0 |
| 7 | Team size: 8 interns in 4 pairs, or 6 with the stretch items moved out | week 0 |
