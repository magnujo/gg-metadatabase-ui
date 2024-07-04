import os, sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
import psycopg2
import json
import os
from constants.misc_constants import DATABASE_CONFIG_2
from getpass import getpass

# Database connection parameters
db_params = DATABASE_CONFIG_2

schema_name = "test_1"

db_params['user'] = input("Enter super username: ")
db_params['password'] = getpass("Enter super user password: ")

def get_table_names(cursor):
    query = f"""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = '{schema_name}'
    """
    cursor.execute(query)
    return [row[0] for row in cursor.fetchall()]

def get_column_names(cursor, table_name):
    query = f"""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name = '{table_name}' AND table_schema = '{schema_name}'
    """
    cursor.execute(query)
    return [row[0] for row in cursor.fetchall()]

def save_to_json_file(table_name, column_names, output_dir):
    data = {col: col for col in column_names}
    with open(os.path.join(output_dir, f"{table_name}.json"), 'w') as f:
        json.dump(data, f, indent=4)

def main():
    # Directory to save JSON files
    output_dir = os.path.join('name_maps', schema_name)
    
    # os.makedirs(output_dir, exist_ok=True)

    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        # Get all table names
        table_names = get_table_names(cursor)

        # For each table, get the column names and save to a JSON file
        for table_name in table_names:
            column_names = get_column_names(cursor, table_name)
            save_to_json_file(table_name, column_names, output_dir)

        print("Column names have been saved to JSON files successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
        raise

    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    main()
