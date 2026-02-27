"""Custom DRF exception handler for the portfolio backend.

Converts all exceptions — Django, DRF, and application-level — into a
single consistent JSON shape consumed by the Next.js frontend:

    Success:
        {"status": "success", "data": {...}, "message": null}

    Error:
        {"status": "error", "data": null, "message": "...", "errors": {...}}

Design follows HackSoft Django Styleguide with adaptations for this project's
response envelope.
Reference: https://github.com/HackSoftware/Django-Styleguide#errors--exception-handling
"""

from __future__ import annotations

import logging

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework import exceptions as drf_exceptions
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import as_serializer_error
from rest_framework.views import exception_handler as drf_exception_handler

from common.exceptions import ApplicationError, ConflictError, NotFoundError
from common.exceptions import PermissionError as AppPermissionError

logger = logging.getLogger("portfolio")


def custom_exception_handler(exc: Exception, context: dict) -> Response | None:
    """Convert any exception into a consistent JSON error envelope.

    Resolution order:
        1. Django ValidationError           → 400 with field errors
        2. Django Http404                   → 404
        3. Django PermissionDenied          → 403
        4. ApplicationError subclasses      → mapped HTTP status
        5. DRF APIException subclasses      → handled by DRF, reformatted
        6. Everything else                  → None → Django 500 (for Sentry/monitoring)

    Args:
        exc: The raised exception.
        context: DRF context dict containing 'request' and 'view'.

    Returns:
        A Response with the error envelope, or None for unhandled exceptions.
    """
    request: Request = context.get("request")

    # Django → DRF conversions 
    if isinstance(exc, DjangoValidationError):
        exc = _django_validation_to_drf(exc)

    elif isinstance(exc, Http404):
        exc = drf_exceptions.NotFound()

    elif isinstance(exc, DjangoPermissionDenied):
        exc = drf_exceptions.PermissionDenied()

    # Application-level exceptions 
    elif isinstance(exc, (ApplicationError, NotFoundError, AppPermissionError, ConflictError)):
        return _handle_application_error(exc, request)

    # DRF exceptions → reformatted envelope 
    response = drf_exception_handler(exc, context)

    if response is None:
        # Unhandled: let it become a 500 so Sentry/logging catches it.
        logger.exception(
            "Unhandled exception in view | path=%s",
            getattr(request, "path", "unknown"),
            exc_info=exc,
        )
        return None

    return _wrap_drf_response(response, exc)


# Private helpers

def _django_validation_to_drf(exc: DjangoValidationError) -> drf_exceptions.ValidationError:
    """Convert Django's ValidationError to a DRF ValidationError.

    Args:
        exc: Django ValidationError (may have message_dict for field errors).

    Returns:
        DRF ValidationError with equivalent detail structure.
    """
    if hasattr(exc, "message_dict"):
        return drf_exceptions.ValidationError(detail=as_serializer_error(exc))
    return drf_exceptions.ValidationError(detail=exc.messages)


def _handle_application_error(exc: ApplicationError, request: Request | None) -> Response:
    """Build an error envelope Response from an ApplicationError subclass.

    Args:
        exc: The raised ApplicationError (or subclass).
        request: The current DRF request (used for path logging).

    Returns:
        Response with appropriate HTTP status and error envelope.
    """
    status_map: dict[type[ApplicationError], int] = {
        NotFoundError: status.HTTP_404_NOT_FOUND,
        AppPermissionError: status.HTTP_403_FORBIDDEN,
        ConflictError: status.HTTP_409_CONFLICT,
        ApplicationError: status.HTTP_400_BAD_REQUEST,
    }

    http_status = status_map.get(type(exc), status.HTTP_400_BAD_REQUEST)

    logger.warning(
        "Application error | type=%s message=%s path=%s extra=%s",
        type(exc).__name__,
        exc.message,
        getattr(request, "path", "unknown"),
        exc.extra,
    )

    return Response(
        _error_envelope(exc.message),
        status=http_status,
    )


def _wrap_drf_response(response: Response, exc: Exception) -> Response:
    """Reformat a DRF-handled response into the project error envelope.

    Args:
        response: The Response object returned by DRF's default handler.
        exc: The original exception (used to distinguish validation vs other).

    Returns:
        The same Response object with data replaced by the error envelope.
    """
    if isinstance(exc, drf_exceptions.ValidationError):
        message, errors = _extract_validation_detail(response.data)
        response.data = _error_envelope(message, errors=errors)
    else:
        message = _extract_detail_message(response.data)
        response.data = _error_envelope(message)

    return response


def _extract_validation_detail(data: dict | list | str) -> tuple[str, dict]:
    """Pull (message, errors) out of a DRF ValidationError response payload.

    Args:
        data: Raw response.data from DRF's ValidationError handler.

    Returns:
        Tuple of (human-readable message, field-errors dict).
    """
    if isinstance(data, dict):
        if "detail" in data:
            detail = data["detail"]
            if isinstance(detail, str):
                return detail, {}
            if isinstance(detail, list) and detail:
                return str(detail[0]), {"non_field_errors": detail}
            return "Validation error.", {}
        # Field-level errors dict — pick first message as summary
        first_field = next(iter(data.values()), None)
        if isinstance(first_field, list) and first_field:
            return str(first_field[0]), data
        return "Validation error.", data

    if isinstance(data, list) and data:
        return str(data[0]), {"non_field_errors": data}

    return str(data), {}


def _extract_detail_message(data: dict | list | str) -> str:
    """Extract a plain string message from any DRF exception response payload.

    Args:
        data: Raw response.data from DRF's exception handler.

    Returns:
        A plain string suitable for the envelope's "message" field.
    """
    if isinstance(data, dict) and "detail" in data:
        return str(data["detail"])
    if isinstance(data, list) and data:
        return str(data[0])
    return str(data)


def _error_envelope(message: str, errors: dict | None = None) -> dict:
    """Build the standard error response envelope.

    Args:
        message: Human-readable error summary.
        errors: Optional field-level error dict (validation errors only).

    Returns:
        Dict matching {"status": "error", "data": null, "message": ..., "errors": ...}.
    """
    envelope: dict = {
        "status": "error",
        "data": None,
        "message": message,
    }
    if errors:
        envelope["errors"] = errors
    return envelope