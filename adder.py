# TODO: Translate
# TODO: Implement
# TODO: Make queries safe from sql injection

import pandas as pd
import json
from utils import queries
from constants.misc_constants import PSYCON_CONFIG, PATH_TO_MOUNT
from db_names import db_names, name_maps, get_column_name, get_schema_name, get_table_name
import os
import psycopg2
import getpass

db_config = PSYCON_CONFIG

def add_columns():
    '''
    Adds columns to the database using the column_adder.json file. The file must have the following format:
    
    {
        <table_id_1>: [<new_column_name_1>, <new_column_name_2>, ..., <new_column_name_N>]
        <table_id_2>: [<new_column_name_1>, <new_column_name_2>, ..., <new_column_name_N>]
        .
        .
        .
        <table_id_N>: [<new_column_name_1>, <new_column_name_2>, ..., <new_column_name_N>]
    }
    
    '''
    
    file_name = "column_adder.json"
    
    print("Starting add_column scripts...")
    
    user_name = input("DB username: ")
    password = getpass.getpass("Password: ")
    db_config["user"] = user_name
    db_config["password"] = password
    
    connection = psycopg2.connect(**db_config)
    
    file_path = os.path.join(PATH_TO_MOUNT, "SUN-GI-metadb-test", "adder", file_name)
    
    # Load renamer file
    with open(file_path, 'r') as file:
        adder_file: dict[int, list[str]] = json.load(file)
        
    adder_file = {int(k): v for k, v in adder_file.items()}
    
    # Test format of file
    if len(adder_file) == 0:
        raise Exception(f"{file_path} is empty")
    
    for key, value in adder_file.items():
        if not isinstance(key, int):
            raise TypeError(f"Expected key of type int, but got {type(key).__name__}")
        if not isinstance(value, list):
            raise TypeError(f"Expected value of type list, but got {type(value).__name__}")
        if len(value) < 1:
            raise TypeError(f"Found empty value")
        for item in value:
            if not isinstance(item, str):
                raise TypeError(f"Expected value of type str, but got {type(item).__name__}")
        
    for item in adder_file.items():
        print("Table: ", get_table_name(int(item[0])), "Columns: ", item[1])  
    
    confirmation = input(f"Do you wish to continue? (y/n)")      
    
    if confirmation == "y":
        full_query = ""
        
        for key in adder_file:
            table_id = int(key) 
            cols_to_add = adder_file[key]
            
            nm = name_maps()
            table_names = name_maps.table_names()
            schema_names = name_maps.schema_names()
            column_names = name_maps.column_names()
            
            q1 = f'''
            select "{schema_names.schema_name}", "{table_names.table_name}", "{table_names.sheet_template_name}"
            from "{nm}"."{table_names}" tn 
            join "{nm}"."{schema_names}" sn on sn."{schema_names.schema_id}" = tn."{table_names.schema_id}"
            where {table_names.table_id} = '{table_id}';
            '''
            
            res = queries.execute_query(q1, connection)
            
            if len(res) != 1 or len(res[0]) != 3:
                raise Exception("res not the expected size")
            
            schema_name, table_name, template_name = res[0]
            if str(schema_name) == str(name_maps()):
                raise Exception(f"Altering table {schema_name} is not allowed.")
            
            for col_name in cols_to_add:
                # Insert row in map
                mapper_update_q = f'''
                INSERT INTO "{name_maps()}"."{column_names}"("{column_names.column_name_db}", "{column_names.table_id}", "{column_names.column_name_sheet}")
                VALUES ('{col_name}', '{table_id}', '{col_name}');
                '''
                
                #  Add col to table
                table_update_q = f'''
                ALTER TABLE "{schema_name}"."{table_name}" 
                ADD COLUMN "{col_name}" TEXT;
                '''
                
            
                full_query = full_query + mapper_update_q + table_update_q
            
            
            # Load the Excel file
            template_file_path = os.path.join(PATH_TO_MOUNT, "SUN-GI-metadb-test", "standard_spreadsheet_templates", template_name)
            df = pd.read_excel(template_file_path)

            for col_name in cols_to_add:
            # Rename the column
                if col_name not in df.columns:
                    df[col_name] = None
                else:
                    raise Exception(f"{col_name} already exists in template")

            # Save the DataFrame back to Excel
            df.to_excel(template_file_path, index=False)
        
        queries.execute_query(full_query, connection)
        
        # TODO: Implement test

        
        # add cols to template:
    
        
    

add_columns()