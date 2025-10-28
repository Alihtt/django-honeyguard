import ipaddress

from django.apps import apps
from django.dispatch import receiver

from .conf import settings as honeyguard_settings
from .loggers import get_logger
from .models import HoneyGuardLog, TimingIssue
from .signals import honeypot_triggered
from .utils import build_email_body, get_client_ip, send_email_alert

logger = get_logger(__name__)


def validate_ip_address(ip_address):
    """
    Validate and normalize IP address.

    Args:
        ip_address: IP address string to validate

    Returns:
        str: Valid IP address or 'invalid'
    """
    try:
        ipaddress.ip_address(ip_address)
        return ip_address
    except (ValueError, ipaddress.AddressValueError):
        logger.warning(f"Invalid IP address received: {ip_address}")
        return "invalid"


def log_to_database(request, ip_address, data):
    """
    Log honeypot trigger to database.

    Args:
        request: Django HttpRequest object
        ip_address: Validated IP address
        data: Dictionary containing trigger data
    """

    if not apps.is_installed("django_honeyguard"):
        logger.warning(
            "django_honeyguard app not installed, cannot log to database"
        )
        return

    try:
        HoneyGuardLog.objects.create(
            ip_address=ip_address,
            path=request.path,
            username_attempted=data.get("username_attempted", ""),
            password_attempted=data.get("password_attempted", ""),
            honeypot_triggered=data.get("honeypot_triggered", False),
            user_agent=data.get("user_agent", ""),
            referer=data.get("referer", ""),
            accept_language=data.get("accept_language", ""),
            accept_encoding=data.get("accept_encoding", ""),
            request_method=request.method,
            timing_issue=data.get("timing_issue", TimingIssue.VALID),
            elapsed_time=data.get("elapsed_time"),
            raw_metadata=data,
        )
        logger.debug(
            f"Logged honeypot trigger to database: IP={ip_address}, Path={request.path}"
        )
    except Exception as e:
        logger.error(
            f"Failed to log honeypot trigger to database: {e}", exc_info=True
        )


def log_to_console(request, ip_address, data):
    """
    Log honeypot trigger to console/file logs.

    This function will only log if ENABLE_CONSOLE_LOGGING is True.

    Args:
        request: Django HttpRequest object
        ip_address: IP address of requester
        data: Dictionary containing trigger data
    """
    username = data.get("username_attempted", "")
    user_agent = data.get("user_agent", "")
    timing_issue = data.get("timing_issue")
    elapsed_time = data.get("elapsed_time")
    honeypot_triggered_flag = data.get("honeypot_triggered", False)
    referer = data.get("referer", "")

    log_parts = [
        f"Honeypot triggered: IP={ip_address}",
        f"Path={request.path}",
        f"Username={username}",
        f"UserAgent={user_agent}",
    ]

    if timing_issue:
        log_parts.append(f"TimingIssue={timing_issue} ({elapsed_time}s)")

    if honeypot_triggered_flag:
        log_parts.append("HoneypotFieldFilled=True")

    if referer:
        log_parts.append(f"Referer={referer}")

    log_msg = ", ".join(log_parts)
    logger.warning(log_msg)


def send_alert_email(request, ip_address, data):
    """
    Send email alert for honeypot trigger.

    Args:
        request: Django HttpRequest object
        ip_address: IP address of requester
        data: Dictionary containing trigger data
    """
    if not honeyguard_settings.EMAIL_RECIPIENTS:
        logger.debug("No email recipients configured, skipping alert")
        return

    subject_prefix = (
        honeyguard_settings.EMAIL_SUBJECT_PREFIX or "🚨 Honeypot Alert"
    )
    subject = f"{subject_prefix} - {request.path}"

    message = build_email_body(
        ip_address=ip_address,
        request=request,
        username=data.get("username_attempted", ""),
        password=data.get("password_attempted", ""),
        user_agent=data.get("user_agent", ""),
        referer=data.get("referer", ""),
        timing_issue=data.get("timing_issue"),
        elapsed_time=data.get("elapsed_time"),
        honeypot_triggered_flag=data.get("honeypot_triggered", False),
        data=data,
    )

    send_email_alert(subject, message)


@receiver(honeypot_triggered)
def handle_honeypot_trigger(sender, request, data, **kwargs):
    """
    Handle honeypot triggers: log to DB, console, and send email alerts.

    This is the main entry point for all honeypot detections.
    It coordinates logging to different destinations based on settings.

    Args:
        sender: Signal sender (view class)
        request: Django HttpRequest object
        data: Dictionary containing trigger data
        **kwargs: Additional signal arguments
    """
    # Extract and validate IP address
    ip_address = data.get("ip_address", get_client_ip(request))
    ip_address = validate_ip_address(ip_address)

    # Log to database if enabled
    log_to_database(request, ip_address, data)

    # Log to console if enabled (logger will check ENABLE_CONSOLE_LOGGING)
    log_to_console(request, ip_address, data)

    # Send email alerts if configured
    send_alert_email(request, ip_address, data)
