"""Business logic for HoneyGuard honeypot triggers."""

from typing import Optional

from django.core.mail import send_mail
from django.http import HttpRequest

from .conf import settings as honeyguard_settings
from .constants import CONSOLE_LOG_FORMAT, EMAIL_ALERT_BODY
from .loggers import get_logger
from .models import HoneyGuardLog, TimingIssue
from .utils import (
    check_timing_attack,
    get_request_metadata,
    sanitize_password,
)

logger = get_logger(__name__)


class HoneyGuardService:
    """Encapsulates core business logic for honeypot event processing."""

    def __init__(self, request: HttpRequest, data: Optional[dict] = None):
        self.request = request
        self.data = data
        self.metadata = get_request_metadata(request)

        elapsed_time = 0
        timing_issue = TimingIssue.VALID

        if self.data:
            render_time = self.data.get("render_time")
            if render_time:
                timing_issue, elapsed_time = check_timing_attack(render_time)
            honeypot_triggered = bool(self.data.get("hp", "").strip())

            self.data["honeypot_triggered"] = honeypot_triggered
            self.data["timing_issue"] = timing_issue
            self.data["elapsed_time"] = elapsed_time
        else:
            self.data = {
                "timing_issue": timing_issue,
                "elapsed_time": elapsed_time,
                "honeypot_triggered": False,
            }

    def _format_log_data(self) -> dict:
        """Format data for logging/email alerts."""
        password_sanitized = sanitize_password(self.data.get("password", ""))
        return {
            **self.metadata,
            "username": self.data.get("username", ""),
            "password": password_sanitized,
            "elapsed_time": self.data.get("elapsed_time", 0),
            "timing_issue": self.data.get("timing_issue", ""),
            "honeypot_triggered": self.data.get("honeypot_triggered", False),
            "raw_metadata": str(self.metadata),
        }

    def log_trigger(self) -> None:
        """Log honeypot trigger to the database."""
        HoneyGuardLog.objects.create(
            path=self.metadata["path"],
            raw_metadata=self.metadata,
            method=self.metadata["method"],
            ip_address=self.metadata["ip_address"],
            user_agent=self.metadata["user_agent"],
            referer=self.metadata["referer"],
            accept_language=self.metadata["accept_language"],
            accept_encoding=self.metadata["accept_encoding"],
            username=self.data.get("username", ""),
            password=sanitize_password(self.data.get("password")),
            honeypot_triggered=self.data.get("honeypot_triggered", False),
            timing_issue=self.data.get("timing_issue"),
            elapsed_time=self.data.get("elapsed_time"),
        )

    def log_to_console(self) -> None:
        """Log honeypot trigger details to console or file."""

        if not honeyguard_settings.ENABLE_CONSOLE_LOGGING:
            return

        log_text = CONSOLE_LOG_FORMAT.format(**self._format_log_data())

        logger.warning(log_text)

    def send_email_alert(self) -> None:
        """Send email alert to configured recipients."""
        recipients = honeyguard_settings.EMAIL_RECIPIENTS or []

        if not recipients:
            logger.warning(
                "No email recipients configured; skipping email alert."
            )
            return

        subject_prefix = honeyguard_settings.EMAIL_SUBJECT_PREFIX
        subject = f"{subject_prefix} - {self.metadata['path']}"

        message = EMAIL_ALERT_BODY.format(
            **self._format_log_data(),
        )

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=honeyguard_settings.EMAIL_FROM
                or "noreply@example.com",
                recipient_list=recipients,
                fail_silently=False,
            )
            logger.info(f"Sent email alert to {len(recipients)} recipient(s)")
        except Exception as e:
            logger.error(f"Error sending email alert: {e}", exc_info=True)
