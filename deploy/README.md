<div dir="rtl">

# پوشه‌ی deploy

هر چیزی که سرمیز را اجرا می‌کند، از محیط محلی تا `production`، در این پوشه و در Git است. اگر چیزی روی cluster هست و اینجا نیست، یعنی یک نفر دستی عوضش کرده و با استقرار بعدی گم می‌شود.

[صفحه‌ی اصلی](../README.md) | [فهرست مستندات](../docs/README.md)

## ۱. چه چیزی اینجاست

</div>

```text
deploy/
├── compose/   local infrastructure: PostgreSQL (4 databases and roles), Redis, NATS JetStream, MinIO, optional Ollama
├── helm/      the generic chart for Go services, values per service and environment, other charts and jobs
├── grafana/   dashboards as JSON
└── alerts/    Prometheus alert rules for Alertmanager
```

<div dir="rtl">

| پوشه | محتوا | کار | تحویل |
|---|---|---|---|
| <span dir="ltr">`compose/`</span> | محیط محلی با یک دستور، و <span dir="ltr">`.env.example`</span> فقط با نام متغیرها | `W1-PA-1` | [هفته‌ی ۱](../docs/handoffs/week-1/platform-ai.md) |
| <span dir="ltr">`helm/`</span> | chart عمومی سرویس‌های Go، valueهای `staging` و `production`، job migration از نوع pre-upgrade | `W1-PA-6` | [هفته‌ی ۱](../docs/handoffs/week-1/platform-ai.md) |
| <span dir="ltr">`helm/`</span> | bucketها و سیاست دسترسی object storage در `staging`، CDN | `W2-PA-2` | [هفته‌ی ۲](../docs/handoffs/week-2/platform-ai.md) |
| <span dir="ltr">`helm/`</span> | CronJob پشتیبان شبانه | `W4-PA-1` | [هفته‌ی ۴](../docs/handoffs/week-4/platform-ai.md) |
| <span dir="ltr">`helm/`</span> | NetworkPolicy، container غیر root، headerهای امنیتی | `W4-PA-2` | [هفته‌ی ۴](../docs/handoffs/week-4/platform-ai.md) |
| <span dir="ltr">`helm/`</span> | requests و limits، autoscaling، rollout بدون قطعی، استقرار `production` با تأیید دستی | `W5-PA-3` | [هفته‌ی ۵](../docs/handoffs/week-5/platform-ai.md) |
| <span dir="ltr">`grafana/`</span> | داشبوردهای overview، هر سرویس، کسب‌وکار و زیرساخت | `W3-PA-1` | [هفته‌ی ۳](../docs/handoffs/week-3/platform-ai.md) |
| <span dir="ltr">`alerts/`</span> | ده قاعده‌ی هشدار بخش ۱۲ مشخصات فنی | `W3-PA-2` | [هفته‌ی ۳](../docs/handoffs/week-3/platform-ai.md) |
| <span dir="ltr">`alerts/`</span> | هشدار شکست پشتیبان شبانه | `W4-PA-1` | [هفته‌ی ۴](../docs/handoffs/week-4/platform-ai.md) |

ساختار داخلی هر پوشه را همان کار تعیین می‌کند. اینکه سرویس `ai` (Python) و `web` (Nginx) chart جدا دارند یا با valueهای دیگری مستقر می‌شوند، و اینکه ابزارهای مشاهده‌پذیری با چه chartهایی نصب می‌شوند، در `W1-PA-6` و `W3-PA-1` تصمیم گرفته و همین‌جا نوشته می‌شود.

## ۲. قواعد

