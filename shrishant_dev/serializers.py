"""Serializers for shrishant_dev domain models.

Naming convention:
    <Model>OutputSerializer  — read operations (GET) — nested, fully expanded
    <Model>InputSerializer   — write operations (POST/PUT) — flat, validated

All shrishant_dev models are managed via Django Admin — the API is read-only.
Therefore only OutputSerializers are defined here (no InputSerializers).
"""

from __future__ import annotations

from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from shrishant_dev.models import (
    BlogCategory,
    BlogPost,
    BlogTag,
    Certification,
    Education,
    Experience,
    Project,
    ProjectImage,
    SkillCategory,
    TechStack,
)

# Skills & Tech Stack


@extend_schema_serializer(component_name="ShrishantTechStackOutput")
class TechStackOutputSerializer(serializers.ModelSerializer):
    """Read serializer for a single tech stack / skill entry.

    Attributes:
        category_name: Denormalised category label for display.
        icon_url: Absolute URL to the icon image (null if not uploaded).
        icon_cdn: Raw CDN icon URL configured in admin (optional).
    """

    category_name: serializers.CharField = serializers.CharField(
        source="category.name",
        read_only=True,
    )
    icon_url: serializers.SerializerMethodField = serializers.SerializerMethodField()

    class Meta:
        model = TechStack
        fields = (
            "id",
            "name",
            "category_name",
            "icon_url",
            "icon_cdn",
            "is_featured",
            "order",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_icon_url(self, obj: TechStack) -> str | None:
        """Return icon URL, preferring uploaded media then CDN URL.

        Args:
            obj: The TechStack instance being serialized.

        Returns:
            Absolute URL string, CDN URL, or None if neither is set.
        """
        if obj.icon:
            request = self.context.get("request")
            if request is not None:
                return request.build_absolute_uri(obj.icon.url)
            return obj.icon.url
        if obj.icon_cdn:
            return obj.icon_cdn
        return None


@extend_schema_serializer(component_name="ShrishantSkillCategoryOutput")
class SkillCategoryOutputSerializer(serializers.ModelSerializer):
    """Read serializer for a skill category with nested skills.

    Attributes:
        skills: All TechStack entries belonging to this category, ordered.
    """

    skills: TechStackOutputSerializer = TechStackOutputSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = SkillCategory
        fields = (
            "id",
            "name",
            "order",
            "skills",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


# Projects

@extend_schema_serializer(component_name="ShrishantProjectImageOutput")
class ProjectImageOutputSerializer(serializers.ModelSerializer):
    """Read serializer for project gallery images.

    Attributes:
        image_url: Absolute URL to the gallery image.
    """

    image_url: serializers.SerializerMethodField = serializers.SerializerMethodField()

    class Meta:
        model = ProjectImage
        fields = (
            "id",
            "image_url",
            "caption",
            "alt_text",
            "order",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_image_url(self, obj: ProjectImage) -> str | None:
        """Return absolute URL for the gallery image.

        Args:
            obj: The ProjectImage instance being serialized.

        Returns:
            Absolute URL string, or None if no image is set.
        """
        if not obj.image:
            return None
        request = self.context.get("request")
        if request is not None:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url


@extend_schema_serializer(component_name="ShrishantProjectOutput")
class ProjectOutputSerializer(serializers.ModelSerializer):
    """Read serializer for portfolio projects.

    Attributes:
        tech_stack: Nested list of associated TechStack entries.
        images: Nested list of gallery images for this project.
        thumbnail_url: Absolute URL to the project thumbnail (null if absent).
        status_display: Human-readable status label from TextChoices.
    """

    tech_stack: TechStackOutputSerializer = TechStackOutputSerializer(
        many=True,
        read_only=True,
    )
    images: ProjectImageOutputSerializer = ProjectImageOutputSerializer(
        many=True,
        read_only=True,
    )
    thumbnail_url: serializers.SerializerMethodField = (
        serializers.SerializerMethodField()
    )
    status_display: serializers.CharField = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    class Meta:
        model = Project
        fields = (
            "id",
            "title",
            "description",
            "thumbnail_url",
            "github_url",
            "live_url",
            "status",
            "status_display",
            "is_featured",
            "tech_stack",
            "images",
            "order",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_thumbnail_url(self, obj: Project) -> str | None:
        """Return absolute URL for the project thumbnail.

        Args:
            obj: The Project instance being serialized.

        Returns:
            Absolute URL string, or None if no thumbnail is set.
        """
        if not obj.thumbnail:
            return None
        request = self.context.get("request")
        if request is not None:
            return request.build_absolute_uri(obj.thumbnail.url)
        return obj.thumbnail.url


# Experience

@extend_schema_serializer(component_name="ShrishantExperienceOutput")
class ExperienceOutputSerializer(serializers.ModelSerializer):
    """Read serializer for work history entries."""

    class Meta:
        model = Experience
        fields = (
            "id",
            "title",
            "company",
            "role",
            "description",
            "start_date",
            "end_date",
            "is_current",
            "company_url",
            "location",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


# Education

@extend_schema_serializer(component_name="ShrishantEducationOutput")
class EducationOutputSerializer(serializers.ModelSerializer):
    """Read serializer for academic history entries."""

    class Meta:
        model = Education
        fields = (
            "id",
            "title",
            "institution",
            "degree",
            "field_of_study",
            "start_date",
            "end_date",
            "description",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


# Certification

@extend_schema_serializer(component_name="ShrishantCertificationOutput")
class CertificationOutputSerializer(serializers.ModelSerializer):
    """Read serializer for certificates and achievements.

    Attributes:
        image_url: Absolute URL to the certificate badge/image.
    """

    image_url: serializers.SerializerMethodField = serializers.SerializerMethodField()

    class Meta:
        model = Certification
        fields = (
            "id",
            "title",
            "issuer",
            "issued_date",
            "credential_url",
            "image_url",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_image_url(self, obj: Certification) -> str | None:
        """Return absolute URL for the certificate image.

        Args:
            obj: The Certification instance being serialized.

        Returns:
            Absolute URL string, or None if no image is set.
        """
        if not obj.image:
            return None
        request = self.context.get("request")
        if request is not None:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url


# Blog

@extend_schema_serializer(component_name="ShrishantBlogCategoryOutput")
class BlogCategoryOutputSerializer(serializers.ModelSerializer):
    """Read serializer for blog categories."""

    class Meta:
        model = BlogCategory
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "meta_description",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


@extend_schema_serializer(component_name="ShrishantBlogTagOutput")
class BlogTagOutputSerializer(serializers.ModelSerializer):
    """Read serializer for blog tags."""

    class Meta:
        model = BlogTag
        fields = (
            "id",
            "name",
            "slug",
            "color_hex",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


@extend_schema_serializer(component_name="ShrishantBlogPostListOutput")
class BlogPostListOutputSerializer(serializers.ModelSerializer):
    """Lightweight read serializer for blog post list views.

    Excludes the full rich-text content to keep list responses fast.
    Contains only metadata needed for post cards.

    Attributes:
        categories: Nested category objects for display.
        tags: Nested tag objects for display.
        hero_image_url: Absolute URL to the hero image.
        read_time: Estimated read time in minutes.
    """

    categories: BlogCategoryOutputSerializer = BlogCategoryOutputSerializer(
        many=True,
        read_only=True,
    )
    tags: BlogTagOutputSerializer = BlogTagOutputSerializer(
        many=True,
        read_only=True,
    )
    hero_image_url: serializers.SerializerMethodField = (
        serializers.SerializerMethodField()
    )
    read_time: serializers.SerializerMethodField = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = (
            "id",
            "title",
            "slug",
            "excerpt",
            "hero_image_url",
            "is_featured",
            "status",
            "published_at",
            "view_count",
            "read_time",
            "categories",
            "tags",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_hero_image_url(self, obj: BlogPost) -> str | None:
        """Return absolute URL for the hero image.

        Args:
            obj: The BlogPost instance being serialized.

        Returns:
            Absolute URL string, or None if no hero image is set.
        """
        if not obj.hero_image:
            return None
        request = self.context.get("request")
        if request is not None:
            return request.build_absolute_uri(obj.hero_image.url)
        return obj.hero_image.url

    def get_read_time(self, obj: BlogPost) -> int:
        """Return estimated read time in minutes.

        Args:
            obj: The BlogPost instance being serialized.

        Returns:
            Integer minutes (minimum 1).
        """
        return obj.get_read_time()


@extend_schema_serializer(component_name="ShrishantBlogPostDetailOutput")
class BlogPostDetailOutputSerializer(BlogPostListOutputSerializer):
    """Full read serializer for blog post detail views.

    Extends the list serializer with the full rich-text content,
    SEO metadata, Open Graph fields, and related posts.

    Attributes:
        related_posts: Nested list of recommended posts (list-level data only).
    """

    related_posts: BlogPostListOutputSerializer = BlogPostListOutputSerializer(
        many=True,
        read_only=True,
    )

    class Meta(BlogPostListOutputSerializer.Meta):
        fields = BlogPostListOutputSerializer.Meta.fields + (
            "content",
            "meta_title",
            "meta_description",
            "og_title",
            "og_description",
            "related_posts",
        )
