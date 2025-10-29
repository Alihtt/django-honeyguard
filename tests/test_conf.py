"""Tests for configuration validation and settings management."""

from unittest.mock import patch

import pytest
from django.conf import settings as dj_settings
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings

from django_honeyguard.conf import Settings, settings


@pytest.mark.django_db
class TestConfigurationValidation:
    """Test configuration validation."""

    def test_default_settings_are_valid(self):
        """Test that default settings work correctly."""
        settings.reset()  # Reset to get defaults
        assert isinstance(settings.EMAIL_RECIPIENTS, list)
        assert settings.EMAIL_RECIPIENTS == []  # Default is empty
        # Note: EMAIL_SUBJECT_PREFIX might be overridden by test settings
        assert isinstance(settings.EMAIL_SUBJECT_PREFIX, str)
        assert settings.EMAIL_FAIL_SILENTLY is True
        assert settings.TIMING_TOO_FAST_THRESHOLD == 2.0
        assert settings.TIMING_TOO_SLOW_THRESHOLD == 600.0

    @override_settings(HONEYGUARD={"EMAIL_RECIPIENTS": ["test@example.com"]})
    def test_dict_configuration(self):
        """Test dictionary-style configuration."""
        settings.reset()
        assert settings.EMAIL_RECIPIENTS == ["test@example.com"]

    @override_settings(
        HONEYGUARD={},  # Clear HONEYGUARD dict so individual setting is used
        HONEYGUARD_EMAIL_RECIPIENTS=["test@example.com"],
    )
    def test_individual_settings(self):
        """Test individual HONEYGUARD_* settings."""
        # Clear cached settings to force reload
        settings.reset()
        # Force clear the attribute if cached
        if hasattr(settings, "EMAIL_RECIPIENTS"):
            delattr(settings, "EMAIL_RECIPIENTS")
        # Now access should get the value from override_settings
        recipients = settings.EMAIL_RECIPIENTS
        # Should get value from HONEYGUARD_EMAIL_RECIPIENTS (individual setting)
        assert recipients == ["test@example.com"]

    def test_settings_priority_dict_over_individual(self):
        """Test that dict settings take priority over individual."""
        with override_settings(
            HONEYGUARD={"EMAIL_RECIPIENTS": ["dict@example.com"]},
            HONEYGUARD_EMAIL_RECIPIENTS=["individual@example.com"],
        ):
            settings.reset()
            assert settings.EMAIL_RECIPIENTS == ["dict@example.com"]

    def test_invalid_setting_name(self):
        """Test that accessing invalid setting raises AttributeError."""
        with pytest.raises(AttributeError):
            _ = settings.INVALID_SETTING_NAME


class TestEmailRecipientsValidation:
    """Test EMAIL_RECIPIENTS validation."""

    @override_settings(HONEYGUARD={"EMAIL_RECIPIENTS": ["valid@example.com"]})
    def test_valid_email_list(self):
        """Test valid email recipients list."""
        settings.reset()
        assert settings.EMAIL_RECIPIENTS == ["valid@example.com"]

    @override_settings(HONEYGUARD={"EMAIL_RECIPIENTS": []})
    def test_empty_email_list(self):
        """Test empty email recipients list."""
        settings.reset()
        assert settings.EMAIL_RECIPIENTS == []

    @override_settings(HONEYGUARD={"EMAIL_RECIPIENTS": "not-a-list"})
    def test_invalid_email_recipients_type(self):
        """Test that invalid type for EMAIL_RECIPIENTS raises error."""
        settings.reset()
        with pytest.raises(ImproperlyConfigured) as exc_info:
            _ = settings.EMAIL_RECIPIENTS
        assert "must be a list or tuple" in str(exc_info.value)

    @override_settings(HONEYGUARD={"EMAIL_RECIPIENTS": [123]})
    def test_non_string_in_email_list(self):
        """Test that non-string in email list raises error."""
        settings.reset()
        with pytest.raises(ImproperlyConfigured) as exc_info:
            _ = settings.EMAIL_RECIPIENTS
        assert "must contain only strings" in str(exc_info.value)

    @override_settings(HONEYGUARD={"EMAIL_RECIPIENTS": ["invalid-email"]})
    def test_invalid_email_format_warns(self, caplog):
        """Test that invalid email format logs warning."""
        settings.reset()
        _ = settings.EMAIL_RECIPIENTS
        assert "potentially invalid email" in caplog.text.lower()


