from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone

from apps.accounts.models import Role
from apps.billing.models import Plan, Subscription
from apps.core.branding import PLATFORM_NAME
from apps.core.storage import upload_file
from apps.forum.models import DiscussionComment, DiscussionTopic
from apps.learning.curriculum import CURRICULUM_CATEGORIES
from apps.learning.curriculum_lessons import (
    CURRICULUM_AUDIO_URL,
    CURRICULUM_VIDEO_URL,
    LESSONS,
)
from apps.learning.misinformation import AWARENESS_ARTICLES
from apps.learning.models import Article, Category, MediaAsset
from apps.quizzes.models import Question, Quiz
from apps.tenants.services import create_organization_with_owner

User = get_user_model()

ROLES = ['citizen', 'moderator', 'editor', 'admin', 'super_admin']

REAL_CONSTITUTION_FILE = 'transitional-constitution.pdf'
SAMPLE_CONSTITUTION_FILE = 'transitional-constitution-sample.pdf'
CONSTITUTION_TEXT_FILE = 'transitional-constitution.txt'
SEED_ASSETS_DIR = Path(__file__).resolve().parent / 'seed_assets'

CONSTITUTION_INTRO = (
    'This controlled document contains the Transitional Constitution of the Republic of '
    'South Sudan, 2011. Citizens can download the PDF attachment, and the AI tutor uses '
    'this text when answering questions about constitutional rights and institutions.\n\n'
)
CONSTITUTION_INTRO_AR = (
    'تتضمن هذه الوثيقة الخاضعة للرقابة الدستور الانتقالي لجمهورية جنوب السودان لعام 2011. '
    'يمكن للمواطنين تنزيل مرفق PDF، ويستخدم مدرّس الذكاء الاصطناعي هذا النص عند الإجابة '
    'عن أسئلة الحقوق والمؤسسات الدستورية.\n\n'
)


def load_constitution_text() -> str | None:
    from apps.tutor.document_text import sanitize_text_for_db

    path = SEED_ASSETS_DIR / CONSTITUTION_TEXT_FILE
    if not path.is_file():
        return None
    text = sanitize_text_for_db(path.read_text(encoding='utf-8').strip())
    return text or None


