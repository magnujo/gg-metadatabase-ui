import psycopg2

# Replace these values with your database connection details
DATABASE = "aedna_metadata_test"
USER = "glj523"
PASSWORD = "!"
HOST = "dandyweb01fl"
PORT = ""

# Replace these values with the schema names you want to create and copy tables to
NEW_SCHEMA = "test_1"
SOURCE_SCHEMA = "test"

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
            cursor.execute(f"CREATE TABLE {destination_schema}.{table_name} (LIKE {source_schema}.{table_name} INCLUDING ALL);")
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

except Exception as e:
    print(f"Error: {e}")

finally:
    if conn is not None:
        conn.close()



