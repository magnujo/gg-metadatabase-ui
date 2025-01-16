from constants.db_names.names import deleted_by_script
from constants.db_connections import ENGINE, PSYCON_CONFIG, SQL_ALCH_CONFIG
from utils import queries, send_email
import logging
from utils.CustomExceptions import DontTriggerFileDeletion
from functools import wraps
from flask import redirect, url_for, session
import pandas as pd
import os
from constants.misc_constants import DELETED_SESSION_DATA, ADMIN_EMAIL, PARSED_SHEETS_FOLDER, ORIGINAL_FILES, UPLOADED_FILES
import psycopg2
import shutil
from datetime import datetime
import time
import random


def delete_files(file_name, session_dir, delete_session_dir, original=False, parsed=False, uploaded=False):
        
        if delete_session_dir:
                if os.path.exists(session_dir):  
                        shutil.move(session_dir, os.path.join(DELETED_SESSION_DATA, "failed_sessions"))
                                                    
                else:
                        raise Exception("Session dir could not be found")
        
        if uploaded:
                
                origin_path = os.path.join(UPLOADED_FILES, file_name)
                timestamp = str(datetime.now().strftime("%Y%m%d_%H%M%S"))
                destination_dir = os.path.join(DELETED_SESSION_DATA, "failed_upload_files", timestamp)
                
                if os.path.exists(origin_path):
                        if os.path.exists(destination_dir):
                                shutil.move(origin_path, destination_dir)
                        else:
                                os.mkdir(destination_dir)
                                shutil.move(origin_path, destination_dir)
                else:
                        raise Exception(f"Error deleting uploaded file. {origin_path} not found. Contact admin.")
                        
    
# TODO: Make more secure: implement time check for example.
def delete_db_entries(database_table_name, upload_id, num_of_rows_to_del):
        schema = SQL_ALCH_CONFIG['schema_name']
        deleted_schema = deleted_by_script()
        print(f'\n Moving FROM "{schema}"."{database_table_name}" where upload_uuid = \'{upload_id}\' to {deleted_schema}.{database_table_name} \n')
        in_db = pd.read_sql(queries.upload_id_filter(schema=SQL_ALCH_CONFIG['schema_name'], table=database_table_name, upload_id=upload_id), con=ENGINE)
        if len(in_db) != num_of_rows_to_del:
                raise Exception("Failed deleting data because of shape mismatch between uploaded data and file. Make sure to notify admin so we can fix this")
        else:
                connection = psycopg2.connect(**PSYCON_CONFIG)
                cursor = connection.cursor()
                now = datetime.now()
                deleted_table = f'{now}_{database_table_name}'
                
                q = f'''
                BEGIN;
                
                CREATE TABLE IF NOT EXISTS "{deleted_schema}"."{deleted_table}" AS
                SELECT * 
                FROM "{schema}"."{database_table_name}" 
                WHERE false

                -- Delete data from the source table and return the deleted rows
                WITH deleted_rows AS (
                DELETE FROM "{schema}"."{database_table_name}" f 
                WHERE upload_uuid = \'{upload_id}\'
                RETURNING *
                )
                
                -- Insert the deleted rows into the destination table
                INSERT INTO "{deleted_schema}"."{deleted_table}"  
                SELECT *
                FROM deleted_rows;

                COMMIT;
                '''
                cursor.execute(q)
                connection.commit()
                cursor.close()
                connection.close()
                
                message = f'Data was deleted by script and {deleted_table} was created'
                send_email.send_email(message=message,
                                      receivers=ADMIN_EMAIL,
                                      subject='Script deleted data!')

