"""Shared utilities for the portfolio backend monorepo.

Available modules:
    base_model          — TimeStampedModel abstract base
    constants           — Shared constants (ResponseStatus, PaginationDefaults, LoggerNames)
    exceptions          — Domain-level exception classes
    exception_handler   — DRF exception → consistent JSON envelope
    pagination          — LimitOffsetPagination + get_paginated_response utility
    responses           — success_response() envelope helper
    renderers           — EnvelopeRenderer: enforces envelope on every response
"""
