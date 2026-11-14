<div dir="rtl">

# API و قراردادها

این فصل به یک سؤال جواب می‌دهد: بخش‌های سرمیز (مرورگر، `gateway`، سرویس‌ها و مصرف‌کننده‌های رویداد) با چه قراردادی با هم حرف می‌زنند، و چطور یک قرارداد را عوض کنی بدون اینکه کار بخش دیگری بشکند؟

[بازگشت به فهرست مستندات](../README.md)

## ۱. چرا مهم است

در سرمیز سه نفر هم‌زمان کار می‌کنند و هیچ‌کدام منتظر کد دیگری نمی‌ماند؛ منتظر **قرارداد** او می‌ماند (contract: شکل توافق‌شده‌ی پیام‌ها بین دو طرف). فرانت کلاینتش را از `docs/api/openapi.yaml` می‌سازد، `order` قیمت را از `catalog.PriceItems` می‌گیرد و صفحه‌ی آشپزخانه با رویداد `order.created` زنده می‌شود. اگر یک نفر بی‌خبر نام یک فیلد را عوض کند، سفارش مهمان ثبت می‌شود ولی روی صفحه‌ی آشپزخانه نمی‌آید.

## ۲. تصمیم‌ها در یک نگاه

| موضوع | تصمیم | چرا |
|---|---|---|
| ورودی مرورگر | فقط REST از `gateway` زیر <span dir="ltr">`/api/v1`</span> و WebSocket از `realtime` | یک در ورودی برای توکن، نقش، محدودیت نرخ و CORS |
| بین سرویس‌ها | gRPC با Protobuf برای تماس هم‌زمان؛ رویداد روی NATS JetStream از راه outbox برای ناهم‌زمان | [سند تصمیم ۴](../decisions/0004-nats-jetstream-and-outbox.md) |
| ساخت REST و OpenAPI | grpc-gateway از annotationهای HTTP در proto؛ OpenAPI تولید و در `docs/api/openapi.yaml` commit می‌شود | یک مرجع برای REST، gRPC و تایپ‌های فرانت |
| قالب JSON | `snake_case`، زمان RFC 3339 به UTC، پول عدد صحیح ریال در فیلد `_rial`، شناسه UUID | یک شکل برای همه‌ی مسیرها |
| خطا | یک قالب و نُه کد ثابت | فرانت فقط یک الگوی مدیریت خطا دارد |
| اعتبارسنجی و شکستن | `protovalidate`؛ `buf lint` و `buf breaking` در CI | ورودی بد و تغییر ناسازگار قبل از merge دیده شوند |
| WebSocket | فقط کانال خبر، نه مرجع وضعیت | رویداد گم‌شده نباید سفارش را گم کند |

## ۳. سه نوع قرارداد و مالک هرکدام

| نوع | کجا تعریف می‌شود | مالک | مصرف‌کننده |
|---|---|---|---|
| REST از `gateway` | annotation `google.api.http` در `proto/sarmiz/<service>/v1/*.proto` | صاحب سرویس پشت مسیر؛ middleware با صاحب `gateway` | `web` |
| gRPC بین سرویس‌ها | همان فایل‌های proto | هسته برای `identity` و `catalog` (`W1-CORE-4`)، سفارش برای `order` (`W1-ORD-2`) | `gateway` و تماس‌های مجاز بخش ۴٫۱ مشخصات فنی |
| رویداد | JSON Schema در <span dir="ltr">`proto/events/`</span> | سرویس ناشر | جدول بخش ۱۰ همین فصل |

REST قرارداد جدایی نیست: هر مسیر REST یک متد gRPC با annotation است. متدی که annotation ندارد از بیرون دیده نمی‌شود (مثل `PriceItems`).

## ۴. قواعد REST

