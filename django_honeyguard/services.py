"""Business logic for HoneyGuard honeypot triggers."""

from typing import Any, Dict, Optional

from django.core.mail import send_mail
from django.http import HttpRequest

from .conf import settings as honeyguard_settings
from .constants import CONSOLE_LOG_FORMAT, EMAIL_ALERT_BODY
from .loggers import get_logger
from .models import HoneyGuardLog, TimingIssue
from .utils import check_timing_attack, get_request_metadata, sanitize_password

logger = get_logger(__name__)


class HoneyGuardService:
    """Encapsulates core business logic for honeypot event processing."""

    def __init__(
        self, request: HttpRequest, data: Optional[Dict[str, Any]] = None
    ) -> None:
        self.request: HttpRequest = request
        self.metadata: Dict[str, str] = get_request_metadata(request)

        elapsed_time = 0.0
        timing_issue = TimingIssue.VALID

        if data:
            render_time = data.get("render_time")
            if render_time:
                timing_issue, elapsed_time = check_timing_attack(render_time)
            honeypot_triggered = bool(data.get("hp", "").strip())

            data["honeypot_triggered"] = honeypot_triggered
            data["timing_issue"] = timing_issue
            data["elapsed_time"] = elapsed_time
            self.data: Dict[str, Any] = data
        else:
            self.data = {
                "timing_issue": timing_issue,
                "elapsed_time": elapsed_time,
                "honeypot_triggered": False,
            }

    def _format_log_data(self) -> Dict[str, Any]:
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
        """
        Send email alert to configured recipients.

        This method handles email sending with proper error handling.
        Email failures will not raise exceptions by default to prevent
        disrupting the honeypot detection flow.
        """
        recipients = honeyguard_settings.EMAIL_RECIPIENTS or []

        if not recipients:
            logger.debug("No email recipients configured; skipping email alert.")
            return

        subject_prefix = honeyguard_settings.EMAIL_SUBJECT_PREFIX
        subject = f"{subject_prefix} - {self.metadata['path']}"

        try:
            message = EMAIL_ALERT_BODY.format(**self._format_log_data())
        except KeyError as e:
            logger.error(
                f"Error formatting email message: missing key {e}",
                exc_info=True,
            )
            return

        # Get fail_silently setting (defaults to True for resilience)
        fail_silently = honeyguard_settings.EMAIL_FAIL_SILENTLY or True

        try:
            from_email = honeyguard_settings.EMAIL_FROM
            if not from_email:
                from_email = None  # Let Django use DEFAULT_FROM_EMAIL

            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=recipients,
                fail_silently=fail_silently,
            )
            logger.info(f"Sent email alert to {len(recipients)} recipient(s)")
        except Exception as e:
            logger.error(
                f"Error sending email alert to {len(recipients)} recipient(s): {e}",
                exc_info=True,
            )
            # If fail_silently is False and we still got an exception, log critical
            if not fail_silently:
                logger.critical(
                    "Email sending failed with fail_silently=False. "
                    "Check email configuration immediately."
                )
