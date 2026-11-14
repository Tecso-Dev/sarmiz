<div dir="rtl">

# شاسی مشترک Go: `libs/go/kit`

کدی که همه‌ی سرویس‌های Go سرمیز لازم دارند و فقط یک بار نوشته می‌شود: تنظیمات، لاگ، سرور gRPC، دیتابیس، رویدادها، خطاها و ابزار تست.

[مشخصات فنی](../../../docs/SPEC.md) | [فصل ۷: سرویس‌های بک‌اند](../../../docs/guide/07-backend-services.md) | [قواعد دستیار AI](../../../AGENTS.md)

| | |
|---|---|
| زبان | Go، یک module جدا در `go.work` |
| بخش مسئول | پلتفرم (`platform-ai`) و سفارش (`order`) در بسته‌ی رویدادها؛ صاحب هر دو نقش «سفارش و زیرساخت» است ([تیم و تقسیم کار](../../../docs/team.md)) |
| استفاده‌کننده‌ها | `gateway`، `identity`، `catalog`، `order`، `realtime` |
| بازبین‌ها | صاحب «ورود و منو»، چون اولین سرویس‌ها روی شاسی را او می‌سازد |

## ۱. چرا شاسی

شاسی (chassis) یعنی اسکلت مشترکی که هر سرویس رویش سوار می‌شود. پنج سرویس Go داریم. اگر هر کدام لاگ، خطا و راه‌اندازی سرور را خودش بنویسد، پنج شکل لاگ و پنج نگاشت خطا خواهیم داشت و یک باگ امنیتی باید پنج بار درست شود. با شاسی، `main.go` هر سرویس چند خط است و همه‌ی سرویس‌ها یک‌جور رفتار می‌کنند.

## ۲. بسته‌ها

نام بسته‌ها پیشنهاد اولیه است؛ محتوای هر کدام از کارهای `W1-PA-2` و `W1-ORD-4` و بخش ۵ مشخصات فنی می‌آید.

| بسته | چه چیزی دارد | کار |
|---|---|---|
| `config` | خواندن تنظیمات از متغیر محیطی، خطای روشن برای مقدار جاافتاده | `W1-PA-2` |
| `log` | `log/slog` با خروجی JSON و فیلدهای `time`، `level`، `service`، `env`، `request_id`، `trace_id`، `venue_id`، `user_id`، `msg`؛ پوشاندن شماره‌ی موبایل | `W1-PA-2` |
| `grpcserver` | راه‌اندازی سرور gRPC با interceptorهای request id، recovery، لاگ، متریک و tracing؛ graceful shutdown | `W1-PA-2` |
| `health` | <span dir="ltr">`/healthz`</span>، <span dir="ltr">`/readyz`</span>، <span dir="ltr">`/metrics`</span> و سرویس health استاندارد gRPC | `W1-PA-2` |
| `errors` | نگاشت خطاهای سرویس به کدهای gRPC در یک جا، بدون نشت جزئیات داخلی | `W1-PA-2` |
| `db` | ساختن pool با pgx (شروع با ۱۰ اتصال برای هر pod)، کمک‌کننده‌ی تراکنش | `W1-PA-2` |
| `redis` | ساختن client و کمک‌کننده‌های رایج | `W1-PA-2` |
| `events` | envelope رویداد، ساختن subject با الگوی <span dir="ltr">`sarmiz.<service>.<entity>.<event>`</span>، نوشتن ردیف outbox در تراکنش، relay که ردیف‌ها را منتشر و `sent_at` را پر می‌کند، consumer بی‌اثر در تکرار (idempotent) با حذف تکراری بر اساس شناسه‌ی رویداد، متریک `outbox_lag_seconds` | `W1-ORD-4` |
| `auth` | خواندن metadata مطمئن (`x-user-id`، `x-venue-id`، `x-role`، `x-guest-session`) از context | بخش ۵ مشخصات فنی |
| `testkit` | راه‌اندازی PostgreSQL، Redis و NATS واقعی برای تست یکپارچه (testcontainers-go) | بخش ۵ مشخصات فنی |

جدول `outbox` در دیتابیس خود هر سرویس است و migrationش در پوشه‌ی همان سرویس. شاسی فقط کد خواندن و نوشتنش را دارد.

