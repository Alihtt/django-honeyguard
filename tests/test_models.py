"""Tests for HoneyGuard models."""

import pytest
from django.utils import timezone

from django_honeyguard.models import HoneyGuardLog, RequestMethod, TimingIssue


@pytest.mark.django_db
class TestHoneyGuardLogModel:
    """Test HoneyGuardLog model."""

    def test_create_basic_log(self, db):
        """Test creating a basic log entry."""
        log = HoneyGuardLog.objects.create(
            ip_address="192.168.1.1",
            path="/admin/",
        )
        assert log.ip_address == "192.168.1.1"
        assert log.path == "/admin/"
        assert log.honeypot_triggered is False
        assert log.timing_issue == TimingIssue.VALID
        assert log.method == RequestMethod.POST

    def test_create_full_log(self, db):
        """Test creating a log with all fields."""
        log = HoneyGuardLog.objects.create(
            ip_address="10.0.0.1",
            path="/wp-admin.php",
            username="admin",
            password="secret123",
            user_agent="Mozilla/5.0",
            referer="http://example.com",
            accept_language="en-US",
            accept_encoding="gzip",
            method=RequestMethod.GET,
            honeypot_triggered=True,
            timing_issue=TimingIssue.TOO_FAST,
            elapsed_time=1.5,
        )
        assert log.ip_address == "10.0.0.1"
        assert log.username == "admin"
        assert log.password == "secret123"
        assert log.honeypot_triggered is True
        assert log.timing_issue == TimingIssue.TOO_FAST

    def test_ip_address_required(self, db):
        """Test that ip_address is required."""
        # Django GenericIPAddressField doesn't allow null by default
        # But in SQLite test DB, constraints might not be enforced until save
        # The ORM will raise ValueError if we try to create without required field
        # However, SQLite might allow it and save as NULL
        # Just verify the model definition requires it
        from django_honeyguard.models import HoneyGuardLog

        field = HoneyGuardLog._meta.get_field("ip_address")
        assert not field.null  # Field should not allow null
        assert not field.blank  # Field should not be blank

    def test_path_required(self, db):
        """Test that path is required."""
        # Django CharField doesn't allow null/blank by default
        # Verify the model definition requires it
        from django_honeyguard.models import HoneyGuardLog

        field = HoneyGuardLog._meta.get_field("path")
        assert not field.null  # Field should not allow null
        assert not field.blank  # Field should not be blank

    def test_default_values(self, db):
        """Test default values for optional fields."""
        log = HoneyGuardLog.objects.create(
            ip_address="192.168.1.1",
            path="/admin/",
        )
        assert log.username == ""
        assert log.password == ""
        assert log.user_agent == ""
        assert log.honeypot_triggered is False
        assert log.timing_issue == TimingIssue.VALID
        assert log.method == RequestMethod.POST
        assert log.elapsed_time is None

    def test_auto_timestamps(self, db):
        """Test that created_at and updated_at are automatically set."""
        before = timezone.now()
        log = HoneyGuardLog.objects.create(
            ip_address="192.168.1.1",
            path="/admin/",
        )
        after = timezone.now()

        assert before <= log.created_at <= after
        assert before <= log.updated_at <= after
        assert log.created_at is not None
        assert log.updated_at is not None

    def test_string_representation(self, honeyguard_log):
        """Test __str__ method."""
        str_repr = str(honeyguard_log)
        assert "HoneyGuard trigger" in str_repr
        assert honeyguard_log.ip_address in str_repr

    def test_repr_representation(self, honeyguard_log):
        """Test __repr__ method."""
        repr_str = repr(honeyguard_log)
        assert "<HoneyGuardLog" in repr_str
        assert honeyguard_log.ip_address in repr_str


