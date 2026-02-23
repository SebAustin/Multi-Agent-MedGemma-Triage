"""
Logging configuration for the application.
"""
import sys
from pathlib import Path
from loguru import logger
from config import LogConfig

# Remove default handler
logger.remove()

# Add console handler
logger.add(
    sys.stderr,
    format=LogConfig.FORMAT,
    level=LogConfig.LEVEL,
    colorize=True
)

# Add file handler
logger.add(
    LogConfig.LOG_FILE,
    format=LogConfig.FORMAT,
    level=LogConfig.LEVEL,
    rotation=LogConfig.ROTATION,
    retention=LogConfig.RETENTION,
    compression=LogConfig.COMPRESSION
)

__all__ = ["logger"]
