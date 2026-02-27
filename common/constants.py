"""Shared constants for the portfolio backend monorepo.

App-specific constants live in their own constants.py (e.g. bijay_dev/constants.py).
Only values shared across multiple apps belong here.
"""

from __future__ import annotations


class PaginationDefaults:
    """Pagination limits applied by common.pagination.LimitOffsetPagination."""

    DEFAULT_LIMIT: int = 10
    MAX_LIMIT: int = 100


class ResponseStatus:
    """String literals for the 'status' field in every API response envelope.

    Usage:
        from common.constants import ResponseStatus
        payload = {"status": ResponseStatus.SUCCESS, "data": ..., "message": None}
    """

    SUCCESS: str = "success"
    ERROR: str = "error"


class LoggerNames:
    """Centralised logger name registry.

    All modules should obtain loggers via:
        logger = logging.getLogger(LoggerNames.PORTFOLIO)

    This ensures every log line has a consistent name prefix visible in
    the LOGGING config in config/settings/base.py.
    """

    PORTFOLIO: str = "portfolio"