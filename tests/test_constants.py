"""Tests for constants module."""

from django_honeyguard.constants import CONSOLE_LOG_FORMAT, EMAIL_ALERT_BODY


class TestConstants:
    """Test constants."""

    def test_console_log_format_exists(self):
        """Test that CONSOLE_LOG_FORMAT exists."""
        assert CONSOLE_LOG_FORMAT is not None
        assert isinstance(CONSOLE_LOG_FORMAT, str)
        assert len(CONSOLE_LOG_FORMAT) > 0

    def test_email_alert_body_exists(self):
        """Test that EMAIL_ALERT_BODY exists."""
        assert EMAIL_ALERT_BODY is not None
        assert isinstance(EMAIL_ALERT_BODY, str)
        assert len(EMAIL_ALERT_BODY) > 0

    def test_console_log_format_has_placeholders(self):
        """Test that CONSOLE_LOG_FORMAT has expected placeholders."""
        placeholders = [
            "ip_address",
            "path",
            "method",
            "username",
            "password",
            "user_agent",
        ]
        for placeholder in placeholders:
            assert (
                f"{{{placeholder}}}" in CONSOLE_LOG_FORMAT
                or placeholder in CONSOLE_LOG_FORMAT
            )

    def test_email_alert_body_has_placeholders(self):
        """Test that EMAIL_ALERT_BODY has expected placeholders."""
        placeholders = [
            "ip_address",
            "path",
            "method",
            "username",
            "password",
            "honeypot_triggered",
            "timing_issue",
        ]
        for placeholder in placeholders:
            assert (
                f"{{{placeholder}}}" in EMAIL_ALERT_BODY
                or placeholder in EMAIL_ALERT_BODY
            )

    def test_email_alert_body_formatting(self):
        """Test that EMAIL_ALERT_BODY can be formatted with sample data."""
        sample_data = {
            "path": "/admin/",
            "ip_address": "192.168.1.1",
            "method": "POST",
            "created_at": "2024-01-01T00:00:00",
            "username": "testuser",
            "password": "***8 chars***",
            "user_agent": "Mozilla/5.0",
            "referer": "http://example.com",
            "accept_language": "en-US",
            "accept_encoding": "gzip",
            "honeypot_triggered": True,
            "timing_issue": "too_fast",
            "elapsed_time": 1.5,
            "raw_metadata": "{}",
        }
        # Should not raise exception
        formatted = EMAIL_ALERT_BODY.format(**sample_data)
        assert len(formatted) > 0
