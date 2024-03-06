import pandas as pd
import json


def run(input_file, output_file):
    '''
    Makes a json file from excel sheet. Use together with update_comments_from_json.py for example.
    '''
    
    # Read Excel file into a DataFrame
    df = pd.read_excel(input_file)
    df.set_index(df.columns[0], inplace=True)

    
    excel_dict = df.to_dict()

    with open(output_file, "w") as json_file:
        json.dump(excel_dict, json_file, indent=4)


input_file = r'static\example_sheets_online\eDNA archive sampling.xlsx'
output_file = r'static\example_sheets_online\json_dumps\eDNA archive sampling.json'

run(input_file=input_file, output_file=output_file)