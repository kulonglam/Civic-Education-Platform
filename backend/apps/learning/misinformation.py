"""Misinformation-awareness track: lesson keys, extra articles, and quiz title.

The curriculum article “Pause before you share” remains the how-to-verify lesson.
Extra published articles and a practice quiz are resolved at runtime by title.
"""

FACT_OR_FICTION_TITLE = 'Fact or Fiction?'

VERIFY_LESSON_TITLE = 'Pause before you share: media literacy'

LESSON_KEYS = (
    'verify',
    'examples',
    'social',
    'credibility',
)

# Extra published articles in category media-misinformation (not the core curriculum pack).
AWARENESS_ARTICLES = [
    {
        'key': 'examples',
        'title': 'Teaching examples: how false stories are built',
        'title_ar': 'أمثلة تعليمية: كيف تُبنى القصص الكاذبة',
        'tags': ['misinformation', 'examples', 'media'],
        'content': """## Teaching examples only

The cases below are **invented for learning**. They are not current events and they are not verified news. Each one shows a pattern you can spot in real life. Do not share them as if they were happening now.

## Example 1 — The clinic rumour

A WhatsApp voice note says: “All clinics in the county close tomorrow.” There is no name, no date on an official letter, and the speaker asks you to forward it “before it is too late.”

**What is going on:** Speed and fear replace a named source. A training day or a shortened hour can be twisted into a total shutdown.

**What to do:** Check the county health office or a trusted radio bulletin. If you cannot name the source, treat it as unverified. Reply with the official notice if you find one — do not forward the rumour.

## Example 2 — The “official” image

A flyer with a government-looking logo announces a new fee “from Monday.” The logo is blurry. There is no gazette number, no office address, and the PDF came from an unknown number.

**What is going on:** Official design is copied to borrow trust. Real notices name the issuing office and can be matched on a notice board or website.

**What to do:** Ask which ministry or county issued it. If nobody can say, it is not a verified fact.

## Example 3 — The old photo as “today”

A photo of a crowded street is captioned “happening in Juba right now.” A reverse look (or a trusted journalist) shows the same picture from another year or another country.

**What is going on:** True images can still be false *news* when the time or place is wrong.

**What to do:** Ask when and where the picture was first published. If that cannot be answered, do not treat the caption as fact.

## Remember

False stories often mix a little truth (a real clinic, a real logo style, a real photo) with a false claim. Your job is not to guess — it is to pause, name the source, and check a second independent place.
""",
        'content_ar': """## أمثلة تعليمية فقط

الحالات أدناه **مُخترعة للتعلّم**. وهي ليست أحداثاً جارية وليست أخباراً موثّقة. كل واحدة تُظهر نمطاً يمكنك رصده في الحياة. لا تشاركها وكأنها تحدث الآن.

## مثال 1 — شائعة العيادة

رسالة واتساب صوتية تقول: «كل عيادات المقاطعة تُغلق غداً». لا اسم، ولا تاريخ على خطاب رسمي، والمتحدث يطلب إعادة الإرسال «قبل فوات الأوان».

**ما الذي يحدث:** السرعة والخوف يحلّان محل مصدر مسمّى. قد يُحوَّل يوم تدريب أو تقليص ساعات إلى إغلاق كامل.

**ماذا تفعل:** تحقق من مكتب الصحة في المقاطعة أو من نشرة إذاعية موثوقة. إن لم تستطع تسمية المصدر، عامل الرسالة كمعلومات غير موثّقة. إن وجدت الإعلان الرسمي، أرسله في المجموعة — ولا تُعد الشائعة.

## مثال 2 — صورة «رسمية»

منشور بشعار يبدو حكومياً يعلن رسماً جديداً «اعتباراً من الاثنين». الشعار ضبابي. لا رقم جريدة، ولا عنوان مكتب، وملف PDF جاء من رقم مجهول.

**ما الذي يحدث:** يُنسخ التصميم الرسمي لاستعارة الثقة. الإعلانات الحقيقية تسمّي الجهة المصدرة ويمكن مطابقتها على لوحة إعلانات أو موقع.

**ماذا تفعل:** اسأل أي وزارة أو مقاطعة أصدرته. إن لم يجب أحد، فليست حقيقة موثّقة.

## مثال 3 — صورة قديمة على أنها «اليوم»

صورة لشارع مزدحم تحمل التعليق «يحدث في جوبا الآن». يتبيّن أن الصورة من سنة أخرى أو بلد آخر.

**ما الذي يحدث:** الصور الحقيقية قد تكون أخباراً كاذبة إذا خُطئ الزمان أو المكان.

**ماذا تفعل:** اسأل متى وأين نُشرت الصورة أولاً. إن تعذّر الجواب، لا تعامل التعليق كحقيقة.

## تذكّر

القصص الكاذبة غالباً تمزج قدراً من الحقيقة (عيادة حقيقية، شكل شعار، صورة حقيقية) بادعاء كاذب. مهمتك ليست التخمين — بل التوقف وتسمية المصدر والتحقق من مكان مستقل ثانٍ.
""",
    },
    {
        'key': 'social',
        'title': 'Social media: why rumours travel faster than facts',
        'title_ar': 'وسائل التواصل: لماذا تسبق الشائعات الحقائق',
        'tags': ['social-media', 'whatsapp', 'misinformation'],
        'content': """## Why this matters

On WhatsApp, Facebook, and similar apps, a message can reach a whole payam before a county official has seen it. **Forwarding is publishing.** You are responsible for what you amplify, even if you only meant to “warn the family.”

## Habits that spread harm

- Voice notes with no name, asking you to share “immediately”
- Screenshots of chats you cannot verify
- Closed groups where nobody is allowed to question the claim
- Counting likes or forwards as proof

## Habits that protect people

- Pause. The urgent tone is often the trick.
- Ask: who published this first, and can I name them?
- Check a second source that is independent of the chat (radio, notice board, this platform’s labelled civic news).
- If you already forwarded something false, send a correction in the same group. That is civic courage, not shame.

## Freedom of expression

The constitution protects honest speech and criticism. It does not require you to circulate panic. Refusing to forward an unnamed claim is not censorship — it is care for your neighbours.
""",
        'content_ar': """## لماذا يهم هذا الموضوع

على واتساب وفيسبوك والتطبيقات المشابهة، قد تصل رسالة إلى البيام كله قبل أن يراها مسؤول المقاطعة. **إعادة الإرسال نشر.** أنت مسؤول عما تضخّمه، حتى لو قصدت فقط «تحذير العائلة».

## عادات تنشر الأذى

- رسائل صوتية بلا اسم تطلب المشاركة «فوراً»
- لقطات محادثات لا يمكنك التحقق منها
- مجموعات مغلقة لا يُسمح فيها بالسؤال عن الادعاء
- اعتبار الإعجابات أو مرات الإعادة دليلاً

## عادات تحمي الناس

- توقّف. نبرة الاستعجال غالباً هي الحيلة.
- اسأل: من نشر هذا أولاً، وهل أستطيع تسميته؟
- تحقق من مصدر ثانٍ مستقل عن الدردشة (راديو، لوحة إعلانات، الأخبار المدنية المصنّفة في هذه المنصة).
- إذا سبق أن أعدت شيئاً كاذباً، أرسل تصحيحاً في المجموعة نفسها. تلك شجاعة مدنية لا عار.

## حرية التعبير

يحمي الدستور الكلام الصادق والنقد. وهو لا يُلزمك بنشر الذعر. رفض إعادة ادعاء غير مسمّى ليس رقابة — بل رعاية لجيرانك.
""",
    },
    {
        'key': 'credibility',
        'title': 'How to judge whether a source is credible',
        'title_ar': 'كيف تحكم إن كان المصدر موثوقاً',
        'tags': ['sources', 'credibility', 'journalism'],
        'content': """## A credible source can be named

Ask four questions:

1. **Who?** A ministry, county office, electoral commission, court, clinic, or a journalist you can name is stronger than “someone inside.”
2. **Where?** A gazette, official letterhead, notice board, or known radio station can be checked. A stray PDF from an unknown number cannot.
3. **When?** Dates matter. An old statement is not “breaking news.”
4. **Can I confirm it elsewhere?** One independent confirmation (a second office, a trusted station, a labelled verified notice on this platform) is worth more than twenty forwards.

## Stronger vs weaker

| Stronger | Weaker |
| --- | --- |
| Named office + document you can match | “Insider” with no name |
| Independent radio or newspaper | Page created last week with a borrowed logo |
| Transitional Constitution or a published law | “New law” with no bill number |
| Civic news labelled **verified fact** with a source | Civic news labelled **unverified** or a viral chat |

## Independent journalism

Reporters who name sources, correct errors, and keep a public record help citizens. Harassment of journalists makes rumours louder. Protecting honest reporting is part of civic duty.

This lesson is an **educational explanation**. It is not a list of banned outlets and it is not legal advice.
""",
        'content_ar': """## المصدر الموثوق يمكن تسميته

اسأل أربعة أسئلة:

1. **من؟** وزارة أو مكتب مقاطعة أو مفوضية انتخابية أو محكمة أو عيادة أو صحفي تستطيع تسميته أقوى من «شخص من الداخل».
2. **أين؟** جريدة رسمية أو ورقة رسمية أو لوحة إعلانات أو إذاعة معروفة يمكن فحصها. ملف PDF ضال من رقم مجهول لا يمكن.
3. **متى؟** التواريخ مهمة. بيان قديم ليس «خبراً عاجلاً».
4. **هل أؤكد من مكان آخر؟** تأكيد مستقل واحد (مكتب ثانٍ، محطة موثوقة، إشعار موثّق مصنّف في هذه المنصة) أغلى من عشرين إعادة إرسال.

## أقوى مقابل أضعف

| أقوى | أضعف |
| --- | --- |
| مكتب مسمّى + وثيقة يمكن مطابقتها | «مطلع» بلا اسم |
| راديو أو صحيفة مستقلة | صفحة أُنشئت الأسبوع الماضي بشعار مستعار |
| الدستور الانتقالي أو قانون منشور | «قانون جديد» بلا رقم مشروع |
| أخبار مدنية مصنّفة **حقيقة موثّقة** مع مصدر | أخبار مصنّفة **غير موثّقة** أو دردشة متداولة |

## الصحافة المستقلة

الصحفيون الذين يسمّون المصادر ويصحّحون الأخطاء ويحفظون سجلاً عاماً يساعدون المواطنين. مضايقة الصحفيين تجعل الشائعات أعلى صوتاً. حماية التغطية الصادقة جزء من الواجب المدني.

هذا الدرس **شرح تعليمي**. وهو ليس قائمة وسائل محظورة وليس استشارة قانونية.
""",
    },
]
