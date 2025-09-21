
"""
logger.py
---------
This module provides logging utilities for the GIC Cinema Booking System.
It configures a file-based logger and exposes helper functions for info, warning, and error logs.
"""

import logging
from datetime import datetime
import os

LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

log_filename = datetime.now().strftime('%Y-%m-%d') + '.log'
log_path = os.path.join(LOG_DIR, log_filename)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler(log_path, mode='a')]  # Append mode
)

logger = logging.getLogger('gic-cbs')

def log_info(message):
    """
    Log an informational message to the log file.
    Args:
        message (str): The message to log.
    """
    logger.info(message)

def log_warning(message):
    """
    Log a warning message to the log file.
    Args:
        message (str): The message to log.
    """
    logger.warning(message)

def log_error(message):
    """
    Log an error message to the log file.
    Args:
        message (str): The message to log.
    """
    logger.error(message)