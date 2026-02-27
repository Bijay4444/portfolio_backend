"""Root URL configuration for the portfolio backend monorepo.

API routes are versioned under /api/v1/.
Each app registers its own router in its urls.py and is included here.
"""

from __future__ import annotations

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    # OpenAPI schema + Swagger UI
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    # Versioned API namespaces — each app's urls.py is included here
    path("api/v1/core/", include("core.urls")),
    path("api/v1/bijay/", include("bijay_dev.urls")),
]