def build_topic_svg(title: str, subtitle: str) -> bytes:
    """Simple infographic card used as the lesson featured image."""
    safe_title = (
        title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    )
    safe_sub = (
        subtitle.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <rect width="1200" height="630" fill="#064e3b"/>
  <rect x="48" y="48" width="1104" height="534" rx="28" fill="#ecfdf5"/>
  <rect x="48" y="48" width="16" height="534" rx="8" fill="#059669"/>
  <text x="100" y="160" font-family="Georgia, serif" font-size="28" fill="#047857">Civic Education RSS</text>
  <text x="100" y="280" font-family="Georgia, serif" font-size="48" font-weight="700" fill="#022c22">{safe_title}</text>
  <text x="100" y="360" font-family="Georgia, serif" font-size="28" fill="#134e4a">{safe_sub}</text>
  <text x="100" y="500" font-family="Georgia, serif" font-size="22" fill="#047857">Lesson pack · text · audio · video · handout</text>
</svg>
'''
    return svg.encode('utf-8')


def build_handout_pdf(title: str, facts: list[str]) -> bytes:
    """One-page learner handout (key facts infographic + reminder)."""
    from io import BytesIO

    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas as pdf_canvas

    buf = BytesIO()
    page = pdf_canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    y = height - 64
    page.setFillColorRGB(0.02, 0.17, 0.13)
    page.rect(0, height - 88, width, 88, fill=1, stroke=0)
    page.setFillColorRGB(1, 1, 1)
    page.setFont('Times-Bold', 16)
    page.drawString(48, height - 52, 'Civic Education RSS · Learner handout')
    page.setFillColorRGB(0.02, 0.17, 0.13)
    page.setFont('Times-Bold', 18)
    y = height - 130
    page.drawString(48, y, title[:90])
    y -= 36
    page.setFont('Times-Bold', 13)
    page.drawString(48, y, 'Key facts')
    y -= 28
    page.setFont('Times-Roman', 12)
    for i, fact in enumerate(facts[:6], start=1):
        wrapped = fact if len(fact) < 95 else fact[:92] + '...'
        page.drawString(56, y, f'{i}. {wrapped}')
        y -= 26
    y -= 12
    page.setFont('Times-Bold', 13)
    page.drawString(48, y, 'Real-life practice')
    y -= 24
    page.setFont('Times-Roman', 12)
    page.drawString(56, y, 'Read the full lesson, listen or watch the media, then discuss the example')
    y -= 18
    page.drawString(56, y, 'with family or a community group. Ask: who is responsible, and what can I do?')
    page.setFont('Times-Italic', 10)
    page.drawString(48, 40, 'Educational material for civic learners. Not a substitute for official legal text.')
    page.save()
    return buf.getvalue()


DEMO_QUIZ = {
    'title': 'South Sudan Civic Basics',
    'title_ar': 'أساسيات المواطنة في جنوب السودان',
    'description': 'A short quiz covering the constitution, rights, elections, and civic participation.',
    'description_ar': 'اختبار قصير يغطي الدستور والحقوق والانتخابات والمشاركة المدنية.',
    'passing_score': 70,
    'kind': 'assessment',
    'feedback_mode': 'end',
    'questions': [
        {
            'question_text': 'What document defines the structure of national government during the transition?',
            'question_text_ar': 'ما الوثيقة التي تحدد هيكل الحكومة الوطنية خلال الفترة الانتقالية؟',
            'question_type': Question.MCQ,
            'options': ['Transitional Constitution', 'County charter', 'Party manifesto', 'UN resolution'],
            'options_ar': ['الدستور الانتقالي', 'ميثاق المقاطعة', 'بيان الحزب', 'قرار الأمم المتحدة'],
            'correct_answer': 'Transitional Constitution',
            'explanation': 'The Transitional Constitution is the supreme law during the transition and organizes the branches of government.',
            'explanation_ar': 'الدستور الانتقالي هو القانون الأعلى خلال الفترة الانتقالية وينظّم سلطات الدولة.',
            'points': 1,
            'order': 0,
        },
        {
            'question_text': 'Peaceful participation in elections is a civic duty.',
            'question_text_ar': 'المشاركة السلمية في الانتخابات واجب مدني.',
            'question_type': Question.TRUE_FALSE,
            'options': ['True', 'False'],
            'options_ar': ['صحيح', 'خطأ'],
            'correct_answer': 'True',
            'explanation': 'Citizens have a duty to take part peacefully: register, vote, and report problems through official channels.',
            'explanation_ar': 'على المواطنين المشاركة بسلام: التسجيل والتصويت والإبلاغ عن المشكلات عبر القنوات الرسمية.',
            'points': 1,
            'order': 1,
        },
        {
            'question_text': 'Human rights belong only to people with political connections.',
            'question_text_ar': 'حقوق الإنسان تخص فقط من لهم علاقات سياسية.',
            'question_type': Question.TRUE_FALSE,
            'options': ['True', 'False'],
            'options_ar': ['صحيح', 'خطأ'],
            'correct_answer': 'False',
            'explanation': 'Human rights belong to every person because of dignity, not because of status or connections.',
            'explanation_ar': 'حقوق الإنسان تخص كل شخص بسبب الكرامة، لا بسبب المكانة أو العلاقات.',
            'points': 1,
            'order': 2,
        },
        {
            'question_text': 'A forwarded WhatsApp voice note is enough proof that a clinic will close.',
            'question_text_ar': 'رسالة واتساب صوتية مُعادة كافية لإثبات أن عيادة ستُغلق.',
            'question_type': Question.TRUE_FALSE,
            'options': ['True', 'False'],
            'options_ar': ['صحيح', 'خطأ'],
            'correct_answer': 'False',
            'explanation': 'Forwarded messages are not proof. Check a second independent source such as the clinic or a trusted official notice.',
            'explanation_ar': 'الرسائل المُعادة ليست دليلاً. تحقق من مصدر مستقل ثانٍ مثل العيادة أو إعلان رسمي موثوق.',
            'points': 1,
            'order': 3,
        },
        {
            'question_text': 'Which practice best supports the rule of law?',
            'question_text_ar': 'أي ممارسة تدعم سيادة القانون أكثر؟',
            'question_type': Question.MCQ,
            'options': [
                'Applying the same rules to leaders and citizens',
                'Letting the strongest person decide every dispute',
                'Paying extra unofficial fees to speed services',
                'Ignoring court orders you dislike',
            ],
            'options_ar': [
                'تطبيق القواعد نفسها على القادة والمواطنين',
                'ترك الأقوى يحسم كل نزاع',
                'دفع رسوم غير رسمية لتسريع الخدمات',
                'تجاهل أوامر المحكمة التي لا تعجبك',
            ],
            'correct_answer': 'Applying the same rules to leaders and citizens',
            'explanation': 'Rule of law means the same rules bind leaders and citizens, and disputes are decided by fair process.',
            'explanation_ar': 'سيادة القانون تعني أن القواعد نفسها تُلزم القادة والمواطنين، وأن النزاعات تُحسم بإجراءات عادلة.',
            'points': 1,
            'order': 4,
        },
    ],
}

DEMO_SCENARIO_QUIZ = {
    'title': 'Civic choices: what would you do?',
    'title_ar': 'خيارات مدنية: ماذا تفعل؟',
    'description': (
        'Practice real situations. Each choice teaches your rights, duties, '
        'legal process, and peaceful civic participation — even when the answer is wrong.'
    ),
    'description_ar': (
        'تدرّب على مواقف حقيقية. كل خيار يعلّمك حقوقك وواجباتك والإجراء القانوني '
        'والمشاركة المدنية السلمية — حتى إذا كانت الإجابة غير صحيحة.'
    ),
    'passing_score': 70,
    'kind': 'practice',
    'feedback_mode': 'per_question',
    'questions': [
        {
            'question_text': (
                'You work in a county office. You see a colleague ask a citizen for an extra '
                'unofficial fee to process a birth certificate. The citizen looks afraid.\n\n'
                'What are your legal and civic options?'
            ),
            'question_text_ar': (
                'تعمل في مكتب المقاطعة. ترى زميلاً يطلب من مواطن رسماً إضافياً غير رسمي '
                'لإنجاز شهادة ميلاد. يبدو المواطن خائفاً.\n\n'
                'ما خياراتك القانونية والمدنية؟'
            ),
            'question_type': Question.SCENARIO,
            'options': [
                'Report through official complaints or anti-corruption channels and keep a record of what you saw',
                'Stay silent so you do not lose your job or make enemies',
                'Confront the colleague angrily in public and threaten them',
                'Tell the citizen to pay the extra fee so the work gets done',
            ],
            'options_ar': [
                'بلّغ عبر قنوات الشكاوى الرسمية أو مكافحة الفساد واحتفظ بسجل لما رأيته',
                'اصمت حتى لا تفقد عملك أو تصنع أعداء',
                'واجه الزميل بغضب أمام الناس وهدّده',
                'قل للمواطن أن يدفع الرسم الإضافي حتى يُنجز العمل',
            ],
            'correct_answer': (
                'Report through official complaints or anti-corruption channels and keep a record of what you saw'
            ),
            'option_feedback': [
                {
                    'en': (
                        'Rights: you and the citizen may seek public services without unofficial fees. '
                        'Duties: public money and office are not private property — staff must not demand bribes. '
                        'Process: write what you saw (date, names, amount), use the office complaints path or an '
                        'anti-corruption / audit body, and keep copies. '
                        'Peaceful participation: reporting through official channels is civic action without violence.'
                    ),
                    'ar': (
                        'الحقوق: لك وللمواطن طلب الخدمات العامة دون رسوم غير رسمية. '
                        'الواجبات: المال العام والمنصب ليسا ملكاً خاصاً — لا يجوز للموظفين طلب رشاوى. '
                        'الإجراء: اكتب ما رأيته (التاريخ والأسماء والمبلغ) واستخدم مسار الشكاوى في المكتب '
                        'أو جهة مكافحة الفساد/الرقابة واحتفظ بنسخ. '
                        'المشاركة السلمية: التبليغ عبر القنوات الرسمية عمل مدني دون عنف.'
                    ),
                },
                {
                    'en': (
                        'Silence can feel safer, but it leaves the citizen unprotected and lets the practice spread. '
                        'Your duty in public service is to the public, not only to colleagues. '
                        'If you fear retaliation, report through a channel that allows written or confidential complaints, '
                        'and do not confront anyone alone. Peaceful reporting is still participation.'
                    ),
                    'ar': (
                        'الصمت قد يبدو أكثر أماناً، لكنه يترك المواطن بلا حماية ويسمح للممارسة بالانتشار. '
                        'واجبك في الخدمة العامة للجمهور لا للزملاء فقط. '
                        'إذا خفت الانتقام فبلّغ عبر قناة تسمح بشكوى مكتوبة أو سرية، ولا تواجه أحداً وحدك. '
                        'التبليغ السلمي يبقى مشاركة.'
                    ),
                },
                {
                    'en': (
                        'Anger is understandable, but threats and public humiliation can become a new offence '
                        'and weaken your report. Rights are protected through fair process, not revenge. '
                        'Record facts, use official channels, and let investigators act. That is peaceful civic duty.'
                    ),
                    'ar': (
                        'الغضب مفهوم، لكن التهديد والإذلال العلني قد يصبح مخالفة جديدة ويُضعف بلاغك. '
                        'تُحمى الحقوق بإجراء عادل لا بالانتقام. '
                        'سجّل الوقائع واستخدم القنوات الرسمية ودع المحققين يعملون. هذا واجب مدني سلمي.'
                    ),
                },
                {
                    'en': (
                        'Telling the citizen to pay continues the harm. The certificate is a legal right, not a favour. '
                        'Unofficial fees are corruption. Help the person use the official fee list and complaints path '
                        'instead of paying extra. Peaceful participation means refusing the bribe and reporting it.'
                    ),
                    'ar': (
                        'قولك للمواطن أن يدفع يُكمل الضرر. الشهادة حق قانوني لا منّة. '
                        'الرسوم غير الرسمية فساد. ساعد الشخص على استخدام قائمة الرسوم الرسمية ومسار الشكاوى '
                        'بدلاً من الدفع الزائد. المشاركة السلمية تعني رفض الرشوة والتبليغ عنها.'
                    ),
                },
            ],
            'points': 1,
            'order': 0,
        },
        {
            'question_text': (
                'A neighbour says armed men told the village not to vote, or they will burn the market. '
                'People are afraid. What should you do?'
            ),
            'question_text_ar': (
                'يقول جار إن مسلحين أخبروا القرية ألا تصوّت وإلا أحرقوا السوق. '
                'الناس خائفون. ماذا ينبغي أن تفعل؟'
            ),
            'question_type': Question.SCENARIO,
            'options': [
                'Report the threat to election officials or police and encourage peaceful, documented complaints',
                'Stay home and tell everyone voting is too dangerous so the threat succeeds',
                'Organize a group to attack the men who made the threat',
                'Pay the men a “protection” fee so the village can vote',
            ],
            'options_ar': [
                'بلّغ عن التهديد لمسؤولي الانتخابات أو الشرطة وشجّع شكاوى سلمية موثّقة',
                'ابق في البيت وقل للجميع إن التصويت خطر جداً حتى ينجح التهديد',
                'نظّم مجموعة لمهاجمة من أطلق التهديد',
                'ادفع للرجال رسماً «للحماية» حتى تتمكّن القرية من التصويت',
            ],
            'correct_answer': (
                'Report the threat to election officials or police and encourage peaceful, documented complaints'
            ),
            'option_feedback': [
                {
                    'en': (
                        'Rights: a free vote is protected; intimidation is unlawful. '
                        'Duties: report threats so others can vote in safety. '
                        'Process: tell election officials, police, or observers; write names, time, and place; keep copies. '
                        'Peaceful participation: documenting and reporting is how citizens defend elections without becoming a militia.'
                    ),
                    'ar': (
                        'الحقوق: التصويت الحر محمي؛ الترهيب غير قانوني. '
                        'الواجبات: بلّغ عن التهديدات حتى يصوّت الآخرون بأمان. '
                        'الإجراء: أخبر مسؤولي الانتخابات أو الشرطة أو المراقبين؛ اكتب الأسماء والوقت والمكان واحتفظ بنسخ. '
                        'المشاركة السلمية: التوثيق والتبليغ هو كيف يدافع المواطنون عن الانتخابات دون أن يصبحوا ميليشيا.'
                    ),
                },
                {
                    'en': (
                        'Fear is real, but if everyone stays home the threat wins and rights are lost. '
                        'Your duty is not to force neighbours into danger, but to report so security and election bodies can act. '
                        'Peaceful civic participation includes asking for protection, not spreading panic as if the threat were law.'
                    ),
                    'ar': (
                        'الخوف حقيقي، لكن إذا بقي الجميع في البيت ينتصر التهديد وتضيع الحقوق. '
                        'واجبك ليس إجبار الجيران على الخطر، بل التبليغ حتى تتحرك جهات الأمن والانتخابات. '
                        'المشاركة المدنية السلمية تشمل طلب الحماية، لا نشر الذعر كأن التهديد قانون.'
                    ),
                },
                {
                    'en': (
                        'Counter-violence invites more harm and can be a crime. The legal process is to report, '
                        'seek protection, and let lawful security act. Peaceful participation defends voting rights '
                        'without becoming the next armed group.'
                    ),
                    'ar': (
                        'العنف المضاد يجلب مزيداً من الأذى وقد يكون جريمة. الإجراء القانوني هو التبليغ '
                        'وطلب الحماية وترك الأمن المشروع يعمل. المشاركة السلمية تدافع عن حق التصويت '
                        'دون أن تصبح المجموعة المسلحة التالية.'
                    ),
                },
                {
                    'en': (
                        'Paying “protection” is another form of corruption and rewards intimidation. '
                        'Voting is a right, not a service you buy from armed men. Report the demand; '
                        'do not fund the threat.'
                    ),
                    'ar': (
                        'دفع «الحماية» شكل آخر من الفساد ويكافئ الترهيب. '
                        'التصويت حق لا خدمة تشتريها من مسلحين. بلّغ عن الطلب؛ لا تموّل التهديد.'
                    ),
                },
            ],
            'points': 1,
            'order': 1,
        },
        {
            'question_text': (
                'Two families dispute a water point. Voices rise. Someone picks up a stick. '
                'You are a neighbour, not a judge. What civic choice fits best?'
            ),
            'question_text_ar': (
                'أسرتان تتنازعان على نقطة مياه. ترتفع الأصوات. يلتقط أحدهم عصا. '
                'أنت جار ولست قاضياً. أي خيار مدني أنسب؟'
            ),
            'question_type': Question.SCENARIO,
            'options': [
                'Call for a pause, suggest a known mediator or chief, and keep the dispute from turning into violence',
                'Cheer for the stronger family so the fight ends quickly',
                'Join the side that is your relative, even if you did not see how the dispute started',
                'Tell both sides that whoever is stronger owns the water, so law does not matter',
            ],
            'options_ar': [
                'اطلب وقفة واقترح وسيطاً أو زعيماً معروفاً وامنع النزاع من التحول إلى عنف',
                'شجّع الأسرة الأقوى حتى ينتهي الشجار سريعاً',
                'انضم إلى طرف قريبك حتى لو لم تر كيف بدأ النزاع',
                'قل للطرفين إن الأقوى يملك الماء، فلا أهمية للقانون',
            ],
            'correct_answer': (
                'Call for a pause, suggest a known mediator or chief, and keep the dispute from turning into violence'
            ),
            'option_feedback': [
                {
                    'en': (
                        'Rights: both families may seek a fair hearing; nobody may settle the dispute by beating the other. '
                        'Duties: neighbours can cool the situation and point to mediation, chiefs, or local courts. '
                        'Process: pause, no weapons, a known mediator, written notes if useful, then the proper forum. '
                        'Peaceful participation: de-escalation is civic leadership even when you are not an official.'
                    ),
                    'ar': (
                        'الحقوق: يحق للأسرتين جلسة عادلة؛ لا يجوز حسم النزاع بالضرب. '
                        'الواجبات: يمكن للجيران تهدئة الموقف والإشارة إلى الوساطة أو الزعماء أو المحاكم المحلية. '
                        'الإجراء: وقفة بلا سلاح ووسيط معروف وملاحظات مكتوبة إن نفعت ثم الجهة المختصة. '
                        'المشاركة السلمية: خفض التوتر قيادة مدنية حتى إن لم تكن مسؤولاً.'
                    ),
                },
                {
                    'en': (
                        'Cheering the stronger side teaches that force replaces law. Your duty is not entertainment; '
                        'it is to reduce harm. Ask for a pause and a mediator instead of a crowd that rewards violence.'
                    ),
                    'ar': (
                        'تشجيع الأقوى يعلّم أن القوة تحل محل القانون. واجبك ليس التسلية بل تقليل الأذى. '
                        'اطلب وقفة ووسيطاً بدلاً من حشد يكافئ العنف.'
                    ),
                },
                {
                    'en': (
                        'Kinship is real, but taking a side you did not witness can spread the conflict. '
                        'Rights require a fair process. Help both sides reach a mediator; do not become a second fighter.'
                    ),
                    'ar': (
                        'القرابة حقيقية، لكن الانحياز دون أن تشهد يوسّع النزاع. '
                        'الحقوق تحتاج إجراءً عادلاً. ساعد الطرفين على الوصول إلى وسيط؛ لا تصبح مقاتلاً ثانياً.'
                    ),
                },
                {
                    'en': (
                        '“Might makes right” is the opposite of the rule of law. Water access can be decided by custom '
                        'and lawful forums, not by who holds the stick. Peaceful civic participation insists that '
                        'rules apply even when tempers are high.'
                    ),
                    'ar': (
                        '«القوة تصنع الحق» نقيض سيادة القانون. يمكن حسم الوصول إلى الماء بالعرف والمنتديات القانونية، '
                        'لا بمن يمسك العصا. المشاركة المدنية السلمية تصرّ على أن القواعد تسري حتى عند غليان الغضب.'
                    ),
                },
            ],
            'points': 1,
            'order': 2,
        },
    ],
}

DEMO_FACT_FICTION_QUIZ = {
    'title': 'Fact or Fiction?',
    'title_ar': 'حقيقة أم خيال؟',
    'description': (
        'Practice spotting rumours, unnamed “official” claims, and old photos used as new news. '
        'Each answer explains how to verify — this is a practice quiz, not a certificate.'
    ),
    'description_ar': (
        'تدرّب على رصد الشائعات والادعاءات «الرسمية» غير المسمّاة والصور القديمة المستخدمة كأخبار جديدة. '
        'كل إجابة تشرح كيف تتحقق — هذا اختبار تطبيقي وليس شهادة.'
    ),
    'passing_score': 70,
    'kind': 'practice',
    'feedback_mode': 'per_question',
    'questions': [
        {
            'question_text': (
                'A forwarded WhatsApp voice note with no name says every clinic in the county will close tomorrow. '
                'Is that enough to treat the shutdown as fact?'
            ),
            'question_text_ar': (
                'رسالة واتساب صوتية مُعادة بلا اسم تقول إن كل عيادة في المقاطعة ستُغلق غداً. '
                'هل يكفي ذلك لاعتبار الإغلاق حقيقة؟'
            ),
            'question_type': Question.TRUE_FALSE,
            'options': ['True', 'False'],
            'options_ar': ['صحيح', 'خطأ'],
            'correct_answer': 'False',
            'explanation': (
                'Fiction until proven. A nameless forward is not an official notice. '
                'Check the county health office or a trusted bulletin before you share or change plans.'
            ),
            'explanation_ar': (
                'خيال حتى يُثبت. إعادة الإرسال بلا اسم ليست إعلاناً رسمياً. '
                'تحقق من مكتب الصحة في المقاطعة أو من نشرة موثوقة قبل أن تشارك أو تغيّر خططك.'
            ),
            'points': 1,
            'order': 0,
        },
        {
            'question_text': (
                'Checking a second independent source — such as a notice board or a named radio station — '
                'is a good way to verify a viral claim.'
            ),
            'question_text_ar': (
                'التحقق من مصدر مستقل ثانٍ — مثل لوحة إعلانات أو إذاعة مسمّاة — '
                'طريقة جيدة للتأكد من ادعاء متداول.'
            ),
            'question_type': Question.TRUE_FALSE,
            'options': ['True', 'False'],
            'options_ar': ['صحيح', 'خطأ'],
            'correct_answer': 'True',
            'explanation': (
                'Fact. One independent confirmation is worth more than many forwards from the same chat.'
            ),
            'explanation_ar': (
                'حقيقة. تأكيد مستقل واحد أغلى من كثير من إعادات الإرسال من الدردشة نفسها.'
            ),
            'points': 1,
            'order': 1,
        },
        {
            'question_text': (
                'A photo can be real and still be false news if the caption uses the wrong date or place.'
            ),
            'question_text_ar': (
                'قد تكون الصورة حقيقية ومع ذلك خبراً كاذباً إذا استخدم التعليق تاريخاً أو مكاناً خاطئاً.'
            ),
            'question_type': Question.TRUE_FALSE,
            'options': ['True', 'False'],
            'options_ar': ['صحيح', 'خطأ'],
            'correct_answer': 'True',
            'explanation': (
                'Fact. Old or foreign pictures are often recycled as “happening now.” Ask when and where it was first published.'
            ),
            'explanation_ar': (
                'حقيقة. غالباً تُعاد صور قديمة أو من بلد آخر على أنها «تحدث الآن». اسأل متى وأين نُشرت أولاً.'
            ),
            'points': 1,
            'order': 2,
        },
        {
            'question_text': (
                'You should forward an unverified warning “just in case,” because sharing rumours is harmless.'
            ),
            'question_text_ar': (
                'ينبغي أن تعيد تحذيراً غير موثّق «احتياطاً»، لأن نشر الشائعات لا يضر.'
            ),
            'question_type': Question.TRUE_FALSE,
            'options': ['True', 'False'],
            'options_ar': ['صحيح', 'خطأ'],
            'correct_answer': 'False',
            'explanation': (
                'Fiction. Forwarding is publishing. Rumours can cause panic, stigma, or election harm. If unsure, do not share.'
            ),
            'explanation_ar': (
                'خيال. إعادة الإرسال نشر. قد تثير الشائعات ذعراً أو وصماً أو ضرراً انتخابياً. إن لم تكن متأكداً، لا تشارك.'
            ),
            'points': 1,
            'order': 3,
        },
        {
            'question_text': (
                'A flyer with a government-looking logo and no issuing office, gazette number, or matching notice board '
                'should be treated as a verified new law.'
            ),
            'question_text_ar': (
                'منشور بشعار يبدو حكومياً بلا جهة مصدرة ولا رقم جريدة ولا لوحة مطابقة '
                'يجب معاملته كقانون جديد موثّق.'
            ),
            'question_type': Question.TRUE_FALSE,
            'options': ['True', 'False'],
            'options_ar': ['صحيح', 'خطأ'],
            'correct_answer': 'False',
            'explanation': (
                'Fiction. Borrowed logos are a common trick. Real notices name the office and can be matched independently.'
            ),
            'explanation_ar': (
                'خيال. الشعارات المستعارة حيلة شائعة. الإعلانات الحقيقية تسمّي المكتب ويمكن مطابقتها بشكل مستقل.'
            ),
            'points': 1,
            'order': 4,
        },
        {
            'question_text': (
                'A neighbour forwards: “Polling stations will close two hours early — tell everyone.” '
                'There is no electoral commission letter. What should you do?'
            ),
            'question_text_ar': (
                'جار يعيد: «ستُغلق مراكز الاقتراع قبل موعدها بساعتين — أخبروا الجميع.» '
                'لا خطاب من المفوضية الانتخابية. ماذا تفعل؟'
            ),
            'question_type': Question.SCENARIO,
            'options': [
                'Forward it immediately so people are not locked out',
                'Treat it as unverified and check an official election source before sharing',
                'Argue in the group that elections are always a fraud',
                'Ignore voting altogether because rumours mean the process is broken',
            ],
            'options_ar': [
                'أعد إرساله فوراً حتى لا يُحرم الناس',
                'عامله كغير موثّق وتحقق من مصدر انتخابي رسمي قبل المشاركة',
                'جادل في المجموعة بأن الانتخابات دائماً احتيال',
                'تجاهل التصويت لأن الشائعات تعني أن العملية منتهية',
            ],
            'correct_answer': 'Treat it as unverified and check an official election source before sharing',
            'explanation': (
                'Unverified election rumours can suppress turnout. Check the electoral commission or a labelled verified notice.'
            ),
            'explanation_ar': (
                'شائعات الانتخابات غير الموثّقة قد تثبّط الإقبال. تحقق من المفوضية أو من إشعار موثّق مصنّف.'
            ),
            'option_feedback': [
                {
                    'en': 'Forwarding an unnamed time change can keep people away from the polls. That is harm, not help.',
                    'ar': 'إعادة تغيير وقت غير مسمّى قد تُبعد الناس عن الصناديق. ذلك أذى لا مساعدة.',
                },
                {
                    'en': 'Rights and duties: vote when you can, and verify process claims through official channels. Peaceful participation includes refusing to spread panic.',
                    'ar': 'الحقوق والواجبات: صوّت عندما تستطيع، وتحقق من ادعاءات الإجراءات عبر القنوات الرسمية. المشاركة السلمية تشمل رفض نشر الذعر.',
                },
                {
                    'en': 'Sweeping attacks on the whole process do not check this message. Ask for a named source instead.',
                    'ar': 'الهجوم الشامل على العملية كلها لا يفحص هذه الرسالة. اطلب مصدراً مسمّى بدلاً من ذلك.',
                },
                {
                    'en': 'Rumours are a reason to verify, not a reason to give up your vote. Check, then participate peacefully.',
                    'ar': 'الشائعات سبب للتحقق لا للتخلي عن صوتك. تحقق ثم شارك بسلام.',
                },
            ],
            'points': 1,
            'order': 5,
        },
    ],
}

DEMO_FORUM = {
    'title': 'How can youth participate in local governance?',
    'content': (
        'Share practical examples of youth councils, community forums, or volunteer initiatives '
        'that helped your county or payam.'
    ),
    'comment': (
        'Our student group attended a payam budget hearing and asked how education funds were allocated.'
    ),
    'board': 'governance',
}

DEMO_FORUM_QUESTION = {
    'title': 'What is one peaceful way to check a rumour about an election?',
    'content': (
        'If someone forwards a message about polling hours or results with no named office, '
        'what should a citizen do before sharing it?'
    ),
    'comment': (
        'Pause, look for a named official source such as the National Elections Commission, '
        'and share only what you can verify. Do not attack people or parties.'
    ),
    'board': 'elections',
}

DEMO_POLLS = [
    {
        'question': 'What civic topic should we cover next?',
        'question_ar': 'ما الموضوع المدني الذي يجب أن نغطيه بعد ذلك؟',
        'description': 'An educational poll to help shape future learning content.',
        'description_ar': 'استطلاع تعليمي للمساعدة في تشكيل محتوى التعلم القادم.',
        'kind': 'educational',
        'options': [
            ('Elections', 'الانتخابات'),
            ('Local governance', 'الحكم المحلي'),
            ('Peacebuilding', 'بناء السلام'),
        ],
    },
    {
        'question': 'What is the biggest challenge in your community?',
        'question_ar': 'ما أكبر تحدٍ في مجتمعك؟',
        'description': 'A community poll. Choose the issue you see most often where you live.',
        'description_ar': 'استطلاع مجتمعي. اختر المسألة التي تراها أكثر في مكان إقامتك.',
        'kind': 'community',
        'options': [
            ('Education', 'التعليم'),
            ('Health services', 'الخدمات الصحية'),
            ('Water and sanitation', 'المياه والصرف الصحي'),
            ('Security', 'الأمن'),
            ('Jobs', 'فرص العمل'),
        ],
    },
    {
        'question': 'Which public service needs improvement?',
        'question_ar': 'أي خدمة عامة تحتاج إلى تحسين؟',
        'description': 'A community poll about everyday public services.',
        'description_ar': 'استطلاع مجتمعي عن الخدمات العامة اليومية.',
        'kind': 'community',
        'options': [
            ('Schools', 'المدارس'),
            ('Clinics', 'العيادات'),
            ('Clean water', 'المياه النظيفة'),
            ('Roads', 'الطرق'),
            ('Local administration', 'الإدارة المحلية'),
        ],
    },
    {
        'question': 'Do citizens understand this new policy?',
        'question_ar': 'هل يفهم المواطنون هذه السياسة الجديدة؟',
        'description': (
            'Educational check: a county office announced a new public fee. '
            'How clear is the policy to you?'
        ),
        'description_ar': (
            'فحص تعليمي: أعلن مكتب المقاطعة عن رسم عام جديد. '
            'ما مدى وضوح السياسة بالنسبة لك؟'
        ),
        'kind': 'educational',
        'options': [
            ('I understand it clearly', 'أفهمها بوضوح'),
            ('I understand some of it', 'أفهم جزءاً منها'),
            ('I do not understand it', 'لا أفهمها'),
            ('I have not heard about it', 'لم أسمع عنها'),
        ],
    },
]

DEMO_NEWS = [
    {
        'title': 'Civic news board is open for labelled public information',
        'title_ar': 'لوحة الأخبار المدنية مفتوحة للمعلومات العامة المصنّفة',
        'topic': 'announcement',
        'claim_type': 'verified_fact',
        'source_name': 'Civic Education RSS',
        'source_url': '',
        'body': (
            'This board publishes public civic information with a visible claim label on every item. '
            'This notice is a verified platform announcement: the News & Civic Information section is live '
            'for learners and visitors. Official government notices posted here must name their issuing source.'
        ),
        'body_ar': (
            'تنشر هذه اللوحة معلومات مدنية عامة مع تصنيف واضح لنوع الادعاء على كل مادة. '
            'هذا إعلان موثّق من المنصة: قسم الأخبار والمعلومات المدنية متاح للمتعلمين والزوار. '
            'يجب أن تذكر الإعلانات الحكومية المنشورة هنا الجهة المصدرة.'
        ),
    },
    {
        'title': 'New practice quiz: civic choices in everyday situations',
        'title_ar': 'اختبار تطبيقي جديد: خيارات مدنية في مواقف يومية',
        'topic': 'education_update',
        'claim_type': 'educational',
        'source_name': '',
        'source_url': '',
        'body': (
            'A new practice quiz walks through everyday civic situations — unofficial fees, election '
            'pressure, and community disputes — and explains rights, duties, and peaceful process. '
            'This update describes a learning resource. It is not a government announcement and does not '
            'change any law.'
        ),
        'body_ar': (
            'يشرح اختبار تطبيقي جديد مواقف مدنية يومية — رسوم غير رسمية، وضغط انتخابي، ونزاعات مجتمعية — '
            'ويوضح الحقوق والواجبات والسبل السلمية. هذا التحديث يصف مورداً تعليمياً. '
            'وهو ليس إعلاناً حكومياً ولا يغيّر أي قانون.'
        ),
    },
    {
        'title': 'How to check official election information',
        'title_ar': 'كيف تتحقق من المعلومات الانتخابية الرسمية',
        'topic': 'election',
        'claim_type': 'educational',
        'source_name': '',
        'source_url': '',
        'body': (
            'Election dates, polling locations, and candidate lists should come from the official electoral '
            'commission or a named government gazette. Treat viral messages, forwarded photos, and unnamed '
            '“insider” claims as unverified until you can match them to an official source. This explainer '
            'teaches that habit; it does not announce an election calendar.'
        ),
        'body_ar': (
            'يجب أن تصدر مواعيد الانتخابات ومراكز الاقتراع وقوائم المرشحين عن المفوضية الانتخابية الرسمية '
            'أو عن جريدة حكومية مسمّاة. تعامل مع الرسائل المتداولة والصور المُعادة وادعاءات "المطلعين" '
            'غير المسمّاة كمعلومات غير موثّقة حتى تطابقها مع مصدر رسمي. هذا الشرح يعلّم تلك العادة؛ '
            'وهو لا يعلن جدولاً انتخابياً.'
        ),
    },
    {
        'title': 'The Transitional Constitution is the supreme law during the transition',
        'title_ar': 'الدستور الانتقالي هو القانون الأعلى خلال الفترة الانتقالية',
        'topic': 'law_policy',
        'claim_type': 'verified_fact',
        'source_name': 'Transitional Constitution of the Republic of South Sudan, 2011',
        'source_url': '',
        'body': (
            'During the transition, the Transitional Constitution of the Republic of South Sudan (2011) '
            'is the supreme law. Other laws and policies should be read against it. This statement restates '
            'that constitutional fact; it is not a new statute and it is not legal advice for a specific case.'
        ),
        'body_ar': (
            'خلال الفترة الانتقالية، يُعد الدستور الانتقالي لجمهورية جنوب السودان (2011) القانون الأعلى. '
            'وينبغي قراءة القوانين والسياسات الأخرى في ضوئه. تعيد هذه المادة ذكر تلك الحقيقة الدستورية؛ '
            'وهي ليست قانوناً جديداً وليست استشارة قانونية لحالة معيّنة.'
        ),
    },
    {
        'title': 'Unofficial fees erode trust — a civic educator’s view',
        'title_ar': 'الرسوم غير الرسمية تُضعف الثقة — رأي مربٍ مدني',
        'topic': 'awareness',
        'claim_type': 'opinion',
        'source_name': 'Civic Education RSS editorial',
        'source_url': '',
        'body': (
            'In our view, asking citizens to pay unofficial fees for public services weakens trust and '
            'makes it harder for people to use their rights. Reporting those requests through lawful channels '
            'protects both the person asked and the integrity of public offices. This is an opinion for public '
            'awareness, not an official investigation or a finding of fact about any named office.'
        ),
        'body_ar': (
            'من رأينا أن مطالبة المواطنين برسوم غير رسمية مقابل خدمات عامة تُضعف الثقة وتصعّب ممارسة الحقوق. '
            'والإبلاغ عن تلك المطالبات عبر القنوات القانونية يحمي من يُطلب منه الرسم ونزاهة المكاتب العامة. '
            'هذا رأي للتوعية العامة، وليس تحقيقاً رسمياً ولا إثباتاً بحق أي مكتب مسمّى.'
        ),
    },
    {
        'title': 'Forwarded claim: polling stations will close early — not confirmed',
        'title_ar': 'ادعاء مُعاد: ستُغلق مراكز الاقتراع مبكراً — غير مؤكد',
        'topic': 'election',
        'claim_type': 'unverified',
        'source_name': '',
        'source_url': '',
        'body': (
            'A forwarded message circulating in some groups claims that polling stations will close early. '
            'Civic Education RSS has not confirmed this from the electoral commission or any named official '
            'source. Do not change your voting plans based on this rumour. If an official body publishes a '
            'notice, it will appear here as a verified fact with the source named. Until then, treat this as '
            'unverified information.'
        ),
        'body_ar': (
            'تداولت بعض المجموعات رسالة مُعادة تدّعي أن مراكز الاقتراع ستُغلق مبكراً. '
            'لم تؤكد منصة التعليم المدني RSS ذلك من المفوضية الانتخابية أو من أي مصدر رسمي مسمّى. '
            'لا تغيّر خطط تصويتك بناءً على هذه الشائعة. إذا نشرت جهة رسمية إشعاراً، سيظهر هنا كحقيقة موثّقة '
            'مع ذكر المصدر. وحتى ذلك الحين، تعامل مع هذا كمعلومات غير موثّقة.'
        ),
    },
]

_JUBA = ZoneInfo('Africa/Juba')


def _event_at(year, month, day, hour=9, minute=0):
    return datetime(year, month, day, hour, minute, tzinfo=_JUBA)


DEMO_EVENTS = [
    {
        'title': 'Voter education briefing for upcoming county polls',
        'title_ar': 'جلسة تثقيف انتخابي لاستطلاعات المقاطعة المقبلة',
        'kind': 'election',
        'location': 'Juba Civic Centre',
        'location_ar': 'مركز جوبا المدني',
        'starts_at': _event_at(2026, 10, 15, 9, 0),
        'ends_at': _event_at(2026, 10, 15, 13, 0),
        'is_all_day': False,
        'allows_registration': True,
        'capacity': 80,
        'source_name': 'Civic Education RSS',
        'source_url': '',
        'description': (
            'A public briefing on how to register, what to bring on polling day, and how to report '
            'intimidation through lawful channels. This is civic education, not a campaign rally.'
        ),
        'description_ar': (
            'جلسة عامة عن كيفية التسجيل، وما يجب إحضاره يوم الاقتراع، وكيفية الإبلاغ عن الترهيب عبر القنوات '
            'القانونية. هذا تثقيف مدني وليس مهرجاناً انتخابياً.'
        ),
    },
    {
        'title': 'Public consultation on county participation rules',
        'title_ar': 'مشاورة عامة حول قواعد المشاركة في المقاطعة',
        'kind': 'public_consultation',
        'location': 'Ministry of Local Government hall, Juba',
        'location_ar': 'قاعة وزارة الحكم المحلي، جوبا',
        'starts_at': _event_at(2026, 9, 18, 10, 0),
        'ends_at': _event_at(2026, 9, 18, 12, 30),
        'is_all_day': False,
        'allows_registration': True,
        'capacity': 60,
        'source_name': 'Civic Education RSS',
        'source_url': '',
        'description': (
            'Citizens can comment on draft rules for public meetings and written submissions. Bring notes; '
            'speakers will be called in order of registration.'
        ),
        'description_ar': (
            'يمكن للمواطنين التعليق على مسودة قواعد الاجتماعات العامة والمذكرات المكتوبة. أحضر ملاحظاتك؛ '
            'يُستدعى المتحدثون حسب ترتيب التسجيل.'
        ),
    },
    {
        'title': 'Payam community meeting on local services',
        'title_ar': 'اجتماع مجتمع البايام حول الخدمات المحلية',
        'kind': 'community_meeting',
        'location': 'Munuki payam compound',
        'location_ar': 'مجمع بايام مونوكي',
        'starts_at': _event_at(2026, 9, 26, 15, 0),
        'ends_at': _event_at(2026, 9, 26, 17, 0),
        'is_all_day': False,
        'allows_registration': True,
        'capacity': 40,
        'source_name': 'Civic Education RSS',
        'source_url': '',
        'description': (
            'Neighbours meet chiefs and county officers to ask about water, schools, and how complaints '
            'are recorded. Open to residents of the payam.'
        ),
        'description_ar': (
            'يجتمع الجيران مع الزعماء ومسؤولي المقاطعة للسؤال عن المياه والمدارس وكيف تُسجَّل الشكاوى. '
            'الاجتماع مفتوح لسكان البايام.'
        ),
    },
    {
        'title': 'Workshop: reading the Transitional Constitution',
        'title_ar': 'ورشة: قراءة الدستور الانتقالي',
        'kind': 'workshop',
        'location': 'University of Juba, civic hall',
        'location_ar': 'جامعة جوبا، القاعة المدنية',
        'starts_at': _event_at(2026, 10, 8, 9, 30),
        'ends_at': _event_at(2026, 10, 8, 16, 0),
        'is_all_day': False,
        'allows_registration': True,
        'capacity': 50,
        'source_name': 'Civic Education RSS',
        'source_url': '',
        'description': (
            'A civic education workshop on rights, duties, and how the constitution limits public power. '
            'Handouts are available after the session.'
        ),
        'description_ar': (
            'ورشة تربية مدنية حول الحقوق والواجبات وكيف يحد الدستور من السلطة العامة. '
            'تتوفر النشرات بعد الجلسة.'
        ),
    },
    {
        'title': 'Independence Day',
        'title_ar': 'عيد الاستقلال',
        'kind': 'national_holiday',
        'location': 'Nationwide',
        'location_ar': 'في أنحاء البلاد',
        'starts_at': _event_at(2027, 7, 9, 0, 0),
        'ends_at': _event_at(2027, 7, 9, 23, 59),
        'is_all_day': True,
        'allows_registration': False,
        'capacity': None,
        'source_name': 'Republic of South Sudan',
        'source_url': '',
        'description': (
            'National holiday marking 9 July 2011. Public offices are typically closed. Set a reminder if you '
            'plan community celebrations or civic education activities.'
        ),
        'description_ar': (
            'عطلة وطنية تصادف 9 تموز/يوليو 2011. تُغلق المكاتب العامة عادة. عيّن تذكيراً إذا كنت تخطط '
            'لاحتفالات مجتمعية أو أنشطة تربية مدنية.'
        ),
    },
    {
        'title': 'County budget public hearing',
        'title_ar': 'جلسة استماع عامة لموازنة المقاطعة',
        'kind': 'public_hearing',
        'location': 'Central Equatoria County hall',
        'location_ar': 'قاعة مقاطعة الاستوائية الوسطى',
        'starts_at': _event_at(2026, 11, 12, 10, 0),
        'ends_at': _event_at(2026, 11, 12, 14, 0),
        'is_all_day': False,
        'allows_registration': True,
        'capacity': 100,
        'source_name': 'Civic Education RSS',
        'source_url': '',
        'description': (
            'A public hearing on the draft county budget. Residents may ask how funds for schools, health, '
            'and roads are allocated. Registration helps organizers plan seating and translation.'
        ),
        'description_ar': (
            'جلسة استماع عامة حول مشروع موازنة المقاطعة. يمكن للسكان السؤال عن تخصيص أموال المدارس والصحة '
            'والطرق. يساعد التسجيل المنظمين على ترتيب المقاعد والترجمة.'
        ),
    },
]

PUBLIC_ORG_SLUG = 'platform-demo'
PUBLIC_ORG_NAME = PLATFORM_NAME
PUBLIC_ORG_TAGLINE = 'Building informed citizens'

PLANS = [
    {
        'code': Plan.FREE,
        'name': 'Free',
        'price_cents': 0,
        'max_members': 5,
        'max_articles': 50,
        'max_quizzes': 5,
        'sort_order': 0,
        'features': {'support': 'community', 'analytics': False, 'tutor_daily_messages': 30, 'sms_alerts': False},
    },
    {
        'code': Plan.PRO,
        'name': 'Pro',
        'price_cents': 2900,
        'max_members': 50,
        'max_articles': 500,
        'max_quizzes': 50,
        'sort_order': 1,
        'features': {'support': 'email', 'analytics': True, 'tutor_daily_messages': 200, 'sms_alerts': True},
    },
    {
        'code': Plan.ENTERPRISE,
        'name': 'Enterprise',
        'price_cents': 9900,
        'max_members': None,
        'max_articles': None,
        'max_quizzes': None,
        'sort_order': 2,
        'features': {'support': 'priority', 'analytics': True, 'sso': True, 'tutor_daily_messages': None, 'sms_alerts': True},
    },
]


def resolve_constitution_attachment(entry: dict | None = None) -> tuple[str, str] | tuple[None, None]:
    """Prefer official PDF in seed_assets/ if present, else sample."""
    entry = entry or {}
    official = SEED_ASSETS_DIR / REAL_CONSTITUTION_FILE
    if official.is_file():
        return REAL_CONSTITUTION_FILE, entry.get(
            'attachment_name_official',
            'Transitional Constitution of South Sudan, 2011.pdf',
        )
    sample = SEED_ASSETS_DIR / SAMPLE_CONSTITUTION_FILE
    if sample.is_file():
        return SAMPLE_CONSTITUTION_FILE, entry.get(
            'attachment_name',
            'Transitional Constitution (Sample).pdf',
        )
    return None, None


def absolute_media_url(url: str) -> str:
    if url.startswith(('http://', 'https://')):
        return url
    return f"{settings.API_BASE_URL.rstrip('/')}{url}"


class Command(BaseCommand):
    help = 'Seed roles, billing plans, demo organization, categories, sample content, and admin user'

    def add_arguments(self, parser):
        parser.add_argument('--admin-email', default='admin@civic-education.ss')
        parser.add_argument('--admin-password', default='AdminPass123!')

    def _seed_article_attachment(self, org, article, asset_filename, attachment_name):
        asset_path = SEED_ASSETS_DIR / asset_filename
        if not asset_path.is_file():
            self.stdout.write(self.style.WARNING(f'Seed asset missing: {asset_filename}'))
            return

        storage_path = f'articles/{org.id}/seed-{asset_filename}'
        url = upload_file(storage_path, asset_path.read_bytes(), 'application/pdf')
        if not url:
            self.stdout.write(self.style.WARNING(f'Could not store attachment: {asset_filename}'))
            return

        url = absolute_media_url(url)
        if article.attachment_url == url and article.attachment_name == attachment_name:
            return

        article.attachment_url = url
        article.attachment_name = attachment_name
        article.save(update_fields=['attachment_url', 'attachment_name'])
        if asset_filename == REAL_CONSTITUTION_FILE:
            self.stdout.write(self.style.SUCCESS(f'Attachment (official PDF): {attachment_name}'))
        elif asset_filename == SAMPLE_CONSTITUTION_FILE:
            self.stdout.write(f'Attachment (sample PDF): {attachment_name}')
            self.stdout.write(
                self.style.WARNING(
                    f'Place the full constitution at seed_assets/{REAL_CONSTITUTION_FILE} and re-run seed_data.',
                ),
            )
        else:
            self.stdout.write(f'Attachment: {attachment_name}')

    def _upload_seed_bytes(self, org, filename, data, content_type):
        storage_path = f'articles/{org.id}/seed-{filename}'
        url = upload_file(storage_path, data, content_type)
        if not url:
            self.stdout.write(self.style.WARNING(f'Could not store seed file: {filename}'))
            return None
        return absolute_media_url(url)

    def _seed_quiz(self, org, admin, spec):
        quiz, created = Quiz.objects.get_or_create(
            organization=org,
            title=spec['title'],
            defaults={
                'title_ar': spec['title_ar'],
                'description': spec['description'],
                'description_ar': spec['description_ar'],
                'passing_score': spec['passing_score'],
                'kind': spec['kind'],
                'feedback_mode': spec['feedback_mode'],
                'is_active': True,
                'created_by': admin,
            },
        )
        if created:
            self.stdout.write(f'Quiz: {quiz.title}')
        else:
            quiz_updates = []
            for field in ('description', 'description_ar', 'kind', 'feedback_mode', 'passing_score'):
                value = spec[field]
                if getattr(quiz, field) != value:
                    setattr(quiz, field, value)
                    quiz_updates.append(field)
            if quiz_updates:
                quiz.save(update_fields=quiz_updates)
        existing_orders = set(quiz.questions.values_list('order', flat=True))
        added = 0
        for q_data in spec['questions']:
            if q_data['order'] not in existing_orders:
                Question.objects.create(quiz=quiz, **q_data)
                added += 1
            else:
                question = quiz.questions.filter(order=q_data['order']).first()
                if not question:
                    continue
                updates = []
                if not question.explanation and q_data.get('explanation'):
                    question.explanation = q_data['explanation']
                    question.explanation_ar = q_data.get('explanation_ar', '')
                    updates.extend(['explanation', 'explanation_ar'])
                if not question.option_feedback and q_data.get('option_feedback'):
                    question.option_feedback = q_data['option_feedback']
                    updates.append('option_feedback')
                if q_data.get('question_type') and question.question_type != q_data['question_type']:
                    question.question_type = q_data['question_type']
                    updates.append('question_type')
                if updates:
                    question.save(update_fields=updates)
        if added:
            self.stdout.write(f'Quiz questions added ({quiz.title}): {added}')

    def _seed_awareness_articles(self, org, admin, now):
        category = Category.objects.filter(organization=org, slug='media-misinformation').first()
        if category is None:
            self.stdout.write(self.style.WARNING('Awareness articles skipped: media-misinformation category missing'))
            return
        for spec in AWARENESS_ARTICLES:
            article, created = Article.objects.get_or_create(
                organization=org,
                title=spec['title'],
                defaults={
                    'title_ar': spec['title_ar'],
                    'content': spec['content'],
                    'content_ar': spec['content_ar'],
                    'category': category,
                    'author': admin,
                    'tags': spec['tags'],
                    'status': 'published',
                    'published_at': now,
                },
            )
            if created:
                self.stdout.write(f'Awareness article: {article.title}')

    def _seed_curriculum(self, org, admin, now):
        catalog_by_slug = {item['slug']: item for item in CURRICULUM_CATEGORIES}
        categories_by_slug = {}
        for item in CURRICULUM_CATEGORIES:
            category, _ = Category.objects.get_or_create(
                organization=org,
                slug=item['slug'],
                defaults={
                    'name': item['name'],
                    'name_ar': item['name_ar'],
                    'description': item['description'],
                    'description_ar': item['description_ar'],
                    'is_locked': True,
                },
            )
            fields = {
                'name': item['name'],
                'name_ar': item['name_ar'],
                'description': item['description'],
                'description_ar': item['description_ar'],
                'is_locked': True,
            }
            updates = [key for key, value in fields.items() if getattr(category, key) != value]
            if updates:
                for key in updates:
                    setattr(category, key, fields[key])
                category.save(update_fields=updates)
            categories_by_slug[item['slug']] = category
            self.stdout.write(f'Category: {item["name"]}')

        constitution_body = load_constitution_text()
        for entry in LESSONS:
            slug = entry['slug']
            catalog = catalog_by_slug[slug]
            category = categories_by_slug[slug]
            content = entry['content']
            content_ar = entry['content_ar']
            if entry.get('load_constitution_text') and constitution_body:
                content = CONSTITUTION_INTRO + constitution_body
                content_ar = CONSTITUTION_INTRO_AR + constitution_body

            article_defaults = {
                'title_ar': entry['title_ar'],
                'content': content,
                'content_ar': content_ar,
                'category': category,
                'author': admin,
                'tags': entry['tags'],
                'status': 'published',
                'published_at': now,
                'is_controlled_document': entry.get('is_controlled_document', False),
                'document_label': entry.get('document_label', ''),
                'attachment_version': entry.get('attachment_version', ''),
            }
            article, article_created = Article.objects.get_or_create(
                organization=org,
                title=entry['title'],
                defaults=article_defaults,
            )
            if article_created:
                self.stdout.write(f'Article: {entry["title"]}')
            else:
                changed = []
                for field, value in article_defaults.items():
                    if field in ('author', 'published_at'):
                        continue
                    if getattr(article, field) != value:
                        setattr(article, field, value)
                        changed.append(field)
                if changed:
                    article.save(update_fields=changed)
                    self.stdout.write(f'Article updated: {article.title}')

            if entry.get('keep_official_pdf'):
                resolved_file, resolved_name = resolve_constitution_attachment(entry)
                if resolved_file:
                    self._seed_article_attachment(org, article, resolved_file, resolved_name)
            else:
                pdf_bytes = build_handout_pdf(entry['title'], entry.get('facts', []))
                pdf_url = self._upload_seed_bytes(
                    org, f'handout-{slug}.pdf', pdf_bytes, 'application/pdf',
                )
                handout_name = f'{entry["title"]} — learner handout.pdf'
                if pdf_url and (
                    article.attachment_url != pdf_url or article.attachment_name != handout_name
                ):
                    article.attachment_url = pdf_url
                    article.attachment_name = handout_name
                    article.save(update_fields=['attachment_url', 'attachment_name'])
                    self.stdout.write(f'Attachment (handout): {handout_name}')

            svg_bytes = build_topic_svg(catalog['name'], catalog['description'][:90])
            image_url = self._upload_seed_bytes(
                org, f'infographic-{slug}.svg', svg_bytes, 'image/svg+xml',
            )
            if image_url and len(image_url) <= 200 and article.featured_image_url != image_url:
                article.featured_image_url = image_url
                article.save(update_fields=['featured_image_url'])

            self._seed_lesson_media(org, admin, category, article, entry, catalog, now)

            if entry.get('load_constitution_text'):
                if constitution_body:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Constitution text ready for AI tutor ({len(constitution_body):,} chars).'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Place full text at seed_assets/{CONSTITUTION_TEXT_FILE} '
                            'so the AI tutor can cite the constitution.'
                        )
                    )

    def _seed_lesson_media(self, org, admin, category, article, entry, catalog, now):
        audio_title = entry.get('audio_title') or f"Audio lesson: {catalog['name']}"
        audio_title_ar = entry.get('audio_title_ar') or f"درس صوتي: {catalog['name_ar']}"
        video_title = entry.get('video_title') or f"Video lesson: {catalog['name']}"
        video_title_ar = entry.get('video_title_ar') or f"درس فيديو: {catalog['name_ar']}"

        audio, audio_created = MediaAsset.objects.get_or_create(
            organization=org,
            title=audio_title,
            defaults={
                'title_ar': audio_title_ar,
                'description': f'A short spoken introduction to {catalog["name"]}.',
                'description_ar': f'مقدمة صوتية قصيرة عن {catalog["name_ar"]}.',
                'media_type': MediaAsset.TYPE_AUDIO,
                'source': MediaAsset.SOURCE_EXTERNAL,
                'external_url': CURRICULUM_AUDIO_URL,
                'category': category,
                'status': 'published',
                'published_at': now,
                'author': admin,
            },
        )
        if audio_created:
            self.stdout.write(f'Media: {audio_title}')

        video, video_created = MediaAsset.objects.get_or_create(
            organization=org,
            title=video_title,
            defaults={
                'title_ar': video_title_ar,
                'description': f'A video explainer on {catalog["name"]}.',
                'description_ar': f'شرح بالفيديو عن {catalog["name_ar"]}.',
                'media_type': MediaAsset.TYPE_VIDEO,
                'source': MediaAsset.SOURCE_EXTERNAL,
                'external_url': CURRICULUM_VIDEO_URL,
                'category': category,
                'status': 'published',
                'published_at': now,
                'author': admin,
            },
        )
        if video_created:
            self.stdout.write(f'Media: {video_title}')

        media_updates = []
        if article.audio_media_id != audio.id:
            article.audio_media = audio
            media_updates.append('audio_media')
        if article.video_media_id != video.id:
            article.video_media = video
            media_updates.append('video_media')
        if media_updates:
            media_updates.append('updated_at')
            article.save(update_fields=media_updates)

    def handle(self, *args, **options):
        for role_name in ROLES:
            Role.objects.get_or_create(name=role_name)
            self.stdout.write(f'Role: {role_name}')

        for entry in PLANS:
            code = entry['code']
            defaults = {k: v for k, v in entry.items() if k != 'code'}
            Plan.objects.update_or_create(code=code, defaults=defaults)
            self.stdout.write(f'Plan: {code}')

        admin_role = Role.objects.get(name='super_admin')
        admin, created = User.objects.get_or_create(
            email=options['admin_email'],
            defaults={
                'first_name': 'Platform',
                'last_name': 'Admin',
                'role': admin_role,
                'is_staff': True,
                'is_superuser': True,
                'email_verified': True,
            },
        )
        if created:
            admin.set_password(options['admin_password'])
            admin.save()
            self.stdout.write(self.style.SUCCESS(f'Super Admin created: {admin.email}'))
        else:
            if admin.role_id != admin_role.id or not admin.is_superuser:
                admin.role = admin_role
                admin.is_staff = True
                admin.is_superuser = True
                admin.save(update_fields=['role', 'is_staff', 'is_superuser'])
            self.stdout.write(f'Super Admin already exists: {admin.email}')

        from apps.core.constants import DEFAULT_PRIMARY_COLOR, LEGACY_BLUE_PRIMARY_COLORS
        from apps.tenants.models import Membership, Organization

        org = Organization.objects.filter(slug=PUBLIC_ORG_SLUG).first()
        if org is None:
            org = create_organization_with_owner(
                name=PUBLIC_ORG_NAME,
                owner=admin,
                slug=PUBLIC_ORG_SLUG,
            )
            org.tagline = PUBLIC_ORG_TAGLINE
            org.primary_color = DEFAULT_PRIMARY_COLOR
            org.save(update_fields=['tagline', 'primary_color'])
            self.stdout.write(self.style.SUCCESS(f'Organization: {org.slug}'))
        else:
            org_updates = []
            if org.name != PUBLIC_ORG_NAME:
                org.name = PUBLIC_ORG_NAME
                org_updates.append('name')
            if org.tagline != PUBLIC_ORG_TAGLINE:
                org.tagline = PUBLIC_ORG_TAGLINE
                org_updates.append('tagline')
            if org.primary_color.lower() in LEGACY_BLUE_PRIMARY_COLORS:
                org.primary_color = DEFAULT_PRIMARY_COLOR
                org_updates.append('primary_color')
            if org_updates:
                org.save(update_fields=org_updates)
            self.stdout.write(f'Organization already exists: {org.slug}')

        enterprise = Plan.objects.filter(code=Plan.ENTERPRISE).first()
        if enterprise:
            Subscription.objects.update_or_create(
                organization=org,
                defaults={'plan': enterprise, 'status': Subscription.ACTIVE},
            )

        now = timezone.now()
        self._seed_curriculum(org, admin, now)
        self._seed_quiz(org, admin, DEMO_QUIZ)
        self._seed_quiz(org, admin, DEMO_SCENARIO_QUIZ)
        self._seed_quiz(org, admin, DEMO_FACT_FICTION_QUIZ)
        self._seed_awareness_articles(org, admin, now)

        topic, topic_created = DiscussionTopic.objects.get_or_create(
            organization=org,
            title=DEMO_FORUM['title'],
            defaults={
                'content': DEMO_FORUM['content'],
                'author': admin,
                'is_approved': True,
                'kind': DiscussionTopic.KIND_DISCUSSION,
                'board': DEMO_FORUM['board'],
            },
        )
        if topic.kind != DiscussionTopic.KIND_DISCUSSION or topic.board != DEMO_FORUM['board']:
            topic.kind = DiscussionTopic.KIND_DISCUSSION
            topic.board = DEMO_FORUM['board']
            topic.save(update_fields=['kind', 'board'])
        if topic_created:
            self.stdout.write(f'Forum topic: {topic.title}')
        if not topic.comments.exists():
            DiscussionComment.objects.create(
                organization=org,
                topic=topic,
                author=admin,
                comment=DEMO_FORUM['comment'],
                is_approved=True,
                is_expert=True,
            )
            self.stdout.write('Forum comment: seeded')

        question, question_created = DiscussionTopic.objects.get_or_create(
            organization=org,
            title=DEMO_FORUM_QUESTION['title'],
            defaults={
                'content': DEMO_FORUM_QUESTION['content'],
                'author': admin,
                'is_approved': True,
                'kind': DiscussionTopic.KIND_QUESTION,
                'board': DEMO_FORUM_QUESTION['board'],
            },
        )
        if (
            question.kind != DiscussionTopic.KIND_QUESTION
            or question.board != DEMO_FORUM_QUESTION['board']
        ):
            question.kind = DiscussionTopic.KIND_QUESTION
            question.board = DEMO_FORUM_QUESTION['board']
            question.save(update_fields=['kind', 'board'])
        if question_created:
            self.stdout.write(f'Forum question: {question.title}')
        answer = question.comments.filter(comment=DEMO_FORUM_QUESTION['comment']).first()
        if answer is None:
            answer = DiscussionComment.objects.create(
                organization=org,
                topic=question,
                author=admin,
                comment=DEMO_FORUM_QUESTION['comment'],
                is_approved=True,
                is_expert=True,
            )
            self.stdout.write('Forum expert answer: seeded')
        elif not answer.is_expert:
            answer.is_expert = True
            answer.save(update_fields=['is_expert'])
        if question.accepted_answer_id != answer.id:
            question.accepted_answer = answer
            question.save(update_fields=['accepted_answer'])

        self._seed_gamification_and_engagement(org, admin)
        self._seed_civic_news(org, admin, now)
        self._seed_civic_events(org, admin)
        self._seed_courses(org, admin)
        self.stdout.write(self.style.SUCCESS('Seed complete.'))

    def _seed_gamification_and_engagement(self, org, admin):
        from apps.engagement.models import Campaign, Petition, Poll, PollOption
        from apps.gamification.models import Badge

        badges = [
            ('first_steps', 'First Steps', 'أول خطوات', 'Earn your first 25 XP', 'star', 25, 1),
            ('article_reader', 'Article Reader', 'قارئ المقالات', 'Complete your first article', 'book', 0, 2),
            ('media_listener', 'Media Listener', 'مستمع', 'Complete your first media lesson', 'headphones', 0, 3),
            ('quiz_starter', 'Quiz Starter', 'بداية الاختبار', 'Attempt your first quiz', 'clipboard', 0, 4),
            ('quiz_champion', 'Quiz Champion', 'بطل الاختبارات', 'Pass three quizzes', 'trophy', 0, 5),
            ('civic_voice', 'Civic Voice', 'صوت مدني', 'Vote in a poll or sign a petition', 'megaphone', 0, 6),
            ('engaged_citizen', 'Engaged Citizen', 'مواطن مشارك', 'Reach 100 XP', 'medal', 100, 7),
            ('constitution_scholar', 'Constitution Scholar', 'دارس الدستور', 'Complete a constitution article', 'scroll', 0, 8),
        ]
        for slug, name, name_ar, desc, icon, xp_req, order in badges:
            Badge.objects.get_or_create(
                organization=org,
                slug=slug,
                defaults={
                    'name': name,
                    'name_ar': name_ar,
                    'description': desc,
                    'icon': icon,
                    'xp_required': xp_req,
                    'sort_order': order,
                },
            )

        polls = []
        for spec in DEMO_POLLS:
            poll, created = Poll.objects.get_or_create(
                organization=org,
                question=spec['question'],
                defaults={
                    'question_ar': spec['question_ar'],
                    'description': spec['description'],
                    'description_ar': spec['description_ar'],
                    'kind': spec['kind'],
                    'status': Poll.STATUS_OPEN,
                    'created_by': admin,
                },
            )
            if poll.kind != spec['kind'] or poll.description != spec['description']:
                poll.kind = spec['kind']
                poll.description = spec['description']
                poll.description_ar = spec['description_ar']
                poll.question_ar = spec['question_ar']
                poll.save(update_fields=['kind', 'description', 'description_ar', 'question_ar'])
            if created or not poll.options.exists():
                PollOption.objects.filter(poll=poll).delete()
                for idx, (label, label_ar) in enumerate(spec['options']):
                    PollOption.objects.create(
                        organization=org,
                        poll=poll,
                        label=label,
                        label_ar=label_ar,
                        sort_order=idx,
                    )
            polls.append(poll)

        self._seed_demo_poll_votes(org, polls)

        Petition.objects.get_or_create(
            organization=org,
            title='Support civic education in every county',
            defaults={
                'title_ar': 'دعم التعليم المدني في كل مقاطعة',
                'description': 'Join citizens calling for accessible civic education resources nationwide.',
                'description_ar': 'انضم إلى المواطنين الذين يطالبون بموارد تعليم مدني في جميع أنحاء البلاد.',
                'goal_signatures': 500,
                'status': Petition.STATUS_OPEN,
                'created_by': admin,
            },
        )

        Campaign.objects.get_or_create(
            organization=org,
            title='Register to vote',
            defaults={
                'title_ar': 'سجّل للتصويت',
                'description': 'Check your voter registration status before the next election.',
                'description_ar': 'تحقق من حالة تسجيلك الناخب قبل الانتخابات القادمة.',
                'link_url': 'https://example.org/voter-registration',
                'status': Campaign.STATUS_ACTIVE,
                'created_by': admin,
            },
            )

    def _seed_demo_poll_votes(self, org, polls):
        from django.db.models import F

        from apps.accounts.models import UserProfile
        from apps.engagement.models import PollOption, PollVote
        from apps.tenants.models import Membership

        voter_specs = [
            ('seed-poll-a@civic-education.ss', 'Asha', 'Deng', 'central_equatoria', '18_24'),
            ('seed-poll-b@civic-education.ss', 'John', 'Lual', 'central_equatoria', '25_34'),
            ('seed-poll-c@civic-education.ss', 'Mary', 'Keji', 'central_equatoria', '35_49'),
            ('seed-poll-d@civic-education.ss', 'Peter', 'Gatluak', 'jonglei', '18_24'),
            ('seed-poll-e@civic-education.ss', 'Grace', 'Nyibol', 'jonglei', '25_34'),
            ('seed-poll-f@civic-education.ss', 'James', 'Wani', 'western_equatoria', '35_49'),
            ('seed-poll-g@civic-education.ss', 'Agnes', 'Ajok', 'upper_nile', '50_plus'),
            ('seed-poll-h@civic-education.ss', 'Daniel', 'Makuach', 'lakes', '25_34'),
        ]
        voters = []
        for email, first_name, last_name, region, age_band in voter_specs:
            user = User.objects.filter(email=email).first()
            if user is None:
                user = User.objects.create_user(
                    email=email,
                    password=None,
                    first_name=first_name,
                    last_name=last_name,
                )
                user.set_unusable_password()
                user.save(update_fields=['password'])
            profile, _ = UserProfile.objects.get_or_create(user=user)
            if profile.region != region or profile.age_band != age_band:
                profile.region = region
                profile.age_band = age_band
                profile.save(update_fields=['region', 'age_band'])
            Membership.objects.get_or_create(
                organization=org,
                user=user,
                defaults={'role': Membership.MEMBER},
            )
            voters.append((user, region, age_band))

        for poll in polls:
            options = list(poll.options.order_by('sort_order', 'label'))
            if not options:
                continue
            for index, (user, region, age_band) in enumerate(voters):
                option = options[index % len(options)]
                vote, created = PollVote.objects.get_or_create(
                    organization=org,
                    poll=poll,
                    user=user,
                    defaults={
                        'option': option,
                        'region': region,
                        'age_band': age_band,
                    },
                )
                if created:
                    PollOption.objects.filter(id=option.id).update(vote_count=F('vote_count') + 1)
                elif vote.region != region or vote.age_band != age_band:
                    vote.region = region
                    vote.age_band = age_band
                    vote.save(update_fields=['region', 'age_band'])

    def _seed_civic_news(self, org, admin, now):
        from apps.engagement.models import CivicNews

        for spec in DEMO_NEWS:
            item, created = CivicNews.objects.get_or_create(
                organization=org,
                title=spec['title'],
                defaults={
                    'title_ar': spec['title_ar'],
                    'body': spec['body'],
                    'body_ar': spec['body_ar'],
                    'topic': spec['topic'],
                    'claim_type': spec['claim_type'],
                    'source_name': spec['source_name'],
                    'source_url': spec['source_url'],
                    'status': CivicNews.STATUS_PUBLISHED,
                    'published_at': now,
                    'created_by': admin,
                },
            )
            if created:
                self.stdout.write(f'Civic news: {item.title}')

    def _seed_civic_events(self, org, admin):
        from apps.engagement.models import CivicEvent

        for spec in DEMO_EVENTS:
            item, created = CivicEvent.objects.get_or_create(
                organization=org,
                title=spec['title'],
                defaults={
                    'title_ar': spec['title_ar'],
                    'description': spec['description'],
                    'description_ar': spec['description_ar'],
                    'location': spec['location'],
                    'location_ar': spec['location_ar'],
                    'kind': spec['kind'],
                    'starts_at': spec['starts_at'],
                    'ends_at': spec['ends_at'],
                    'is_all_day': spec['is_all_day'],
                    'allows_registration': spec['allows_registration'],
                    'capacity': spec['capacity'],
                    'source_name': spec['source_name'],
                    'source_url': spec['source_url'],
                    'status': CivicEvent.STATUS_PUBLISHED,
                    'created_by': admin,
                },
            )
            if created:
                self.stdout.write(f'Civic event: {item.title}')

    def _seed_courses(self, org, admin):
        from apps.learning.curriculum import CURRICULUM_CATEGORIES
        from apps.learning.models import Article, Category, Course, CourseLesson

        for spec in CURRICULUM_CATEGORIES:
            category = Category.objects.filter(organization=org, slug=spec['slug']).first()
            if category is None:
                continue
            articles = list(
                Article.objects.filter(
                    organization=org,
                    category=category,
                    status='published',
                ).order_by('created_at', 'title')
            )
            if not articles:
                continue
            course, created = Course.objects.get_or_create(
                organization=org,
                slug=spec['slug'],
                defaults={
                    'title': spec['name'],
                    'title_ar': spec.get('name_ar') or '',
                    'description': spec.get('description') or '',
                    'description_ar': spec.get('description_ar') or '',
                    'status': Course.STATUS_PUBLISHED,
                    'created_by': admin,
                },
            )
            if not course.lessons.exists():
                for idx, article in enumerate(articles):
                    CourseLesson.objects.create(
                        organization=org,
                        course=course,
                        article=article,
                        sort_order=idx,
                    )
            if created:
                self.stdout.write(f'Course: {course.title}')
