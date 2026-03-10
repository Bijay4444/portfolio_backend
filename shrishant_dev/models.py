"""shrishant_dev domain models — Shrishant's frontend developer portfolio data.

All models are specific to Shrishant's developer portfolio. They must never
be imported by core/, bijay_dev/, or other personal apps.

Tables created:
    shrishant_skillcategory  — skill groupings (Frontend, Frameworks, Tools…)
    shrishant_techstack      — individual tools/skills linked to a category
    shrishant_project        — portfolio projects with M2M tech stack
    shrishant_projectimage   — gallery images for a project
    shrishant_experience     — work history entries
    shrishant_education      — academic history entries
    shrishant_certification  — certificates and achievements
    shrishant_blogcategory   — blog post categories
    shrishant_blogtag        — blog post tags
    shrishant_blogpost       — full blog posts with SEO metadata
"""

from __future__ import annotations

import uuid

from django.core.validators import MaxLengthValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field

from common.base_model import TimeStampedModel

# Skills & Tech Stack

class SkillCategory(TimeStampedModel):
    """Groups individual tools/skills into named categories.

    Examples: Frontend, Frameworks, CSS, Build Tools, Testing.
    Managed exclusively via Django Admin.

    Attributes:
        name: Display label for the category (e.g. "Frontend").
        order: Controls display order on the portfolio page.
    """

    name: models.CharField = models.CharField(
        max_length=100,
        unique=True,
        help_text=_("Category label shown on the portfolio (e.g. 'Frontend')."),
    )
    order: models.PositiveSmallIntegerField = models.PositiveSmallIntegerField(
        default=0,
        help_text=_("Display order — lower numbers appear first."),
    )

    class Meta:
        verbose_name = "Skill Category"
        verbose_name_plural = "Skill Categories"
        ordering = ["order", "name"]
        db_table = "shrishant_skillcategory"

    def __str__(self) -> str:
        return self.name


class TechStack(TimeStampedModel):
    """A single tool or skill belonging to a SkillCategory.

    Examples: React (under Frameworks), Tailwind CSS (under CSS).
    Managed exclusively via Django Admin.

    Attributes:
        category: The SkillCategory this tool belongs to.
        name: Tool or skill name (e.g. "React").
        icon: Uploaded icon image displayed on the portfolio.
        is_featured: Highlights this skill in the "key skills" section.
        order: Controls display order within the category.
    """

    category: models.ForeignKey = models.ForeignKey(
        SkillCategory,
        on_delete=models.PROTECT,
        related_name="skills",
        help_text=_("Category this tool or skill belongs to."),
    )
    name: models.CharField = models.CharField(
        max_length=100,
        help_text=_("Tool or skill name (e.g. 'React')."),
    )
    icon: models.ImageField = models.ImageField(
        upload_to="shrishant/techstack/icons/",
        blank=True,
        help_text=_("Icon image. Recommended: SVG/PNG, square, transparent bg."),
    )
    is_featured: models.BooleanField = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_("Show this skill in the featured / hero skills section."),
    )
    order: models.PositiveSmallIntegerField = models.PositiveSmallIntegerField(
        default=0,
        help_text=_("Display order within the category. Lower = first."),
    )

    class Meta:
        verbose_name = "Tech Stack / Skill"
        verbose_name_plural = "Tech Stack / Skills"
        ordering = ["category__order", "order", "name"]
        db_table = "shrishant_techstack"
        constraints = [
            models.UniqueConstraint(
                fields=["category", "name"],
                name="shrishant_unique_skill_per_category",
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.category.name})"


# Projects

