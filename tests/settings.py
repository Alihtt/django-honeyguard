"""Django settings for running tests."""

SECRET_KEY = "test-secret-key-for-testing-only"

DEBUG = True

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django_honeyguard",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

ROOT_URLCONF = "django_honeyguard.urls"

USE_TZ = True

HONEYGUARD = {
    "EMAIL_RECIPIENTS": [],
    "EMAIL_SUBJECT_PREFIX": "Test Alert",
    "ENABLE_CONSOLE_LOGGING": True,
    "LOG_LEVEL": "DEBUG",
    "EMAIL_FAIL_SILENTLY": True,
}

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
