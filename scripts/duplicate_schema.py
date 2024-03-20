import psycopg2
import getpass

# Replace these values with your database connection details
DATABASE = "aedna_metadata_test"
USER = input("Enter your database username: ")
PASSWORD = getpass.getpass("Enter your password: ")
HOST = "dandyweb01fl"
PORT = "5432"

# Replace these values with the schema names you want to create and copy tables to
NEW_SCHEMA = "test_2"
SOURCE_SCHEMA = "test_1"

#TODO: Remove upload_user and all its privileges
# Query to give privileges to upload_user 
priv_q = f"GRANT SELECT, INSERT, DELETE ON ALL TABLES IN SCHEMA {NEW_SCHEMA} TO upload_user;"

# Function to create a new schema
def create_schema(conn, schema_name):
    try:
        cursor = conn.cursor()
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
        conn.commit()
        print(f"Schema '{schema_name}' created successfully.")
    except Exception as e:
        print(f"Error creating schema: {e}")
        conn.rollback()
    finally:
        cursor.close()

# Function to copy tables from one schema to another
def copy_tables(conn, source_schema, destination_schema):
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{source_schema}'")
        tables = cursor.fetchall()
        for table in tables:
            table_name = table[0]
            cursor.execute(f'CREATE TABLE {destination_schema}.\"{table_name}\" (LIKE {source_schema}.\"{table_name}\" INCLUDING ALL);')
        conn.commit()
        print(f"Tables copied from schema '{source_schema}' to schema '{destination_schema}' successfully.")
    except Exception as e:
        print(f"Error copying tables: {e}")
        conn.rollback()
    finally:
        cursor.close()

try:
    # Connect to the database
    conn = psycopg2.connect(
        dbname=DATABASE,
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT
    )

    # Create a new schema
    create_schema(conn, NEW_SCHEMA)

    # Copy tables from source schema to the new schema
    copy_tables(conn, SOURCE_SCHEMA, NEW_SCHEMA)
    
    try:
        cursor = conn.cursor()
        cursor.execute(priv_q)
        conn.commit()
        print(f"Privileges given to upload_user succesfully")
    except Exception as e:
        print(f"Error copying tables: {e}")
        conn.rollback()
    finally:
        cursor.close()
    
except Exception as e:
    print(f"Error: {e}")

finally:
    if conn is not None:
        conn.close()



