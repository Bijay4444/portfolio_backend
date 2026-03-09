"""URL configuration for bijay_dev app.

All routes are nested under ``api/v1/bijay/`` (configured in config/urls.py).
"""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from bijay_dev.views import (
    BlogCategoryViewSet,
    BlogPostViewSet,
    BlogTagViewSet,
    BookViewSet,
    CertificationViewSet,
    EducationViewSet,
    ExperienceViewSet,
    ProjectViewSet,
    ReadingListViewSet,
    SkillCategoryViewSet,
    TechStackViewSet,
    ThoughtViewSet,
)

router = DefaultRouter()

# Skills & Tech Stack
router.register(r"skills", SkillCategoryViewSet, basename="skill-category")
router.register(r"tech-stack", TechStackViewSet, basename="tech-stack")

# Portfolio
router.register(r"projects", ProjectViewSet, basename="project")
router.register(r"experience", ExperienceViewSet, basename="experience")
router.register(r"education", EducationViewSet, basename="education")
router.register(r"certifications", CertificationViewSet, basename="certification")

# Blog
router.register(r"blog/categories", BlogCategoryViewSet, basename="blog-category")
router.register(r"blog/tags", BlogTagViewSet, basename="blog-tag")
router.register(r"blog/posts", BlogPostViewSet, basename="blog-post")

# Extras
router.register(r"reading-list", ReadingListViewSet, basename="reading-list")
router.register(r"thoughts", ThoughtViewSet, basename="thought")
router.register(r"books", BookViewSet, basename="book")

urlpatterns = [
    path("", include(router.urls)),
]
