"""API views for shrishant_dev portfolio models.

Endpoints:
    GET  /api/v1/shrishant/skills/                — list skill categories (nested skills)
    GET  /api/v1/shrishant/skills/{id}/           — retrieve single skill category
    GET  /api/v1/shrishant/tech-stack/            — list all tech stack entries
    GET  /api/v1/shrishant/tech-stack/{id}/       — retrieve single tech stack entry
    GET  /api/v1/shrishant/projects/              — list active projects (with gallery)
    GET  /api/v1/shrishant/projects/{id}/         — retrieve single project
    GET  /api/v1/shrishant/experience/            — list work history
    GET  /api/v1/shrishant/experience/{id}/       — retrieve single experience
    GET  /api/v1/shrishant/education/             — list education entries
    GET  /api/v1/shrishant/education/{id}/        — retrieve single education entry
    GET  /api/v1/shrishant/certifications/        — list certifications
    GET  /api/v1/shrishant/certifications/{id}/   — retrieve single certification
    GET  /api/v1/shrishant/blog/categories/       — list blog categories
    GET  /api/v1/shrishant/blog/tags/             — list blog tags
    GET  /api/v1/shrishant/blog/posts/            — list published blog posts
    GET  /api/v1/shrishant/blog/posts/{slug}/     — retrieve single blog post by slug

All endpoints are public (AllowAny). All data is managed via Django Admin.
"""

from __future__ import annotations

import logging
from typing import Any

from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from common.constants import LoggerNames
from common.pagination import LimitOffsetPagination, get_paginated_response
from common.responses import success_response
from shrishant_dev.filters import (
    BlogPostFilter,
    ExperienceFilter,
    ProjectFilter,
    TechStackFilter,
)
from shrishant_dev.models import (
    BlogCategory,
    BlogPost,
    BlogTag,
    Certification,
    Education,
    Experience,
    Project,
    SkillCategory,
    TechStack,
)
from shrishant_dev.serializers import (
    BlogCategoryOutputSerializer,
    BlogPostDetailOutputSerializer,
    BlogPostListOutputSerializer,
    BlogTagOutputSerializer,
    CertificationOutputSerializer,
    EducationOutputSerializer,
    ExperienceOutputSerializer,
    ProjectOutputSerializer,
    SkillCategoryOutputSerializer,
    TechStackOutputSerializer,
)

logger = logging.getLogger(LoggerNames.PORTFOLIO)


# ---------------------------------------------------------------------------
# Skills & Tech Stack
# ---------------------------------------------------------------------------


