from .constants import DEFAULT_LANGUAGE, normalize_language


def get_preferred_language(request) -> str:
    """Resolve API content language to ``en`` or ``ar`` only."""
    lang = request.query_params.get('lang')
    if lang:
        return normalize_language(lang)

    accept = request.META.get('HTTP_ACCEPT_LANGUAGE', DEFAULT_LANGUAGE)
    if accept.startswith('ar'):
        return 'ar'

    if request.user and request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        if profile and profile.preferred_language:
            return normalize_language(profile.preferred_language)

    return DEFAULT_LANGUAGE
