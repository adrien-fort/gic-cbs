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
    handlers=[logging.FileHandler(log_path)]  # Only file handler, no StreamHandler
)

logger = logging.getLogger('gic-cbs')

def log_info(message):
    logger.info(message)

def log_warning(message):
    logger.warning(message)

def log_error(message):
    logger.error(message)