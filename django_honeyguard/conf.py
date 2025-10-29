"""Configuration management for django-honeyguard."""

import logging
from typing import Any, Callable, Dict, List, Tuple, Type, Union

from django.conf import settings as dj_settings
from django.core.signals import setting_changed
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)

# Type definitions for validators
ValidatorFunc = Callable[[Any, str], Tuple[Any, str]]

# Valid log levels
VALID_LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

DEFAULTS: Dict[str, Any] = {
    # Email alerts configuration
    "EMAIL_RECIPIENTS": [],
    "EMAIL_SUBJECT_PREFIX": "🚨 Honeypot Alert",
    "EMAIL_FROM": None,  # Uses Django's DEFAULT_FROM_EMAIL if None
    "EMAIL_FAIL_SILENTLY": True,  # Don't raise exceptions on email send failure
    # Timing detection thresholds (in seconds)
    "TIMING_TOO_FAST_THRESHOLD": 2.0,
    "TIMING_TOO_SLOW_THRESHOLD": 600.0,  # 10 minutes
    # Logging configuration
    "ENABLE_CONSOLE_LOGGING": True,
    "LOG_LEVEL": "WARNING",
    # Honeypot behavior
    "ENABLE_GET_METHOD_DETECTION": False,
    # Security features
    "MAX_USERNAME_LENGTH": 150,  # Django default
    "MAX_PASSWORD_LENGTH": 128,  # Django default
    # WordPress-specific settings
    "WORDPRESS_USERNAME_MAX_LENGTH": 60,
    "WORDPRESS_PASSWORD_MAX_LENGTH": 255,
    # Error messages
    "DJANGO_ERROR_MESSAGE": (
        "Please enter a correct username and password. "
        "Note that both fields may be case-sensitive."
    ),
    "WORDPRESS_ERROR_MESSAGE": (
        "<strong>Error:</strong> The password you entered for the username is incorrect."
    ),
}


def validate_email_recipients(value: Any, setting_name: str) -> Tuple[List[str], str]:
    """
    Validate EMAIL_RECIPIENTS setting.

    Args:
        value: Setting value to validate
        setting_name: Name of the setting

    Returns:
        tuple: (validated_value, error_message)

    Raises:
        ImproperlyConfigured: If value is invalid and cannot be fixed
    """
    if value is None:
        return [], ""

    if not isinstance(value, (list, tuple)):
        raise ImproperlyConfigured(
            f"{setting_name} must be a list or tuple of email addresses, "
            f"got {type(value).__name__}: {value}"
        )

    validated = []
    for email in value:
        if not isinstance(email, str):
            raise ImproperlyConfigured(
                f"{setting_name} must contain only strings (email addresses), "
                f"got {type(email).__name__}: {email}"
            )
        if "@" not in email:  # Basic email validation
            logger.warning(
                f"{setting_name} contains potentially invalid email: {email}"
            )
        validated.append(email)

    return validated, ""


def validate_positive_number(
    value: Any, setting_name: str, min_value: float = 0.0
) -> Tuple[float, str]:
    """
    Validate a positive number setting.

    Args:
        value: Setting value to validate
        setting_name: Name of the setting
        min_value: Minimum allowed value

    Returns:
        tuple: (validated_value, error_message)

    Raises:
        ImproperlyConfigured: If value is invalid
    """
    try:
        num_value = float(value)
    except (TypeError, ValueError):
        raise ImproperlyConfigured(
            f"{setting_name} must be a number, got {type(value).__name__}: {value}"
        )

    if num_value < min_value:
        raise ImproperlyConfigured(
            f"{setting_name} must be >= {min_value}, got {num_value}"
        )

    return num_value, ""


def validate_positive_integer(
    value: Any, setting_name: str, min_value: int = 1
) -> Tuple[int, str]:
    """
    Validate a positive integer setting.

    Args:
        value: Setting value to validate
        setting_name: Name of the setting
        min_value: Minimum allowed value

    Returns:
        tuple: (validated_value, error_message)

    Raises:
        ImproperlyConfigured: If value is invalid
    """
    try:
        int_value = int(value)
    except (TypeError, ValueError):
        raise ImproperlyConfigured(
            f"{setting_name} must be an integer, got {type(value).__name__}: {value}"
        )

    if int_value < min_value:
        raise ImproperlyConfigured(
            f"{setting_name} must be >= {min_value}, got {int_value}"
        )

    return int_value, ""


