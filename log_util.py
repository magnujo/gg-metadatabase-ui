import logging
from logging.handlers import RotatingFileHandler
from flask import has_request_context, request


def console_logger():
    # Configure logging to console
    console_handler = logging.StreamHandler()
    # console_handler.setLevel(logging.INFO)  # Set the desired logging level for the console
    console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    return console_handler
    
def file_logger():
    file_handler = RotatingFileHandler('flask_app.log', maxBytes=1024*1024, backupCount=10)
    file_handler.setLevel(logging.NOTSET)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    return file_handler



