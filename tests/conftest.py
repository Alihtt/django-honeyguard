"""Pytest configuration and shared fixtures."""

from datetime import datetime, timedelta
from typing import Dict

import pytest
from django.contrib.auth.models import User
from django.core.signing import BadSignature, TimestampSigner
from django.http import HttpRequest
from django.test import RequestFactory
from django.utils import timezone

from django_honeyguard.models import HoneyGuardLog, RequestMethod, TimingIssue

# Configure pytest-django
pytest_plugins = ["pytest_django"]


@pytest.fixture
def rf() -> RequestFactory:
    """Request factory fixture."""
    return RequestFactory()


@pytest.fixture
def sample_request(rf: RequestFactory) -> HttpRequest:
    """Create a sample HTTP request."""
    request = rf.post("/admin/", data={"username": "admin", "password": "pass"})
    request.META.update(
        {
            "REMOTE_ADDR": "192.168.1.1",
            "HTTP_USER_AGENT": "Mozilla/5.0",
            "HTTP_REFERER": "http://example.com",
            "HTTP_ACCEPT_LANGUAGE": "en-US",
            "HTTP_ACCEPT_ENCODING": "gzip",
        }
    )
    return request


@pytest.fixture
def sample_request_with_x_forwarded_for(rf: RequestFactory) -> HttpRequest:
    """Create a request with X-Forwarded-For header."""
    request = rf.post("/admin/")
    request.META.update(
        {
            "HTTP_X_FORWARDED_FOR": "203.0.113.1, 192.168.1.1",
            "REMOTE_ADDR": "192.168.1.1",
            "HTTP_USER_AGENT": "Mozilla/5.0",
        }
    )
    return request


@pytest.fixture
def honeyguard_log(db) -> HoneyGuardLog:
    """Create a sample HoneyGuardLog instance."""
    return HoneyGuardLog.objects.create(
        ip_address="192.168.1.1",
        path="/admin/",
        username="testuser",
        password="***10 chars***",
        user_agent="Mozilla/5.0",
        honeypot_triggered=True,
        timing_issue=TimingIssue.TOO_FAST,
        elapsed_time=1.5,
    )


@pytest.fixture
def honeyguard_log_bot(db) -> HoneyGuardLog:
    """Create a bot-detected log."""
    return HoneyGuardLog.objects.create(
        ip_address="10.0.0.1",
        path="/wp-admin.php",
        username="bot",
        password="***12 chars***",
        user_agent="",
        honeypot_triggered=True,
        timing_issue=TimingIssue.VALID,
        elapsed_time=5.0,
    )


@pytest.fixture
def honeyguard_log_human(db) -> HoneyGuardLog:
    """Create a human-like log (not a bot)."""
    return HoneyGuardLog.objects.create(
        ip_address="172.16.0.1",
        path="/admin/",
        username="user",
        password="***8 chars***",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        honeypot_triggered=False,
        timing_issue=TimingIssue.VALID,
        elapsed_time=15.0,
    )


@pytest.fixture
def form_data() -> Dict[str, str]:
    """Sample form data for testing (human - honeypot not filled)."""
    return {
        "username": "testuser",
        "password": "testpass123",
        "hp": "",  # Not filled (human) - field name is "hp"
        "render_time": "",
    }


@pytest.fixture
def form_data_bot() -> Dict[str, str]:
    """Form data with honeypot filled (bot detected)."""
    return {
        "username": "bot",
        "password": "password",
        "hp": "filled",  # Bot filled this - field name is "hp"
        "render_time": "",
    }


@pytest.fixture
def signed_render_time() -> str:
    """Create a signed render time."""
    signer = TimestampSigner()
    render_time = timezone.now()
    return signer.sign(render_time.isoformat())


@pytest.fixture
def expired_render_time() -> str:
    """Create an expired signed render time."""
    signer = TimestampSigner()
    # Sign a time from 1 hour ago with max_age of 30 minutes
    old_time = timezone.now() - timedelta(hours=1)
    return signer.sign(old_time.isoformat())


@pytest.fixture
def invalid_render_time() -> str:
    """Create an invalid signed render time."""
    return "invalid.signature.here"


@pytest.fixture
def django_settings_for_tests(settings):
    """Override Django settings for tests."""
    # Set minimal settings for testing
    settings.DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
    settings.SECRET_KEY = "test-secret-key"
    settings.INSTALLED_APPS = [
        "django.contrib.contenttypes",
        "django.contrib.auth",
        "django_honeyguard",
    ]
    return settings