@extend_schema_view(
    list=extend_schema(
        summary="List skill categories with nested skills",
        description=(
            "Returns all skill categories, each containing its nested TechStack "
            "entries ordered by display order. Used to render the Skills section."
        ),
        responses={
            200: OpenApiResponse(
                response=SkillCategoryOutputSerializer(many=True),
                description="Skill categories retrieved successfully.",
            ),
        },
        tags=["shrishant:skills"],
    ),
    retrieve=extend_schema(
        summary="Retrieve a single skill category",
        description="Returns a single skill category with its nested skills by UUID.",
        responses={
            200: OpenApiResponse(
                response=SkillCategoryOutputSerializer,
                description="Skill category retrieved successfully.",
            ),
            404: OpenApiResponse(description="Skill category not found."),
        },
        tags=["shrishant:skills"],
    ),
)
class SkillCategoryViewSet(ReadOnlyModelViewSet):
    """Read-only ViewSet for skill categories with nested tech stack entries.

    Prefetches skills to avoid N+1 queries on the nested serializer.
    """

    serializer_class = SkillCategoryOutputSerializer
    permission_classes = [AllowAny]
    throttle_classes: list = []
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        """Return all skill categories with prefetched skills.

        Returns:
            QuerySet of SkillCategory instances ordered by display order.
        """
        return SkillCategory.objects.prefetch_related("skills").order_by(
            "order", "name"
        )

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Return paginated list of skill categories.

        Args:
            request: The incoming DRF request.

        Returns:
            Paginated success response with nested skill categories.
        """
        return get_paginated_response(
            pagination_class=LimitOffsetPagination,
            serializer_class=SkillCategoryOutputSerializer,
            queryset=self.get_queryset(),
            request=request,
            view=self,
        )

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Return a single skill category by pk.

        Args:
            request: The incoming DRF request.

        Returns:
            Success response with the skill category data.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={"request": request})
        return success_response(data=serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="List all tech stack entries",
        description=(
            "Returns all tech stack / skill entries across all categories. "
            "Supports filtering by is_featured and category, "
            "ordering by order/name/created_at, and search by name."
        ),
        responses={
            200: OpenApiResponse(
                response=TechStackOutputSerializer(many=True),
                description="Tech stack entries retrieved successfully.",
            ),
        },
        tags=["shrishant:skills"],
    ),
    retrieve=extend_schema(
        summary="Retrieve a single tech stack entry",
        description="Returns a single tech stack entry by UUID.",
        responses={
            200: OpenApiResponse(
                response=TechStackOutputSerializer,
                description="Tech stack entry retrieved successfully.",
            ),
            404: OpenApiResponse(description="Tech stack entry not found."),
        },
        tags=["shrishant:skills"],
    ),
)
class TechStackViewSet(ReadOnlyModelViewSet):
    """Read-only ViewSet for individual tech stack / skill entries.

    Supports filtering via django-filter, ordering, and search.
    """

    serializer_class = TechStackOutputSerializer
    permission_classes = [AllowAny]
    throttle_classes: list = []
    pagination_class = LimitOffsetPagination
    filterset_class = TechStackFilter
    ordering_fields = ("order", "name", "created_at")
    search_fields = ("name",)

    def get_queryset(self):
        """Return tech stack entries with category selected.

        Returns:
            QuerySet of TechStack instances ordered by category and display order.
        """
        return TechStack.objects.select_related("category").order_by(
            "category__order", "order", "name"
        )

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Return paginated list of tech stack entries.

        Args:
            request: The incoming DRF request.

        Returns:
            Paginated success response with tech stack entries.
        """
        queryset = self.filter_queryset(self.get_queryset())
        return get_paginated_response(
            pagination_class=LimitOffsetPagination,
            serializer_class=TechStackOutputSerializer,
            queryset=queryset,
            request=request,
            view=self,
        )

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Return a single tech stack entry by pk.

        Args:
            request: The incoming DRF request.

        Returns:
            Success response with the tech stack entry data.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={"request": request})
        return success_response(data=serializer.data)


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------


