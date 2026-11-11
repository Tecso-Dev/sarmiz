<div dir="rtl">

# سرویس `gateway`

تنها در ورودی REST سرمیز: هر درخواستی که مرورگر به <span dir="ltr">`/api/v1/*`</span> می‌فرستد از اینجا رد می‌شود.

[مشخصات فنی](../../docs/SPEC.md) | [فهرست مستندات](../../docs/README.md) | [قواعد دستیار AI](../../AGENTS.md)

| | |
|---|---|
| زبان | Go، کد تولیدی grpc-gateway به‌اضافه‌ی middleware دست‌نویس |
| بخش مسئول | پلتفرم و هوش مصنوعی (`platform-ai`) |
| دیتابیس | ندارد؛ از Redis برای محدودیت نرخ استفاده می‌کند |
| ارتباط با بیرون | HTTPS روی <span dir="ltr">`/api/v1/*`</span> |

## ۱. یک‌خطی

`gateway` درخواست HTTPS مرورگر را می‌گیرد، توکن و نقش را بررسی می‌کند و آن را به متد gRPC سرویس درست ترجمه می‌کند. هیچ منطق کسب‌وکاری ندارد؛ اگر جایی در این سرویس `if` درباره‌ی قیمت یا وضعیت سفارش نوشتی، جای اشتباهی است.

## ۲. مسئولیت‌ها

- ترجمه‌ی REST به gRPC با grpc-gateway (ابزاری که از annotationهای HTTP در فایل‌های proto یک سرور REST می‌سازد).
- بررسی JWT دسترسی (کوکی `sz_at`) با کلیدهای عمومی که `identity` به شکل JWKS منتشر می‌کند؛ JWKS ده دقیقه در حافظه می‌ماند.
- بررسی نقش برای هر مسیر از روی claim `mem` و جدول دسترسی بخش ۸ مشخصات فنی؛ مسیرهای <span dir="ltr">`/admin/*`</span> فقط با claim `adm`.
- محدودیت نرخ با پنجره‌ی لغزان (sliding window) در Redis، با عددهای بخش ۱۰ مشخصات فنی، جواب `429` و هدر `Retry-After`.
- CORS فقط برای originهای سرمیز، و بررسی هدر `Origin` روی هر متد ناامن (دفاع در برابر CSRF همراه با `SameSite=Lax`).
- ساختن request id و فرستادن metadata مطمئن به سرویس‌ها.
- برگرداندن همه‌ی خطاها در قالب یکسان بخش ۶٫۱، بدون SQL، stack trace یا نام داخلی.
- محدودیت حجم بدنه: ۱ مگابایت برای JSON و ۶ مگابایت برای آپلود.

## ۳. چه چیزی مالِ این سرویس است

| چیز | کجا | قاعده |
|---|---|---|
| شمارنده‌های محدودیت نرخ | Redis | نام کلیدها را تیم در `W2-PA-1` تعیین می‌کند |
| کش JWKS | حافظه‌ی همین pod | ۱۰ دقیقه |
| فهرست originهای مجاز و عددهای محدودیت | تنظیمات (متغیر محیطی) | عددها نقطه‌ی شروع‌اند و بعد از load test تنظیم می‌شوند |

## ۴. قرارداد

مسیرهای HTTP از annotationهای proto ساخته می‌شوند. گروه‌ها (بخش ۶٫۱ مشخصات فنی):

| گروه | ورود | سرویس پشتش |
|---|---|---|
| <span dir="ltr">`/auth/*`</span>، `GET /me` | ندارد یا کوکی | `identity` |
| <span dir="ltr">`/venues`</span> و <span dir="ltr">`/venues/{venue_id}/*`</span> | کاربر پنل با نقش در همان کسب‌وکار | `catalog` |
| <span dir="ltr">`/venues/{venue_id}/orders*`</span>، <span dir="ltr">`/service-requests*`</span>، <span dir="ltr">`/reports/*`</span>، <span dir="ltr">`/payment-config`</span> | کاربر پنل | `order` |
| <span dir="ltr">`/public/t/{qr_token}*`</span>، <span dir="ltr">`/public/m/{slug}`</span> | ندارد | `catalog` |
| <span dir="ltr">`/public/t/{qr_token}/orders`</span>، <span dir="ltr">`/public/orders/{order_id}*`</span>، <span dir="ltr">`/public/payments/zarinpal/callback`</span>، <span dir="ltr">`/public/t/{qr_token}/service-requests`</span> | ندارد؛ order token هر جا لازم است | `order` |
| <span dir="ltr">`/public/t/{qr_token}/assistant`</span> | ندارد | `catalog` (که `ai` را صدا می‌زند) |
| <span dir="ltr">`/stream-tickets`</span> | کاربر پنل یا order token | `identity` |
| <span dir="ltr">`/admin/*`</span> | ادمین پلتفرم | `catalog`، `order` |

هدرهای ورودی که باید بشناسد: `Idempotency-Key` روی `POST .../orders` و `POST .../pay`، و `X-Guest-Session` از مرورگر مهمان.

metadata مطمئنی که به هر فراخوانی gRPC اضافه می‌کند: `x-request-id`، `x-user-id`، `x-venue-id`، `x-role`، `x-guest-session` و trace context از نوع W3C.

رویداد: هیچ رویدادی منتشر یا مصرف نمی‌کند.

## ۵. به چه کسی وابسته است

