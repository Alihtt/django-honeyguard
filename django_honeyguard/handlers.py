"""Signal handlers for honeypot events."""

from django.dispatch import receiver

from .loggers import get_logger
from .services import HoneyGuardService
from .signals import honeypot_triggered

logger = get_logger(__name__)


@receiver(honeypot_triggered)
def handle_honeypot_trigger(sender, request, data, **_kwargs):
    """
    Handle honeypot triggers by delegating to HoneyGuardService.

    Args:
        _sender: Signal sender (unused, prefixed with _)
        request: Django HttpRequest object
        data: Dictionary containing trigger data
        **_kwargs: Additional signal arguments (unused, prefixed with _)
    """
    service = HoneyGuardService(request, data)
    service.log_trigger()
    service.log_to_console()
    service.send_email_alert()
