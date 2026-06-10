"""Logging configuration for ART.WE.ED.IT"""

import logging
from pathlib import Path
from loguru import logger as loguru_logger


def setup_logging(log_file: str = "logs/art_we_ed_it.log", level: str = "INFO") -> None:
    """Configure logging for the application"""
    
    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Remove default handler
    loguru_logger.remove()
    
    # Add file handler
    loguru_logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=level,
        rotation="500 MB",
        retention="30 days"
    )
    
    # Add console handler
    loguru_logger.add(
        lambda msg: print(msg, end=""),
        format="<level>{time:HH:mm:ss}</level> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=level
    )


def get_logger(name: str):
    """Get logger instance"""
    return loguru_logger.bind(name=name)
