"""WebSocket origin allowlist (frontend SPA, not the API host)."""


def allowed_websocket_origins():
    """Return Origins Channels may accept (CORS + FRONTEND_URL)."""
    from django.conf import settings

    origins = []
    for item in getattr(settings, 'CORS_ALLOWED_ORIGINS', None) or []:
        cleaned = str(item).strip().rstrip('/')
        if cleaned:
            origins.append(cleaned)
    frontend = (getattr(settings, 'FRONTEND_URL', '') or '').strip().rstrip('/')
    if frontend and frontend not in origins:
        origins.append(frontend)
    return origins
