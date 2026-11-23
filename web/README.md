<div dir="rtl">

# اپ وب (`web`)

اپ React سرمیز: منوی مهمان، پنل صاحب کسب‌وکار، صفحه‌ی آشپزخانه، صفحه‌ی معرفی و پنل ادمین Tecso، همه در یک اپ. مسئول این پوشه بخش فرانت (`web`) است.

[فهرست مستندات](../docs/README.md) | [فصل ۵: فرانت‌اند](../docs/guide/05-frontend.md)

## ۱. این اپ چیست

یک اپ Vite با React، TypeScript در حالت strict، Tailwind CSS، React Router و TanStack Query. خروجی build فایل‌های ثابت است که Nginx پشت CDN می‌دهد. مرورگر فقط با دو جا حرف می‌زند: `gateway` از راه REST روی <span dir="ltr">`/api/v1/*`</span> و `realtime` از راه WebSocket روی <span dir="ltr">`/ws`</span>.

## ۲. چهار گروه مسیر

هر گروه lazy بارگذاری می‌شود تا کد پنل و ادمین به گوشی مهمان نرسد.

| مسیر | مخاطب | نکته |
|---|---|---|
| <span dir="ltr">`/`</span> و <span dir="ltr">`/pricing`</span> | بازدیدکننده | از پیش به HTML ساخته می‌شود (prerender) برای موتورهای جست‌وجو |
| <span dir="ltr">`/t/:qrToken`</span>، <span dir="ltr">`/m/:slug`</span>، <span dir="ltr">`/o/:orderId`</span> | مهمان | بدون ورود؛ بودجه‌ی کارایی سخت |
| <span dir="ltr">`/panel/*`</span>، از جمله <span dir="ltr">`/panel/kitchen`</span> | صاحب کسب‌وکار و آشپزخانه | ورود با کد یک‌بارمصرف |
| <span dir="ltr">`/admin/*`</span> | ادمین Tecso | فقط با claim به نام `adm` |

مسیر زیرصفحه‌های پنل را تیم در `W1-WEB-1` تعیین می‌کند و همین‌جا اضافه می‌کند.

## ۳. قاعده‌هایی که نباید بشکنند

از `AGENTS.md` و بخش ۱۹ [مشخصات فنی](../docs/SPEC.md):

1. TypeScript strict و بدون `any`. نوع‌های API فقط از کلاینت ساخته‌شده از `docs/api/openapi.yaml` می‌آیند.
2. داده‌ی سرور با TanStack Query، با `staleTime` جدا برای هر منبع و کلید query که شناسه‌ی کسب‌وکار را دارد.
3. فقط utilityهای منطقی Tailwind: <span dir="ltr">`ms-`</span>، <span dir="ltr">`me-`</span>، <span dir="ltr">`ps-`</span>، <span dir="ltr">`pe-`</span>، `text-start`. هرگز چپ و راست. رابط اول راست‌به‌چپ است.
4. همه‌ی متن‌های دیدنی از لایه‌ی i18n می‌آیند. زبان رابط `fa` (پیش‌فرض) و `en`؛ جهت از زبان می‌آید (`fa`، `ar`، `ckb`، `azb` راست‌به‌چپ).
5. عدد و قیمت با `Intl.NumberFormat`؛ قیمت به تومان نشان داده می‌شود ولی API همیشه ریال است.
6. توکن‌ها فقط در کوکی‌های `HttpOnly` هستند. هیچ توکنی در `localStorage` یا state اپ نیست.
7. سبد مهمان در `localStorage` با کلید میز. جمع سفارش را سرور حساب می‌کند.
8. ناحیه‌ی لمس دست‌کم ۴۴ پیکسل، focus دیدنی، تضاد WCAG AA. متن زعفرانی روی زمینه‌ی کرم ممنوع.
9. متن منو و جواب گارسون هوشمند همیشه متن ساده‌اند، هرگز HTML.
10. error boundaryها خطا را به GlitchTip گزارش می‌دهند، بدون داده‌ی شخصی.
11. JavaScript مسیر مهمان حداکثر ۱۵۰ کیلوبایت gzip و LCP زیر ۲ ثانیه روی 4G.

رنگ‌ها و فونت از [راهنمای برند](../docs/brand/README.md) می‌آیند. لوگو و favicon آماده‌اند: محتوای <span dir="ltr">`docs/brand/logo/web/`</span> را در <span dir="ltr">`public/`</span> کپی کن ([راهنمای لوگو](../docs/brand/logo/README.md)).

## ۴. ساختار پوشه (پیشنهاد اولیه)

