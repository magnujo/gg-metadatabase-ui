import pandas as pd
from openpyxl import load_workbook
from openpyxl.worksheet.datavalidation import DataValidation

# Create a DataFrame
data = {'Name': ['Alice', 'Bob', 'Charlie'], 'Choice': [''] * 3}
df = pd.DataFrame(data)

# Write DataFrame to an Excel file
excel_path = 'example.xlsx'
with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
    df.to_excel(writer, index=False, sheet_name='Sheet1')

# Open the file with openpyxl to add dropdowns
wb = load_workbook(excel_path)
ws = wb['Sheet1']

# Create a dropdown list
dropdown = DataValidation(type='list', formula1='"Option1,Option2,Option3"', allow_blank=True)
ws.add_data_validation(dropdown)

# Apply the dropdown to the desired column (e.g., 'Choice' column)
for row in range(2, len(df) + 2):  # Excel rows start at 1, header is row 1
    cell = f'B{row}'  # 'B' is the second column (Choice column)
    dropdown.add(ws[cell])

# Save the updated file
wb.save(excel_path)
