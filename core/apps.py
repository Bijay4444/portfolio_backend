from __future__ import annotations

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """App config for the shared core app."""

    name = "core"
    default_auto_field = "django.db.models.BigAutoField"
