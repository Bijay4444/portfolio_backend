"""Django Admin registration for shrishant_dev models.

Features:
    SkillCategory  — ordered list with inline TechStack entries
    TechStack      — filterable by category, featured badge
    Project        — CKEditor 5 description, status/featured filters, M2M tech_stack
    ProjectImage   — inline gallery images on Project admin page
    Experience     — chronological list with current-job badge
    Education      — chronological list
    Certification  — date-ordered, image preview
    BlogCategory   — auto-slug, CKEditor 5 description
    BlogTag        — colour swatch preview
    BlogPost       — full CKEditor 5 editor, SEO fieldsets, featured/status management
"""

from __future__ import annotations

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html, mark_safe
from django.utils.translation import gettext_lazy as _, ngettext

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

class TechStackInline(admin.TabularInline):
    """Inline editor for TechStack entries on the SkillCategory page."""

    model = TechStack
    extra = 1
    fields = ("name", "icon", "icon_cdn", "is_featured", "order")
    ordering = ("order", "name")


@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    """Admin for skill categories with inline skills."""

    inlines = [TechStackInline]
    list_display = ("name", "order", "skill_count", "updated_at")
    list_editable = ("order",)
    search_fields = ("name",)
    ordering = ("order", "name")

    @admin.display(description=_("Skills"))
    def skill_count(self, obj: SkillCategory) -> int:
        """Return the number of skills in this category."""
        return obj.skills.count()


@admin.register(TechStack)
class TechStackAdmin(admin.ModelAdmin):
    """Admin for individual tech stack / skill entries."""

    list_display = (
        "name",
        "category",
        "featured_badge",
        "icon_preview",
        "icon_cdn",
        "order",
        "updated_at",
    )
    list_filter = ("category", "is_featured")
    list_editable = ("order",)
    search_fields = ("name", "category__name", "icon_cdn")
    ordering = ("category__order", "order", "name")

    @admin.display(description=_("Featured"), boolean=False)
    def featured_badge(self, obj: TechStack) -> str:
        """Render a coloured badge for featured status."""
        if obj.is_featured:
            return mark_safe(
                '<span style="color:#16a34a;font-weight:600;">★ Featured</span>'
            )
        return mark_safe('<span style="color:#9ca3af;">—</span>')

    @admin.display(description=_("Icon"))
    def icon_preview(self, obj: TechStack) -> str:
        """Render a small inline preview of the uploaded icon or CDN icon."""
        if obj.icon:
            source = obj.icon.url
        elif obj.icon_cdn:
            source = obj.icon_cdn
        else:
            return _("—")
        return format_html(
            '<img src="{}" style="width:24px;height:24px;object-fit:contain;" />',
            source,
        )


# Projects