@extend_schema_view(
    list=extend_schema(
        summary="List active portfolio projects",
        description=(
            "Returns paginated active projects with nested tech stack and gallery "
            "images. Archived projects are excluded. "
            "Supports filtering by is_featured and tech_stack, "
            "ordering by order/created_at, and search by title."
        ),
        responses={
            200: OpenApiResponse(
                response=ProjectOutputSerializer(many=True),
                description="Projects retrieved successfully.",
            ),
        },
        tags=["shrishant:projects"],
    ),
    retrieve=extend_schema(
        summary="Retrieve a single project",
        description=(
            "Returns a single project by UUID with full details, "
            "nested tech stack, and gallery images."
        ),
        responses={
            200: OpenApiResponse(
                response=ProjectOutputSerializer,
                description="Project retrieved successfully.",
            ),
            404: OpenApiResponse(description="Project not found."),
        },
        tags=["shrishant:projects"],
    ),
)
class ProjectViewSet(ReadOnlyModelViewSet):
    """Read-only ViewSet for portfolio projects.

    Only active projects are returned. Prefetches tech_stack M2M and gallery images.
    Supports filtering via django-filter, ordering, and search.
    """

    serializer_class = ProjectOutputSerializer
    permission_classes = [AllowAny]
    throttle_classes: list = []
    pagination_class = LimitOffsetPagination
    filterset_class = ProjectFilter
    ordering_fields = ("order", "created_at")
    search_fields = ("title",)

    def get_queryset(self):
        """Return active projects with prefetched tech stack and gallery images.

        Returns:
            QuerySet of active Project instances.
        """
        return (
            Project.objects.filter(status=Project.Status.ACTIVE)
            .prefetch_related("tech_stack__category", "images")
            .order_by("order", "-created_at")
        )

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Return paginated list of active projects.

        Args:
            request: The incoming DRF request.

        Returns:
            Paginated success response with project data.
        """
        queryset = self.filter_queryset(self.get_queryset())
        return get_paginated_response(
            pagination_class=LimitOffsetPagination,
            serializer_class=ProjectOutputSerializer,
            queryset=queryset,
            request=request,
            view=self,
        )

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Return a single project by pk.

        Args:
            request: The incoming DRF request.

        Returns:
            Success response with the project data.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={"request": request})
        return success_response(data=serializer.data)


# ---------------------------------------------------------------------------
# Experience
# ---------------------------------------------------------------------------


@extend_schema_view(
    list=extend_schema(
        summary="List work history entries",
        description=(
            "Returns paginated work experience entries ordered by start date "
            "(most recent first). Current jobs appear first."
        ),
        responses={
            200: OpenApiResponse(
                response=ExperienceOutputSerializer(many=True),
                description="Experience entries retrieved successfully.",
            ),
        },
        tags=["shrishant:experience"],
    ),
    retrieve=extend_schema(
        summary="Retrieve a single experience entry",
        description="Returns a single work history entry by UUID.",
        responses={
            200: OpenApiResponse(
                response=ExperienceOutputSerializer,
                description="Experience entry retrieved successfully.",
            ),
            404: OpenApiResponse(description="Experience entry not found."),
        },
        tags=["shrishant:experience"],
    ),
)
class ExperienceViewSet(ReadOnlyModelViewSet):
    """Read-only ViewSet for work history entries.

    Supports filtering by is_current and ordering by start_date.
    """

    serializer_class = ExperienceOutputSerializer
    permission_classes = [AllowAny]
    throttle_classes: list = []
    pagination_class = LimitOffsetPagination
    filterset_class = ExperienceFilter
    ordering_fields = ("start_date",)

    def get_queryset(self):
        """Return experience entries ordered by recency.

        Returns:
            QuerySet of Experience instances, current jobs first.
        """
        return Experience.objects.order_by("-is_current", "-start_date")

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Return paginated list of experience entries.

        Args:
            request: The incoming DRF request.

        Returns:
            Paginated success response with experience data.
        """
        queryset = self.filter_queryset(self.get_queryset())
        return get_paginated_response(
            pagination_class=LimitOffsetPagination,
            serializer_class=ExperienceOutputSerializer,
            queryset=queryset,
            request=request,
            view=self,
        )

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Return a single experience entry by pk.

        Args:
            request: The incoming DRF request.

        Returns:
            Success response with the experience data.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data)


# ---------------------------------------------------------------------------
# Education
# ---------------------------------------------------------------------------


