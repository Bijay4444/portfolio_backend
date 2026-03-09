"""Serializers for core domain models.

Naming convention:
    <Model>OutputSerializer  — read operations (GET) — nested, fully expanded
    <Model>InputSerializer   — write operations (POST/PUT/PATCH) — flat, validated

ContactSubmission has InputSerializer only (POST from contact form).
Profile and SocialLink have OutputSerializer only (read-only via API —
writes happen through Django Admin exclusively).
"""

from __future__ import annotations

from rest_framework import serializers

from core.models import ContactSubmission, Profile, SocialLink


class SocialLinkOutputSerializer(serializers.ModelSerializer):
    """Read serializer for SocialLink — used nested inside ProfileOutputSerializer.

    Attributes:
        platform_display: Human-readable platform label from TextChoices.
    """

    platform_display: serializers.CharField = serializers.CharField(
        source="get_platform_display",
        read_only=True,
    )

    class Meta:
        model = SocialLink
        fields = (
            "id",
            "platform",
            "platform_display",
            "url",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


class ProfileOutputSerializer(serializers.ModelSerializer):
    """Read serializer for Profile — fully expanded with nested social links.

    Only active social links are included — inactive ones are filtered
    at the serializer level, not the queryset, since Profile is a singleton
    and always fetched as a single object.

    Attributes:
        social_links: Nested list of active SocialLink objects.
        avatar_url: Absolute URL to the avatar image.
        resume_url: Absolute URL to the resume file. Null if not uploaded.
    """

    social_links: SocialLinkOutputSerializer = SocialLinkOutputSerializer(
        many=True,
        read_only=True,
        source="active_social_links",
    )
    avatar_url: serializers.SerializerMethodField = serializers.SerializerMethodField()
    resume_url: serializers.SerializerMethodField = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            "id",
            "full_name",
            "tagline",
            "bio",
            "role",
            "email",
            "phone",
            "location",
            "is_available",
            "avatar_url",
            "resume_url",
            "social_links",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )

    def get_avatar_url(self, obj: Profile) -> str | None:
        """Return absolute URL for avatar image.

        Args:
            obj: The Profile instance being serialized.

        Returns:
            Absolute URL string, or None if no avatar is set.
        """
        if not obj.avatar:
            return None
        request = self.context.get("request")
        if request is not None:
            return request.build_absolute_uri(obj.avatar.url)
        return obj.avatar.url

    def get_resume_url(self, obj: Profile) -> str | None:
        """Return absolute URL for resume file.

        Args:
            obj: The Profile instance being serialized.

        Returns:
            Absolute URL string, or None if no resume is uploaded.
        """
        if not obj.resume:
            return None
        request = self.context.get("request")
        if request is not None:
            return request.build_absolute_uri(obj.resume.url)
        return obj.resume.url


class ContactSubmissionInputSerializer(serializers.ModelSerializer):
    """Write serializer for ContactSubmission — used on POST /api/v1/core/contact/.

    Validates visitor-submitted contact form data before saving.
    All fields are required except subject (has a sensible default).

    Note:
        is_read and created_at are never accepted from the client —
        they are set server-side only.
    """

    class Meta:
        model = ContactSubmission
        fields = (
            "full_name",
            "email",
            "subject",
            "message",
        )

    def validate_message(self, value: str) -> str:
        """Reject suspiciously short messages (likely spam or accidental submits).

        Args:
            value: The raw message string from the request.

        Returns:
            The validated message string.

        Raises:
            serializers.ValidationError: If message is under 10 characters.
        """
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Message must be at least 10 characters."
            )
        return value.strip()

    def validate_full_name(self, value: str) -> str:
        """Strip whitespace and reject blank-after-strip names.

        Args:
            value: The raw full_name string from the request.

        Returns:
            The stripped full_name string.

        Raises:
            serializers.ValidationError: If name is blank after stripping.
        """
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Full name cannot be blank.")
        return stripped


class ContactSubmissionOutputSerializer(serializers.ModelSerializer):
    """Read serializer for ContactSubmission — used in Admin API or submission confirmation.

    Returns the saved submission back to the caller after a successful POST,
    confirming what was stored without exposing is_read (internal field).
    """

    class Meta:
        model = ContactSubmission
        fields = (
            "id",
            "full_name",
            "email",
            "subject",
            "message",
            "created_at",
        )
        read_only_fields = (
            "id",
            "created_at",
        )