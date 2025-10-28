from typing import Optional, Tuple

from django.conf import settings as dj_settings
from django.core.mail import send_mail
from django.http import HttpRequest
from django.utils import timezone

from .conf import settings as honeyguard_settings
from .loggers import get_logger
from .models import TimingIssue

logger = get_logger(__name__)


def get_client_ip(request: HttpRequest) -> str:
    """
    Extract the client's IP address, honoring X-Forwarded-For if present.

    Args:
        request: Django HttpRequest object

    Returns:
        str: Client IP address
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        # Take the first IP in the chain
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def get_request_metadata(request: HttpRequest) -> dict:
    """
    Collect request metadata for logging and alerting.

    Args:
        request: Django HttpRequest object

    Returns:
        dict: Dictionary containing request metadata
    """
    return {
        "ip_address": get_client_ip(request),
        "user_agent": request.META.get("HTTP_USER_AGENT", ""),
        "referer": request.META.get("HTTP_REFERER", ""),
        "accept_language": request.META.get("HTTP_ACCEPT_LANGUAGE", ""),
        "accept_encoding": request.META.get("HTTP_ACCEPT_ENCODING", ""),
        "timestamp": timezone.now().isoformat(),
        "path": request.path,
        "request_method": request.method,
    }


def check_timing_attack(
    render_time: str,
) -> Tuple[Optional[str], Optional[float]]:
    """
    Check if form submission timing is suspicious.

    Args:
        render_time: ISO format timestamp when form was rendered

    Returns:
        tuple: (timing_issue, elapsed_time) where timing_issue is a TimingIssue choice
               or None if valid timing
    """

    try:
        submit_time = timezone.now()
        render_time_dt = timezone.datetime.fromisoformat(render_time)

        # Make datetime timezone-aware if needed
        if timezone.is_naive(render_time_dt):
            render_time_dt = timezone.make_aware(render_time_dt)

        elapsed = (submit_time - render_time_dt).total_seconds()

        if elapsed < honeyguard_settings.TIMING_TOO_FAST_THRESHOLD:
            return TimingIssue.TOO_FAST, elapsed

        if elapsed > honeyguard_settings.TIMING_TOO_SLOW_THRESHOLD:
            return TimingIssue.TOO_SLOW, elapsed

        return TimingIssue.VALID, elapsed

    except (ValueError, TypeError) as e:
        logger.warning(f"Error parsing render time: {e}")
        return None, None


def build_email_body(
    ip_address: str,
    request: HttpRequest,
    username: str,
    password: str,
    user_agent: str,
    referer: str,
    timing_issue: Optional[str],
    elapsed_time: Optional[float],
    honeypot_triggered_flag: bool,
    data: dict,
) -> str:
    """
    Build email body content for honeypot alerts.

    Args:
        ip_address: IP address of requester
        request: Django HttpRequest object
        username: Attempted username
        password: Attempted password
        user_agent: User agent string
        referer: HTTP referer
        timing_issue: Type of timing anomaly (if any)
        elapsed_time: Time elapsed between render and submit
        honeypot_triggered_flag: Whether honeypot field was filled
        data: Full metadata dictionary

    Returns:
        str: Formatted email body
    """
    email_lines = [
        f"🚨 Honeypot Alert - {request.path}",
        "",
        "=== Request Details ===",
        f"IP Address: {ip_address}",
        f"Path: {request.path}",
        f"Method: {request.method}",
        f"Timestamp: {data.get('timestamp', 'N/A')}",
        "",
        "=== Authentication Attempt ===",
        f"Username: {username or '(empty)'}",
        f"Password: {password or '(empty)'}",
        "",
        "=== Detection Flags ===",
        f"Honeypot Field Triggered: {'✓ YES' if honeypot_triggered_flag else '✗ No'}",
        f"Timing Issue: {timing_issue or 'None'}",
    ]

    if elapsed_time is not None:
        email_lines.append(f"Submission Time: {elapsed_time:.2f} seconds")

    email_lines.extend(
        [
            "",
            "=== Browser & Environment ===",
            f"User Agent: {user_agent or '(empty)'}",
            f"Referer: {referer or 'None'}",
            f"Accept-Language: {data.get('accept_language', 'N/A')}",
            f"Accept-Encoding: {data.get('accept_encoding', 'N/A')}",
            "",
            "=== Full Metadata ===",
            str(data),
        ]
    )

    return "\n".join(email_lines)


def send_email_alert(subject: str, message: str) -> bool:
    """
    Send email alert to configured recipients.

    Args:
        subject: Email subject line
        message: Email body content

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    recipients = honeyguard_settings.EMAIL_RECIPIENTS or []

    if not recipients:
        logger.debug("No email recipients configured, skipping alert")
        return False

    from_email = (
        honeyguard_settings.EMAIL_FROM
        or getattr(dj_settings, "DEFAULT_FROM_EMAIL", None)
        or "noreply@example.com"
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipients,
            fail_silently=False,
        )
        logger.info(f"Email alert sent to {len(recipients)} recipient(s)")
        return True

    except Exception as e:
        logger.error(f"Failed to send email alert: {e}", exc_info=True)
        return False
