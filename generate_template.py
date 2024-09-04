import pandas as pd
import psycopg2
from constants.misc_constants import AUTO_GENERATED_COLUMNS
from constants.db_names.name_maps import db_to_sheet_rename_map, sheet_to_db_rename_map
from constants.db_names.names import data

from openpyxl import Workbook
from openpyxl.styles import PatternFill, Alignment


# Database connection parameters
conn_params = {
    'dbname': 'aedna_metadata_test',
    'user': 'glj523',
    'password': 'Wtcantfw36c!',
    'host': 'dandyweb01fl',
    'port': '5432'
}

# Connect to the database
conn = psycopg2.connect(**conn_params)

your_table = 'field_sample'
your_schema = 'test_1'
# Query to fetch the first row of the table
query = f"SELECT * FROM {your_schema}.{your_table} LIMIT 1"
df = pd.read_sql(query, conn)

for col in df.columns:
    if pd.api.types.is_datetime64tz_dtype(df[col]):
        df[col] = df[col].dt.tz_localize(None)

# Query to fetch column constraints
constraints_query = f"""
SELECT column_name, is_nullable
FROM information_schema.columns
WHERE table_name = '{your_table}' and table_schema = '{your_schema}'
"""
constraints_df = pd.read_sql(constraints_query, conn)




# Close the database connection
conn.close()

if your_table == data.field_sample():
    col_names = data.field_sample()
print(df.columns)
df = df.drop(columns=AUTO_GENERATED_COLUMNS, errors='ignore')
renamer = db_to_sheet_rename_map(schema_name=your_schema, table_name=your_table)
df_translated = df.rename(columns=renamer, errors='raise')
new_order = [col_names.field_sample_id(),
             'Field Label (informal)',
             'Master ID/Parent sample ID',
             'Running Project Title',
             'Permit for DNA Analysis (yes/no)',
             'Country/Ocean',
             'Site name',
             'Longitude (WGS84 decimal degrees)',
             'Latitude (WGS84 decimal degrees)',
             'Elevation (m asl)',
             'Water depth (m)',
             'Sample context',
             'Sample type',
             'Sample type in storage at GM',
             'Sample material',
             'Sample environment',
             'Age Estimate - from (ka)',
             'Age Estimate - to (ka)',
             'Sampling depth (discrete, cm)',
             'Sampling interval - from (cm)',
             'Sampling interval - to (cm)',
             'Sample date',
             'PI (Full name)',
             'Sample Provider(s) (Full name)',
             'Sample Provider(s) (Contact info)',
             'Sample storage setting',
             'Sample storage location',
             'Sample storage address',
             'Comments',
             'Link(s) to other relevant information',
             'Link(s) to images',
             'Miscellaneous Environmental Measurement(s) or Observation(s)',
             'Miscellaneous Sample Measurement(s) or Observation(s)',
             'Alias',
             'Cultural Affiliation',
             'Museum/Institution',
             'Other Relevant Information',
             'Site-Grid Elev (m asl)',
             'Site-Grid Latitude (WGS84 decimal degrees)',
             'Site-Grid Longitude (WGS84 decimal degrees)']

print(df.columns)


# Create a Pandas Excel writer using openpyxl as the engine
writer = pd.ExcelWriter('colored_header.xlsx', engine='openpyxl')

# Convert the DataFrame to an XlsxWriter Excel object
df_translated.to_excel(writer, index=False, sheet_name='Sheet1')

# Get the xlsxwriter workbook and worksheet objects
workbook  = writer.book
worksheet = writer.sheets['Sheet1']

# Define header formats
green_fill = PatternFill(start_color='00FF00', end_color='00FF00', fill_type='solid')
white_fill = PatternFill(start_color='FFFFFF', end_color='FFFFFF', fill_type='solid')
center_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

# Apply the header format based on NOT NULL constraints, center the text, and wrap text
for col in range(len(df.columns)):
    column_name = df.columns[col]
    is_nullable = constraints_df[constraints_df['column_name'] == column_name]['is_nullable'].values[0]
    cell = worksheet.cell(row=1, column=col+1)
    if is_nullable == 'NO':
        cell.fill = green_fill
    else:
        cell.fill = white_fill
    cell.alignment = center_alignment



# Set the row height for the header
worksheet.row_dimensions[1].height = 61  # You can adjust the height as needed

# Set the column width for all columns
for col in worksheet.columns:
    col_letter = col[0].column_letter
    worksheet.column_dimensions[col_letter].width = 30

# Save and close the Excel file
writer.close()




