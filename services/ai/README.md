<div dir="rtl">

# سرویس `ai`

ترجمه‌ی منو، ورود منو از عکس یا Excel، و پیشخدمت AI که فقط از روی منوی واقعی جواب می‌دهد.

[مشخصات فنی](../../docs/SPEC.md) | [فصل ۱۹: سرویس هوش مصنوعی](../../docs/guide/19-ai-service.md) | [مستندات AI](../../docs/ai/README.md) | [قواعد دستیار AI](../../AGENTS.md)

| | |
|---|---|
| زبان | Python با FastAPI |
| بخش مسئول | پلتفرم و هوش مصنوعی (`platform-ai`) |
| دیتابیس | `ai` با افزونه‌ی pgvector |
| ارتباط با بیرون | فقط HTTP داخلی |

## ۱. یک‌خطی

`ai` تنها سرویس Python سرمیز است و همه‌ی کار با مدل‌ها (از طریق Ollama) را انجام می‌دهد. اگر پایین باشد، منو، سفارش و پرداخت باید کامل کار کنند.

## ۲. مسئولیت‌ها

- ترجمه‌ی متن منو میان پنج زبان سرمیز (`fa`، `en`، `ar`، `ckb`، `azb`) وقتی `catalog` می‌خواهد.
- ورود منو به‌صورت غیرهم‌زمان: خواندن فایل از bucket `sarmiz-imports`، استخراج پیش‌نویس منو (دسته، آیتم، قیمت، گزینه) با امتیاز اطمینان و هشدارها. صاحب کسب‌وکار همیشه پیش‌نویس را قبل از اعمال بازبینی می‌کند.
- ایندکس منو برای پیشخدمت: با هر `menu.changed` منو را از `catalog` می‌خواند و آیتم‌های تغییرکرده را دوباره embed (تبدیل متن به بردار عددی) می‌کند.
- پیشخدمت AI به روش RAG: جست‌وجوی ترکیبی برداری و کلیدواژه‌ای، فیلترشده با `venue_id`، جواب با `cited_item_ids` و رد کردن سؤال بی‌ربط.

## ۳. چه چیزی مالِ این سرویس است

| جدول یا داده | ستون‌های کلیدی |
|---|---|
| `menu_chunks` | `venue_id`، `item_id`، `locale`، `content`، `embedding` (vector)، `menu_version` |
| bucket `sarmiz-imports` | فقط خواندن؛ صاحبش `catalog` است |
| انتخاب مدل‌ها | نتیجه‌ی ارزیابی هفته‌ی ۱ در <span dir="ltr">`docs/ai/`</span> |

## ۴. قرارداد

HTTP داخلی (بخش ۱۸ مشخصات فنی)، محافظت‌شده با هدر secret مشترک و NetworkPolicy:

| endpoint | ورودی | خروجی |
|---|---|---|
| `POST /v1/translate` | `venue_id`، `source_locale`، `target_locales`، `texts` (هر کدام `key`، `text`، `context`) | ترجمه برای هر کلید و هر زبان |
| `POST /v1/assistant` | `venue_id`، `locale`، `message`، `history` (حداکثر ۶ نوبت) | `answer`، `cited_item_ids`، `refused` |
| `GET /healthz`، `GET /readyz`، `GET /metrics` | | سلامت و متریک |

| رویداد | جهت |
|---|---|
| `sarmiz.catalog.import.requested` | مصرف می‌کند |
| `sarmiz.catalog.menu.changed` | مصرف می‌کند |
| `sarmiz.ai.import.completed` | منتشر می‌کند؛ `data`: `job_id`، `status`، `draft` یا `error` |

## ۵. به چه کسی وابسته است

| به | چطور | برای چه |
|---|---|---|
| `catalog` | gRPC، `SnapshotService.GetMenuSnapshot` | خواندن منو برای ایندکس |
| Ollama | پشت interface `LLMProvider` | chat، vision و embeddings |
| object storage | مستقیم | خواندن فایل ورود منو |

چه کسی صدایش می‌زند: فقط `catalog` (ترجمه و پیشخدمت). مرورگر و `gateway` هیچ‌وقت مستقیم به `ai` نمی‌رسند.

## ۶. قاعده‌هایی که نباید بشکنند

