<div dir="rtl">

# تیم و تقسیم کار

این صفحه می‌گوید سه نفری که سرمیز را می‌سازند، هر کدام دقیقاً چه کاری می‌کنند. اگر فقط یک صفحه را با دقت می‌خوانی، همین باشد. بعد از خواندنش باید بدون پرسیدن بدانی: نقشت چیست، هر هفته کدام کارها مال توست، کارت را چه کسی بازبینی می‌کند، و چه کسی منتظر کار توست.

[صفحه‌ی اصلی](../README.md) | [از اینجا شروع کن](guide/01-start-here.md) | [فهرست کارها](backlog.md) | [سند تصمیم ۷](decisions/0007-three-person-team.md)

## ۱. تیم

| نقش | صاحب | حساب GitHub |
|---|---|---|
| فرانت | | |
| ورود و منو | | |
| سفارش و زیرساخت | | |
| منتور | سبحان عظیم‌زاده | `sobhanaz` |

اعضای تیم در GitHub: `elshan85-mhz`، `Moh4mmadNSZ` و `sahandmusanezhad`. سه ردیف اول را روز اول، بعد از انتخاب نقش‌ها، یک نفر در یک PR پر می‌کند (بخش ۳).

## ۲. سه نقش در یک نگاه

| | فرانت | ورود و منو | سفارش و زیرساخت |
|---|---|---|---|
| برچسب issue | `role:web` | `role:menu` | `role:orders` |
| زبان و ابزار اصلی | TypeScript و React | Go | Go، Docker و Kubernetes |
| صاحب این پوشه‌ها | <span dir="ltr">`web/`</span>، <span dir="ltr">`tests/e2e/`</span> | <span dir="ltr">`services/identity/`</span>، <span dir="ltr">`services/catalog/`</span>، <span dir="ltr">`services/gateway/`</span>، <span dir="ltr">`proto/sarmiz/identity/`</span>، <span dir="ltr">`proto/sarmiz/catalog/`</span>، <span dir="ltr">`tests/isolation/`</span> | <span dir="ltr">`services/order/`</span>، <span dir="ltr">`services/realtime/`</span>، <span dir="ltr">`libs/go/kit/`</span>، <span dir="ltr">`proto/sarmiz/order/`</span>، تنظیمات `buf`، <span dir="ltr">`proto/events/`</span>، <span dir="ltr">`deploy/`</span>، <span dir="ltr">`.github/workflows/`</span>، <span dir="ltr">`tests/load/`</span> |
| چه چیزی می‌سازد | همه‌ی صفحه‌ها: منوی مهمان، سبد و وضعیت سفارش، پرداخت مهمان، پنل صاحب کسب‌وکار، صفحه‌ی آشپزخانه، صفحه‌ی معرفی، پنل ادمین، و تست‌های Playwright | ورود با کد پیامکی و توکن‌ها، کسب‌وکار، منو و گزینه‌ها، عکس‌ها، میز و QR، منوی عمومی و قیمت‌گذاری، مسیرها و محدودیت نرخ `gateway`، کلید «تمام شد»، API ادمین، و پشتیبان‌گیری، لاگ مرکزی، مانیتورینگ و تست جداسازی | محیط محلی، شاسی مشترک Go، ابزار `buf`، CI، cluster و استقرار، رویدادها و outbox، سفارش و ماشین وضعیت، صفحه‌ی زنده با `realtime`، درخواست خدمت، پرداخت پای صندوق و آنلاین، تاب‌آوری، تست بار، تمرین بازیابی و آمادگی `production` |
| تعداد کار | ۱۸ | ۲۲ | ۲۲ |
| بازبین PRهایش | صاحب APIای که صفحه از آن استفاده می‌کند | سفارش و زیرساخت | ورود و منو |

**پیشوند شاخه از شناسه‌ی کار می‌آید، نه از نقش:** کار `CORE` با <span dir="ltr">`core/`</span>، کار `ORD` با <span dir="ltr">`order/`</span>، کار `WEB` با <span dir="ltr">`web/`</span> و کار `PA` با <span dir="ltr">`platform/`</span> شروع می‌شود. مثلاً صاحب «ورود و منو» برای `W1-PA-4` شاخه‌ی `platform/W1-PA-4-gateway` می‌سازد.

