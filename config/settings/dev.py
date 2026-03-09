"""Development settings — local environment only. Never use in production."""

from .base import *  # noqa: F401, F403

# Installed apps for this deployment
INSTALLED_APPS += [  # noqa: F405
    "core",
    "bijay_dev",
]

# Static — use simple storage in dev (no hashing, faster iteration)
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"  # noqa: F405

# Media — served by Django's built-in dev server via config/urls.py
# Files land at BASE_DIR/media/ locally
MEDIA_URL = "/media/"  # noqa: F405
MEDIA_ROOT = BASE_DIR / "media"  # noqa: F405

