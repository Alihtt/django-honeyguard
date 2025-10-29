"""Tests for signal handlers."""

from unittest.mock import patch

import pytest

from django_honeyguard.handlers import handle_honeypot_trigger
from django_honeyguard.models import HoneyGuardLog
from django_honeyguard.signals import honeypot_triggered


@pytest.mark.django_db
class TestHoneypotTriggerHandler:
    """Test honeypot_triggered signal handler."""

    def test_handler_called_on_signal(self, sample_request):
        """Test that handler is called when signal is sent."""
        data = {"username": "testuser", "password": "pass"}
        initial_count = HoneyGuardLog.objects.count()

        # Send signal
        honeypot_triggered.send(
            sender=self.__class__, request=sample_request, data=data
        )

        # Handler should create log
        assert HoneyGuardLog.objects.count() > initial_count

    def test_handler_calls_service_methods(self, sample_request):
        """Test that handler calls all service methods."""
        data = {"username": "user", "password": "pass"}

        with patch("django_honeyguard.handlers.HoneyGuardService") as mock_service:
            mock_instance = mock_service.return_value

            # Send signal
            honeypot_triggered.send(
                sender=self.__class__, request=sample_request, data=data
            )

            # Verify service methods were called
            mock_instance.log_trigger.assert_called_once()
            mock_instance.log_to_console.assert_called_once()
            mock_instance.send_email_alert.assert_called_once()

    def test_handler_with_empty_data(self, sample_request):
        """Test handler with empty data."""
        initial_count = HoneyGuardLog.objects.count()

        honeypot_triggered.send(sender=self.__class__, request=sample_request, data={})

        assert HoneyGuardLog.objects.count() > initial_count

    def test_handler_with_none_data(self, sample_request):
        """Test handler with None data."""
        initial_count = HoneyGuardLog.objects.count()

        honeypot_triggered.send(
            sender=self.__class__, request=sample_request, data=None
        )

        assert HoneyGuardLog.objects.count() > initial_count
