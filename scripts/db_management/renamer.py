'''
This script is used for renaming db columns, tables and schemas as well as upload sheet templates and their columns. 

How to:
To use it go to N:\SUN-GI-metadb-test\renamer and edit the relevant json. For example if you want to rename a 
table(s) open n:\SUN-GI-metadb-test\renamer\db_table_renamer.json and insert the 
table id(s) of the table(s) you want to rename and the new name you want to give them as follows:

{
    "<table_id_1>": "<new_name_1>",
    "<table_id_2>": "<new_name_2>",
    .
    .
    .
    "<table_id_N>": "<new_name_N>"
}

Example:
{
    "15": "geological_sampling"
}

This will rename the table with the ID of 15 in name_maps.table_names to "geological_sampling" and it will update
table_name in name_maps.table_names where ID = 15 to "geological_sampling". 

NOTE: Table IDs can be found in the database under name_maps.

To run this file do the following:
    1. Activate a conda environment with the environment.yml file
    2. Set environment variable DB_PASSWORD = your_db_password.
    3. python renamer.py
'''

# TODO: Make queries safe from sql injection
import os, sys

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(parent_dir)

import pandas as pd
import json
from utils import queries
from constants.misc_constants import PATH_TO_MOUNT
from constants.db_names.name_maps import name_maps, get_column_name, get_schema_name, get_table_name
import psycopg2
import getpass
from threading import Lock

lock = Lock()

    

def rename_templates(connection):
    
    file_path = os.path.join(PATH_TO_MOUNT, "SUN-GI-metadb-test", "renamer", "template_renamer.json")
    
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
        select sn."{schema_names.schema_name}", tn.{table_names.sheet_template_name}  
        from "{nm}"."{table_names}" tn 
        join "{nm}"."{schema_names}" sn on sn."{schema_names.schema_id}" = tn."{table_names.schema_id}"
        where {table_names.table_id} = '{id}';
        '''
         
        res = queries.execute_query(q1, connection)
        
        if len(res) != 1 or len(res[0]) != 2:
            raise Exception("res not the expected size")
        
        schema_name, template_name = res[0]
            
        if str(schema_name) == str(name_maps()):
            raise Exception(f"Altering table {schema_name} is not allowed.")
        
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
    
    user_output = {get_table_name(int(key), template=True): val for key, val in rename_file.items()}
    print(f"Do you want to complete the following template renaming? (y/n)")
    print(f"{user_output}")
    confirmation = input("")
    
    if confirmation == 'y':
    
        tables_before = {key: get_table_name(int(key), template=True) for key in rename_file}
        queries.execute_query(full_query, connection)
        tables_after = {key: get_table_name(int(key), template=True) for key in rename_file}
        
        errors = []
        for key in rename_file:
            if tables_before[key] == tables_after[key]:
                errors.append(key)
        
        if len(errors) != 0:
            raise Exception(f"The following columns where not renamed correctly: {errors}")


def rename_template_column(connection):
    # TODO: notify people of renaming.
    
    file_path = os.path.join(PATH_TO_MOUNT, "SUN-GI-metadb-test", "renamer", "template_column_renamer.json")
 
    
    
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
        select sn."{schema_names.schema_name}", tn."{table_names.sheet_template_name}" 
        from "{name_maps()}"."{column_names}" cn 
        join "{nm}"."{table_names}" tn on cn."{column_names.table_id}" = tn."{table_names.table_id}" 
        join "{nm}"."{schema_names}" sn on sn."{schema_names.schema_id}" = tn."{table_names.schema_id}"
        where {column_names.column_id} = '{id}';
        '''
                
        res = queries.execute_query(q1, connection)
        
        if len(res) != 1 or len(res[0]) != 2:
            raise Exception("res not the expected size")
        
        schema_name, template_name = res[0]
        
        if str(schema_name) == str(name_maps()):
            raise Exception(f"Altering table {schema_name} is not allowed.")
        
    
        column_names = name_maps.column_names()
        
        
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

    user_output = {get_column_name(int(key), template=True): val for key, val in rename_file.items()}
    print(f"Do you want to complete the following renaming in template: {template_name}? (y/n)")
    print(f"{user_output}")
    confirmation = input("")
    
    if confirmation == 'y':
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


def rename_db_schema(connection):
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
        
        if str(schema_name) == str(name_maps()):
            raise Exception(f"Altering table {schema_name} is not allowed.")
        
        table_update_q = f'''
        ALTER SCHEMA "{schema_name}"
        RENAME TO "{new_name}";
        '''
        
        full_query = full_query + table_update_q
    
    
    user_output = {get_table_name(int(key)): val for key, val in rename_file.items()}
    print(f"Do you want to complete the schema renaming? (y/n)")
    print(f"{user_output}")
    confirmation = input("")
    
    if confirmation == 'y':
        schemas_before = {key: get_schema_name(int(key)) for key in rename_file}
        queries.execute_query(full_query, connection)
        schemas_after = {key: get_table_name(int(key)) for key in rename_file}
        
        errors = []
        for key in rename_file:
            if schemas_before[key] == schemas_after[key]:
                errors.append(key)
        
        if len(errors) != 0:
            raise Exception(f"The following columns where not renamed correctly: {errors}")        


