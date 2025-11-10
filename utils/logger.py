"""
Logging utility for PHP to FastAPI converter.
"""

import logging
import sys
import os
from typing import Optional
from pathlib import Path


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output for better readability."""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green  
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'ENDC': '\033[0m',       # End color
        'BOLD': '\033[1m',       # Bold
    }
    
    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors and sys.stdout.isatty()
        super().__init__()
    
    def format(self, record):
        if self.use_colors:
            log_color = self.COLORS.get(record.levelname, '')
            reset_color = self.COLORS['ENDC']
            bold = self.COLORS['BOLD']
            
            # Format the level name with color
            record.levelname = f"{bold}{log_color}{record.levelname}{reset_color}"
        
        # Create custom format based on level
        if record.levelname.endswith('DEBUG'):
            fmt = '[%(asctime)s] %(levelname)s %(name)s:%(lineno)d - %(message)s'
        else:
            fmt = '%(levelname)s - %(message)s'
        
        formatter = logging.Formatter(fmt, datefmt='%H:%M:%S')
        return formatter.format(record)


def setup_logger(
    name: str = "php2fastapi",
    level: Optional[str] = None,
    verbose: bool = False,
    debug: bool = False,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Setup logger with appropriate configuration.
    
    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        verbose: Enable verbose output
        debug: Enable debug mode
        log_file: Optional log file path
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Determine log level
    if debug:
        log_level = logging.DEBUG
    elif verbose:
        log_level = logging.INFO
    elif level:
        log_level = getattr(logging, level.upper(), logging.INFO)
    else:
        # Check environment variable
        env_debug = os.getenv('DEBUG', '').lower() in ('1', 'true', 'yes')
        log_level = logging.DEBUG if env_debug else logging.INFO
    
    logger.setLevel(log_level)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(ColoredFormatter(use_colors=True))
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Always debug level for files
        
        file_formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s %(name)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        logger.info(f"Logging to file: {log_file}")
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_logger(name: str = "php2fastapi") -> logging.Logger:
    """Get existing logger instance."""
    return logging.getLogger(name)


class LoggerMixin:
    """Mixin class to add logging capability to any class."""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        if not hasattr(self, '_logger'):
            self._logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        return self._logger