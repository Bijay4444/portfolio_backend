"""Django Admin registration for core models.

Features:
    Profile    — singleton editor with CKEditor 5 rich-text bio, inline social links
    SocialLink — managed inline from Profile page
    ContactSubmission — read-only list with mark-read bulk action, unread count badge
"""

from __future__ import annotations

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html, mark_safe
from django.utils.translation import gettext_lazy as _, ngettext

from core.models import ContactSubmission, Profile, SocialLink


class SocialLinkInline(admin.TabularInline):
    """Inline editor for SocialLinks on the Profile admin page."""

    model = SocialLink
    extra = 1
    fields = ("platform", "url", "is_active")
    ordering = ("platform",)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin view for the singleton Profile model.

    CKEditor 5 renders in the bio field automatically via django-ckeditor-5.
    Social links are managed inline — no separate admin page needed.
    """

    inlines = [SocialLinkInline]
    list_display = (
        "full_name",
        "role",
        "email",
        "location",
        "availability_badge",
        "updated_at",
    )
    readonly_fields = ("id", "created_at", "updated_at", "avatar_preview")
    search_fields = ("full_name", "email", "role", "location")
    fieldsets = (
        (
            _("Identity"),
            {
                "fields": (
                    "full_name",
                    "tagline",
                    "role",
                    ("avatar", "avatar_preview"),
                )
            },
        ),
        (
            _("About"),
            {
                "fields": ("bio", "resume"),
                "description": _(
                    "Bio supports rich text via CKEditor 5. "
                    "Resume PDF is served from MEDIA_ROOT."
                ),
            },
        ),
        (
            _("Contact Info"),
            {"fields": ("email", "phone", "location")},
        ),
        (
            _("Status"),
            {
                "fields": ("is_available",),
                "description": _(
                    "Toggle to show/hide the 'open to work' indicator on the frontend."
                ),
            },
        ),
        (
            _("Metadata"),
            {
                "fields": ("id", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description=_("Available"), boolean=False)
    def availability_badge(self, obj: Profile) -> str:
        """Render a coloured badge for open-to-work status.

        Args:
            obj: The Profile instance.

        Returns:
            Safe HTML string — green badge if available, grey if not.
        """
        if obj.is_available:
            return mark_safe(
                '<span style="color:#16a34a;font-weight:600;">● Open to work</span>'
            )
        return mark_safe(
            '<span style="color:#6b7280;">● Not available</span>'
        )

    @admin.display(description=_("Avatar preview"))
    def avatar_preview(self, obj: Profile) -> str:
        """Render a small inline preview of the uploaded avatar.

        Args:
            obj: The Profile instance.

        Returns:
            Safe HTML img tag, or placeholder text if no avatar uploaded.
        """
        if not obj.avatar:
            return _("No avatar uploaded.")
        return format_html(
            '<img src="{}" style="width:80px;height:80px;'
            'object-fit:cover;border-radius:50%;" />',
            obj.avatar.url,
        )

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Prevent creating a second Profile row from Admin.

        Args:
            request: The current admin HTTP request.

        Returns:
            False if a Profile already exists, True otherwise.
        """
        return not Profile.objects.exists()

    def has_delete_permission(
        self, request: HttpRequest, obj: Profile | None = None
    ) -> bool:
        """Prevent deleting the only Profile row.

        Args:
            request: The current admin HTTP request.
            obj: The Profile instance (if on change page).

        Returns:
            Always False — profile deletion is not permitted via Admin.
        """
        return False


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    """Admin view for visitor contact form submissions.

    Features:
        - Unread submissions are bolded in the list view.
        - Bulk action to mark multiple submissions as read.
        - All fields are read-only — no editing visitor messages.
        - Search by name, email, subject.
    """

    list_display = (
        "full_name",
        "email",
        "subject",
        "read_status_badge",
        "created_at",
    )
    list_filter = ("is_read", "created_at")
    search_fields = ("full_name", "email", "subject", "message")
    readonly_fields = (
        "id",
        "full_name",
        "email",
        "subject",
        "message",
        "is_read",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    actions = ["mark_as_read", "mark_as_unread"]
    fieldsets = (
        (
            _("Sender"),
            {"fields": ("full_name", "email")},
        ),
        (
            _("Message"),
            {"fields": ("subject", "message")},
        ),
        (
            _("Status"),
            {"fields": ("is_read",)},
        ),
        (
            _("Metadata"),
            {
                "fields": ("id", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description=_("Status"))
    def read_status_badge(self, obj: ContactSubmission) -> str:
        """Render a coloured read/unread badge.

        Args:
            obj: The ContactSubmission instance.

        Returns:
            Safe HTML string — orange badge if unread, grey if read.
        """
        if not obj.is_read:
            return mark_safe(
                '<span style="color:#ea580c;font-weight:600;">● Unread</span>'
            )
        return mark_safe('<span style="color:#6b7280;">✓ Read</span>')

    @admin.action(description=_("Mark selected submissions as read"))
    def mark_as_read(
        self, request: HttpRequest, queryset: QuerySet[ContactSubmission]
    ) -> None:
        """Bulk-mark selected submissions as read.

        Args:
            request: The current admin HTTP request.
            queryset: Selected ContactSubmission rows.
        """
        updated = queryset.update(is_read=True)
        self.message_user(
            request,
            # ngettext handles singular/plural + no f-string inside _()
            ngettext(
                "%(count)d submission marked as read.",
                "%(count)d submissions marked as read.",
                updated,
            ) % {"count": updated},
        )

    @admin.action(description=_("Mark selected submissions as unread"))
    def mark_as_unread(
        self, request: HttpRequest, queryset: QuerySet[ContactSubmission]
    ) -> None:
        """Bulk-mark selected submissions as unread.

        Args:
            request: The current admin HTTP request.
            queryset: Selected ContactSubmission rows.
        """
        updated = queryset.update(is_read=False)
        self.message_user(
            request,
            ngettext(
                "%(count)d submission marked as unread.",
                "%(count)d submissions marked as unread.",
                updated,
            ) % {"count": updated},
        )

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Disable manual creation — submissions come from the contact form only."""
        return False

    def has_change_permission(
        self, request: HttpRequest, obj: ContactSubmission | None = None
    ) -> bool:
        """Allow list view but block the change form — submissions are immutable.

        Django Admin needs has_change_permission=True to render the list view.
        We block it only when obj is present (i.e. on the change form page).

        Args:
            request: The current admin HTTP request.
            obj: None on list view, ContactSubmission instance on change page.

        Returns:
            False only when viewing a specific submission (change form).
        """
        return obj is None
