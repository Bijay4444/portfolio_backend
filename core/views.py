"""API views for core domain models.

Endpoints:
    GET  /api/v1/core/profile/          — retrieve singleton portfolio owner profile
    GET  /api/v1/core/social-links/     — list active social links
    POST /api/v1/core/contact/          — submit a contact form message

All endpoints are public (AllowAny). Write operations on Profile and
SocialLink happen exclusively through Django Admin — no API write endpoints.
"""

from __future__ import annotations

import logging

from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from common.constants import LoggerNames
from common.exceptions import NotFoundError
from common.pagination import LimitOffsetPagination, get_paginated_response
from common.responses import success_response
from core.models import ContactSubmission, Profile, SocialLink
from core.serializers import (
    ContactSubmissionInputSerializer,
    ContactSubmissionOutputSerializer,
    ProfileOutputSerializer,
    SocialLinkOutputSerializer,
)

logger = logging.getLogger(LoggerNames.PORTFOLIO)


@extend_schema_view(
    retrieve=extend_schema(
        summary="Retrieve portfolio owner profile",
        description=(
            "Returns the singleton Profile for this portfolio deployment. "
            "Includes nested active social links, avatar URL, and resume URL."
        ),
        responses={
            200: OpenApiResponse(
                response=ProfileOutputSerializer,
                description="Profile retrieved successfully.",
            ),
            404: OpenApiResponse(description="No profile configured yet."),
        },
        tags=["core:profile"],
    ),
)
class ProfileViewSet(RetrieveModelMixin, GenericViewSet):
    """Read-only ViewSet for the singleton Profile model.

    Only supports retrieve (GET /profile/).
    Frontend always calls /api/v1/core/profile/ — no UUID needed.
    """

    serializer_class = ProfileOutputSerializer
    permission_classes = [AllowAny]
    throttle_classes = []  # public read — global AnonRateThrottle applies

    def get_object(self) -> Profile:
        """Return the singleton Profile, raising NotFoundError if not configured.

        Returns:
            The single Profile instance for this deployment.

        Raises:
            NotFoundError: If no Profile row exists yet.
        """
        profile = Profile.objects.prefetch_related("social_links").first()

        if profile is None:
            raise NotFoundError(
                "Portfolio profile is not configured yet.",
                extra={"hint": "Create a Profile in Django Admin."},
            )
        return profile

    def retrieve(self, request: Request, *args, **kwargs) -> success_response:
        """Return the singleton portfolio profile.

        Args:
            request: The incoming DRF request.
            *args: Passed through.
            **kwargs: Passed through.

        Returns:
            Success response containing serialized Profile data.
        """
        profile = self.get_object()
        serializer = self.get_serializer(profile, context={"request": request})

        logger.info("Profile retrieved | profile=%s", profile.full_name)

        return success_response(data=serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="List active social links",
        description=(
            "Returns paginated active social links ordered alphabetically by platform. "
            "Query params: limit (default 10), offset (default 0)."
        ),
        responses={
            200: OpenApiResponse(
                response=SocialLinkOutputSerializer(many=True),
                description="Social links retrieved successfully.",
            ),
        },
        tags=["core:social-links"],
    ),
    retrieve=extend_schema(
        summary="Retrieve a single social link",
        description="Returns a single active social link by UUID.",
        responses={
            200: OpenApiResponse(
                response=SocialLinkOutputSerializer,
                description="Social link retrieved successfully.",
            ),
            404: OpenApiResponse(description="Social link not found."),
        },
        tags=["core:social-links"],
    ),
)
class SocialLinkViewSet(ReadOnlyModelViewSet):
    """Read-only ViewSet for active SocialLink entries.

    Supports list (paginated) and retrieve.
    Filters inactive links at queryset level.
    Uses common.pagination.LimitOffsetPagination.
    """

    serializer_class = SocialLinkOutputSerializer
    permission_classes = [AllowAny]
    throttle_classes = []  # public read — global AnonRateThrottle applies
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        """Return only active social links, ordered by platform.

        Returns:
            QuerySet of active SocialLink instances with profile selected.
        """
        return (
            SocialLink.objects.select_related("profile")
            .filter(is_active=True)
            .order_by("platform")
        )

    def list(self, request: Request, *args, **kwargs) -> success_response:
        """Return paginated list of active social links.

        Args:
            request: The incoming DRF request.
            *args: Passed through.
            **kwargs: Passed through.

        Returns:
            Paginated success response containing serialized SocialLink list.
        """
        return get_paginated_response(
            pagination_class=LimitOffsetPagination,
            serializer_class=SocialLinkOutputSerializer,
            queryset=self.get_queryset(),
            request=request,
            view=self,
        )

    def retrieve(self, request: Request, *args, **kwargs) -> success_response:
        """Return a single active social link by pk.

        Args:
            request: The incoming DRF request.
            *args: Passed through.
            **kwargs: Passed through.

        Returns:
            Success response containing serialized SocialLink data.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data)


@extend_schema_view(
    create=extend_schema(
        summary="Submit a contact form message",
        description=(
            "Accepts a visitor contact form submission. "
            "Rate limited to 5 requests per hour per IP to prevent spam."
        ),
        request=ContactSubmissionInputSerializer,
        responses={
            201: OpenApiResponse(
                response=ContactSubmissionOutputSerializer,
                description="Message submitted successfully.",
            ),
            400: OpenApiResponse(description="Validation error — check errors field."),
            429: OpenApiResponse(description="Rate limit exceeded. Try again later."),
        },
        tags=["core:contact"],
    ),
)
class ContactSubmissionViewSet(CreateModelMixin, GenericViewSet):
    """Write-only ViewSet for ContactSubmission.

    Only supports create (POST /contact/).
    Rate limited to 5/hour via ScopedRateThrottle — contact_submit scope
    defined in REST_FRAMEWORK settings in base.py.
    """

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "contact_submit"

    def get_serializer_class(self):
        """Return input serializer for all actions on this viewset.

        Returns:
            ContactSubmissionInputSerializer.
        """
        return ContactSubmissionInputSerializer

    def create(self, request: Request, *args, **kwargs) -> success_response:
        """Validate and store a visitor contact form submission.

        Args:
            request: The incoming DRF request containing contact form data.
            *args: Passed through.
            **kwargs: Passed through.

        Returns:
            201 success response with the stored submission data.
        """
        input_serializer = ContactSubmissionInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        submission: ContactSubmission = input_serializer.save()

        logger.info(
            "Contact submission received | from=%s email=%s subject=%s",
            submission.full_name,
            submission.email,
            submission.subject,
        )

        output_serializer = ContactSubmissionOutputSerializer(submission)

        return success_response(
            data=output_serializer.data,
            message="Your message has been received. We'll be in touch soon.",
            status_code=status.HTTP_201_CREATED,
        )