## ۳. انتخاب نقش‌ها، روز اول

1. قبل از جلسه‌ی شروع، هر سه نفر بخش ۲ و جدول کارهای هر سه نقش (بخش ۵) را بخوانند.
2. در جلسه‌ی شروع، هر نفر یک نقش برمی‌دارد. یک راهنمای ساده: کسی که React را بهتر بلد است «فرانت»؛ از دو نفر دیگر، کسی که با Docker، لینوکس و استقرار راحت‌تر است «سفارش و زیرساخت».
3. تقسیم دیگری هم آزاد است، با سه شرط: آخر روز اول هر کار دقیقاً یک صاحب دارد؛ دو نفر هم‌زمان روی یک پوشه کار نمی‌کنند؛ و همین صفحه و برچسب issueها با تقسیم واقعی یکی است.
4. یک نفر جدول بخش ۱ را پر می‌کند و با یک PR از شاخه‌ی `docs/team-roles` می‌فرستد. یکی دیگر بازبینی و merge می‌کند.
5. هر نفر همه‌ی issueهای نقش خودش را به خودش assign می‌کند: [کارهای فرانت](https://github.com/Tecso-Dev/sarmiz/issues?q=is%3Aissue%20is%3Aopen%20label%3A%22role%3Aweb%22)، [کارهای ورود و منو](https://github.com/Tecso-Dev/sarmiz/issues?q=is%3Aissue%20is%3Aopen%20label%3A%22role%3Amenu%22)، [کارهای سفارش و زیرساخت](https://github.com/Tecso-Dev/sarmiz/issues?q=is%3Aissue%20is%3Aopen%20label%3A%22role%3Aorders%22).
6. اگر بعداً کاری جابه‌جا شد، assign و برچسب issue را عوض کنید و در گروه تیم خبر بدهید.

## ۴. قاعده‌های کار سه‌نفره

**بازبینی.** هر PR را یکی از دو نفر دیگر بازبینی می‌کند:

| PR از | بازبین | منتور هم لازم است اگر |
|---|---|---|
| فرانت | صاحب APIای که صفحه از آن استفاده می‌کند | |
| ورود و منو | سفارش و زیرساخت | به ورود دست می‌زند: `identity`، توکن، کوکی یا بررسی توکن در `gateway` |
| سفارش و زیرساخت | ورود و منو | به پرداخت دست می‌زند |
| قرارداد: proto، رویداد یا OpenAPI | هر دو نفر دیگر | قرارداد ورود یا پرداخت است |

> [!WARNING]
> ریپو خصوصی و روی پلن رایگان GitHub است. در این حالت GitHub بازبین را خودکار درخواست نمی‌کند، CODEOWNERS اثری ندارد و جلوی merge بدون بازبینی را نمی‌گیرد. بازبین را خودت روی PR بگذار، هیچ‌وقت مستقیم روی `main` push نکن و PR بدون تأیید را merge نکن.

**مسیر تازه در `gateway`.** هر کس endpoint تازه می‌سازد، مسیر و نقش لازم آن را در `gateway` هم در همان PR اضافه می‌کند (بخش ۴٫۲ مشخصات فنی). صاحب «ورود و منو» این بخش را بازبینی می‌کند.

**وقتی منتظر کسی هستی.** صبر نکن: از روی قرارداد (proto یا OpenAPI) و با یک لایه‌ی جعلی جلو برو. جدول «وابستگی‌ها» در صفحه‌ی هر هفته می‌گوید چه چیزی کی می‌رسد.

**وقتی زودتر تمام کردی.** به این ترتیب: ۱) کاری که کس دیگری منتظرش است، ۲) بازبینی PRهای باز، ۳) کار بعدی نقش خودت، ۴) کار هفته‌ی بعد نقش خودت.

**وقتی گیر کردی.** بیش از یک ساعت: در issue همان کار بپرس. بیش از یک روز: به منتور بگو تا برنامه را عوض کند. عقب‌افتادگی را همان روز در گزارش روزانه بنویس، نه روز دمو.

**وقتی کسی نیست.** زوجی برای جایگزینی نیست. اگر کسی بیش از دو روز نیست، منتور کارهایی را که معیار پایان هفته به آن‌ها بسته است به دو نفر دیگر می‌دهد. به همین دلیل دو نقش Go کد همدیگر را بازبینی می‌کنند: بازبین هر کد، نفر دومی است که آن را می‌فهمد.

