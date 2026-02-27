"""Custom DRF renderer that enforces the portfolio API response envelope.

Guarantees that every response — success or error — leaving the API
matches the contract expected by the Next.js frontend:

    Success:  {"status": "success", "data": ..., "message": null}
    Error:    {"status": "error",   "data": null, "message": "...", "errors": {...}}

Why a renderer instead of relying solely on success_response()?
    success_response() only wraps responses where the view author remembers
    to call it. A renderer wraps at the Django response layer — it is
    impossible to accidentally bypass.

Exceptions (not wrapped):
    - Binary responses (file downloads, images)
    - Already-wrapped responses (contain a "status" key) — idempotent guard
    - Non-dict/list payloads from DRF browsable API or schema endpoints
"""

from __future__ import annotations

import logging
from typing import Any

from rest_framework.renderers import JSONRenderer

from common.constants import LoggerNames, ResponseStatus

logger = logging.getLogger(LoggerNames.PORTFOLIO)

# Schema/docs endpoints that must not be wrapped — they have their own format.
_PASSTHROUGH_PATHS: frozenset[str] = frozenset(
    [
        "/api/schema/",
        "/api/docs/",
        "/api/redoc/",
    ]
)


class EnvelopeRenderer(JSONRenderer):
    """JSON renderer that wraps every API response in the standard envelope.

    Registered in REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] in base.py.
    No view-level configuration needed — it applies globally.

    Envelope shape:
        {
            "status": "success" | "error",
            "data":    <payload> | null,
            "message": <string>  | null,
            "errors":  <dict>    | absent       # validation errors only
            "meta":    <dict>    | absent       # pagination info only
        }
    """

    def render(
        self,
        data: Any,
        accepted_media_type: str | None = None,
        renderer_context: dict | None = None,
    ) -> bytes:
        """Wrap data in the envelope then delegate serialisation to JSONRenderer.

        Args:
            data: The response payload from the view or exception handler.
            accepted_media_type: Negotiated media type (passed through to super).
            renderer_context: DRF renderer context containing response/request/view.

        Returns:
            UTF-8 encoded JSON bytes of the wrapped envelope.
        """
        renderer_context = renderer_context or {}
        response = renderer_context.get("response")
        request = renderer_context.get("request")

        # Passthrough: schema/docs endpoints 
        if request is not None and self._is_passthrough(request):
            return super().render(data, accepted_media_type, renderer_context)

        # Passthrough: already wrapped (idempotent guard) 
        if isinstance(data, dict) and "status" in data and data["status"] in (
            ResponseStatus.SUCCESS,
            ResponseStatus.ERROR,
        ):
            return super().render(data, accepted_media_type, renderer_context)

        # Passthrough: non-dict/list (e.g. raw strings, binary) 
        if data is not None and not isinstance(data, (dict, list)):
            logger.warning(
                "EnvelopeRenderer received unexpected data type | type=%s",
                type(data).__name__,
            )
            return super().render(data, accepted_media_type, renderer_context)

        # Wrap 
        wrapped = self._wrap(data, response)
        return super().render(wrapped, accepted_media_type, renderer_context)

    # Private helpers

    def _is_passthrough(self, request: Any) -> bool:
        """Return True if the request path should bypass envelope wrapping.

        Args:
            request: DRF or Django request object.

        Returns:
            True if the path starts with any _PASSTHROUGH_PATHS entry.
        """
        path: str = getattr(request, "path", "")
        return any(path.startswith(p) for p in _PASSTHROUGH_PATHS)

    def _wrap(self, data: Any, response: Any) -> dict[str, Any]:
        """Build the envelope dict from raw response data.

        Determines success/error from HTTP status code. Error responses
        (built by exception_handler) already contain "message" and
        optionally "errors" — extract those cleanly.

        Args:
            data: Raw payload from the view or exception handler.
            response: DRF Response object (used to read status_code).

        Returns:
            Envelope dict ready for JSON serialisation.
        """
        status_code: int = getattr(response, "status_code", 200)
        is_error: bool = status_code >= 400

        if is_error:
            # exception_handler already shaped this as:
            # {"status": "error", "data": null, "message": "...", "errors": {...}}
            # If it somehow arrives raw, normalise it.
            if isinstance(data, dict):
                return {
                    "status": ResponseStatus.ERROR,
                    "data": None,
                    "message": data.get("message", "An error occurred."),
                    **({"errors": data["errors"]} if "errors" in data else {}),
                }
            return {
                "status": ResponseStatus.ERROR,
                "data": None,
                "message": str(data) if data else "An error occurred.",
            }

        # Success — extract meta if present (set by get_paginated_response)
        if isinstance(data, dict):
            return {
                "status": ResponseStatus.SUCCESS,
                "data": data.get("data", data),
                "message": data.get("message", None),
                **({"meta": data["meta"]} if "meta" in data else {}),
            }

        return {
            "status": ResponseStatus.SUCCESS,
            "data": data,
            "message": None,
        }