import logging
from logging.handlers import RotatingFileHandler

def setup_logging(logger):
    logger.setLevel(logging.INFO)

    file_handler = RotatingFileHandler('app.log', maxBytes=1e9, backupCount=3)
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger

def get_logger(logger_name='my_app'):
    logger = logging.getLogger(logger_name)
    
    if not logger.hasHandlers():
        setup_logging(logger)
    
    return logger
