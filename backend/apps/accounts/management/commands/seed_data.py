from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from pathlib import Path

from apps.accounts.models import Role
from apps.billing.models import Plan, Subscription
from apps.core.storage import upload_file
from apps.forum.models import DiscussionComment, DiscussionTopic
from apps.learning.models import Article, Category
from apps.quizzes.models import Question, Quiz
from apps.tenants.services import create_organization_with_owner

User = get_user_model()

ROLES = ['citizen', 'moderator', 'editor', 'admin']

CATEGORIES = [
    ('constitution', 'Constitution', 'الدستور'),
    ('governance', 'Governance', 'الحكم'),
    ('elections', 'Elections', 'الانتخابات'),
    ('peacebuilding', 'Peacebuilding', 'بناء السلام'),
]

REAL_CONSTITUTION_FILE = 'transitional-constitution.pdf'
SAMPLE_CONSTITUTION_FILE = 'transitional-constitution-sample.pdf'
SEED_ASSETS_DIR = Path(__file__).resolve().parent / 'seed_assets'

DEMO_ARTICLES = [
    {
        'category_slug': 'constitution',
        'title': 'Understanding the Transitional Constitution',
        'title_ar': 'فهم الدستور الانتقالي',
        'content': (
            'The Transitional Constitution defines the structure of government, '
            'fundamental rights, and the roadmap toward a permanent constitution. '
            'Citizens should know how laws are made and how institutions check one another. '
            'Download the sample PDF attachment for the full document text.'
        ),
        'content_ar': (
            'يحدد الدستور الانتقالي هيكل الحكومة والحقوق الأساسية '
            'والطريق نحو دستور دائم. يجب أن يعرف المواطنون كيف تُصنع القوانين '
            'وكيف تراقب المؤسسات بعضها بعضاً. '
            'حمّل مرفق PDF النموذجي للاطلاع على نص الوثيقة كاملاً.'
        ),
        'tags': ['constitution', 'rights'],
        'attachment_asset': SAMPLE_CONSTITUTION_FILE,
        'attachment_name': 'Transitional Constitution (Sample).pdf',
        'attachment_name_official': 'Transitional Constitution.pdf',
    },
    {
        'category_slug': 'governance',
        'title': 'How Local Government Works',
        'title_ar': 'كيف تعمل الحكومة المحلية',
        'content': (
            'States and counties deliver services such as education coordination, '
            'local security cooperation, and community development. '
            'Participating in local meetings is a practical form of civic engagement.'
        ),
        'content_ar': (
            'تقدم الولايات والمقاطعات خدمات مثل تنسيق التعليم '
            'والتعاون الأمني المحلي والتنمية المجتمعية. '
            'المشاركة في الاجتماعات المحلية شكل عملي من المشاركة المدنية.'
        ),
        'tags': ['governance', 'local'],
    },
    {
        'category_slug': 'elections',
        'title': 'Your Role in Free and Fair Elections',
        'title_ar': 'دورك في انتخابات حرة ونزيهة',
        'content': (
            'Elections depend on informed voters, transparent processes, and peaceful participation. '
            'Register, verify your polling station, and report irregularities through official channels.'
        ),
        'content_ar': (
            'تعتمد الانتخابات على ناخبين واعين وعمليات شفافة ومشاركة سلمية. '
            'سجّل، تحقق من مركز الاقتراع، وأبلغ عن المخالفات عبر القنوات الرسمية.'
        ),
        'tags': ['elections', 'voting'],
    },
]