class ProjectImageInline(admin.TabularInline):
    """Inline editor for gallery images on the Project admin page."""

    model = ProjectImage
    extra = 1
    fields = ("image", "image_preview", "caption", "alt_text", "order")
    readonly_fields = ("image_preview",)
    ordering = ("order",)

    @admin.display(description=_("Preview"))
    def image_preview(self, obj: ProjectImage) -> str:
        """Render a small inline preview of the gallery image."""
        if not obj.image:
            return _("—")
        return format_html(
            '<img src="{}" style="max-width:120px;max-height:80px;'
            'object-fit:cover;border-radius:4px;" />',
            obj.image.url,
        )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin for portfolio projects with CKEditor 5 rich-text description."""

    inlines = [ProjectImageInline]
    list_display = (
        "title",
        "status_badge",
        "featured_badge",
        "tech_count",
        "image_count",
        "order",
        "created_at",
    )
    list_filter = ("status", "is_featured")
    list_editable = ("order",)
    search_fields = ("title",)
    filter_horizontal = ("tech_stack",)
    readonly_fields = ("id", "created_at", "updated_at", "thumbnail_preview")
    ordering = ("order", "-created_at")
    fieldsets = (
        (
            _("Project Info"),
            {
                "fields": (
                    "title",
                    "description",
                    ("thumbnail", "thumbnail_preview"),
                ),
            },
        ),
        (
            _("Links"),
            {"fields": ("github_url", "live_url")},
        ),
        (
            _("Classification"),
            {"fields": ("status", "is_featured", "tech_stack", "order")},
        ),
        (
            _("Metadata"),
            {
                "fields": ("id", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description=_("Status"), boolean=False)
    def status_badge(self, obj: Project) -> str:
        """Render a coloured badge for project status."""
        if obj.status == Project.Status.ACTIVE:
            return mark_safe(
                '<span style="color:#16a34a;font-weight:600;">● Active</span>'
            )
        return mark_safe(
            '<span style="color:#6b7280;">● Archived</span>'
        )

    @admin.display(description=_("Featured"), boolean=False)
    def featured_badge(self, obj: Project) -> str:
        """Render a coloured badge for featured status."""
        if obj.is_featured:
            return mark_safe(
                '<span style="color:#f59e0b;font-weight:600;">★ Featured</span>'
            )
        return mark_safe('<span style="color:#9ca3af;">—</span>')

    @admin.display(description=_("Tech"))
    def tech_count(self, obj: Project) -> int:
        """Return the number of tech stack entries linked to this project."""
        return obj.tech_stack.count()

    @admin.display(description=_("Images"))
    def image_count(self, obj: Project) -> int:
        """Return the number of gallery images for this project."""
        return obj.images.count()

    @admin.display(description=_("Thumbnail"))
    def thumbnail_preview(self, obj: Project) -> str:
        """Render a small inline preview of the project thumbnail."""
        if not obj.thumbnail:
            return _("No thumbnail uploaded.")
        return format_html(
            '<img src="{}" style="max-width:200px;max-height:120px;'
            'object-fit:cover;border-radius:4px;" />',
            obj.thumbnail.url,
        )


# Experience

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    """Admin for work history entries."""

    list_display = (
        "role",
        "company",
        "location",
        "current_badge",
        "start_date",
        "end_date",
    )
    list_filter = ("is_current",)
    search_fields = ("title", "company", "role", "location")
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("-start_date",)
    fieldsets = (
        (
            _("Position"),
            {"fields": ("title", "company", "role", "description")},
        ),
        (
            _("Duration & Location"),
            {"fields": ("start_date", "end_date", "is_current", "location")},
        ),
        (
            _("Links"),
            {"fields": ("company_url",)},
        ),
        (
            _("Metadata"),
            {
                "fields": ("id", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description=_("Current"), boolean=False)
    def current_badge(self, obj: Experience) -> str:
        """Render a badge indicating if this is the current job."""
        if obj.is_current:
            return mark_safe(
                '<span style="color:#16a34a;font-weight:600;">● Current</span>'
            )
        return mark_safe('<span style="color:#9ca3af;">—</span>')


# Education

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    """Admin for academic history entries."""

    list_display = ("title", "institution", "degree", "field_of_study", "start_date")
    search_fields = ("title", "institution", "degree", "field_of_study")
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("-start_date",)
    fieldsets = (
        (
            _("Programme"),
            {
                "fields": (
                    "title",
                    "institution",
                    "degree",
                    "field_of_study",
                    "description",
                ),
            },
        ),
        (
            _("Duration"),
            {"fields": ("start_date", "end_date")},
        ),
        (
            _("Metadata"),
            {
                "fields": ("id", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


# Certification

@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    """Admin for certificates and achievements."""

    list_display = ("title", "issuer", "issued_date", "has_credential", "image_preview")
    search_fields = ("title", "issuer")
    readonly_fields = ("id", "created_at", "updated_at", "image_preview")
    ordering = ("-issued_date",)
    fieldsets = (
        (
            _("Certificate"),
            {"fields": ("title", "issuer", "issued_date")},
        ),
        (
            _("Verification"),
            {"fields": ("credential_url", ("image", "image_preview"))},
        ),
        (
            _("Metadata"),
            {
                "fields": ("id", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description=_("Credential"), boolean=True)
    def has_credential(self, obj: Certification) -> bool:
        """Return True if a credential URL is provided."""
        return bool(obj.credential_url)

    @admin.display(description=_("Image"))
    def image_preview(self, obj: Certification) -> str:
        """Render a small inline preview of the certificate image."""
        if not obj.image:
            return _("—")
        return format_html(
            '<img src="{}" style="max-width:120px;max-height:80px;'
            'object-fit:contain;border-radius:4px;" />',
            obj.image.url,
        )


# Blog

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    """Admin for blog categories with CKEditor 5 rich-text description."""

    list_display = ("name", "slug", "post_count", "updated_at")
    search_fields = ("name", "slug")
    readonly_fields = ("id", "slug", "created_at", "updated_at")
    prepopulated_fields: dict = {}
    fieldsets = (
        (
            None,
            {"fields": ("name", "slug", "description", "meta_description")},
        ),
        (
            _("Metadata"),
            {
                "fields": ("id", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description=_("Posts"))
    def post_count(self, obj: BlogCategory) -> int:
        """Return the number of blog posts in this category."""
        return obj.posts.count()


@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    """Admin for blog tags with colour swatch preview."""

    list_display = ("name", "slug", "color_swatch", "post_count", "updated_at")
    search_fields = ("name", "slug")
    readonly_fields = ("id", "slug", "created_at", "updated_at")
    fieldsets = (
        (
            None,
            {"fields": ("name", "slug", "color_hex")},
        ),
        (
            _("Metadata"),
            {
                "fields": ("id", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description=_("Colour"))
    def color_swatch(self, obj: BlogTag) -> str:
        """Render a small coloured square showing the tag colour."""
        return format_html(
            '<span style="display:inline-block;width:18px;height:18px;'
            'border-radius:3px;background:{};" title="{}"></span>',
            obj.color_hex,
            obj.color_hex,
        )

    @admin.display(description=_("Posts"))
    def post_count(self, obj: BlogTag) -> int:
        """Return the number of blog posts using this tag."""
        return obj.posts.count()


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    """Admin for blog posts with CKEditor 5, SEO fields, and Open Graph.

    Fieldsets are organised into logical groups: Content, SEO, Open Graph,
    Publication, and Relationships. Slug is read-only after creation.
    """

    list_display = (
        "title",
        "status_badge",
        "featured_badge",
        "published_at",
        "view_count",
        "updated_at",
    )
    list_filter = ("status", "is_featured", "categories", "tags")
    search_fields = ("title", "slug", "excerpt")
    readonly_fields = (
        "id",
        "slug",
        "view_count",
        "published_at",
        "created_at",
        "updated_at",
        "hero_preview",
    )
    filter_horizontal = ("categories", "tags", "related_posts")
    ordering = ("-published_at", "-created_at")
    date_hierarchy = "published_at"
    actions = ["publish_posts", "unpublish_posts"]
    fieldsets = (
        (
            _("Content"),
            {
                "fields": (
                    "title",
                    "slug",
                    "excerpt",
                    "content",
                    ("hero_image", "hero_preview"),
                ),
            },
        ),
        (
            _("SEO"),
            {
                "fields": ("meta_title", "meta_description"),
                "classes": ("collapse",),
                "description": _(
                    "Override title and description for search engine results. "
                    "Falls back to title/excerpt if left blank."
                ),
            },
        ),
        (
            _("Open Graph"),
            {
                "fields": ("og_title", "og_description"),
                "classes": ("collapse",),
                "description": _(
                    "Override title and description for social media previews. "
                    "Falls back to title/meta_description if left blank."
                ),
            },
        ),
        (
            _("Publication"),
            {"fields": ("status", "is_featured", "published_at", "view_count")},
        ),
        (
            _("Relationships"),
            {"fields": ("categories", "tags", "related_posts")},
        ),
        (
            _("Metadata"),
            {
                "fields": ("id", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description=_("Status"), boolean=False)
    def status_badge(self, obj: BlogPost) -> str:
        """Render a coloured badge for publication status."""
        if obj.status == BlogPost.Status.PUBLISHED:
            return mark_safe(
                '<span style="color:#16a34a;font-weight:600;">● Published</span>'
            )
        return mark_safe(
            '<span style="color:#f59e0b;font-weight:600;">● Draft</span>'
        )

    @admin.display(description=_("Featured"), boolean=False)
    def featured_badge(self, obj: BlogPost) -> str:
        """Render a badge for featured posts."""
        if obj.is_featured:
            return mark_safe(
                '<span style="color:#f59e0b;font-weight:600;">★ Featured</span>'
            )
        return mark_safe('<span style="color:#9ca3af;">—</span>')

    @admin.display(description=_("Hero"))
    def hero_preview(self, obj: BlogPost) -> str:
        """Render a small inline preview of the hero image."""
        if not obj.hero_image:
            return _("No hero image uploaded.")
        return format_html(
            '<img src="{}" style="max-width:300px;max-height:170px;'
            'object-fit:cover;border-radius:4px;" />',
            obj.hero_image.url,
        )

    @admin.action(description=_("Publish selected posts"))
    def publish_posts(
        self, request: HttpRequest, queryset: QuerySet[BlogPost]
    ) -> None:
        """Bulk action: set selected posts to published status."""
        updated = queryset.filter(status=BlogPost.Status.DRAFT).update(
            status=BlogPost.Status.PUBLISHED,
        )
        self.message_user(
            request,
            ngettext(
                "%d post was published.",
                "%d posts were published.",
                updated,
            )
            % updated,
        )

    @admin.action(description=_("Revert selected posts to draft"))
    def unpublish_posts(
        self, request: HttpRequest, queryset: QuerySet[BlogPost]
    ) -> None:
        """Bulk action: revert selected posts back to draft status."""
        updated = queryset.filter(status=BlogPost.Status.PUBLISHED).update(
            status=BlogPost.Status.DRAFT,
        )
        self.message_user(
            request,
            ngettext(
                "%d post was reverted to draft.",
                "%d posts were reverted to draft.",
                updated,
            )
            % updated,
        )
