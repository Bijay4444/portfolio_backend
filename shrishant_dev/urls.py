"""URL configuration for shrishant_dev app.

All routes are nested under ``api/v1/shrishant/`` (configured in config/urls.py).
"""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from shrishant_dev.views import (
    BlogCategoryViewSet,
    BlogPostViewSet,
    BlogTagViewSet,
    CertificationViewSet,
    EducationViewSet,
    ExperienceViewSet,
    ProjectViewSet,
    SkillCategoryViewSet,
    TechStackViewSet,
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

urlpatterns = [
    path("", include(router.urls)),
]