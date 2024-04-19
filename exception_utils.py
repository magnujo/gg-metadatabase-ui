from utils import queries
import logging
from utils.CustomExceptions import DontTriggerFileDeletion
from functools import wraps
from flask import redirect, url_for, session
import pandas as pd
import os
from constants import PARSED_SHEETS_FOLDER, ORIGINAL_FILES, UPLOAD_FOLDER, DATABASE_CONFIG, DATABASE_CONFIG_2, ENGINE
import psycopg2

def delete_files(file_name, original=False, parsed=False, uploaded=False):
        if original and os.path.exists(os.path.join(ORIGINAL_FILES, file_name)):
                os.remove(os.path.join(ORIGINAL_FILES, file_name))
                
        if uploaded and os.path.exists(os.path.join(UPLOAD_FOLDER, file_name)):
                os.remove(os.path.join(UPLOAD_FOLDER, file_name))
    
        if parsed and os.path.exists(os.path.join(PARSED_SHEETS_FOLDER, file_name)):
                os.remove(os.path.join(PARSED_SHEETS_FOLDER, file_name))
    
# TODO: Make more secure: implement time check for example.
def delete_db_entries(database_table_name, upload_id, num_of_rows_to_del):
        print(f"\n DELETE FROM {DATABASE_CONFIG['schema_name']}.{database_table_name} where upload_uuid = \'{upload_id}\'; \n")
        in_db = pd.read_sql(queries.upload_id_filter(schema=DATABASE_CONFIG['schema_name'], table=database_table_name, upload_id=upload_id), con=ENGINE)
        print("TEST \n")
        print(len(in_db))
        print(num_of_rows_to_del)
        if len(in_db) != num_of_rows_to_del:
                raise Exception("Failed deleting data because of shape mismatch between uploaded data and file. Make sure to notify admin so we can fix this")
        else:
                connection = psycopg2.connect(**DATABASE_CONFIG_2)
                cursor = connection.cursor()
                cursor.execute(f"DELETE FROM {DATABASE_CONFIG['schema_name']}.{database_table_name} where upload_uuid = \'{upload_id}\';")
                connection.commit()
                cursor.close()
                connection.close()

