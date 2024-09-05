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

if your_table == data.field_sample():
    col_names = data.field_sample

# Query a good example row
query = f'''
SELECT * FROM "{your_schema}"."{your_table}" where "{col_names.field_sample_id()}" = 'min22a_3';
'''

df = pd.read_sql(query, conn)

# Handle timezone-aware datetime columns
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



# Drop auto-generated columns
df = df.drop(columns=AUTO_GENERATED_COLUMNS, errors='ignore')

# Rename columns based on the renaming map
renamer = db_to_sheet_rename_map(schema_name=your_schema, table_name=your_table)
df_translated = df.rename(columns=renamer, errors='raise')

# New column order
new_order = [
    col_names.field_sample_id(template=True),
    col_names.field_label(template=True),
    col_names.master_id_parent_sample_id(template=True),
    col_names.running_project_title(template=True),
    col_names.permit_for_dna_analysis(template=True),
    col_names.country_ocean(template=True),
    col_names.site_name(template=True),
    col_names.longitude(template=True),
    col_names.latitude(template=True),
    col_names.elevation(template=True),
    col_names.water_depth(template=True),
    col_names.sample_context(template=True),
    col_names.sample_type(template=True),
    col_names.sample_type_in_storage_at_gm(template=True),
    col_names.sample_material(template=True),
    col_names.sample_environment(template=True),
    col_names.age_estimate___from(template=True),
    col_names.age_estimate___to(template=True),
    col_names.sampling_depth(template=True),
    col_names.sampling_interval___from(template=True),
    col_names.sampling_interval___to(template=True),
    col_names.sample_date(template=True),
    col_names.pi(template=True),
    col_names.sample_provider_name(template=True),
    col_names.sample_provider_contact(template=True),
    col_names.sample_storage_setting(template=True),
    col_names.sample_storage_location(template=True),
    col_names.sample_storage_address(template=True),
    col_names.comments(template=True),
    col_names.link_to_other_relevant_information(template=True),
    col_names.link_to_images(template=True),
    col_names.miscellaneous_environmental_measurement_or_observation(template=True),
    col_names.miscellaneous_sample_measurement_or_observation(template=True),
    col_names.alias(template=True),
    col_names.cultural_affiliation(template=True),
    col_names.museum_institution(template=True),
    col_names.other_relevant_information(template=True),
    col_names.site_grid_elev(template=True),
    col_names.site_grid_latitude(template=True),
    col_names.site_grid_longitude(template=True)
]

df_translated = df_translated[new_order]

for col in df_translated.select_dtypes(include='bool').columns:
    df_translated[col] = df_translated[col].map({True: 'yes', False: 'no'})

# Create a Pandas Excel writer using openpyxl as the engine
writer = pd.ExcelWriter('colored_header.xlsx', engine='openpyxl')

# Write the DataFrame to Excel
df_translated.to_excel(writer, index=False, sheet_name='Sheet1')

# Get the xlsxwriter workbook and worksheet objects
workbook = writer.book
worksheet = writer.sheets['Sheet1']

# Define header formats
green_fill = PatternFill(start_color='00FF00', end_color='00FF00', fill_type='solid')
white_fill = PatternFill(start_color='FFFFFF', end_color='FFFFFF', fill_type='solid')
center_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

# Map renamed columns back to the original names for constraint checking
reverse_renamer = {v: k for k, v in renamer.items()}

special_non_mandatory_columns = [
    col_names.sampling_depth(template=True),
    col_names.sampling_interval___from(template=True),
    col_names.sampling_interval___to(template=True)
]

#  Columns that are not mandatory in DB but actually should be filled
should_be_mandatory = [
    col_names.sample_date(template=True),
]

light_green_fill = PatternFill(start_color='CCFFCC', end_color='CCFFCC', fill_type='solid')


for col_num, col_name in enumerate(df_translated.columns):
    # Get the original column name
    original_col_name = reverse_renamer.get(col_name, col_name)

    # Check the NOT NULL constraint
    is_nullable = constraints_df[constraints_df['column_name'] == original_col_name]['is_nullable'].values[0]
    
    # Apply color based on constraints and special non-mandatory status
    cell = worksheet.cell(row=1, column=col_num + 1)
    if original_col_name in special_non_mandatory_columns:
        cell.fill = light_green_fill
    elif is_nullable == 'NO' or original_col_name in should_be_mandatory:
        cell.fill = green_fill
    else:
        cell.fill = white_fill

    # Align the text in the cell
    cell.alignment = center_alignment

# Set the row height for the header
worksheet.row_dimensions[1].height = 61  # Adjust the height as needed

# Set the column width for all columns
for col in worksheet.columns:
    col_letter = col[0].column_letter
    worksheet.column_dimensions[col_letter].width = 30

# Save and close the Excel file
writer.close()
