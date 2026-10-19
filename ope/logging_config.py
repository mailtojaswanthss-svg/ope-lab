"""Central logging configuration for OPE Lab.

Logs to both console and logs/app.log without bare prints.
"""

from __future__ import annotations

import logging
from pathlib import Path

_LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"
_LOG_FILE = _LOGS_DIR / "app.log"


def configure_logging(level: int = logging.INFO) -> logging.Logger:
    """Configures and returns the central logger for OPE Lab.

    Logs to both console (StreamHandler) and logs/app.log (FileHandler).

    Args:
        level: Logging level (e.g. logging.INFO).

    Returns:
        Configured Logger instance.
    """
    _LOGS_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("ope_lab")
    if logger.hasHandlers():
        return logger

    logger.setLevel(level)
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    logger.addHandler(file_handler)

    logger.propagate = False
    return logger


logger = configure_logging()
