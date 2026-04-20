"""
Central app logging.
Usage:
    from log_setup import get_logger
    logger = get_logger(__name__)
"""
import logging, logging.handlers
from pathlib import Path

_LOGGER = None

def get_logger(name: str = None):
    global _LOGGER
    if _LOGGER is None:
        logdir = Path(__file__).resolve().parent / "logs"
        logdir.mkdir(parents=True, exist_ok=True)
        fh = logging.handlers.RotatingFileHandler(logdir / "app.log", maxBytes=1_000_000, backupCount=5, encoding="utf-8")
        fmt = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(filename)s:%(lineno)d - %(message)s")
        logger = logging.getLogger("app")
        logger.setLevel(logging.INFO)
        fh.setFormatter(fmt)
        logger.addHandler(fh)
        _LOGGER = logger
    return _LOGGER.getChild(name or "module")
