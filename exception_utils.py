from utils import queries
import logging
from utils.CustomExceptions import DontTriggerFileDeletion
from functools import wraps
from flask import redirect, url_for, session
import pandas as pd
import os
from constants import PARSED_SHEETS_FOLDER, ORIGINAL_FILES, UPLOADED_FILES, DATABASE_CONFIG, DATABASE_CONFIG_2, ENGINE
import psycopg2
from scripts import deleted_schema_management

def delete_files(file_name, original=False, parsed=False, uploaded=False):
        if original and os.path.exists(os.path.join(ORIGINAL_FILES, file_name)):
                os.remove(os.path.join(ORIGINAL_FILES, file_name))
                
        if uploaded and os.path.exists(os.path.join(UPLOADED_FILES, file_name)):
                os.remove(os.path.join(UPLOADED_FILES, file_name))
    
        if parsed and os.path.exists(os.path.join(PARSED_SHEETS_FOLDER, file_name)):
                os.remove(os.path.join(PARSED_SHEETS_FOLDER, file_name))
    
# TODO: Make more secure: implement time check for example.
def delete_db_entries(database_table_name, upload_id, num_of_rows_to_del):
        schema = DATABASE_CONFIG['schema_name']
        deleted_schema = deleted_schema_management.get_active_deleted_schema(schema_name=schema, engine=ENGINE)
        print(f'\n Moving FROM "{schema}"."{database_table_name}" where upload_uuid = \'{upload_id}\' to {deleted_schema}.{database_table_name} \n')
        in_db = pd.read_sql(queries.upload_id_filter(schema=DATABASE_CONFIG['schema_name'], table=database_table_name, upload_id=upload_id), con=ENGINE)
        if len(in_db) != num_of_rows_to_del:
                raise Exception("Failed deleting data because of shape mismatch between uploaded data and file. Make sure to notify admin so we can fix this")
        else:
                connection = psycopg2.connect(**DATABASE_CONFIG_2)
                cursor = connection.cursor()
                q = f'''
                BEGIN;

                -- Delete data from the source table and return the deleted rows
                WITH deleted_rows AS (
                DELETE FROM "{schema}"."{database_table_name}" f 
                WHERE upload_uuid = \'{upload_id}\'
                RETURNING *
                )
                -- Insert the deleted rows into the destination table
                INSERT INTO "{deleted_schema}"."{database_table_name}"  
                SELECT *
                FROM deleted_rows;

                COMMIT;
                '''
                cursor.execute(q)
                connection.commit()
                cursor.close()
                connection.close()

