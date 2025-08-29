"""Logging configuration for scheLLMa package.

This module provides optional logging functionality for debugging
and monitoring conversion operations. Logging is disabled by default
and can be enabled by users as needed.

## Example

```python
import logging
from schellma.logging import setup_logging
setup_logging(level=logging.DEBUG)
# Now scheLLMa operations will log debug information
```
"""

import logging

# Create a logger for the schellma package
logger = logging.getLogger("schellma")
logger.setLevel(logging.WARNING)  # Default to WARNING level


def setup_logging(
    level: int = logging.INFO,
    format_string: str | None = None,
    handler: logging.Handler | None = None,
) -> None:
    """Set up logging for schellma operations.

    This function configures logging for the schellma package. By default,
    schellma uses minimal logging to avoid interfering with user applications.

    Args:
        level: Logging level (e.g., logging.DEBUG, logging.INFO)
        format_string: Custom format string for log messages
        handler: Custom logging handler (if None, uses StreamHandler)

    Example:
        >>> import logging
        >>> from schellma.logging import setup_logging
        >>> # Enable debug logging
        >>> setup_logging(level=logging.DEBUG)
        >>> # Custom format
        >>> setup_logging(
        ...     level=logging.INFO,
        ...     format_string="%(asctime)s - %(name)s - %(message)s"
        ... )
    """
    # Remove existing handlers to avoid duplicates
    for existing_handler in logger.handlers[:]:
        logger.removeHandler(existing_handler)

    # Set up the handler
    if handler is None:
        handler = logging.StreamHandler()

    # Set up the formatter
    if format_string is None:
        format_string = "%(name)s - %(levelname)s - %(message)s"

    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)

    # Configure the logger
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False  # Don't propagate to root logger


def disable_logging() -> None:
    """Disable all logging for schellma operations.

    This function disables logging by setting the level to CRITICAL+1,
    effectively silencing all log messages.

    Example:
        >>> from schellma.logging import disable_logging
        >>> disable_logging()
        # Now schellma operations will not produce any log output
    """
    logger.setLevel(logging.CRITICAL + 1)


def get_logger() -> logging.Logger:
    """Get the schellma logger instance.

    This function returns the logger instance used by schellma,
    allowing users to configure it directly if needed.

    Returns:
        The schellma logger instance

    Example:
        >>> from schellma.logging import get_logger
        >>> logger = get_logger()
        >>> logger.setLevel(logging.DEBUG)
    """
    return logger
