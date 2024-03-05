from sqlalchemy import create_engine
import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
import constants
from constants import DATABASE_CONFIG, DATABASE_CONFIG_2
import pandas as pd
import psycopg2
import os, sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
import constants
import psycopg2
import pandas as pd

current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join('static', 'auto_sheets')
path = os.path.relpath(data_dir, current_dir)

special_formats = {}

data_types = {'integer': None, 
              'text': None, 
              'smallint': None, 
              'int4range': None, 
              'timestamp with time zone': None, 
              'real': None, 
              'date': None, 
              'timestamp without time zone': None, 
              'double precision': None}


def generate_excel_from_table(output_file, database_config, table_name, schema_name):
    # Connect to your PostgreSQL database
    conn = psycopg2.connect(**database_config)    

    # SQL query to retrieve column comments and data types
    query = f"""
    SELECT 
        column_name,
        udt_name as data_type,
        col_description(pg_attribute.attrelid, pg_attribute.attnum) as column_comment
    FROM 
        information_schema.columns
    JOIN 
        pg_attribute ON pg_attribute.attname = information_schema.columns.column_name
    JOIN 
        pg_class ON pg_class.oid = pg_attribute.attrelid
    LEFT JOIN 
        pg_namespace ON pg_namespace.oid = pg_class.relnamespace
    WHERE 
        table_name = '{table_name}'
        AND pg_namespace.nspname = '{schema_name}'
        and table_catalog = '{database_config['dbname']}'
        and relname = '{table_name}';
    """

    # Execute the query and fetch the results
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()

    # Create a DataFrame from the fetched data
    df = pd.DataFrame(rows, columns=['Column Name', 'Data Type', 'Description'])
    # auto_generated_cols_in_df = [col for col in constants.auto_generated_columns if col in df.columns]
    df = df[~df['Column Name'].isin(constants.auto_generated_columns)]


    # Export the DataFrame to an Excel file
    df.to_excel(output_file, index=False)

    # Close the cursor and connection
    cursor.close()
    conn.close()

def generate_excels_from_schema(output_folder, schema, database_config):
    
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(**database_config)
    
    engine = create_engine(f"postgresql://{database_config['user']}:{database_config['password']}@{database_config['host']}:{database_config['port']}/{database_config['database']}")

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
    
generate_excel_from_table(output_file="test.xlsx", database_config=constants.DATABASE_CONFIG_2, table_name='field_sample_internal', schema_name='test')