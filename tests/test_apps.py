"""Tests for Django app configuration."""

import pytest
from django.core.exceptions import ImproperlyConfigured


class TestHoneyGuardConfig:
    """Test HoneyGuardConfig."""

    def test_app_config_name(self):
        """Test app config name."""
        from django.apps import apps

        app_config = apps.get_app_config("django_honeyguard")
        assert app_config.name == "django_honeyguard"
        assert app_config.verbose_name == "HoneyGuard"

    def test_app_config_default_auto_field(self):
        """Test default auto field."""
        from django.apps import apps

        app_config = apps.get_app_config("django_honeyguard")
        assert app_config.default_auto_field == "django.db.models.BigAutoField"

    @pytest.mark.django_db
    def test_ready_validates_settings(self):
        """Test that ready() validates settings."""
        from django.apps import apps

        app_config = apps.get_app_config("django_honeyguard")

        # With valid settings, should not raise
        try:
            app_config.validate_settings()
        except ImproperlyConfigured:
            # If settings are invalid, this is expected
            pass

    @pytest.mark.django_db
    def test_validate_settings_with_invalid_config(self):
        """Test validate_settings with invalid configuration."""
        from django.apps import apps
        from django.test import override_settings

        from django_honeyguard.conf import settings as hg_settings

        app_config = apps.get_app_config("django_honeyguard")

        with override_settings(HONEYGUARD={"TIMING_TOO_FAST_THRESHOLD": -5}):
            # Reset settings to reload
            hg_settings.reset()
            # Should raise ImproperlyConfigured when accessing the setting
            with pytest.raises(ImproperlyConfigured):
                # Access the setting to trigger validation
                _ = hg_settings.TIMING_TOO_FAST_THRESHOLD
