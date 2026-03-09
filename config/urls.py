"""Root URL configuration for the portfolio backend monorepo.

API routes are versioned under /api/v1/.
Each app registers its own router in its urls.py and is included here.
"""

from __future__ import annotations

from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("ckeditor5/", include("django_ckeditor_5.urls")),   
    # OpenAPI schema + docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # App routers
    path("api/v1/core/", include("core.urls")),
    path("api/v1/bijay/", include("bijay_dev.urls")),
]

# Serve media files via Django in development only.
# In production nginx handles /media/ → MEDIA_ROOT directly.
if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
