"""
Django settings for example project.
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Quick-start development settings - unsuitable for production
SECRET_KEY = "example-secret-key-change-in-production"

DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Honeypot apps
    "django_honeyguard",
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

ROOT_URLCONF = "urls"

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

WSGI_APPLICATION = "wsgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Honeypot settings - django-honeyguard supports both configuration styles:

# Option 1: Dictionary-style configuration (recommended, like DRF)
HONEYGUARD = {
    # Email alerts configuration
    "EMAIL_RECIPIENTS": ["example@gmail.com"],
    "EMAIL_SUBJECT_PREFIX": "[Honeypot Alert]",
    "EMAIL_FROM": None,  # Uses Django's DEFAULT_FROM_EMAIL
    # Timing detection thresholds (in seconds)
    "TIMING_TOO_FAST_THRESHOLD": 2.0,  # Submissions faster than this are suspicious
    "TIMING_TOO_SLOW_THRESHOLD": 600.0,  # 10 minutes - submissions slower than this are suspicious
    # Logging configuration
    "ENABLE_CONSOLE_LOGGING": True,
    "LOG_LEVEL": "WARNING",
    # Honeypot behavior
    "ENABLE_GET_METHOD_DETECTION": True,  # Trigger honeypot on GET requests to URLs
    # Security features
    "MAX_USERNAME_LENGTH": 150,  # Django default
    "MAX_PASSWORD_LENGTH": 128,  # Django default
    # WordPress-specific settings
    "WORDPRESS_USERNAME_MAX_LENGTH": 60,  # WordPress default
    "WORDPRESS_PASSWORD_MAX_LENGTH": 255,
    # Error messages (can be customized)
    "DJANGO_ERROR_MESSAGE": "Please enter a correct username and password. Note that both fields may be case-sensitive.",
    "WORDPRESS_ERROR_MESSAGE": "The password you entered for the username is incorrect.",
}

# Option 2: Individual settings (still supported)
# HONEYGUARD_EMAIL_RECIPIENTS = ["example@gmail.com"]
# HONEYGUARD_EMAIL_SUBJECT_PREFIX = "[Honeypot Alert]"
# HONEYGUARD_TIMING_TOO_FAST_THRESHOLD = 2.0
# HONEYGUARD_ENABLE_GET_METHOD_DETECTION = True  # Enable GET request detection
# ... etc


# Email settings (configure for production)
EMAIL_BACKEND = (
    "django.core.mail.backends.console.EmailBackend"  # Console for dev
)
DEFAULT_FROM_EMAIL = "noreply@example.com"
