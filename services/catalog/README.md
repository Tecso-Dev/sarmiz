<div dir="rtl">

# سرویس `catalog`

کسب‌وکارها، شعبه‌ها، میزها و QR، برند، منو، تصویرها، منوی عمومی، کارهای ورود منو و ترجمه‌های ذخیره‌شده.

[مشخصات فنی](../../docs/SPEC.md) | [فصل ۸: دیتابیس و ذخیره‌سازی](../../docs/guide/08-database-and-storage.md) | [قواعد دستیار AI](../../AGENTS.md)

| | |
|---|---|
| زبان | Go، روی شاسی [`libs/go/kit`](../../libs/go/kit/README.md) |
| بخش مسئول | هسته (`core`)؛ صاحبش نقش «ورود و منو» است ([تیم و تقسیم کار](../../docs/team.md)) |
| دیتابیس | `catalog`، Redis برای کش، و دو bucket در object storage |
| ارتباط با بیرون | gRPC |

## ۱. یک‌خطی

`catalog` همه‌ی چیزی است که مهمان با اسکن QR می‌بیند و صاحب کسب‌وکار در پنل می‌سازد. کسب‌وکار و میز کنار منو در همین سرویس‌اند، چون در هر اسکن با هم خوانده می‌شوند.

## ۲. مسئولیت‌ها

- ساخت و ویرایش کسب‌وکار، شعبه‌ی پیش‌فرض، میزها و `qr_token` تصادفی، و تصویر QR با لوگو.
- منو: دسته‌ها، آیتم‌ها، گروه گزینه‌ها، برنامه‌ی زمانی، «با این خوب است» (pairing)، نشان‌ها، برچسب رژیم و آلرژی، کلید «تمام شد».
- آپلود تصویر: بررسی نوع از روی محتوا، حداکثر ۵ مگابایت، تبدیل به WebP در عرض‌های ۳۲۰، ۸۰۰ و ۱۶۰۰.
- منوی عمومی: `GetPublicMenuByTable` و `GetPublicMenuBySlug` با fallback زبان، کش Redis و ETag.
- قیمت‌گذاری مرجع برای `order`: `ResolveTable` و `PriceItems`.
- کار ورود منو از عکس یا Excel، ترجمه از طریق `ai`، پیشخدمت AI برای مهمان، و APIهای ادمین Tecso (فهرست، فعال و معلق کردن کسب‌وکار).

## ۳. چه چیزی مالِ این سرویس است

| گروه | جدول‌ها |
|---|---|
| کسب‌وکار | `venues` (با `slug` یکتا، `status`، `is_demo`، `menu_version`)، `branches`، `dining_tables` |
| منو | `menu_categories`، `menu_items`، `option_groups`، `options`، `menu_schedules`، `item_pairings` |
| فایل و ورود | `media`، `import_jobs` |
| زیرساخت | `outbox`، `audit_log` |

ستون‌های دقیق در بخش ۷٫۲ مشخصات فنی است و نمودار جدول‌ها را بخش هسته در `W1-CORE-1` اینجا اضافه می‌کند. خارج از دیتابیس:

| چیز | قاعده |
|---|---|
| کش منوی عمومی در Redis | کلید <span dir="ltr">`menu:{venue_id}:{locale}:{menu_version}`</span>، TTL ۲۴ ساعت |
| کش `qr_token` به میز در Redis | TTL ۵ دقیقه |
| bucket `sarmiz-media` | تصویرها، خواندن عمومی از CDN، کلید `v/{venue_id}/{sha256}-{width}.webp` |
| bucket `sarmiz-imports` | عکس و Excel منو، خصوصی، حذف بعد از ۳۰ روز؛ `ai` هم آن را می‌خواند |

## ۴. قرارداد

gRPC در بسته‌ی `sarmiz.catalog.v1`: `VenueService`، `TableService` (با `RegenerateQrToken`، `GetTableQr`، `ResolveTable`)، `MenuService`، `PublicMenuService`، `PricingService` (داخلی، `PriceItems`)، `MediaService`، `ImportService`، `TranslationService`، `AssistantService` و `SnapshotService` (داخلی، `GetMenuSnapshot`). فهرست کامل متدها در بخش ۶٫۲ مشخصات فنی است.

مسیرهای REST از `gateway`: <span dir="ltr">`/venues`</span> و <span dir="ltr">`/venues/{venue_id}/*`</span>، <span dir="ltr">`/public/t/{qr_token}*`</span>، <span dir="ltr">`/public/m/{slug}`</span>، <span dir="ltr">`/public/t/{qr_token}/assistant`</span> و بخشی از <span dir="ltr">`/admin/*`</span>. رویدادها:

| رویداد | جهت | `data` |
|---|---|---|
| `sarmiz.catalog.menu.changed` | منتشر می‌کند، `ai` مصرف می‌کند | `venue_id`، `menu_version` |
| `sarmiz.catalog.venue.updated` | منتشر می‌کند، در انتشار ۱ مصرف‌کننده ندارد | `venue_id` |
| `sarmiz.catalog.import.requested` | منتشر می‌کند، `ai` مصرف می‌کند | `job_id`، `venue_id`، `kind`، `file_key`، `locale_hint` |
| `sarmiz.ai.import.completed` | مصرف می‌کند | `job_id`، `status`، `draft` یا `error` |