</div>

```text
web/
├── src/
│   ├── app/            router, providers, error boundaries
│   ├── routes/         guest/, panel/, admin/, landing/
│   ├── features/       menu, cart, orders, kitchen, auth, venue, payment, import
│   ├── components/ui/  Button, Input, Card, Sheet, Modal, Toast, Skeleton, EmptyState
│   ├── api/            generated/ (do not edit), client.ts, errors.ts, queryKeys.ts
│   ├── realtime/       WebSocket, backoff, event handling
│   ├── i18n/           fa.json, en.json
│   ├── lib/            money, format, storage helpers
│   └── styles/         tokens.css
├── public/             fonts (Vazirmatn), logo files from docs/brand/logo/web/, static files
└── README.md
```

<div dir="rtl">

هیچ فایلی در `routes/guest` از `routes/panel` یا `routes/admin` import نمی‌کند.

## ۵. ساختن کلاینت API

1. بخش پلتفرم `docs/api/openapi.yaml` را از protoها می‌سازد (`W1-PA-3`).
2. بخش فرانت در `W1-WEB-5` ابزار ساخت کلاینت TypeScript را انتخاب می‌کند و دستورش را در جدول بخش ۶ می‌نویسد.
3. خروجی در <span dir="ltr">`src/api/generated/`</span> می‌نشیند و دستی ویرایش نمی‌شود. اگر نوعی اشتباه است، proto را درست کن.
4. هر PR که `openapi.yaml` را عوض می‌کند، کلاینت را هم دوباره می‌سازد.

## ۶. اجرا و تست

دستورهای واقعی را تیم در هفته‌ی ۱ (`W1-WEB-1`) اینجا و در بخش «Commands» فایل `AGENTS.md` می‌نویسد.

| کار | دستور |
|---|---|
| نصب وابستگی‌ها | در هفته‌ی ۱ اضافه می‌شود |
| اجرای سرور توسعه | در هفته‌ی ۱ اضافه می‌شود |
| ساختن کلاینت API | در هفته‌ی ۱ اضافه می‌شود |
| lint و بررسی نوع | در هفته‌ی ۱ اضافه می‌شود |
| تست‌ها (Vitest) | در هفته‌ی ۱ اضافه می‌شود |
| تست سرتاسری (Playwright، در <span dir="ltr">`tests/e2e/`</span>) | در هفته‌ی ۵ اضافه می‌شود |
| build تولید | در هفته‌ی ۱ اضافه می‌شود |

## ۷. کارهای فرانت در هر هفته

| هفته | کارها | تحویل |
|---|---|---|
| ۱ | `W1-WEB-1`، `W1-WEB-2`، `W1-WEB-3`، `W1-WEB-4`، `W1-WEB-5` | [week-1/web.md](../docs/handoffs/week-1/web.md) |
| ۲ | `W2-WEB-1`، `W2-WEB-2`، `W2-WEB-3`، `W2-WEB-4`، `W2-WEB-5` | [week-2/web.md](../docs/handoffs/week-2/web.md) |
| ۳ | `W3-WEB-1`، `W3-WEB-2`، `W3-WEB-3`، `W3-WEB-4` | [week-3/web.md](../docs/handoffs/week-3/web.md) |
| ۴ | `W4-WEB-1`، `W4-WEB-2`، `W4-WEB-3`، `W4-WEB-4` | [week-4/web.md](../docs/handoffs/week-4/web.md) |
| ۵ | `W5-WEB-1`، `W5-WEB-2`، `W5-WEB-3`، `W5-WEB-4`، `W5-WEB-5` | [week-5/web.md](../docs/handoffs/week-5/web.md) |
| ۶ | کارهای مشترک `W6-ALL-1` تا `W6-ALL-6` | [week-6/README.md](../docs/handoffs/week-6/README.md) |

`W1-WEB-3` بازبینی منتور می‌خواهد. `W4-WEB-3` (بخش داشبورد) و `W5-WEB-2` اختیاری‌اند.

## ۸. بیشتر بخوان

- [فصل ۵: فرانت‌اند](../docs/guide/05-frontend.md) و [فصل ۲۲: چندزبانگی، راست‌به‌چپ و دسترس‌پذیری](../docs/guide/22-i18n-rtl-accessibility.md).
- [فصل ۱۷: تست](../docs/guide/17-testing.md) و [پوشه‌ی طراحی](../docs/design/README.md).
- [قواعد دستیارهای AI](../AGENTS.md) و [راهنمای مشارکت](../CONTRIBUTING.md).

</div>
