"""Abstract base model shared across all portfolio apps.

Every model in core/, bijay_dev/, frontend_dev/, and uiux_dev/ must
inherit from TimeStampedModel to get UUID primary keys and audit timestamps.
"""

from __future__ import annotations

import uuid

from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base providing UUID pk, created_at, and updated_at to all models.

    Attributes:
        id: UUID primary key, auto-generated, never editable.
        created_at: Set once on INSERT, never updated.
        updated_at: Updated on every SAVE automatically.
    """

    id: models.UUIDField = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """Return string representation using pk as fallback."""
        return str(self.pk)