1. همه‌ی دسترسی به مدل از `LLMProvider` می‌گذرد. هیچ ماژولی مستقیم Ollama را صدا نمی‌زند.
2. هر خروجی مدل با Pydantic اعتبارسنجی می‌شود؛ خروجی نامعتبر خطا است، نه جواب.
3. متن منو و پیام مهمان داده‌اند، نه دستور. پیشخدمت ابزار ندارد، کاری انجام نمی‌دهد و فقط از منوی همان کسب‌وکار جواب می‌دهد.
4. هر جست‌وجو در `menu_chunks` با `venue_id` فیلتر می‌شود.
5. هیچ نشانی‌ای را که کاربر داده fetch نکن.
6. کار سنگین (ورود منو) از صف کار NATS با محدودیت هم‌زمانی می‌گذرد.
7. لاگ JSON با `structlog`؛ هیچ secret، توکن یا credential در لاگ نمی‌آید.
8. تست‌های واحد با provider جعلی اجرا می‌شوند و به مدل واقعی نیاز ندارند.

## ۷. ساختار پوشه

مشخصات فنی چیدمان Python را تعیین نکرده است. پیشنهاد اولیه:

</div>

```text
services/ai/
├── app/
│   ├── main.py         FastAPI app, health, metrics
│   ├── api/            translate, assistant routes
│   ├── providers/      LLMProvider, Ollama, fake
│   ├── importer/       import.requested consumer
│   ├── indexer/        menu.changed consumer, embeddings
│   └── models.py       Pydantic schemas
├── migrations/
├── tests/
├── Dockerfile
└── README.md
```

<div dir="rtl">

## ۸. اجرا و تست

دستورهای اجرا و تست را تیم در هفته‌ی ۱ می‌سازد و در بخش Commands فایل [AGENTS.md](../../AGENTS.md) می‌نویسد. تست با pytest؛ مجموعه‌ی نمونه‌ی ترجمه، دقت ورود روی ۵ منوی واقعی، و ۳۰ سؤال برای پیشخدمت شامل سؤال بی‌ربط و prompt injection (متنی که سعی می‌کند دستور مدل را عوض کند).

## ۹. در کدام هفته چه چیزی ساخته می‌شود

| هفته | کار | چه چیزی | تحویل |
|---|---|---|---|
| ۱ | `W1-PA-7` | اسکلت FastAPI، `LLMProvider`، ارزیابی مدل‌ها و گزارش go/no-go | [platform-ai](../../docs/handoffs/week-1/platform-ai.md) |
| ۲ | `W2-PA-3`، `W2-PA-4` | اتصال به GlitchTip و لاگ مرکزی، ورود منو (مسیر عکس اختیاری است) | [platform-ai](../../docs/handoffs/week-2/platform-ai.md) |
| ۳ | `W3-PA-4` | endpoint ترجمه با نمونه‌ی کیفیت برای هر زبان | [platform-ai](../../docs/handoffs/week-3/platform-ai.md) |
| ۴ | `W4-PA-4` | پایه‌ی پیشخدمت: ایندکس، بازیابی ترکیبی، رد سؤال بی‌ربط (اختیاری) | [platform-ai](../../docs/handoffs/week-4/platform-ai.md) |
| ۵ | `W5-PA-1` | تکمیل پیشخدمت و ارزیابی prompt injection (اختیاری) | [platform-ai](../../docs/handoffs/week-5/platform-ai.md) |
| ۶ | `W6-ALL-1` | بازبینی امنیتی کامل | [هفته‌ی ۶](../../docs/handoffs/week-6/README.md) |

## ۱۰. سؤال‌های باز

- مدل‌های ترجمه، vision و embedding بعد از ارزیابی هفته‌ی ۱ انتخاب می‌شوند (بخش ۲۰ مشخصات فنی، تصمیم ۵). شاید سرور مدل ماشین جدا بخواهد.
- `ai` رویداد منتشر می‌کند، ولی بخش ۷٫۴ جدول `outbox` یا `processed_events` برایش ندارد. اینکه انتشار `import.completed` و حذف رویداد تکراری چطور انجام شود را تیم در `W2-PA-4` تصمیم می‌گیرد و سند تصمیم می‌نویسد.
- ابزار migration دیتابیس `ai` (goose مثل سرویس‌های Go یا ابزار Python) را تیم در `W1-PA-7` تعیین می‌کند.

</div>
