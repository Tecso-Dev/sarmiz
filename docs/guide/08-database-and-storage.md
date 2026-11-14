<div dir="rtl">

# دیتابیس و ذخیره‌سازی

این فصل به یک سؤال جواب می‌دهد: داده‌ی سرمیز کجا و با چه قاعده‌ای ذخیره می‌شود، و چطور schema (ساختار جدول‌ها) را عوض کنی بدون اینکه چیزی بشکند یا داده‌ی یک کسب‌وکار به دیگری نشت کند؟

[بازگشت به فهرست مستندات](../README.md)

## ۱. چرا مهم است

کد را می‌شود دوباره نوشت، ولی منوی یک کافه و سفارش‌های دیشبش را نه. در سرمیز ده‌ها کسب‌وکار در یک دیتابیس کنار هم هستند؛ یک query بدون `venue_id` یعنی سفارش‌های یک کافه روی صفحه‌ی آشپزخانه‌ی کافه‌ی دیگر. پول هم در همین جدول‌هاست: اگر تأیید پرداخت و وضعیت سفارش در یک تراکنش نباشند، مهمان پول داده و آشپزخانه چیزی ندیده است. این فصل قاعده‌هایی را می‌گوید که جلوی این اتفاق‌ها را می‌گیرند.

## ۲. تصمیم‌ها در یک نگاه

| موضوع | تصمیم | چرا |
|---|---|---|
| دیتابیس | یک سرور PostgreSQL با چهار دیتابیس `identity`، `catalog`، `orders` و `ai`؛ هر کدام با نقش (role) خودش | هر سرویس مالک داده‌ی خودش است، ولی تیم کوچک فقط یک سرور نگه می‌دارد |
| مرز سرویس‌ها | هیچ سرویسی دیتابیس سرویس دیگر را نمی‌خواند؛ ارجاع بین سرویس‌ها UUID ساده و بدون foreign key است | [سند تصمیم ۳](../decisions/0003-database-per-service.md) |
| شناسه و زمان | هر جدول `id uuid primary key`، `created_at` و `updated_at` دارد، مگر جایی که گفته شده | شناسه‌ی حدس‌نزدنی و ردگیری تغییرها |
| جداسازی کسب‌وکارها | هر جدولِ متعلق به کسب‌وکار `venue_id uuid not null` و ایندکسی دارد که با آن شروع می‌شود | همه‌ی queryها با `venue_id` فیلتر می‌شوند و باید سریع بمانند |
| متن چندزبانه | JSONB با کلید زبان؛ `fa` اجباری است | [سند تصمیم ۵](../decisions/0005-i18n-as-jsonb.md) |
| پول | `bigint` به ریال؛ رابط کاربری تومان نشان می‌دهد (ریال تقسیم بر ۱۰) | عدد اعشاری در پول خطای گرد کردن می‌سازد |
| سفارش | ردیف‌های سفارش snapshot (رونوشت لحظه‌ای) نام، قیمت و گزینه‌ها را نگه می‌دارند | ویرایش بعدی منو سفارش قدیمی را عوض نکند |
| migration | goose، یک پوشه برای هر سرویس، با الگوی expand-then-contract | برگرداندن کد همیشه بی‌خطر باشد |
| رویداد | ردیف `outbox` در همان تراکنشِ تغییر اصلی نوشته می‌شود | [سند تصمیم ۴](../decisions/0004-nats-jetstream-and-outbox.md) |
| Redis | محدودیت نرخ، کش و کد یک‌بارمصرف | داده‌ی کوتاه‌عمری که دوباره ساخته یا دوباره خواسته می‌شود |
| فایل | object storage سازگار با S3 با دو bucket؛ در محیط محلی MinIO | تصویر باید از CDN برسد، نه از دیتابیس |

## ۳. یک سرور، چهار دیتابیس، چهار نقش

