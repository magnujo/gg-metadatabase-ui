from utils import parsers
import constants
import pandas as pd
from constants import DATABASE_CONFIG, ADMIN_EMAILS, ENGINE
import pandas as pd
from utils.parsers import parse_dates, validate_integers

def parse(file_path, date_format, database_table_name, decimal_point, thousands_seperator):
    
    integer_columns = ['Mass']
    date_columns = ['SamplingDate', 'SubmissionDate']
    primary_key = 'SubSampleID'
    
    if not decimal_point == 'not_relevant':
        raise Exception(f"Did not expect decimal numbers. Please contact contact {ADMIN_EMAILS} if you think this is a mistake.")
    
    # read sheet
    sheet = pd.read_csv(file_path, sep='\t', encoding='utf_16', dtype=str)
    
    # TODO: Delete after deployment and ask make uploader responsible.
    sheet = sheet.dropna(axis='index', how='all')
    sheet = sheet.drop(columns=sheet.columns[sheet.columns.str.contains('^Unnamed')])

    # check for expected cols
    expected_columns = pd.read_sql(sql=f"SELECT * from {constants.DATABASE_CONFIG['schema_name']}.{database_table_name}", con=constants.ENGINE).columns
    
    expected_columns = expected_columns[:-3] 
    
    print(sheet.columns)
    print(expected_columns)
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
        raise Exception(f'Error dropping null values. Contact {constants.ADMIN_EMAILS} for help.')
    
    # Parse dates, throws error if formatting is wrong in the sheet
    sheet = parse_dates(sheet, date_columns=date_columns, date_format=date_format)
            
    sheet = validate_integers(sheet, integer_columns)
    
    return sheet