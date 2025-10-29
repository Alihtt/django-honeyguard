import logging

from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class HoneyGuardConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_honeyguard"
    verbose_name = _("HoneyGuard")

    def ready(self) -> None:
        """Validate configuration when app is ready."""
        from . import handlers  # noqa

        # Validate all settings at startup
        self.validate_settings()

    def validate_settings(self) -> None:
        """
        Validate all HoneyGuard settings at startup.

        This provides immediate feedback to users about configuration errors
        instead of failing later when settings are accessed.
        """
        from .conf import settings as honeyguard_settings

        try:
            # Try to access all settings to trigger validation
            _ = honeyguard_settings.EMAIL_RECIPIENTS
            _ = honeyguard_settings.EMAIL_SUBJECT_PREFIX
            _ = honeyguard_settings.EMAIL_FROM
            _ = honeyguard_settings.EMAIL_FAIL_SILENTLY
            _ = honeyguard_settings.TIMING_TOO_FAST_THRESHOLD
            _ = honeyguard_settings.TIMING_TOO_SLOW_THRESHOLD
            _ = honeyguard_settings.ENABLE_CONSOLE_LOGGING
            _ = honeyguard_settings.LOG_LEVEL
            _ = honeyguard_settings.ENABLE_GET_METHOD_DETECTION
            _ = honeyguard_settings.MAX_USERNAME_LENGTH
            _ = honeyguard_settings.MAX_PASSWORD_LENGTH
            _ = honeyguard_settings.WORDPRESS_USERNAME_MAX_LENGTH
            _ = honeyguard_settings.WORDPRESS_PASSWORD_MAX_LENGTH
            _ = honeyguard_settings.DJANGO_ERROR_MESSAGE
            _ = honeyguard_settings.WORDPRESS_ERROR_MESSAGE

            logger.debug("HoneyGuard settings validated successfully")
        except ImproperlyConfigured as e:
            # Re-raise with helpful message
            raise ImproperlyConfigured(
                f"HoneyGuard configuration error: {e}\n"
                f"Please check your HONEYGUARD settings in settings.py"
            ) from e
        except Exception as e:
            # Log unexpected errors but don't crash the app
            logger.error(
                f"Unexpected error validating HoneyGuard settings: {e}",
                exc_info=True,
            )
            # Don't raise - allow app to continue with defaults
