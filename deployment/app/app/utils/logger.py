import sys
from pathlib import Path
from loguru import logger as _logger
from app.config import settings

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

_logger.remove()

# Console logger
_logger.add(
    sys.stdout,
    level=settings.LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level:<8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    colorize=True,
    enqueue=True,
)

# File logger
_logger.add(
    LOG_DIR / "app.log",
    rotation="20 MB",
    retention="14 days",
    compression="zip",
    level=settings.LOG_LEVEL,
    enqueue=True,
)

logger = _logger
app_logger = _logger

__all__ = ["logger", "app_logger"]
