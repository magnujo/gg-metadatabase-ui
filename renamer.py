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


def rename_db_column():
    
    file_path = os.path.join(PATH_TO_MOUNT, "SUN-GI-metadb-test", "renamer", "db_renamer.json")
    
    # If rename file is not empty: ask user if they really want to rename
    
    
    # Load renamer file
    with open(file_path, 'r') as file:
        rename_file = json.load(file)
        
    full_query = ""
    
    for key in rename_file:
        id = str(key)
        new_name = rename_file[key]
        
        nm = name_maps()
        table_names = name_maps.table_names()
        column_names = name_maps.column_names()
        schema_names = name_maps.schema_names()
        
        q1 = f'''
        select "{schema_names.schema_name}", "{table_names.table_name}" 
        from "{name_maps()}"."{column_names}" cn 
        join "{nm}"."{table_names}" tn on cn."{column_names.table_id}" = tn."{table_names.table_id}" 
        join "{nm}"."{schema_names}" sn on sn."{schema_names.schema_id}" = tn."{table_names.schema_id}"
        where {column_names.column_id} = '{id}';
        '''
                
        res = queries.execute_query(q1, connection)
        
        if len(res) != 1 or len(res[0]) != 2:
            raise Exception("res not the expected size")
        
        schema_name, table_name = res[0]
        
    
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

    
    queries.execute_query(full_query, connection)
    
    # update translater:
    # from excel name to db name



# Change name in mapper
# change name in database
