from sqlalchemy import create_engine
import pandas as pd

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

def generate_excel_from_postgres_table(host, database, user, password, table_name, output_file):
    # Connect to the PostgreSQL database
    
    # Query to get column names and data types
    query = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}'"
    
    # Read SQL query into a DataFrame
    df = pd.read_sql_query(query, ENGINE)
    
    # Write DataFrame to Excel file
    df.to_excel(output_file, index=False)
    
    # Close the database connection
    conn.close()