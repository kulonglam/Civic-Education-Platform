"""Shared application constants."""

# UI and API content languages supported by the platform (English and Arabic only).
SUPPORTED_LANGUAGES = frozenset({'en', 'ar'})
DEFAULT_LANGUAGE = 'en'
DEFAULT_PRIMARY_COLOR = '#059669'

LANGUAGE_CHOICES = (
    ('en', 'English'),
    ('ar', 'Arabic'),
)

# Legacy Tailwind blue palette values stored before the green rebrand.
LEGACY_BLUE_PRIMARY_COLORS = frozenset({
    '#2563eb',
    '#3b82f6',
    '#1d4ed8',
    '#1e40af',
    '#1e3a8a',
    '#60a5fa',
    '#93c5fd',
    '#bfdbfe',
    '#dbeafe',
    '#eff6ff',
})


def normalize_language(lang: str | None) -> str:
    """Return ``en`` or ``ar``; any other value maps to ``en``."""
    if not lang:
        return DEFAULT_LANGUAGE
    if lang == 'ar' or str(lang).startswith('ar'):
        return 'ar'
    return DEFAULT_LANGUAGE


def normalize_primary_color(color: str | None) -> str:
    """Return green default when ``color`` is a legacy blue brand value."""
    if not color:
        return DEFAULT_PRIMARY_COLOR
    normalized = str(color).strip().lower()
    if normalized in LEGACY_BLUE_PRIMARY_COLORS:
        return DEFAULT_PRIMARY_COLOR
    return color
