"""Development settings — local environment only. Never use in production."""

from .base import *  # noqa: F401, F403

# Installed apps for this deployment
INSTALLED_APPS += [  # noqa: F405
    "core",
    "bijay_dev",
]

