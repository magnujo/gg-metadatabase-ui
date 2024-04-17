'''
The scripts should be used with caution.

Only edit compatible sheets by updating the table in the database and run generate_sheet_from_table.py.
Not the other way around. This is to prevent inconsistency between db tables and compatible sheets.

excel_to_json and update_comments_from_json should only be used for special cases.
'''




import json
import psycopg2
import getpass


'''
Loads a json file were the keys are equal to column names in table_name of schema_name. 
Then updates the comments of schema_name.table_name.column_x with the value of column_x in the json file.
'''

username = input("Enter your database username: ")
password = getpass.getpass("Enter your password: ")

# Specify the table name
table_name = 'field_sample_internal'
schema_name = 'test_1'
file = r'static\example_sheets_online\json_dumps\Field sampling (internal).json'


DATABASE_CONFIG_2 = {
        'host': 'dandyweb01fl',
        'database': 'aedna_metadata_test',
        'port': '5432',
        'user': username,
        'password': password,
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
