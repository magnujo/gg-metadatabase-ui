import requests
import json
import pandas as pd
import constants.db_table_related_constants as db_table_related_constants
from utils import misc
import constants.misc_constants as misc_constants


def validate_enums(parsed_sheet, table_name, type="Environmental"):
    
    '''
    Checks all the enum columns of a parsed_sheet. Translates relevant columns to match the column names of the SPAAM comminuty and validates
    the data against their defined enum members. An enum column is defined as being restricted to a fixed set of allowed values. Example: County/Ocean is restricted
    to a official list of ocean and country names.
    '''

    if table_name in db_table_related_constants.DBTableRelated.TABLE_TYPES_FOR_ENUM_VALIDATION["ENVIRONMENTAL"]["SAMPLE"]:
        validation_schema = misc.load_json_url(misc_constants.VALIDATION_SCHEMA_LINKS["SAMPLE"])
    elif table_name in db_table_related_constants.DBTableRelated.TABLE_TYPES_FOR_ENUM_VALIDATION["ENVIRONMENTAL"]["LIBRARY"]:
        validation_schema = misc.load_json_url(misc_constants.VALIDATION_SCHEMA_LINKS["LIBRARY"])
    else:
        raise Exception(f"validate_enums is not available for {table_name}")
    
    if not type == "Environmental":
        raise Exception("validate_enums only works for enviornmental samples for now")
        
    schema = pd.DataFrame(validation_schema["items"]["properties"])
    schema_t = schema.T
    
    # If a column is a enum column it means it has a reference ($ref) to the SPAAM list of allowed values. 
    enum_columns = schema_t[~schema_t["$ref"].isna()]["$ref"]
    
    if table_name in misc_constants.TO_SPAAM_COLUMN_NAMES:
        column_name_translator = misc_constants.TO_SPAAM_COLUMN_NAMES[table_name]
        parsed_sheet = parsed_sheet.rename(columns=column_name_translator)
        
    parsed_sheet = parsed_sheet.rename(columns=lambda x: x.lower())
    
    
    # The following loops through each enum column in the parsed_sheet and returns a dataframe with the column and rows that do not contain an enum member.
    res = {}
    enum_members = {}
    enum_members_dfs = []
    for column_name in list(enum_columns.index):
        if column_name in parsed_sheet.columns:
            link_to_enum_members_json = enum_columns[column_name] 
            enum_members[column_name] = list(map(lambda x: x.lower(), misc.load_json_url(link_to_enum_members_json)["enum"]))
            
            is_valid = parsed_sheet[column_name].str.lower().isin(enum_members[column_name])
            res[column_name] = is_valid
    
    # Filter the parsed sheet to only show the neg of valid_values and drop any rows and columns with 0 invalid values.
    valid_values = pd.DataFrame(res)

    # Returns True if all values are good
    passed = valid_values.all().all()

    # Returns all the bad values as a pandas dataframe with row numbers as index
    bad_values = parsed_sheet[~valid_values].dropna(axis="columns", how="all").dropna(axis="rows", how="all")

    for key in enum_members:
        if key in list(bad_values):
            enum_members_dfs.append(pd.DataFrame({key: list(map(lambda x: x.lower(), enum_members[key]))}))
    
    translator = misc_constants.FROM_SPAAM_COLUMN_NAMES(table_name)
    if translator:
        bad_values = bad_values.rename(columns=translator)
        
    bad_values_output = []
    for col in bad_values.columns:
        trimmed = pd.DataFrame(bad_values[col].dropna())
        trimmed["Row number"] = trimmed.index
        trimmed["Row number"] = trimmed["Row number"].apply(lambda x: x + 2)
        column_name = trimmed.columns[0]
        trimmed = trimmed.rename(columns={column_name: 'Value'})
        trimmed.columns = pd.MultiIndex.from_tuples([(f"Column name: '{column_name}'", 'Value'), (f"Column name: '{column_name}'", 'Row Number')])
        
        bad_values_output.append(trimmed)

    for i in range(len(enum_members_dfs)):
        enum_members_dfs[i] = enum_members_dfs[i].rename(columns=translator)
    
    return passed, bad_values_output, enum_members_dfs
    

    

    