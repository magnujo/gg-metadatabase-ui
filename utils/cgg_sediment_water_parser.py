from utils import parsers
import constants
import pandas as pd
from constants import DATABASE_CONFIG, ADMIN_EMAIL, ENGINE
import pandas as pd
from utils.parsers import parse_dates, parse_floats, validate_integers

def parse(file_path, date_format, database_table_name, decimal_point, thousands_seperator):
    
    float_columns = ['Depth (discrete, cm)',
                     'height (m) asl.',
                     'Sample size',
                     'Lat',
                     'Lon',
                     ]
    
    integer_columns = []
    
    int_range_columns = ['Depth (interval, cm)', 'Age (years BP)']
    
    date_columns = ['Extraction date', 
                    'Library date',
                    'Date collected',
                    'Date recieved',
                    'Date returned',
                    'Date out'
                    ]
    
    boolean_columns = []
    
    primary_key = 'CGG ID'

    # check for expected cols
    expected_columns = pd.read_sql(sql=f"SELECT * from {constants.DATABASE_CONFIG['schema_name']}.{database_table_name}", con=constants.ENGINE).columns
    expected_columns = expected_columns[:-3] 
    
    
    
    # TODO: Make unit test with mock data.
    assert list(expected_columns) == list(sheet.columns), ("Column names and/or positions not as expected")

    # For drop testing. Counts the number of rows where primary key is not null.
    num_of_not_null_rows = len(sheet[sheet[primary_key].notnull()]) 

    # TODO: Delete after deployment and ask make uploader responsible.
    if primary_key in sheet.columns:
        sheet = sheet.dropna(axis='index', how='all', subset=[primary_key])
    else:
        raise Exception (f"Upload failed. Expected column {primary_key} not found. Contact {constants.ADMIN_EMAIL} if you think this is a mistake")
    
    # Drop test:
    if len(sheet) != num_of_not_null_rows:
        raise Exception(f'Error dropping null values. Contact {constants.ADMIN_EMAIL} for help.')
    
    # Parse dates, throws error if formatting is wrong in the sheet
    sheet = parse_dates(sheet, date_columns=date_columns, date_format=date_format)
            
    sheet = parse_floats(sheet, float_columns, decimal_point, thousands_seperator)
    sheet = validate_integers(sheet, integer_columns)

    return sheet