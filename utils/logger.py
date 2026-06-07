import logging
import os
from logging.handlers import RotatingFileHandler

LOG_FILE = "filemaster.log"

def setup_logger():
    """Configura y devuelve el logger principal de la aplicación."""
    logger = logging.getLogger("FileMaster")
    logger.setLevel(logging.DEBUG)
    
    # Avoid duplicate handlers if already configured
    if logger.handlers:
        return logger

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler (Rotating, max 5MB, keep 3 backups)
    try:
        file_handler = RotatingFileHandler(
            LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not create log file: {e}")

    return logger

# Global logger instance
logger = setup_logger()
