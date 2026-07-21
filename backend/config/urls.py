from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# All versioned API routes live here.  Both /api/v1/ (canonical) and /api/
# (backward-compat alias) are mounted so existing clients continue to work
# while new clients can adopt the versioned base URL.
_v1_patterns = [
    path('', include('apps.core.urls')),
    path('auth/', include('apps.accounts.urls.auth')),
    path('users/', include('apps.accounts.urls.users')),
    path('articles/', include('apps.learning.urls.articles')),
    path('categories/', include('apps.learning.urls.categories')),
    path('media/', include('apps.learning.urls.media')),
    path('content-bundle/', include('apps.learning.urls.bundle')),
    path('quizzes/', include('apps.quizzes.urls')),
    path('topics/', include('apps.forum.urls.topics')),
    path('comments/', include('apps.forum.urls.comments')),
    path('notifications/', include('apps.notifications.urls')),
    path('notify/', include('apps.notifications.notify_urls')),
    path('analytics/', include('apps.analytics.urls')),
    path('audit/', include('apps.audit.urls')),
    path('tutor/', include('apps.tutor.urls')),
    path('organization/', include('apps.tenants.urls')),
    path('billing/', include('apps.billing.urls')),
]

urlpatterns = [
    path('', RedirectView.as_view(url='/api/docs/', permanent=False)),
    path('admin/', admin.site.urls),

    # ── Canonical versioned API (v1) ──────────────────────────────────────
    path('api/v1/', include(_v1_patterns)),

    # ── Backward-compatible unversioned alias ─────────────────────────────
    # Clients that already use /api/... continue to work without changes.
    # New integrations should target /api/v1/.
    path('api/', include(_v1_patterns)),

    # ── SCIM 2.0 (enterprise IdP provisioning) ────────────────────────────
    path('scim/v2/', include('apps.tenants.scim_urls')),

    # ── Schema / docs ─────────────────────────────────────────────────────
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
