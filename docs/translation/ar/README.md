<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - رخصة MIT (انظر ملف LICENSE) -->
<div align="center">
  <img src="../../assets/omega-fuzz.png" alt="Omega-Fuzz" width="384">
</div>

# 🗱 OMEGA-FUZZ

**ماسح الثغرات**

> طُوّر بواسطة **kraynux** لصالح **Omega-server**  
> [https://kraynux.snake-mackarel.ts.net](https://kraynux.snake-mackarel.ts.net)

الصفحة الرسمية: [OMEGA-FUZZ](https://kraynux.snake-mackarel.ts.net/omega-fuzz/) &nbsp; لقطات الشاشة: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-fuzz/screenshots/)  

[![الرخصة: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![المنصة](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![الواجهة](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 الواجهة والتقارير المُصدَّرة متاحة بـ **17 لغة** — انظر [لغات الواجهة](#لغات-الواجهة).  
**اللغات:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](README.md)

**Omega-Fuzz** هو تطبيق طرفية محلي (واجهة TUI مبنية على [Textual](https://github.com/Textualize/textual) + واجهة CLI قابلة للبرمجة) ينفّذ اكتشافًا واختبارات أمان للويب (fuzzing عبر HTTP) في بيئات مصرّح بها: مختبرات، نسخ شخصية، أو اختبارات تمت الموافقة عليها صراحةً.

الأداة جزء من حزمة `omega-` ومبنية وفق Clean Architecture — راجع `docs/ARCHITECTURE.md` للتفاصيل التقنية الكاملة.

## 1. الرؤية والنطاق

### ما يفعله Omega-Fuzz

- يكتشف نطاق هدف واحد عبر BFS محدود بنطاق صريح (المخطط، النطاقات الفرعية، المسارات المسموحة/المحظورة، العمق)، ولا يعمل أبدًا دون ضوابط حماية.
- ينفّذ fuzzing عامًا على معاملات query string ورؤوس HTTP والنماذج `GET` الموجودة في كل URL مكتشف، ثم يفحص ثلاث عائلات من التواقيع: XSS عاكس غير مدمّر، حقن عام (كشف خطأ في الاستجابة)، ورؤوس أمان مفقودة أو مهيأة بشكل خاطئ — انظر [§5](#5-اختبارات-الأمان-المنفذة).
- يقيّم كل شذوذ على ثلاثة محاور (التأثير، قابلية الاستغلال، النطاق) ويستنتج درجة الخطورة (`low`/`medium`/`high`/`critical`)، مع إزالة التكرار وفق `(النوع، نقطة النهاية، المعامل)` والاحتفاظ بأفضل دليل — انظر [§6](#6-النتيجة-والخطورة).
- يدعم المصادقة (كوكي، رمز bearer، نموذج تسجيل دخول) عبر ملف YAML مخصص؛ ولا تُمرَّر بيانات الاعتماد أبدًا كنص صريح في سطر الأوامر.
- يعرض النتائج في TUI (Textual) أو CLI قابل للبرمجة، مع ثلاثة صيغ تصدير (JSON وMarkdown وHTML بخمسة ثيمات).
- يحفظ سجل الفحوصات ونتائجها (findings) بشكل دائم في SQLite، إضافة إلى قائمة أهداف مفضلة قابلة لإعادة الاستخدام.
- يتطلب تأكيدًا صريحًا (عبارة صارمة في الحالات الأكثر حساسية) قبل أي فحص عدواني أو موسّع أو مع تعطيل التحقق من TLS.

### ما لا يفعله Omega-Fuzz

- Fuzzing لهياكل JSON — الكود موجود (`plugins/fuzzers/json_body_fuzzer.py`) لكنه غير موصول (اكتشاف HTML/BFS لا ينتج أي مخطط API JSON أو مصدر قوالب قابل للاستخدام).
- Fuzzing لنماذج `POST`/`PUT`/`DELETE` — مستبعد من خط الأنابيب الآلي عن قصد (خطر الكتابة غير المقصودة على الهدف)؛ تُختبر نماذج `GET` فقط.
- اختبارات منطق الأعمال (IDOR، التحكم في التفويض، كسر سير العمل) — الكود موجود (`plugins/logic_tests/`) لكنه خارج خط الأنابيب الآلي، ولا يمكن استدعاؤه إلا بشكل منفصل ولا يُطلق أبدًا عبر فحص قياسي.
- فحص متعدد الأهداف بالتوازي — هدف واحد لكل فحص.
- إعادة التشغيل أو المقارنة أو التصدير من شاشة السجل — يُحفظ `Scan` و`Finding` فقط (لا التهيئة الفعلية الكاملة ولا الطلبات)؛ إعادة التشغيل أو التصدير من السجل من شأنه أن يُنشئ بيانات. الشاشة تشرح ذلك بدلًا من تقديم الميزة بصمت.
- عرض JavaScript من جهة العميل (تُجلب الصفحة كما قدّمها الخادم، ولا تُنفذ في متصفح headless).
- لوحة تحكم ويب.

## 2. التثبيت

### المتطلبات

- Python 3.10 أو أحدث
- اتصال بالإنترنت لتثبيت الاعتماديات
- لواجهة TUI: يجب تثبيت خط [Nerd Font](https://www.nerdfonts.com/) في الطرفية لعرض أيقونة الترويسة — بدونه يظهر المحرف كمربع فارغ (نفس قصور الإيموجي، لكنه أكثر شيوعًا لدى مستخدمي الطرفية). غيابه لا يؤثر على الأداء؛ وهو مسألة شكلية فقط.

### التثبيت

```bash
[ -d omega-fuzz ] && echo "ℹ️ تم فك الضغط هنا مسبقًا، يتم تجاوز الخطوة." || tar -xzf omega-fuzz.tar.gz
cd omega-fuzz/
chmod +x install.sh
./install.sh
```

يقوم `install.sh` بما يلي:

1. إنشاء البيئة الافتراضية `.venv` إذا لم تكن موجودة.
2. تثبيت الاعتماديات (`vendor/omega-lib/` ثم `pip install -e .`؛ ويبقى `pyproject.toml` المصدر الوحيد للحقيقة).
3. جعل `omega-fuzz.sh` و`install.sh` قابلين للتنفيذ.
4. إضافة الاسم المستعار `fuzz` إلى `~/.bashrc` و`~/.zshrc` (دون تكرار إن وُجد مسبقًا).

### الاعتماديات

مُعلنة في `pyproject.toml` (لا يوجد `requirements.txt`):

- `omega-lib`: مكتبة مشتركة للحزمة (ثيمات التصدير، كشف الطرفية، `ConfidenceLevel`) — مضمّنة في `vendor/omega-lib/`
- `httpx`: طلبات HTTP غير متزامنة (الاكتشاف + fuzzing)، وبث الاستجابة (لا يُحتفظ أبدًا بالاستجابة كاملة في الذاكرة، حتى مع ملف بحجم عدة غيغابايت يقدمه الهدف)
- `beautifulsoup4` + `lxml`: استخراج عناوين URL ونماذج HTML
- `jinja2`: القوالب لتصدير HTML
- `textual`: واجهة TUI، الثيمات، التكيف التلقائي مع الطرفية
- `pyyaml`: تحميل ملف `--auth-config`
- اعتماديات التطوير (`pip install -e ".[dev]"`): `pytest`، `pytest-asyncio`، `pytest-cov`، `pytest-httpserver`، `ruff`، `mypy`، `import-linter`

## 3. الاستخدام

### الوضع التفاعلي (TUI)

موصى به للاستخدام اليومي — يُشغّل دون وسائط:

```bash
./omega-fuzz.sh
```

إذا تم إنشاء الاسم المستعار، اكتب فقط `fuzz` في الطرفية:

```bash
fuzz
```

المسار: شاشة البداية (تُغلق بمفتاح أو نقرة) → القائمة الرئيسية (فحص / أهداف / إعدادات / سجل / مساعدة) → إدخال الهدف (URL كامل، مع مخطط `http://`/`https://` إلزامي)، إعداد مسبق أو تهيئة يدوية (نطاق + مستوى عدوانية)، مصادقة اختيارية، تحقق TLS، تجاوز الحدود → شاشة المراجعة (تأكيد بسيط، أو عبارة صارمة `OUI-J-AI-L-AUTORISATION` للحالات الحساسة) → الفحص (مؤشر تقدم غير محدد، وزر **إيقاف** متاح في أي وقت) → النتائج (findings، تصدير) → السجل (تفاصيل فحص سابق ونتائجه) والأهداف المفضلة من القائمة الرئيسية. التكيف مع الطرفية (الألوان، الحجم، التدهور الهيكلي) تلقائي.

#### اختصارات لوحة المفاتيح

| المفتاح | الإجراء |
|---|---|
| `↑` / `↓` | التنقل بين عناصر الشاشة |
| `Tab` / `Shift+Tab` | التنقل بين حقول النموذج |
| `Esc` | العودة إلى الشاشة السابقة (تأكيد الخروج في شاشة البداية) |
| `t` | الثيم التالي (يُطبق فورًا دون تأكيد) |
| `r` | تحديث كشف الطرفية |
| `a` | عرض المساعدة (جدول الإعدادات المسبقة المضمنة) |
| `q` | الخروج (مع تأكيد) |
| `Ctrl+P` | لوحة الأوامر (Theme, خروج, لقطة شاشة) |

### لغات الواجهة

الواجهة متاحة بـ 17 لغة: الفرنسية، الإنجليزية، الإسبانية، البرتغالية (البرازيل)، الإيطالية، الألمانية، الهولندية، البولندية، الروسية، الصينية المبسطة، الفيتنامية، التايلاندية، الإندونيسية، اليابانية، الكورية، الهندية، والعربية. يتم اختيار اللغة في الإعدادات («اللغة / Language») وتُطبق بعد إعادة تشغيل الواجهة؛ والمتغير `OMEGA_FUZZ_LANG` (مثل `OMEGA_FUZZ_LANG=en ./omega-fuzz.sh`) يفرض لغة لجلسة واحدة. عند التشغيل من omega-suite، يستخدم omega-fuzz لغة الحزمة. في طرفية نصية لينكس (TTY)، تظهر اللغات ذات الكتابة غير اللاتينية بالإنجليزية خلال الجلسة. ويبقى سطر الأوامر بالفرنسية.

### الوضع القابل للبرمجة (CLI)

```bash
# فحص باستخدام إعداد مسبق جاهز
./omega-fuzz.sh scan --target https://example.com --preset prod-safe

# دمج يدوي بين النطاق والعدوانية (دون إعداد مسبق)
./omega-fuzz.sh scan --target https://example.com --scope-profile standard --aggressiveness standard

# مع مصادقة (ملف YAML، لا بيانات اعتماد صريحة في سطر الأوامر)
./omega-fuzz.sh scan --target https://example.com --preset staging-full --auth-config auth.yaml

# Dry-run: يعرض التهيئة الفعلية والخطة التقديرية دون إرسال أي طلب
./omega-fuzz.sh scan --target https://example.com --preset prod-safe --dry-run

# تصدير محدد (مجلد، صيغ، ثيم HTML)
./omega-fuzz.sh scan --target https://example.com --preset prod-safe \
    --output-dir ./rapports --format html --export-theme omega-neon
```

خيارات الأمر `scan`:

| الخيار | الافتراضي | التأثير |
|---|---|---|
| `--target` | *(مطلوب)* | عنوان URL للهدف، مع مخطط `http://`/`https://` إلزامي (لا يُستكمل تلقائيًا أبدًا) |
| `--preset` | — | إعداد مسبق جاهز (انظر [§4](#4-ملفات-النطاق-والإعدادات-المسبقة)) |
| `--scope-profile` | — | ملف نطاق، يُدمج مع `--aggressiveness`، دون `--preset` |
| `--aggressiveness` | — | مستوى العدوانية، يُدمج مع `--scope-profile`، دون `--preset` |
| `--auth-config` | — | ملف YAML للمصادقة |
| `--insecure-tls` | معطل | يعطّل التحقق من TLS (يُطلق التأكيد المعزز) |
| `--max-duration` | *(من الملف)* | يتجاوز المدة القصوى (بالثواني) |
| `--max-requests` | *(من الملف)* | يتجاوز الحد الأقصى للطلبات |
| `--max-tests` | *(من الملف)* | يتجاوز الحد الأقصى للاختبارات |
| `--max-concurrent` | *(من الملف)* | يتجاوز الحد الأقصى للتزامن |
| `--dry-run` | معطل | يعرض التهيئة الفعلية والخطة التقديرية دون إرسال طلبات |
| `--output-dir` | `var/exports/` | مجلد التقارير المصدرة، بأسماء `<preset>-<طابع زمني>.<امتداد>` (يمكن تغييره من الإعدادات) |
| `--format` | `all` | `json` أو `markdown` أو `html` أو `all` |
| `--export-theme` | `omega-base` | ثيم تقرير HTML المُصدَّر (لا يؤثر على json/markdown) |

لا يوجد أمر فرعي `history`/`show` في CLI: السجل والأهداف المفضلة متاحة فقط من TUI.

إذا أنشأ `install.sh` الاسم المستعار، يعمل `fuzz scan ...` من أي مكان في الطرفية دون البادئة `./omega-fuzz.sh`.

## 4. ملفات النطاق والإعدادات المسبقة

### ملفات النطاق

| الملف | الوضع | أقصى عمق | القيود |
|---|---|---|---|
| `strict` | هدف دقيق | 1 | يحظر `/health` و`/ready` و`/metrics` و`/favicon.ico` و`/robots.txt` |
| `standard` | + نطاقات فرعية | 2 | يحظر النطاقات الفرعية الثابتة الشائعة، والمسارات التقنية، والأصول (صور/css/js/خطوط) |
| `large` | + نطاقات فرعية | 4 | يحظر المسارات التقنية والأصول فقط (بما فيها الأرشيف/PDF) |
| `api` | هدف دقيق | 3 | يقصر على `/api` و`/v1` و`/v2`؛ ويحظر التوثيق والأصول |
| `custom` | + نطاقات فرعية | 3 | لا قيود افتراضية — نقطة انطلاق للتهيئة اليدوية |

بغض النظر عن الملف المختار، قائمة امتدادات الملفات الثنائية/الكبيرة (`.iso` و`.zip` و`.exe` و`.mp4` وغيرها) **دائمًا** مستبعدة من الزحف وfuzzing، حتى في `custom` — لا يُجلب الرابط إلى ملف من هذا النوع أبدًا عبر طلب HTTP حقيقي، لتفادي إبطاء الفحص لعدة دقائق بسبب مجلد تنزيلات.

### مستويات العدوانية

`doux` · `standard` · `agressif` · `violent` — لكل مستوى حدود أساسية خاصة به (المدة، الطلبات، الاختبارات، العمق، التزامن)، ويمكن للإعداد المسبق تجاوزها إن وُجد.

### الإعدادات المسبقة الجاهزة

| الإعداد | النطاق | العدوانية | أقصى مدة | أقصى طلبات | أقصى اختبارات | أقصى عمق | تأكيد معزز |
|---|---|---|---|---|---|---|---|
| `prod-safe` | strict | doux | 300 ثانية | 1,000 | 500 | 1 | لا |
| `staging-full` | standard | standard | 1,800 ثانية | 20,000 | 10,000 | 2 | لا |
| `lab-deep` | large | agressif | 3,600 ثانية | 100,000 | 50,000 | 4 | لا |
| `lab-extreme` | large | violent | 7,200 ثانية | 500,000 | 250,000 | 5 | **نعم** |
| `api-hardened` | api | agressif | 1,800 ثانية | 50,000 | 25,000 | 3 | لا |

يُحظر الفحص حتى يتم تأكيده. **التأكيد المعزز** (إدخال العبارة الدقيقة `OUI-J-AI-L-AUTORISATION`) مطلوب عند وجود أي من العوامل الثلاثة: عدوانية `violent`، أو الإعداد المسبق `lab-extreme`، أو تعطيل التحقق من TLS (`--insecure-tls`) — وفي تركيبة غير معتادة لا تتضمن أحد هذه العوامل الثلاثة، يكفي تأكيد بسيط بنعم/لا.

## 5. اختبارات الأمان المنفذة

خط أنابيب آلي، على كل URL مكتشف داخل النطاق (وكل نموذج `GET` موجود فيه):

| الاختبار | التشغيل | ما يتم فحصه |
|---|---|---|
| Fuzzing عام للمعاملات | كل معامل query string | سلوك الهدف تجاه القيم الحدية/التالفة |
| Fuzzing للرؤوس | مرة واحدة لكل URL، 4 رؤوس ثابتة (`User-Agent`، `Referer`، `X-Forwarded-For`، `Accept-Language`) | سلوك الهدف تجاه القيم الحدية/التالفة في الرأس |
| Fuzzing للنموذج (`GET` فقط) | كل حقل نموذج `GET` مكتشف في النطاق | سلوك الهدف تجاه القيم الحدية/التالفة في حقل النموذج |
| XSS عاكس | كل معامل query string | انعكاس payload غير مُرشّح في الاستجابة (غير مدمّر) |
| حقن عام | كل معامل query string | كشف خطأ خادم في الاستجابة لـ payload حقن (دون بصمة SQL/NoSQL محددة) |
| رؤوس الأمان | مرة واحدة لكل URL | رؤوس أمان مفقودة أو مهيأة بشكل خاطئ في الاستجابة |

الاختبارات الثلاثة الأولى (fuzzing عام للمعاملات/الرؤوس/النموذج) هي محرك طفرات **دون كشف** — لا تنتج `Finding` مباشرة أبدًا؛ تُحتسب فقط أخطاء الخادم (5xx) التي تُصادف في `Test` المقابل. فقط التواقيع (XSS، الحقن، رؤوس الأمان) تُنتج findings.

## 6. النتيجة والخطورة

يُقيّم كل شذوذ مكتشف على ثلاثة محاور (`impact` و`exploitability` و`scope`، من 1 إلى 5 لكل منها) حسب طبيعة الملاحظة — والتعيين **متحفظ** عمدًا (الحد الأدنى من المدى، دون تأكيد بشري في هذه المرحلة الآلية):

| النتيجة الخام (مجموع المحاور الثلاثة) | الخطورة |
|---|---|
| ≥ 13 | `critical` |
| ≥ 10 | `high` |
| ≥ 7 | `medium` |
| < 7 | `low` |

يظل التعديل اليدوي ممكنًا (`severity_override`) لكنه يتطلب دائمًا مبررًا صريحًا. تُزال النتائج المتكافئة (نفس النوع ونقطة النهاية والمعامل) من التكرار مع الاحتفاظ بأفضل دليل متاح (مستوى الثقة `omega_lib.core.confidence.ConfidenceLevel`، ثم النتيجة الخام عند التعادل).

## 7. المصادقة

ملف YAML مخصص (`--auth-config`)، دون بيانات اعتماد صريحة في سطر الأوامر:

| الوضع | التأثير |
|---|---|
| `none` | لا مصادقة (افتراضي) |
| `cookie` | توفير كوكي الجلسة مباشرة |
| `bearer_token` | رمز `Authorization: Bearer ...` |
| `login_form` | مصادقة عبر نموذج (رابط تسجيل الدخول، حقول المستخدم/كلمة المرور) |

## 8. البنية

منظم Omega-Fuzz وفق **Clean Architecture** (domain / application / infrastructure / interfaces / ports / core / app / plugins)، متوافق مع قالب حزمة `omega-` (انظر `omega-check`/`omega-deep`/`omega-fold`) ويُتحقق منه بواسطة `import-linter` عند كل تعديل. التفاصيل الكاملة في **`docs/ARCHITECTURE.md`**.

نظرة عامة موجزة جدًا:

```text
src/omega_fuzz/
├── domain/          منطق الأعمال النقي (الأهداف/النطاق، الطلبات، الاختبارات، النتائج، الملفات، التقارير...)
├── application/     حالات الاستخدام (commands/queries) والمنسقون (الاكتشاف، الفحص، التقرير، الحدود)
├── ports/           العقود التي تتوقعها التطبيقات (http_client، repositories، exporters...)
├── infrastructure/  التنفيذات الملموسة (httpx، BeautifulSoup، SQLite، مُصدّرات Jinja2 — Textual ليس هنا)
├── interfaces/      tui/ (Textual) وcli/ (قابل للبرمجة)، بتكافؤ وظيفي صارم
├── plugins/         أدوات fuzzing والتواقيع (دوال نقية، دون وصول مباشر للشبكة)
├── app/             التجميع (Container، نقطة التركيب، دورة الحياة)
└── core/            المفردات المشتركة، الأخطاء، الثوابت
```

قواعد التصميم:

- `plugins/fuzzers/` و`plugins/signatures/`: دوال نقية تبني خطط اختبار (`Test` + `ScanRequest`) ولا تلمس `HttpClient` أبدًا.
- `infrastructure/network/`: ينفذ عمليات الشبكة (`httpx`، بث محدود الذاكرة) ولا يصدر أحكامًا.
- `infrastructure/analyzers/`: يقرأ استجابة وردت بالفعل، وينتج `Observation` مهيكلة، ولا يعيد حساب النتيجة أبدًا.
- `interfaces/`: تعرض فقط، ولا تحتوي منطق أعمال.

## 9. التصدير

تُكتب تقارير Markdown وHTML باللغة المختارة في الإعدادات («لغة التصدير»، افتراضيًا لغة الواجهة)؛ ويبقى JSON بيانات غير مترجمة. تُنشأ التقارير افتراضيًا في `var/exports/` (مسار وقت التشغيل مرتبط بمجلد المشروع، و`$OMEGA_FUZZ_VAR_DIR` لتجاوزه، ويمكن تجاوزه أيضًا من شاشة الإعدادات)، أو في المسار المحدد (`--output-dir`). اسم ملف مسطح دون مجلد فرعي: `<preset>-<طابع زمني>.<امتداد>` (مثل `prod-safe-2026-09-01_14-30-22.html`).

### JSON، مصدر الحقيقة

بنية التقرير الكاملة (التهيئة الفعلية، الإحصاءات، الاختبارات، النتائج)، قابلة للتسلسل إلى JSON بشكل صارم.

### Markdown، تقرير مختصر للإنسان

قابل للقراءة خارج الطرفية، دون أكواد ANSI.

### HTML، تقرير ويب مستقل

5 ثيمات للاختيار (`--export-theme` في CLI، ومحدد في TUI): `omega-base` و`omega-burn` و`omega-neon` و`light-basic` و`light-alt`.

## 10. السجل والأهداف المفضلة

يُحفظ كل فحص (SQLite، `var/db/omega-fuzz.db`) مع نتائجه، ويمكن عرضه من شاشة السجل في TUI. يُحفظ `Scan` و`Finding` فقط — لا التهيئة الفعلية الكاملة ولا الطلبات التفصيلية — لذلك لا توجد إعادة تشغيل أو مقارنة أو تصدير جديد من هذه الشاشة (الشاشة تشرح ذلك بدلًا من إنشاء بيانات).

تحفظ شاشة **الأهداف** قائمة المفضلة (عناوين URL مُطبّعة، `var/targets.json`)، قابلة لإعادة الاستخدام لملء حقل الهدف في فحص جديد مباشرةً.

## 11. لقطات الشاشة

أمر **لقطة شاشة** من لوحة الأوامر (`Ctrl+P`): يحفظ SVG للشاشة الحالية في TUI افتراضيًا في `var/screenshots/`، ويمكن تغييره من شاشة الإعدادات (مثل مجلد التصدير). تتوفر أيضًا وظيفة تنظيف مخصصة في الإعدادات.

## 12. توافق الطرفيات

يكتشف TUI (Textual) قدرات الطرفية تلقائيًا (المحاكي، الحجم) ويكيّف ورقة الأنماط الهيكلية وفقًا لذلك (`complete`/`standard`/`reduced`/`mono`)، دون علم يدوي. يبقى CLI دائمًا نصًا عاديًا، مستقلًا عن الطرفية. هذه السياسة مشتركة في كامل حزمة `omega-` (`omega-lib`، `terminal/policies.py`).

### الملف حسب المحاكي المكتشف

| المحاكي | الملف الابتدائي |
|---|---|
| Ghostty، Alacritty، WezTerm، Kitty | `complete` |
| Konsole، GNOME Terminal، Terminator، Xfce4 Terminal | `standard` |
| xterm، urxvt، SSH حديث | `reduced` |
| TTY لينكس، SSH قديم | `mono` |
| محاكي غير معروف | `reduced` (بديل افتراضي) |

### الملف حسب حجم الطرفية

| الحد الأدنى للحجم (أعمدة × أسطر) | سقف الملف |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| أقل | `mono` |

الملف النهائي هو **الأكثر تقييدًا من بين الاثنين** (المحاكي والحجم) — ويمكن تحديثه مباشرةً بمفتاح `r`.

## 13. الاختبارات

```bash
source .venv/bin/activate
lint-imports        # يتحقق من قاعدة الاعتماديات (6 عقود)
pytest -q           # 344 اختبارًا
ruff check src tests
mypy -p omega_fuzz
```

البنية: `tests/unit/` (النطاق والتطبيق، دون I/O حقيقي)، `tests/integration/` (نظام ملفات حقيقي عبر `tmp_path`، خادم HTTP وهمي `pytest-httpserver`، قاعدة SQLite حقيقية، CLI من البداية إلى النهاية)، `tests/tui/` (تنقل عبر `Pilot`، فحوص هيكلية — دون ادعاء تحقق بصري آلي).

## 14. خارج النطاق

- Fuzzing لهياكل JSON (الكود موجود لكنه غير موصول — لا اكتشاف لمخطط API)
- Fuzzing لنماذج `POST`/`PUT`/`DELETE` (مستبعد عن قصد، خطر الكتابة)
- اختبارات منطق الأعمال (IDOR، التفويض، سير العمل) خارج الاستدعاء اليدوي
- فحص متعدد الأهداف متزامن
- إعادة التشغيل أو المقارنة أو التصدير من السجل
- عرض JavaScript من جهة العميل
- لوحة تحكم ويب

---

> Omega-Fuzz — اكتشف النطاق، واختبره بضوابط صريحة، ولا تخمّن أبدًا ما لم يتم تأكيده.
