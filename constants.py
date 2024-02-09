from sqlalchemy import create_engine
import pandas as pd
import psycopg2

ADMIN_EMAILS = "magnus.johannsen@sund.ku.dk or julian.perez@sund.ku.dk"
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt'}

DATABASE_CONFIG = {
    'host': 'dandyweb01fl',
    'database': 'aedna_metadata',
    'port': '5432',
    'user': 'upload_user',
    'password': 'Ce65r-l+!D04',
    'schema_name': 'test'
}

DATABASE_CONFIG_2 = {
    'host': DATABASE_CONFIG['host'],
    'dbname': DATABASE_CONFIG['database'],
    'port': DATABASE_CONFIG['port'],
    'user': DATABASE_CONFIG['user'],
    'password': DATABASE_CONFIG['password'],
}

ENGINE = create_engine(f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}")




SHEET_TYPES = {
    'field_sample_internal': 'Field sampling (internal)',
    'archive_sample': 'eDNA archive sampling',
    'robot_sample': 'eDNA robot sampling',
    'edna_wetlab_report': 'eDNA Wet lab final report',
    'adna_wetlab_report': 'aDNA Wet lab final report',
    'cgg_sediment_water': 'CGG Sediment Water',
    'cgg_animal_plant': 'CGG Animal Plant'
}

ALLOWED_DATE_FORMATS = ['YYYY-MM-DD', 'DD-MM-YYYY', 'DD/MM/YYYY', 'YYYY/MM/DD']
# ALLOWED_DATE_FORMATS = {'YYYY-MM-DD': 'ISO8601', 'DD-MM-YYYY': '%d-%m-%Y', 'DD/MM/YYYY': '%d/%m/%Y', 'YYYY/MM/DD': '%Y/%m/%d'}                         

def generate_excel(output_folder):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host=DATABASE_CONFIG['host'],
        database=DATABASE_CONFIG['database'],
        user=DATABASE_CONFIG['user'],
        password=DATABASE_CONFIG['password']
    )
    
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
        output_file = f"{output_folder}/{table_name}.xlsx"
        
        # Query to get column names and data types
        column_query = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}'"
        
        # Read SQL query into a DataFrame
        df = pd.read_sql_query(column_query, conn)
        
        # Write DataFrame to Excel file
        df.to_excel(output_file, index=False)
    
    # Close the cursor and database connection
    cur.close()
    conn.close()