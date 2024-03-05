import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
import constants
from constants import DATABASE_CONFIG, DATABASE_CONFIG_2, ENGINE
import pandas as pd
import psycopg2
current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join('static', 'auto_sheets')
path = os.path.relpath(data_dir, current_dir)

data_types = {'integer': None, 
              'text': None, 
              'smallint': None, 
              'int4range': None, 
              'timestamp with time zone': None, 
              'real': None, 
              'date': None, 
              'timestamp without time zone': None, 
              'double precision': None}


type_descriptions = {'integer': {None}, 
                    'text': None, 
                    'smallint': None, 
                    'int4range': None, 
                    'timestamp with time zone': None, 
                    'real': None, 
                    'date': {'format': constants.ALLOWED_DATE_FORMATS}}, 
                    'timestamp without time zone': None, 
                    'double precision': None}
}

def generate_excel(output_folder, get_dtypes=False):
    f'''
    Generates and overwrites example sheets in {path} from table information in postgres
    '''
    
    dtypes = set()
    
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(**DATABASE_CONFIG_2)

    # Get a cursor
    cur = conn.cursor()

    # Query to get all tables in the schema
    query = f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{DATABASE_CONFIG['schema_name']}'"

    # Execute the query
    cur.execute(query)

    # Fetch all table names
    tables = cur.fetchall()

    # Loop through each table and generate Excel file
    for table in tables:
        table_name = table[0]
        output_file = os.path.join(output_folder, f'{table_name}.xlsx')

        # Query to get column names and data types
        column_query = f'''
        SELECT column_name, data_type, ordinal_position 
        FROM information_schema.columns 
        WHERE table_schema = '{DATABASE_CONFIG["schema_name"]}' AND table_name = '{table_name}' 
        ORDER BY ordinal_position;
        '''

        # Read SQL query into a DataFrame
        df = pd.read_sql_query(column_query, ENGINE)
        if get_dtypes:
            dtypes = dtypes.union(set(df['data_type']))
        

        # Write DataFrame to Excel file
        df.to_excel(output_file, index=False)

    # Close the cursor and database connection
    cur.close()
    conn.close()   


print(data_types)

