import logging
from logging.handlers import RotatingFileHandler
from flask import has_request_context, request

class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None
        return super().format(record)

def setup():
    logger = logging.getLogger()

    formatter = RequestFormatter('%(asctime)s; %(remote_addr)s; %(url)s; %(levelname)s; %(message)s')

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)

    fileHandler = logging.FileHandler('log_file.csv')
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    return logger




