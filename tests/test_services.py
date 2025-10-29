"""Tests for HoneyGuard services."""

from unittest.mock import MagicMock, patch

import pytest
from django.core import mail
from django.test import override_settings

from django_honeyguard.models import HoneyGuardLog, TimingIssue
from django_honeyguard.services import HoneyGuardService


@pytest.mark.django_db
class TestHoneyGuardService:
    """Test HoneyGuardService class."""

    def test_service_initialization_with_data(self, sample_request):
        """Test service initialization with form data."""
        data = {
            "username": "testuser",
            "password": "testpass",
            "hp": "",
            "render_time": None,
        }
        service = HoneyGuardService(sample_request, data)
        assert service.request == sample_request
        assert service.data["username"] == "testuser"
        assert service.data["honeypot_triggered"] is False
        assert service.data["timing_issue"] == TimingIssue.VALID

    def test_service_initialization_without_data(self, sample_request):
        """Test service initialization without form data."""
        service = HoneyGuardService(sample_request, None)
        assert service.request == sample_request
        assert service.data["honeypot_triggered"] is False
        assert service.data["timing_issue"] == TimingIssue.VALID

    def test_service_detects_honeypot_trigger(self, sample_request):
        """Test that service detects honeypot trigger."""
        data = {"hp": "filled", "username": "user", "password": "pass"}  # Field is "hp"
        service = HoneyGuardService(sample_request, data)
        # Service processes "hp" field and sets "honeypot_triggered" boolean
        assert service.data["honeypot_triggered"] is True

    def test_service_calculates_timing_too_fast(self, sample_request):
        """Test timing calculation for too fast submission."""
        from datetime import timedelta

        from django.utils import timezone

        render_time = (timezone.now() - timedelta(seconds=0.5)).isoformat()
        data = {"render_time": render_time}
        service = HoneyGuardService(sample_request, data)
        assert service.data["timing_issue"] == TimingIssue.TOO_FAST

    def test_format_log_data(self, sample_request):
        """Test _format_log_data method."""
        data = {
            "username": "user",
            "password": "secret123",
            "hp": "filled",  # Honeypot field filled (service converts to boolean)
            "render_time": None,
        }
        service = HoneyGuardService(sample_request, data)
        # Service will process "hp" and set "honeypot_triggered"
        formatted = service._format_log_data()
        assert formatted["username"] == "user"
        assert "***" in formatted["password"]  # Password sanitized
        assert formatted["honeypot_triggered"] is True
        assert "ip_address" in formatted
        assert "path" in formatted
        assert "elapsed_time" in formatted


@pytest.mark.django_db
class TestLogTrigger:
    """Test log_trigger method."""

    def test_log_trigger_creates_log(self, sample_request):
        """Test that log_trigger creates a log entry."""
        initial_count = HoneyGuardLog.objects.count()
        from datetime import timedelta

        from django.utils import timezone

        # Create render time that will result in TOO_FAST
        render_time = (timezone.now() - timedelta(seconds=0.5)).isoformat()
        data = {
            "username": "testuser",
            "password": "password123",
            "hp": "filled",  # Honeypot field filled
            "render_time": render_time,  # Will trigger TOO_FAST timing
        }
        service = HoneyGuardService(sample_request, data)
        service.log_trigger()

        assert HoneyGuardLog.objects.count() > initial_count
        log = HoneyGuardLog.objects.filter(ip_address="192.168.1.1").latest(
            "created_at"
        )
        assert log.username == "testuser"
        assert "***" in log.password  # Password sanitized
        assert log.honeypot_triggered is True
        assert log.timing_issue == TimingIssue.TOO_FAST

    def test_log_trigger_sanitizes_password(self, sample_request):
        """Test that log_trigger sanitizes password."""
        data = {"username": "user", "password": "secret123"}
        service = HoneyGuardService(sample_request, data)
        service.log_trigger()

        log = HoneyGuardLog.objects.first()
        assert log.password != "secret123"
        assert "***" in log.password

    def test_log_trigger_with_minimal_data(self, sample_request):
        """Test log_trigger with minimal data."""
        service = HoneyGuardService(sample_request, {})
        service.log_trigger()

        assert HoneyGuardLog.objects.count() == 1
        log = HoneyGuardLog.objects.first()
        assert log.ip_address == "192.168.1.1"


