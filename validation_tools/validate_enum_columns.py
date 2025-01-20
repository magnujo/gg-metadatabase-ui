

import requests
import json
import pandas as pd
import constants.db_table_related_constants as db_table_related_constants
from utils import misc
import constants.misc_constants as misc_constants
from constants.db_names.names import data


ALLOWED_VALUES = {data.field_sample(): {'sample type': ['osl', 'core', 'monolith', 'sample bag', 'tube']}}

COLUMNS_TO_CHECK = {data.field_sample(): ["Country/Ocean", ""]}

def validate_enum_columns(df, valid_enum_values):
    '''
Not being used. Enum validation is done in the database with foreign keys to enum tables.
'''
    '''
    valid_enum_values format: {col_name1: [allowed values], col_name2: [allowed values]}
    '''
    invalid_entries = []
    for column, valid_values in valid_enum_values.items():
        if column in df.columns:
            df[column] = df[column].str.lower()
            invalid_values = df[~df[column].isin(valid_values)][column]
            if not invalid_values.empty:
                invalid_entries.append((column, invalid_values))
    return invalid_entries

def get_spaam(table_name):
    '''
Not being used. Enum validation is done in the database with foreign keys to enum tables.
'''
    '''
    Returns allowed values from the spaam community as a dataframe where index is column name and '
    '''
    
    if table_name in db_table_related_constants.DBTableRelated.TABLE_TYPES_FOR_ENUM_VALIDATION["ENVIRONMENTAL"]["SAMPLE"]:
        validation_schema = misc.load_json_url(misc_constants.VALIDATION_SCHEMA_LINKS["SAMPLE"])
    elif table_name in db_table_related_constants.DBTableRelated.TABLE_TYPES_FOR_ENUM_VALIDATION["ENVIRONMENTAL"]["LIBRARY"]:
        validation_schema = misc.load_json_url(misc_constants.VALIDATION_SCHEMA_LINKS["LIBRARY"])
    else:
        raise Exception(f"validate_enums is not available for {table_name}")

    schema = pd.DataFrame(validation_schema["items"]["properties"])
    schema_t = schema.T
    
    # If a column is a enum column it means it has a reference ($ref) to the SPAAM list of allowed values or if its in ALLOWED_VALUES. 
    enum_columns = schema_t[~schema_t["$ref"].isna()]["$ref"]
        
    # The following loops through each enum column in the parsed_sheet and returns a dataframe with the column and rows that do not contain an enum member.
    for column_name in list(enum_columns.index):
        link_to_enum_members_json = enum_columns[column_name] 
        enum_columns[column_name] = list(misc.load_json_url(link_to_enum_members_json)["enum"])
        
    # enum_columns = enum_columns.rename(columns={'$ref': 'allowed_values'})
    return enum_columns

def validate_enums_exp(parsed_sheet, table_name):
    '''
Not being used. Enum validation is done in the database with foreign keys to enum tables.
'''
    
    table_name = table_name.lower()
    parsed_sheet = parsed_sheet.rename(columns=lambda x: x.lower())
    spaam_allowed_values = get_spaam(table_name)
    # only return the columns that are in parsed sheet
    
    translator = misc_constants.FROM_SPAAM_COLUMN_NAMES(table_name)
    
    translator = misc.values_and_keys_to_lower(translator)
    
    if translator:
        spaam_allowed_values = spaam_allowed_values.rename(index=translator)
    
    spaam_allowed_values = spaam_allowed_values.rename(index=lambda x: x.lower())

    custom_allowed_values = ALLOWED_VALUES[table_name]
    custom_allowed_values = misc.values_and_keys_to_lower(custom_allowed_values)
    
    combined = {**custom_allowed_values, **spaam_allowed_values}
    combined = misc.values_and_keys_to_lower(combined)
    invalid_values = validate_enum_columns(parsed_sheet, combined)
    
    return combined, invalid_values
    

# def validate_enums_spaam(parsed_sheet, table_name, type="Environmental"):
    
