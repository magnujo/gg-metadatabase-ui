import pandas as pd
import psycopg2
from utils import queries
import constants

def duplicate_schema(conn, source_schema, target_schema):
    cursor = conn.cursor()

    # Check if schema C and schema B are equivalent
    cursor.execute("SELECT * FROM information_schema.tables WHERE table_schema = %s", (source_schema,))
    source_tables = cursor.fetchall()
    cursor.execute("SELECT * FROM information_schema.tables WHERE table_schema = %s", (target_schema,))
    target_tables = cursor.fetchall()

    if source_tables == target_tables:
        # Duplicate schema B from schema A
        cursor.execute("CREATE SCHEMA IF NOT EXISTS {}".format(target_schema))

        for table in source_tables:
            table_name = table[2]
            cursor.execute("CREATE TABLE {}.{} AS SELECT * FROM {}.{}".format(target_schema, table_name, source_schema, table_name))

        conn.commit()
        print("Schema {} duplicated from {} to {}.".format(target_schema, source_schema, target_schema))
    else:
        print("Schema {} and {} are not equivalent. Not duplicating schema or inserting data.".format(source_schema, target_schema))
    
    conn.close()


import psycopg2

def copy_data(source_table, destination_table):
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname="your_database_name",
            user="your_username",
            password="your_password",
            host="your_host",
            port="your_port"
        )
        
        # Create a cursor object
        cur = conn.cursor()
        
        active_schema = constants.DATABASE_CONFIG["schema_name"]
        
        # Get column information for source and destination tables
        source_columns = queries.get_column_names(source_table, constants.DATABASE_CONFIG["schema_name"])
        schema_names = get_schema_names(constants.ENGINE)
        destination_schema = f"{active_schema}_deleted"
        destination_columns = queries.get_column_names(destination_table, constants.DATABASE_CONFIG["schema_name"])
        
        
        #Find the most recent schema:
        
        
        
        # Check if the tables have the same number of columns and column names
        if len(source_columns) != len(destination_columns) or set(source_columns) != set(destination_columns):
            print("Error: Source and destination tables do not have the same structure.")
            return
        
        # Execute the SQL query to copy data from source to destination
        sql_query = f"INSERT INTO {destination_table} SELECT * FROM {source_table}"
        cur.execute(sql_query)
        
        # Commit the transaction
        conn.commit()
        print("Data copied successfully!")
        
    except psycopg2.Error as e:
        print("Error:", e)
        
    finally:
        # Close the cursor and connection
        if cur:
            cur.close()
        if conn:
            conn.close()
            
def grant_schema_usage(schema_name, user, conn):
    # Create a cursor object
    cur = conn.cursor()

    # Execute the SQL command to grant USAGE permission on the schema
    grant_sql = f"GRANT USAGE ON SCHEMA {schema_name} TO {user};"
    cur.execute(grant_sql)

    # Commit the transaction
    conn.commit()

    # Close the cursor and the connection
    cur.close()
    conn.close()


def get_latest_deleted_schema():
    q = '''
    SELECT schema_name
    FROM information_schema.schemata;
    '''
    df = pd.read_sql(q, con=constants.ENGINE)
    schema_name = "test_1"
    df = df[df["schema_name"].str.startswith(f"{schema_name}_deleted")]

    df.loc[:, "date"] = df["schema_name"].apply(lambda x: x.split("_")[-1])
    
    # Test:
    for index, row in df.iterrows():
            if row["schema_name"].split("_")[-1] != row["date"]:
                raise Exception("Error happened parsing")
    
    df.loc[:, 'date'] = pd.to_datetime(df['date'], format='%Y%m%d')
    result = df.loc[df['date'].idxmax()]["schema_name"]
    
    return result