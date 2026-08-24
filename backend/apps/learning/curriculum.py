"""Official civic curriculum catalog (15 learning modules).

Seed data, the AI tutor, and the public topic list share these slugs so a
new module cannot drift between backend retrieval and demo content.
"""

from __future__ import annotations

CURRICULUM_CATEGORIES: tuple[dict, ...] = (
    {
        'slug': 'constitution',
        'name': 'Constitution and rights',
        'name_ar': 'الدستور والحقوق',
        'description': 'The Transitional Constitution, rights, and how supreme law limits power.',
        'description_ar': 'الدستور الانتقالي والحقوق وكيف يقيّد القانون الأعلى السلطة.',
        'keywords': {
            'constitution', 'constitutional', 'article', 'articles', 'bill',
            'fundamental', 'transitional', 'amendment', 'chapter',
            'دستور', 'مادة',
        },
    },
    {
        'slug': 'human-rights',
        'name': 'Human rights',
        'name_ar': 'حقوق الإنسان',
        'description': 'Dignity, equality, and protections every person is entitled to.',
        'description_ar': 'الكرامة والمساواة والحماية التي يستحقها كل إنسان.',
        'keywords': {
            'human', 'rights', 'dignity', 'discrimination', 'torture', 'refugee',
            'udhr', 'inhuman', 'حق', 'حقوق', 'كرامة', 'تمييز',
        },
    },
    {
        'slug': 'citizen-responsibilities',
        'name': 'Citizen responsibilities',
        'name_ar': 'واجبات المواطن',
        'description': 'Duties that accompany rights: obeying the law, taxes, and civic care.',
        'description_ar': 'الواجبات المرافقة للحقوق: احترام القانون والضرائب والرعاية المدنية.',
        'keywords': {
            'responsibility', 'responsibilities', 'duty', 'duties', 'obligations',
            'tax', 'taxes', 'census', 'obey', 'واجب', 'واجبات', 'ضريبة',
        },
    },
    {
        'slug': 'government-structure',
        'name': 'Government structure',
        'name_ar': 'هيكل الحكومة',
        'description': 'National, state, and local institutions and how they relate.',
        'description_ar': 'المؤسسات الوطنية والولائية والمحلية وكيف ترتبط.',
        'keywords': {
            'structure', 'president', 'legislature', 'judiciary', 'separation',
            'ministry', 'minister', 'cabinet', 'payam', 'boma',
            'هيكل', 'رئيس', 'وزارة', 'قضاء',
        },
    },
    {
        'slug': 'governance',
        'name': 'Democracy and governance',
        'name_ar': 'الديمقراطية والحكم',
        'description': 'How public decisions are made, checked, and opened to citizens.',
        'description_ar': 'كيف تُتخذ القرارات العامة وتُراقب وتُفتح أمام المواطنين.',
        'keywords': {
            'governance', 'government', 'govern', 'democracy', 'democratic',
            'institution', 'institutions', 'decentral', 'administration',
            'حكم', 'حكومة', 'ديمقراطية', 'مجلس',
        },
    },
    {
        'slug': 'elections',
        'name': 'Elections and voting',
        'name_ar': 'الانتخابات والتصويت',
        'description': 'Registering, voting peacefully, and protecting a fair count.',
        'description_ar': 'التسجيل والتصويت السلمي وحماية عدالة الفرز.',
        'keywords': {
            'election', 'elections', 'elect', 'vote', 'voting', 'voter', 'voters',
            'ballot', 'candidate', 'poll', 'referendum', 'turnout', 'register',
            'انتخاب', 'انتخابات', 'تصويت', 'ناخب',
        },
    },
    {
        'slug': 'rule-of-law',
        'name': 'Rule of law',
        'name_ar': 'سيادة القانون',
        'description': 'Nobody is above the law; disputes are decided by fair process.',
        'description_ar': 'لا أحد فوق القانون؛ تُحسم النزاعات بإجراءات عادلة.',
        'keywords': {
            'rule', 'law', 'laws', 'legal', 'court', 'courts', 'due',
            'arbitrary', 'impunity', 'قانون', 'محكمة', 'محاكم',
        },
    },
    {
        'slug': 'peacebuilding',
        'name': 'Peacebuilding',
        'name_ar': 'بناء السلام',
        'description': 'Reconciliation, trust, and preventing a return to violence.',
        'description_ar': 'المصالحة والثقة ومنع العودة إلى العنف.',
        'keywords': {
            'peace', 'peacebuilding', 'reconciliation', 'unity', 'dialogue',
            'security', 'violence', 'disarm', 'tolerance', 'coexist', 'healing',
            'سلام', 'مصالحة', 'نزاع',
        },
    },
    {
        'slug': 'gender-equality',
        'name': 'Gender equality and inclusion',
        'name_ar': 'المساواة بين الجنسين والشمول',
        'description': 'Equal voice and protection for women, girls, and excluded groups.',
        'description_ar': 'صوت متساوٍ وحماية للنساء والفتيات والفئات المستبعدة.',
        'keywords': {
            'gender', 'women', 'woman', 'girl', 'girls', 'inclusion', 'inclusive',
            'gbv', 'equality', 'مساواة', 'نساء', 'مرأة', 'شمول',
        },
    },
    {
        'slug': 'anti-corruption',
        'name': 'Anti-corruption',
        'name_ar': 'مكافحة الفساد',
        'description': 'Transparency, public money, and how citizens can report abuse.',
        'description_ar': 'الشفافية والمال العام وكيف يبلغ المواطنون عن إساءة الاستخدام.',
        'keywords': {
            'corruption', 'corrupt', 'bribe', 'bribery', 'transparency',
            'audit', 'kickback', 'embezzle', 'فساد', 'رشوة', 'شفافية',
        },
    },
    {
        'slug': 'public-participation',
        'name': 'Public participation',
        'name_ar': 'المشاركة العامة',
        'description': 'Hearings, consultations, petitions, and shaping local budgets.',
        'description_ar': 'الجلسات والاستشارات والعرائض والمساهمة في الموازنات المحلية.',
        'keywords': {
            'participation', 'participate', 'consultation', 'hearing', 'hearings',
            'petition', 'petitions', 'budget', 'consult', 'مشاركة', 'استشارة', 'عريضة',
        },
    },
    {
        'slug': 'media-misinformation',
        'name': 'Media and misinformation',
        'name_ar': 'الإعلام والمعلومات المضللة',
        'description': 'Reliable news, rumours, and how to check claims before sharing.',
        'description_ar': 'الأخبار الموثوقة والإشاعات وكيف تتحقق من الادعاءات قبل النشر.',
        'keywords': {
            'media', 'misinformation', 'disinformation', 'rumour', 'rumor',
            'fact', 'journalism', 'press', 'propaganda', 'إعلام', 'إشاعة', 'تضليل',
        },
    },
    {
        'slug': 'digital-citizenship',
        'name': 'Digital citizenship',
        'name_ar': 'المواطنة الرقمية',
        'description': 'Safe, respectful, and informed use of phones and the internet.',
        'description_ar': 'استخدام آمن ومحترم ومستنير للهواتف والإنترنت.',
        'keywords': {
            'digital', 'internet', 'online', 'cyber', 'password', 'smartphone',
            'whatsapp', 'facebook', 'رقمي', 'إنترنت', 'إلكتروني',
        },
    },
    {
        'slug': 'community-leadership',
        'name': 'Community leadership',
        'name_ar': 'القيادة المجتمعية',
        'description': 'Chiefs, councils, youth, and faith leaders serving the public.',
        'description_ar': 'الزعماء والمجالس والشباب والقيادات الدينية في خدمة الجمهور.',
        'keywords': {
            'leadership', 'leader', 'leaders', 'chief', 'elder', 'elders',
            'volunteer', 'youth', 'قيادة', 'زعيم', 'متطوع', 'شباب',
        },
    },
    {
        'slug': 'conflict-resolution',
        'name': 'Conflict resolution',
        'name_ar': 'حل النزاعات',
        'description': 'Mediation, dialogue, and settling disputes without violence.',
        'description_ar': 'الوساطة والحوار وتسوية الخلافات دون عنف.',
        'keywords': {
            'conflict', 'conflicts', 'mediation', 'mediate', 'dispute', 'disputes',
            'negotiate', 'negotiation', 'arbitrate', 'نزاع', 'وساطة', 'خلاف',
        },
    },
)

CATEGORY_SLUGS = tuple(item['slug'] for item in CURRICULUM_CATEGORIES)

CATEGORY_LABELS = {item['slug']: item['name'] for item in CURRICULUM_CATEGORIES}

CATEGORY_KEYWORDS = {item['slug']: set(item['keywords']) for item in CURRICULUM_CATEGORIES}


def curriculum_category_list() -> str:
    """Human-readable list for tutor prompts."""
    names = [item['name'] for item in CURRICULUM_CATEGORIES]
    if len(names) == 1:
        return names[0]
    return ', '.join(names[:-1]) + f', and {names[-1]}'