def rename_db_tables(connection):
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
        select sn."{schema_names.schema_name}", tn.{table_names.table_name}  
        from "{nm}"."{table_names}" tn 
        join "{nm}"."{schema_names}" sn on sn."{schema_names.schema_id}" = tn."{table_names.schema_id}"
        where {table_names.table_id} = '{id}';
        '''
         
        res = queries.execute_query(q1, connection)
        
        if len(res) != 1 or len(res[0]) != 2:
            raise Exception("res not the expected size")
        
        schema_name, table_name = res[0]
        
        if str(schema_name) == str(name_maps()):
            raise Exception(f"Altering table {schema_name} is not allowed.")
                    
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
    
    user_output = {get_table_name(int(key)): val for key, val in rename_file.items()}
    print(f"Do you want to complete the following renaming? (y/n)")
    print(f"{user_output}")
    confirmation = input("")
    
    if confirmation == 'y':
    
        tables_before = {key: get_table_name(int(key)) for key in rename_file}
        queries.execute_query(full_query, connection)
        tables_after = {key: get_table_name(int(key)) for key in rename_file}
        
        errors = []
        for key in rename_file:
            if tables_before[key] == tables_after[key]:
                errors.append(key)
        
        if len(errors) != 0:
            raise Exception(f"The following columns where not renamed correctly: {errors}")


def rename_db_column(connection):
    
    file_path = os.path.join(PATH_TO_MOUNT, "SUN-GI-metadb-test", "renamer", "db_column_renamer.json")
    
    # Load renamer file
    with open(file_path, 'r') as file:
        rename_file = json.load(file)
        
    full_query = ""
    
    for key in rename_file:
        id = int(key) 
        new_name = rename_file[key]
        
        nm = name_maps()
        table_names = name_maps.table_names()
        column_names = name_maps.column_names()
        schema_names = name_maps.schema_names()
        
        q1 = f'''
        select sn."{schema_names.schema_name}", tn."{table_names.table_name}" 
        from "{name_maps()}"."{column_names}" cn 
        join "{nm}"."{table_names}" tn on cn."{column_names.table_id}" = tn."{table_names.table_id}" 
        join "{nm}"."{schema_names}" sn on sn."{schema_names.schema_id}" = tn."{table_names.schema_id}"
        where {column_names.column_id} = '{id}';
        '''
                
        res = queries.execute_query(q1, connection)
        
        if len(res) != 1 or len(res[0]) != 2:
            raise Exception("res not the expected size")
        
        schema_name, table_name = res[0]
        
        if str(schema_name) == str(name_maps()):
            raise Exception(f"Altering table {schema_name} is not allowed.")
        
    
        column_names = name_maps.column_names()
                
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
        
    user_output = {get_column_name(int(key)): val for key, val in rename_file.items()}
    print(f"Do you want to complete the following renaming in {schema_name}.{table_name}? (y/n)")
    print(f"{user_output}")
    confirmation = input("")
    
    if confirmation == 'y':

        cols_before = {key: get_column_name(int(key)) for key in rename_file}
        queries.execute_query(full_query, connection)
        cols_after = {key: get_column_name(int(key)) for key in rename_file}
            
        
        errors = []
        for key in rename_file:
            if cols_before[key] == cols_after[key]:
                errors.append(key)
        
        if len(errors) != 0:
            raise Exception(f"The following columns where not renamed correctly: {errors}")


def run():
    user = input("Enter your database username: ")
    password = getpass.getpass("Enter your database password: ")
    
    db_config = {
        'host': "dandypdb01fl",
        'dbname': "aedna_metadata_test",
        'port': "5432",
        'user': user,
        'password': password
    }
    
    rename_files = {
        "db_column_renamer.json": rename_db_column,
        "db_schema_renamer.json": rename_db_schema,
        "db_table_renamer.json": rename_db_tables,
        "template_column_renamer.json": rename_template_column,
        "template_renamer.json": rename_templates
    }
    
    renamer_dir_path = os.path.join(PATH_TO_MOUNT, "SUN-GI-metadb-test", "renamer")
    file_names = os.listdir(renamer_dir_path)
    
    if set(rename_files.keys()) != set(file_names):
        raise Exception("Files names not as expected")
    
    if len(file_names) != 5:
        raise Exception("number of renamer files not as expected")
    
    active_rename_files = []
    
    for file_name in file_names:
        file_path = os.path.join(renamer_dir_path, file_name)
        with open(file_path, 'r') as file:
            rename_file = json.load(file)
            if len(rename_file) > 0:    
                active_rename_files.append((file_name, rename_file))                            
    
    if len(active_rename_files) == 1:
        # prompt user to confirm and user info 
        # do rename
        file_name = active_rename_files[0][0]
        rename_file = active_rename_files[0][1]

        
    
        connection = psycopg2.connect(**db_config)   
        
        rename_files[file_name](connection)
                
    
    elif len(active_rename_files) == 0:
        raise Exception("All renaming files are empty")    
    
    else:
        raise Exception("Only one rename file can be non empty at a time")
        
    # Prompt user: Are you sure you want to rename?

    # Run renaming

run()