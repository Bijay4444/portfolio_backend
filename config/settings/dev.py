"""Development settings — local environment only. Never use in production."""

from .base import *  # noqa: F401, F403

# Installed apps for this deployment
INSTALLED_APPS += [  # noqa: F405
    "core",
    "bijay_dev",
]

# Database — SQLite for frictionless local dev
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "dev.sqlite3",  # noqa: F405
    }
}