| قاعده | مقدار |
|---|---|
| مسیر و بدنه | پیشوند <span dir="ltr">`/api/v1`</span>؛ فقط JSON؛ سقف ۱ مگابایت، و ۶ مگابایت برای بارگذاری |
| نام و زمان | `snake_case`؛ زمان RFC 3339 به UTC مثل `2026-11-10T12:00:00Z`؛ تبدیل به وقت محلی فقط در `web` |
| پول و شناسه | عدد صحیح ریال در فیلد `_rial` (تومان فقط در رابط کاربری)؛ شناسه رشته‌ی UUID |
| فهرست | <span dir="ltr">`?limit=`</span> (پیش‌فرض ۲۰، حداکثر ۱۰۰) و <span dir="ltr">`?cursor=`</span>؛ پاسخ <span dir="ltr">`{"items": [...], "next_cursor": "..."}`</span>. cursor مات است: فرانت آن را نمی‌خواند و نمی‌سازد، فقط برمی‌گرداند |
| idempotency | هدر `Idempotency-Key` روی `POST .../orders` و `POST .../pay`؛ کلید ۲۴ ساعت نگه داشته می‌شود |
| مهمان | هدر `X-Guest-Session` با شناسه‌ی تصادفی مرورگر |

**`Idempotency-Key`** (کلیدی که می‌گوید «این همان درخواست قبلی است»). مهمان دکمه‌ی «ثبت سفارش» را می‌زند، روی اینترنت ضعیف پاسخ نمی‌رسد و دوباره می‌زند. با همان کلید، سرور باید **همان سفارش قبلی** را برگرداند، نه سفارش دوم. کلید در `orders.idempotency_key` ذخیره می‌شود. پیشنهاد اولیه: فرانت برای هر سبد یک UUID می‌سازد و تا موفقیت عوضش نمی‌کند؛ همان کلید با بدنه‌ی دیگر `conflict` می‌گیرد. رفتار دقیق در `W2-ORD-1` نهایی می‌شود.

## ۵. قالب خطا

</div>

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

<div dir="rtl">

| کد | HTTP | کی | کد gRPC (پیشنهاد اولیه) |
|---|---|---|---|
| `validation_failed` | `400` | ورودی نامعتبر؛ `fields` خطای هر فیلد را می‌گوید | `InvalidArgument` |
| `unauthenticated` | `401` | توکن نیست یا منقضی است | `Unauthenticated` |
| `permission_denied` | `403` | نقش برای این مسیر کافی نیست | `PermissionDenied` |
| `not_found` | `404` | نیست، **یا مال کسب‌وکار دیگری است** | `NotFound` |
| `conflict` | `409` | تکراری یا هم‌زمانی، مثل `slug` تکراری | `AlreadyExists`، `Aborted` |
| `failed_precondition` | `422` | درخواست درست است ولی وضعیت اجازه نمی‌دهد: آیتم تمام‌شده، تغییر وضعیت غیرمجاز | `FailedPrecondition` |
| `rate_limited` | `429` | محدودیت نرخ، با هدر `Retry-After` | در خود `gateway` ساخته می‌شود |
| `unavailable` | `503` | سرویس پشتی یا وابستگی در دسترس نیست | `Unavailable`، `DeadlineExceeded` |
| `internal` | `500` | هر چیز پیش‌بینی‌نشده | بقیه‌ی کدها |

ستون آخر را مشخصات فنی تعیین نکرده؛ نگاشت فقط یک بار در `libs/go/kit` (`W1-PA-2`) و `gateway` (`W1-PA-4`) نوشته می‌شود. `message` برای برنامه‌نویس است؛ پیشنهاد اولیه: فرانت متن فارسی را از روی `code` نشان می‌دهد. در پاسخ هیچ‌وقت SQL، stack trace یا نام داخلی نمی‌آید؛ `request_id` برای پیدا کردن خطا در لاگ کافی است.

## ۶. گروه‌های مسیر