class TestTimingValidation:
    """Test timing threshold validation."""

    @override_settings(HONEYGUARD={"TIMING_TOO_FAST_THRESHOLD": 1.5})
    def test_valid_timing_threshold(self):
        """Test valid timing threshold."""
        settings.reset()
        assert settings.TIMING_TOO_FAST_THRESHOLD == 1.5

    @override_settings(HONEYGUARD={"TIMING_TOO_FAST_THRESHOLD": -5})
    def test_negative_timing_threshold(self):
        """Test that negative timing threshold raises error."""
        settings.reset()
        with pytest.raises(ImproperlyConfigured) as exc_info:
            _ = settings.TIMING_TOO_FAST_THRESHOLD
        assert "must be >= 0.1" in str(exc_info.value)

    @override_settings(HONEYGUARD={"TIMING_TOO_FAST_THRESHOLD": "not-a-number"})
    def test_non_numeric_timing_threshold(self):
        """Test that non-numeric timing threshold raises error."""
        settings.reset()
        with pytest.raises(ImproperlyConfigured) as exc_info:
            _ = settings.TIMING_TOO_FAST_THRESHOLD
        assert "must be a number" in str(exc_info.value)

    @override_settings(HONEYGUARD={"TIMING_TOO_SLOW_THRESHOLD": 0.5})
    def test_timing_slow_below_minimum(self):
        """Test that TIMING_TOO_SLOW_THRESHOLD below minimum raises error."""
        settings.reset()
        with pytest.raises(ImproperlyConfigured) as exc_info:
            _ = settings.TIMING_TOO_SLOW_THRESHOLD
        assert "must be >= 1.0" in str(exc_info.value)


class TestLogLevelValidation:
    """Test LOG_LEVEL validation."""

    @override_settings(HONEYGUARD={"LOG_LEVEL": "DEBUG"})
    def test_valid_log_level(self):
        """Test valid log level."""
        settings.reset()
        assert settings.LOG_LEVEL == "DEBUG"

    @override_settings(HONEYGUARD={"LOG_LEVEL": "debug"})  # lowercase
    def test_log_level_case_insensitive(self):
        """Test that log level is converted to uppercase."""
        settings.reset()
        assert settings.LOG_LEVEL == "DEBUG"

    @override_settings(HONEYGUARD={"LOG_LEVEL": "INVALID"})
    def test_invalid_log_level(self):
        """Test that invalid log level raises error."""
        settings.reset()
        with pytest.raises(ImproperlyConfigured) as exc_info:
            _ = settings.LOG_LEVEL
        assert "must be one of" in str(exc_info.value)

    @override_settings(HONEYGUARD={"LOG_LEVEL": 123})
    def test_non_string_log_level(self):
        """Test that non-string log level raises error."""
        settings.reset()
        with pytest.raises(ImproperlyConfigured) as exc_info:
            _ = settings.LOG_LEVEL
        assert "must be a string" in str(exc_info.value)


class TestBooleanValidation:
    """Test boolean settings validation."""

    @override_settings(HONEYGUARD={"EMAIL_FAIL_SILENTLY": True})
    def test_boolean_true(self):
        """Test boolean True."""
        settings.reset()
        assert settings.EMAIL_FAIL_SILENTLY is True

    @override_settings(HONEYGUARD={"EMAIL_FAIL_SILENTLY": False})
    def test_boolean_false(self):
        """Test boolean False."""
        settings.reset()
        assert settings.EMAIL_FAIL_SILENTLY is False

    @override_settings(HONEYGUARD={"EMAIL_FAIL_SILENTLY": "true"})
    def test_string_true_conversion(self, caplog):
        """Test string 'true' converts to boolean."""
        settings.reset()
        assert settings.EMAIL_FAIL_SILENTLY is True

    @override_settings(HONEYGUARD={"EMAIL_FAIL_SILENTLY": "false"})
    def test_string_false_conversion(self):
        """Test string 'false' converts to boolean."""
        settings.reset()
        assert settings.EMAIL_FAIL_SILENTLY is False

    @override_settings(HONEYGUARD={"EMAIL_FAIL_SILENTLY": 1})
    def test_numeric_to_boolean_conversion(self, caplog):
        """Test numeric value converts to boolean with warning."""
        settings.reset()
        assert settings.EMAIL_FAIL_SILENTLY is True
        assert "should be a boolean" in caplog.text.lower()