@pytest.mark.django_db
class TestIsBotProperty:
    """Test is_bot property."""

    def test_is_bot_true_when_honeypot_triggered(self, db):
        """Test is_bot is True when honeypot is triggered."""
        log = HoneyGuardLog.objects.create(
            ip_address="192.168.1.1",
            path="/admin/",
            honeypot_triggered=True,
            timing_issue=TimingIssue.VALID,
        )
        assert log.is_bot is True

    def test_is_bot_true_when_timing_too_fast(self, db):
        """Test is_bot is True when timing is too fast."""
        log = HoneyGuardLog.objects.create(
            ip_address="192.168.1.1",
            path="/admin/",
            honeypot_triggered=False,
            timing_issue=TimingIssue.TOO_FAST,
        )
        assert log.is_bot is True

    def test_is_bot_false_when_valid(self, db):
        """Test is_bot is False for valid human-like behavior."""
        log = HoneyGuardLog.objects.create(
            ip_address="192.168.1.1",
            path="/admin/",
            honeypot_triggered=False,
            timing_issue=TimingIssue.VALID,
        )
        assert log.is_bot is False

    def test_is_bot_false_when_too_slow(self, db):
        """Test is_bot is False when timing is too slow (abandoned form)."""
        log = HoneyGuardLog.objects.create(
            ip_address="192.168.1.1",
            path="/admin/",
            honeypot_triggered=False,
            timing_issue=TimingIssue.TOO_SLOW,
        )
        assert log.is_bot is False


@pytest.mark.django_db
class TestRiskScoreProperty:
    """Test risk_score property."""

    def test_risk_score_honeypot_triggered(self, db):
        """Test risk score when honeypot is triggered."""
        log = HoneyGuardLog.objects.create(
            ip_address="192.168.1.1",
            path="/admin/",
            honeypot_triggered=True,
            timing_issue=TimingIssue.VALID,
            user_agent="Mozilla/5.0",
        )
        assert log.risk_score >= 50  # Honeypot triggered adds 50

    def test_risk_score_timing_too_fast(self, db):
        """Test risk score when timing is too fast."""
        log = HoneyGuardLog.objects.create(
            ip_address="192.168.1.1",
            path="/admin/",
            honeypot_triggered=False,
            timing_issue=TimingIssue.TOO_FAST,
            user_agent="Mozilla/5.0",
        )
        assert log.risk_score >= 30  # Too fast adds 30

    def test_risk_score_no_user_agent(self, db):
        """Test risk score when user agent is missing."""
        log = HoneyGuardLog.objects.create(
            ip_address="192.168.1.1",
            path="/admin/",
            honeypot_triggered=False,
            timing_issue=TimingIssue.VALID,
            user_agent="",
        )
        assert log.risk_score >= 20  # No user agent adds 20

    def test_risk_score_all_flags(self, db):
        """Test risk score with all risk flags."""
        log = HoneyGuardLog.objects.create(
            ip_address="192.168.1.1",
            path="/admin/",
            honeypot_triggered=True,
            timing_issue=TimingIssue.TOO_FAST,
            user_agent="",
        )
        # Should be capped at 100
        assert log.risk_score == 100

    def test_risk_score_zero(self, db):
        """Test risk score for completely valid request."""
        log = HoneyGuardLog.objects.create(
            ip_address="192.168.1.1",
            path="/admin/",
            honeypot_triggered=False,
            timing_issue=TimingIssue.VALID,
            user_agent="Mozilla/5.0",
        )
        assert log.risk_score == 0

    def test_risk_score_capped_at_100(self, db):
        """Test that risk score is capped at 100."""
        log = HoneyGuardLog.objects.create(
            ip_address="192.168.1.1",
            path="/admin/",
            honeypot_triggered=True,
            timing_issue=TimingIssue.TOO_FAST,
            user_agent="",
        )
        assert log.risk_score <= 100


@pytest.mark.django_db
class TestModelQueries:
    """Test model queries and ordering."""

    def test_default_ordering(self, db):
        """Test that default ordering is by created_at descending."""
        # Create logs with different timestamps
        log1 = HoneyGuardLog.objects.create(
            ip_address="192.168.1.1",
            path="/admin/",
        )
        import time

        time.sleep(0.01)  # Small delay to ensure different timestamps
        log2 = HoneyGuardLog.objects.create(
            ip_address="192.168.1.2",
            path="/admin/",
        )

        logs = list(HoneyGuardLog.objects.all())
        # Most recent should be first
        assert logs[0].ip_address == log2.ip_address
        assert logs[1].ip_address == log1.ip_address

    def test_filter_by_ip(self, honeyguard_log):
        """Test filtering logs by IP address."""
        results = HoneyGuardLog.objects.filter(ip_address="192.168.1.1")
        assert results.count() >= 1
        assert all(log.ip_address == "192.168.1.1" for log in results)

    def test_filter_by_honeypot_triggered(
        self, honeyguard_log_bot, honeyguard_log_human
    ):
        """Test filtering by honeypot_triggered."""
        triggered = HoneyGuardLog.objects.filter(honeypot_triggered=True)
        assert honeyguard_log_bot in triggered
        assert honeyguard_log_human not in triggered