| گروه (بعد از <span dir="ltr">`/api/v1`</span>) | ورود | نمونه‌ها | سرویس پشتی |
|---|---|---|---|
| <span dir="ltr">`/auth/*`</span> | ندارد یا کوکی | `POST /auth/otp/request`، `POST /auth/otp/verify`، `POST /auth/refresh`، `POST /auth/logout`، `GET /me` | `identity` |
| <span dir="ltr">`/venues`</span> و <span dir="ltr">`/venues/{venue_id}/*`</span> | کاربر پنل با نقش در همان کسب‌وکار | کسب‌وکار، برندینگ، میزها، دسته‌ها، آیتم‌ها، گروه گزینه‌ها، زمان‌بندی، pairing، بارگذاری، import، ترجمه | `catalog` |
| <span dir="ltr">`/venues/{venue_id}/orders*`</span>، <span dir="ltr">`/service-requests*`</span>، <span dir="ltr">`/reports/*`</span>، <span dir="ltr">`/payment-config`</span> | کاربر پنل | فهرست سفارش، تغییر وضعیت، پرداخت در صندوق، خلاصه‌ی فروش | `order` |
| <span dir="ltr">`/public/t/{qr_token}*`</span>، <span dir="ltr">`/public/m/{slug}`</span> | ندارد | منوی عمومی با میز یا با slug | `catalog` |
| <span dir="ltr">`/public/t/{qr_token}/orders`</span>، <span dir="ltr">`/public/orders/{order_id}*`</span>، <span dir="ltr">`/public/payments/zarinpal/callback`</span>، <span dir="ltr">`/public/t/{qr_token}/service-requests`</span> | ندارد؛ order token هر جا لازم است | ساخت و دیدن سفارش، شروع پرداخت، امتیاز | `order` |
| <span dir="ltr">`/public/t/{qr_token}/assistant`</span> | ندارد | گارسون هوشمند | `catalog` که `ai` را صدا می‌زند |
| <span dir="ltr">`/stream-tickets`</span> | کاربر پنل یا order token | ticket برای WebSocket | `identity` |
| <span dir="ltr">`/admin/*`</span> | ادمین پلتفرم | فهرست کسب‌وکارها، فعال و تعلیق، حالت پرداخت | `catalog`، `order` |

مسیر دقیق هر متد در PR قرارداد همان سرویس نوشته می‌شود و باید با این جدول بخواند؛ مسیری بیرون از این گروه‌ها سند تصمیم می‌خواهد. order token (مقدار تصادفی ۱۲۸ بیتی که فقط یک بار هنگام ساخت سفارش برمی‌گردد) هیچ‌وقت در query string نمی‌آید، چون در لاگ‌ها می‌ماند؛ پیشنهاد اولیه: هدر `X-Order-Token`، نهایی در `W2-ORD-2`.

## ۷. از proto تا REST و OpenAPI

1. متد را در proto بنویس و annotation مسیر را، با پیشوند <span dir="ltr">`/api/v1`</span>، بگذار.
2. `buf lint` و `buf generate` را اجرا کن (دستور دقیق را `W1-PA-3` در `AGENTS.md` می‌نویسد). از یک proto کد Go، handlerهای grpc-gateway، stubهای Python و `docs/api/openapi.yaml` ساخته می‌شوند.
3. `gateway` همین handlerها به‌علاوه‌ی middleware دست‌نویس است و منطق کسب‌وکار ندارد.
4. `openapi.yaml` **در همان PR** commit می‌شود و CI فرقش را با فایل تولیدشده می‌سنجد. بخش فرانت کلاینت تایپ‌دار را از آن می‌سازد (`W1-WEB-5`).

</div>

```proto
rpc GetPublicMenuByTable(GetPublicMenuByTableRequest) returns (PublicMenu) {
  option (google.api.http) = {get: "/api/v1/public/t/{qr_token}"};
}
message GetPublicMenuByTableRequest {
  string qr_token = 1 [(buf.validate.field).string.min_len = 1];
  string locale = 2; // initial proposal: ?locale=en
}
```

<div dir="rtl">

> [!NOTE]
> چند کار در قالب ساده‌ی grpc-gateway جا نمی‌شود: گذاشتن کوکی‌های `sz_at` و `sz_rt` بعد از ورود، redirect مهمان بعد از callback پرداخت، و بارگذاری فایل. این‌ها کار دست‌نویس `gateway` هستند و روششان در `W1-PA-4`، `W2-CORE-3` و `W4-ORD-2` تعیین می‌شود.

## ۸. قواعد gRPC

| قاعده | جزئیات |
|---|---|
| پکیج و مسیر فایل | `sarmiz.<service>.v1` در <span dir="ltr">`proto/sarmiz/<service>/v1/`</span> |
| deadline و تکرار | هر تماس deadline دارد (پیش‌فرض ۲ ثانیه)؛ فقط خواندن‌های idempotent دوباره امتحان می‌شوند، با jitter (فاصله‌ی تصادفی)؛ هر کلاینت پشت circuit breaker |
| اعتبارسنجی | قواعد فیلد با `protovalidate` در خود proto، و دوباره در سرویس |
| شماره‌ی فیلد | هیچ‌وقت دوباره استفاده یا جابه‌جا نمی‌شود؛ فیلد حذف‌شده با <span dir="ltr">`reserved 7;`</span> و <span dir="ltr">`reserved "old_name";`</span> قفل می‌شود |
| بررسی | `buf lint` و `buf breaking` در CI روی هر PR |
| metadata مطمئن | `gateway` روی هر تماس `x-request-id`، `x-user-id`، `x-venue-id`، `x-role`، `x-guest-session` و trace context از نوع W3C را می‌فرستد |

