import os
import glob
import re
import pytest
from src import logger as mylogger

def test_log_file_creation_and_content():
    # Find the log file path as per logger.py logic
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
    log_pattern = os.path.join(log_dir, '*.log')
    # Remove any pre-existing log files to ensure a clean test
    for f in glob.glob(log_pattern):
        os.remove(f)


    # Reconfigure logger to ensure a FileHandler is attached for this test
    import logging
    for handler in list(mylogger.logger.handlers):
        mylogger.logger.removeHandler(handler)

    test_log_file = os.path.join(log_dir, 'pytest-test.log')
    file_handler = logging.FileHandler(test_log_file)
    file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    mylogger.logger.addHandler(file_handler)
    mylogger.logger.setLevel(logging.INFO)

    test_message = 'Test log message for logger.'
    mylogger.log_info(test_message)

    # Force flush of all handlers to ensure log is written
    for handler in mylogger.logger.handlers:
        handler.flush()

    # Check that the log file was created
    assert os.path.exists(test_log_file), 'No log file was created.'

    # Check file content before cleanup
    with open(test_log_file, 'r') as f:
        content = f.read()
    assert test_message in content, 'Log message not found in log file.'
    assert re.search(r'\[INFO\]', content), 'Log level [INFO] not found in log file.'

    # Clean up: close and remove the file handler before deleting the file
    mylogger.logger.removeHandler(file_handler)
    file_handler.close()
    os.remove(test_log_file)
    assert not os.path.exists(test_log_file), 'Log file was not deleted after test.'
    
def test_log_warning_file_content():
    import logging
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
    test_log_file = os.path.join(log_dir, 'pytest-warning.log')
    if os.path.exists(test_log_file):
        os.remove(test_log_file)
    for handler in list(mylogger.logger.handlers):
        mylogger.logger.removeHandler(handler)
    file_handler = logging.FileHandler(test_log_file)
    file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    mylogger.logger.addHandler(file_handler)
    mylogger.logger.setLevel(logging.INFO)
    test_message = 'Test warning log message.'
    mylogger.log_warning(test_message)
    for handler in mylogger.logger.handlers:
        handler.flush()
    assert os.path.exists(test_log_file), 'No log file was created.'
    with open(test_log_file, 'r') as f:
        content = f.read()
    assert test_message in content, 'Log message not found in log file.'
    assert re.search(r'\[WARNING\]', content), 'Log level [WARNING] not found in log file.'
    mylogger.logger.removeHandler(file_handler)
    file_handler.close()
    os.remove(test_log_file)

def test_log_error_file_content():
    import logging
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
    test_log_file = os.path.join(log_dir, 'pytest-error.log')
    if os.path.exists(test_log_file):
        os.remove(test_log_file)
    for handler in list(mylogger.logger.handlers):
        mylogger.logger.removeHandler(handler)
    file_handler = logging.FileHandler(test_log_file)
    file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    mylogger.logger.addHandler(file_handler)
    mylogger.logger.setLevel(logging.INFO)
    test_message = 'Test error log message.'
    mylogger.log_error(test_message)
    for handler in mylogger.logger.handlers:
        handler.flush()
    assert os.path.exists(test_log_file), 'No log file was created.'
    with open(test_log_file, 'r') as f:
        content = f.read()
    assert test_message in content, 'Log message not found in log file.'
    assert re.search(r'\[ERROR\]', content), 'Log level [ERROR] not found in log file.'
    mylogger.logger.removeHandler(file_handler)
    file_handler.close()
    os.remove(test_log_file)