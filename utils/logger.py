"""
Logging Configuration
=====================
Provides a project-wide logger with console and file handlers.
Logs are written to PROJECT_ROOT/logs/traffic_system.log.

Usage:
    from utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Application started")
"""

import logging
import sys
from pathlib import Path

# Log directory (created lazily)
_LOG_DIR = Path(__file__).parent.parent / "logs"
_LOG_FILE = _LOG_DIR / "traffic_system.log"


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name:  Logger name (typically __name__).
        level: Logging level (default INFO).

    Returns:
        Configured logging.Logger instance.
    """
    logger = logging.getLogger(name)

    # Prevent adding duplicate handlers if called multiple times
    if logger.handlers:
        return logger

    logger.setLevel(level)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ── Console Handler ────────────────────────────────────────────
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # ── File Handler ───────────────────────────────────────────────
    try:
        _LOG_DIR.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except OSError:
        logger.warning("Could not create log file handler. Logging to console only.")

    return logger
