import requests
import json
import pandas as pd
from utils import misc
import constants


def validate_enums(parsed_sheet, table_name, type="Environmental"):
    
    '''
    Checks all the enum columns of a parsed_sheet. Translates relevant columns to match the column names of the SPAAM comminuty and validates
    the data against their defined enum members. An enum column is defined as being restricted to a fixed set of allowed values. Example: County/Ocean is restricted
    to a official list of ocean and country names.
    '''
    
    
    # TODO: Place all enum schema links in a list to make it easier to expand
    
    if type == "Environmental":
        sample_schema = misc.load_json_url('https://raw.githubusercontent.com/SPAAM-community/AncientMetagenomeDir/master/ancientmetagenome-environmental/samples/ancientmetagenome-environmental_samples_schema.json')
        library_schema = misc.load_json_url('https://raw.githubusercontent.com/SPAAM-community/AncientMetagenomeDir/master/ancientmetagenome-environmental/libraries/ancientmetagenome-environmental_libraries_schema.json')
    else:
        raise Exception("validate_enums only works for enviornmental samples for now")
        
    schema = pd.DataFrame(validation_schema["items"]["properties"])
    schema_t = schema.T
    
    # If a column is a enum column it means it has a reference ($ref) to the SPAAM list of allowed values. 
    enum_columns = schema_t[~schema_t["$ref"].isna()]["$ref"]
    
    column_name_translator = constants.TO_SPAAM_COLUMN_NAMES[table_name]
    parsed_sheet = parsed_sheet.rename(columns=column_name_translator)
    parsed_sheet = parsed_sheet.rename(columns=lambda x: x.lower())
    
    # The following loops through each enum column in the parsed_sheet and returns a dataframe with the column and rows that do not contain an enum member.
    res = {}
    for column_name in list(enum_columns.index):
        if column_name in parsed_sheet.columns:
            link_to_enum_members_json = enum_columns[column_name] 
            enum_members = list(map(lambda x: x.lower(), misc.load_json_url(link_to_enum_members_json)["enum"]))
            print(enum_members)
            is_valid = parsed_sheet[column_name].str.lower().isin(enum_members)
            res[column_name] = is_valid
    
    # Filter the parsed sheet to only show the neg of valid_values and drop any rows and columns with 0 invalid values.
    valid_values = pd.DataFrame(res)
    final_res = parsed_sheet[~valid_values].dropna(axis="columns", how="all").dropna(axis="rows", how="all")

    
    return final_res    
    

    

    