| سرویس | دیتابیس | چه چیزی در آن است |
|---|---|---|
| `identity` | `identity` | کاربران پنل، نقش‌ها، توکن‌های تازه‌سازی |
| `catalog` | `catalog` | کسب‌وکار، شعبه، میز، منو، تصویر، کارهای import |
| `order` | `orders` | سفارش، پرداخت، درخواست خدمت، امتیاز |
| `ai` | `ai` (با افزونه‌ی pgvector) | تکه‌های منو برای جست‌وجوی دستیار |
| `gateway` و `realtime` | ندارند | `gateway` فقط از Redis استفاده می‌کند |

دقت کن: نام سرویس `order` است ولی نام دیتابیسش `orders`.

- نقش هر سرویس فقط به دیتابیس خودش می‌رسد. اگر کد `order` اشتباهی بخواهد جدول `menu_items` را بخواند، PostgreSQL جلویش را می‌گیرد، نه بازبین PR.
- ارجاع بین سرویس‌ها فقط UUID است. `orders.table_id` به میزی در `catalog` اشاره می‌کند ولی foreign key ندارد؛ برای همین `order` برچسب میز را در `table_label` رونویسی می‌کند. داخل یک دیتابیس، foreign key عادی است (مثل `order_items.order_id`).
- چیزی که از سرویس دیگر لازم داری را با gRPC بگیر (`catalog.ResolveTable`، `catalog.PriceItems`)، نه با JOIN.

</div>

```sql
-- example only: W1-PA-1 picks the real role names and passwords come from secrets
CREATE ROLE catalog_svc LOGIN;
CREATE DATABASE catalog OWNER catalog_svc;
REVOKE CONNECT ON DATABASE catalog FROM PUBLIC;
```

<div dir="rtl">

در `W1-CORE-1` باید با یک تست نشان بدهی که نقش یک سرویس نمی‌تواند به دیتابیس سرویس دیگر وصل شود. هر pod یک pool کوچک pgx دارد (شروع با ۱۰ اتصال).

## ۴. قاعده‌هایی که برای همه‌ی جدول‌ها یکی است

1. **شناسه و زمان.** `id uuid primary key`، `created_at` و `updated_at`. استثنا: `payment_configs` که کلید اصلی‌اش خود `venue_id` است.
2. **`venue_id`.** هر جدولِ متعلق به کسب‌وکار این ستون را `not null` دارد، حتی جدول‌های فرزند مثل `options` و `order_items`. هر متد repository آن را می‌گیرد و در `WHERE` می‌گذارد.
3. **ایندکس.** دست‌کم یک ایندکس که با `venue_id` شروع شود.
4. **متن چندزبانه.** متنی که مهمان می‌بیند JSONB است، مثل <span dir="ltr">`{"fa": "لاته", "en": "Latte"}`</span>. `fa` اجباری است. ترتیب خواندن: زبان خواسته‌شده، بعد `venues.default_locale`، بعد `fa`.
5. **پول.** فقط `bigint` به ریال، در ستون‌هایی که به `_rial` ختم می‌شوند. تبدیل به تومان فقط در `web`.
6. **snapshot.** `order_items` ستون‌های `name_snapshot`، `unit_price_rial`، `options_snapshot` و `line_total_rial` را دارد و `orders` ستون `table_label` را. سفارش هیچ‌وقت برای نمایش به منوی فعلی نگاه نمی‌کند.
7. **نسخه‌ی منو.** هر تغییر در منو، موجودی یا زمان‌بندی، `venues.menu_version` را در همان تراکنش یکی بالا می‌برد.

ترتیب خواندن زبان در SQL این شکلی است (فقط برای دیدن ایده):

</div>

```sql
-- $2 = requested locale, $3 = venues.default_locale
SELECT id, COALESCE(name->>$2, name->>$3, name->>'fa') AS name, price_rial
FROM menu_items
WHERE venue_id = $1 AND is_active;
```

<div dir="rtl">

## ۵. جدول‌های هر سرویس

ستون‌های کامل در بخش ۷ [مشخصات فنی](../SPEC.md) است. اینجا فقط می‌گوییم هر جدول برای چیست. این طرحِ پایه است؛ بخش‌ها در `W1-CORE-1` و `W1-ORD-1` آن را نهایی می‌کنند و هر تفاوت یک سند تصمیم می‌خواهد.

