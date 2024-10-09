
from openpyxl.comments import Comment
import pandas as pd
import psycopg2
from constants.misc_constants import AUTO_GENERATED_COLUMNS, ADMIN_EMAIL
from constants.db_names.name_maps import db_to_sheet_rename_map, sheet_to_db_rename_map
from constants.db_names.names import data
from constants.db_connections import ENGINE_READ_ONLY, DATABASE_CONFIG_READ_ONLY, PSY_CONN
from utils import misc

from openpyxl import Workbook, load_workbook
from openpyxl.styles import PatternFill, Alignment, Border, Side, Font


# Connect to the database

def generate(table_name, schema_name, conn, save_path):

    table_name = 'field_sample'
    schema_name = 'test_1'

    if table_name == data.field_sample():
        col_names = data.field_sample

    # Query a good example row
    query = f'''
    SELECT * FROM "{schema_name}"."{table_name}" where "{col_names.field_sample_id()}" = 'min22a_3';
    '''

    df = pd.read_sql(query, conn)

    context_types = pd.read_sql(f'select * from "{schema_name}"."{data.field_sample_context_types()}"', con=ENGINE_READ_ONLY)[data.field_sample_context_types.name()]
    environment_types = pd.read_sql(f'select * from "{schema_name}"."{data.field_sample_environment_types()}"', con=ENGINE_READ_ONLY)[data.field_sample_environment_types.name()]
    material_types = pd.read_sql(f'select * from "{schema_name}"."{data.field_sample_material_type()}"', con=ENGINE_READ_ONLY)[data.field_sample_material_type.name()]
    sample_types = pd.read_sql(f'select * from "{schema_name}"."{data.field_sample_types()}"', con=ENGINE_READ_ONLY)[data.field_sample_types.name()]

    enum_sheet = pd.DataFrame({
        data.field_sample.sample_context(template=True): context_types,
        data.field_sample.sample_environment(template=True): environment_types,
        data.field_sample.sample_material(template=True): material_types,
        data.field_sample.sample_type(template=True): sample_types
    })

    for col in df.select_dtypes(include='bool').columns:
        df[col] = df[col].map({True: 'yes', False: 'no'})

    new_rows = [
        {col_names.field_label(): ""},
        {col_names.field_sample_id(): "Column colour legend:"},
        {col_names.field_label(): " = Mandatory column"},
        {col_names.field_label(): " = Non-mandatory column"},
        {col_names.field_label(): " = Mandatory depending on environment, type or other features"},
        {col_names.field_sample_id(): "Delete this and all rows above before uploading (except row 1 ofcourse!)"}
    ]
    
    new_row_0 = {col_names.field_sample_id(): "EXAMPLE ROW:"}
    
    df_list = df.to_dict('records')

    # Insert rows at specific positions
   
    df_list.insert(0, new_row_0)
    
    for i, row in enumerate(new_rows):
        df_list.insert(i+2, row)

    # Convert back to DataFrame
    df = pd.DataFrame(df_list)

    # Sort the index to maintain order
    df = df.sort_index().reset_index(drop=True)

    # Handle timezone-aware datetime columns
    # for col in df.columns:
    #     if pd.api.types.is_datetime64tz_dtype(df[col]):
    #         df[col] = df[col].dt.tz_localize(None)

    for col in df.columns:
        if isinstance(df[col].dtype, pd.DatetimeTZDtype):
            df[col] = df[col].dt.tz_localize(None)
            
    # Query to fetch column constraints
    constraints_query = f"""
    SELECT column_name, is_nullable
    FROM information_schema.columns
    WHERE table_name = '{table_name}' and table_schema = '{schema_name}'
    """
    constraints_df = pd.read_sql(constraints_query, conn)

    # Drop auto-generated columns
    df = df.drop(columns=AUTO_GENERATED_COLUMNS, errors='ignore')

    # Rename columns based on the renaming map
    renamer = db_to_sheet_rename_map(schema_name=schema_name, table_name=table_name)
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
    
    # Create a Pandas Excel writer using openpyxl as the engine
    writer = pd.ExcelWriter(save_path, engine='openpyxl')
    
    enum_sheet_name = 'Allowed categorical values'
    data_sheet_name = 'Insert Data Here'
    
    # Write the DataFrame to Excel
    df_translated.to_excel(writer, index=False, sheet_name=data_sheet_name)
    enum_sheet.to_excel(writer, index=False, sheet_name=enum_sheet_name)
    

    # Get the xlsxwriter workbook and worksheet objects
    workbook = writer.book
    worksheet = writer.sheets[data_sheet_name]
    # bold_format = workbook.add_format({'bold': True})
    enum_sheet = writer.sheets[enum_sheet_name]

    # Define header formats
    mandatory_colour = PatternFill(start_color='8ED973', end_color='8ED973', fill_type='solid')
    non_mandatory_colour = PatternFill(start_color='FFFFFF', end_color='FFFFFF', fill_type='solid')
    feature_dependent_colour = PatternFill(start_color='D9EFCD', end_color='D9EFCD', fill_type='solid')
    yellow_fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')
    center_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    border = Border(top=Side('thin'), bottom=Side('thin'), left=Side('thin'), right=Side('thin'))


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

    # comments = misc.get_comments(DATABASE_CONFIG_READ_ONLY['dbname'], 'test_1', 'field_sample', psy_conn=PSY_CONN)
    
    for col_num, col_name in enumerate(df_translated.columns):
        # Get the original column name
        original_col_name = reverse_renamer.get(col_name, col_name)

        # Check the NOT NULL constraint
        is_nullable = constraints_df[constraints_df['column_name'] == original_col_name]['is_nullable'].values[0]
        
        # Apply color based on constraints and special non-mandatory status
        cell = worksheet.cell(row=1, column=col_num + 1)
        if original_col_name in special_non_mandatory_columns:
            cell.fill = feature_dependent_colour
        elif is_nullable == 'NO' or original_col_name in should_be_mandatory:
            cell.fill = mandatory_colour
        else:
            cell.fill = non_mandatory_colour
        
        # comment = str(comments[comments['Column Name'] == original_col_name]['Comment'].iloc[0])
        # print(comment)
        # cell.comment = Comment(comment, ADMIN_EMAIL)
        
            
        # Align the text in the cell
        cell.alignment = center_alignment
    
        example_cell = worksheet.cell(row=9, column=col_num + 1)
        example_cell.fill = yellow_fill
        example_cell.font = Font(bold=True)

    worksheet.cell(row=6, column=1).fill = mandatory_colour 
    worksheet.cell(row=6, column=1).border = border 
    worksheet.cell(row=7, column=1).fill = non_mandatory_colour 
    worksheet.cell(row=7, column=1).border = border 
    worksheet.cell(row=8, column=1).fill = feature_dependent_colour 
    worksheet.cell(row=8, column=1).border = border 
    # Set the row height for the header
    worksheet.row_dimensions[1].height = 61  # Adjust the height as needed
    # Set the column width for all columns
    for col in worksheet.columns:
        col_letter = col[0].column_letter
        worksheet.column_dimensions[col_letter].width = 30
    

    worksheet = writer.sheets[enum_sheet_name]
    for col in worksheet.columns:
        col_letter = col[0].column_letter
        worksheet.column_dimensions[col_letter].width = 30
        
    # Create a new sheet for the guide
    guide_sheet = workbook.create_sheet(title='Guide')

    # Add instructions to the guide sheet
    instructions = [
        "To limit data insert errors, please read the instructions below before you begin to insert data:",
        "1. Read the column definitions thoroughly before inserting data, so you know what data to put there. Hover over the column names to see their definitions.",
        f"2. There are some columns that only accepts a finite set of categorical values. Inspect the sheet 'Allowed categorical values', to see what those values are. If you wish to include a categorical value contact {ADMIN_EMAIL} (it wont help if you just add it to the template)", 
        "3. Before uploading/sending the file, ensure all entries are accurate and complete.",
        "4. Delete any empty rows and columns",
        "5. Delete the yellow row and all the rows above it, except the row with the column names."
        f"Feel free to contact {ADMIN_EMAIL} if you have any questions or feedback to this template"
    ]

    for idx, instruction in enumerate(instructions, start=1):
        guide_sheet[f'A{idx}'] = instruction

    # Optionally, adjust column width for better readability
    for col in guide_sheet.columns:
        max_length = 0
        column = col[0].column_letter  # Get the column name
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2)
        guide_sheet.column_dimensions[column].width = adjusted_width
    
    # Save and close the Excel file
    writer.close()

# generate('field_sample', 'test_1', conn=ENGINE_READ_ONLY, save_path='color.xlsx')