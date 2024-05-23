import logging
from functools import wraps
from logging.handlers import RotatingFileHandler
from flask import request
from constants.misc_constants import DATABASE_CONFIG_2
import psycopg2

def db_stuff(func):
    def wrapper():
        conn = psycopg2.connect(**DATABASE_CONFIG_2)

        cur = conn.cursor()
        
        func()  # Call the original function
        cur.close()
        conn.close() 
    return wrapper


def log_info(app):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # # Add functionality before calling the view function
            # ip_address = request.remote_addr
            app.logger.info(f'Running: {str(func.__name__)}')
            
            # # You can access request, session, or any other Flask objects here if needed
            # # For example, to access request arguments: request.args
            
            # # Call the original view function
            result = func(*args, **kwargs)
            
            # # Add functionality after calling the view function
            # # You can modify the result if needed before returning
            
            return result
        return wrapper
    return decorator
