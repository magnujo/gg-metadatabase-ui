'''
Run by calling run() in the bottom
'''

import constants.db_connections
import constants.misc_constants as misc_constants
import psycopg2
import getpass
from utils import queries


# Function to create a new schema
def create_schema(conn, schema_name):
    try:
        cursor = conn.cursor()
        cursor.execute(f'CREATE SCHEMA "{schema_name}"')
        conn.commit()
        print(f"Schema '{schema_name}' created successfully.")
    except Exception as e:
        print(f"Error creating schema: {e}")
        conn.rollback()
    finally:
        cursor.close()

# Function to copy tables from one schema to another
def copy_tables(conn, super_psy_conn, source_schema, destination_schema, include_constraints, copy_dtypes, engine):
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{source_schema}'")
        tables = cursor.fetchall()
        cursor.close()
        conn.commit()
        
        super_cursor = super_psy_conn.cursor()
        for table in tables:
            table_name = table[0]
            if include_constraints:
                super_cursor.execute(f'CREATE TABLE "{destination_schema}".\"{table_name}\" (LIKE {source_schema}.\"{table_name}\" INCLUDING ALL);')
            else:
                super_cursor.execute(f'CREATE TABLE "{destination_schema}".\"{table_name}\" (LIKE "{source_schema}".\"{table_name}\");')
            if copy_dtypes == False:
                column_names = queries.get_column_names(table_name=table_name, schema_name=source_schema, engine=engine)
                for column_name in column_names:
                    super_cursor.execute(f'ALTER TABLE "{destination_schema}"."{table_name}" ALTER COLUMN "{column_name}" TYPE text')
        
        
        super_cursor.close() 
        super_psy_conn.commit()
        
        print(f"Tables copied from schema '{source_schema}' to schema '{destination_schema}' successfully.")
    except Exception as e:
        print(f"Error copying tables: {e}")
        conn.rollback()
        super_psy_conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if super_cursor:
            super_cursor.close()


def run(conn, source_schema, new_schema, owner, include_constraints, copy_datatypes, privileges, engine):
    """
    Create a new schema, copy all tables from a source schema to the new schema,
    and grant privileges to the specified owner.

    Parameters:
    conn (psycopg2.Connection): A connection object to the database.
    source_schema (str): The name of the source schema to copy tables from.
    new_schema (str): The name of the new schema to create and copy tables to.
    owner (str): The owner to grant privileges to.
    include_constraints (bool): If True, include constraints while copying tables.
    copy_datatypes (bool): If True, copy data types of columns, otherwise all columns will be text.
    priviliges (list): specify which priviliges owner should have (SELECT, INSERT and/or DELETE).

    Returns:
    None

    Raises:
    Any exception encountered during the process.
    """
    print("Duplicating schema...")
    try:
        super_user = input("Enter your database super username: ")
        super_password = getpass.getpass("Enter your super password: ")
        super_psy_conn = psycopg2.connect(
            dbname=constants.db_connections.SQL_ALCH_CONFIG["database"],
            user=str(super_user),
            password=str(super_password),
            host=constants.db_connections.SQL_ALCH_CONFIG["host"],
            port=constants.db_connections.SQL_ALCH_CONFIG["port"]
        )
       
        # Create a new schema
        create_schema(super_psy_conn, new_schema)

        # Copy tables from source schema to the new schema
        copy_tables(conn, super_psy_conn, source_schema, new_schema, include_constraints=include_constraints, copy_dtypes=copy_datatypes, engine=engine)
        
        if len(privileges) > 3:
            raise Exception(f"Expected priviliges list to be max length of 3 but got {len(privileges)}")
        
        
        if not all(item in misc_constants.ALLOWED_PRIVILIGES for item in privileges):
            raise Exception(f"Expected found not allowed value in priviliges list. Only {misc_constants.ALLOWED_PRIVILIGES} allowed but got {privileges}")
        
        # TODO: Remove upload_user and all its privileges
        # Query to give privileges to upload_user 
        priv_q_2 = f'GRANT USAGE ON SCHEMA "{new_schema}" TO "{owner}";'
        priv_q = f'GRANT {", ".join(privileges)} ON ALL TABLES IN SCHEMA "{new_schema}" TO "{owner}";'
        
        try:
            cursor = super_psy_conn.cursor()
            cursor.execute(priv_q_2)
            cursor.execute(priv_q)
            super_psy_conn.commit()
            print(f"Privileges given to upload_user succesfully")
        except Exception as e:
            print(f"Error copying tables: {e}")
            super_psy_conn.rollback()
        finally:
            cursor.close()
        
    except Exception as e:
        print(f"Error: {e}")

    finally:
        if conn is not None:
            conn.close()
        if super_psy_conn is not None:
            super_psy_conn.close()
            
# Replace these values with your database connection details
# DATABASE = "aedna_metadata_test"
# USER = input("Enter your database username: ")
# PASSWORD = getpass.getpass("Enter your password: ")
# HOST = "dandyweb01fl"
# PORT = "5432"
# INCLUDE_CONSTRAINTS = True

# # Replace these values with the schema names you want to create and copy tables to
# NEW_SCHEMA = "data_deleted"
# SOURCE_SCHEMA = "data"

# conn = psycopg2.connect(
#             dbname=DATABASE,
#             user=USER,
#             password=PASSWORD,
#             host=HOST,
#             port=PORT
#         )


# run(conn=conn, source_schema=SOURCE_SCHEMA, new_schema=NEW_SCHEMA, owner=, include_constraints=INCLUDE_CONSTRAINTS, copy_datatypes=)