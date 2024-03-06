import json
import psycopg2
import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
import constants 

'''
Loads a json file were the keys are equal to column names in table_name of schema_name. 
Then updates the comments of schema_name.table_name.column_x with the value of column_x in the json file.
'''

# Specify the table name
table_name = 'edna_archive_sample'
schema_name = 'test_1'
file = r'static\example_sheets_online\json_dumps\eDNA archive sampling.json'

DATABASE_CONFIG_2 = {
        'host': 'dandyweb01fl',
        'database': 'aedna_metadata_test',
        'port': '5432',
        'user': 'glj523',
        'password': 'Wtcantfw36c!',
    }


def insert_column_comments(conn, table_name, schema_name, column_comments):
    with conn.cursor() as cursor:
        for column, comment in column_comments.items():
            # Convert the comment to string if it's not already
            if not isinstance(comment, str):
                comment = str(comment)
            cursor.execute(
                "COMMENT ON COLUMN \"{}\".\"{}\".\"{}\" IS %s".format(schema_name, table_name, column), (comment,))
    conn.commit()

# Connect to your PostgreSQL database
conn = psycopg2.connect(**DATABASE_CONFIG_2)


# Load the JSON file
with open(file, 'r') as f:
    column_comments = json.load(f)

# Insert column comments into the PostgreSQL table
insert_column_comments(conn, table_name, schema_name, column_comments)

# Close the connection
conn.close()
