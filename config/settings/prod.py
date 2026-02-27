"""Production settings. Loaded when DJANGO_SETTINGS_MODULE=config.settings.prod."""

from .base import *  # noqa: F401, F403

# Installed apps for this deployment
INSTALLED_APPS += [  # noqa: F405
    "core",
    "bijay_dev",
]

# Security — enforced in production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Static — WhiteNoise CompressedManifestStaticFilesStorage inherited from base.py
# Run `python manage.py collectstatic` before deploying.

# Media — stored on VPS filesystem, served by nginx directly (not Django).
# Nginx config must alias /media/ → /path/to/portfolio_backend/media/
# Django only writes files here via ImageField/FileField uploads.
MEDIA_URL = "/media/"  # noqa: F405
MEDIA_ROOT = BASE_DIR / "media"  # noqa: F405

# Database — PostgreSQL required in production
DATABASES = {  # noqa: F405
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME"),  # noqa: F405
        "USER": env("DB_USER"),  # noqa: F405
        "PASSWORD": env("DB_PASSWORD"),  # noqa: F405
        "HOST": env("DB_HOST", default="localhost"),  # noqa: F405
        "PORT": env("DB_PORT", default="5432"),  # noqa: F405
        "OPTIONS": {
            "connect_timeout": 10,
        },
    }
}
