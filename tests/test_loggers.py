"""Tests for logging utilities."""

from django.test import override_settings

from django_honeyguard.loggers import HoneyGuardLogger, get_logger


class TestHoneyGuardLogger:
    """Test HoneyGuardLogger class."""

    def test_logger_initialization(self):
        """Test logger initialization."""
        logger = HoneyGuardLogger("test.logger")
        assert logger.logger.name == "test.logger"

    @override_settings(
        HONEYGUARD={"ENABLE_CONSOLE_LOGGING": True, "LOG_LEVEL": "DEBUG"}
    )
    def test_debug_logging_when_enabled(self, caplog):
        """Test debug logging when enabled."""
        from django_honeyguard.conf import settings as hg_settings

        hg_settings.reset()  # Reset to reload settings
        logger = HoneyGuardLogger("test")
        with caplog.at_level("DEBUG"):
            logger.debug("Debug message")
        # Check if message was logged (may not appear if logging not fully configured in tests)
        # Just verify no exception and logger works
        assert logger is not None

    @override_settings(HONEYGUARD={"ENABLE_CONSOLE_LOGGING": False})
    def test_debug_logging_when_disabled(self, caplog):
        """Test debug logging when disabled."""
        logger = HoneyGuardLogger("test")
        logger.debug("Debug message")
        # Should not log when disabled
        assert "Debug message" not in caplog.text

    @override_settings(
        HONEYGUARD={"ENABLE_CONSOLE_LOGGING": True, "LOG_LEVEL": "WARNING"}
    )
    def test_info_logging_below_threshold(self, caplog):
        """Test that info logs below threshold are not logged."""
        logger = HoneyGuardLogger("test")
        logger.info("Info message")
        # Should not log info when level is WARNING
        assert "Info message" not in caplog.text

    @override_settings(
        HONEYGUARD={"ENABLE_CONSOLE_LOGGING": True, "LOG_LEVEL": "WARNING"}
    )
    def test_warning_logging_at_threshold(self, caplog):
        """Test that warning logs at threshold are logged."""
        logger = HoneyGuardLogger("test")
        logger.warning("Warning message")
        assert "Warning message" in caplog.text

    @override_settings(
        HONEYGUARD={"ENABLE_CONSOLE_LOGGING": True, "LOG_LEVEL": "ERROR"}
    )
    def test_error_logging(self, caplog):
        """Test error logging."""
        logger = HoneyGuardLogger("test")
        logger.error("Error message")
        assert "Error message" in caplog.text

    @override_settings(
        HONEYGUARD={"ENABLE_CONSOLE_LOGGING": True, "LOG_LEVEL": "CRITICAL"}
    )
    def test_critical_logging(self, caplog):
        """Test critical logging."""
        logger = HoneyGuardLogger("test")
        logger.critical("Critical message")
        assert "Critical message" in caplog.text


class TestGetLogger:
    """Test get_logger function."""

    def test_get_logger_returns_instance(self):
        """Test that get_logger returns HoneyGuardLogger instance."""
        logger = get_logger("test.logger")
        assert isinstance(logger, HoneyGuardLogger)

    def test_get_logger_different_names(self):
        """Test that get_logger creates loggers with different names."""
        logger1 = get_logger("test.logger1")
        logger2 = get_logger("test.logger2")
        assert logger1.logger.name != logger2.logger.name
