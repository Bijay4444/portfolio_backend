"""Standardized API response helpers for the portfolio backend.

All views must return responses through success_response() to guarantee
the envelope shape consumed by the Next.js frontend:

    Success:  {"status": "success", "data": ..., "message": null, "meta": {...}}
    Error:    {"status": "error",   "data": null, "message": "...", "errors": {...}}

The error envelope is built exclusively by common.exception_handler —
never call an error response builder directly from a view.
"""

from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.response import Response

from common.constants import ResponseStatus


def success_response(
    data: Any = None,
    message: str | None = None,
    status_code: int = status.HTTP_200_OK,
    meta: dict | None = None,
) -> Response:
    """Build a standardized success response envelope.

    Args:
        data: Serialized payload to return. None is valid (e.g. DELETE 204).
        message: Optional human-readable context ("Project created.").
        status_code: HTTP status code (default 200).
        meta: Optional metadata block — used for pagination info.

    Returns:
        DRF Response with the success envelope.

    Example:
        return success_response(
            data=ProjectOutputSerializer(project).data,
            message="Project created.",
            status_code=status.HTTP_201_CREATED,
        )
    """
    envelope: dict[str, Any] = {
        "status": ResponseStatus.SUCCESS,
        "data": data,
        "message": message,
    }
    if meta is not None:
        envelope["meta"] = meta

    return Response(envelope, status=status_code)
