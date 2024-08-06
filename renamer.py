from utils import queries
from constants.misc_constants import RENAME_CONFIG, PATH_TO_MOUNT
from db_names import db_names, name_maps, get_column_name, get_schema_name, get_table_name
import os
    
    
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
    
    column_names = name_maps.column_names()
    
    # # Rename column in map
    # mapper_update_q = f'''
    # UPDATE "{name_maps()}"."{column_names}"
	# SET "{column_names.column_name_db}"='{new_name}'
	# WHERE "{column_names.column_id}"='{id}';
    # '''
    
    # # Rename column in database
    # old_name = get_column_name(id)
    
    # table_update_q = f'''
    # ALTER TABLE "{schema_name}"."{table_name}" RENAME COLUMN "{old_name}" TO "{new_name}";
    # '''
    
    # queries.execute_query(mapper_update_q)
    # queries.execute_query(table_update_q)
    
    # update translater:
    # from excel name to db name

rename_db_column("test", "test" )



def change_name_in_db(old_name, new_name):
    pass


# Change name in mapper
# change name in database