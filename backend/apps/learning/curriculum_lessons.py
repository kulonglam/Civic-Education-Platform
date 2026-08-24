"""Bilingual lesson packs for the 15 civic curriculum modules.

Each pack is one published article (text + real-life example) plus metadata
used by ``seed_data`` to attach an infographic image, audio, video, and PDF.
"""

from __future__ import annotations

# Shared placeholder media (public examples). Each module gets uniquely titled
# MediaAsset rows pointing at these URLs so the player and progress APIs work.
CURRICULUM_AUDIO_URL = 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3'
CURRICULUM_VIDEO_URL = 'https://www.youtube.com/watch?v=0PAy1zBtT9w'

LESSONS: tuple[dict, ...] = (
    {
        'slug': 'constitution',
        'title': 'Understanding the Transitional Constitution',
        'title_ar': 'فهم الدستور الانتقالي',
        'tags': ['constitution', 'rights'],
        'is_controlled_document': True,
        'document_label': 'Transitional Constitution of the Republic of South Sudan, 2011',
        'attachment_version': '2011',
        'load_constitution_text': True,
        'keep_official_pdf': True,
        'audio_title': 'Civic basics: why constitutions matter (audio)',
        'audio_title_ar': 'أساسيات المواطنة: لماذا تهم الدساتير (صوت)',
        'video_title': 'Video lesson: Constitution and rights',
        'video_title_ar': 'درس فيديو: الدستور والحقوق',
        'facts': [
            'The Transitional Constitution is the supreme law during the transition.',
            'It organizes the legislature, executive, and judiciary.',
            'The Bill of Rights protects dignity, equality, and basic freedoms.',
            'Public officials must act within the constitution, not above it.',
        ],
        'content': """## Why this matters

A constitution is the highest law of the land. In South Sudan, the **Transitional Constitution (2011)** sets out how government is formed, which rights every person holds, and how power is limited until a permanent constitution is adopted.

## What the constitution does

- Names the branches of government and their core duties.
- Lists fundamental rights such as equality before the law and freedom of expression.
- Explains how laws are made and how institutions check one another.
- Provides a path toward a permanent constitution through an inclusive process.

Download the PDF attachment for the official text. The AI tutor uses this document when you ask about rights and institutions.

## Real-life example

A county official cannot invent a new “local tax” that contradicts the constitution or national law. Citizens can ask: *Which law allows this fee?* If the answer is unclear, the fee may be unlawful. Knowing the constitution gives you language to question power calmly and in public.

## What you can do

1. Read the Bill of Rights section in the attached PDF.
2. Ask the AI tutor about a specific article (for example Article 14 on equality).
3. Share one right you learned with family or a community group.
""",
        'content_ar': """## لماذا يهم هذا الموضوع

الدستور هو أعلى قانون في البلاد. في جنوب السودان يحدد **الدستور الانتقالي (2011)** كيف تُشكَّل الحكومة، وما الحقوق التي يتمتع بها كل شخص، وكيف تُقيَّد السلطة إلى أن يُعتمد دستور دائم.

## ماذا يفعل الدستور

- يسمّي سلطات الدولة وواجباتها الأساسية.
- يدرج حقوقاً أساسية مثل المساواة أمام القانون وحرية التعبير.
- يشرح كيف تُصنع القوانين وكيف تراقب المؤسسات بعضها بعضاً.
- يضع مساراً نحو دستور دائم عبر عملية شاملة.

حمّل مرفق PDF للاطلاع على النص الرسمي. يستخدم المدرّس الذكي هذه الوثيقة عند سؤالك عن الحقوق والمؤسسات.

## مثال من الواقع

لا يستطيع مسؤول في المقاطعة اختراع «ضريبة محلية» تتعارض مع الدستور أو القانون الوطني. يمكن للمواطنين أن يسألوا: *أي قانون يجيز هذا الرسم؟* إذا كان الجواب غير واضح فقد يكون الرسم غير قانوني. معرفة الدستور تمنحك لغة لمساءلة السلطة بهدوء وأمام الناس.

## ماذا يمكنك أن تفعل

1. اقرأ قسم وثيقة الحقوق في ملف PDF المرفق.
2. اسأل المدرّس الذكي عن مادة محددة (مثل المادة 14 عن المساواة).
3. شارك حقاً واحداً تعلمته مع الأسرة أو مجموعة مجتمعية.
""",
    },
    {
        'slug': 'human-rights',
        'title': 'Human rights belong to every person',
        'title_ar': 'حقوق الإنسان حق لكل شخص',
        'tags': ['rights', 'dignity', 'equality'],
        'facts': [
            'Human rights belong to every person, not only to citizens with connections.',
            'Equality forbids discrimination based on sex, ethnicity, religion, or opinion.',
            'Nobody may be tortured or treated in a cruel, inhuman way.',
            'Rights include food, education, and a fair hearing — not only political speech.',
        ],
        'content': """## Why this matters

Human rights are protections that every person has because they are human — women and men, children, displaced people, and persons with disabilities. South Sudan’s Bill of Rights and international standards such as the Universal Declaration of Human Rights point in the same direction: **dignity and equal protection**.

## Core ideas

- **Dignity:** No official may treat a person as if they have no worth.
- **Equality:** The law should not favour one ethnicity, faith, or gender over another.
- **Freedom from abuse:** Torture, slavery, and arbitrary arrest violate rights.
- **Economic and social rights:** Health, education, and an adequate standard of living matter as much as the right to speak.

Rights are not a gift from a leader. Government exists to **respect, protect, and fulfil** them.

## Real-life example

A girl is told she cannot enrol in the local primary school “because there are not enough desks for girls.” That is not only a school-management problem — it can be discrimination. Parents, teachers, and the county education office can insist that both boys and girls receive the same chance to learn.

## What you can do

1. Learn which rights are listed in the constitution’s Bill of Rights.
2. If someone is harmed, document facts (date, place, names) and use official complaint channels when it is safe.
3. Support neighbours who are displaced or excluded rather than spreading rumours about them.
""",
        'content_ar': """## لماذا يهم هذا الموضوع

حقوق الإنسان حماية لكل شخص لأنه إنسان — النساء والرجال والأطفال والنازحون وذوو الإعاقة. تشير وثيقة الحقوق في جنوب السودان والمعايير الدولية مثل الإعلان العالمي لحقوق الإنسان إلى الاتجاه نفسه: **الكرامة والحماية المتساوية**.

## أفكار أساسية

- **الكرامة:** لا يجوز لمسؤول أن يعامل شخصاً وكأنه بلا قيمة.
- **المساواة:** ينبغي ألا يفضّل القانون عرقاً أو ديناً أو جنساً على آخر.
- **الحماية من الإساءة:** التعذيب والاسترقاق والاعتقال التعسفي انتهاك للحقوق.
- **الحقوق الاقتصادية والاجتماعية:** الصحة والتعليم ومستوى معيشي لائق لا تقل أهمية عن حق التعبير.

الحقوق ليست هبة من قائد. وُجدت الحكومة لـ**احترامها وحمايتها وإعمالها**.

## مثال من الواقع

تُمنع فتاة من الالتحاق بالمدرسة الأساسية «لأنه لا توجد مقاعد كافية للبنات». هذه ليست مشكلة إدارة مدرسية فحسب — بل قد تكون تمييزاً. يمكن للأهالي والمعلمين ومكتب التعليم في المقاطعة أن يصرّوا على أن يحصل الفتيان والفتيات على الفرصة نفسها للتعلم.

## ماذا يمكنك أن تفعل

1. تعرّف على الحقوق المدرجة في وثيقة الحقوق بالدستور.
2. إذا تضرر أحد، وثّق الوقائع (التاريخ والمكان والأسماء) واستخدم قنوات الشكوى الرسمية عندما يكون ذلك آمناً.
3. ادعم الجيران النازحين أو المستبعدين بدلاً من نشر الشائعات عنهم.
""",
    },
    {
        'slug': 'citizen-responsibilities',
        'title': 'Rights come with civic duties',
        'title_ar': 'الحقوق ترافقها واجبات مدنية',
        'tags': ['duties', 'citizenship', 'law'],
        'facts': [
            'Rights and duties travel together: freedom depends on respecting others.',
            'Obeying lawful rules protects the weak from the powerful.',
            'Paying lawful taxes funds schools, clinics, and roads.',
            'Peaceful participation is a duty, not only a right.',
        ],
        'content': """## Why this matters

A republic cannot run on rights alone. Citizens also have **responsibilities**: to obey lawful rules, to respect the rights of others, to pay taxes that the law requires, and to take part in public life without violence.

## Duties in daily life

- Follow the law even when nobody is watching.
- Tell the truth in official processes (registration, court, census).
- Care for public property — schools, boreholes, and roads belong to everyone.
- Reject rumours that can incite hate.
- Vote when elections are held, and accept peaceful outcomes.

Duties are not an excuse for officials to abuse people. Unlawful orders are not “your duty to obey.”

## Real-life example

After a storm damages the market, some traders dump waste in the drainage ditch “because the county should clean it.” The county does have a duty to maintain drains — and traders have a duty not to block them. A traders’ association that organises a clean-up *and* petitions the county for regular collection is practising both rights and responsibilities.

## What you can do

1. Name one public rule you will follow this month (for example, not bribing a clerk).
2. Join a lawful community effort: school committee, water user group, or neighbourhood watch that respects rights.
3. Teach children that freedom of speech does not include incitement to violence.
""",
        'content_ar': """## لماذا يهم هذا الموضوع

لا تقوم الجمهورية على الحقوق وحدها. على المواطنين أيضاً **واجبات**: احترام القواعد القانونية، واحترام حقوق الآخرين، ودفع الضرائب التي يفرضها القانون، والمشاركة في الحياة العامة دون عنف.

## واجبات في الحياة اليومية

- التزم بالقانون حتى عندما لا يراك أحد.
- اصدق في الإجراءات الرسمية (التسجيل والمحكمة والتعداد).
- اعتنِ بالممتلكات العامة — المدارس والآبار والطرق ملك للجميع.
- ارفض الشائعات التي قد تحرّض على الكراهية.
- صوّت عند إجراء الانتخابات، واقبل النتائج السلمية.

الواجبات ليست عذراً للمسؤولين لإساءة معاملة الناس. الأوامر غير القانونية ليست «واجبك أن تطيعها».

## مثال من الواقع

بعد عاصفة تضرّر السوق، يلقي بعض التجار النفايات في قناة الصرف «لأن المقاطعة يجب أن تنظّف». على المقاطعة واجب صيانة المصارف — وعلى التجار واجب عدم سدّها. جمعية تجار تنظّم حملة تنظيف *وتقدّم عريضة* للمقاطعة من أجل جمع منتظم تمارس الحقوق والواجبات معاً.

## ماذا يمكنك أن تفعل

1. سمِّ قاعدة عامة ستلتزم بها هذا الشهر (مثلاً عدم رشوة موظف).
2. انضم إلى جهد مجتمعي مشروع: لجنة مدرسة أو مجموعة مستخدمي المياه أو حراسة حي تحترم الحقوق.
3. علّم الأطفال أن حرية التعبير لا تشمل التحريض على العنف.
""",
    },
    {
        'slug': 'government-structure',
        'title': 'How national and local government are organized',
        'title_ar': 'كيف تُنظَّم الحكومة الوطنية والمحلية',
        'tags': ['institutions', 'states', 'counties'],
        'facts': [
            'Power is divided among the legislature, executive, and judiciary.',
            'States and counties deliver many services citizens meet every day.',
            'Payams and bomas are the closest local units for many communities.',
            'Knowing who is responsible helps you take a complaint to the right office.',
        ],
        'content': """## Why this matters

If you do not know **who does what**, it is easy to blame the wrong office — or to give up. South Sudan’s government is organised in layers: national institutions, states, counties, and local units such as payams and bomas.

## The three branches

- **Legislature** makes and amends laws, and scrutinises spending.
- **Executive** (presidency, ministers, governors) implements policy and runs services.
- **Judiciary** interprets the law and settles disputes independently.

Local government is where most people meet the state: birth registration, primary schools, local security cooperation, and market regulation.

## Real-life example

A borehole breaks. The water user committee first checks the county rural water office — not the national ministry. If the county says the spare parts budget sits with the state ministry, the committee writes to *that* office and copies the county. Clear structure turns anger into a paper trail.

## What you can do

1. Learn the name of your county commissioner or equivalent local authority.
2. Ask which office handles education, water, and police in your area.
3. Keep copies of letters or complaint numbers when you seek a service.
""",
        'content_ar': """## لماذا يهم هذا الموضوع

إن لم تعرف **من يفعل ماذا** سهُل أن تلوم الجهة الخطأ — أو أن تيأس. تُنظَّم حكومة جنوب السودان على طبقات: مؤسسات وطنية، وولايات، ومقاطعات، ووحدات محلية مثل البيام والبومة.

## السلطات الثلاث

- **السلطة التشريعية** تضع القوانين وتعدّلها وتراقب الإنفاق.
- **السلطة التنفيذية** (الرئاسة والوزراء والولاة) تنفّذ السياسات وتدير الخدمات.
- **السلطة القضائية** تفسّر القانون وتفصل في النزاعات باستقلال.

الحكومة المحلية هي حيث يلتقي معظم الناس بالدولة: تسجيل المواليد والمدارس الأساسية والتعاون الأمني المحلي وتنظيم الأسواق.

## مثال من الواقع

تعطّلت بئر. تتحقق لجنة مستخدمي المياه أولاً من مكتب المياه الريفية في المقاطعة — لا من الوزارة الاتحادية. إذا قالت المقاطعة إن ميزانية قطع الغيار لدى وزارة الولاية، تكتب اللجنة إلى *تلك* الجهة وتُرسل نسخة إلى المقاطعة. الهيكل الواضح يحوّل الغضب إلى مسار موثّق.

## ماذا يمكنك أن تفعل

1. تعرّف على اسم مفوض مقاطعتك أو السلطة المحلية المماثلة.
2. اسأل أي مكتب يتولى التعليم والمياه والشرطة في منطقتك.
3. احتفظ بنسخ الرسائل أو أرقام الشكاوى عند طلب خدمة.
""",
    },
    {
        'slug': 'governance',
        'title': 'How Local Government Works',
        'title_ar': 'كيف تعمل الحكومة المحلية',
        'tags': ['governance', 'democracy', 'local'],
        'video_title': 'Participatory democracy explained (video)',
        'video_title_ar': 'شرح الديمقراطية التشاركية (فيديو)',
        'audio_title': 'Audio lesson: Democracy and governance',
        'audio_title_ar': 'درس صوتي: الديمقراطية والحكم',
        'facts': [
            'Democracy means public power with rules, not rule by one person alone.',
            'Good governance is transparent, accountable, and responsive.',
            'Local meetings are a practical place to practise democracy.',
            'Opposition and criticism are normal in a healthy public life.',
        ],
        'content': """## Why this matters

**Democracy** is a way of making binding decisions with the consent of the people and under the law. **Governance** is how those decisions are carried out: fairly, openly, and with room to complain.

States and counties deliver services such as education coordination, local security cooperation, and community development. Participating in local meetings is a practical form of civic engagement.

## Signs of healthy governance

- Budgets and contracts can be explained in public.
- Officials give reasons for decisions.
- Mistakes can be corrected without revenge.
- Women, youth, and minorities can speak without fear.

Democracy is more than a polling day. It is the habit of listening, recording decisions, and returning to the public with results.

## Real-life example

A payam meeting is called to decide where a new classroom block should go. Two villages compete. Instead of the chief announcing a winner in private, the meeting lists criteria (number of children, distance, flood risk), votes or reaches consensus, and writes the result on a chalkboard. That is local democracy — imperfect, but public.

## What you can do

1. Attend one advertised local meeting this quarter.
2. Ask for the decision in writing, even if it is a photo of the minutes.
3. Support leaders who explain *why*, not only *what*.
""",
        'content_ar': """## لماذا يهم هذا الموضوع

**الديمقراطية** طريقة لاتخاذ قرارات ملزمة بموافقة الناس وتحت القانون. **الحكم** هو كيفية تنفيذ تلك القرارات: بعدل وعلنية ومع مجال للتظلم.

تقدم الولايات والمقاطعات خدمات مثل تنسيق التعليم والتعاون الأمني المحلي والتنمية المجتمعية. المشاركة في الاجتماعات المحلية شكل عملي من المشاركة المدنية.

## علامات الحكم السليم

- يمكن شرح الموازنات والعقود أمام الناس.
- يقدّم المسؤولون أسباب قراراتهم.
- يمكن تصحيح الأخطاء دون انتقام.
- تستطيع النساء والشباب والأقليات الكلام دون خوف.

الديمقراطية أكثر من يوم اقتراع. هي عادة الاستماع وتوثيق القرارات والعودة إلى الجمهور بالنتائج.

## مثال من الواقع

يُدعى اجتماع بيام لتقرير موقع كتلة فصول جديدة. قريتان تتنافسان. بدلاً من أن يعلن الزعيم الفائز في السر، يسرد الاجتماع المعايير (عدد الأطفال والمسافة وخطر الفيضان)، ويصوّت أو يتوافق، ويكتب النتيجة على السبورة. هذه ديمقراطية محلية — غير كاملة، لكنها علنية.

## ماذا يمكنك أن تفعل

1. احضر اجتماعاً محلياً معلناً في هذا الربع.
2. اطلب القرار مكتوباً، حتى لو كان صورة للمحضر.
3. ادعم القادة الذين يشرحون *لماذا* لا *ماذا* فقط.
""",
    },
    {
        'slug': 'elections',
        'title': 'Your Role in Free and Fair Elections',
        'title_ar': 'دورك في انتخابات حرة ونزيهة',
        'tags': ['elections', 'voting'],
        'facts': [
            'A free election lets people choose without fear or bribery.',
            'A fair election counts every valid ballot equally.',
            'Register early and confirm your polling station.',
            'Report irregularities through official channels, not rumours.',
        ],
        'content': """## Why this matters

Elections depend on informed voters, transparent processes, and peaceful participation. Your vote is how public offices receive a mandate — and how they can lose it without violence.

## Before, during, and after polling

- **Register** when the electoral body opens the roll. Check your name.
- **Learn** what each level of election decides (national, state, local).
- **Refuse** vote-buying. A small gift is not worth a captured government.
- **Observe** calmly if you are an accredited observer or party agent.
- **Accept** lawful results; challenge them in court or through official petitions, not by attacking polling staff.

## Real-life example

A young voter finds her name missing at the polling station. Instead of leaving in anger, she asks the presiding officer for the complaint form, notes the time, and follows the official correction process. That record can restore her ballot — shouting cannot.

## What you can do

1. Confirm whether you are registered and where you should vote.
2. Agree with friends that you will not accept money for your vote.
3. Share only official announcements about results.
""",
        'content_ar': """## لماذا يهم هذا الموضوع

تعتمد الانتخابات على ناخبين واعين وعمليات شفافة ومشاركة سلمية. صوتك هو كيف تحصل المناصب العامة على تفويض — وكيف تفقده دون عنف.

## قبل يوم الاقتراع وأثناءه وبعده

- **سجّل** عندما تفتح الهيئة الانتخابية السجل. تحقق من اسمك.
- **تعلّم** ماذا يقرر كل مستوى انتخابي (وطني وولائي ومحلي).
- **ارفض** شراء الأصوات. هدية صغيرة لا تساوي حكومة مأسورة.
- **راقب** بهدوء إن كنت مراقباً معتمداً أو مندوب حزب.
- **اقبل** النتائج القانونية؛ وطعن فيها في المحكمة أو عبر العرائض الرسمية، لا بمهاجمة موظفي المراكز.

## مثال من الواقع

تكتشف ناخبة شابة أن اسمها غير موجود في المركز. بدلاً من المغادرة غاضبة، تطلب من رئيس المركز نموذج الشكوى، وتسجّل الوقت، وتتبع مسار التصحيح الرسمي. هذا السجل قد يعيد صوتها — أما الصراخ فلا يفعل.

## ماذا يمكنك أن تفعل

1. تأكد إن كنت مسجّلاً وأين يجب أن تصوّت.
2. اتفق مع الأصدقاء على رفض المال مقابل الصوت.
3. شارك فقط الإعلانات الرسمية عن النتائج.
""",
    },
    {
        'slug': 'rule-of-law',
        'title': 'Nobody is above the law',
        'title_ar': 'لا أحد فوق القانون',
        'tags': ['courts', 'justice', 'equality'],
        'facts': [
            'The rule of law means rules apply to leaders and citizens alike.',
            'Fair process (notice, hearing, appeal) is as important as the outcome.',
            'Independent courts protect people from arbitrary power.',
            'Impunity — no consequences for abuse — destroys public trust.',
        ],
        'content': """## Why this matters

The **rule of law** is the opposite of arbitrary power. It means laws are public, they apply equally, and disputes are decided by independent institutions — not by whoever is stronger today.

## What it looks like

- Police need legal grounds to arrest; they must bring a person before a court.
- Contracts and land claims are decided with evidence, not only connections.
- Public officials follow procurement rules when spending tax money.
- Customary courts can settle many community disputes, but they must still respect constitutional rights (including the rights of women and children).

Rule of law is slow compared with a shout. It is also the only way weaker people can win against stronger people without violence.

## Real-life example

A soldier demands free fuel from a station “for security.” The attendant who quietly records the unit, time, and amount — and reports through a lawful channel — is defending the rule of law. Paying extra “to keep peace” in secret trains everyone that the law is optional.

## What you can do

1. Ask for a receipt or written reason when an official demands money.
2. Support legal aid clinics and paralegals in your area if they exist.
3. Do not take revenge outside the law, even when you are right to be angry.
""",
        'content_ar': """## لماذا يهم هذا الموضوع

**سيادة القانون** نقيض السلطة التعسفية. تعني أن القوانين معلنة، وتسري بالتساوي، وأن النزاعات تُحسم بمؤسسات مستقلة — لا بمن هو الأقوى اليوم.

## كيف تبدو

- تحتاج الشرطة إلى سند قانوني للاعتقال؛ وعليها تقديم الشخص إلى محكمة.
- تُحسم العقود ومطالبات الأرض بالأدلة لا بالواسطة وحدها.
- يتبع المسؤولون قواعد الشراء عند إنفاق مال الضرائب.
- يمكن للمحاكم العرفية تسوية نزاعات مجتمعية كثيرة، لكن عليها احترام الحقوق الدستورية (بما فيها حقوق النساء والأطفال).

سيادة القانون أبطأ من الصراخ. وهي أيضاً الطريق الوحيد ليفوز الأضعف على الأقوى دون عنف.

## مثال من الواقع

يطالب جندي بوقود مجاني من محطة «من أجل الأمن». العامل الذي يسجّل بهدوء الوحدة والوقت والكمية — ويبلّغ عبر قناة قانونية — يدافع عن سيادة القانون. دفع زيادة «للحفاظ على السلام» في السر يدرّب الجميع على أن القانون اختياري.

## ماذا يمكنك أن تفعل

1. اطلب إيصالاً أو سبباً مكتوباً عندما يطلب مسؤول مالاً.
2. ادعم عيادات المساعدة القانونية والمساعدين القانونيين في منطقتك إن وُجدوا.
3. لا تنتقم خارج القانون، حتى عندما يحق لك أن تغضب.
""",
    },
    {
        'slug': 'peacebuilding',
        'title': 'Building peace in everyday community life',
        'title_ar': 'بناء السلام في حياة المجتمع اليومية',
        'tags': ['peace', 'reconciliation', 'dialogue'],
        'facts': [
            'Peace is more than the absence of shooting — it is rebuilt trust.',
            'Dialogue works when all sides can speak without humiliation.',
            'Rumours and revenge cycles restart conflict.',
            'Youth and women are not spectators; they are peace actors.',
        ],
        'content': """## Why this matters

Peacebuilding is the long work after — and before — violence: reconciliation, sharing resources fairly, and refusing to dehumanise neighbours. South Sudan’s communities have deep traditions of dialogue; civic education adds **rights and public rules** so peace is not only a deal among strongmen.

## Practices that help

- Separate the person from the problem in a dispute.
- Include women, youth, and displaced people in talks that affect them.
- Agree on small, checkable steps (reopen a market, return cattle, reopen a school).
- Honour agreements in public so spoilers are visible.

Peace that silences victims is not peace. Justice and dialogue must travel together.

## Real-life example

Two cattle camps clash after a theft. Elders from both sides meet with women leaders and a county official. They agree: return the animals that can be identified, compensate the rest through a schedule, and ban night raids. A youth group monitors rumours on the radio. That mix of custom, local government, and civic voice is peacebuilding.

## What you can do

1. Refuse to share unverified “attack” messages.
2. Support inter-communal sports, markets, and school events.
3. Ask that any local peace deal protect women and children explicitly.
""",
        'content_ar': """## لماذا يهم هذا الموضوع

بناء السلام عمل طويل بعد العنف — وقبله: المصالحة، وتقاسم الموارد بعدل، ورفض تجريد الجيران من إنسانيتهم. لدى مجتمعات جنوب السودان تقاليد عميقة للحوار؛ ويضيف التعليم المدني **الحقوق والقواعد العامة** حتى لا يكون السلام مجرد صفقة بين الأقوياء.

## ممارسات تساعد

- افصل الشخص عن المشكلة في النزاع.
- أشرك النساء والشباب والنازحين في المحادثات التي تمسّهم.
- اتفقوا على خطوات صغيرة قابلة للتحقق (إعادة فتح سوق، إعادة الماشية، إعادة فتح مدرسة).
- أكرموا الاتفاقات علناً حتى يظهر المخربون.

السلام الذي يُسكت الضحايا ليس سلاماً. يجب أن تسير العدالة والحوار معاً.

## مثال من الواقع

يتصادم معسكران للماشية بعد سرقة. يلتقي كبار الطرفين مع قيادات نسائية ومسؤول مقاطعة. يتفقون: إعادة الحيوانات التي يمكن التعرف عليها، وتعويض الباقي وفق جدول، ومنع الغارات الليلية. تراقب مجموعة شباب الشائعات في الراديو. هذا المزيج من العرف والحكم المحلي والصوت المدني هو بناء السلام.

## ماذا يمكنك أن تفعل

1. ارفض مشاركة رسائل «هجوم» غير محققة.
2. ادعم الرياضة والأسواق والفعاليات المدرسية بين المجتمعات.
3. اطلب أن يحمي أي اتفاق سلام محلي النساء والأطفال صراحة.
""",
    },
    {
        'slug': 'gender-equality',
        'title': 'Equal voice for women, girls, and excluded groups',
        'title_ar': 'صوت متساوٍ للنساء والفتيات والفئات المستبعدة',
        'tags': ['gender', 'inclusion', 'women'],
        'facts': [
            'Equality means equal rights and equal chances, not identical lives.',
            'Inclusion brings women, youth, persons with disabilities, and minorities into decisions.',
            'Gender-based violence is a civic and legal issue, not a private shame only.',
            'Quotas and training help, but everyday respect matters more.',
        ],
        'content': """## Why this matters

A democracy that silences half the population is incomplete. **Gender equality and inclusion** mean women, girls, persons with disabilities, and minorities can learn, own property, speak in meetings, and live free from violence.

## What equality looks like

- Girls stay in school through secondary level.
- Women can inherit and hold land according to the constitution and reform of discriminatory custom.
- Meeting chairs invite women to speak early, not only at the end.
- Services (clinics, police desks) treat survivors with confidentiality and dignity.

Equality is not “foreign culture.” It is a constitutional promise and a development strategy: communities that include women recover faster from crisis.

## Real-life example

A water committee of ten men decides borehole hours that clash with the time women fetch water. After women demand two seats and a morning slot, waiting times drop and fights at the pump decrease. Inclusion improved the *technical* outcome, not only fairness.

## What you can do

1. Support girls’ school attendance in your household and neighbourhood.
2. Challenge jokes that normalise beating or child marriage.
3. Insist that local committees include women and youth as voting members.
""",
        'content_ar': """## لماذا يهم هذا الموضوع

الديمقراطية التي تُسكت نصف السكان ناقصة. **المساواة بين الجنسين والشمول** تعني أن النساء والفتيات وذوي الإعاقة والأقليات يستطيعون التعلم وامتلاك الأرض والكلام في الاجتماعات والعيش بلا عنف.

## كيف تبدو المساواة

- تبقى الفتيات في المدرسة حتى المرحلة الثانوية.
- تستطيع النساء الإرث وحيازة الأرض وفق الدستور وإصلاح العرف التمييزي.
- يدعو رؤساء الاجتماعات النساء للكلام مبكراً لا في النهاية فقط.
- تعامل الخدمات (العيادات ومكاتب الشرطة) الناجيات بسرية وكرامة.

المساواة ليست «ثقافة أجنبية». هي وعد دستوري واستراتيجية تنمية: المجتمعات التي تُشرك النساء تتعافى أسرع من الأزمات.

## مثال من الواقع

لجنة مياه من عشرة رجال تقرر ساعات البئر بما يتعارض مع وقت جلب النساء للماء. بعد أن تطالب النساء بمقعدين وفترة صباحية، يقل الانتظار وتقل المشاجرات عند المضخة. الشمول حسّن النتيجة *الفنية* لا الإنصاف وحده.

## ماذا يمكنك أن تفعل

1. ادعم استمرار الفتيات في المدرسة في أسرتك وحيك.
2. واجه النكات التي تطبيع الضرب أو زواج الأطفال.
3. أصرّ على أن تضم اللجان المحلية نساءً وشباباً كأعضاء مصوّتين.
""",
    },
    {
        'slug': 'anti-corruption',
        'title': 'Public money is not private property',
        'title_ar': 'المال العام ليس ملكاً خاصاً',
        'tags': ['transparency', 'accountability', 'integrity'],
        'facts': [
            'Corruption is the abuse of entrusted power for private gain.',
            'Bribes raise the price of school, health, and justice for the poor.',
            'Transparency (open budgets, receipts) makes theft harder.',
            'Reporting is safer when channels are independent and confidential.',
        ],
        'content': """## Why this matters

**Corruption** steals classrooms, medicines, and roads. It is not a clever shortcut — it is a tax on people who cannot pay twice. Anti-corruption is civic education because every citizen can demand receipts, ask about tenders, and refuse to normalise bribes.

## Common patterns

- Paying a clerk to “speed up” a document that should be free or fixed-fee.
- Ghost workers on a payroll.
- Contracts awarded to relatives without competition.
- Humanitarian aid diverted from the intended community.

Leaders set the tone, but daily small bribes keep the system alive.

## Real-life example

A parent is told the birth certificate “costs extra under the table.” She asks for the official fee schedule posted on the wall, pays only that amount, and waits. It takes longer. The next parent sees that the extra fee is not inevitable. Collective refusal starts with one documented “no.”

## What you can do

1. Always ask for a receipt.
2. Use official hotlines or anti-corruption commissions when it is safe.
3. Praise public servants who work without gifts — culture changes when honesty is visible.
""",
        'content_ar': """## لماذا يهم هذا الموضوع

**الفساد** يسرق الفصول والأدوية والطرق. ليس اختصاراً ذكياً — بل ضريبة على من لا يستطيع الدفع مرتين. مكافحة الفساد تعليم مدني لأن كل مواطن يستطيع أن يطلب إيصالاً، ويسأل عن العطاءات، ويرفض تطبيع الرشوة.

## أنماط شائعة

- دفع مبلغ لموظف «لتسريع» وثيقة يفترض أن تكون مجانية أو برسم ثابت.
- موظفون وهميون على كشوف الرواتب.
- ترسية عقود على أقارب بلا منافسة.
- تحويل مساعدات إنسانية عن المجتمع المقصود.

القادة يحددون النبرة، لكن الرشى اليومية الصغيرة تُبقي النظام حياً.

## مثال من الواقع

يُقال لوالدة إن شهادة الميلاد «تكلف زيادة تحت الطاولة». تطلب جدول الرسوم الرسمي على الحائط، وتدفع ذلك المبلغ فقط، وتنتظر. يستغرق الأمر وقتاً أطول. الوالد التالي يرى أن الرسم الإضافي ليس قدراً. الرفض الجماعي يبدأ بـ«لا» موثّقة واحدة.

## ماذا يمكنك أن تفعل

1. اطلب إيصالاً دائماً.
2. استخدم الخطوط الساخنة الرسمية أو هيئات مكافحة الفساد عندما يكون ذلك آمناً.
3. امتدح الموظفين العامين الذين يعملون بلا هدايا — تتغير الثقافة عندما تظهر الأمانة.
""",
    },
    {
        'slug': 'public-participation',
        'title': 'Your voice belongs in public decisions',
        'title_ar': 'صوتك جزء من القرارات العامة',
        'tags': ['participation', 'consultation', 'petitions'],
        'facts': [
            'Public participation is more than voting every few years.',
            'Hearings, consultations, and petitions are lawful tools.',
            'Written input is harder to ignore than a corridor complaint.',
            'Inclusive meetings last longer — and produce better projects.',
        ],
        'content': """## Why this matters

Governments decide where clinics go, how school funds are spent, and which roads are graded. **Public participation** means affected people can influence those choices — not only hear about them afterwards.

## Ways to participate

- Attend advertised budget or planning hearings.
- Submit a short written comment (even a signed paragraph).
- Join a parent-teacher association or water user committee.
- Use lawful petitions and platform civic tools (polls and petitions here).
- Invite excluded neighbours so “the public” is not only the loudest men in the room.

Participation fails when meetings are announced the same morning, held far from women with childcare duties, or conducted only in a language many cannot follow.

## Real-life example

A county drafts a market-relocation plan. Traders who wait until demolition day lose. Traders who send a one-page note — “keep the well, move only the meat stalls, consult on the date” — give officials a workable alternative. Several associations signing the same note is participation with power.

## What you can do

1. Ask when the next public meeting is, and put it on a shared calendar.
2. Practise a 60-second statement: problem, who is affected, what you propose.
3. Sign or start a lawful petition on an issue that affects your payam.
""",
        'content_ar': """## لماذا يهم هذا الموضوع

تقرر الحكومات أين تُقام العيادات، وكيف تُنفق أموال المدارس، وأي طرق تُسوَّى. **المشاركة العامة** تعني أن يستطيع المتأثرون التأثير في تلك الخيارات — لا أن يسمعوا بها بعد التنفيذ فقط.

## طرق المشاركة

- احضر جلسات الموازنة أو التخطيط المعلنة.
- قدّم تعليقاً مكتوباً قصيراً (حتى فقرة موقّعة).
- انضم إلى جمعية آباء ومعلمين أو لجنة مستخدمي المياه.
- استخدم العرائض القانونية وأدوات المنصة المدنية (الاستطلاعات والعرائض هنا).
- ادعُ الجيران المستبعدين حتى لا يكون «الجمهور» أعلى أصوات الرجال في القاعة فقط.

تفشل المشاركة عندما يُعلن عن الاجتماع في الصباح نفسه، أو يُعقد بعيداً عن النساء المشغولات برعاية الأطفال، أو يُجرى بلغة لا يفهمها كثيرون.

## مثال من الواقع

تعدّ المقاطعة خطة لنقل السوق. التجار الذين ينتظرون يوم الهدم يخسرون. التجار الذين يرسلون ورقة واحدة — «أبقوا البئر، انقلوا أكشاك اللحم فقط، تشاوروا على التاريخ» — يمنحون المسؤولين بديلاً قابلاً للتنفيذ. توقيع عدة جمعيات على المذكرة نفسها مشاركة ذات وزن.

## ماذا يمكنك أن تفعل

1. اسأل عن موعد الاجتماع العام التالي وضعه في تقويم مشترك.
2. تدرب على بيان من 60 ثانية: المشكلة، من المتأثر، ماذا تقترح.
3. وقّع أو ابدأ عريضة قانونية في مسألة تمس بيامك.
""",
    },
    {
        'slug': 'media-misinformation',
        'title': 'Pause before you share: media literacy',
        'title_ar': 'توقّف قبل أن تشارك: الوعي الإعلامي',
        'tags': ['media', 'misinformation', 'facts'],
        'facts': [
            'Misinformation is false or misleading content, whether or not the sender meant harm.',
            'A forwarded voice note is not proof.',
            'Check the original source, date, and location before sharing.',
            'Independent journalism is a public good — protect reporters.',
        ],
        'content': """## Why this matters

Phones move rumours faster than county officials can respond. **Misinformation** can trigger panic, stigmatise a community, or steal an election’s legitimacy. Civic media literacy is the habit of pausing, checking, and correcting.

## A simple check

1. Who first published this, and can I name them?
2. Does the photo or clip match the date and place claimed?
3. What would a reputable radio station or official bulletin say?
4. If I am still unsure, I do **not** forward it.

Freedom of expression protects honest reporting and criticism. It does not require you to amplify lies.

## Real-life example

A WhatsApp message claims “all clinics in the county will close tomorrow.” A teacher checks the county health office notice board and a trusted FM station: both say a *training day* will shorten hours, not close facilities. She replies in the group with the official notice instead of the rumour. Panic at the gate is avoided.

## What you can do

1. Follow at least one verified official and one independent news source.
2. Teach family members the four checks above.
3. Apologise and correct if you shared something false — that is civic courage.
""",
        'content_ar': """## لماذا يهم هذا الموضوع

تنقل الهواتف الشائعات أسرع مما يستطيع مسؤولو المقاطعة الرد. **المعلومات المضللة** قد تثير الذعر أو تُلصق العار بمجتمع أو تسرق شرعية انتخابات. الوعي الإعلامي المدني عادة التوقف والتحقق والتصحيح.

## فحص بسيط

1. من نشر هذا أولاً، وهل أستطيع تسميته؟
2. هل تطابق الصورة أو المقطع التاريخ والمكان المزعومين؟
3. ماذا يقول راديو موثوق أو بيان رسمي؟
4. إن بقيت غير متأكد، **لا** أُعيد الإرسال.

حرية التعبير تحمي التغطية الصادقة والنقد. وهي لا تُلزمك بتضخيم الأكاذيب.

## مثال من الواقع

رسالة واتساب تزعم أن «كل عيادات المقاطعة ستُغلق غداً». تتحقق معلمة من لوحة مكتب الصحة في المقاطعة ومن محطة FM موثوقة: كلاهما يقول إن *يوم تدريب* سيقلّل الساعات لا يغلق المرافق. ترد في المجموعة بالإعلان الرسمي بدلاً من الشائعة. يُتجنَّب الذعر عند البوابة.

## ماذا يمكنك أن تفعل

1. تابع مصدراً رسمياً موثقاً ومصدراً إخبارياً مستقلاً على الأقل.
2. علّم أفراد الأسرة الفحوصات الأربعة أعلاه.
3. اعتذر وصحّح إذا شاركت شيئاً خاطئاً — ذلك شجاعة مدنية.
""",
    },
    {
        'slug': 'digital-citizenship',
        'title': 'Rights and safety on your phone',
        'title_ar': 'الحقوق والسلامة على هاتفك',
        'tags': ['digital', 'safety', 'online'],
        'facts': [
            'The same dignity and honesty rules apply online and offline.',
            'Strong passwords and updates protect your identity and money.',
            'Think before you post photos of children or survivors.',
            'Digital citizenship includes calling out harassment — and not joining it.',
        ],
        'content': """## Why this matters

More civic life now happens on phones: news, petitions, payments, and political debate. **Digital citizenship** means using those tools without harming others or yourself.

## Practical habits

- Use a PIN or password; do not share it for “verification” scams.
- Be sceptical of links that promise jobs, visas, or lottery wins.
- Do not record or share intimate images without consent — it can be abuse.
- In political arguments, attack ideas, not ethnic groups.
- Know how to mute, block, and report on the apps you use.

The constitution’s rights (expression, privacy, dignity) still apply on WhatsApp.

## Real-life example

A youth activist is asked to send her ID photo “to collect a civic training allowance.” The request comes from a new number. She calls the known NGO landline instead. The real organiser confirms they never collect IDs by chat. She avoided identity theft *and* modelled verification for her group.

## What you can do

1. Turn on device lock today.
2. Agree in your family which photos of children may never be posted.
3. Use this platform’s lessons offline when the network is weak — civic learning should not depend on rumours alone.
""",
        'content_ar': """## لماذا يهم هذا الموضوع

جزء أكبر من الحياة المدنية يحدث الآن على الهواتف: الأخبار والعرائض والمدفوعات والنقاش السياسي. **المواطنة الرقمية** تعني استخدام تلك الأدوات دون إلحاق الأذى بالآخرين أو بنفسك.

## عادات عملية

- استخدم رمزاً أو كلمة مرور؛ ولا تشاركها في عمليات احتيال «التحقق».
- كن متشككاً من الروابط التي تعد بوظائف أو تأشيرات أو جوائز.
- لا تسجّل أو تشارك صوراً حميمة دون موافقة — قد يكون ذلك إساءة.
- في الجدل السياسي، هاجم الأفكار لا الجماعات الإثنية.
- اعرف كيف تكتم وتحظر وتبلّغ في التطبيقات التي تستخدمها.

حقوق الدستور (التعبير والخصوصية والكرامة) ما زالت تسري على واتساب.

## مثال من الواقع

يُطلب من ناشطة شابة إرسال صورة هويتها «لاستلام بدل تدريب مدني». الطلب يأتي من رقم جديد. تتصل بالخط الأرضي المعروف للمنظمة بدلاً من ذلك. يؤكد المنظم الحقيقي أنهم لا يجمعون الهويات عبر الدردشة. تجنّبت سرقة الهوية *وقدّمت* نموذجاً للتحقق لمجموعتها.

## ماذا يمكنك أن تفعل

1. فعّل قفل الجهاز اليوم.
2. اتفقوا في الأسرة على صور الأطفال التي لا تُنشر أبداً.
3. استخدم دروس هذه المنصة دون اتصال عندما تكون الشبكة ضعيفة — لا ينبغي أن يعتمد التعلّم المدني على الشائعات وحدها.
""",
    },
    {
        'slug': 'community-leadership',
        'title': 'Leadership that serves the public',
        'title_ar': 'قيادة تخدم الجمهور',
        'tags': ['leadership', 'community', 'youth'],
        'facts': [
            'Leadership is a public trust, whether you are a chief, pastor, or youth chair.',
            'Good leaders listen, explain, and rotate tasks — they do not own the community.',
            'Youth and women leaders are part of the civic system, not a side project.',
            'Accountability (minutes, money records) is a form of respect.',
        ],
        'content': """## Why this matters

Laws and ministries cannot reach every boma. **Community leadership** — chiefs, elders, faith leaders, teachers, and youth chairs — is how many South Sudanese experience public authority. Civic education asks those leaders to serve, not to extract.

## Habits of public-minded leaders

- Call meetings with an agenda and keep minutes.
- Declare conflicts of interest (for example, a relative bidding for a contract).
- Share credit and train a successor.
- Protect dissenters from humiliation.
- Put women and youth on the decision list, not only the tea list.

Leadership is not only titles. Anyone who organises a school feeding roster is practising it.

## Real-life example

A youth union collects money for a football kit. The chair publishes a notebook photo: income, spending, remaining balance. Trust rises; the next collection is larger. Opacity would have killed the project faster than a lack of talent.

## What you can do

1. If you hold a role, publish a simple account of funds.
2. If you do not, ask for minutes rather than rumours.
3. Mentor one younger person to chair a meeting.
""",
        'content_ar': """## لماذا يهم هذا الموضوع

لا تستطيع القوانين والوزارات الوصول إلى كل بومة. **القيادة المجتمعية** — الزعماء والكبار والقيادات الدينية والمعلمون ورؤساء الشباب — هي كيف يختبر كثير من جنوب السودانيين السلطة العامة. يطلب التعليم المدني من هؤلاء القادة أن يخدموا لا أن يستغلوا.

## عادات القادة ذوي الروح العامة

- ادعُ إلى اجتماعات بجدول أعمال واحتفظ بالمحاضر.
- أعلن تضارب المصالح (مثلاً قريب يتقدم لعطاء).
- شارك الإنجاز ودرّب خليفة.
- احمِ المعارضين من الإذلال.
- ضع النساء والشباب في قائمة القرار لا في قائمة الشاي فقط.

القيادة ليست الألقاب وحدها. من ينظّم جدول إطعام مدرسي يمارسها.

## مثال من الواقع

يجمع اتحاد شباب مالاً لملابس كرة قدم. ينشر الرئيس صورة دفتر: الدخل والإنفاق والرصيد. ترتفع الثقة؛ وتكبر الجولة التالية. الغموض كان سيقتل المشروع أسرع من نقص الموهبة.

## ماذا يمكنك أن تفعل

1. إن كنت تتولى دوراً، انشر حساباً بسيطاً للأموال.
2. إن لم تكن، اطلب المحاضر بدلاً من الشائعات.
3. أرشد شخصاً أصغر لرئاسة اجتماع.
""",
    },
    {
        'slug': 'conflict-resolution',
        'title': 'Settle disputes without violence',
        'title_ar': 'سوِّ الخلافات دون عنف',
        'tags': ['mediation', 'dialogue', 'disputes'],
        'facts': [
            'Most local conflicts are about land, cattle, family, or rumours — they can be mediated.',
            'A mediator is impartial and does not take a side in secret.',
            'Agreements should be specific: who, what, when.',
            'Some harms (serious crime, GBV) need formal justice, not only a handshake.',
        ],
        'content': """## Why this matters

**Conflict resolution** is the skill of turning a clash into a process: listening, naming interests, and recording an agreement people can check. It sits beside peacebuilding (the longer political project) and the courts (for crimes and rights).

## A simple process

1. Cool down — delay talks if people are armed or drunk.
2. Let each side tell the story without interruption.
3. List facts you agree on and facts you dispute.
4. Invent options (compensation, apology, shared access, referral to court).
5. Write the deal and name who monitors it.

Customary mediation remains vital. It must not silence women or excuse serious violence.

## Real-life example

Two families dispute a plot after a relative dies without a will. A church mediator and a woman paralegal sit with both sides. They map the land, hear witnesses, and agree: the widow keeps the house plot; grazing land is shared by season; a county land officer stamps the sketch. The alternative was a fight at the boundary.

## What you can do

1. Practise listening for two minutes without preparing your reply.
2. Ask for written terms in any community settlement.
3. Refer cases of assault or child harm to formal authorities while support is offered to survivors.
""",
        'content_ar': """## لماذا يهم هذا الموضوع

**حل النزاعات** مهارة تحويل الصدام إلى مسار: الاستماع، وتسمية المصالح، وتوثيق اتفاق يمكن التحقق منه. يقع إلى جانب بناء السلام (المشروع السياسي الأطول) والمحاكم (للجرائم والحقوق).

## مسار بسيط

1. هدّئ الأجواء — أجّل الحديث إذا كان الناس مسلحين أو في حالة سكر.
2. دع كل طرف يروي القصة دون مقاطعة.
3. اسرد الوقائع المتفق عليها والمتنازع عليها.
4. ابتكر خيارات (تعويض، اعتذار، وصول مشترك، إحالة إلى المحكمة).
5. اكتب الاتفاق وسمِّ من يراقبه.

الوساطة العرفية ما زالت حيوية. ويجب ألا تُسكت النساء أو تبرر العنف الجسيم.

## مثال من الواقع

تتنازع أسرتان على قطعة أرض بعد وفاة قريب بلا وصية. يجلس وسيط كنسي ومساعدة قانونية مع الطرفين. يرسمان الأرض، ويسمعان الشهود، ويتفقان: تحتفظ الأرملة بقطعة المنزل؛ وتُستخدم أرض الرعي موسمياً؛ ويختم موظف الأراضي في المقاطعة الرسم. البديل كان عراكاً على الحدود.

## ماذا يمكنك أن تفعل

1. تدرب على الاستماع دقيقتين دون تحضير ردك.
2. اطلب شروطاً مكتوبة في أي تسوية مجتمعية.
3. أحل قضايا الاعتداء أو أذى الأطفال إلى السلطات الرسمية مع تقديم الدعم للناجيات.
""",
    },
)