class TestIntegerValidation:
    """Test integer settings validation."""

    @override_settings(HONEYGUARD={"MAX_USERNAME_LENGTH": 100})
    def test_valid_integer(self):
        """Test valid integer setting."""
        settings.reset()
        assert settings.MAX_USERNAME_LENGTH == 100

    @override_settings(HONEYGUARD={"MAX_USERNAME_LENGTH": 0})
    def test_zero_integer(self):
        """Test that zero raises error."""
        settings.reset()
        with pytest.raises(ImproperlyConfigured) as exc_info:
            _ = settings.MAX_USERNAME_LENGTH
        assert "must be >= 1" in str(exc_info.value)

    @override_settings(HONEYGUARD={"MAX_USERNAME_LENGTH": "not-an-int"})
    def test_non_integer(self):
        """Test that non-integer raises error."""
        settings.reset()
        with pytest.raises(ImproperlyConfigured) as exc_info:
            _ = settings.MAX_USERNAME_LENGTH
        assert "must be an integer" in str(exc_info.value)


class TestStringValidation:
    """Test string settings validation."""

    @override_settings(HONEYGUARD={"EMAIL_SUBJECT_PREFIX": "Custom Prefix"})
    def test_valid_string(self):
        """Test valid string setting."""
        settings.reset()
        assert settings.EMAIL_SUBJECT_PREFIX == "Custom Prefix"

    @override_settings(HONEYGUARD={"EMAIL_SUBJECT_PREFIX": 123})
    def test_non_string_converts_to_string(self, caplog):
        """Test that non-string converts to string with warning."""
        settings.reset()
        assert settings.EMAIL_SUBJECT_PREFIX == "123"
        assert "should be a string" in caplog.text.lower()


class TestOptionalStringValidation:
    """Test optional string (None or string) validation."""

    @override_settings(HONEYGUARD={"EMAIL_FROM": None})
    def test_none_allowed(self):
        """Test that None is allowed for optional string."""
        settings.reset()
        assert settings.EMAIL_FROM is None

    @override_settings(HONEYGUARD={"EMAIL_FROM": "test@example.com"})
    def test_string_allowed(self):
        """Test that string is allowed."""
        settings.reset()
        assert settings.EMAIL_FROM == "test@example.com"


class TestSettingsCaching:
    """Test settings caching behavior."""

    @override_settings(HONEYGUARD={"EMAIL_RECIPIENTS": ["first@example.com"]})
    def test_settings_are_cached(self):
        """Test that settings are cached after first access."""
        settings.reset()
        first_access = settings.EMAIL_RECIPIENTS
        second_access = settings.EMAIL_RECIPIENTS

        # Should be the same object (cached)
        assert first_access is second_access

    def test_reset_clears_cache(self):
        """Test that reset clears cached values."""
        settings.reset()
        # Access to create cache
        _ = settings.EMAIL_RECIPIENTS

        # Reset should clear cache
        settings.reset()
        # Should work fine after reset
        assert isinstance(settings.EMAIL_RECIPIENTS, list)


class TestSettingsChangeSignal:
    """Test settings change signal handling."""

    def test_setting_change_updates_cache(self):
        """Test that setting change updates cache."""
        settings.reset()
        # Access to cache
        _ = settings.EMAIL_RECIPIENTS

        # Simulate setting change
        from django.test import override_settings

        with override_settings(HONEYGUARD={"EMAIL_RECIPIENTS": ["new@example.com"]}):
            # Signal should update cache
            settings.change_setting(
                "HONEYGUARD", {"EMAIL_RECIPIENTS": ["new@example.com"]}, True
            )