1. **هیچ رازی اینجا نیست.** نه رمز، نه کلید، نه توکن، نه DSN بک‌اند، نه حتی «فقط برای `staging`». valueها فقط **نام** Kubernetes secret را می‌آورند. gitleaks روی هر PR این را می‌سنجد.
2. **یک chart عمومی برای سرویس‌های Go.** `gateway`، `identity`، `catalog`، `order` و `realtime` همه با یک chart مستقر می‌شوند و فقط valueهایشان فرق دارد. chart را برای یک سرویس کپی نکن؛ اگر چیزی کم است، به chart عمومی اضافه‌اش کن تا همه از آن استفاده کنند.
3. **valueها برای هر محیط.** هر سرویس برای `staging` و `production` valueهای جدا دارد. پیشنهاد اولیه برای نام فایل‌ها: `helm/values/<service>/staging.yaml` و `helm/values/<service>/production.yaml`؛ قطعی‌اش با `W1-PA-6`.
4. **tag image فقط git SHA.** CI آن را هنگام استقرار می‌گذارد. `latest` در هیچ فایلی نمی‌آید.
5. **migration قبل از کد.** هر سرویس دیتابیس‌دار یک job از نوع `pre-upgrade` دارد. migrationها expand-then-contract هستند تا `helm rollback` بی‌خطر باشد.
6. **داشبورد و هشدار فایل‌اند.** داشبوردی که فقط در رابط Grafana ساخته شده، با رفتن سرور می‌رود. بعد از ساختن در Grafana، JSON را export کن و PR بده.
7. **تغییر دستی روی cluster ممنوع.** `kubectl edit`، `kubectl apply` از روی لپ‌تاپ یا `helm upgrade` دستی در `production` نداریم، مگر در rollback طبق [فصل ۱۴](../docs/guide/14-ci-cd-and-version-control.md).
8. **`staging` و `production` هیچ داده و رازی را با هم شریک نیستند.**

## ۳. نشانی محیط‌ها

دامنه تصمیم باز ۱ مشخصات فنی است. بعد از قطعی شدنش، زوج پلتفرم در `W1-PA-6` این جدول را پر می‌کند:

| محیط | نشانی وب و API | WebSocket | Grafana و GlitchTip |
|---|---|---|---|
| `local` | `localhost`، پورت‌ها در `W1-PA-1` | در `W1-PA-1` | در `W1-PA-1` |
| `staging` | در `W1-PA-6` پر می‌شود | در `W1-PA-6` پر می‌شود | فقط برای تیم، روش دسترسی در `W1-PA-6` |
| `production` | در `W1-PA-6` پر می‌شود | در `W1-PA-6` پر می‌شود | فقط برای تیم، روش دسترسی در `W1-PA-6` |

دستورهای محیط محلی هم در `W1-PA-1` اینجا و در بخش «Commands» فایل [AGENTS.md](../AGENTS.md) اضافه می‌شوند.

## ۴. پیشنهاد یک تغییر زیرساخت

1. **issue باز کن.** بگو چه مشکلی را حل می‌کند و با یک مثال واقعی نشانش بده.
2. **ابزار یا سرویس تازه؟** اگر تغییر چیزی اضافه می‌کند که در [مشخصات فنی](../docs/SPEC.md) نیست (پایگاه‌داده، صف، exporter، سرویس بیرونی)، اول با منتور حرف بزن و یک [سند تصمیم](../docs/decisions/README.md) بنویس.
3. **شاخه بساز:** <span dir="ltr">`platform/<task-id>-<slug>`</span>.
4. **خروجی را نشان بده.** در توضیح PR، تفاوت خروجی `helm template` قبل و بعد را بگذار تا بازبین ببیند دقیقاً چه چیزی روی cluster عوض می‌شود.
5. **بازبینی بگیر.** دست‌کم یک نفر. تغییر در NetworkPolicy، ingress، رازها یا هر چیزی که به پرداخت و ورود مربوط است، منتور را هم می‌خواهد.
6. **merge کن و `staging` را ببین.** استقرار خودکار است. داشبورد سرویس و هشدارها را نگاه کن.
7. **`production` با انتشار بعدی.** با tag `vX.Y.Z` و تأیید دستی، نه جدا و نه دستی.

## ۵. بیشتر بخوان

- [فصل ۱۳: میزبانی و زیرساخت ابری](../docs/guide/13-hosting-and-cloud.md)
- [فصل ۱۴: CI/CD و کنترل نسخه](../docs/guide/14-ci-cd-and-version-control.md)
- [فصل ۱۵: لاگ و ردیابی خطا](../docs/guide/15-logs-and-error-tracking.md)
- [فصل ۱۶: مانیتورینگ و هشدار](../docs/guide/16-monitoring-and-alerts.md)
- [فصل ۲۱: پشتیبان‌گیری و بازیابی](../docs/guide/21-backup-and-recovery.md)
- [مشخصات فنی](../docs/SPEC.md): بخش‌های ۵، ۱۲، ۱۴، ۱۵ و ۱۷.

</div>