سرویس‌ها به این metadata فقط به این دلیل اعتماد می‌کنند که جز `gateway` کسی به آن‌ها نمی‌رسد (NetworkPolicy)، و با این حال هر query را باز هم با `venue_id` محدود می‌کنند.

## ۹. سرویس‌ها و متدها

| سرویس | سرویس gRPC: متدهای اصلی | چه کسی صدا می‌زند |
|---|---|---|
| `identity` | `AuthService`: RequestOtp، VerifyOtp، RefreshToken، Logout، GetMe، IssueStreamTicket | `gateway` |
| `identity` | `AccessService`: GrantMembership، RevokeMembership، ListMemberships | `GrantMembership` فقط از `catalog` |
| `catalog` | `VenueService`: CreateVenue، GetVenue، UpdateVenue، ListMyVenues، AdminListVenues، AdminSetVenueStatus | `gateway` |
| `catalog` | `TableService`: CRUD، RegenerateQrToken، GetTableQr، ResolveTable | `gateway`؛ `ResolveTable` از `order` |
| `catalog` | `MenuService`: دسته‌ها، آیتم‌ها، گروه گزینه‌ها، زمان‌بندی، pairing، SetItemAvailability، reorder؛ `PublicMenuService`: GetPublicMenuByTable، GetPublicMenuBySlug | `gateway` |
| `catalog` | `MediaService`: UploadImage؛ `ImportService`: CreateImportJob، GetImportJob، ApplyImportJob؛ `TranslationService`: TranslateMenu؛ `AssistantService`: Ask | `gateway` |
| `catalog` | `PricingService`: PriceItems؛ `SnapshotService`: GetMenuSnapshot (هر دو داخلی) | `order`؛ `ai` |
| `order` | `OrderService`: CreateOrder، GetOrder، ListOrders، UpdateOrderStatus، MarkPaidAtCounter، CancelOrder، ValidateOrderToken | `gateway` |
| `order` | `PaymentService`: GetPaymentConfig، SetPaymentConfig، StartPayment، HandleCallback، AdminSetPaymentMode | `gateway` |
| `order` | `ServiceRequestService`: Create، List، Resolve؛ `RatingService`: CreateRating؛ `ReportService`: GetSalesSummary، GetTopItems، GetBusyHours | `gateway` |

`realtime` و `ai` سرویس gRPC ندارند؛ `ai` یک API داخلی HTTP دارد ([فصل ۱۹](19-ai-service.md)). ترتیب تماس برای ticket مهمان در مشخصات فنی نیامده؛ پیشنهاد اولیه: `gateway` اول `order.ValidateOrderToken` و بعد `identity.IssueStreamTicket` را صدا می‌زند، چون `identity` حق تماس با کسی را ندارد (`W2-ORD-4`).

## ۱۰. رویدادها

Subject با الگوی <span dir="ltr">`sarmiz.<service>.<entity>.<event>`</span> روی stream `SARMIZ`:

| Subject | ناشر | مصرف‌کننده | `data` |
|---|---|---|---|
| `sarmiz.catalog.menu.changed` | `catalog` | `ai` | `venue_id`، `menu_version` |
| `sarmiz.catalog.venue.updated` | `catalog` | در انتشار ۱ هیچ | `venue_id` |
| `sarmiz.catalog.import.requested` | `catalog` | `ai` | `job_id`، `venue_id`، `kind`، `file_key`، `locale_hint` |
| `sarmiz.ai.import.completed` | `ai` | `catalog` | `job_id`، `status`، `draft` یا `error` |
| `sarmiz.order.order.created` | `order` | `realtime` | خلاصه‌ی سفارش: شناسه‌ها، کد، برچسب میز، ردیف‌ها، جمع‌ها، وضعیت |
| `sarmiz.order.order.status_changed` | `order` | `realtime` | `order_id`، `venue_id`، `from`، `to` |
| `sarmiz.order.order.paid` | `order` | `realtime` | `order_id`، `venue_id`، `amount_rial`، `method` |
| `sarmiz.order.service_request.created` | `order` | `realtime` | `request_id`، `venue_id`، `table_label`، `type` |
| `sarmiz.order.service_request.resolved` | `order` | `realtime` | `request_id`، `venue_id` |

