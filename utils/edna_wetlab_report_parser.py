from utils import parsers
import constants
import pandas as pd
from constants import DATABASE_CONFIG, ADMIN_EMAILS, ENGINE
import pandas as pd
from utils.parsers import parse_dates, parse_floats, validate_integers

def parse(file_path, date_format, database_table_name, decimal_point, thousands_seperator):
    
    float_columns = ['eDNA Concentration (ng/µL)',
                     'Library Concentration (nM)',
                     'Library Peak Size (bp)',
                     'Library Leftover Volume  (µL)',
                     'Ct',
                     'DNA Pooled (nmol)']
    
    integer_columns = ['No',
                       'Total Sample Quantity',
                       'PCR Cycle',
                       'Expected Sequencing Data (MB)']
    
    date_columns = ['Order Date', 
                    'Lysis Date',
                    'Cleanup Date',
                    'Library Start Date',
                    'qPCR Date',
                    'Indexing PCR Date',
                    'Library Cleanup Date',
                    'Library QC Date',
                    'Submitting Date',
                    'Project Done Date']
    
    primary_key = 'eDNA ID'
        
    # read sheet
    sheet = pd.read_csv(file_path, sep='\t', encoding='utf_16', dtype=str)
    
    # TODO: Delete after deployment and ask make uploader responsible.
    sheet = sheet.dropna(axis='index', how='all')
    #sheet = sheet.drop(columns=sheet.columns[sheet.columns.str.contains('^Unnamed')])

    # check for expected cols
    expected_columns = pd.read_sql(sql=f"SELECT * from {constants.DATABASE_CONFIG['schema_name']}.{database_table_name}", con=constants.ENGINE).columns
    
    expected_columns = expected_columns[:-3] 
    
    print(sheet.columns)
    print(expected_columns)
    
    # TODO: Make unit test with mock data.
    assert list(expected_columns) == list(sheet.columns), ("Column names and/or positions not as expected")

    # For drop testing. Counts the number of rows where primary key is not null.
    num_of_not_null_rows = len(sheet[sheet[primary_key].notnull()]) 

    # TODO: Delete after deployment and ask make uploader responsible.
    if primary_key in sheet.columns:
        sheet = sheet.dropna(axis='index', how='all', subset=[primary_key])
    else:
        raise Exception (f"Upload failed. Expected column {primary_key} not found. Contact {constants.ADMIN_EMAILS} if you think this is a mistake")
    
    # Drop test:
    if len(sheet) != num_of_not_null_rows:
        raise Exception(f'Error dropping null values. Contact {constants.ADMIN_EMAILS} for help.')
    
    # Parse dates, throws error if formatting is wrong in the sheet
    sheet = parse_dates(sheet, date_columns=date_columns, date_format=date_format)
            
    sheet = parse_floats(sheet, float_columns, decimal_point, thousands_seperator)
    sheet = validate_integers(sheet, integer_columns)

    return sheet