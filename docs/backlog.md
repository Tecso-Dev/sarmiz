<div dir="rtl">

# فهرست کارها

همه‌ی کارهای ۶ هفته‌ی انتشار ۱ برای تیم سه‌نفره ([سند تصمیم ۷](decisions/0007-three-person-team.md)). هر کار یک issue در GitHub با همین شناسه دارد و جزئیاتش در تحویل همان کار است. صاحب هر نقش در [تیم و تقسیم کار](team.md) آمده است.

[فهرست مستندات](README.md) | [تیم و تقسیم کار](team.md) | [راهنمای تحویل‌ها](handoffs/README.md)

**چطور بخوانی:** کارها به ترتیب **هفته‌ی اجرا** آمده‌اند. شناسه‌ی هر کار عوض نشده است، پس بعضی کارها در هفته‌ای انجام می‌شوند که با عدد شناسه‌شان فرق دارد؛ مثلاً `W2-CORE-2` در هفته‌ی ۳ انجام می‌شود. ستون «تغییر» می‌گوید هر کار در طرح سه‌نفره چه فرقی کرده است. برچسب «بازبینی منتور» یعنی کار بدون تأیید منتور merge نمی‌شود.

## هفته‌ی ۰: آماده‌سازی منتور

**معیار پایان هفته:** دسترسی‌ها، دامنه، سرور و حساب‌ها آماده است و جلسه‌ی شروع برگزار شده است.