def validate_boolean(value: Any, setting_name: str) -> Tuple[bool, str]:
    """
    Validate a boolean setting.

    Args:
        value: Setting value to validate
        setting_name: Name of the setting

    Returns:
        tuple: (validated_value, error_message)
    """
    if isinstance(value, bool):
        return value, ""

    if isinstance(value, str):
        lower = value.lower()
        if lower in ("true", "1", "yes", "on"):
            return True, ""
        if lower in ("false", "0", "no", "off"):
            return False, ""

    # Try to convert, but warn
    try:
        bool_value = bool(value)
        logger.warning(
            f"{setting_name} should be a boolean, got {type(value).__name__}: {value}. "
            f"Converted to {bool_value}."
        )
        return bool_value, ""
    except Exception:
        raise ImproperlyConfigured(
            f"{setting_name} must be a boolean, got {type(value).__name__}: {value}"
        )


def validate_log_level(value: Any, setting_name: str) -> Tuple[str, str]:
    """
    Validate LOG_LEVEL setting.

    Args:
        value: Setting value to validate
        setting_name: Name of the setting

    Returns:
        tuple: (validated_value, error_message)

    Raises:
        ImproperlyConfigured: If value is invalid
    """
    if not isinstance(value, str):
        raise ImproperlyConfigured(
            f"{setting_name} must be a string, got {type(value).__name__}: {value}"
        )

    upper_value = value.upper()
    if upper_value not in VALID_LOG_LEVELS:
        raise ImproperlyConfigured(
            f"{setting_name} must be one of {VALID_LOG_LEVELS}, got: {value}"
        )

    return upper_value, ""


def validate_string(value: Any, setting_name: str) -> Tuple[str, str]:
    """
    Validate a string setting.

    Args:
        value: Setting value to validate
        setting_name: Name of the setting

    Returns:
        tuple: (validated_value, error_message)
    """
    if not isinstance(value, str):
        logger.warning(
            f"{setting_name} should be a string, got {type(value).__name__}. "
            f"Converting to string."
        )
        return str(value), ""

    return value, ""


def validate_optional_string(value: Any, setting_name: str) -> Tuple[Any, str]:
    """
    Validate an optional string setting (can be None or string).

    Args:
        value: Setting value to validate
        setting_name: Name of the setting

    Returns:
        tuple: (validated_value, error_message)
    """
    if value is None:
        return None, ""

    if not isinstance(value, str):
        logger.warning(
            f"{setting_name} should be None or a string, got {type(value).__name__}. "
            f"Converting to string."
        )
        return str(value), ""

    return value, ""


# Wrapper functions for validators that need additional parameters
def validate_timing_fast(value: Any, setting_name: str) -> Tuple[float, str]:
    """Validate TIMING_TOO_FAST_THRESHOLD."""
    return validate_positive_number(value, setting_name, min_value=0.1)


def validate_timing_slow(value: Any, setting_name: str) -> Tuple[float, str]:
    """Validate TIMING_TOO_SLOW_THRESHOLD."""
    return validate_positive_number(value, setting_name, min_value=1.0)


def validate_username_length(value: Any, setting_name: str) -> Tuple[int, str]:
    """Validate username length settings."""
    return validate_positive_integer(value, setting_name, min_value=1)


# Validators for each setting
VALIDATORS: Dict[str, ValidatorFunc] = {
    "EMAIL_RECIPIENTS": validate_email_recipients,
    "EMAIL_SUBJECT_PREFIX": validate_string,
    "EMAIL_FROM": validate_optional_string,
    "EMAIL_FAIL_SILENTLY": validate_boolean,
    "TIMING_TOO_FAST_THRESHOLD": validate_timing_fast,
    "TIMING_TOO_SLOW_THRESHOLD": validate_timing_slow,
    "ENABLE_CONSOLE_LOGGING": validate_boolean,
    "LOG_LEVEL": validate_log_level,
    "ENABLE_GET_METHOD_DETECTION": validate_boolean,
    "MAX_USERNAME_LENGTH": validate_username_length,
    "MAX_PASSWORD_LENGTH": validate_username_length,
    "WORDPRESS_USERNAME_MAX_LENGTH": validate_username_length,
    "WORDPRESS_PASSWORD_MAX_LENGTH": validate_username_length,
    "DJANGO_ERROR_MESSAGE": validate_string,
    "WORDPRESS_ERROR_MESSAGE": validate_string,
}