همراه شاسی یک قالب «سرویس تازه» هم مستند می‌شود (`W1-PA-2`): چیدمان پوشه‌ها مثل بخش ۵ مشخصات فنی و یک `main.go` نمونه. شکلش چیزی شبیه این است، فقط برای نشان دادن ایده:

</div>

```go
func main() {
	ctx := context.Background()
	cfg := config.MustLoad[Config]()
	logger := log.New(cfg.Service, cfg.Env)
	pool := db.MustConnect(ctx, cfg.DatabaseURL)
	srv := grpcserver.New(logger, grpcserver.WithHealth(pool))
	catalogv1.RegisterVenueServiceServer(srv, handler.NewVenue(service.NewVenue(repository.New(pool))))
	grpcserver.Run(ctx, srv, cfg.GRPCAddr)
}
```

<div dir="rtl">

## ۳. قاعده‌ها

1. **کپی ممنوع.** هیچ سرویسی کد شاسی را داخل خودش کپی یا بازنویسی نمی‌کند. اگر چیزی کم است، به شاسی اضافه‌اش کن.
2. **منطق کسب‌وکار ممنوع.** شاسی از قیمت، سفارش یا منو چیزی نمی‌داند و هیچ سرویسی را import نمی‌کند.
3. **سازگاری.** همه‌ی سرویس‌ها به شاسی وابسته‌اند. تغییری که امضای یک تابع را عوض می‌کند، در همان PR همه‌ی استفاده‌ها را هم درست می‌کند و CI همه‌ی سرویس‌ها باید سبز باشد.
4. **تست.** هر بسته تست دارد و با <span dir="ltr">`-race`</span> اجرا می‌شود؛ `events` تست یکپارچه با NATS واقعی.
5. **امنیت.** شاسی هیچ‌وقت کد، توکن، credential یا شماره‌ی کامل را لاگ نمی‌کند. تغییر در `auth` بازبینی منتور می‌خواهد.

## ۴. چطور چیزی اضافه کنی

1. یک issue باز کن: چه چیزی کم است، کدام سرویس‌ها لازمش دارند و چرا جای آن در شاسی است، نه در یک سرویس.
2. اگر فقط یک سرویس لازمش دارد، فعلاً در همان سرویس بماند. وقتی سرویس دوم هم خواست، به شاسی منتقلش کن.
3. PR کوچک با تست بفرست. بخش پلتفرم و دست‌کم یکی از بخش‌های هسته یا سفارش بازبینی می‌کنند.
4. همین README را در همان PR به‌روز کن.

## ۵. در کدام هفته چه چیزی ساخته می‌شود

| هفته | کار | چه چیزی | تحویل |
|---|---|---|---|
| ۱ | `W1-PA-2` | بسته‌های پایه و قالب سرویس تازه | [platform-ai](../../../docs/handoffs/week-1/platform-ai.md) |
| ۱ | `W1-ORD-4` | بسته‌ی `events`، با بخش پلتفرم | [order](../../../docs/handoffs/week-1/order.md) |
| ۲ | `W2-PA-3` | اتصال GlitchTip و request id و trace id در هر خط لاگ | [platform-ai](../../../docs/handoffs/week-2/platform-ai.md) |
| ۳ | `W3-PA-1` | متریک‌ها و OpenTelemetry به Tempo | [platform-ai](../../../docs/handoffs/week-3/platform-ai.md) |
| ۵ | `W5-ORD-1` | پیشنهاد اولیه: deadline، retry با jitter و circuit breaker برای clientهای gRPC، اگر بیش از یک سرویس لازمش داشت | [order](../../../docs/handoffs/week-5/order.md) |

دستورهای اجرا و تست را تیم در هفته‌ی ۱ می‌سازد و در بخش Commands فایل [AGENTS.md](../../../AGENTS.md) می‌نویسد.

## ۶. سؤال‌های باز

- بسته‌های `auth` و `testkit` در بخش ۵ مشخصات فنی آمده‌اند ولی در فهرست `W1-PA-2` نیستند. پیشنهاد اولیه: بخش پلتفرم در همان کار بسازد. تابع کمکی scope کسب‌وکار در `W1-CORE-3` هم در صورت نیاز سرویس‌های دیگر به `auth` منتقل شود.
- جای قالب «سرویس تازه» (پوشه‌ی جدا یا فقط مستند) را تیم در `W1-PA-2` تعیین می‌کند.

</div>
