"""Django settings for Options Fiesta.

All repository paths are derived from this file.  The web application lives in
``backend/`` while market data lives in the repository-level ``data/`` folder.
Use ``OPTIONS_FIESTA_DATA_DIR`` to point the application at another dataset
without changing source code.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# backend/
BASE_DIR = Path(__file__).resolve().parent.parent
# options-fiesta/
PROJECT_ROOT = BASE_DIR.parent

# Keep local secrets/configuration at the repository root.
load_dotenv(PROJECT_ROOT / ".env")


def _environment_path(variable: str, default: Path) -> Path:
    """Resolve a path from an environment variable relative to PROJECT_ROOT."""

    raw_value = os.getenv(variable)
    path = Path(raw_value).expanduser() if raw_value else default
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()


SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-options-fiesta-development-key-change-me",
)
DEBUG = os.getenv("DEBUG", "True").strip().lower() in {"1", "true", "yes", "on"}
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost,testserver").split(",")
    if host.strip()
]

# Centralized market-data configuration.  Every data consumer should import
# these values through django.conf.settings rather than constructing paths.
DATA_ROOT = _environment_path("OPTIONS_FIESTA_DATA_DIR", PROJECT_ROOT / "data")
OPTIONS_UNDERLYING = os.getenv("OPTIONS_UNDERLYING", "NIFTY")
OPTIONS_EXPIRY = os.getenv("OPTIONS_EXPIRY", "2023-12-28")
SPOT_CSV_PATH = DATA_ROOT / "spot" / "nifty_underlying.csv"
OPTIONS_DATA_DIR = DATA_ROOT / "options" / OPTIONS_UNDERLYING / OPTIONS_EXPIRY

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "dashboard",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "options_dashboard.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "options_dashboard.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = os.getenv("TIME_ZONE", "Asia/Kolkata")
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