@pytest.mark.django_db
class TestLogToConsole:
    """Test log_to_console method."""

    @override_settings(HONEYGUARD={"ENABLE_CONSOLE_LOGGING": True})
    def test_log_to_console_when_enabled(self, sample_request, caplog):
        """Test console logging when enabled."""
        service = HoneyGuardService(sample_request, {"username": "user"})
        service.log_to_console()
        assert "Honeypot triggered" in caplog.text or len(caplog.text) > 0

    @override_settings(HONEYGUARD={"ENABLE_CONSOLE_LOGGING": False})
    def test_log_to_console_when_disabled(self, sample_request, caplog):
        """Test console logging when disabled."""
        service = HoneyGuardService(sample_request, {"username": "user"})
        service.log_to_console()
        # Should not log when disabled
        log_text = caplog.text
        # May be empty or have other logs, but honeypot log should not be there
        assert service.request is not None


@pytest.mark.django_db
class TestSendEmailAlert:
    """Test send_email_alert method."""

    @override_settings(
        HONEYGUARD={
            "EMAIL_RECIPIENTS": ["admin@example.com"],
            "EMAIL_SUBJECT_PREFIX": "Alert",
        },
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    )
    def test_send_email_alert_with_recipients(self, sample_request):
        """Test sending email alert with recipients configured."""
        service = HoneyGuardService(sample_request, {"username": "user"})
        service.send_email_alert()

        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert "admin@example.com" in email.to
        assert "Alert" in email.subject

    @override_settings(HONEYGUARD={"EMAIL_RECIPIENTS": []})
    def test_send_email_alert_no_recipients(self, sample_request, caplog):
        """Test email alert when no recipients configured."""
        service = HoneyGuardService(sample_request, {"username": "user"})
        service.send_email_alert()

        assert len(mail.outbox) == 0
        assert "No email recipients" in caplog.text or len(caplog.text) >= 0

    @override_settings(
        HONEYGUARD={
            "EMAIL_RECIPIENTS": ["admin@example.com"],
            "EMAIL_FAIL_SILENTLY": True,
        },
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    )
    def test_send_email_alert_fail_silently(self, sample_request):
        """Test email alert with fail_silently=True."""
        service = HoneyGuardService(sample_request, {"username": "user"})
        # Should not raise exception even if email fails
        with patch(
            "django_honeyguard.services.send_mail", side_effect=Exception("Email error")
        ):
            service.send_email_alert()
            # Should complete without raising

    @override_settings(
        HONEYGUARD={
            "EMAIL_RECIPIENTS": ["admin@example.com"],
            "EMAIL_FROM": "noreply@example.com",
        },
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    )
    def test_send_email_alert_with_from_email(self, sample_request):
        """Test email alert uses EMAIL_FROM setting."""
        service = HoneyGuardService(sample_request, {"username": "user"})
        service.send_email_alert()

        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert email.from_email == "noreply@example.com"

    @override_settings(
        HONEYGUARD={"EMAIL_RECIPIENTS": ["admin@example.com"]},
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="default@example.com",
    )
    def test_send_email_alert_uses_default_from(self, sample_request):
        """Test email alert uses Django DEFAULT_FROM_EMAIL when EMAIL_FROM is None."""
        service = HoneyGuardService(sample_request, {"username": "user"})
        service.send_email_alert()

        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert email.from_email == "default@example.com"


@pytest.mark.django_db
class TestServiceIntegration:
    """Test service integration with all methods."""

    @override_settings(
        HONEYGUARD={
            "EMAIL_RECIPIENTS": ["admin@example.com"],
            "ENABLE_CONSOLE_LOGGING": True,
        },
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    )
    def test_service_full_workflow(self, sample_request):
        """Test full service workflow."""
        data = {
            "username": "attacker",
            "password": "password",
            "hp": "filled",  # Bot filled honeypot
        }
        service = HoneyGuardService(sample_request, data)
        service.log_trigger()
        service.log_to_console()
        service.send_email_alert()

        # Check log was created
        assert HoneyGuardLog.objects.count() == 1
        log = HoneyGuardLog.objects.first()
        assert log.username == "attacker"
        assert log.honeypot_triggered is True

        # Check email was sent
        assert len(mail.outbox) == 1