@extend_schema_view(
    list=extend_schema(
        summary="List education entries",
        description=(
            "Returns paginated education entries ordered by start date "
            "(most recent first)."
        ),
        responses={
            200: OpenApiResponse(
                response=EducationOutputSerializer(many=True),
                description="Education entries retrieved successfully.",
            ),
        },
        tags=["shrishant:education"],
    ),
    retrieve=extend_schema(
        summary="Retrieve a single education entry",
        description="Returns a single education entry by UUID.",
        responses={
            200: OpenApiResponse(
                response=EducationOutputSerializer,
                description="Education entry retrieved successfully.",
            ),
            404: OpenApiResponse(description="Education entry not found."),
        },
        tags=["shrishant:education"],
    ),
)
class EducationViewSet(ReadOnlyModelViewSet):
    """Read-only ViewSet for academic history entries."""

    serializer_class = EducationOutputSerializer
    permission_classes = [AllowAny]
    throttle_classes: list = []
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        """Return education entries ordered by recency.

        Returns:
            QuerySet of Education instances.
        """
        return Education.objects.order_by("-start_date")

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Return paginated list of education entries.

        Args:
            request: The incoming DRF request.

        Returns:
            Paginated success response with education data.
        """
        return get_paginated_response(
            pagination_class=LimitOffsetPagination,
            serializer_class=EducationOutputSerializer,
            queryset=self.get_queryset(),
            request=request,
            view=self,
        )

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Return a single education entry by pk.

        Args:
            request: The incoming DRF request.

        Returns:
            Success response with the education data.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data)


# ---------------------------------------------------------------------------
# Certification
# ---------------------------------------------------------------------------


@extend_schema_view(
    list=extend_schema(
        summary="List certifications and achievements",
        description=(
            "Returns paginated certifications ordered by issue date "
            "(most recent first)."
        ),
        responses={
            200: OpenApiResponse(
                response=CertificationOutputSerializer(many=True),
                description="Certifications retrieved successfully.",
            ),
        },
        tags=["shrishant:certifications"],
    ),
    retrieve=extend_schema(
        summary="Retrieve a single certification",
        description="Returns a single certification by UUID.",
        responses={
            200: OpenApiResponse(
                response=CertificationOutputSerializer,
                description="Certification retrieved successfully.",
            ),
            404: OpenApiResponse(description="Certification not found."),
        },
        tags=["shrishant:certifications"],
    ),
)
class CertificationViewSet(ReadOnlyModelViewSet):
    """Read-only ViewSet for certificates and achievements."""

    serializer_class = CertificationOutputSerializer
    permission_classes = [AllowAny]
    throttle_classes: list = []
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        """Return certifications ordered by issue date.

        Returns:
            QuerySet of Certification instances.
        """
        return Certification.objects.order_by("-issued_date")

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Return paginated list of certifications.

        Args:
            request: The incoming DRF request.

        Returns:
            Paginated success response with certification data.
        """
        return get_paginated_response(
            pagination_class=LimitOffsetPagination,
            serializer_class=CertificationOutputSerializer,
            queryset=self.get_queryset(),
            request=request,
            view=self,
        )

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Return a single certification by pk.

        Args:
            request: The incoming DRF request.

        Returns:
            Success response with the certification data.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={"request": request})
        return success_response(data=serializer.data)


# ---------------------------------------------------------------------------
# Blog
# ---------------------------------------------------------------------------


