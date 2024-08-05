from utils import parsers
import constants.misc_constants as misc_constants
import pandas as pd
from constants.misc_constants import SQL_ALCH_CONFIG, ADMIN_EMAIL, ENGINE
import pandas as pd
from utils.parsers import parse_dates, validate_integers

def parse(sheet, date_format, database_table_name, decimal_point, thousands_seperator):
    
    integer_columns = ['Mass']
    date_columns = ['SamplingDate', 'SubmissionDate']
    primary_key = 'SubSampleID'
    
    if not decimal_point == 'not_relevant':
        raise Exception(f"Did not expect decimal numbers. Please contact contact {ADMIN_EMAIL} if you think this is a mistake.")

    # check for expected cols
    expected_columns = pd.read_sql(sql=f"SELECT * from {misc_constants.SQL_ALCH_CONFIG['schema_name']}.{database_table_name}", con=misc_constants.ENGINE).columns
    
    expected_columns = expected_columns[:-3] 
    
    
    # TODO: Make unit test with mock data.
    assert list(expected_columns) == list(sheet.columns), ("Column names and/or positions not as expected")

    num_of_not_null_rows = len(sheet[sheet[primary_key].notnull()]) # For drop testing

    # TODO: Delete after deployment and ask make uploader responsible.
    if primary_key in sheet.columns:
        sheet = sheet.dropna(axis='index', how='all', subset=[primary_key])
    else:
        raise Exception ("Upload failed. Expected column 'Robot TUBE barcode' not found. Are you sure you uploaded the correct spreadsheet?")
    
    # Drop test:
    if len(sheet) != num_of_not_null_rows:
        raise Exception(f'Error dropping null values. Contact {misc_constants.ADMIN_EMAIL} for help.')
    
    # Parse dates, throws error if formatting is wrong in the sheet
    sheet = parse_dates(sheet, date_columns=date_columns, date_format=date_format)
            
    sheet = validate_integers(sheet, integer_columns)
    
    return sheet