**`identity`**

| جدول | برای چه |
|---|---|
| `users` | کاربر پنل: `phone` یکتا به قالب E.164، `name`، `is_platform_admin` |
| `memberships` | نقش کاربر در یک کسب‌وکار (`owner`، `manager`، `staff`)؛ یکتا روی (`user_id`، `venue_id`) |
| `refresh_tokens` | hash توکن تازه‌سازی، `family_id`، `expires_at`، `revoked_at`، `user_agent`، `ip` |
| `audit_log` | کار حساس را چه کسی و کی انجام داد |

کد یک‌بارمصرف در PostgreSQL نیست؛ فقط در Redis است (بخش ۱۰).

**`catalog`**

| جدول | برای چه |
|---|---|
| `venues` | حساب کسب‌وکار: `slug` یکتا، نام، نوع، لوگو و رنگ، زبان‌ها، `status`، `is_demo`، `menu_version` |
| `branches` | مکان فیزیکی. انتشار ۱ برای هر کسب‌وکار دقیقاً یکی می‌سازد |
| `dining_tables` | میز و `qr_token` تصادفی و یکتای آن |
| `menu_categories`، `menu_items` | دسته‌ها و آیتم‌های منو با قیمت، برچسب‌ها، موجودی و ترتیب |
| `option_groups`، `options` | گزینه‌های آیتم (اندازه، افزودنی) با `min_select`، `max_select` و `price_delta_rial` |
| `menu_schedules` | منوی زمان‌دار: روزهای هفته و ساعت شروع و پایان |
| `item_pairings` | پیشنهاد «با این می‌چسبد» |
| `media` | مشخصات هر تصویر در object storage |
| `import_jobs` | کار import منو از عکس یا Excel، وضعیت و پیش‌نویس آن |
| `outbox`، `audit_log` | رویدادهای در صف انتشار، و ثبت کارهای حساس |

مقدارهای مجاز `diet_tags`، `allergens` و `badges` در بخش ۷٫۲ مشخصات فنی ثابت شده‌اند.

**`orders`**

| جدول | برای چه |
|---|---|
| `orders` | سفارش: میز، `code` روزانه، وضعیت، روش و وضعیت پرداخت، جمع‌ها، `guest_session_id`، `order_token_hash`، `idempotency_key`، `expires_at` |
| `order_items` | ردیف‌های سفارش با snapshot |
| `payments` | هر تلاش پرداخت: `authority` یکتا، `amount_rial`، `status`، `ref_id`، پاسخ درگاه |
| `payment_configs` | تنظیم پرداخت هر کسب‌وکار: `mode`، `credentials_enc` رمزشده |
| `service_requests` | صدا زدن گارسون و درخواست صورت‌حساب |
| `ratings` | امتیاز بعد از سفارش؛ `order_id` یکتا |
| `daily_counters` | آخرین `code` هر کسب‌وکار در هر روز |
| `outbox`، `processed_events`، `audit_log` | رویدادهای خروجی، رویدادهای پردازش‌شده، ثبت کارهای حساس |

**`ai`**

| جدول | برای چه |
|---|---|
| `menu_chunks` | متن هر آیتم به هر زبان، با `embedding` و `menu_version`، برای جست‌وجوی دستیار |

## ۶. migration با goose و الگوی expand-then-contract

goose فایل‌های SQL شماره‌دار را به ترتیب اجرا می‌کند. هر سرویس پوشه‌ی خودش را دارد: <span dir="ltr">`services/<name>/migrations/`</span>. در استقرار، migration به شکل یک job از نوع pre-upgrade در Helm اجرا می‌شود، یعنی **قبل** از بالا آمدن کد تازه. برگرداندن هم `helm rollback` است که فقط کد را عقب می‌برد، نه schema را.

