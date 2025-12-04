# backend/utils/logger.py
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from backend.config import get_settings


def _build_log_format():
    return (
        "%(asctime)s | %(levelname)s | %(name)s | "
        "%(filename)s:%(lineno)d | %(message)s"
    )


def _create_file_handler(log_dir: Path, log_name: str, level: str) -> RotatingFileHandler:
    """
    Creates rotating file handler:
    - 5MB per file
    - 5 backup files
    """
    log_file = log_dir / f"{log_name}.log"
    handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
    )
    handler.setLevel(level)
    formatter = logging.Formatter(_build_log_format())
    handler.setFormatter(formatter)
    return handler


def get_logger(name: str) -> logging.Logger:
    """
    Global logger factory.
    Uses env LOG_LEVEL and LOG_DIR.
    """
    settings = get_settings()

    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL)

    if logger.handlers:
        return logger  # Prevent duplicate handlers

    # Console Handler (always)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(settings.LOG_LEVEL)
    console_handler.setFormatter(logging.Formatter(_build_log_format()))
    logger.addHandler(console_handler)

    # File Handler
    try:
        file_handler = _create_file_handler(settings.LOG_DIR, name, settings.LOG_LEVEL)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.error(f"Failed to create file logger: {e}")

    logger.propagate = False
    return logger