`gateway` با gRPC به `identity`، `catalog` و `order` وصل می‌شود، با HTTP داخلی JWKS را از `identity` می‌خواند، و برای محدودیت نرخ مستقیم به Redis می‌رود. جدول دیتابیس ندارد و نباید داشته باشد. `gateway` حق ندارد `ai` یا `realtime` را صدا بزند (بخش ۴٫۱). فقط مرورگر، از طریق ingress، به `gateway` می‌رسد.

## ۶. قاعده‌هایی که نباید بشکنند

1. منطق کسب‌وکار ممنوع. قیمت، وضعیت و مالکیت را سرویس پشتی تصمیم می‌گیرد.
2. سرویس‌ها به metadata اعتماد می‌کنند؛ پس `gateway` هیچ‌وقت `x-user-id` یا `x-venue-id` را از هدرهای خود مرورگر عبور نمی‌دهد و همیشه خودش از روی توکن و مسیر درخواست می‌سازد.
3. وقتی Redis در دسترس نیست: مسیرهای OTP بسته می‌مانند (fail closed) و منوی عمومی باز می‌ماند (fail open).
4. پاسخ‌های ورود، سفارش، پرداخت و هر چیزی زیر <span dir="ltr">`/venues/*`</span> کش نمی‌شود.
5. هر فراخوانی gRPC deadline دارد (پیش‌فرض ۲ ثانیه).
6. توکن، کد یک‌بارمصرف و شماره‌ی کامل در لاگ نمی‌آید.
7. تغییر در بررسی توکن یا نقش، تغییر کد ورود است و بازبینی منتور می‌خواهد.

## ۷. ساختار پوشه

پیشنهاد اولیه؛ جای دقیق کد تولیدی را تیم در `W1-PA-3` تعیین می‌کند:

</div>

```text
services/gateway/
├── cmd/server/main.go
├── internal/
│   ├── config/
│   ├── middleware/   auth, roles, rate limit, CORS, origin, request id, body limit
│   └── errors/       gRPC status to the unified error format
├── Dockerfile
└── README.md
```

<div dir="rtl">

## ۸. اجرا و تست

دستورهای اجرا و تست را تیم در هفته‌ی ۱ می‌سازد و در بخش Commands فایل [AGENTS.md](../../AGENTS.md) می‌نویسد. این سرویس تست واحد برای middlewareها، تست یکپارچه با Redis واقعی برای محدودیت نرخ، و سهم اصلی در مجموعه‌ی تست جداسازی <span dir="ltr">`tests/isolation/`</span> دارد.

## ۹. در کدام هفته چه چیزی ساخته می‌شود

| هفته | کار | چه چیزی | تحویل |
|---|---|---|---|
| ۱ | `W1-PA-3` | ابزار `buf`، کد تولیدی grpc-gateway و OpenAPI | [platform-ai](../../docs/handoffs/week-1/platform-ai.md) |
| ۱ | `W1-PA-4` | اسکلت: اتصال به `identity`، JWKS، CORS، بررسی Origin، request id، قالب خطا | [platform-ai](../../docs/handoffs/week-1/platform-ai.md) |
| ۲ | `W2-PA-1` | مسیرهای هفته‌های ۱ تا ۳، نقش هر مسیر، metadata مطمئن، محدودیت نرخ | [platform-ai](../../docs/handoffs/week-2/platform-ai.md) |
| ۳ | `W3-PA-1`، `W3-PA-3` | متریک‌ها و tracing، load test منوی عمومی و ساخت سفارش | [platform-ai](../../docs/handoffs/week-3/platform-ai.md) |
| ۴ | `W4-PA-2`، `W4-PA-3` | هدرهای امنیتی و NetworkPolicy، تست جداسازی کسب‌وکارها | [platform-ai](../../docs/handoffs/week-4/platform-ai.md) |
| ۵ | `W5-PA-3` | آمادگی production: منابع، autoscaling، استقرار بی‌وقفه | [platform-ai](../../docs/handoffs/week-5/platform-ai.md) |
| ۶ | `W6-ALL-1` | بازبینی امنیتی کامل | [هفته‌ی ۶](../../docs/handoffs/week-6/README.md) |

## ۱۰. سؤال‌های باز

- کوکی‌های `sz_at` و `sz_rt` را چه کسی روی پاسخ HTTP می‌گذارد؟ `identity` فقط gRPC حرف می‌زند، پس پیشنهاد اولیه این است که `gateway` توکن‌های برگشتی را به کوکی تبدیل کند. این را تیم در `W1-PA-4` با زوج هسته تصمیم می‌گیرد.
- تیکت WebSocket برای مهمان: order token را چه کسی بررسی می‌کند؟ پیشنهاد اولیه: `gateway` اول `order.ValidateOrderToken` و بعد `identity.IssueStreamTicket` را صدا بزند. در هفته‌ی ۲ با زوج سفارش تصمیم بگیرید.
- وقتی Redis در دسترس نیست، مسیرهای دیگر (پنل، ساخت سفارش) باز بمانند یا بسته؟ مشخصات فنی فقط OTP و منوی عمومی را گفته است؛ تیم در هفته‌ی ۲ تصمیم می‌گیرد.
- `W2-PA-1` فقط مسیرهای هفته‌های ۱ تا ۳ را می‌پوشاند. نقش مسیرهای پرداخت، ادمین و پیشخدمت AI در هفته‌های ۴ و ۵ کار جدا ندارد؛ پیشنهاد اولیه: بخشی که متد را می‌سازد نقش مسیرش را هم اضافه کند و زوج پلتفرم بازبینی کند.

</div>
