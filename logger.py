"""
Logging configuration for the Mini AI Assistant.

Provides structured logging with different levels and formatters.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = "mini_ai_assistant",
    level: int = logging.INFO,
    log_file: Optional[Path] = None
) -> logging.Logger:
    """
    Set up application logger.
    
    Args:
        name: Logger name.
        level: Logging level.
        log_file: Optional file path for logging.
        
    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# Default logger instance
logger = setup_logger()