{'Expected column names and positions:': {0: 'Examples of accepted data:', 1: nan, 2: nan, 3: nan, 4: 'Accepted format:', 5: 'Description:', 6: 'Required?*', 7: nan, 8: nan, 9: '*If a column is required, this means that the sheet will be rejected if there are any values missing from that column'}, 'Sample label (sticker)': {0: 'jkl223_hollerup_20230914_1', 1: 'jkl223_hollerup_20230914_2', 2: 'jkl223_hollerup_20230914_3', 3: nan, 4: '<ku-id>_<sampling_site>_<sampling_date>_<no>', 5: 'A standardized unique ID for the physical label. Consist of ku ID of field trip representative/leader/PI + sampling site (as local as possible) + collection date + incrementing integer.', 6: 'yes', 7: nan, 8: nan, 9: nan}, 'QR Code': {0: nan, 1: nan, 2: nan, 3: nan, 4: nan, 5: 'An id for the physical QR code on the sample', 6: 'yes', 7: nan, 8: nan, 9: nan}, 'Country/Ocean': {0: 'Denmark', 1: 'Denmark', 2: 'Denmark', 3: nan, 4: 'text', 5: nan, 6: 'yes', 7: nan, 8: nan, 9: nan}, 'City/Town/Location': {0: 'Hollerup', 1: 'Hollerup', 2: 'Hollerup', 3: nan, 4: 'text', 5: 'If relevant. Otherwise leave blank.', 6: nan, 7: nan, 8: nan, 9: nan}, 'Sampling site': {0: 'Hollerup', 1: 'Hollerup', 2: 'Hollerup', 3: nan, 4: 'text and/or numbers', 5: 'If relevant. Otherwise leave blank.', 6: nan, 7: nan, 8: nan, 9: nan}, 'Latitude': {0: 61.1399, 1: 61.1399, 2: 61.1399, 3: nan, 4: 'decimal degrees, max 2 digits, max 8 decimal points (-90 to 90)', 5: 'The geographical origin of the sample as defined by latitude. The values should be reported in decimal degrees as precise as possible (max. 8 decimal points).', 6: 'yes', 7: nan, 8: nan, 9: nan}, 'Longitude': {0: -45.5347, 1: -45.5347, 2: -45.5347, 3: nan, 4: 'decimal degrees, max 2 digits, max 8 decimal points (-180 to 180)', 5: 'The geographical origin of the sample as defined by longitude. The values should be reported in decimal degrees as precise as possible (max. 8 decimal points).', 6: 'yes', 7: nan, 8: nan, 9: nan}, 'Sampling Date': {0: '2023-10-22', 1: '2023-10-22', 2: '2023-10-22', 3: nan, 4: 'YYYY-MM-DD or DD-MM-YYYY (choose one)', 5: 'Date when the sampling occured.', 6: 'yes', 7: nan, 8: nan, 9: nan}, 'Sample provider(s)': {0: 'hlj234', 1: 'hlj234', 2: 'hlj234; glj523', 3: nan, 4: 'KU Ids', 5: 'Unique KU id(s) of the person(s) responsible for the sample extraction, seperated by semicolon if multiple.', 6: 'yes', 7: nan, 8: nan, 9: nan}, 'PI (KU ID)': {0: 'hlj234', 1: 'hlj234', 2: 'hlj234', 3: nan, 4: 'KU Id', 5: 'KU id of the principal investigator responsible for the project.', 6: 'yes', 7: nan, 8: nan, 9: nan}, 'Grant': {0: 'NOVO', 1: 'NOVO', 2: 'NOVO', 3: nan, 4: 'text and/or numbers', 5: 'Specify the grant that funds the project.', 6: 'yes', 7: nan, 8: nan, 9: nan}, 'Running Project Title': {0: 'Traversing European Coastlines', 1: 'Arctic Canada', 2: 'Arctic Canada', 3: nan, 4: 'text and/or numbers', 5: 'Referencing this google sheet: https://docs.google.com/spreadsheets/d/10TWDtKMug4yzOQUP7Q4APIoPNHQXCFX_RasijIgyCAA/edit?usp=sharing', 6: 'yes', 7: nan, 8: nan, 9: nan}, 'Sampling depth (discrete, cm)': {0: 10, 1: 200, 2: '300.3', 3: nan, 4: 'Numbers (decimals allowed)', 5: 'Depth measurement for discrete type samples (such as tube)', 6: nan, 7: nan, 8: nan, 9: nan}, 'Sampling depth (interval, cm)': {0: '[10, 50)', 1: '[10, 20)', 2: '[-10, -5)', 3: nan, 4: 
'Restricted mathematical notation of the form [<no>, <no>). Meaning only use "[" as the opening bracket and ")" as the closing bracket (decimals not allowed).', 5: 'Depth measurement for interval type samples (such as core) ', 6: nan, 7: nan, 8: nan, 9: nan}, 'Sampling depth reference': {0: 'msl', 1: 'local surface', 2: 'CGG_3_000002', 3: nan, 4: 'text and/or numbers', 5: 'Point from where the depth measurement was taken', 6: nan, 7: nan, 8: nan, 9: nan}, 'Correlation depth (bottom, cm)': {0: 10, 1: 200, 2: '300.3', 3: nan, 4: 'Numbers (decimals allowed)', 5: 'The local core depth that correlates with the  correlation depth (top) of the core immediately above.', 6: nan, 7: nan, 8: nan, 9: nan}, 'Correlation depth (top, cm)': {0: 10, 1: 200, 2: '300.3', 3: nan, 
4: 'Numbers (decimals allowed)', 5: 'The local core depth  that correlates with the  correlation depth (bottom) of the core immediately below.', 6: nan, 7: nan, 8: nan, 9: nan}, 'Sample container': {0: 'Core', 1: 'Monolith', 2: 'OSL', 3: nan, 4: 'Mathematical notation: Numbers, "()", "[]" and "," (decimal allowed only if "." is used as decimal point).', 5: 'Container used for sample collection/extraction/excavation', 6: nan, 7: nan, 8: nan, 9: nan}, 'Sediment type': {0: 'Lacustrine', 1: 'Glaciofluvial', 2: 'Glaciofluvial', 3: nan, 4: 'text and/or numbers', 5: 'Eg. Glacial, Lacustrine\nFluvial, Aeolian,Peat\nSoil', 6: nan, 7: nan, 8: nan, 9: nan}, 'Setting': {0: 'Outcrop', 1: 'Cave', 2: 'Lake', 3: nan, 4: 'text and/or numbers', 5: 'Outcrop, cave, lake, bog etc.', 6: nan, 7: nan, 8: nan, 9: nan}, 'Marine isotope stage estimate': {0: '5e', 1: '5e', 2: '5e', 3: nan, 4: 'text and/or numbers', 5: nan, 6: nan, 7: nan, 8: nan, 9: nan}, 'Period Estimate': {0: 'Holocene', 1: 'Holocene', 2: 'Pleistocene', 3: nan, 4: 'Full names seperated by comma', 5: nan, 6: nan, 7: nan, 8: nan, 9: nan}, 'Age Estimate (ka)': {0: '[1, 105)', 1: '[1, 105)', 2: '[1, 105)', 3: nan, 4: 'Restricted mathematical notation of the form [<no>, <no>). Meaning only use "[" as the opening bracket and ")" 
as the closing bracket (decimals not allowed).', 5: 'Not c14, just an estimate', 6: nan, 7: nan, 8: nan, 9: nan}, 'Height above mean sea level (meters)': {0: 37, 1: 37, 2: '37.5', 3: nan, 4: 'Number (decimal allowed)', 5: 'Specify as negative number if below mean sea level.', 6: nan, 7: nan, 8: nan, 9: nan}, 'Sample storage address': {0: 'GM', 1: 'GM', 2: 'GM', 3: nan, 4: 'Address ', 5: 'The exact address where the sample. If it\'s stored at geological museum then you can just write "GM".', 6: 'yes', 7: nan, 
8: nan, 9: nan}, 'Sample storage setting': {0: 'Cold room', 1: 'Walk-in Freezer', 2: 'Cold room', 3: nan, 4: 'text and/or numbers', 5: 'Specify the storage setting ', 6: 'yes', 7: nan, 8: nan, 9: nan}, 'Sample storage location': {0: 'A: shelf 4.5; W: shelf 
4.6', 1: 'A: shelf 4.5; W: shelf 4.6', 2: 'A: shelf 4.5; W: shelf 4.6', 3: nan, 4: 'text and/or numbers', 5: 'If working half and archive half are stored different places, report two locations seperated by semi-colon and preceded by either A: or W: ', 6: nan, 7: nan, 8: nan, 9: nan}, 'Storing date': {0: '2023-10-22', 1: '2023-10-22', 2: '2023-10-22', 3: nan, 4: 'YYYY-MM-DD or DD-MM-YYYY (choose one)', 5: 'Report when the sample was stored in the specified storage location.', 6: nan, 7: nan, 8: nan, 9: nan}, 'Disposal date': {0: '2023-10-22', 1: '2023-10-22', 2: '2023-10-22', 3: nan, 4: 'YYYY-MM-DD or DD-MM-YYYY (choose one)', 5: 'Report when the sample was disposed.', 6: nan, 7: nan, 8: nan, 9: nan}, 'Miscellaneous Sample Measurements or Observations': {0: 'water content: 10 %; ', 1: 'water content: 10 %;', 2: 'water content: 10 %; porosity: 5 %', 3: nan, 4: '<measurement/observation type>: <measurement/observation> <unit (optional)>', 5: 'Any relevant measurements/observations taken of the field sample. If multiple: seperate by semi-colon.', 6: 'yes', 7: nan, 8: nan, 9: nan}, 'Miscellaneous Environmental Measurements or Observations': {0: 'temperature: 7 celcius; ', 1: 'temperature: 7 celcius; ', 2: 'temperature: 7 celcius; cloud cover: overcast;', 3: nan, 4: '<measurement/observation type>: <measurement/observation> <unit (optional)>', 5: 'Any other relevant environmental measurements/observations. If multiple: seperate by semi-colon.', 6: nan, 7: nan, 8: nan, 9: nan}, 'Link to images': {0: nan, 1: nan, 2: nan, 3: 
nan, 4: 'text and/or numbers', 5: 'Link to any relevant images of the sample.', 6: nan, 7: nan, 8: nan, 9: nan}, 'Link to other relevant data': {0: nan, 1: nan, 2: nan, 3: nan, 4: 'text and/or numbers', 5: 'Link to other relevant data.', 6: nan, 7: nan, 8: 
nan, 9: nan}, 'Comment': {0: nan, 1: nan, 2: nan, 3: nan, 4: 'text and/or numbers', 5: nan, 6: nan, 7: nan, 8: nan, 9: nan}}