import os, sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

import pandas as pd
import psycopg2
import constants.misc_constants as misc_constants
from sqlalchemy import create_engine
import getpass

excel_file = r'static\example_sheets_offline\SS0077_Sediment Soil Done Summary Table_240216.xls'
database = 'aedna_metadata_test'
schema = 'test_1'
table_name = 'edna_wetlab_report'

def add_cols_to_db(excel_file, database, table_name, schema):
    '''
    Updates the columns of a database to match the columns of a excel sheet.
    '''
    
    user = input("Enter your database username: ")
    password = getpass.getpass("Enter your password: ")
    
    DATABASE_CONFIG = {
        'host': 'dandypdb01fl',
        'database': database,
        'port': '5432',
        'user': user,
        'password': password,
    }
   
    # Read the Excel spreadsheet to get column names
    df_excel = pd.read_excel(excel_file)
    df_excel = df_excel.drop(df_excel.columns[0], axis=1)
    excel_columns = list(df_excel.columns)    
    database = DATABASE_CONFIG['database']
   
    # Connect to PostgreSQL database
    ENGINE = create_engine(f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}")
    
    # Get existing column names from the PostgreSQL table
    connection = psycopg2.connect(**DATABASE_CONFIG)
    cursor = connection.cursor()
    existing_columns = pd.read_sql(sql=f"SELECT * from {database}.{schema}.{table_name}",
                                   con=ENGINE).columns
    missing_columns = [col for col in excel_columns if col not in existing_columns]
    # Add missing columns to the PostgreSQL table
    for col in missing_columns:
        cursor.execute(
            f"ALTER TABLE {database}.{schema}.{table_name} ADD COLUMN \"{col}\" text;")  # Change 'datatype' to match your data type
    connection.commit()
    print(f'added {missing_columns} to {database}.{schema}.{table_name}')
    cursor.close()
    connection.close()
    # Optionally, you may need to update data types or other properties of existing columns to match the Excel spreadsheet
    # Now, you can proceed with updating the data in the table as needed



add_cols_to_db(excel_file=excel_file, database=database, table_name=table_name, schema=schema)