import warnings

from django.conf import settings as dj_settings
from django.core.signals import setting_changed
from django.utils.translation import gettext_lazy as _

DEFAULTS = {
    # Email alerts configuration
    "EMAIL_RECIPIENTS": [],
    "EMAIL_SUBJECT_PREFIX": "🚨 Honeypot Alert",
    "EMAIL_FROM": None,  # Uses Django's DEFAULT_FROM_EMAIL if None
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


def _is_callable_not_type(value):
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

    def __getattr__(self, name):
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

    def _get_setting(self, setting):
        """
        Get setting value from Django settings or defaults.

        Priority order:
        1. HONEYGUARD dictionary setting
        2. Individual HONEYGUARD_* setting
        3. Default value

        Args:
            setting: Setting name (without HONEYGUARD_ prefix)

        Returns:
            Setting value
        """
        # Check for dictionary-style settings
        honeyguard_config = getattr(dj_settings, "HONEYGUARD", {})
        if setting in honeyguard_config:
            return honeyguard_config[setting]

        # Check for individual HONEYGUARD_* settings
        django_setting = f"HONEYGUARD_{setting}"

        # Handle deprecated settings
        if self._is_deprecated(django_setting):
            warnings.warn(
                f"The '{django_setting}' setting has been deprecated.",
                DeprecationWarning,
                stacklevel=3,
            )

        return getattr(dj_settings, django_setting, DEFAULTS[setting])

    def _is_deprecated(self, django_setting):
        """
        Check if a Django setting is deprecated.

        Args:
            django_setting: Full Django setting name (e.g., 'HONEYGUARD_SOME_SETTING')

        Returns:
            bool: True if deprecated and exists in Django settings
        """
        deprecated_settings = getattr(self, "_deprecated_settings", set())
        return django_setting in deprecated_settings and hasattr(
            dj_settings, django_setting
        )

    def change_setting(self, setting, value, enter, **kwargs):
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

    def _handle_dict_setting_change(self, value, enter):
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

    def reset(self):
        """Reset all cached settings to force reload from Django settings."""
        for key in DEFAULTS:
            if hasattr(self, key):
                delattr(self, key)


# Create global settings instance
settings = Settings()

# Connect to Django's setting_changed signal
setting_changed.connect(settings.change_setting)
