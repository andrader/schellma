"""Test logging functionality."""

import logging
from io import StringIO

from schellma.logger import disable_logging, get_logger, setup_logging


class TestLogging:
    """Test logging configuration and functionality."""

    def test_get_logger(self):
        """Test getting the schellma logger."""
        logger = get_logger()
        assert logger.name == "schellma"
        assert isinstance(logger, logging.Logger)

    def test_setup_logging_default(self):
        """Test setting up logging with default configuration."""
        # Capture log output
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)

        setup_logging(level=logging.INFO, handler=handler)

        logger = get_logger()
        logger.info("Test message")

        output = log_stream.getvalue()
        assert "schellma - INFO - Test message" in output

    def test_setup_logging_custom_format(self):
        """Test setting up logging with custom format."""
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)

        setup_logging(
            level=logging.DEBUG,
            format_string="CUSTOM: %(levelname)s - %(message)s",
            handler=handler,
        )

        logger = get_logger()
        logger.debug("Debug message")

        output = log_stream.getvalue()
        assert "CUSTOM: DEBUG - Debug message" in output

    def test_disable_logging(self):
        """Test disabling logging."""
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)

        # First enable logging
        setup_logging(level=logging.DEBUG, handler=handler)
        logger = get_logger()
        logger.info("This should appear")

        # Then disable it
        disable_logging()
        logger.critical("This should not appear")

        output = log_stream.getvalue()
        assert "This should appear" in output
        assert "This should not appear" not in output

    def test_logging_levels(self):
        """Test different logging levels."""
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)

        setup_logging(level=logging.WARNING, handler=handler)
        logger = get_logger()

        logger.debug("Debug message")  # Should not appear
        logger.info("Info message")  # Should not appear
        logger.warning("Warning message")  # Should appear
        logger.error("Error message")  # Should appear

        output = log_stream.getvalue()
        assert "Debug message" not in output
        assert "Info message" not in output
        assert "Warning message" in output
        assert "Error message" in output

    def test_logger_propagation(self):
        """Test that logger doesn't propagate to root logger."""
        setup_logging(level=logging.INFO)
        logger = get_logger()
        assert logger.propagate is False

    def test_multiple_setup_calls(self):
        """Test that multiple setup calls don't create duplicate handlers."""
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)

        # Set up logging twice
        setup_logging(level=logging.INFO, handler=handler)
        setup_logging(level=logging.INFO, handler=handler)

        logger = get_logger()
        logger.info("Test message")

        output = log_stream.getvalue()
        # Should only appear once, not twice
        assert output.count("Test message") == 1
