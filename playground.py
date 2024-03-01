
import pandas as pd
import json
# Read the Excel file into a DataFrame
df = pd.read_excel(r'C:\Users\glj523\Documents\github repoes\upload_web_app\static\example_sheets_online\Field sampling (internal).xlsx')
df  = df.drop(df.columns[0], axis=1)
# Convert the DataFrame into a dictionary
excel_dict = df.to_dict()


with open("output.json", "w") as json_file:
    json.dump(excel_dict, json_file, indent=4)