هر رویداد در یک پاکت (envelope) ثابت است. نمونه‌ی کامل `order.created` برای سفارشی که در صندوق پرداخت می‌شود؛ نام فیلدهای داخل `data` پیشنهاد اولیه است و در JSON Schema آن (`W2-ORD-3`) نهایی می‌شود:

</div>

```json
{
  "id": "0b6f3c1e-8a52-4c3e-9d7a-2f1e5b6c7d80",
  "type": "sarmiz.order.order.created",
  "version": 1,
  "time": "2026-11-10T12:00:00Z",
  "venue_id": "5f0c2a9e-1b3d-4e6f-8a7b-9c0d1e2f3a4b",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "data": {
    "order_id": "9a1b2c3d-4e5f-4a6b-8c7d-0e1f2a3b4c5d", "venue_id": "5f0c2a9e-1b3d-4e6f-8a7b-9c0d1e2f3a4b",
    "table_id": "c3d4e5f6-a7b8-4c9d-8e0f-1a2b3c4d5e6f", "table_label": "12", "code": 42,
    "status": "pending", "payment_method": "counter",
    "lines": [{"item_id": "e1f2a3b4-c5d6-4e7f-8a9b-0c1d2e3f4a5b", "name_snapshot": {"fa": "لاته", "en": "Latte"},
               "quantity": 2, "options_snapshot": [{"name": {"fa": "بزرگ", "en": "Large"}, "price_delta_rial": 50000}],
               "unit_price_rial": 1200000, "line_total_rial": 2400000, "note": ""}],
    "subtotal_rial": 2400000, "total_rial": 2400000
  }
}
```

<div dir="rtl">

- ردیف رویداد در همان تراکنشِ تغییر اصلی در `outbox` نوشته می‌شود و relay منتشرش می‌کند ([فصل ۸](08-database-and-storage.md)). `outbox_lag_seconds` زیر ۶۰ می‌ماند. `trace_id` همان trace درخواست اصلی است.
- هر رویداد ممکن است دو بار برسد؛ مصرف‌کننده با `id` پاکت تکراری را کنار می‌گذارد.
- سفارش آنلاین با `awaiting_payment` شروع می‌شود و آشپزخانه نباید آن را ببیند. مشخصات فنی نگفته `order.created` برای آن منتشر شود یا نه؛ پیشنهاد اولیه: منتشر شود (صفحه‌ی سفارش مهمان لازمش دارد) و صفحه‌ی آشپزخانه آن را تا رسیدن `order.paid` نشان ندهد. در `W2-ORD-3` با بخش فرانت نهایی کن.

## ۱۱. WebSocket

1. کلاینت با `POST /api/v1/stream-tickets` یک ticket می‌گیرد: JWT شصت‌ثانیه‌ای با scope <span dir="ltr">`venue:<venue_id>`</span> برای پنل یا <span dir="ltr">`order:<order_id>`</span> برای مهمان. شکل بدنه در `W2-ORD-4` نوشته می‌شود.
2. به <span dir="ltr">`wss://<host>/ws?ticket=<ticket>`</span> وصل می‌شود. ticket فقط برای لحظه‌ی وصل شدن است.
3. سرور پاکت‌های رویداد را، فیلترشده با scope، می‌فرستد و هر ۲۵ ثانیه ping می‌زند. با قطع اتصال، کلاینت با backoff (فاصله‌ی رو به افزایش) ticket تازه می‌گیرد و دوباره وصل می‌شود.

> [!IMPORTANT]
> WebSocket فقط کانال خبر است. پنل وضعیت واقعی را از `GET /api/v1/venues/{venue_id}/orders` می‌خواند: هنگام وصل شدن، بعد از هر وصل دوباره، و هر ۳۰ ثانیه برای احتیاط. اگر `realtime` پایین باشد، پنل هر ۵ ثانیه polling می‌کند. رویداد گم‌شده هیچ‌وقت نباید سفارش را گم کند.

