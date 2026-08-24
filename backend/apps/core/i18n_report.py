"""English/Arabic bilingual content completeness for admin dashboards and CLI."""

from __future__ import annotations

from django.apps import apps
from django.db.models import Q

from apps.tenants.context import get_current_organization

# Models and their (english_field, arabic_field) bilingual pairs
BILINGUAL_MODELS = [
    ('learning', 'Article', [('title', 'title_ar'), ('content', 'content_ar')]),
    ('learning', 'Category', [('name', 'name_ar')]),
    ('learning', 'MediaAsset', [('title', 'title_ar')]),
    ('quizzes', 'Quiz', [('title', 'title_ar')]),
    ('quizzes', 'Question', [('question_text', 'question_text_ar')]),
    ('engagement', 'CivicNews', [('title', 'title_ar')]),
    ('engagement', 'CivicEvent', [('title', 'title_ar')]),
    ('engagement', 'Poll', [('question', 'question_ar')]),
    ('engagement', 'Petition', [('title', 'title_ar')]),
    ('engagement', 'Campaign', [('title', 'title_ar')]),
    ('learning', 'Course', [('title', 'title_ar')]),
]


def _organization_lookup(model) -> str | None:
    names = {field.name for field in model._meta.fields}
    if 'organization' in names:
        return 'organization'
    if model._meta.model_name == 'question':
        return 'quiz__organization'
    return None


def bilingual_queryset(model, *, org_slug: str | None = None):
    """Rows for one bilingual model, optionally limited to an organization."""
    lookup = _organization_lookup(model)
    if org_slug:
        manager = getattr(model, 'all_objects', model.objects)
        qs = manager.all()
        if lookup:
            qs = qs.filter(**{f'{lookup}__slug': org_slug})
        return qs

    qs = model.objects.all()
    organization = get_current_organization()
    if organization is not None and lookup == 'quiz__organization':
        qs = qs.filter(quiz__organization=organization)
    return qs


def build_translation_completeness(*, org_slug: str | None = None) -> dict:
    """Per-field Arabic translation coverage for tenant content."""
    rows = []
    for app_label, model_name, pairs in BILINGUAL_MODELS:
        try:
            model = apps.get_model(app_label, model_name)
        except LookupError:
            continue

        qs = bilingual_queryset(model, org_slug=org_slug)
        total = qs.count()
        if total == 0:
            continue

        for _en_field, ar_field in pairs:
            empty = qs.filter(Q(**{ar_field: ''}) | Q(**{f'{ar_field}__isnull': True})).count()
            pct = round((total - empty) / total * 100, 1) if total else 0.0
            rows.append({
                'model': f'{app_label}.{model_name}',
                'field': ar_field,
                'total': total,
                'translated': total - empty,
                'missing': empty,
                'completeness_pct': pct,
            })

    overall_missing = sum(row['missing'] for row in rows)
    overall_total = sum(row['total'] for row in rows)
    overall_translated = overall_total - overall_missing
    overall_pct = (
        round(overall_translated / overall_total * 100, 1) if overall_total else 0.0
    )
    return {
        'rows': rows,
        'overall_translated': overall_translated,
        'overall_total': overall_total,
        'overall_pct': overall_pct,
    }