DEMO_QUIZ = {
    'title': 'South Sudan Civic Basics',
    'title_ar': 'أساسيات المواطنة في جنوب السودان',
    'description': 'A short quiz covering constitution, governance, and civic participation.',
    'description_ar': 'اختبار قصير يغطي الدستور والحكم والمشاركة المدنية.',
    'passing_score': 70,
    'questions': [
        {
            'question_text': 'What document defines the structure of national government during the transition?',
            'question_text_ar': 'ما الوثيقة التي تحدد هيكل الحكومة الوطنية خلال الفترة الانتقالية؟',
            'question_type': Question.MCQ,
            'options': ['Transitional Constitution', 'County charter', 'Party manifesto', 'UN resolution'],
            'options_ar': ['الدستور الانتقالي', 'ميثاق المقاطعة', 'بيان الحزب', 'قرار الأمم المتحدة'],
            'correct_answer': 'Transitional Constitution',
            'points': 1,
            'order': 0,
        },
        {
            'question_text': 'Peaceful participation in elections is a civic duty.',
            'question_text_ar': 'المشاركة السلمية في الانتخابات واجب مدني.',
            'question_type': Question.TRUE_FALSE,
            'options': ['True', 'False'],
            'options_ar': [],
            'correct_answer': 'True',
            'points': 1,
            'order': 1,
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
}

PUBLIC_ORG_SLUG = 'platform-demo'
PUBLIC_ORG_NAME = 'Civic Education Platform'
PUBLIC_ORG_TAGLINE = 'Building informed citizens of South Sudan'

PLANS = [
    {
        'code': Plan.FREE,
        'name': 'Free',
        'price_cents': 0,
        'max_members': 5,
        'max_articles': 10,
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


def resolve_constitution_attachment(entry: dict) -> tuple[str, str] | tuple[None, None]:
    """Prefer official PDF in seed_assets/ if present, else sample."""
    if not entry.get('attachment_asset'):
        return None, None
    official = SEED_ASSETS_DIR / REAL_CONSTITUTION_FILE
    if official.is_file():
        return REAL_CONSTITUTION_FILE, entry.get('attachment_name_official', 'Transitional Constitution.pdf')
    sample = SEED_ASSETS_DIR / SAMPLE_CONSTITUTION_FILE
    if sample.is_file():
        return SAMPLE_CONSTITUTION_FILE, entry.get('attachment_name', 'Transitional Constitution (Sample).pdf')
    asset = entry.get('attachment_asset')
    return asset, entry.get('attachment_name', asset)


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

    def handle(self, *args, **options):
        for role_name in ROLES:
            Role.objects.get_or_create(name=role_name)
            self.stdout.write(f'Role: {role_name}')

        for entry in PLANS:
            code = entry['code']
            defaults = {k: v for k, v in entry.items() if k != 'code'}
            Plan.objects.update_or_create(code=code, defaults=defaults)
            self.stdout.write(f'Plan: {code}')

        admin_role = Role.objects.get(name='admin')
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
            self.stdout.write(self.style.SUCCESS(f'Admin created: {admin.email}'))
        else:
            self.stdout.write(f'Admin already exists: {admin.email}')

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

        categories_by_slug = {}
        for slug, name, name_ar in CATEGORIES:
            category, _ = Category.objects.get_or_create(
                organization=org,
                slug=slug,
                defaults={'name': name, 'name_ar': name_ar},
            )
            categories_by_slug[slug] = category
            self.stdout.write(f'Category: {name}')

        now = timezone.now()
        for entry in DEMO_ARTICLES:
            category = categories_by_slug[entry['category_slug']]
            article_defaults = {
                'title_ar': entry['title_ar'],
                'content': entry['content'],
                'content_ar': entry['content_ar'],
                'category': category,
                'author': admin,
                'tags': entry['tags'],
                'status': 'published',
                'published_at': now,
            }
            article, article_created = Article.objects.get_or_create(
                organization=org,
                title=entry['title'],
                defaults=article_defaults,
            )
            if article_created:
                self.stdout.write(f'Article: {entry["title"]}')

            asset_filename = entry.get('attachment_asset')
            if asset_filename:
                resolved_file, resolved_name = resolve_constitution_attachment(entry)
                if resolved_file:
                    self._seed_article_attachment(org, article, resolved_file, resolved_name)

        quiz, quiz_created = Quiz.objects.get_or_create(
            organization=org,
            title=DEMO_QUIZ['title'],
            defaults={
                'title_ar': DEMO_QUIZ['title_ar'],
                'description': DEMO_QUIZ['description'],
                'description_ar': DEMO_QUIZ['description_ar'],
                'passing_score': DEMO_QUIZ['passing_score'],
                'is_active': True,
                'created_by': admin,
            },
        )
        if quiz_created:
            self.stdout.write(f'Quiz: {quiz.title}')
        if not quiz.questions.exists():
            for q_data in DEMO_QUIZ['questions']:
                Question.objects.create(quiz=quiz, **q_data)
            self.stdout.write(f'Quiz questions: {quiz.questions.count()}')

        topic, topic_created = DiscussionTopic.objects.get_or_create(
            organization=org,
            title=DEMO_FORUM['title'],
            defaults={
                'content': DEMO_FORUM['content'],
                'author': admin,
                'is_approved': True,
            },
        )
        if topic_created:
            self.stdout.write(f'Forum topic: {topic.title}')
        if not topic.comments.exists():
            DiscussionComment.objects.create(
                organization=org,
                topic=topic,
                author=admin,
                comment=DEMO_FORUM['comment'],
                is_approved=True,
            )
            self.stdout.write('Forum comment: seeded')

        self.stdout.write(self.style.SUCCESS('Seed complete.'))
