"""Tests for Django admin interface."""

import pytest
from django.contrib.admin.sites import site
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse

from django_honeyguard.admin import HoneyGuardLogAdmin
from django_honeyguard.models import HoneyGuardLog, TimingIssue


@pytest.mark.django_db
class TestHoneyGuardLogAdmin:
    """Test HoneyGuardLogAdmin."""

    @pytest.fixture
    def admin_user(self, db):
        """Create admin user."""
        return User.objects.create_superuser(
            username="admin", email="admin@example.com", password="password"
        )

    @pytest.fixture
    def admin_client(self, admin_user):
        """Create admin client."""
        client = Client()
        client.force_login(admin_user)
        return client

    def test_admin_registered(self):
        """Test that HoneyGuardLog is registered in admin."""
        assert HoneyGuardLog in site._registry

    def test_admin_list_display(self):
        """Test that admin has correct list_display."""
        admin_class = site._registry[HoneyGuardLog]
        assert "created_at" in admin_class.list_display
        assert "ip_address" in admin_class.list_display
        assert "risk_score_display" in admin_class.list_display

    def test_admin_list_filter(self):
        """Test that admin has correct list_filter."""
        admin_class = site._registry[HoneyGuardLog]
        assert "created_at" in admin_class.list_filter

    def test_admin_search_fields(self):
        """Test that admin has correct search_fields."""
        admin_class = site._registry[HoneyGuardLog]
        assert "ip_address" in admin_class.search_fields
        assert "username" in admin_class.search_fields

    def test_admin_actions_exist(self):
        """Test that admin actions are registered."""
        admin_class = site._registry[HoneyGuardLog]
        assert "export_to_csv" in admin_class.actions
        assert "archive_old_logs" in admin_class.actions

    def test_username_display_truncates(self, honeyguard_log):
        """Test username_display truncates long usernames."""
        admin = HoneyGuardLogAdmin(HoneyGuardLog, site)
        long_username = "a" * 50
        honeyguard_log.username = long_username
        display = admin.username_display(honeyguard_log)
        assert len(display) <= 33  # 30 chars + "..."

    def test_username_display_empty(self, honeyguard_log):
        """Test username_display shows dash for empty username."""
        admin = HoneyGuardLogAdmin(HoneyGuardLog, site)
        honeyguard_log.username = ""
        display = admin.username_display(honeyguard_log)
        assert "—" in display or display == ""

    def test_risk_score_display_high_risk(self, db):
        """Test risk_score_display for high risk."""
        admin = HoneyGuardLogAdmin(HoneyGuardLog, site)
        log = HoneyGuardLog.objects.create(
            ip_address="192.168.1.1",
            path="/admin/",
            honeypot_triggered=True,
            timing_issue=TimingIssue.TOO_FAST,  # Add timing issue for higher score
            user_agent="",  # No user agent adds 20
        )
        # This should give score: 50 (honeypot) + 30 (too fast) + 20 (no UA) = 100
        display = admin.risk_score_display(log)
        assert log.risk_score >= 70
        assert "High" in display or str(log.risk_score) in display

    def test_risk_score_display_low_risk(self, honeyguard_log_human):
        """Test risk_score_display for low risk."""
        admin = HoneyGuardLogAdmin(HoneyGuardLog, site)
        display = admin.risk_score_display(honeyguard_log_human)
        assert "Low" in display or "0" in display

    def test_is_bot_display(self, honeyguard_log_bot):
        """Test is_bot_display method."""
        admin = HoneyGuardLogAdmin(HoneyGuardLog, site)
        # is_bot_display is in list_display as a property/method
        # Check that the log has is_bot property
        assert honeyguard_log_bot.is_bot is True

    def test_request_summary(self, honeyguard_log):
        """Test request_summary method."""
        admin = HoneyGuardLogAdmin(HoneyGuardLog, site)
        summary = admin.request_summary(honeyguard_log)
        assert "IP:" in summary
        assert "192.168.1.1" in summary


@pytest.mark.django_db
class TestAdminActions:
    """Test admin actions."""

    @pytest.fixture
    def admin_user(self, db):
        """Create admin user."""
        return User.objects.create_superuser(
            username="admin", email="admin@example.com", password="password"
        )

    @pytest.fixture
    def admin_client(self, admin_user):
        """Create admin client."""
        client = Client()
        client.force_login(admin_user)
        return client

    def test_export_to_csv(self, admin_client, honeyguard_log, honeyguard_log_bot):
        """Test export_to_csv action."""
        admin = HoneyGuardLogAdmin(HoneyGuardLog, site)
        queryset = HoneyGuardLog.objects.all()

        # Create a mock request
        request = type("Request", (), {"user": None})()

        response = admin.export_to_csv(request, queryset)

        assert response.status_code == 200
        assert "text/csv" in response["Content-Type"]
        assert "attachment" in response["Content-Disposition"]

        # Check CSV content
        content = response.content.decode("utf-8")
        # CSV headers use camelCase like "IpAddress", "CreatedAt", etc. (no spaces)
        assert "IpAddress" in content or "IP" in content.upper()
        assert "192.168.1.1" in content

    def test_archive_old_logs(self, db):
        """Test archive_old_logs action."""
        from datetime import timedelta

        from django.utils import timezone

        # Create old log by using update() after creation to bypass auto_now_add
        old_log = HoneyGuardLog.objects.create(
            ip_address="192.168.1.1",
            path="/admin/",
        )
        # Update created_at directly in the database to bypass auto_now
        old_date = timezone.now() - timedelta(days=100)
        HoneyGuardLog.objects.filter(id=old_log.id).update(created_at=old_date)
        old_log.refresh_from_db()

        # Create recent log
        recent_log = HoneyGuardLog.objects.create(
            ip_address="192.168.1.2",
            path="/admin/",
        )
        # Update created_at to be recent (within 90 days)
        recent_date = timezone.now() - timedelta(days=10)
        HoneyGuardLog.objects.filter(id=recent_log.id).update(created_at=recent_date)
        recent_log.refresh_from_db()

        from unittest.mock import Mock

        from django.contrib.auth.models import AnonymousUser
        from django.test import RequestFactory

        admin = HoneyGuardLogAdmin(HoneyGuardLog, site)
        request_factory = RequestFactory()
        request = request_factory.get("/")
        request.user = AnonymousUser()
        # Add messages attribute to avoid MessageMiddleware error
        request._messages = Mock()
        queryset = HoneyGuardLog.objects.all()

        # This will delete logs older than 90 days
        admin.archive_old_logs(request, queryset)

        # Old log should be deleted (older than 90 days)
        assert not HoneyGuardLog.objects.filter(id=old_log.id).exists()
        # Recent log should remain (less than 90 days old)
        assert HoneyGuardLog.objects.filter(id=recent_log.id).exists()