نتیجه: هر migration باید با **نسخه‌ی قبلی کد** هم کار کند. الگوی expand-then-contract همین را تضمین می‌کند: اول اضافه کن، بعد کد را عوض کن، آخر سر حذف کن.

مثال فرضی (چنین تصمیمی گرفته نشده): می‌خواهی ستون `note` در `orders` را به `guest_note` تغییر نام بدهی.

| قدم | چه کاری | در کدام انتشار |
|---|---|---|
| ۱. expand | ستون `guest_note` را nullable اضافه کن | migration اول |
| ۲. کد | در هر دو ستون بنویس؛ از ستون تازه بخوان و اگر خالی بود از قدیمی | همان انتشار |
| ۳. backfill | ردیف‌های قدیمی را دسته‌دسته پر کن | migration دوم |
| ۴. کد | فقط با ستون تازه کار کن | انتشار بعد |
| ۵. contract | ستون `note` را حذف کن | یک انتشار بعدتر |

</div>

```sql
-- services/order/migrations/00012_orders_add_guest_note.sql (example)
-- +goose Up
ALTER TABLE orders ADD COLUMN guest_note text;

-- +goose Down
ALTER TABLE orders DROP COLUMN guest_note;
```

<div dir="rtl">

قاعده‌های کوتاه:

- migrationی که ادغام شده را ویرایش نکن؛ یک فایل تازه بنویس.
- تغییر نام و حذف مستقیم ممنوع است؛ همیشه از مسیر بالا برو.
- ستون `not null` تازه: اول nullable، بعد backfill، بعد `SET NOT NULL`.
- هر migration را روی دیتابیس خالی با `up` و `down` امتحان کن.

## ۷. ایندکس و خواندن plan

queryهای داغ سرمیز این‌ها هستند:

| query | کی اجرا می‌شود | ایندکس |
|---|---|---|
| میز از روی `qr_token` | هر اسکن (بعد از آن ۵ دقیقه در Redis) | یکتایی `qr_token` |
| ساخت منوی عمومی یک کسب‌وکار | فقط وقتی کش Redis خالی است | پیشنهاد اولیه: <span dir="ltr">`menu_items (venue_id, category_id, sort_order)`</span> |
| سفارش‌های یک کسب‌وکار با وضعیت | صفحه‌ی آشپزخانه: هنگام وصل شدن، بعد از هر وصل دوباره، و هر ۳۰ ثانیه | پیشنهاد اولیه: <span dir="ltr">`orders (venue_id, status, created_at)`</span> |
| پرداخت از روی `authority` | callback درگاه | یکتایی `authority` |

ترکیب دقیق ستون‌ها را مشخصات فنی تعیین نکرده؛ فقط گفته ایندکس با `venue_id` شروع شود. پیشنهادهای بالا را با `EXPLAIN` روی داده‌ی واقعی‌نما بسنج:

</div>

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, code, status, total_rial
FROM orders
WHERE venue_id = '00000000-0000-0000-0000-000000000001'
  AND status IN ('pending', 'accepted', 'preparing', 'ready')
