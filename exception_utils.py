from utils.CustomExceptions import DontTriggerFileDeletion
from functools import wraps
from flask import redirect, url_for, session
import pandas as pd
import os
from constants import PARSED_SHEETS_FOLDER, ORIGINAL_FILES, UPLOAD_FOLDER, DATABASE_CONFIG, DATABASE_CONFIG_2
import psycopg2

def delete_files(file_name, original=False, parsed=False, uploaded=False):
        if original and os.path.exists(os.path.join(ORIGINAL_FILES, file_name)):
                os.remove(os.path.join(ORIGINAL_FILES, file_name))
                
        if uploaded and os.path.exists(os.path.join(UPLOAD_FOLDER, file_name)):
                os.remove(os.path.join(UPLOAD_FOLDER, file_name))
    
        if parsed and os.path.exists(os.path.join(PARSED_SHEETS_FOLDER, file_name)):
                os.remove(os.path.join(PARSED_SHEETS_FOLDER, file_name))
    
# TODO: Make more secure: implement time check for example.
def delete_db_entries(database_table_name, file_name):
    file_name = session.get('file_name')
    database_table_name = session.get('database_table_name')
    connection = psycopg2.connect(**DATABASE_CONFIG_2)
    cursor = connection.cursor()
    cursor.execute(f"DELETE FROM {DATABASE_CONFIG['schema_name']}.{database_table_name} where from_spreadsheet = \'{file_name}\';")
    connection.commit()
    cursor.close()
    connection.close()
