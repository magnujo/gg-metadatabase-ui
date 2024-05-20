import getpass
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import pandas as pd
from utils import queries
import constants
from scripts import duplicate_schema


def copy_or_generate(active_schema, database_name, alch_engine, psy_conn):
    
    """
    Tries to copy data from the active schema to the active deleted schema. If they are equal not, 
    a new deleted schema that replicates the active schema is made with the current datetime appended.

    Parameters:
    - source_schema (str): The name of the active schema used for uploads and queries.
    - database_name (str): The name of the database where the schemas reside.
    - engine (sqlalchemy.engine.Engine): SQLAlchemy engine to connect to the database.

    Returns:
    None

    Note:
    This function compares table structures and data between the active schema and 
    the latest deleted schema. If they have identical structures, data is copied from 
    the active schema to the latest deleted schema. If not, a duplicate of the active 
    schema is generated with the current date appended to its name.
    """
    
    active_deleted_schema_name = get_active_deleted_schema(schema_name=active_schema, engine=alch_engine)
    
    
    table_names_source = queries.get_table_names(schema_name=active_schema, database_name=database_name)
    table_names_destination = queries.get_table_names(schema_name=active_deleted_schema_name, database_name=database_name)
    
    equal = False
    
    # check if the two schemas already match ie. they contain the same table names and their tables have the same column names.
    if sorted(table_names_source) == sorted(table_names_destination):
        equal = True
        for table in table_names_source:
            cols_source = queries.get_column_names(table, active_schema)
            cols_destination = queries.get_column_names(table, active_deleted_schema_name)
            if sorted(cols_source) != sorted(cols_destination):
                equal = False
    
    if equal:
        # If the active deleted schema is equal to the active schema then we keep it
        print("Old deleted schema is equal to active schema, so old deleted schema is used...")
        pass       
        
    else:
        # Make a duplicate schema of the active schema with todays date appended
        now = datetime.now().strftime('%Y%m%d%H:%M')
        new_schema_name = f"{active_schema}_deleted_{now}"
        print(f"Making new deleted schema {new_schema_name} because either tables or columns from active deleted schema are different from active schema")
    
        duplicate_schema.run(conn=psy_conn, 
                            source_schema=active_schema, 
                            new_schema=new_schema_name, 
                            owner="upload_user", 
                            include_constraints=False, 
                            copy_datatypes=False,
                            privileges=["SELECT", "INSERT"])
    

def get_active_deleted_schema(schema_name, engine):
    q = '''
    SELECT schema_name
    FROM information_schema.schemata;
    '''
    df = pd.read_sql(q, con=engine)
    df = df[df["schema_name"].str.startswith(f"{schema_name}_deleted")]

    df.loc[:, "date"] = df["schema_name"].apply(lambda x: x.split("_")[-1])
    
    # Test:
    for index, row in df.iterrows():
            if row["schema_name"].split("_")[-1] != row["date"]:
                raise Exception("Error happened parsing")

    df.loc[:, 'date'] = pd.to_datetime(df['date'], format='%Y%m%d%H:%M')
    result = df.loc[df['date'].idxmax()]["schema_name"]
    
    return result