class Project(TimeStampedModel):
    """A portfolio project showcasing Shrishant's frontend work.

    Projects are linked to TechStack entries via M2M. Only active projects
    are shown on the frontend; archived projects remain accessible in Admin.
    Gallery images are stored in the related ProjectImage model.

    Attributes:
        title: Project name displayed on the portfolio.
        description: Rich-text project description with CKEditor 5.
        thumbnail: Cover image shown in the project card grid.
        github_url: Link to the public GitHub repository.
        live_url: Link to the live/demo deployment (optional).
        status: ACTIVE = shown on portfolio; ARCHIVED = hidden from public.
        is_featured: Pins the project to the featured projects section.
        tech_stack: Many-to-many link to TechStack entries used in project.
        order: Overrides default ordering when set.
    """

    class Status(models.TextChoices):
        ACTIVE = "active", _("Active")
        ARCHIVED = "archived", _("Archived")

    title: models.CharField = models.CharField(
        max_length=200,
        help_text=_("Project name displayed on the portfolio."),
    )
    description: CKEditor5Field = CKEditor5Field(
        config_name="default",
        help_text=_(
            "Rich-text project description. Supports code blocks, links, lists."
        ),
    )
    thumbnail: models.ImageField = models.ImageField(
        upload_to="shrishant/projects/thumbnails/",
        blank=True,
        help_text=_("Cover image for the project card. Recommended: 16:9 ratio."),
    )
    github_url: models.URLField = models.URLField(
        blank=True,
        help_text=_("Public GitHub repository URL."),
    )
    live_url: models.URLField = models.URLField(
        blank=True,
        help_text=_("Live deployment or demo URL."),
    )
    status: models.CharField = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
        help_text=_("Active = shown on portfolio. Archived = hidden from public."),
    )
    is_featured: models.BooleanField = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_("Pin this project to the featured projects section."),
    )
    tech_stack: models.ManyToManyField = models.ManyToManyField(
        TechStack,
        related_name="projects",
        blank=True,
        help_text=_("Technologies used in this project."),
    )
    order: models.PositiveSmallIntegerField = models.PositiveSmallIntegerField(
        default=0,
        help_text=_("Manual display order. Lower = first. 0 = use default ordering."),
    )

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ["order", "-created_at"]
        db_table = "shrishant_project"

    def __str__(self) -> str:
        return self.title


class ProjectImage(TimeStampedModel):
    """A gallery image belonging to a Project.

    Allows admin to upload multiple images per project for a visual showcase.
    Displayed as an image gallery on the project detail page.

    Attributes:
        project: The parent project this image belongs to.
        image: The uploaded gallery image.
        caption: Optional short description of the image.
        alt_text: Accessibility alt text for screen readers and SEO.
        order: Controls display order in the gallery.
    """

    project: models.ForeignKey = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="images",
        help_text=_("The project this gallery image belongs to."),
    )
    image: models.ImageField = models.ImageField(
        upload_to="shrishant/projects/gallery/",
        help_text=_("Gallery image. Recommended: high-res screenshot or mockup."),
    )
    caption: models.CharField = models.CharField(
        max_length=300,
        blank=True,
        help_text=_("Optional short description of this image."),
    )
    alt_text: models.CharField = models.CharField(
        max_length=300,
        blank=True,
        help_text=_("Accessibility alt text for screen readers and SEO."),
    )
    order: models.PositiveSmallIntegerField = models.PositiveSmallIntegerField(
        default=0,
        help_text=_("Display order in the gallery. Lower = first."),
    )

    class Meta:
        verbose_name = "Project Image"
        verbose_name_plural = "Project Images"
        ordering = ["order", "-created_at"]
        db_table = "shrishant_projectimage"

    def __str__(self) -> str:
        return f"{self.project.title} — Image {self.order}"


# Experience

class Experience(TimeStampedModel):
    """A work history entry.

    Displayed in the Experience / Work History section of the portfolio.
    If is_current is True, end_date is ignored on the frontend
    and displayed as "Present".

    Attributes:
        title: Entry heading (e.g. "Frontend Developer at Acme Corp").
        company: Company or organisation name.
        role: Specific role/position held.
        description: Responsibilities and achievements (plain text or rich text).
        start_date: Month/year the role started.
        end_date: Month/year the role ended. Null when is_current=True.
        is_current: True when this is the current job (hides end_date).
        company_url: Company website URL.
        location: City/country or "Remote".
    """

    title: models.CharField = models.CharField(
        max_length=200,
        help_text=_("Entry heading e.g. 'Frontend Developer at Acme Corp'."),
    )
    company: models.CharField = models.CharField(
        max_length=200,
        help_text=_("Company or organisation name."),
    )
    role: models.CharField = models.CharField(
        max_length=200,
        help_text=_("Specific role/position title held at this company."),
    )
    description: models.TextField = models.TextField(
        blank=True,
        help_text=_("Key responsibilities and achievements."),
    )
    start_date: models.DateField = models.DateField(
        help_text=_("Month/year the role started (day value is ignored)."),
    )
    end_date: models.DateField = models.DateField(
        null=True,
        blank=True,
        help_text=_("Month/year the role ended. Leave blank when is_current=True."),
    )
    is_current: models.BooleanField = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_(
            "Check if this is your current job. Displays 'Present' on frontend."
        ),
    )
    company_url: models.URLField = models.URLField(
        blank=True,
        help_text=_("Company website URL."),
    )
    location: models.CharField = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("City/country or 'Remote'."),
    )

    class Meta:
        verbose_name = "Experience"
        verbose_name_plural = "Experiences"
        ordering = ["-is_current", "-start_date"]
        db_table = "shrishant_experience"

    def __str__(self) -> str:
        return f"{self.role} at {self.company}"


