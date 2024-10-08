import pandas as pd
from openpyxl import load_workbook
from openpyxl.worksheet.datavalidation import DataValidation

# Sample DataFrame
df = pd.DataFrame({
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Role': ['Engineer', 'Doctor', 'Artist']
})

# Save the DataFrame to an Excel file without the dropdowns
excel_filename = 'data_with_dropdowns.xlsx'
df.to_excel(excel_filename, index=False, engine='openpyxl')

# Open the file with openpyxl to add dropdowns
wb = load_workbook(excel_filename)
ws = wb.active

# Define the dropdown values
roles = ['Engineer', 'Doctor', 'Artist']

# Create a DataValidation object for the dropdown
dv = DataValidation(type="list", formula1=f'"{",".join(roles)}"', showErrorMessage=True, showInputMessage=True)

# Apply the dropdown to an arbitrary large range in column B (e.g., B2:B1000)
dv.add('B1:B1048576')

# Add the DataValidation object to the sheet
ws.add_data_validation(dv)

# Save the workbook with dropdowns
wb.save(excel_filename)

print(f"Excel file '{excel_filename}' created with dropdowns.")
