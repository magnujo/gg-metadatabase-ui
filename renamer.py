from utils import queries
from constants.misc_constants import PSYCON_CONFIG, PATH_TO_MOUNT
from db_names import db_names, name_maps, get_column_name, get_schema_name, get_table_name
import os
import psycopg2
import getpass

db_config = PSYCON_CONFIG

# user = input("Enter your database username: ")
db_config["user"] = "glj523"
# password = getpass.getpass("Enter your database password: ")
db_config["password"] = "Wtcantfw36c!"


    
connection = psycopg2.connect(**db_config)

import json


# TODO:
def rename_sheet_column(): 
    # rename template
    # rename column_name_sheet in name_maps.column names
    pass


def rename_db_column(schema_name, table_name):
    
    file_path = os.path.join(PATH_TO_MOUNT, "SUN-GI-metadb-test", "renamer", "db_renamer.json")
    
    # If rename file is not empty: ask user if they really want to rename
    
    
    
    # Load renamer file
    with open(file_path, 'r') as file:
        rename_file = json.load(file)
    
    print(rename_file)
    
    full_query = ""
    
    for key in rename_file:
        id = str(key)
        new_name = rename_file[key]
        print(key)
    
        column_names = name_maps.column_names()
        
        #TODO: Make queries safe from sql injection
        
        # Rename column in map
        mapper_update_q = f'''
        UPDATE "{name_maps()}"."{column_names}"
        SET "{column_names.column_name_db}"='{new_name}'
        WHERE "{column_names.column_id}"={id};
        '''
        
        full_query = full_query + mapper_update_q
        
        # Rename column in database
        old_name = get_column_name(id)
        
        table_update_q = f'''
        ALTER TABLE "{schema_name}"."{table_name}" 
        RENAME COLUMN "{old_name}" TO "{new_name}";
        '''
        
        full_query = full_query + table_update_q

    print(full_query)
    
    queries.execute_query(full_query, connection)
    # queries.execute_query(table_update_q, connection)
    
    # update translater:
    # from excel name to db name

rename_db_column("test_1", "initials_translator")



def change_name_in_db(old_name, new_name):
    pass


# Change name in mapper
# change name in database