## ۱۲. نمونه‌ی درخواست و پاسخ

شکل دقیق پاسخ‌ها در PRهای قرارداد هفته‌ی ۱ تعیین می‌شود؛ این‌ها پیشنهاد اولیه‌اند. منوی عمومی، `GET /api/v1/public/t/{qr_token}?locale=en`، با هدرهای `ETag` و `Cache-Control: public, max-age=30, stale-while-revalidate=300`:

</div>

```json
{"venue": {"name": "Sample Cafe", "theme_color": "#1F6F5C", "locale": "en"}, "table_label": "12", "menu_version": 37,
 "categories": [{"id": "…", "name": "Coffee", "items": [{"id": "…", "name": "Latte", "price_rial": 1200000,
   "is_available": true, "badges": ["popular"], "diet_tags": ["vegetarian"], "allergens": ["dairy"]}]}]}
```

<div dir="rtl">

ساخت سفارش، `POST /api/v1/public/t/{qr_token}/orders` با هدرهای `Idempotency-Key` و `X-Guest-Session`. در بدنه **هیچ قیمتی نیست**؛ سرور با `PriceItems` حساب می‌کند. اول درخواست، بعد پاسخ موفق، و آخر خطا وقتی یک آیتم همین الان تمام شده:

</div>

```json
{"payment_method": "counter", "locale": "fa", "items": [{"item_id": "…", "quantity": 2, "option_ids": ["…"], "note": ""}]}
{"order": {"id": "…", "code": 42, "status": "pending", "payment_status": "unpaid", "total_rial": 2400000}, "order_token": "…"}
{"error": {"code": "failed_precondition", "message": "item is not available", "request_id": "01JC..."}}
```

<div dir="rtl">

## ۱۳. تغییر امن قرارداد

| | نمونه |
|---|---|
| سازگار | فیلد تازه با شماره‌ی تازه، متد تازه، مقدار تازه در enum (مصرف‌کننده مقدار ناشناخته را تحمل می‌کند)، فیلد تازه در `data` رویداد |
| ناسازگار | حذف، تغییر نام، نوع یا شماره‌ی فیلد؛ عوض کردن مسیر HTTP؛ اجباری کردن فیلد اختیاری؛ تغییر معنای فیلد با همان نام |

1. اول راه سازگار را امتحان کن: فیلد تازه کنار فیلد قدیمی، و قدیمی با `deprecated = true` تا انتشار بعد.
2. اگر نشد: پکیج `v2` برای proto یا `version` بالاتر برای رویداد که مدتی کنار نسخه‌ی قبلی منتشر می‌شود. این سند تصمیم و تأیید منتور می‌خواهد.
3. تغییر قرارداد در PR جدا از پیاده‌سازی می‌آید و `openapi.yaml` و JSON Schema را هم‌زمان به‌روز می‌کند.

| تغییر در | می‌نویسد | باید بازبینی کند |
|---|---|---|
| proto `identity` یا `catalog` | هسته | فرانت، سفارش، پلتفرم |
| proto `order` | سفارش | فرانت، پلتفرم |
| JSON Schema یک رویداد | ناشر | همه‌ی مصرف‌کننده‌ها |
| هر چیزی در ورود یا پرداخت، یا تغییر ناسازگار | صاحب سرویس | به‌علاوه‌ی منتور |

## چک‌لیست انتشار ۱

- [ ] هر مسیر REST با جدول گروه‌های مسیر می‌خواند، `docs/api/openapi.yaml` با proto یکی است، و `buf lint` و `buf breaking` در CI اجباری و سبزند.
- [ ] همه‌ی خطاها، حتی panic و timeout، با قالب واحد و یکی از نُه کد و با `request_id` برمی‌گردند و هیچ‌کدام SQL یا نام داخلی نشان نمی‌دهد.
- [ ] `Idempotency-Key` روی ساخت سفارش و پرداخت با درخواست تکراریِ هم‌زمان تست شده است.
- [ ] هر رویداد یک JSON Schema در <span dir="ltr">`proto/events/`</span> دارد و تست، نمونه‌ی منتشرشده را با آن می‌سنجد.
- [ ] با خاموش کردن `realtime`، پنل با polling کار می‌کند و سفارشی گم نمی‌شود.
- [ ] order token در هیچ URL و هیچ لاگی نیست.