| شناسه | کار | نقش | برچسب | تغییر | issue |
|---|---|---|---|---|---|
| `W0-M-1` | [چک‌لیست آماده‌سازی منتور](handoffs/week-0-mentor.md) | منتور |  | تیم سه‌نفره است و نقش‌ها را خود تیم روز اول هفته‌ی ۱ انتخاب می‌کند. عکس منوها و هر چیز مربوط به ارزیابی AI لازم نیست. | [#1](https://github.com/Tecso-Dev/sarmiz/issues/1) |

## هفته‌ی ۱: پایه

**معیار پایان هفته:** محیط محلی با یک دستور بالا می‌آید، CI سبز است، طرح داده و قراردادها تأیید منتور را دارند، و ورود با کد پیامکی از راه `gateway` روی محیط محلی کار می‌کند.

| شناسه | کار | نقش | برچسب | تغییر | issue |
|---|---|---|---|---|---|
| `W1-CORE-1` | [نهایی کردن طرح داده](handoffs/week-1/core.md) | ورود و منو | بازبینی منتور |  | [#2](https://github.com/Tecso-Dev/sarmiz/issues/2) |
| `W1-CORE-2` | [سرویس identity](handoffs/week-1/core.md) | ورود و منو | بازبینی منتور |  | [#3](https://github.com/Tecso-Dev/sarmiz/issues/3) |
| `W1-CORE-4` | [قرارداد proto](handoffs/week-1/core.md) | ورود و منو |  |  | [#5](https://github.com/Tecso-Dev/sarmiz/issues/5) |
| `W1-ORD-1` | [نهایی کردن طرح داده و ماشین‌های وضعیت](handoffs/week-1/order.md) | سفارش و زیرساخت | بازبینی منتور |  | [#6](https://github.com/Tecso-Dev/sarmiz/issues/6) |
| `W1-WEB-1` | [اسکلت اپ](handoffs/week-1/web.md) | فرانت |  |  | [#10](https://github.com/Tecso-Dev/sarmiz/issues/10) |
| `W1-WEB-2` | [توکن‌های طراحی و اجزای پایه](handoffs/week-1/web.md) | فرانت |  |  | [#11](https://github.com/Tecso-Dev/sarmiz/issues/11) |
| `W1-WEB-3` | [wireframe صفحه‌های اصلی](handoffs/week-1/web.md) | فرانت | بازبینی منتور |  | [#12](https://github.com/Tecso-Dev/sarmiz/issues/12) |
| `W1-WEB-5` | [کلاینت تایپ‌شده و الگوی خطا](handoffs/week-1/web.md) | فرانت |  |  | [#14](https://github.com/Tecso-Dev/sarmiz/issues/14) |
| `W1-PA-1` | [محیط محلی](handoffs/week-1/platform-ai.md) | سفارش و زیرساخت |  | دیتابیس `ai`، pgvector و Ollama لازم نیست. در زمان نوشتن این طرح، image رسمی MinIO در Docker Hub پیدا نمی‌شد: روز اول بررسی کن و اگر نبود، یک object storage سازگار با S3 مثل RustFS بگذار و انتخاب را در `deploy/README.md` بنویس. اگر پورت ۵۴۳۲ روی ماشینی گرفته است، پورت PostgreSQL را در Compose قابل تنظیم کن. | [#15](https://github.com/Tecso-Dev/sarmiz/issues/15) |
| `W1-PA-2` | [شاسی مشترک Go](handoffs/week-1/platform-ai.md) | سفارش و زیرساخت |  |  | [#16](https://github.com/Tecso-Dev/sarmiz/issues/16) |
| `W1-PA-3` | [ابزار Protobuf](handoffs/week-1/platform-ai.md) | سفارش و زیرساخت |  | stubهای Python لازم نیست. | [#17](https://github.com/Tecso-Dev/sarmiz/issues/17) |
| `W1-PA-4` | [اسکلت gateway](handoffs/week-1/platform-ai.md) | ورود و منو |  |  | [#18](https://github.com/Tecso-Dev/sarmiz/issues/18) |
| `W1-PA-5` | [CI](handoffs/week-1/platform-ai.md) | سفارش و زیرساخت |  | Ruff و تست‌های Python لازم نیست. | [#19](https://github.com/Tecso-Dev/sarmiz/issues/19) |

## هفته‌ی ۲: منو

**معیار پایان هفته:** روی سرور واقعی با دامنه و TLS، یک QR چاپ‌شده روی گوشی یک منوی واقعی باز می‌کند.

| شناسه | کار | نقش | برچسب | تغییر | issue |
|---|---|---|---|---|---|
| `W1-CORE-3` | [اسکلت catalog و ساخت کسب‌وکار](handoffs/week-1/core.md) | ورود و منو |  | از هفته‌ی ۱ به این هفته آمده است. | [#4](https://github.com/Tecso-Dev/sarmiz/issues/4) |
| `W1-ORD-2` | [اسکلت order و قرارداد سفارش](handoffs/week-1/order.md) | سفارش و زیرساخت |  | از هفته‌ی ۱ به این هفته آمده است. | [#7](https://github.com/Tecso-Dev/sarmiz/issues/7) |
| `W1-ORD-4` | [پایه‌ی رویدادها در شاسی](handoffs/week-1/order.md) | سفارش و زیرساخت |  | از هفته‌ی ۱ به این هفته آمده است. | [#9](https://github.com/Tecso-Dev/sarmiz/issues/9) |
| `W1-WEB-4` | [ورود به پنل و ساخت کسب‌وکار](handoffs/week-1/web.md) | فرانت |  | از هفته‌ی ۱ به این هفته آمده است. صفحه‌ی ورود را هفته‌ی ۱ روی لایه‌ی جعلی شروع کن؛ اتصال واقعی و ساخت کسب‌وکار در هفته‌ی ۲، چون `CreateVenue` (`W1-CORE-3`) هفته‌ی ۲ می‌رسد. | [#13](https://github.com/Tecso-Dev/sarmiz/issues/13) |
| `W1-PA-6` | [cluster و استقرار](handoffs/week-1/platform-ai.md) | سفارش و زیرساخت |  | از هفته‌ی ۱ به این هفته آمده است. روز اول هفته‌ی ۱ فقط یک ساعت دسترسی سرور به registry و DNS را بسنج و نتیجه را در گروه تیم بنویس. خود cluster و استقرار در هفته‌ی ۲ است. نسخه‌ی «سلام» سرویس `ai` لازم نیست؛ هر سرویسی که تا آن روز اسکلت دارد بالا می‌آید. | [#20](https://github.com/Tecso-Dev/sarmiz/issues/20) |
| `W2-CORE-1` | [دسته‌ها و آیتم‌های منو](handoffs/week-2/core.md) | ورود و منو |  |  | [#22](https://github.com/Tecso-Dev/sarmiz/issues/22) |
| `W2-CORE-4` | [میزها و QR](handoffs/week-2/core.md) | ورود و منو |  |  | [#25](https://github.com/Tecso-Dev/sarmiz/issues/25) |
| `W2-CORE-5` | [منوی عمومی](handoffs/week-2/core.md) | ورود و منو |  |  | [#26](https://github.com/Tecso-Dev/sarmiz/issues/26) |
| `W2-ORD-1` | [ساخت سفارش](handoffs/week-2/order.md) | سفارش و زیرساخت |  | تا `W2-CORE-6` برسد (روز اول هفته‌ی ۳)، با `catalog` جعلی پشت یک interface کار کن. | [#28](https://github.com/Tecso-Dev/sarmiz/issues/28) |
| `W2-WEB-1` | [ویرایشگر منو در پنل](handoffs/week-2/web.md) | فرانت |  | بارگذاری عکس در ویرایشگر وقتی کامل می‌شود که `W2-CORE-3` در هفته‌ی ۳ برسد. | [#32](https://github.com/Tecso-Dev/sarmiz/issues/32) |
| `W2-WEB-3` | [صفحه‌ی میزها، طراح QR و چاپ](handoffs/week-2/web.md) | فرانت |  |  | [#34](https://github.com/Tecso-Dev/sarmiz/issues/34) |
| `W2-WEB-4` | [منوی مهمان](handoffs/week-2/web.md) | فرانت |  |  | [#35](https://github.com/Tecso-Dev/sarmiz/issues/35) |
| `W2-PA-1` | [مسیرهای کامل gateway، نقش‌ها و محدودیت نرخ](handoffs/week-2/platform-ai.md) | ورود و منو |  |  | [#37](https://github.com/Tecso-Dev/sarmiz/issues/37) |

## هفته‌ی ۳: سفارش

**معیار پایان هفته:** سفارشی که مهمان با گوشی ثبت می‌کند، در کمتر از ۲ ثانیه روی صفحه‌ی آشپزخانه دیده می‌شود.

| شناسه | کار | نقش | برچسب | تغییر | issue |
|---|---|---|---|---|---|
| `W2-CORE-2` | [گزینه‌های آیتم](handoffs/week-2/core.md) | ورود و منو |  | از هفته‌ی ۲ به این هفته آمده است. | [#23](https://github.com/Tecso-Dev/sarmiz/issues/23) |
| `W2-CORE-3` | [عکس و برند کسب‌وکار](handoffs/week-2/core.md) | ورود و منو |  | از هفته‌ی ۲ به این هفته آمده است. | [#24](https://github.com/Tecso-Dev/sarmiz/issues/24) |
| `W2-CORE-6` | [قرارداد قیمت‌گذاری برای سرویس سفارش](handoffs/week-2/core.md) | ورود و منو |  | از هفته‌ی ۲ به این هفته آمده است. روز اول هفته‌ی ۳ تحویل بده، چون `W2-ORD-1` منتظرش است. | [#27](https://github.com/Tecso-Dev/sarmiz/issues/27) |
| `W2-ORD-2` | [ماشین وضعیت و APIهای پنل](handoffs/week-2/order.md) | سفارش و زیرساخت |  | از هفته‌ی ۲ به این هفته آمده است. | [#29](https://github.com/Tecso-Dev/sarmiz/issues/29) |
| `W2-ORD-3` | [رویدادهای سفارش](handoffs/week-2/order.md) | سفارش و زیرساخت |  | از هفته‌ی ۲ به این هفته آمده است. | [#30](https://github.com/Tecso-Dev/sarmiz/issues/30) |
| `W2-ORD-4` | [کانال‌های realtime](handoffs/week-2/order.md) | سفارش و زیرساخت |  | از هفته‌ی ۲ به این هفته آمده است. `W1-ORD-3` هم در همین کار است. | [#31](https://github.com/Tecso-Dev/sarmiz/issues/31) |
| `W2-WEB-2` | [ویرایشگر گزینه‌ها](handoffs/week-2/web.md) | فرانت |  | از هفته‌ی ۲ به این هفته آمده است. | [#33](https://github.com/Tecso-Dev/sarmiz/issues/33) |
| `W2-PA-2` | [object storage و CDN](handoffs/week-2/platform-ai.md) | ورود و منو |  | از هفته‌ی ۲ به این هفته آمده است. | [#38](https://github.com/Tecso-Dev/sarmiz/issues/38) |
| `W2-PA-5` | [داده‌ی نمونه و اسکریپت کسب‌وکار دمو](handoffs/week-2/platform-ai.md) | ورود و منو |  | از هفته‌ی ۲ به این هفته آمده است. | [#41](https://github.com/Tecso-Dev/sarmiz/issues/41) |
| `W3-ORD-3` | [پرداخت پای صندوق و «سفارش‌های من»](handoffs/week-3/order.md) | سفارش و زیرساخت | بازبینی منتور |  | [#48](https://github.com/Tecso-Dev/sarmiz/issues/48) |
| `W3-ORD-4` | [طراحی ماژول پرداخت](handoffs/week-3/order.md) | سفارش و زیرساخت | بازبینی منتور |  | [#49](https://github.com/Tecso-Dev/sarmiz/issues/49) |
| `W3-WEB-1` | [سبد خرید مهمان و ثبت سفارش](handoffs/week-3/web.md) | فرانت |  |  | [#50](https://github.com/Tecso-Dev/sarmiz/issues/50) |
| `W3-WEB-2` | [صفحه‌ی زنده‌ی وضعیت سفارش، گارسون و صورت‌حساب](handoffs/week-3/web.md) | فرانت |  | دکمه‌های «صدا زدن گارسون» و «درخواست صورت‌حساب» وقتی `W3-ORD-1` در هفته‌ی ۴ برسد وصل می‌شوند. | [#51](https://github.com/Tecso-Dev/sarmiz/issues/51) |
| `W3-WEB-3` | [صفحه‌ی زنده‌ی آشپزخانه و صندوق](handoffs/week-3/web.md) | فرانت |  | `W3-WEB-4` هم در همین کار است. | [#52](https://github.com/Tecso-Dev/sarmiz/issues/52) |

## هفته‌ی ۴: پرداخت و مدیریت

**معیار پایان هفته:** پرداخت آزمایشی سفارش را دقیقاً یک بار «پرداخت‌شده» می‌کند و منتور کد پرداخت را بازبینی کرده است.

| شناسه | کار | نقش | برچسب | تغییر | issue |
|---|---|---|---|---|---|
| `W3-CORE-2` | [کلید «تمام شد» (منوی زمان‌دار در انتشار ۲)](handoffs/week-3/core.md) | ورود و منو |  | از هفته‌ی ۳ به این هفته آمده است. فقط کلید «تمام شد» (`SetItemAvailability` و اثرش در منوی عمومی و `PriceItems`). منوی زمان‌دار به انتشار ۲ رفته است. | [#43](https://github.com/Tecso-Dev/sarmiz/issues/43) |
| `W3-ORD-1` | [درخواست خدمت](handoffs/week-3/order.md) | سفارش و زیرساخت |  | از هفته‌ی ۳ به این هفته آمده است. | [#46](https://github.com/Tecso-Dev/sarmiz/issues/46) |
| `W3-ORD-2` | [محکم‌کاری قواعد سفارش](handoffs/week-3/order.md) | سفارش و زیرساخت |  | از هفته‌ی ۳ به این هفته آمده است. | [#47](https://github.com/Tecso-Dev/sarmiz/issues/47) |
| `W4-CORE-2` | [API ادمین Tecso](handoffs/week-4/core.md) | ورود و منو |  |  | [#59](https://github.com/Tecso-Dev/sarmiz/issues/59) |
| `W4-ORD-1` | [تنظیمات پرداخت کسب‌وکار](handoffs/week-4/order.md) | سفارش و زیرساخت | بازبینی منتور |  | [#61](https://github.com/Tecso-Dev/sarmiz/issues/61) |
| `W4-ORD-2` | [پرداخت آنلاین در محیط آزمایشی](handoffs/week-4/order.md) | سفارش و زیرساخت | بازبینی منتور |  | [#62](https://github.com/Tecso-Dev/sarmiz/issues/62) |
| `W4-WEB-1` | [جریان پرداخت مهمان](handoffs/week-4/web.md) | فرانت |  |  | [#65](https://github.com/Tecso-Dev/sarmiz/issues/65) |
| `W4-WEB-2` | [تنظیمات پنل](handoffs/week-4/web.md) | فرانت |  | `W2-WEB-5` هم در همین کار است. ویرایشگر منوی زمان‌دار و pairing به انتشار ۲ رفته‌اند؛ کلید «تمام شد» روی صفحه‌ی آشپزخانه می‌ماند. | [#66](https://github.com/Tecso-Dev/sarmiz/issues/66) |
| `W4-PA-1` | [پشتیبان‌گیری شبانه](handoffs/week-4/platform-ai.md) | ورود و منو |  |  | [#69](https://github.com/Tecso-Dev/sarmiz/issues/69) |
| `W4-PA-3` | [مجموعه‌ی تست جداسازی کسب‌وکارها](handoffs/week-4/platform-ai.md) | ورود و منو |  | متدهای اعضا در انتشار ۲اند؛ فقط endpointهایی را که وجود دارند بسنج. | [#71](https://github.com/Tecso-Dev/sarmiz/issues/71) |
| `W5-WEB-3` | [پنل ادمین Tecso](handoffs/week-5/web.md) | فرانت |  | از هفته‌ی ۵ به این هفته آمده است. صفحه‌ی ادمین فقط چیزهایی را دارد که `W4-CORE-2` و `AdminSetPaymentMode` می‌دهند. | [#79](https://github.com/Tecso-Dev/sarmiz/issues/79) |

## هفته‌ی ۵: ویترین

**معیار پایان هفته:** یک نفر غریبه بدون کمک، دمو را از اسکن QR تا پرداخت آزمایشی کامل امتحان می‌کند.

| شناسه | کار | نقش | برچسب | تغییر | issue |
|---|---|---|---|---|---|
| `W2-PA-3` | [لاگ مرکزی و ردگیری خطا](handoffs/week-2/platform-ai.md) | ورود و منو |  | از هفته‌ی ۲ به این هفته آمده است. | [#39](https://github.com/Tecso-Dev/sarmiz/issues/39) |
| `W3-PA-1` | [metric، trace و داشبوردها](handoffs/week-3/platform-ai.md) | ورود و منو |  | از هفته‌ی ۳ به این هفته آمده است. `W3-PA-2` هم در همین کار است. اول metric، داشبورد و هشدار؛ trace با Tempo فقط اگر وقت ماند. | [#54](https://github.com/Tecso-Dev/sarmiz/issues/54) |
| `W4-CORE-3` | [لینک عمومی منو و بهینه‌سازی منوی عمومی](handoffs/week-4/core.md) | ورود و منو |  | از هفته‌ی ۴ به این هفته آمده است. | [#60](https://github.com/Tecso-Dev/sarmiz/issues/60) |
| `W5-CORE-2` | [کسب‌وکارهای دمو، بازسازی شبانه، کارایی و رفع باگ](handoffs/week-5/core.md) | ورود و منو |  | `W5-PA-4` هم در همین کار است. ترجمه‌ی منوی دمو دستی است، دست‌کم `en`. | [#74](https://github.com/Tecso-Dev/sarmiz/issues/74) |
| `W5-ORD-1` | [تاب‌آوری](handoffs/week-5/order.md) | سفارش و زیرساخت |  |  | [#75](https://github.com/Tecso-Dev/sarmiz/issues/75) |
| `W5-ORD-2` | [کارایی و رفع باگ از روی تست بار](handoffs/week-5/order.md) | سفارش و زیرساخت |  | `W3-PA-3` هم در همین کار است. اول اسکریپت‌های k6 و گزارش تست بار، بعد رفع کندترین مسیرها. | [#76](https://github.com/Tecso-Dev/sarmiz/issues/76) |
| `W5-WEB-1` | [صفحه‌ی معرفی و صفحه‌ی قیمت](handoffs/week-5/web.md) | فرانت |  |  | [#77](https://github.com/Tecso-Dev/sarmiz/issues/77) |
| `W5-WEB-4` | [دو دمو، «امتحان کن»، لینک منو برای اینستاگرام، دسترس‌پذیری](handoffs/week-5/web.md) | فرانت |  |  | [#80](https://github.com/Tecso-Dev/sarmiz/issues/80) |
| `W5-WEB-5` | [تست‌های سرتاسری با Playwright](handoffs/week-5/web.md) | فرانت |  |  | [#81](https://github.com/Tecso-Dev/sarmiz/issues/81) |
| `W5-PA-2` | [تمرین بازیابی و runbook](handoffs/week-5/platform-ai.md) | سفارش و زیرساخت |  |  | [#83](https://github.com/Tecso-Dev/sarmiz/issues/83) |
| `W5-PA-3` | [آمادگی production](handoffs/week-5/platform-ai.md) | سفارش و زیرساخت |  | `W4-PA-2` هم در همین کار است. | [#84](https://github.com/Tecso-Dev/sarmiz/issues/84) |

## هفته‌ی ۶: محکم‌کاری و انتشار

**معیار پایان هفته:** همه‌ی معیارهای «تمام شد» در طرح پروژه برقرار است.

| شناسه | کار | نقش | برچسب | تغییر | issue |
|---|---|---|---|---|---|
| `W6-ALL-1` | [بازبینی امنیتی کامل](handoffs/week-6/README.md) | همه‌ی تیم | بازبینی منتور |  | [#86](https://github.com/Tecso-Dev/sarmiz/issues/86) |
| `W6-ALL-2` | [روز شکار باگ](handoffs/week-6/README.md) | همه‌ی تیم |  |  | [#87](https://github.com/Tecso-Dev/sarmiz/issues/87) |
| `W6-ALL-3` | [اولین پرداخت واقعی](handoffs/week-6/README.md) | همه‌ی تیم | بازبینی منتور |  | [#88](https://github.com/Tecso-Dev/sarmiz/issues/88) |
| `W6-ALL-4` | [مستندات](handoffs/week-6/README.md) | همه‌ی تیم |  |  | [#89](https://github.com/Tecso-Dev/sarmiz/issues/89) |
| `W6-ALL-5` | [سنجیدن معیارهای «تمام شد»](handoffs/week-6/README.md) | همه‌ی تیم |  |  | [#90](https://github.com/Tecso-Dev/sarmiz/issues/90) |
| `W6-ALL-6` | [روز دمو و تحویل به دوره‌ی بعد](handoffs/week-6/README.md) | همه‌ی تیم |  |  | [#91](https://github.com/Tecso-Dev/sarmiz/issues/91) |

## کارهایی که در کار دیگری ادغام شدند

این کارها جدا انجام نمی‌شوند. محدوده و معیارهای پذیرششان جزو کار مقصد است و صاحب کار مقصد آن‌ها را هم انجام می‌دهد. issue آن‌ها بسته شده است.

| شناسه | کار | ادغام در | issue |
|---|---|---|---|
| `W1-ORD-3` | [اسکلت realtime](handoffs/week-1/order.md) | `W2-ORD-4` | [#8](https://github.com/Tecso-Dev/sarmiz/issues/8) |
| `W2-WEB-5` | [تنظیمات برند کسب‌وکار](handoffs/week-2/web.md) | `W4-WEB-2` | [#36](https://github.com/Tecso-Dev/sarmiz/issues/36) |
| `W3-WEB-4` | [فهرست و جزئیات سفارش‌ها در پنل](handoffs/week-3/web.md) | `W3-WEB-3` | [#53](https://github.com/Tecso-Dev/sarmiz/issues/53) |
| `W3-PA-2` | [هشدارها و پایش از بیرون](handoffs/week-3/platform-ai.md) | `W3-PA-1` | [#55](https://github.com/Tecso-Dev/sarmiz/issues/55) |
| `W3-PA-3` | [تست بار با k6](handoffs/week-3/platform-ai.md) | `W5-ORD-2` | [#56](https://github.com/Tecso-Dev/sarmiz/issues/56) |
| `W4-PA-2` | [امنیت در CI و کلاستر](handoffs/week-4/platform-ai.md) | `W5-PA-3` | [#70](https://github.com/Tecso-Dev/sarmiz/issues/70) |
| `W5-PA-4` | [محتوای کافه و رستوران دمو](handoffs/week-5/platform-ai.md) | `W5-CORE-2` | [#85](https://github.com/Tecso-Dev/sarmiz/issues/85) |

## کارهایی که به انتشار ۲ رفتند

این کارها در انتشار ۱ انجام نمی‌شوند، حتی اگر تحویل‌ها یا راهنما از آن‌ها حرف بزنند. issue آن‌ها باز می‌ماند، با milestone «Release 2» و برچسب `release-2`، تا دوره‌ی بعد از همین‌جا شروع کند.

| شناسه | کار | چرا | issue |
|---|---|---|---|
| `W1-PA-7` | [ارزیابی AI و اسکلت سرویس ai](handoffs/week-1/platform-ai.md) | سرویس `ai` و همه‌ی قابلیت‌های هوش مصنوعی به انتشار ۲ رفته‌اند. | [#21](https://github.com/Tecso-Dev/sarmiz/issues/21) |
| `W2-PA-4` | [ساخت منو در سرویس ai](handoffs/week-2/platform-ai.md) | سرویس `ai` و همه‌ی قابلیت‌های هوش مصنوعی به انتشار ۲ رفته‌اند. | [#40](https://github.com/Tecso-Dev/sarmiz/issues/40) |
| `W3-CORE-1` | [جریان ساخت منو از فایل](handoffs/week-3/core.md) | ساخت منو از فایل (عکس یا Excel) به انتشار ۲ رفته است؛ صاحب کسب‌وکار منو را در پنل وارد می‌کند. | [#42](https://github.com/Tecso-Dev/sarmiz/issues/42) |
| `W3-CORE-3` | [ترجمه‌ی منو](handoffs/week-3/core.md) | ترجمه‌ی خودکار به انتشار ۲ رفته است؛ صاحب کسب‌وکار ترجمه را در ویرایشگر منو دستی می‌نویسد. | [#44](https://github.com/Tecso-Dev/sarmiz/issues/44) |
| `W3-CORE-4` | [«با این می‌چسبد» و نشان‌ها](handoffs/week-3/core.md) | پیشنهاد «با این می‌چسبد» به انتشار ۲ رفته است؛ نشان‌ها با `W2-CORE-1` دستی گذاشته می‌شوند. | [#45](https://github.com/Tecso-Dev/sarmiz/issues/45) |
| `W3-PA-4` | [نشانی ترجمه در سرویس ai](handoffs/week-3/platform-ai.md) | سرویس `ai` و همه‌ی قابلیت‌های هوش مصنوعی به انتشار ۲ رفته‌اند. | [#57](https://github.com/Tecso-Dev/sarmiz/issues/57) |
| `W4-CORE-1` | [نقش‌ها و audit log](handoffs/week-4/core.md) | API اعضا و مدیریت نقش‌ها به انتشار ۲ رفته است؛ در انتشار ۱ هر کسب‌وکار فقط مالک دارد. | [#58](https://github.com/Tecso-Dev/sarmiz/issues/58) |
| `W4-ORD-3` | [گزارش فروش](handoffs/week-4/order.md) | گزارش فروش به انتشار ۲ رفته است. | [#63](https://github.com/Tecso-Dev/sarmiz/issues/63) |
| `W4-ORD-4` | [امتیاز بعد از سفارش](handoffs/week-4/order.md) | امتیاز مهمان به انتشار ۲ رفته است. | [#64](https://github.com/Tecso-Dev/sarmiz/issues/64) |
| `W4-WEB-3` | [داشبورد فروش و درخواست امتیاز](handoffs/week-4/web.md) | داشبورد فروش و درخواست امتیاز به انتشار ۲ رفته‌اند. | [#67](https://github.com/Tecso-Dev/sarmiz/issues/67) |
| `W4-WEB-4` | [صفحه‌ی ساخت منو از فایل و ترجمه‌ی خودکار](handoffs/week-4/web.md) | ساخت منو از فایل و ترجمه‌ی خودکار به انتشار ۲ رفته‌اند. | [#68](https://github.com/Tecso-Dev/sarmiz/issues/68) |
| `W4-PA-4` | [پایه‌ی گارسون هوشمند](handoffs/week-4/platform-ai.md) | سرویس `ai` و همه‌ی قابلیت‌های هوش مصنوعی به انتشار ۲ رفته‌اند. | [#72](https://github.com/Tecso-Dev/sarmiz/issues/72) |
| `W5-CORE-1` | [نشانی گارسون هوشمند برای مهمان (اختیاری)](handoffs/week-5/core.md) | سرویس `ai` و همه‌ی قابلیت‌های هوش مصنوعی به انتشار ۲ رفته‌اند. | [#73](https://github.com/Tecso-Dev/sarmiz/issues/73) |
| `W5-WEB-2` | [پنجره‌ی گفتگو با گارسون هوشمند (اختیاری)](handoffs/week-5/web.md) | سرویس `ai` و همه‌ی قابلیت‌های هوش مصنوعی به انتشار ۲ رفته‌اند. | [#78](https://github.com/Tecso-Dev/sarmiz/issues/78) |
| `W5-PA-1` | [تکمیل گارسون هوشمند و ارزیابی آن (اختیاری)](handoffs/week-5/platform-ai.md) | سرویس `ai` و همه‌ی قابلیت‌های هوش مصنوعی به انتشار ۲ رفته‌اند. | [#82](https://github.com/Tecso-Dev/sarmiz/issues/82) |

</div>
