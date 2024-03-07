import pandas as pd
import ast
import numpy as np
import sys, os
import pandas as pd
import psycopg2
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))  # Add parent directory to sys.path
import constants
import psycopg2
import pandas as pd
import getpass

'''
Automatically generates a compatible excel sheet template for a given table.
'''

output_file=r'static\auto_sheets\adna_wetlab_report.xlsx' 
table_name='adna_wetlab_report' 
schema_name='test_1'
user = input("Enter your database username: ")
password = getpass.getpass("Enter your password: ")
database_name='aedna_metadata_test'

current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join('static', 'auto_sheets')
path = os.path.relpath(data_dir, current_dir)

special_formats = {}

def si(value):
    if value is not None:
        return ast.literal_eval(value)
    else:
        return None


def generate_excel_from_table(output_file, table_name, database_name, schema_name, user, password):
    '''
    Generates spreaddsheet with a tables column names and corresponding data types and comments.
    '''
    # Connect to your PostgreSQL database
    
    database_config = {
    'host': 'dandyweb01fl',
    'dbname': database_name,
    'port': 5432,
    'user': user,
    'password': password,
}
    
    conn = psycopg2.connect(**database_config)    

    # SQL query to retrieve column comments and data types
    query = f"""
select
    c.column_name,
    c.data_type,
    c.is_nullable,
    pgd.description
from pg_catalog.pg_statio_all_tables as st
inner join pg_catalog.pg_description pgd on (
    pgd.objoid = st.relid
)
full outer join information_schema.columns c on (
    pgd.objsubid   = c.ordinal_position and
    c.table_schema = st.schemaname and
    c.table_name   = st.relname
) where c.table_catalog = '{database_name}' and c.table_schema = '{schema_name}' and c.table_name = '{table_name}';
    """
    
    # Execute the query and fetch the results
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()

    # Create a DataFrame from the fetched data
    df = pd.DataFrame(rows, columns=['Column Name', 'Data Type', 'Is Nullable', 'Description'])
    # auto_generated_cols_in_df = [col for col in constants.auto_generated_columns if col in df.columns]
    df = df[~df['Column Name'].isin(constants.auto_generated_columns)]


    # Export the DataFrame to an Excel file
    

    # Close the cursor and connection
    cursor.close()
    conn.close()

    df['Description'] = df['Description'].str.replace("nan", 'None')

    df['Description'] = df['Description'].apply(si)

    expanded_df = pd.json_normalize(df['Description'])
    result_df = pd.concat([df, expanded_df], axis=1)
    result_df = result_df.fillna(np.nan)
    result_df = result_df.dropna(axis='rows', how='all')
    result_df = result_df.drop(columns=['Description'])
    result_df.to_excel(output_file, index=False)

generate_excel_from_table(output_file=output_file, 
                          table_name=table_name, 
                          schema_name=schema_name,
                          user=user,
                          password=password,
                          database_name=database_name)

def generate_excels_from_schema(output_folder, schema, database_config):
    '''
    Generates multiple excel sheets from all tables in a schema using generate_excel_from_table function.
    '''
    
    
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(**database_config)
    
    # Get a cursor
    cur = conn.cursor()

    # Query to get all tables in the schema
    query = f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema}'"

    # Execute the query
    cur.execute(query)

    # Fetch all table names
    tables = cur.fetchall()

    # Loop through each table and generate Excel file
    for table in tables:
        
        table_name = table[0]
        output_file = os.path.join(output_folder, f'{table_name}.xlsx')
        generate_excel_from_table(output_file=output_file, database_config=database_config, table_name=table_name, schema_name=schema)

    # Close the cursor and database connection
    cur.close()
    conn.close()   
    