# Education

class Education(TimeStampedModel):
    """An academic history entry.

    Displayed in the Education section of the portfolio.

    Attributes:
        title: Entry heading (e.g. "Bachelor of Computer Science").
        institution: University, college, or school name.
        degree: Degree or qualification type (e.g. "Bachelor's").
        field_of_study: Subject area (e.g. "Computer Science").
        start_date: Start of the programme.
        end_date: End/graduation date. Null when still ongoing.
        description: Optional notes, achievements, or highlights.
    """

    title: models.CharField = models.CharField(
        max_length=200,
        help_text=_(
            "Entry heading e.g. 'B.Sc. Computer Science — Tribhuvan University'."
        ),
    )
    institution: models.CharField = models.CharField(
        max_length=200,
        help_text=_("University, college, or school name."),
    )
    degree: models.CharField = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('Degree or qualification type e.g. "Bachelor\'s".'),
    )
    field_of_study: models.CharField = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("Subject area e.g. 'Computer Science'."),
    )
    start_date: models.DateField = models.DateField(
        help_text=_("Programme start date (day value is ignored)."),
    )
    end_date: models.DateField = models.DateField(
        null=True,
        blank=True,
        help_text=_("Graduation or end date. Leave blank if still ongoing."),
    )
    description: models.TextField = models.TextField(
        blank=True,
        help_text=_("Optional notes, achievements, or academic highlights."),
    )

    class Meta:
        verbose_name = "Education"
        verbose_name_plural = "Education"
        ordering = ["-start_date"]
        db_table = "shrishant_education"

    def __str__(self) -> str:
        return f"{self.title} — {self.institution}"


# Certification / Achievement

class Certification(TimeStampedModel):
    """A certificate or professional achievement.

    Displayed in the Certifications section of the portfolio.

    Attributes:
        title: Certificate or achievement name.
        issuer: Awarding body (e.g. "freeCodeCamp", "Meta").
        issued_date: Date the certificate was issued.
        credential_url: Verification/credential link (optional).
        image: Certificate image or badge uploaded via Admin.
    """

    title: models.CharField = models.CharField(
        max_length=200,
        help_text=_("Certificate or achievement name."),
    )
    issuer: models.CharField = models.CharField(
        max_length=200,
        help_text=_("Awarding body e.g. 'freeCodeCamp', 'Meta'."),
    )
    issued_date: models.DateField = models.DateField(
        null=True,
        blank=True,
        help_text=_("Date the certificate was issued."),
    )
    credential_url: models.URLField = models.URLField(
        blank=True,
        help_text=_("Public verification or credential URL."),
    )
    image: models.ImageField = models.ImageField(
        upload_to="shrishant/certifications/",
        blank=True,
        help_text=_("Certificate image or digital badge."),
    )

    class Meta:
        verbose_name = "Certification"
        verbose_name_plural = "Certifications"
        ordering = ["-issued_date"]
        db_table = "shrishant_certification"

    def __str__(self) -> str:
        return f"{self.title} — {self.issuer}"


# Blog

def _blog_hero_upload_path(instance: BlogPost, filename: str) -> str:
    """Generate a collision-safe upload path for blog hero images."""
    ext = filename.rsplit(".", 1)[-1].lower()
    slug_part = slugify(instance.slug or instance.title or "post")[:50]
    unique_id = uuid.uuid4().hex[:8]
    return f"shrishant/blog/heroes/{slug_part}-{unique_id}.{ext}"