#     '''
#     Checks all the enum columns of a parsed_sheet. Translates relevant columns to match the column names of the SPAAM comminuty and validates
#     the data against their defined enum members. An enum column is defined as being restricted to a fixed set of allowed values. Example: County/Ocean is restricted
#     to a official list of ocean and country names.
#     '''

#     if table_name in db_table_related_constants.DBTableRelated.TABLE_TYPES_FOR_ENUM_VALIDATION["ENVIRONMENTAL"]["SAMPLE"]:
#         validation_schema = misc.load_json_url(misc_constants.VALIDATION_SCHEMA_LINKS["SAMPLE"])
#     elif table_name in db_table_related_constants.DBTableRelated.TABLE_TYPES_FOR_ENUM_VALIDATION["ENVIRONMENTAL"]["LIBRARY"]:
#         validation_schema = misc.load_json_url(misc_constants.VALIDATION_SCHEMA_LINKS["LIBRARY"])
#     else:
#         raise Exception(f"validate_enums is not available for {table_name}")
    
#     if not type == "Environmental":
#         raise Exception("validate_enums only works for enviornmental samples for now")
        
#     schema = pd.DataFrame(validation_schema["items"]["properties"])
#     schema_t = schema.T
    
#     # If a column is a enum column it means it has a reference ($ref) to the SPAAM list of allowed values or if its in ALLOWED_VALUES. 
#     enum_columns = schema_t[~schema_t["$ref"].isna()]["$ref"]
    
    
#     if table_name in misc_constants.TO_SPAAM_COLUMN_NAMES:
#         column_name_translator = misc_constants.TO_SPAAM_COLUMN_NAMES[table_name]
#         parsed_sheet = parsed_sheet.rename(columns=column_name_translator)
        
#     parsed_sheet = parsed_sheet.rename(columns=lambda x: x.lower())
    
    
#     # The following loops through each enum column in the parsed_sheet and returns a dataframe with the column and rows that do not contain an enum member.
#     res = {}
#     enum_members = {}
#     enum_members_dfs = []
    
#     for column_name in list(enum_columns.index):
#         if column_name in parsed_sheet.columns:
#             link_to_enum_members_json = enum_columns[column_name] 
#             enum_members[column_name] = list(map(lambda x: x.lower(), misc.load_json_url(link_to_enum_members_json)["enum"]))
            
#             is_valid = parsed_sheet[column_name].str.lower().isin(enum_members[column_name])
#             res[column_name] = is_valid
    
#     # Filter the parsed sheet to only show the neg of valid_values and drop any rows and columns with 0 invalid values.
#     valid_values = pd.DataFrame(res)

#     invalid_values = validate_enum_columns(parsed_sheet, valid_enum_values=enum_members)
    
#     # Returns True if all values are good
#     passed = valid_values.all().all()

#     # Returns all the bad values as a pandas dataframe with row numbers as index
#     bad_values = parsed_sheet[~valid_values].dropna(axis="columns", how="all").dropna(axis="rows", how="all")

#     for key in enum_members:
#         if key in list(bad_values):
#             enum_members_dfs.append(pd.DataFrame({key: list(map(lambda x: x.lower(), enum_members[key]))}))
    
#     translator = misc_constants.FROM_SPAAM_COLUMN_NAMES(table_name)
#     if translator:
#         bad_values = bad_values.rename(columns=translator)
        
#     bad_values_output = []
#     for col in bad_values.columns:
#         trimmed = pd.DataFrame(bad_values[col].dropna())
#         trimmed["Row number"] = trimmed.index
#         trimmed["Row number"] = trimmed["Row number"].apply(lambda x: x + 2)
#         column_name = trimmed.columns[0]
#         trimmed = trimmed.rename(columns={column_name: 'Value'})
#         trimmed.columns = pd.MultiIndex.from_tuples([(f"Column name: '{column_name}'", 'Value'), (f"Column name: '{column_name}'", 'Row Number')])
        
#         bad_values_output.append(trimmed)

#     for i in range(len(enum_members_dfs)):
#         enum_members_dfs[i] = enum_members_dfs[i].rename(columns=translator)
    
#     return passed, bad_values_output, enum_members_dfs
    

    

    