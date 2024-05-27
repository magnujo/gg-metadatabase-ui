import psycopg2
from psycopg2 import sql
import sys
sys.path.append(r'c:\Users\glj523\Documents\github repoes\upload_web_app')
from constants import misc_constants

def enum_exists(cursor, enum_name):
    cursor.execute(
        sql.SQL("SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = %s);"),
        [enum_name]
    )
    return cursor.fetchone()[0]

def create_enum(cursor, enum_name, schema_name, values):
    cursor.execute(
        sql.SQL("CREATE TYPE {}.{} AS ENUM ({});").format(
            sql.Identifier(schema_name),
            sql.Identifier(enum_name),
            sql.SQL(', ').join(map(sql.Literal, values))
        )
    )

def add_enum_values(cursor, enum_name, schema_name, values):
    for value in values:
        cursor.execute(
            sql.SQL("ALTER TYPE {}.{} ADD VALUE IF NOT EXISTS %s;").format(
                sql.Identifier(schema_name),
                sql.Identifier(enum_name)
            ),
            [value]
        )
        
def run(enum_name, values, schema_name):    
    connection = psycopg2.connect(
            dbname=misc_constants.DATABASE_CONFIG["database"],
            user="",
            password="",
            host=misc_constants.DATABASE_CONFIG["host"],
            port=misc_constants.DATABASE_CONFIG["port"]
        )
    connection.autocommit = True
    
    if connection is None:
        return

    cursor = connection.cursor()

    if enum_exists(cursor, enum_name):
        print(f"ENUM type '{enum_name}' exists. Updating...")
        add_enum_values(cursor, enum_name, schema_name, values)
    else:
        print(f"ENUM type '{enum_name}' does not exist. Creating...")
        create_enum(cursor, enum_name, schema_name, values)

    cursor.close()
    connection.close()
    print("Operation completed.")
