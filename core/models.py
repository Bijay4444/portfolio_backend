"""Core domain models shared across all portfolio deployments.

Every portfolio (bijay_dev, uiux_dev, frontend_dev) uses these models.
Only models that are IDENTICAL across all three portfolios live here.

Tables created:
    core_profile            — singleton portfolio owner profile
    core_sociallink         — owner's social media links (FK → Profile)
    core_contactsubmission  — visitor-submitted contact form messages
"""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field

from common.base_model import TimeStampedModel


class Profile(TimeStampedModel):
    """Portfolio owner profile — singleton row per deployment.

    Enforces one-row-only at the model level via clean() and save().
    Managed exclusively through Django Admin — no API write endpoint.

    Attributes:
        full_name: Display name shown on the portfolio homepage.
        tagline: Short punchy one-liner shown under the name.
        bio: Rich-text description edited via CKEditor 5 in Django Admin.
        avatar: Profile picture uploaded via Django Admin.
        resume: PDF resume uploaded via Django Admin, served from MEDIA_ROOT.
        role: Job title e.g. "Backend Engineer".
        email: Contact email displayed publicly on the portfolio.
        phone: Optional contact phone number.
        location: City/country string e.g. "Kathmandu, Nepal".
        is_available: Toggles the "open to work" indicator on the frontend.
    """

    full_name: models.CharField = models.CharField(
        max_length=100,
        help_text=_("Full display name shown on the portfolio."),
    )
    tagline: models.CharField = models.CharField(
        max_length=160,
        blank=True,
        help_text=_("Short one-liner shown under your name. Max 160 chars."),
    )
    bio: CKEditor5Field = CKEditor5Field(
        config_name="default",
        help_text=_("Rich-text biography. Supports formatting, links, lists."),
    )
    avatar: models.ImageField = models.ImageField(
        upload_to="core/avatars/",
        help_text=_("Profile picture. Recommended: square, min 400×400px."),
    )
    resume: models.FileField = models.FileField(
        upload_to="core/resumes/",
        blank=True,
        help_text=_("PDF resume. Served from MEDIA_ROOT in dev, nginx in prod."),
    )
    role: models.CharField = models.CharField(
        max_length=100,
        help_text=_("Job title e.g. 'Backend Engineer'."),
    )
    email: models.EmailField = models.EmailField(
        help_text=_("Public contact email displayed on the portfolio."),
    )
    phone: models.CharField = models.CharField(
        max_length=20,
        blank=True,
        help_text=_("Optional contact phone number."),
    )
    location: models.CharField = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("City/country string e.g. 'Kathmandu, Nepal'."),
    )
    is_available: models.BooleanField = models.BooleanField(
        default=False,
        help_text=_("Toggles the 'open to work' indicator on the frontend."),
    )

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profile"

    def __str__(self) -> str:
        """Return owner's full name as string representation."""
        return self.full_name

    def clean(self) -> None:
        """Enforce singleton constraint — only one Profile row per deployment.

        Raises:
            ValidationError: If a Profile row already exists and this is a new instance.
        """
        if not self.pk and Profile.objects.exists():
            raise ValidationError(
                _("Only one Profile can exist per deployment. Edit the existing one.")
            )

    def save(self, *args, **kwargs) -> None:
        """Run full validation before saving to enforce singleton constraint.

        Args:
            *args: Passed through to super().save().
            **kwargs: Passed through to super().save().
        """
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def active_social_links(self):
        """Return only active social links for this profile.

        Returns:
            QuerySet of SocialLink instances where is_active=True.
        """
        return self.social_links.filter(is_active=True)


class SocialLink(TimeStampedModel):
    """A single social media link belonging to the portfolio owner.

    New platforms can be added by inserting a row in Django Admin —
    no migration needed. Use is_active to hide without deleting.

    Attributes:
        profile: FK to the owner's Profile.
        platform: Platform identifier from Platform.choices.
        url: Full URL to the owner's profile on that platform.
        is_active: If False, the link is hidden from the frontend.
    """

    class Platform(models.TextChoices):
        """Supported social/professional platforms."""

        GITHUB = "github", "GitHub"
        LINKEDIN = "linkedin", "LinkedIn"
        TWITTER = "twitter", "Twitter"
        DEVTO = "devto", "Dev.to"
        INSTAGRAM = "instagram", "Instagram"
        YOUTUBE = "youtube", "YouTube"
        WEBSITE = "website", "Personal Website"
        MEDIUM = "medium" , "medium"

    profile: models.ForeignKey = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="social_links",
        help_text=_("Portfolio owner this link belongs to."),
    )
    platform: models.CharField = models.CharField(
        max_length=20,
        choices=Platform.choices,
        help_text=_("Social platform identifier."),
    )
    url: models.URLField = models.URLField(
        help_text=_("Full URL to the owner's profile on this platform."),
    )
    is_active: models.BooleanField = models.BooleanField(
        default=True,
        help_text=_("Uncheck to hide this link from the frontend without deleting it."),
    )

    class Meta:
        verbose_name = "Social Link"
        verbose_name_plural = "Social Links"
        # One row per platform per profile — no duplicate GitHub links
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "platform"],
                name="unique_platform_per_profile",
            )
        ]
        ordering = ["platform"]

    def __str__(self) -> str:
        """Return platform name and URL as string representation."""
        return f"{self.get_platform_display()} → {self.url}"


class ContactSubmission(TimeStampedModel):
    """A message submitted by a portfolio visitor via the contact form.

    No FK to Profile — there is only one portfolio owner per deployment.
    Managed (read/mark-read) through Django Admin only.

    Attributes:
        full_name: Visitor's name as submitted.
        email: Visitor's reply-to email address.
        subject: Short subject line for the message.
        message: Full message body from the visitor.
        is_read: Toggled manually in Admin once the owner reads it.
    """

    full_name: models.CharField = models.CharField(
        max_length=100,
        help_text=_("Visitor's full name as submitted."),
    )
    email: models.EmailField = models.EmailField(
        help_text=_("Visitor's reply-to email address."),
    )
    subject: models.CharField = models.CharField(
        max_length=200,
        help_text=_("Short subject line describing the inquiry."),
    )
    message: models.TextField = models.TextField(
        help_text=_("Full message body from the visitor."),
    )
    is_read: models.BooleanField = models.BooleanField(
        default=False,
        help_text=_("Mark as read once reviewed. Managed in Django Admin."),
    )

    class Meta:
        verbose_name = "Contact Submission"
        verbose_name_plural = "Contact Submissions"
        ordering = ["-created_at"]  # newest first in Admin

    def __str__(self) -> str:
        """Return sender name and subject as string representation."""
        return f"{self.full_name} — {self.subject}"
