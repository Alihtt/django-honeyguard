from django.db import models
from django.utils.translation import gettext_lazy as _


class TimingIssue(models.TextChoices):
    TOO_FAST = "too_fast", _("Too Fast (<2s)")
    TOO_SLOW = "too_slow", _("Too Slow (>10min)")
    VALID = "valid", _("Valid Timing")


class RequestMethod(models.TextChoices):
    GET = "GET", _("GET Request")
    POST = "POST", _("POST Request")


class HoneyGuardLog(models.Model):
    """Log entry for honeypot detection events."""

    # Basic Information
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text=_("Timestamp of the honeypot trigger"),
    )
    ip_address = models.GenericIPAddressField(
        db_index=True, help_text=_("IP address of the requester")
    )
    path = models.CharField(
        max_length=255, db_index=True, help_text=_("URL path accessed")
    )

    # Authentication Attempt
    username_attempted = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text=_("Username submitted in login attempt"),
    )
    password_attempted = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text=_("Password submitted in login attempt"),
    )

    # Request Metadata
    user_agent = models.TextField(
        blank=True, default="", help_text=_("User agent string from request")
    )
    referer = models.CharField(
        max_length=500,
        blank=True,
        default="",
        help_text=_("HTTP referer header"),
    )
    accept_language = models.CharField(max_length=255, blank=True, default="")
    accept_encoding = models.CharField(max_length=255, blank=True, default="")
    request_method = models.CharField(
        max_length=10, default=RequestMethod.POST, choices=RequestMethod.choices
    )

    # Detection Flags
    honeypot_triggered = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_("Whether the honeypot field was filled"),
    )
    timing_issue = models.CharField(
        max_length=20,
        choices=TimingIssue.choices,
        default=TimingIssue.VALID,
        help_text=_("Type of timing anomaly detected"),
    )
    elapsed_time = models.FloatField(
        null=True,
        blank=True,
        help_text=_("Time in seconds between form render and submission"),
    )

    # Additional Metadata
    raw_metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Raw request metadata for debugging"),
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["-timestamp", "ip_address"]),
            models.Index(fields=["honeypot_triggered", "-timestamp"]),
            models.Index(fields=["path", "-timestamp"]),
        ]
        verbose_name = _("HoneyGuard Log")
        verbose_name_plural = _("HoneyGuard Logs")

    def __str__(self):
        return f"HoneyGuard trigger from {self.ip_address} at {self.timestamp}"

    def __repr__(self):
        return (
            f"<HoneyGuardLog(ip={self.ip_address}, "
            f"path={self.path}, timestamp={self.timestamp})>"
        )

    @property
    def is_bot(self):
        """Check if this appears to be bot activity."""
        return (
            self.honeypot_triggered or self.timing_issue == TimingIssue.TOO_FAST
        )

    @property
    def risk_score(self):
        """
        Calculate a simple risk score based on detection flags.

        Returns:
            int: Risk score between 0 and 100
        """
        score = 0
        if self.honeypot_triggered:
            score += 50
        if self.timing_issue == TimingIssue.TOO_FAST:
            score += 30
        if not self.user_agent:
            score += 20
        return min(score, 100)
