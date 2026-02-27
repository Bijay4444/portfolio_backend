"""Domain-level exception classes for the portfolio backend.

These are raised in service/business logic layers and converted to
consistent JSON responses by common.exception_handler.custom_exception_handler.

Error response shape (all errors):
    {
        "status": "error",
        "data": null,
        "message": "<human readable>",
        "errors": { "field": ["msg"] }   # validation errors only
    }
"""

from __future__ import annotations


class ApplicationError(Exception):
    """Base exception for all application-level business logic errors.

    Raise this (or a subclass) from service functions when a business rule
    is violated. The exception handler converts it to a 400 JSON response.

    Args:
        message: Human-readable description of what went wrong.
        extra: Optional dict of additional context (logged, not exposed to client).

    Example:
        raise ApplicationError("Project slug already exists.", extra={"slug": slug})
    """

    def __init__(self, message: str, extra: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.extra = extra or {}


class NotFoundError(ApplicationError):
    """Raised when a requested resource does not exist.

    Results in a 404 response from the exception handler.

    Example:
        raise NotFoundError("Project not found.", extra={"id": str(pk)})
    """


class PermissionError(ApplicationError):  # noqa: A001
    """Raised when the authenticated user lacks permission for an action.

    Results in a 403 response from the exception handler.

    Example:
        raise PermissionError("You do not own this resource.")
    """


class ConflictError(ApplicationError):
    """Raised when an action conflicts with existing state (e.g. duplicate slug).

    Results in a 409 response from the exception handler.

    Example:
        raise ConflictError("A project with this slug already exists.")
    """