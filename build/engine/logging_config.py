#!/usr/bin/env python3
"""
Logging configuration for Patchwork Isles engine.
Provides structured logging with configurable levels and output formats.
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    log_to_console: bool = True,
    detailed_format: bool = False
) -> logging.Logger:
    """
    Set up logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        log_to_console: Whether to log to console
        detailed_format: Whether to use detailed log format with timestamps
    
    Returns:
        Configured logger instance
    """
    # Configure root logger
    logger = logging.getLogger("patchwork_isles")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatters
    if detailed_format:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
    else:
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_formatter = formatter
    
    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Use rotating file handler to prevent log files from growing too large
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # Always debug level for files
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name under the patchwork_isles hierarchy.
    
    Args:
        name: Name for the logger (will be prefixed with 'patchwork_isles.')
    
    Returns:
        Logger instance
    """
    return logging.getLogger(f"patchwork_isles.{name}")


def setup_game_logging(settings=None) -> logging.Logger:
    """
    Set up logging specifically for the game engine with appropriate defaults.
    
    Args:
        settings: Optional settings object with logging preferences
    
    Returns:
        Configured logger instance
    """
    # Default log level
    log_level = "INFO"
    log_to_file = True
    detailed_format = False
    
    # Override from settings if provided
    if settings and hasattr(settings, 'logging'):
        logging_config = getattr(settings, 'logging', {})
        log_level = logging_config.get('level', log_level)
        log_to_file = logging_config.get('to_file', log_to_file)
        detailed_format = logging_config.get('detailed', detailed_format)
    
    # Determine log file path
    log_file = None
    if log_to_file:
        # Default to logs directory in project root
        project_root = Path(__file__).parent.parent
        logs_dir = project_root / "logs"
        log_file = logs_dir / "patchwork_isles.log"
    
    return setup_logging(
        level=log_level,
        log_file=log_file,
        log_to_console=True,
        detailed_format=detailed_format
    )


class GameLogger:
    """Context manager for game session logging."""
    
    def __init__(self, session_id: Optional[str] = None, settings=None):
        self.session_id = session_id or f"session_{os.getpid()}"
        self.settings = settings
        self.logger = None
    
    def __enter__(self):
        self.logger = setup_game_logging(self.settings)
        self.logger.info(f"Starting game session: {self.session_id}")
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.logger:
            if exc_type:
                self.logger.error(f"Game session ended with error: {exc_val}")
            else:
                self.logger.info(f"Game session ended: {self.session_id}")


# Module-level convenience functions
def log_engine_event(message: str, level: str = "INFO") -> None:
    """Log an engine-level event."""
    logger = get_logger("engine")
    getattr(logger, level.lower())(message)


def log_story_event(message: str, level: str = "INFO") -> None:
    """Log a story-related event."""
    logger = get_logger("story")
    getattr(logger, level.lower())(message)


def log_save_event(message: str, level: str = "INFO") -> None:
    """Log a save/load related event."""
    logger = get_logger("save")
    getattr(logger, level.lower())(message)


def log_validation_event(message: str, level: str = "INFO") -> None:
    """Log a validation event."""
    logger = get_logger("validation")
    getattr(logger, level.lower())(message)