class BlogCategory(TimeStampedModel):
    """Category for grouping blog posts by topic.

    Slugs are auto-generated on creation and never mutated afterwards
    to prevent URL breakage and SEO damage.

    Attributes:
        name: Human-readable category label.
        slug: URL-safe identifier (immutable after creation).
        description: Optional CKEditor5 description for the category page.
        meta_description: SEO meta description (plain text, ≤160 chars).
    """

    name: models.CharField = models.CharField(
        max_length=160,
        unique=True,
        db_index=True,
        help_text=_("Category display label e.g. 'Frontend Engineering'."),
    )
    slug: models.SlugField = models.SlugField(
        max_length=180,
        unique=True,
        help_text=_("URL-safe identifier. Auto-generated; do not edit after creation."),
    )
    description: CKEditor5Field = CKEditor5Field(
        config_name="default",
        blank=True,
        help_text=_("Optional rich-text description for the category page."),
    )
    meta_description: models.CharField = models.CharField(
        max_length=160,
        blank=True,
        validators=[MaxLengthValidator(160)],
        help_text=_(
            "SEO meta description for the category page (plain text, ≤160 chars)."
        ),
    )

    class Meta:
        verbose_name = "Blog Category"
        verbose_name_plural = "Blog Categories"
        ordering = ["name"]
        db_table = "shrishant_blogcategory"

    def __str__(self) -> str:
        return self.name

    def save(self, *args: object, **kwargs: object) -> None:
        """Auto-generate slug on first save only."""
        if self._state.adding and not self.slug:
            base = slugify(self.name)
            candidate = base
            counter = 1
            while BlogCategory.objects.filter(slug=candidate).exists():
                candidate = f"{base}-{counter}"
                counter += 1
            self.slug = candidate
        super().save(*args, **kwargs)


class BlogTag(TimeStampedModel):
    """Tag for fine-grained blog post classification.

    Slugs are auto-generated on creation and never mutated.

    Attributes:
        name: Tag display label.
        slug: URL-safe identifier (immutable after creation).
        color_hex: Hex colour for the tag pill UI element.
    """

    name: models.CharField = models.CharField(
        max_length=80,
        unique=True,
        db_index=True,
        help_text=_("Tag display label."),
    )
    slug: models.SlugField = models.SlugField(
        max_length=100,
        unique=True,
        help_text=_("URL-safe identifier. Auto-generated; do not edit after creation."),
    )
    color_hex: models.CharField = models.CharField(
        max_length=7,
        default="#3b82f6",
        help_text=_("Hex colour for the tag UI pill e.g. '#3b82f6'."),
    )

    class Meta:
        verbose_name = "Blog Tag"
        verbose_name_plural = "Blog Tags"
        ordering = ["name"]
        db_table = "shrishant_blogtag"

    def __str__(self) -> str:
        return self.name

    def save(self, *args: object, **kwargs: object) -> None:
        """Auto-generate slug on first save only."""
        if self._state.adding and not self.slug:
            base = slugify(self.name)
            candidate = base
            counter = 1
            while BlogTag.objects.filter(slug=candidate).exists():
                candidate = f"{base}-{counter}"
                counter += 1
            self.slug = candidate
        super().save(*args, **kwargs)


