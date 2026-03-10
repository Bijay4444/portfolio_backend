"""Django filter classes for shrishant_dev API endpoints.

FilterSets are declared here and referenced by ViewSets via filterset_class.
Uses django-filter (already in INSTALLED_APPS and DEFAULT_FILTER_BACKENDS).

Each FilterSet documents the query params it exposes. drf-spectacular
auto-discovers these and adds them to the Swagger docs.
"""

from __future__ import annotations

import django_filters

from shrishant_dev.models import BlogPost, Experience, Project, TechStack


class TechStackFilter(django_filters.FilterSet):
    """Filters for tech stack / skill entries.

    Query params:
        ?is_featured=true       — only featured skills
        ?category=<name>        — filter by category name (case-insensitive)
    """

    category = django_filters.CharFilter(
        field_name="category__name",
        lookup_expr="iexact",
        help_text="Filter by category name (case-insensitive match).",
    )

    class Meta:
        model = TechStack
        fields = ("is_featured",)


class ProjectFilter(django_filters.FilterSet):
    """Filters for portfolio projects.

    Query params:
        ?is_featured=true       — only featured projects
        ?tech_stack=<name>      — filter by tech stack name (case-insensitive)
    """

    tech_stack = django_filters.CharFilter(
        field_name="tech_stack__name",
        lookup_expr="iexact",
        help_text="Filter by tech stack name (case-insensitive match).",
    )

    class Meta:
        model = Project
        fields = ("is_featured",)


class ExperienceFilter(django_filters.FilterSet):
    """Filters for work experience entries.

    Query params:
        ?is_current=true    — only current jobs
    """

    class Meta:
        model = Experience
        fields = ("is_current",)


class BlogPostFilter(django_filters.FilterSet):
    """Filters for published blog posts.

    Query params:
        ?category=<slug>    — filter by category slug
        ?tag=<slug>         — filter by tag slug
        ?is_featured=true   — only featured post(s)
    """

    category = django_filters.CharFilter(
        field_name="categories__slug",
        lookup_expr="exact",
        help_text="Filter by category slug.",
    )
    tag = django_filters.CharFilter(
        field_name="tags__slug",
        lookup_expr="exact",
        help_text="Filter by tag slug.",
    )

    class Meta:
        model = BlogPost
        fields = ("is_featured",)
