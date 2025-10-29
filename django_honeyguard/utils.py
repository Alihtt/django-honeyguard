"""Utility functions for django-honeyguard."""

import ipaddress
from datetime import datetime
from typing import Optional, Tuple

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
        ip_address = x_forwarded_for.split(",")[0].strip()
    else:
        ip_address = request.META.get("REMOTE_ADDR", "unknown")

    try:
        ipaddress.ip_address(ip_address)
        return ip_address
    except (ValueError, ipaddress.AddressValueError):
        logger.warning(f"Invalid IP address received: {ip_address}")
        return "0.0.0.0"


def sanitize_password(password: str) -> str:
    """
    Sanitize password by replacing it with asterisks.
    """
    if not password:
        return ""

    return f"***{len(password)} chars***"


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
        "created_at": timezone.now().isoformat(),
        "path": request.path,
        "method": request.method,
    }


def check_timing_attack(
    render_time: Optional[str],
) -> Tuple[str, float]:
    """
    Check if form submission timing is suspicious.

    Args:
        render_time: ISO format created_at when form was rendered, or None

    Returns:
        tuple: (timing_issue, elapsed_time) where timing_issue is a TimingIssue choice
               and elapsed_time is in seconds
    """
    timing_issue = TimingIssue.VALID
    elapsed_time = 0.0

    if not render_time:
        return timing_issue, elapsed_time

    try:
        submit_time = timezone.now()
        render_time_dt = datetime.fromisoformat(render_time)

        # Make datetime timezone-aware if needed
        if timezone.is_naive(render_time_dt):
            render_time_dt = timezone.make_aware(render_time_dt)

        elapsed_time = (submit_time - render_time_dt).total_seconds()
        if elapsed_time < honeyguard_settings.TIMING_TOO_FAST_THRESHOLD:
            timing_issue = TimingIssue.TOO_FAST
        elif elapsed_time > honeyguard_settings.TIMING_TOO_SLOW_THRESHOLD:
            timing_issue = TimingIssue.TOO_SLOW

        return timing_issue, elapsed_time

    except (ValueError, TypeError) as e:
        logger.warning(f"Error parsing render time: {e}")
        return timing_issue, elapsed_time
