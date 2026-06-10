"""
Logging configuration and utilities.
"""

from loguru import logger
import sys


def setup_logging(debug_mode: bool = False, log_file: str = None):
    """
    Configure logging for BEAT SYNC FUNC.
    
    Args:
        debug_mode: Enable debug level logging
        log_file: Optional file path for logging
    """
    # Remove default handler
    logger.remove()
    
    # Add console handler
    log_level = "DEBUG" if debug_mode else "INFO"
    logger.add(
        sys.stdout,
        format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=log_level,
    )
    
    # Add file handler if specified
    if log_file:
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=log_level,
            rotation="500 MB",
            retention="10 days",
        )
