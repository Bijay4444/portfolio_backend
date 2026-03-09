"""URL router for core app ViewSets.

Routes:
    GET  /api/v1/core/profile/          — singleton profile (no pk needed)
    GET  /api/v1/core/social-links/     — list active social links
    GET  /api/v1/core/social-links/{id}/ — retrieve single social link
    POST /api/v1/core/contact/          — submit contact form
"""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core.views import ContactSubmissionViewSet, ProfileViewSet, SocialLinkViewSet

router = DefaultRouter()
router.register(r"social-links", SocialLinkViewSet, basename="social-links")
router.register(r"contact", ContactSubmissionViewSet, basename="contact")

urlpatterns = [
    # Profile — fixed endpoint, no pk required from frontend
    path(
        "profile/",
        ProfileViewSet.as_view({"get": "retrieve"}),
        name="profile-detail",
    ),
    path("", include(router.urls)),
]