@extend_schema_view(
    list=extend_schema(
        summary="List blog categories",
        description="Returns paginated blog categories.",
        responses={
            200: OpenApiResponse(
                response=BlogCategoryOutputSerializer(many=True),
                description="Blog categories retrieved successfully.",
            ),
        },
        tags=["shrishant:blog"],
    ),
    retrieve=extend_schema(
        summary="Retrieve a single blog category",
        description="Returns a single blog category by UUID.",
        responses={
            200: OpenApiResponse(
                response=BlogCategoryOutputSerializer,
                description="Blog category retrieved successfully.",
            ),
            404: OpenApiResponse(description="Blog category not found."),
        },
        tags=["shrishant:blog"],
    ),
)
class BlogCategoryViewSet(ReadOnlyModelViewSet):
    """Read-only ViewSet for blog categories."""

    serializer_class = BlogCategoryOutputSerializer
    permission_classes = [AllowAny]
    throttle_classes: list = []
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        """Return blog categories ordered by name.

        Returns:
            QuerySet of BlogCategory instances.
        """
        return BlogCategory.objects.order_by("name")

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Return paginated list of blog categories.

        Args:
            request: The incoming DRF request.

        Returns:
            Paginated success response with blog category data.
        """
        return get_paginated_response(
            pagination_class=LimitOffsetPagination,
            serializer_class=BlogCategoryOutputSerializer,
            queryset=self.get_queryset(),
            request=request,
            view=self,
        )

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Return a single blog category by pk.

        Args:
            request: The incoming DRF request.

        Returns:
            Success response with the blog category data.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="List blog tags",
        description="Returns paginated blog tags.",
        responses={
            200: OpenApiResponse(
                response=BlogTagOutputSerializer(many=True),
                description="Blog tags retrieved successfully.",
            ),
        },
        tags=["shrishant:blog"],
    ),
    retrieve=extend_schema(
        summary="Retrieve a single blog tag",
        description="Returns a single blog tag by UUID.",
        responses={
            200: OpenApiResponse(
                response=BlogTagOutputSerializer,
                description="Blog tag retrieved successfully.",
            ),
            404: OpenApiResponse(description="Blog tag not found."),
        },
        tags=["shrishant:blog"],
    ),
)
class BlogTagViewSet(ReadOnlyModelViewSet):
    """Read-only ViewSet for blog tags."""

    serializer_class = BlogTagOutputSerializer
    permission_classes = [AllowAny]
    throttle_classes: list = []
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        """Return blog tags ordered by name.

        Returns:
            QuerySet of BlogTag instances.
        """
        return BlogTag.objects.order_by("name")

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Return paginated list of blog tags.

        Args:
            request: The incoming DRF request.

        Returns:
            Paginated success response with blog tag data.
        """
        return get_paginated_response(
            pagination_class=LimitOffsetPagination,
            serializer_class=BlogTagOutputSerializer,
            queryset=self.get_queryset(),
            request=request,
            view=self,
        )

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Return a single blog tag by pk.

        Args:
            request: The incoming DRF request.

        Returns:
            Success response with the blog tag data.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="List published blog posts",
        description=(
            "Returns paginated published blog posts (drafts excluded). "
            "Ordered by published date (most recent first). "
            "List view excludes full content for performance — use detail view "
            "to fetch full post content. "
            "Supports filtering by category, tag, and is_featured, "
            "ordering by published_at/view_count/created_at, "
            "and search by title/excerpt."
        ),
        responses={
            200: OpenApiResponse(
                response=BlogPostListOutputSerializer(many=True),
                description="Blog posts retrieved successfully.",
            ),
        },
        tags=["shrishant:blog"],
    ),
    retrieve=extend_schema(
        summary="Retrieve a single blog post by slug",
        description=(
            "Returns the full blog post including rich-text content, "
            "SEO metadata, Open Graph fields, and related posts. "
            "Increments the view counter."
        ),
        responses={
            200: OpenApiResponse(
                response=BlogPostDetailOutputSerializer,
                description="Blog post retrieved successfully.",
            ),
            404: OpenApiResponse(description="Blog post not found."),
        },
        tags=["shrishant:blog"],
    ),
)
class BlogPostViewSet(ReadOnlyModelViewSet):
    """Read-only ViewSet for published blog posts.

    List view uses BlogPostListOutputSerializer (lightweight, no content).
    Detail view uses BlogPostDetailOutputSerializer (full content + SEO).
    Lookup is by slug, not UUID, for SEO-friendly URLs.
    Supports filtering via django-filter, ordering, and search.
    """

    permission_classes = [AllowAny]
    throttle_classes: list = []
    pagination_class = LimitOffsetPagination
    lookup_field = "slug"
    filterset_class = BlogPostFilter
    ordering_fields = ("published_at", "view_count", "created_at")
    search_fields = ("title", "excerpt")

    def get_serializer_class(self):
        """Return list or detail serializer based on action.

        Returns:
            BlogPostListOutputSerializer for list, BlogPostDetailOutputSerializer
            for retrieve.
        """
        if self.action == "retrieve":
            return BlogPostDetailOutputSerializer
        return BlogPostListOutputSerializer

    def get_queryset(self):
        """Return published posts with prefetched relationships.

        Returns:
            QuerySet of published BlogPost instances.
        """
        return (
            BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED)
            .prefetch_related("categories", "tags", "related_posts")
            .order_by("-published_at", "-created_at")
        )

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Return paginated list of published blog posts.

        Args:
            request: The incoming DRF request.

        Returns:
            Paginated success response with blog post list data.
        """
        queryset = self.filter_queryset(self.get_queryset()).distinct()
        return get_paginated_response(
            pagination_class=LimitOffsetPagination,
            serializer_class=BlogPostListOutputSerializer,
            queryset=queryset,
            request=request,
            view=self,
        )

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Return a single published blog post by slug.

        Increments the view counter atomically on each retrieval.

        Args:
            request: The incoming DRF request.

        Returns:
            Success response with the full blog post data.
        """
        instance = self.get_object()
        instance.increment_view_count()

        serializer = self.get_serializer(instance, context={"request": request})

        logger.info(
            "Blog post viewed | slug=%s views=%d",
            instance.slug,
            instance.view_count + 1,
        )

        return success_response(data=serializer.data)