class BlogPost(TimeStampedModel):
    """Full blog post with rich content, SEO metadata, and Open Graph support.

    Slugs are auto-generated on creation and never mutated.
    published_at is auto-set when status transitions to PUBLISHED.
    Only one post can be featured at a time — save() enforces this.

    Attributes:
        title: Post headline displayed at the top of the page.
        slug: URL-safe identifier (immutable after creation).
        excerpt: Short plain-text summary for cards and social previews.
        content: Full rich-text body edited via CKEditor 5.
        hero_image: Uploaded cover image (recommended 1200×630 px).
        is_featured: Pins this post as the hero/featured post.
        meta_title: Override title for SEO (≤60 chars).
        meta_description: SEO description (≤160 chars).
        og_title: Open Graph title for social sharing.
        og_description: Open Graph description for social sharing.
        status: DRAFT = not public; PUBLISHED = live on the blog.
        published_at: Auto-set on first publish, or manually overridden.
        view_count: Incrementing page view counter.
        categories: M2M to BlogCategory.
        tags: M2M to BlogTag.
        related_posts: Manually curated related posts (M2M self).
    """

    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        PUBLISHED = "published", _("Published")

    title: models.CharField = models.CharField(
        max_length=200,
        db_index=True,
        help_text=_("Post headline."),
    )
    slug: models.SlugField = models.SlugField(
        max_length=220,
        unique=True,
        help_text=_("URL-safe identifier. Auto-generated; do not edit after creation."),
    )
    excerpt: models.TextField = models.TextField(
        max_length=500,
        blank=True,
        help_text=_(
            "Short plain-text summary (≤500 chars) for cards and meta previews."
        ),
    )
    content: CKEditor5Field = CKEditor5Field(
        config_name="extends",
        help_text=_("Full rich-text post body. Supports code blocks, tables, images."),
    )
    hero_image: models.ImageField = models.ImageField(
        upload_to=_blog_hero_upload_path,
        blank=True,
        null=True,
        help_text=_("Cover image. Recommended: 1200×630 px for social sharing."),
    )
    is_featured: models.BooleanField = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_(
            "Feature this post as the hero post. Only one post is featured at a time."
        ),
    )
    # SEO
    meta_title: models.CharField = models.CharField(
        max_length=60,
        blank=True,
        validators=[MaxLengthValidator(60)],
        help_text=_("SEO title override (≤60 chars). Falls back to title if blank."),
    )
    meta_description: models.CharField = models.CharField(
        max_length=160,
        blank=True,
        validators=[MaxLengthValidator(160)],
        help_text=_(
            "SEO meta description (≤160 chars). Falls back to excerpt if blank."
        ),
    )
    # Open Graph
    og_title: models.CharField = models.CharField(
        max_length=95,
        blank=True,
        help_text=_(
            "Open Graph title for Facebook/LinkedIn (≤95 chars). Falls back to title."
        ),
    )
    og_description: models.CharField = models.CharField(
        max_length=200,
        blank=True,
        help_text=_(
            "Open Graph description (≤200 chars). Falls back to meta_description."
        ),
    )
    # Publication
    status: models.CharField = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        help_text=_("Draft = not public. Published = live on the blog."),
    )
    published_at: models.DateTimeField = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text=_("Auto-set when first published. Override to backdate."),
    )
    view_count: models.PositiveIntegerField = models.PositiveIntegerField(
        default=0,
        help_text=_("Page view counter incremented on each visit."),
    )
    # Relationships
    categories: models.ManyToManyField = models.ManyToManyField(
        BlogCategory,
        related_name="posts",
        blank=True,
        help_text=_("Topic categories for content clustering and SEO authority."),
    )
    tags: models.ManyToManyField = models.ManyToManyField(
        BlogTag,
        related_name="posts",
        blank=True,
        help_text=_(
            "Tags for fine-grained classification and related content discovery."
        ),
    )
    related_posts: models.ManyToManyField = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="related_to",
        blank=True,
        help_text=_("Manually curated related posts shown at the bottom of the post."),
    )

    class Meta:
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
        ordering = ["-published_at", "-created_at"]
        db_table = "shrishant_blogpost"
        indexes = [
            models.Index(fields=["status", "-published_at"]),
            models.Index(fields=["is_featured", "status"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["-view_count"]),
        ]

    def __str__(self) -> str:
        return self.title

    def save(self, *args: object, **kwargs: object) -> None:
        """Auto-generate slug; auto-set published_at; enforce single featured post."""
        if self._state.adding and not self.slug:
            base = slugify(self.title)
            candidate = base
            counter = 1
            while BlogPost.objects.filter(slug=candidate).exists():
                candidate = f"{base}-{counter}"
                counter += 1
            self.slug = candidate

        if self.status == self.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()

        if self.is_featured and self.status == self.Status.PUBLISHED:
            BlogPost.objects.filter(
                is_featured=True,
                status=self.Status.PUBLISHED,
            ).exclude(pk=self.pk).update(is_featured=False)

        super().save(*args, **kwargs)

    def get_read_time(self) -> int:
        """Return estimated read time in minutes (200 wpm baseline)."""
        word_count = len(self.content.split())
        return max(1, round(word_count / 200))

    def is_published(self) -> bool:
        """True when publicly visible on the blog."""
        return (
            self.status == self.Status.PUBLISHED
            and self.published_at is not None
            and self.published_at <= timezone.now()
        )

    def increment_view_count(self) -> None:
        """Atomically increment the view counter without a full model fetch."""
        BlogPost.objects.filter(pk=self.pk).update(
            view_count=models.F("view_count") + 1
        )
