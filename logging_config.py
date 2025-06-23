import logging
import colorlog
import os
from pathlib import Path
from datetime import datetime

def setup_logging(log_level=logging.INFO):
    """Set up logging with both file and console output."""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Create a log file with timestamp
    log_file = log_dir / f"mirror_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    console_formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )

    # Set up file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(file_formatter)

    # Set up console handler
    console_handler = colorlog.StreamHandler()
    console_handler.setFormatter(console_formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Create logger for the application
    logger = logging.getLogger('mirror')
    logger.setLevel(log_level)

    return logger

# Create a function to get the logger
def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name."""
    return logging.getLogger(f"mirror.{name}") 