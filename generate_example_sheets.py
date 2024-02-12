

from constants import DATABASE_CONFIG, DATABASE_CONFIG_2, ENGINE
import pandas as pd
import psycopg2
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join('static', 'auto_sheets')
path = os.path.relpath(data_dir, current_dir)

data_types = {'integer': None, 
              'text': None, 
              'smallint': None, 
              'int4range': None, 
              'timestamp with time zone': None, 
              'real': None, 
              'date': None, 
              'timestamp without time zone': None, 
              'double precision': None}


def generate_excel(output_folder, get_dtypes=False):
    f'''
    Generates and overwrites example sheets in {path} from table information in postgres
    '''
    
    dtypes = set()
    
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(**DATABASE_CONFIG_2)

    # Get a cursor
    cur = conn.cursor()

    # Query to get all tables in the schema
    query = f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{DATABASE_CONFIG['schema_name']}'"

    # Execute the query
    cur.execute(query)

    # Fetch all table names
    tables = cur.fetchall()

    # Loop through each table and generate Excel file
    for table in tables:
        table_name = table[0]
        output_file = os.path.join(output_folder, f'{table_name}.xlsx')

        # Query to get column names and data types
        column_query = f'''
        SELECT column_name, data_type, ordinal_position 
        FROM information_schema.columns 
        WHERE table_schema = '{DATABASE_CONFIG["schema_name"]}' AND table_name = '{table_name}' 
        ORDER BY ordinal_position;
        '''

        # Read SQL query into a DataFrame
        df = pd.read_sql_query(column_query, ENGINE)
        if get_dtypes:
            dtypes = dtypes.union(set(df['data_type']))
        

        # Write DataFrame to Excel file
        df.to_excel(output_file, index=False)

    # Close the cursor and database connection
    cur.close()
    conn.close()   


dtypes = generate_excel(path, True)
dtypes_ = {key: None for key in dtypes}
print(dtypes)