ORDER BY created_at DESC
LIMIT 20;
```

<div dir="rtl">

| در خروجی می‌بینی | یعنی چه | چه کار کن |
|---|---|---|
| `Seq Scan on orders` | کل جدول خوانده می‌شود | ایندکسی که با `venue_id` شروع شود نیست، یا شرط با آن جور نیست |
| `Index Scan` با <span dir="ltr">`Index Cond: (venue_id = ...)`</span> | خوب است | کاری لازم نیست |
| `Rows Removed by Filter` بزرگ | ایندکس فقط بخشی از شرط را می‌پوشاند | ستون بعدی شرط را به ایندکس اضافه کن |
| گره‌ی `Sort` جدا | مرتب‌سازی بعد از خواندن انجام می‌شود | ستون مرتب‌سازی را آخر ایندکس بگذار |
| فاصله‌ی زیاد تخمین `rows` با مقدار واقعی | آمار جدول کهنه است | <span dir="ltr">`ANALYZE orders;`</span> |
| `actual time` | زمان واقعی به میلی‌ثانیه | با هدف‌های بخش ۳ مشخصات فنی مقایسه کن |

> [!TIP]
> روی جدول ده‌ردیفه PostgreSQL به‌درستی `Seq Scan` انتخاب می‌کند. plan را بعد از اجرای اسکریپت داده‌ی نمونه (`W2-PA-5`) و در آزمون بار (`W3-PA-3`) بخوان، نه روی دیتابیس خالی.

برای فهرست‌ها از `OFFSET` استفاده نکن. صفحه‌بندی سرمیز با cursor است؛ cursor را از (`created_at`، `id`) آخرین ردیف بساز تا query همیشه از ایندکس برود.

## ۸. تراکنش و قفل ردیف

| کجا | چه چیزهایی باید با هم ثبت شوند |
|---|---|
| `CreateVenue` | کسب‌وکار و شعبه‌ی پیش‌فرض |
| هر تغییر منو | خود تغییر، بالا رفتن `menu_version`، ردیف `outbox` برای `menu.changed` |
| `CreateOrder` | سفارش، ردیف‌هایش، `code` روزانه، ردیف `outbox` برای `order.created` |
| `HandleCallback` | پرداخت `verified`، سفارش `paid` و `pending`، ردیف `outbox` برای `order.paid` |

**شمارنده‌ی روزانه.** `SELECT max(code) + 1` زیر بار دو سفارش با یک کد می‌سازد. با یک دستور اتمی بشمار، در همان تراکنش سفارش:

</div>

```sql
INSERT INTO daily_counters (venue_id, day, last_code)
VALUES ($1, $2, 1)
ON CONFLICT (venue_id, day)
DO UPDATE SET last_code = daily_counters.last_code + 1
RETURNING last_code;
```

<div dir="rtl">

این دستور به یکتایی (`venue_id`، `day`) نیاز دارد. مرز «روز» در مشخصات فنی نیامده؛ پیشنهاد اولیه وقت تهران است و در `W1-ORD-1` نهایی می‌شود.

**callback پرداخت.** درگاه ممکن است callback را دو بار بفرستد و job تطبیق هم هم‌زمان همان پرداخت را بررسی کند. قفل ردیف نمی‌گذارد دو نفر با هم جلو بروند:

</div>

```sql
BEGIN;
SELECT id, order_id, venue_id, amount_rial, status
FROM payments WHERE authority = $1 FOR UPDATE;
-- already verified: return the same result. Otherwise verify with the stored amount_rial, then:
UPDATE payments SET status = 'verified', ref_id = $2, verified_at = now() WHERE id = $3;
UPDATE orders SET payment_status = 'paid', status = 'pending' WHERE id = $4 AND venue_id = $5;
INSERT INTO outbox (event_id, subject, payload) VALUES ($6, 'sarmiz.order.order.paid', $7);
COMMIT;
```

<div dir="rtl">

> [!IMPORTANT]
> تراکنش را کوتاه نگه دار و وسط آن سرویس دیگری را صدا نزن. تنها جایی که قاعده‌ی ۳ بخش ۹ مشخصات فنی قفل را هنگام یک تماس بیرونی (verify درگاه) نگه می‌دارد همین‌جاست. آن تماس timeout کوتاه می‌خواهد و طرحش در `W3-ORD-4` با منتور نهایی می‌شود.

برای تغییر وضعیت سفارش، وضعیت قبلی را در شرط بگذار (<span dir="ltr">`... WHERE id = $1 AND venue_id = $2 AND status = $3`</span>) و تعداد ردیف‌های تغییرکرده را بررسی کن. اگر صفر بود، کس دیگری زودتر وضعیت را عوض کرده است.

## ۹. `outbox` و `processed_events`

اگر اول سفارش را ذخیره کنی و بعد رویداد را به NATS بفرستی، با یک قطعی بین این دو، سفارشی داری که آشپزخانه هیچ‌وقت خبرش را نمی‌گیرد. راه‌حل: ردیف رویداد را در جدول `outbox` (`event_id`، `subject`، `payload`، `sent_at`) در همان تراکنش بنویس. یک حلقه‌ی relay ردیف‌های فرستاده‌نشده را منتشر می‌کند و `sent_at` را پر می‌کند.

- relay ممکن است یک رویداد را دو بار بفرستد (بعد از انتشار و قبل از ثبت `sent_at` از کار بیفتد). برای همین مصرف‌کننده `id` رویداد را نگه می‌دارد و تکراری را کنار می‌گذارد؛ جدول `processed_events` برای همین است.
- از هر سرویس دست‌کم دو نسخه اجرا می‌شود، پس دو relay هم‌زمان داری. پیشنهاد اولیه: ردیف‌ها را با `FOR UPDATE SKIP LOCKED` بردار تا هر ردیف را فقط یکی بفرستد.
- متریک `outbox_lag_seconds` باید زیر ۶۰ بماند؛ بالاتر از آن هشدار می‌دهد.
- ستون‌های `processed_events` و زمان پاک کردن ردیف‌های قدیمی هر دو جدول در مشخصات فنی نیامده است. این‌ها در `W1-ORD-4` تصمیم گرفته می‌شوند.

## ۱۰. Redis

| چه چیزی | سرویس | کلید | TTL | اگر پاک شود |
|---|---|---|---|---|
| کد یک‌بارمصرف (hash کد و شمارنده‌ی تلاش) | `identity` | <span dir="ltr">`otp:{phone}`</span> | ۱۲۰ ثانیه | کاربر دوباره کد می‌خواهد |
| مدل خواندن منوی عمومی | `catalog` | <span dir="ltr">`menu:{venue_id}:{locale}:{menu_version}`</span> | ۲۴ ساعت | از PostgreSQL دوباره ساخته می‌شود |
| نگاشت `qr_token` به میز | `catalog` | نامش در مشخصات فنی نیامده | ۵ دقیقه | از `dining_tables` خوانده می‌شود |
| شمارنده‌های محدودیت نرخ | `gateway` | [فصل ۱۱](11-rate-limiting.md) | به اندازه‌ی پنجره | شمارش از نو شروع می‌شود |

> [!WARNING]
> Redis هیچ‌وقت تنها نسخه‌ی داده‌ی مهم نیست. قبل از نوشتن هر کلید بپرس: «اگر همین الان Redis خالی شود چه می‌شود؟» جواب فقط می‌تواند «دوباره ساخته می‌شود» یا «کاربر دوباره درخواست می‌دهد» باشد. سفارش، پرداخت، نقش و `Idempotency-Key` سفارش (ستون `orders.idempotency_key`) در PostgreSQL هستند.

وقتی Redis پایین است، منو بدون کش از PostgreSQL می‌آید و ورود با کد از کار می‌افتد. هر کلید TTL دارد؛ کلید بدون TTL ننویس.

## ۱۱. object storage

| bucket | چه چیزی | دسترسی | کلید و نگه‌داری |
|---|---|---|---|
| `sarmiz-media` | تصویر آیتم، لوگو، کاور | خواندن عمومی از راه CDN | `v/{venue_id}/{sha256}-{width}.webp` |
| `sarmiz-imports` | عکس منوی کاغذی و فایل Excel | خصوصی | بعد از ۳۰ روز حذف می‌شود |

مسیر بارگذاری تصویر (`W2-CORE-3`):

1. `gateway` بدنه‌ی بزرگ‌تر از ۶ مگابایت را رد می‌کند و هر کاربر ۳۰ بارگذاری در ساعت دارد.
2. `catalog` فایل بزرگ‌تر از ۵ مگابایت را نمی‌پذیرد.
3. نوع فایل از روی **محتوا** بررسی می‌شود، نه پسوند یا هدر `Content-Type`: فقط JPEG، PNG یا WebP.
4. تصویر decode و دوباره به WebP در سه عرض ۳۲۰، ۸۰۰ و ۱۶۰۰ ساخته می‌شود. این کار metadata مثل موقعیت GPS را هم پاک می‌کند.
5. خروجی‌ها با کلید بالا در `sarmiz-media` می‌نشینند و مشخصاتشان در جدول `media` ثبت می‌شود.

چون hash محتوا در کلید است، تصویر تازه کلید تازه می‌گیرد و کلید قدیمی هیچ‌وقت عوض نمی‌شود. همین اجازه می‌دهد CDN تصویر را برای همیشه نگه دارد ([فصل ۱۲](12-caching-and-cdn.md)).

فایل‌های import را فقط `catalog` می‌نویسد و `ai` می‌خواند؛ کلیدشان در `import_jobs.file_key` است. مشخصات فنی نگفته حذف ۳۰ روزه با چه سازوکاری است؛ پیشنهاد اولیه قاعده‌ی lifecycle خود bucket است (`W2-PA-2`). این هم که برای سه عرض یک ردیف `media` ساخته شود یا سه ردیف، در `W2-CORE-3` تصمیم گرفته می‌شود.

## ۱۲. جای انتشار ۲ و ۳ در schema

این ستون‌ها از همین حالا هستند تا بعداً migration سنگین لازم نشود. در انتشار ۱ قابلیتی رویشان نساز.

| در schema | در انتشار ۱ | برای بعد |
|---|---|---|
| `branches` و ستون `branch_id` در `dining_tables`، `orders` و `service_requests` | دقیقاً یک شعبه برای هر کسب‌وکار | چندشعبه‌ای |
| `memberships.role` با سه مقدار | رابط کاربری فقط `owner` می‌سازد، ولی بررسی‌ها هر سه را می‌شناسند | مدیریت کارکنان |
| `orders.type` | فقط `dine_in` | `pickup` و `delivery` کنار گذاشته شده‌اند |
| `orders.guest_session_id` | شناسه‌ی تصادفی مرورگر | هویت اختیاری مهمان |
| `payments.provider` و `payment_configs.provider` | یک درگاه | درگاه‌های دیگر |

## چک‌لیست انتشار ۱

- [ ] نقش هر سرویس فقط به دیتابیس خودش وصل می‌شود و تستش در CI هست.
- [ ] هر جدولِ متعلق به کسب‌وکار `venue_id` و ایندکسی دارد که با آن شروع می‌شود.
- [ ] هیچ ستون پولی غیر از `bigint` نیست.
- [ ] همه‌ی migrationها روی دیتابیس خالی `up` و `down` می‌شوند و با نسخه‌ی قبلی کد سازگارند.
- [ ] plan queryهای داغ بخش ۷ روی داده‌ی آزمون بار بررسی شده و `Seq Scan` روی جدول بزرگ ندارد.
- [ ] تست هم‌زمانی برای `code` روزانه و برای callback تکراری پرداخت وجود دارد.
- [ ] `outbox_lag_seconds` در `staging` زیر ۶۰ است.
- [ ] `sarmiz-imports` خصوصی است و حذف ۳۰ روزه‌اش کار می‌کند.
- [ ] پشتیبان شبانه‌ی هر چهار دیتابیس گرفته و یک بار بازیابی شده است ([فصل ۲۱](21-backup-and-recovery.md)).

## اشتباه‌های رایج

| اشتباه | چرا بد است | چه کار کن |
|---|---|---|
| query بدون `venue_id` چون «`id` که یکتاست» | هر کس با داشتن یک شناسه داده‌ی کسب‌وکار دیگر را می‌گیرد | همیشه `WHERE id = $1 AND venue_id = $2` |
| `float` یا `numeric` برای پول، یا ذخیره به تومان | جمع‌ها با درگاه نمی‌خواند | `bigint` به ریال |
| نمایش سفارش قدیمی با JOIN به منوی فعلی | با تغییر قیمت، سفارش دیروز عوض می‌شود | از ستون‌های snapshot بخوان |
| حذف یا تغییر نام ستون در یک قدم | کد قبلی هنگام استقرار یا rollback می‌شکند | expand-then-contract |
| فرستادن رویداد به NATS بیرون از تراکنش | سفارش ثبت می‌شود ولی رویدادش گم می‌شود | `outbox` |
| نگه داشتن تنها نسخه‌ی یک داده در Redis | با یک restart از بین می‌رود | مرجع PostgreSQL است |
| اعتماد به پسوند فایل در بارگذاری | فایل مخرب با نام `menu.jpg` | بررسی محتوا و ساخت دوباره‌ی تصویر |
| ایندکس برای هر ستون «محض احتیاط» | نوشتن کند می‌شود | فقط برای queryی که plan آن را دیده‌ای |

## کار با AI روی این موضوع

**فایل‌هایی که به دستیار می‌دهی:** `AGENTS.md`، بخش ۷ از `docs/SPEC.md`، همین فصل، README سرویس و پوشه‌ی <span dir="ltr">`migrations/`</span> همان سرویس.

بازبینی migration:

</div>

```text
این فایل migration را برای سرویس order بخوان.
بخش ۷ و بخش ۱۴ از docs/SPEC.md و docs/guide/08-database-and-storage.md را هم بخوان.
به این سه سؤال جواب بده:
۱. اگر این migration اجرا شود ولی کد نسخه‌ی قبلی هنوز بالا باشد، چه چیزی می‌شکند؟
۲. آیا down آن واقعاً up را برمی‌گرداند؟
۳. کدام قاعده‌ی بخش ۷ رعایت نشده است (venue_id، ایندکس، bigint، jsonb)؟
جدول یا ستونی که در مشخصات فنی نیست پیشنهاد نده.
```

<div dir="rtl">

خواندن plan:

</div>

```text
این خروجی EXPLAIN (ANALYZE, BUFFERS) برای فهرست سفارش‌های یک venue است.
خط‌به‌خط به فارسی توضیح بده هر گره چه می‌کند و بیشترین زمان کجا می‌رود.
اگر ایندکس لازم است، فقط یک ایندکس پیشنهاد بده که با venue_id شروع شود و بگو چرا ترتیب ستون‌هایش این است.
```

<div dir="rtl">

بازبینی جداسازی:

</div>

```text
همه‌ی متدهای پوشه‌ی internal/repository این سرویس را بخوان.
هر query روی جدول متعلق به venue که venue_id در WHERE آن نیست را با نام فایل و شماره‌ی خط فهرست کن.
اگر موردی پیدا نکردی همین را بگو.
```

<div dir="rtl">

**خودت حتماً بررسی کن:** migration را خودت روی دیتابیس خالی `up` و `down` کن. `EXPLAIN` را خودت روی داده‌ی نمونه بگیر؛ دستیار دیتابیس تو را نمی‌بیند و فقط حدس می‌زند. هیچ داده‌ی واقعی `production` را در گفت‌وگو با دستیار نگذار.

## بیشتر بخوان

- [مشخصات فنی](../SPEC.md): بخش ۴٫۱ (قواعد ارتباط)، بخش ۷ (مدل داده)، بخش ۱۴ (migration در استقرار)، بخش ۱۶ (رفتار هنگام خرابی).
- [فصل ۴: معماری](04-architecture.md) و [فصل ۷: سرویس‌های بک‌اند](07-backend-services.md): لایه‌ی repository و شاسی مشترک.
- [فصل ۹: ورود و دسترسی](09-auth-and-permissions.md): جدول‌های `identity` در عمل.
- [فصل ۱۰: امنیت و پرداخت](10-security-and-payments.md): تراکنش پرداخت با جزئیات.
- [فصل ۱۲: کش و CDN](12-caching-and-cdn.md)، [فصل ۱۸: مقیاس‌پذیری و تاب‌آوری](18-scaling-and-resilience.md)، [فصل ۲۱: پشتیبان و بازیابی](21-backup-and-recovery.md).
- README سرویس‌ها: [catalog](../../services/catalog/README.md)، [order](../../services/order/README.md)، [identity](../../services/identity/README.md).

</div>
