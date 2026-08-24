"""Award XP and badges for learner milestones."""

from __future__ import annotations

from apps.accounts.models import UserProfile
from apps.tenants.context import get_current_organization

from .models import Badge, UserBadge

XP_ARTICLE_COMPLETE = 25
XP_MEDIA_COMPLETE = 20
XP_QUIZ_ATTEMPT = 10
XP_QUIZ_PASS = 50
XP_POLL_VOTE = 5
XP_PETITION_SIGN = 10
XP_CAMPAIGN_JOIN = 5


def award_xp(user, amount: int, *, reason: str = '') -> int:
    if amount <= 0 or user is None:
        return 0
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.xp_points = (profile.xp_points or 0) + amount
    profile.save(update_fields=['xp_points'])
    evaluate_badges(user)
    return profile.xp_points


def evaluate_badges(user) -> list[str]:
    """Grant badges the user qualifies for but has not earned yet."""
    organization = get_current_organization()
    if organization is None:
        return []

    profile = UserProfile.objects.filter(user=user).first()
    xp = profile.xp_points if profile else 0

    from apps.engagement.models import PetitionSignature, PollVote
    from apps.learning.models import ArticleProgress, MediaProgress
    from apps.quizzes.models import QuizAttempt

    articles_done = ArticleProgress.objects.filter(user=user, completed=True).count()
    media_done = MediaProgress.objects.filter(user=user, completed=True).count()
    quiz_attempts = QuizAttempt.objects.filter(user=user).count()
    quizzes_passed = QuizAttempt.objects.filter(user=user, passed=True).count()
    poll_votes = PollVote.objects.filter(user=user).count()
    petition_signs = PetitionSignature.objects.filter(user=user).count()

    checks: dict[str, bool] = {
        'first_steps': xp >= 25,
        'article_reader': articles_done >= 1,
        'media_listener': media_done >= 1,
        'quiz_starter': quiz_attempts >= 1,
        'quiz_champion': quizzes_passed >= 3,
        'civic_voice': poll_votes >= 1 or petition_signs >= 1,
        'engaged_citizen': xp >= 100,
        'constitution_scholar': ArticleProgress.objects.filter(
            user=user,
            completed=True,
            article__category__slug='constitution',
        ).exists(),
    }

    earned_slugs: list[str] = []
    badges = Badge.objects.filter(organization=organization)
    existing = set(
        UserBadge.objects.filter(user=user, organization=organization)
        .values_list('badge_id', flat=True)
    )

    for badge in badges:
        if badge.id in existing:
            continue
        qualified = checks.get(badge.slug, False) or xp >= badge.xp_required
        if not qualified:
            continue
        UserBadge.objects.create(
            organization=organization,
            user=user,
            badge=badge,
        )
        earned_slugs.append(badge.slug)

    return earned_slugs


def build_gamification_summary(user) -> dict:
    organization = get_current_organization()
    profile = UserProfile.objects.filter(user=user).first()
    xp = profile.xp_points if profile else 0
    level = max(1, 1 + xp // 100)

    badges_qs = UserBadge.objects.filter(user=user).select_related('badge')
    if organization is not None:
        badges_qs = badges_qs.filter(organization=organization)

    badges = [
        {
            'slug': row.badge.slug,
            'name': row.badge.name,
            'name_ar': row.badge.name_ar,
            'description': row.badge.description,
            'icon': row.badge.icon,
            'earned_at': row.earned_at,
        }
        for row in badges_qs.order_by('-earned_at')
    ]

    available = []
    if organization is not None:
        earned_ids = {b['slug'] for b in badges}
        for badge in Badge.objects.filter(organization=organization).order_by('sort_order'):
            if badge.slug in earned_ids:
                continue
            available.append({
                'slug': badge.slug,
                'name': badge.name,
                'name_ar': badge.name_ar,
                'description': badge.description,
                'icon': badge.icon,
                'xp_required': badge.xp_required,
            })

    return {
        'xp_points': xp,
        'level': level,
        'xp_to_next_level': (level * 100) - xp,
        'badges_earned': badges,
        'badges_available': available,
    }


def _display_name(user) -> str:
    first = (user.first_name or '').strip()
    last = (user.last_name or '').strip()
    if first and last:
        return f'{first} {last[0]}.'
    if first:
        return first
    if last:
        return last
    return 'Learner'


def build_leaderboard(user, *, limit: int = 20) -> dict:
    organization = get_current_organization()
    if organization is None:
        return {'entries': [], 'me': None, 'total_ranked': 0}

    from django.contrib.auth import get_user_model

    User = get_user_model()
    members = list(
        User.objects.filter(
            memberships__organization=organization,
            is_active=True,
        ).distinct()
    )
    profiles = {
        profile.user_id: profile
        for profile in UserProfile.objects.filter(user__in=members)
    }

    ranked = []
    for member in members:
        profile = profiles.get(member.id)
        xp = profile.xp_points if profile else 0
        badge_count = UserBadge.objects.filter(user=member, organization=organization).count()
        ranked.append({
            'user_id': str(member.id),
            'display_name': _display_name(member),
            'xp_points': xp,
            'level': max(1, 1 + xp // 100),
            'badges_earned': badge_count,
            'show': bool(profile.show_on_leaderboard) if profile else True,
            'is_me': member.id == user.id,
        })
    ranked.sort(key=lambda row: (-row['xp_points'], row['display_name'].lower()))
    for index, row in enumerate(ranked, start=1):
        row['rank'] = index

    me = next((row for row in ranked if row['is_me']), None)
    public = [row for row in ranked if row['show'] or row['is_me']]
    entries = []
    for row in public[: max(1, min(limit, 100))]:
        entries.append({k: v for k, v in row.items() if k != 'show'})
    me_payload = None
    if me:
        me_payload = {k: v for k, v in me.items() if k != 'show'}
    return {
        'entries': entries,
        'me': me_payload,
        'total_ranked': len(ranked),
    }