def _is_callable_not_type(value: Any) -> bool:
    """
    Check if value is callable but not a type/class.

    Args:
        value: Value to check

    Returns:
        bool: True if callable and not a type
    """
    return callable(value) and not isinstance(value, type)


class Settings:
    """
    Settings management for django-honeyguard.

    Allows settings to be configured either through:
    1. A HONEYGUARD dictionary in Django settings
    2. Individual HONEYGUARD_* settings

    Settings are lazily loaded and cached for performance.
    """

    def __getattr__(self, name: str) -> Any:
        """
        Get a setting value by name.

        Args:
            name: Setting name (without HONEYGUARD_ prefix)

        Returns:
            Setting value from Django settings or default

        Raises:
            AttributeError: If setting name is not valid
        """
        if name not in DEFAULTS:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'"
            )

        value = self._get_setting(name)

        # Execute callables (except types)
        if _is_callable_not_type(value):
            value = value()

        # Cache the result
        setattr(self, name, value)
        return value

    def _get_setting(self, setting: str, validate: bool = True) -> Any:
        """
        Get setting value from Django settings or defaults.

        Priority order:
        1. HONEYGUARD dictionary setting
        2. Individual HONEYGUARD_* setting
        3. Default value

        Args:
            setting: Setting name (without HONEYGUARD_ prefix)
            validate: Whether to validate the setting value

        Returns:
            Setting value (validated if validate=True)

        Raises:
            ImproperlyConfigured: If validation fails
        """
        # Check for dictionary-style settings
        honeyguard_config = getattr(dj_settings, "HONEYGUARD", {})
        if setting in honeyguard_config:
            value = honeyguard_config[setting]
        else:
            # Check for individual HONEYGUARD_* settings
            django_setting = f"HONEYGUARD_{setting}"
            value = getattr(dj_settings, django_setting, DEFAULTS[setting])

        # Validate the value if validator exists
        if validate and setting in VALIDATORS:
            validator = VALIDATORS[setting]
            setting_full_name = f"HONEYGUARD['{setting}'] or HONEYGUARD_{setting}"
            try:
                validated_value, _ = validator(value, setting_full_name)
                return validated_value
            except ImproperlyConfigured:
                # Re-raise configuration errors as-is
                raise
            except Exception as e:
                # Wrap unexpected errors
                raise ImproperlyConfigured(
                    f"Error validating {setting_full_name}: {e}"
                ) from e

        return value

    def change_setting(
        self, setting: str, value: Any, enter: bool, **kwargs: Any
    ) -> None:
        """
        Handle Django setting changes via setting_changed signal.

        Args:
            setting: Django setting name that changed
            value: New value of the setting
            enter: True if setting is being added/changed, False if removed
            **kwargs: Additional signal arguments
        """
        # Handle HONEYGUARD dictionary setting
        if setting == "HONEYGUARD":
            self._handle_dict_setting_change(value, enter)
            return

        # Handle individual HONEYGUARD_* settings
        if not setting.startswith("HONEYGUARD_"):
            return

        setting_name = setting[11:]  # Strip 'HONEYGUARD_' prefix

        # Ensure valid app setting
        if setting_name not in DEFAULTS:
            return

        # Update or clear cached value
        if enter:
            setattr(self, setting_name, value)
        else:
            if hasattr(self, setting_name):
                delattr(self, setting_name)

    def _handle_dict_setting_change(self, value: Any, enter: bool) -> None:
        """
        Handle changes to the HONEYGUARD dictionary setting.

        Args:
            value: New dictionary value
            enter: True if setting is being added/changed, False if removed
        """
        if enter and isinstance(value, dict):
            # Update all settings from dictionary
            for key, val in value.items():
                if key in DEFAULTS:
                    setattr(self, key, val)
        else:
            # Clear all cached values
            for key in DEFAULTS:
                if hasattr(self, key):
                    delattr(self, key)

    def reset(self) -> None:
        """Reset all cached settings to force reload from Django settings."""
        for key in DEFAULTS:
            if hasattr(self, key):
                delattr(self, key)


# Create global settings instance
settings = Settings()

# Connect to Django's setting_changed signal
setting_changed.connect(settings.change_setting)
