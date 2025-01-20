import pandas as pd
import os, sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
import constants.misc_constants as misc_constants


def add_db_datatyped_to_excel(input_file, output_file, row, table, schema, database_engine):
    '''
    Inserts a row of the official column datatypes of a table to its 
    corresponding compatible Excel sheet at the specified row.
    '''

    table_name = table
    file_name = input_file
    row = row - 2

    # Query to get column names and data types
    column_query = f'''
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema = '{schema}' AND table_name = '{table_name}' 
    ORDER BY ordinal_position;
    '''

    # Read SQL query into a DataFrame
    df_db = pd.read_sql_query(column_query, database_engine)
    df_excel = pd.read_excel(file_name)
    df_db = df_db.transpose()
    df_db = df_db.reset_index()
    header = df_db.iloc[0]
    df_db.columns = header
    # Drop the first row (since it's now the header)
    df_db = df_db[1:]
    df_db = df_db.reset_index(drop=True)
    df_db = df_db.rename(columns={'column_name': 'Expected column names and positions:'})
    df_db = df_db[df_excel.columns]

    df = pd.concat([df_excel.iloc[:row], df_db, df_excel.iloc[row:]]).reset_index(drop=True)
    df.to_excel(output_file, index=False)
    
