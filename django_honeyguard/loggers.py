"""Logging utilities for django-honeyguard."""

import logging
from typing import Any

from .conf import settings as honeyguard_settings


class HoneyGuardLogger:
    """
    Custom logger wrapper that respects HoneyGuard settings.

    This logger checks ENABLE_CONSOLE_LOGGING before actually logging,
    and respects the configured LOG_LEVEL.
    """

    def __init__(self, name: str) -> None:
        """
        Initialize logger with given name.

        Args:
            name: Logger name (usually __name__)
        """
        self.logger: logging.Logger = logging.getLogger(name)
        self._log_level_map: dict[str, int] = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }

    def _should_log(self, level: int) -> bool:
        """
        Check if logging is enabled and level is appropriate.

        Args:
            level: Logging level (e.g., logging.WARNING)

        Returns:
            bool: True if should log, False otherwise
        """
        if not honeyguard_settings.ENABLE_CONSOLE_LOGGING:
            return False

        # Get configured minimum level
        configured_level_str = honeyguard_settings.LOG_LEVEL.upper()
        configured_level = self._log_level_map.get(
            configured_level_str, logging.WARNING
        )

        # Only log if the message level meets or exceeds configured level
        return level >= configured_level

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log debug message if enabled."""
        if self._should_log(logging.DEBUG):
            self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log info message if enabled."""
        if self._should_log(logging.INFO):
            self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log warning message if enabled."""
        if self._should_log(logging.WARNING):
            self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log error message if enabled."""
        if self._should_log(logging.ERROR):
            self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log critical message if enabled."""
        if self._should_log(logging.CRITICAL):
            self.logger.critical(msg, *args, **kwargs)


def get_logger(name: str) -> HoneyGuardLogger:
    """
    Get a HoneyGuard logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        HoneyGuardLogger: Logger instance that respects HoneyGuard settings
    """
    return HoneyGuardLogger(name)