## اشتباه‌های رایج

| اشتباه | چرا بد است | چه کار کن |
|---|---|---|
| ویرایش دستی `openapi.yaml` | با `buf generate` بعدی پاک می‌شود و کلاینت فرانت دروغ می‌گوید | proto را عوض کن و دوباره بساز |
| استفاده‌ی دوباره از شماره‌ی فیلد حذف‌شده | کلاینت قدیمی داده‌ی اشتباه می‌خواند، بی‌صدا | `reserved` |
| فرستادن قیمت یا جمع از مرورگر | مهمان قیمت را عوض می‌کند | فقط `item_id`، `quantity` و `option_ids` |
| `permission_denied` برای منبع کسب‌وکار دیگر | می‌شود شناسه‌ها را حدس زد | `not_found` |
| فرض اینکه هر رویداد دقیقاً یک بار می‌رسد | سفارش دو بار روی صفحه‌ی آشپزخانه می‌آید | dedupe با `id` پاکت |
| تکیه‌ی پنل فقط به WebSocket | با یک قطعی کوتاه سفارش دیده نمی‌شود | بارگذاری دوباره بعد از هر وصل و هر ۳۰ ثانیه |
| مسیر تازه بیرون از گروه‌ها | `gateway` نقش را برایش بررسی نمی‌کند | از جدول گروه‌ها پیروی کن یا سند تصمیم بنویس |

## کار با AI روی این موضوع

**فایل‌هایی که به دستیار می‌دهی:** `AGENTS.md`، بخش ۶ از `docs/SPEC.md`، همین فصل، `proto/README.md`، و فایل proto یا JSON Schema که عوض می‌کنی.

</div>

```text
این فایل proto را برای سرویس catalog بخوان. بخش ۶٫۱ و ۶٫۲ از docs/SPEC.md و docs/guide/06-api-and-contracts.md را هم بخوان.
بررسی کن: ۱. هر مسیر HTTP با جدول route groups می‌خواند؟ ۲. نام‌ها snake_case و پول int64 با پسوند _rial است؟
۳. فیلدی هست که protovalidate ندارد ولی باید داشته باشد؟ ۴. نسبت به main تغییری هست که buf breaking را می‌شکند؟
مسیر، متد یا فیلدی که در مشخصات فنی نیست پیشنهاد نده؛ فقط بگو کجا تصمیم لازم است.
```

```text
برای رویداد sarmiz.order.order.paid یک JSON Schema در proto/events/ بنویس که envelope بخش ۶٫۳ را دارد
و data آن دقیقاً order_id، venue_id، amount_rial و method است. بعد یک تست Go بنویس که یک نمونه را با schema بسنجد.
بگو کدام فیلدها required هستند و چرا.
```

<div dir="rtl">

**خودت حتماً بررسی کن:** `buf breaking` را خودت اجرا کن و خروجی‌اش را بخوان. یک درخواست واقعی با `curl` به `staging` بزن و پاسخ را با `openapi.yaml` مقایسه کن. دستیار معمولاً مسیر یا فیلد «منطقی» از خودش می‌سازد؛ هر نامی را با بخش ۶ مشخصات فنی تطبیق بده.

## بیشتر بخوان

- [مشخصات فنی](../SPEC.md): بخش ۴٫۱ و ۴٫۳ (ارتباط و جریان‌ها)، ۶ (قراردادها)، ۸ (ورود و metadata)، ۱۰ (محدودیت نرخ)، ۱۱ (کش منوی عمومی).
- [فصل ۷: منطق بک‌اند و سرویس‌ها](07-backend-services.md) و [فصل ۸: دیتابیس و ذخیره‌سازی](08-database-and-storage.md).
- [فصل ۵: فرانت](05-frontend.md)، [فصل ۹: ورود و دسترسی](09-auth-and-permissions.md)، [فصل ۱۱: محدودیت نرخ](11-rate-limiting.md)، [فصل ۱۲: کش و CDN](12-caching-and-cdn.md)، [فصل ۱۷: تست](17-testing.md).
- [راهنمای API](../api/README.md)، [پوشه‌ی proto](../../proto/README.md)، [سند تصمیم ۴](../decisions/0004-nats-jetstream-and-outbox.md).

</div>
