"""
Logging Utility
Provides consistent logging and tool call wrapping
"""

import time
from functools import wraps
from loguru import logger
from typing import Any, Callable


def setup_logger(log_dir: str = "logs", log_level: str = "INFO"):
    """
    Configure the logger with file and console output.

    Args:
        log_dir: Directory to store log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    logger.add(
        f"{log_dir}/assistant_{{time}}.log",
        rotation="1 day",
        retention="7 days",
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    )
    logger.info("Logger initialized")


def log_tool_call(func: Callable) -> Callable:
    """
    Decorator to log tool calls with timing and results.

    Args:
        func: The function to wrap

    Returns:
        Wrapped function with logging
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        tool_name = func.__name__
        logger.info(f"🔧 Tool Call: {tool_name}")
        logger.debug(f"   Args: {args}")
        logger.debug(f"   Kwargs: {kwargs}")

        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.info(f"✓ Tool {tool_name} completed in {elapsed:.2f}s")
            logger.debug(f"   Result preview: {str(result)[:200]}...")
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"✗ Tool {tool_name} failed after {elapsed:.2f}s: {str(e)}")
            raise

    return wrapper
