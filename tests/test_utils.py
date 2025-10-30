"""Tests for utility functions."""

import ipaddress
from datetime import datetime, timedelta

from django.utils import timezone

from django_honeyguard.models import TimingIssue
from django_honeyguard.utils import (
    check_timing_attack,
    get_client_ip,
    get_request_metadata,
    sanitize_password,
)


class TestGetClientIP:
    """Test get_client_ip function."""

    def test_get_ip_from_remote_addr(self, rf):
        """Test getting IP from REMOTE_ADDR."""
        request = rf.get("/")
        request.META["REMOTE_ADDR"] = "192.168.1.1"
        assert get_client_ip(request) == "192.168.1.1"

    def test_get_ip_from_x_forwarded_for(self, rf):
        """Test getting IP from X-Forwarded-For header."""
        request = rf.get("/")
        request.META["HTTP_X_FORWARDED_FOR"] = "203.0.113.1, 192.168.1.1"
        request.META["REMOTE_ADDR"] = "192.168.1.1"
        # Should get first IP from X-Forwarded-For
        assert get_client_ip(request) == "203.0.113.1"

    def test_get_ip_with_multiple_proxies(self, rf):
        """Test getting IP when multiple proxies are in X-Forwarded-For."""
        request = rf.get("/")
        request.META["HTTP_X_FORWARDED_FOR"] = (
            "203.0.113.1, 198.51.100.1, 192.168.1.1"
        )
        # Should get first IP
        assert get_client_ip(request) == "203.0.113.1"

    def test_get_ip_falls_back_to_remote_addr(self, rf):
        """Test fallback to REMOTE_ADDR when X-Forwarded-For not present."""
        request = rf.get("/")
        request.META["REMOTE_ADDR"] = "10.0.0.1"
        assert get_client_ip(request) == "10.0.0.1"

    def test_get_ip_unknown_when_no_remote_addr(self, rf):
        """Test that 'unknown' is returned when no remote address."""
        request = rf.get("/")
        if "REMOTE_ADDR" in request.META:
            del request.META["REMOTE_ADDR"]
        ip = get_client_ip(request)
        # Should handle gracefully
        assert ip == "unknown" or ipaddress.ip_address(ip)

    def test_invalid_ip_address(self, rf, caplog):
        """Test handling of invalid IP address."""
        request = rf.get("/")
        request.META["REMOTE_ADDR"] = "not-an-ip"
        ip = get_client_ip(request)
        # Should return fallback
        assert ip == "0.0.0.0"
        assert "Invalid IP address" in caplog.text


class TestSanitizePassword:
    """Test sanitize_password function."""

    def test_sanitize_password_with_content(self):
        """Test sanitizing a password with content."""
        password = "secret123"
        sanitized = sanitize_password(password)
        assert sanitized == "***9 chars***"

    def test_sanitize_password_empty(self):
        """Test sanitizing an empty password."""
        assert sanitize_password("") == ""

    def test_sanitize_password_long(self):
        """Test sanitizing a long password."""
        password = "a" * 100
        sanitized = sanitize_password(password)
        assert sanitized == "***100 chars***"

    def test_sanitize_password_none(self):
        """Test sanitizing None password."""
        assert sanitize_password(None) == ""


class TestGetRequestMetadata:
    """Test get_request_metadata function."""

    def test_get_metadata_basic(self, sample_request):
        """Test getting basic request metadata."""
        metadata = get_request_metadata(sample_request)
        assert metadata["ip_address"] == "192.168.1.1"
        assert metadata["user_agent"] == "Mozilla/5.0"
        assert metadata["referer"] == "http://example.com"
        assert metadata["accept_language"] == "en-US"
        assert metadata["accept_encoding"] == "gzip"
        assert metadata["path"] == "/admin/"
        assert metadata["method"] == "POST"
        assert "created_at" in metadata

    def test_get_metadata_missing_headers(self, rf):
        """Test metadata extraction with missing headers."""
        request = rf.get("/test")
        request.META["REMOTE_ADDR"] = "192.168.1.1"
        metadata = get_request_metadata(request)
        assert metadata["ip_address"] == "192.168.1.1"
        assert metadata["user_agent"] == ""
        assert metadata["referer"] == ""
        assert metadata["accept_language"] == ""

    def test_get_metadata_with_x_forwarded_for(
        self, sample_request_with_x_forwarded_for
    ):
        """Test metadata uses X-Forwarded-For for IP."""
        metadata = get_request_metadata(sample_request_with_x_forwarded_for)
        assert metadata["ip_address"] == "203.0.113.1"


class TestCheckTimingAttack:
    """Test check_timing_attack function."""

    def test_timing_valid(self):
        """Test valid timing (not too fast or slow)."""
        render_time = (timezone.now() - timedelta(seconds=10)).isoformat()
        timing_issue, elapsed = check_timing_attack(render_time)
        assert timing_issue == TimingIssue.VALID
        assert elapsed > 0

    def test_timing_too_fast(self):
        """Test timing that is too fast (bot behavior)."""
        render_time = (timezone.now() - timedelta(seconds=0.5)).isoformat()
        timing_issue, elapsed = check_timing_attack(render_time)
        assert timing_issue == TimingIssue.TOO_FAST
        assert elapsed < 2.0

    def test_timing_too_slow(self):
        """Test timing that is too slow (abandoned form)."""
        render_time = (timezone.now() - timedelta(minutes=15)).isoformat()
        timing_issue, elapsed = check_timing_attack(render_time)
        assert timing_issue == TimingIssue.TOO_SLOW
        assert elapsed > 600.0

    def test_timing_none(self):
        """Test when render_time is None."""
        timing_issue, elapsed = check_timing_attack(None)
        assert timing_issue == TimingIssue.VALID
        assert elapsed == 0.0

    def test_timing_empty_string(self):
        """Test when render_time is empty string."""
        timing_issue, elapsed = check_timing_attack("")
        assert timing_issue == TimingIssue.VALID
        assert elapsed == 0.0

    def test_timing_invalid_format(self, caplog):
        """Test handling of invalid ISO format."""
        timing_issue, elapsed = check_timing_attack("not-an-iso-date")
        assert timing_issue == TimingIssue.VALID
        assert elapsed == 0.0
        assert "Error parsing render time" in caplog.text

    def test_timing_naive_datetime(self):
        """Test handling of naive datetime (without timezone)."""
        naive_dt = datetime.now()
        timing_issue, elapsed = check_timing_attack(naive_dt.isoformat())
        # Should handle naive datetime correctly
        assert timing_issue in [
            TimingIssue.VALID,
            TimingIssue.TOO_FAST,
            TimingIssue.TOO_SLOW,
        ]