## ۵. کارهای هر نقش، هفته به هفته

این جدول‌ها از [فهرست کارها](backlog.md) آمده‌اند. ستون «نکته» می‌گوید هر کار در طرح سه‌نفره چه فرقی کرده است؛ هر چیزی که آنجا نیامده، همان است که در تحویل و issue همان کار نوشته شده. بعضی کارها در هفته‌ای انجام می‌شوند که با عدد شناسه‌شان فرق دارد؛ ملاک، ستون «هفته» است.

### نقش «فرانت» (`role:web`)

| هفته | شناسه | کار | برچسب | نکته | issue |
|---|---|---|---|---|---|
| ۱ | `W1-WEB-1` | [اسکلت اپ](handoffs/week-1/web.md) |  |  | [#10](https://github.com/Tecso-Dev/sarmiz/issues/10) |
| ۱ | `W1-WEB-2` | [توکن‌های طراحی و اجزای پایه](handoffs/week-1/web.md) |  |  | [#11](https://github.com/Tecso-Dev/sarmiz/issues/11) |
| ۱ | `W1-WEB-3` | [wireframe صفحه‌های اصلی](handoffs/week-1/web.md) | بازبینی منتور |  | [#12](https://github.com/Tecso-Dev/sarmiz/issues/12) |
| ۱ | `W1-WEB-5` | [کلاینت تایپ‌شده و الگوی خطا](handoffs/week-1/web.md) |  |  | [#14](https://github.com/Tecso-Dev/sarmiz/issues/14) |
| ۲ | `W1-WEB-4` | [ورود به پنل و ساخت کسب‌وکار](handoffs/week-1/web.md) |  | صفحه‌ی ورود را هفته‌ی ۱ روی لایه‌ی جعلی شروع کن؛ اتصال واقعی و ساخت کسب‌وکار در هفته‌ی ۲، چون `CreateVenue` (`W1-CORE-3`) هفته‌ی ۲ می‌رسد. | [#13](https://github.com/Tecso-Dev/sarmiz/issues/13) |
| ۲ | `W2-WEB-1` | [ویرایشگر منو در پنل](handoffs/week-2/web.md) |  | بارگذاری عکس در ویرایشگر وقتی کامل می‌شود که `W2-CORE-3` در هفته‌ی ۳ برسد. | [#32](https://github.com/Tecso-Dev/sarmiz/issues/32) |
| ۲ | `W2-WEB-3` | [صفحه‌ی میزها، طراح QR و چاپ](handoffs/week-2/web.md) |  |  | [#34](https://github.com/Tecso-Dev/sarmiz/issues/34) |
| ۲ | `W2-WEB-4` | [منوی مهمان](handoffs/week-2/web.md) |  |  | [#35](https://github.com/Tecso-Dev/sarmiz/issues/35) |
| ۳ | `W2-WEB-2` | [ویرایشگر گزینه‌ها](handoffs/week-2/web.md) |  |  | [#33](https://github.com/Tecso-Dev/sarmiz/issues/33) |
| ۳ | `W3-WEB-1` | [سبد خرید مهمان و ثبت سفارش](handoffs/week-3/web.md) |  |  | [#50](https://github.com/Tecso-Dev/sarmiz/issues/50) |
| ۳ | `W3-WEB-2` | [صفحه‌ی زنده‌ی وضعیت سفارش، گارسون و صورت‌حساب](handoffs/week-3/web.md) |  | دکمه‌های «صدا زدن گارسون» و «درخواست صورت‌حساب» وقتی `W3-ORD-1` در هفته‌ی ۴ برسد وصل می‌شوند. | [#51](https://github.com/Tecso-Dev/sarmiz/issues/51) |
| ۳ | `W3-WEB-3` | [صفحه‌ی زنده‌ی آشپزخانه و صندوق](handoffs/week-3/web.md) |  | `W3-WEB-4` هم در همین کار است. | [#52](https://github.com/Tecso-Dev/sarmiz/issues/52) |
| ۴ | `W4-WEB-1` | [جریان پرداخت مهمان](handoffs/week-4/web.md) |  |  | [#65](https://github.com/Tecso-Dev/sarmiz/issues/65) |
| ۴ | `W4-WEB-2` | [تنظیمات پنل](handoffs/week-4/web.md) |  | `W2-WEB-5` هم در همین کار است. ویرایشگر منوی زمان‌دار و pairing به انتشار ۲ رفته‌اند؛ کلید «تمام شد» روی صفحه‌ی آشپزخانه می‌ماند. | [#66](https://github.com/Tecso-Dev/sarmiz/issues/66) |
| ۴ | `W5-WEB-3` | [پنل ادمین Tecso](handoffs/week-5/web.md) |  | صفحه‌ی ادمین فقط چیزهایی را دارد که `W4-CORE-2` و `AdminSetPaymentMode` می‌دهند. | [#79](https://github.com/Tecso-Dev/sarmiz/issues/79) |
| ۵ | `W5-WEB-1` | [صفحه‌ی معرفی و صفحه‌ی قیمت](handoffs/week-5/web.md) |  |  | [#77](https://github.com/Tecso-Dev/sarmiz/issues/77) |
| ۵ | `W5-WEB-4` | [دو دمو، «امتحان کن»، لینک منو برای اینستاگرام، دسترس‌پذیری](handoffs/week-5/web.md) |  |  | [#80](https://github.com/Tecso-Dev/sarmiz/issues/80) |
| ۵ | `W5-WEB-5` | [تست‌های سرتاسری با Playwright](handoffs/week-5/web.md) |  |  | [#81](https://github.com/Tecso-Dev/sarmiz/issues/81) |

### نقش «ورود و منو» (`role:menu`)

| هفته | شناسه | کار | برچسب | نکته | issue |
|---|---|---|---|---|---|
| ۱ | `W1-CORE-1` | [نهایی کردن طرح داده](handoffs/week-1/core.md) | بازبینی منتور |  | [#2](https://github.com/Tecso-Dev/sarmiz/issues/2) |
| ۱ | `W1-CORE-2` | [سرویس identity](handoffs/week-1/core.md) | بازبینی منتور |  | [#3](https://github.com/Tecso-Dev/sarmiz/issues/3) |
| ۱ | `W1-CORE-4` | [قرارداد proto](handoffs/week-1/core.md) |  |  | [#5](https://github.com/Tecso-Dev/sarmiz/issues/5) |
| ۱ | `W1-PA-4` | [اسکلت gateway](handoffs/week-1/platform-ai.md) |  |  | [#18](https://github.com/Tecso-Dev/sarmiz/issues/18) |
| ۲ | `W1-CORE-3` | [اسکلت catalog و ساخت کسب‌وکار](handoffs/week-1/core.md) |  |  | [#4](https://github.com/Tecso-Dev/sarmiz/issues/4) |
| ۲ | `W2-CORE-1` | [دسته‌ها و آیتم‌های منو](handoffs/week-2/core.md) |  |  | [#22](https://github.com/Tecso-Dev/sarmiz/issues/22) |
| ۲ | `W2-CORE-4` | [میزها و QR](handoffs/week-2/core.md) |  |  | [#25](https://github.com/Tecso-Dev/sarmiz/issues/25) |
| ۲ | `W2-CORE-5` | [منوی عمومی](handoffs/week-2/core.md) |  |  | [#26](https://github.com/Tecso-Dev/sarmiz/issues/26) |
| ۲ | `W2-PA-1` | [مسیرهای کامل gateway، نقش‌ها و محدودیت نرخ](handoffs/week-2/platform-ai.md) |  |  | [#37](https://github.com/Tecso-Dev/sarmiz/issues/37) |
| ۳ | `W2-CORE-2` | [گزینه‌های آیتم](handoffs/week-2/core.md) |  |  | [#23](https://github.com/Tecso-Dev/sarmiz/issues/23) |
| ۳ | `W2-CORE-3` | [عکس و برند کسب‌وکار](handoffs/week-2/core.md) |  |  | [#24](https://github.com/Tecso-Dev/sarmiz/issues/24) |
| ۳ | `W2-CORE-6` | [قرارداد قیمت‌گذاری برای سرویس سفارش](handoffs/week-2/core.md) |  | روز اول هفته‌ی ۳ تحویل بده، چون `W2-ORD-1` منتظرش است. | [#27](https://github.com/Tecso-Dev/sarmiz/issues/27) |
| ۳ | `W2-PA-2` | [object storage و CDN](handoffs/week-2/platform-ai.md) |  |  | [#38](https://github.com/Tecso-Dev/sarmiz/issues/38) |
| ۳ | `W2-PA-5` | [داده‌ی نمونه و اسکریپت کسب‌وکار دمو](handoffs/week-2/platform-ai.md) |  |  | [#41](https://github.com/Tecso-Dev/sarmiz/issues/41) |
| ۴ | `W3-CORE-2` | [کلید «تمام شد» (منوی زمان‌دار در انتشار ۲)](handoffs/week-3/core.md) |  | فقط کلید «تمام شد» (`SetItemAvailability` و اثرش در منوی عمومی و `PriceItems`). منوی زمان‌دار به انتشار ۲ رفته است. | [#43](https://github.com/Tecso-Dev/sarmiz/issues/43) |
| ۴ | `W4-CORE-2` | [API ادمین Tecso](handoffs/week-4/core.md) |  |  | [#59](https://github.com/Tecso-Dev/sarmiz/issues/59) |
| ۴ | `W4-PA-1` | [پشتیبان‌گیری شبانه](handoffs/week-4/platform-ai.md) |  |  | [#69](https://github.com/Tecso-Dev/sarmiz/issues/69) |
| ۴ | `W4-PA-3` | [مجموعه‌ی تست جداسازی کسب‌وکارها](handoffs/week-4/platform-ai.md) |  | متدهای اعضا در انتشار ۲اند؛ فقط endpointهایی را که وجود دارند بسنج. | [#71](https://github.com/Tecso-Dev/sarmiz/issues/71) |
| ۵ | `W2-PA-3` | [لاگ مرکزی و ردگیری خطا](handoffs/week-2/platform-ai.md) |  |  | [#39](https://github.com/Tecso-Dev/sarmiz/issues/39) |
| ۵ | `W3-PA-1` | [metric، trace و داشبوردها](handoffs/week-3/platform-ai.md) |  | `W3-PA-2` هم در همین کار است. اول metric، داشبورد و هشدار؛ trace با Tempo فقط اگر وقت ماند. | [#54](https://github.com/Tecso-Dev/sarmiz/issues/54) |
| ۵ | `W4-CORE-3` | [لینک عمومی منو و بهینه‌سازی منوی عمومی](handoffs/week-4/core.md) |  |  | [#60](https://github.com/Tecso-Dev/sarmiz/issues/60) |
| ۵ | `W5-CORE-2` | [کسب‌وکارهای دمو، بازسازی شبانه، کارایی و رفع باگ](handoffs/week-5/core.md) |  | `W5-PA-4` هم در همین کار است. ترجمه‌ی منوی دمو دستی است، دست‌کم `en`. | [#74](https://github.com/Tecso-Dev/sarmiz/issues/74) |

### نقش «سفارش و زیرساخت» (`role:orders`)

| هفته | شناسه | کار | برچسب | نکته | issue |
|---|---|---|---|---|---|
| ۱ | `W1-ORD-1` | [نهایی کردن طرح داده و ماشین‌های وضعیت](handoffs/week-1/order.md) | بازبینی منتور |  | [#6](https://github.com/Tecso-Dev/sarmiz/issues/6) |
| ۱ | `W1-PA-1` | [محیط محلی](handoffs/week-1/platform-ai.md) |  | دیتابیس `ai`، pgvector و Ollama لازم نیست. در زمان نوشتن این طرح، image رسمی MinIO در Docker Hub پیدا نمی‌شد: روز اول بررسی کن و اگر نبود، یک object storage سازگار با S3 مثل RustFS بگذار و انتخاب را در `deploy/README.md` بنویس. اگر پورت ۵۴۳۲ روی ماشینی گرفته است، پورت PostgreSQL را در Compose قابل تنظیم کن. | [#15](https://github.com/Tecso-Dev/sarmiz/issues/15) |
| ۱ | `W1-PA-2` | [شاسی مشترک Go](handoffs/week-1/platform-ai.md) |  |  | [#16](https://github.com/Tecso-Dev/sarmiz/issues/16) |
| ۱ | `W1-PA-3` | [ابزار Protobuf](handoffs/week-1/platform-ai.md) |  | stubهای Python لازم نیست. | [#17](https://github.com/Tecso-Dev/sarmiz/issues/17) |
| ۱ | `W1-PA-5` | [CI](handoffs/week-1/platform-ai.md) |  | Ruff و تست‌های Python لازم نیست. | [#19](https://github.com/Tecso-Dev/sarmiz/issues/19) |
| ۲ | `W1-ORD-2` | [اسکلت order و قرارداد سفارش](handoffs/week-1/order.md) |  |  | [#7](https://github.com/Tecso-Dev/sarmiz/issues/7) |
| ۲ | `W1-ORD-4` | [پایه‌ی رویدادها در شاسی](handoffs/week-1/order.md) |  |  | [#9](https://github.com/Tecso-Dev/sarmiz/issues/9) |
| ۲ | `W1-PA-6` | [cluster و استقرار](handoffs/week-1/platform-ai.md) |  | روز اول هفته‌ی ۱ فقط یک ساعت دسترسی سرور به registry و DNS را بسنج و نتیجه را در گروه تیم بنویس. خود cluster و استقرار در هفته‌ی ۲ است. نسخه‌ی «سلام» سرویس `ai` لازم نیست؛ هر سرویسی که تا آن روز اسکلت دارد بالا می‌آید. | [#20](https://github.com/Tecso-Dev/sarmiz/issues/20) |
| ۲ | `W2-ORD-1` | [ساخت سفارش](handoffs/week-2/order.md) |  | تا `W2-CORE-6` برسد (روز اول هفته‌ی ۳)، با `catalog` جعلی پشت یک interface کار کن. | [#28](https://github.com/Tecso-Dev/sarmiz/issues/28) |
| ۳ | `W2-ORD-2` | [ماشین وضعیت و APIهای پنل](handoffs/week-2/order.md) |  |  | [#29](https://github.com/Tecso-Dev/sarmiz/issues/29) |
| ۳ | `W2-ORD-3` | [رویدادهای سفارش](handoffs/week-2/order.md) |  |  | [#30](https://github.com/Tecso-Dev/sarmiz/issues/30) |
| ۳ | `W2-ORD-4` | [کانال‌های realtime](handoffs/week-2/order.md) |  | `W1-ORD-3` هم در همین کار است. | [#31](https://github.com/Tecso-Dev/sarmiz/issues/31) |
| ۳ | `W3-ORD-3` | [پرداخت پای صندوق و «سفارش‌های من»](handoffs/week-3/order.md) | بازبینی منتور |  | [#48](https://github.com/Tecso-Dev/sarmiz/issues/48) |
| ۳ | `W3-ORD-4` | [طراحی ماژول پرداخت](handoffs/week-3/order.md) | بازبینی منتور |  | [#49](https://github.com/Tecso-Dev/sarmiz/issues/49) |
| ۴ | `W3-ORD-1` | [درخواست خدمت](handoffs/week-3/order.md) |  |  | [#46](https://github.com/Tecso-Dev/sarmiz/issues/46) |
| ۴ | `W3-ORD-2` | [محکم‌کاری قواعد سفارش](handoffs/week-3/order.md) |  |  | [#47](https://github.com/Tecso-Dev/sarmiz/issues/47) |
| ۴ | `W4-ORD-1` | [تنظیمات پرداخت کسب‌وکار](handoffs/week-4/order.md) | بازبینی منتور |  | [#61](https://github.com/Tecso-Dev/sarmiz/issues/61) |
| ۴ | `W4-ORD-2` | [پرداخت آنلاین در محیط آزمایشی](handoffs/week-4/order.md) | بازبینی منتور |  | [#62](https://github.com/Tecso-Dev/sarmiz/issues/62) |
| ۵ | `W5-ORD-1` | [تاب‌آوری](handoffs/week-5/order.md) |  |  | [#75](https://github.com/Tecso-Dev/sarmiz/issues/75) |
| ۵ | `W5-ORD-2` | [کارایی و رفع باگ از روی تست بار](handoffs/week-5/order.md) |  | `W3-PA-3` هم در همین کار است. اول اسکریپت‌های k6 و گزارش تست بار، بعد رفع کندترین مسیرها. | [#76](https://github.com/Tecso-Dev/sarmiz/issues/76) |
| ۵ | `W5-PA-2` | [تمرین بازیابی و runbook](handoffs/week-5/platform-ai.md) |  |  | [#83](https://github.com/Tecso-Dev/sarmiz/issues/83) |
| ۵ | `W5-PA-3` | [آمادگی production](handoffs/week-5/platform-ai.md) |  | `W4-PA-2` هم در همین کار است. | [#84](https://github.com/Tecso-Dev/sarmiz/issues/84) |

### هفته‌ی ۶: همه با هم

جزئیات در [صفحه‌ی هفته‌ی ۶](handoffs/week-6/README.md) است.

| شناسه | کار | رهبری |
|---|---|---|
| `W6-ALL-1` | بازبینی امنیتی کامل | سفارش و زیرساخت، با منتور |
| `W6-ALL-2` | روز شکار باگ | فرانت |
| `W6-ALL-3` | اولین پرداخت واقعی | سفارش و زیرساخت، با منتور |
| `W6-ALL-4` | مستندات | راهنمای برنامه‌نویس: سفارش و زیرساخت؛ راهنمای صاحب کسب‌وکار: فرانت، با کمک ورود و منو |
| `W6-ALL-5` | سنجیدن معیارهای «تمام شد» | ورود و منو |
| `W6-ALL-6` | روز دمو و تحویل به دوره‌ی بعد | منتور |

## ۶. چه چیزی ساخته نمی‌شود

این‌ها در انتشار ۱ ساخته نمی‌شوند، حتی اگر یک تحویل، فصل راهنما یا دستیار AI از آن‌ها حرف بزند:

- سرویس `ai` و هر قابلیت هوش مصنوعی: ترجمه‌ی خودکار، ساخت منو از عکس، گارسون هوشمند
- ساخت منو از فایل Excel
- منوی زمان‌دار (کلید «تمام شد» ساخته می‌شود)
- پیشنهاد «با این می‌چسبد»
- گزارش فروش و داشبورد فروش
- امتیاز مهمان بعد از سفارش
- API اعضا و مدیریت کارکنان
- هر چیزی که در [نقشه‌ی انتشارها](roadmap.md) مال انتشار ۲ یا ۳ است

فهرست دقیق کارهایی که کنار رفتند در [فهرست کارها](backlog.md) است. اگر شک داری چیزی در محدوده هست یا نه، در issue از منتور بپرس.

## ۷. اگر عقب افتادید: خط برش دوم

اگر آخر یک هفته معیار پایانش برقرار نیست، منتور این کارها را به همین ترتیب به انتشار ۲ می‌فرستد، و هر بار فقط تا جایی که لازم است:

1. `W5-WEB-3` پنل ادمین. ادمین Tecso با چند درخواست مستند (`curl`) کار می‌کند.
2. `W4-CORE-3` لینک عمومی منو با slug و بهینه‌سازی منوی عمومی، و صفحه‌ی لینک اینستاگرام در `W5-WEB-4`.
3. `W3-ORD-1` درخواست خدمت، و دکمه‌های گارسون و صورت‌حساب در `W3-WEB-2`.
4. `W5-ORD-2` تست بار. به‌جایش یک اندازه‌گیری دستی از منوی مهمان و ثبت سفارش.
5. `W2-CORE-3` و `W2-PA-2` عکس‌ها. منو بدون عکس و لوگو، فقط با رنگ کسب‌وکار.

این‌ها هرگز حذف نمی‌شوند: ورود، منو، میز و QR، منوی مهمان، ثبت سفارش، صفحه‌ی آشپزخانه، پرداخت پای صندوق، پرداخت آزمایشی با بازبینی منتور، پشتیبان‌گیری، تست جداسازی و بازبینی امنیتی.

## ۸. فرض‌های این طرح

- هر نفر تمام‌وقت کار می‌کند، حدود ۴۰ ساعت در هفته. اگر کسی پاره‌وقت است، منتور خط برش دوم را از هفته‌ی ۱ فعال می‌کند.
- منتور مالک محصول است: کد محصول نمی‌نویسد، PRهای ورود و پرداخت را حداکثر ظرف یک روز بازبینی می‌کند و آخر هر هفته دمو می‌گیرد.
- همه با دستیار AI کار می‌کنند و قواعد [AGENTS.md](../AGENTS.md) و [فصل ۲۰: کار با AI](guide/20-working-with-ai.md) را رعایت می‌کنند.

</div>
