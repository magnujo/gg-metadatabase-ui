import pandas as pd

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

# TODO: Only allow one rename file to be not empty
# TODO: Dont allow rename of anything inside name_maps
#TODO: Make queries safe from sql injection
# TODO: If rename file is not empty: ask user if they really want to rename
    # TODO: If rename file is empty: error


def rename_templates():
    file_path = os.path.join(PATH_TO_MOUNT, "SUN-GI-metadb-test", "renamer", "template_renamer.json")
    
    # TODO: If rename file is not empty: ask user if they really want to rename
    # TODO: If rename file is empty: error
    
    # Load renamer file
    with open(file_path, 'r') as file:
        rename_file = json.load(file)
        
    full_query = ""
    
    for key in rename_file:
        id = int(key)
        new_name = rename_file[key]
        
        nm = name_maps()
        table_names = name_maps.table_names()
        schema_names = name_maps.schema_names()
        
        q1 = f'''
        select "{schema_names.schema_name}", {table_names.sheet_template_name}  
        from "{nm}"."{table_names}" tn 
        join "{nm}"."{schema_names}" sn on sn."{schema_names.schema_id}" = tn."{table_names.schema_id}"
        where {table_names.table_id} = '{id}';
        '''
         
        res = queries.execute_query(q1, connection)
        
        if len(res) != 1 or len(res[0]) != 2:
            raise Exception("res not the expected size")
        
        schema_name, template_name = res[0]
            
        #TODO: Make queries safe from sql injection
        
        # Rename table_name in map
        mapper_update_q = f'''
        UPDATE "{name_maps()}"."{table_names}"
        SET "{table_names.sheet_template_name}"='{new_name}'
        WHERE "{table_names.table_id}"='{id}';
        '''
        old_name = os.path.join(PATH_TO_MOUNT, "SUN-GI-metadb-test", "standard_spreadsheet_templates", template_name)
        new_name = os.path.join(PATH_TO_MOUNT, "SUN-GI-metadb-test", "standard_spreadsheet_templates", new_name)
        
        full_query = full_query + mapper_update_q
        
        # Rename template file
        os.rename(old_name, new_name)
        
        full_query = full_query
    
    
    tables_before = {key: get_table_name(int(key), template=True) for key in rename_file}
    queries.execute_query(full_query, connection)
    tables_after = {key: get_table_name(int(key), template=True) for key in rename_file}
    
    errors = []
    for key in rename_file:
        if tables_before[key] == tables_after[key]:
            errors.append(key)
    
    if len(errors) != 0:
        raise Exception(f"The following columns where not renamed correctly: {errors}")

rename_templates()

# TODO: Implement this:
def rename_template_column():
    # TODO: notify people of renaming.
    
    file_path = os.path.join(PATH_TO_MOUNT, "SUN-GI-metadb-test", "renamer", "template_column_renamer.json")
    
    # TODO: If rename file is not empty: ask user if they really want to rename
    # TODO: If rename file is empty: error
    
    
    # Load renamer file
    with open(file_path, 'r') as file:
        rename_file = json.load(file)
        
    full_query = ""
    
    for key in rename_file:
        id = int(key) #  TODO: Int?
        new_name = rename_file[key]
        
        nm = name_maps()
        table_names = name_maps.table_names()
        column_names = name_maps.column_names()
        schema_names = name_maps.schema_names()
        
        q1 = f'''
        select "{schema_names.schema_name}", "{table_names.sheet_template_name}" 
        from "{name_maps()}"."{column_names}" cn 
        join "{nm}"."{table_names}" tn on cn."{column_names.table_id}" = tn."{table_names.table_id}" 
        join "{nm}"."{schema_names}" sn on sn."{schema_names.schema_id}" = tn."{table_names.schema_id}"
        where {column_names.column_id} = '{id}';
        '''
                
        res = queries.execute_query(q1, connection)
        
        if len(res) != 1 or len(res[0]) != 2:
            raise Exception("res not the expected size")
        
        schema_name, template_name = res[0]
        
    
        column_names = name_maps.column_names()
        
        #TODO: Make queries safe from sql injection
        
        # Rename column in map
        mapper_update_q = f'''
        UPDATE "{name_maps()}"."{column_names}"
        SET "{column_names.column_name_sheet}"='{new_name}'
        WHERE "{column_names.column_id}"='{id}';
        '''
        
        full_query = full_query + mapper_update_q
        
        
        # Rename template column
        old_name = get_column_name(id, template=True)
        
        # Load the Excel file
        template_file_path = os.path.join(PATH_TO_MOUNT, "SUN-GI-metadb-test", "standard_spreadsheet_templates", template_name)
        df = pd.read_excel(template_file_path)

        # Rename the column
        df = df.rename(columns={old_name: new_name}, errors='raise')

        # Save the DataFrame back to Excel
        df.to_excel(template_file_path, index=False)


        full_query = full_query

    cols_before = {key: get_column_name(int(key), template=True) for key in rename_file}
    queries.execute_query(full_query, connection)
    cols_after = {key: get_column_name(int(key), template=True) for key in rename_file}
        
    # TODO: Check that names in db are the same as in template?
    
    errors = []
    for key in rename_file:
        if cols_before[key] == cols_after[key]:
            errors.append(key)
    
    if len(errors) != 0:
        raise Exception(f"The following columns where not renamed correctly: {errors}")


