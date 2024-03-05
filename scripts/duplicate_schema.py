import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
import constants 
import psycopg2

def duplicate_schema(conn, original_schema, new_schema):
    '''
    Duplicates all tables from original_shcmea and pastes them into new_schema
    '''
    
    # Create a new schema
    with conn.cursor() as cursor:
        cursor.execute(f"CREATE SCHEMA {new_schema}")

    # Get all tables in the original schema
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = %s;
        """, (original_schema,))
        tables = cursor.fetchall()

    # Iterate through each table and copy its structure and data
    for table in tables:
        table_name = table[0]
        # Copy table structure
        with conn.cursor() as cursor:
            cursor.execute(f"""
                CREATE TABLE {new_schema}.{table_name} AS 
                SELECT * FROM {original_schema}.{table_name} WHERE 1=0;
            """)

        # Copy table data
        with conn.cursor() as cursor:
            cursor.execute(f"""
                INSERT INTO {new_schema}.{table_name}
                SELECT * FROM {original_schema}.{table_name};
            """)

    conn.commit()

DATABASE_CONFIG = {
    'host':'dandyweb01fl',
    'dbname': 'aedna_metadata',
    'port': 5432,
    'user': '',
    'password': '',
}

# Connect to your PostgreSQL database
conn = psycopg2.connect(**DATABASE_CONFIG)

# Duplicate schema "original_schema" as "new_schema"
duplicate_schema(conn, "test", "example_sheets_generator")

# Close the connection
conn.close()