## ۵. به چه کسی وابسته است

- `identity` با gRPC، فقط برای `GrantMembership` هنگام ساخت کسب‌وکار.
- `ai` با HTTP داخلی و هدر secret مشترک، برای ترجمه (`POST /v1/translate`) و پیشخدمت AI (`POST /v1/assistant`).

چه کسی صدایش می‌زند: `gateway`، `order` (`ResolveTable` و `PriceItems`) و `ai` (`GetMenuSnapshot`).

## ۶. قاعده‌هایی که نباید بشکنند

1. هر متد repository `venue_id` می‌گیرد. منبع کسب‌وکار دیگر `not_found` برمی‌گرداند.
2. هر تغییر در منو، موجودی یا برنامه‌ی زمانی `venues.menu_version` را در همان تراکنش بالا می‌برد و ردیف `menu.changed` را در `outbox` می‌نویسد.
3. `fa` در هر متن چندزبانه اجباری است. ترتیب fallback: زبان درخواستی، بعد `default_locale` کسب‌وکار، بعد `fa`.
4. برچسب‌ها فقط از مقدارهای مجاز بخش ۷٫۲ هستند.
5. `PriceItems` مرجع قیمت است و snapshot نام، قیمت و گزینه را برمی‌گرداند. منوی کش‌شده تا ۳۰ ثانیه کهنه بودنش قابل قبول است، قیمت نه.
6. `identity` را وسط تراکنش دیتابیس صدا نزن. اگر `GrantMembership` شکست خورد، کسب‌وکار نیمه‌ساخته نماند.
7. هیچ نشانی‌ای را که کاربر داده fetch نکن. متن منو و جواب مدل داده‌اند و به شکل متن ساده برمی‌گردند.
8. اگر `ai` در دسترس نیست، منو و سفارش کار می‌کنند و فقط ترجمه، ورود منو و پیشخدمت پیام «دوباره امتحان کن» می‌دهند.

## ۷. ساختار پوشه

</div>

```text
services/catalog/
├── cmd/server/main.go
├── internal/
│   ├── config/
│   ├── handler/      gRPC handlers, no business rules
│   ├── service/      menu rules, pricing, locale fallback (unit tested)
│   ├── repository/   SQL with pgx, venue_id on every method
│   └── model/
├── migrations/       goose SQL files
├── Dockerfile
└── README.md
```

<div dir="rtl">

## ۸. اجرا و تست

دستورهای اجرا و تست را تیم در هفته‌ی ۱ می‌سازد و در بخش Commands فایل [AGENTS.md](../../AGENTS.md) می‌نویسد. قیمت‌گذاری و fallback زبان تست واحد جدولی دارند و هر متد پنل یک تست جداسازی.

## ۹. در کدام هفته چه چیزی ساخته می‌شود

| هفته | کارها | چه چیزی | تحویل |
|---|---|---|---|
| ۱ | `W1-CORE-1`، `W1-CORE-3`، `W1-CORE-4` | طرح داده، اسکلت و `CreateVenue`، قرارداد proto | [core](../../docs/handoffs/week-1/core.md) |
| ۲ | `W2-CORE-1` تا `W2-CORE-6` | منو، گزینه‌ها، تصویر و برند، میز و QR، منوی عمومی، `ResolveTable` و `PriceItems` | [core](../../docs/handoffs/week-2/core.md) |
| ۳ | `W3-CORE-1` تا `W3-CORE-4` | جریان ورود منو، منوی زمانی و «تمام شد»، ترجمه، pairing و نشان‌ها | [core](../../docs/handoffs/week-3/core.md) |
| ۴ | `W4-CORE-1` تا `W4-CORE-3` | نقش‌ها و audit، APIهای ادمین، منوی عمومی با slug و بهینه‌سازی | [core](../../docs/handoffs/week-4/core.md) |
| ۵ | `W5-CORE-1` (اختیاری)، `W5-CORE-2` | پیشخدمت AI برای مهمان، کسب‌وکارهای دمو | [core](../../docs/handoffs/week-5/core.md) |
| ۶ | `W6-ALL-1` | بازبینی امنیتی کامل | [هفته‌ی ۶](../../docs/handoffs/week-6/README.md) |

## ۱۰. سؤال‌های باز

- جدول ۴٫۱ مشخصات فنی اجازه‌ی `catalog` به `ai` را فقط برای ترجمه نوشته، ولی بخش ۶٫۱ و `W5-CORE-1` پیشخدمت AI را هم از همین مسیر می‌برند. تا اصلاح مشخصات فنی، این را از منتور بپرس.
- مصرف‌کننده‌ی `import.completed` باید رویداد تکراری را تشخیص بدهد، ولی بخش ۷٫۲ جدول `processed_events` ندارد. تیم در `W1-CORE-1` تصمیم می‌گیرد و سند تصمیم می‌نویسد.

</div>