def rename_db_schema():
    file_path = os.path.join(PATH_TO_MOUNT, "SUN-GI-metadb-test", "renamer", "db_schema_renamer.json")
    
    # Load renamer file
    with open(file_path, 'r') as file:
        rename_file = json.load(file)
        
    full_query = ""
    
    for key in rename_file:
        id = int(key)
        new_name = rename_file[key]
        
        nm = name_maps()
        schema_names = name_maps.schema_names()
                    
        # Rename table_name in map
        mapper_update_q = f'''
        UPDATE "{name_maps()}"."{schema_names}"
        SET "{schema_names.schema_name}"='{new_name}'
        WHERE "{schema_names.schema_id}"='{id}';
        '''
        
        full_query = full_query + mapper_update_q
        
        schema_name = get_schema_name(id)
        
        table_update_q = f'''
        ALTER SCHEMA "{schema_name}"
        RENAME TO "{new_name}";
        '''
        
        full_query = full_query + table_update_q
    
    print(full_query)
    
    schemas_before = {key: get_schema_name(int(key)) for key in rename_file}
    queries.execute_query(full_query, connection)
    schemas_after = {key: get_table_name(int(key)) for key in rename_file}
    
    errors = []
    for key in rename_file:
        if schemas_before[key] == schemas_after[key]:
            errors.append(key)
    
    if len(errors) != 0:
        raise Exception(f"The following columns where not renamed correctly: {errors}")


def rename_db_tables():
    file_path = os.path.join(PATH_TO_MOUNT, "SUN-GI-metadb-test", "renamer", "db_table_renamer.json")
    
    # TODO: If rename file is not empty: ask user if they really want to rename
    # TODO: If rename file is empty: error
    
    # Load renamer file
    with open(file_path, 'r') as file:
        rename_file = json.load(file)
        
    full_query = ""
    
    for key in rename_file:
        id = int(key)
        new_name = rename_file[key]
        
        nm = name_maps()
        table_names = name_maps.table_names()
        schema_names = name_maps.schema_names()
        
        q1 = f'''
        select "{schema_names.schema_name}", {table_names.table_name}  
        from "{nm}"."{table_names}" tn 
        join "{nm}"."{schema_names}" sn on sn."{schema_names.schema_id}" = tn."{table_names.schema_id}"
        where {table_names.table_id} = '{id}';
        '''
         
        res = queries.execute_query(q1, connection)
        
        if len(res) != 1 or len(res[0]) != 2:
            raise Exception("res not the expected size")
        
        schema_name, table_name = res[0]
            
        #TODO: Make queries safe from sql injection
        
        # Rename table_name in map
        mapper_update_q = f'''
        UPDATE "{name_maps()}"."{table_names}"
        SET "{table_names.table_name}"='{new_name}'
        WHERE "{table_names.table_id}"='{id}';
        '''
        
        full_query = full_query + mapper_update_q
        
        table_update_q = f'''
        ALTER TABLE "{schema_name}"."{table_name}" 
        RENAME TO "{new_name}";
        '''
        
        full_query = full_query + table_update_q
    
    
    tables_before = {key: get_table_name(int(key)) for key in rename_file}
    queries.execute_query(full_query, connection)
    tables_after = {key: get_table_name(int(key)) for key in rename_file}
    
    errors = []
    for key in rename_file:
        if tables_before[key] == tables_after[key]:
            errors.append(key)
    
    if len(errors) != 0:
        raise Exception(f"The following columns where not renamed correctly: {errors}")


def rename_db_column():
    
    file_path = os.path.join(PATH_TO_MOUNT, "SUN-GI-metadb-test", "renamer", "db_column_renamer.json")
    
    # TODO: If rename file is not empty: ask user if they really want to rename
    # TODO: If rename file is empty: error
    
    
    # Load renamer file
    with open(file_path, 'r') as file:
        rename_file = json.load(file)
        
    full_query = ""
    
    for key in rename_file:
        id = int(key) #  TODO: Int?
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
        WHERE "{column_names.column_id}"='{id}';
        '''
        
        full_query = full_query + mapper_update_q
        
        # Rename column in database
        old_name = get_column_name(id)
        
        table_update_q = f'''
        ALTER TABLE "{schema_name}"."{table_name}" 
        RENAME COLUMN "{old_name}" TO "{new_name}";
        '''
        
        full_query = full_query + table_update_q

    cols_before = {key: get_column_name(int(key)) for key in rename_file}
    queries.execute_query(full_query, connection)
    cols_after = {key: get_column_name(int(key)) for key in rename_file}
        
    
    errors = []
    for key in rename_file:
        if cols_before[key] == cols_after[key]:
            errors.append(key)
    
    if len(errors) != 0:
        raise Exception(f"The following columns where not renamed correctly: {errors}")
    
   
    

# rename_db_column()
        
    # update translater:
    # from excel name to db name



# Change name in mapper
# change name in database
