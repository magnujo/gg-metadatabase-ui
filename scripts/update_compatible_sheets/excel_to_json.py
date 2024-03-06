import pandas as pd
import json

input_file = r'static/example_sheets_online/Field sampling (internal).xlsx'
output_file = r'static\example_sheets_online\json_dumps\Field sampling (internal).json'

def run(input_file, output_file):
    '''
    Makes or updates a json file from excel sheet. Use together with update_comments_from_json.py for example 
    to add/update comments of a table with a spreadsheet.
    '''
    
    # Read Excel file into a DataFrame
    df = pd.read_excel(input_file)
    df.set_index(df.columns[0], inplace=True)

    
    excel_dict = df.to_dict()

    with open(output_file, "w") as json_file:
        json.dump(excel_dict, json_file, indent=4)


run(input_file=input_file, output_file=output_file)