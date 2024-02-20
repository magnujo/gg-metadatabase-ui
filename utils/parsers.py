import sys
import constants
import pandas as pd

def parse(file_path, 
          date_format, 
          database_table_name, 
          decimal_point, 
          thousands_seperator, 
          float_columns, 
          integer_columns, 
          range_columns,
          date_columns,
          boolean_columns,
          primary_key):
    
    
    float_columns = ['Latitude',
                     'Longitude',
                     'Sampling depth (discrete, cm)',
                     'Correlation depth (bottom, cm)',
                     'Correlation depth (top, cm)',
                     'Height above mean sea level (meters)']
    
    integer_columns = []
    
    date_columns = ['Sampling Date', 
                    'Storing date',
                    'Disposal date'
                    ]
    
    boolean_columns = []
    
    primary_key = 'Sample label (sticker)'  
    
    sheet = pd.read_csv(file_path, sep='\t', encoding='utf_16', dtype=str)
    
    if not '--production' in sys.argv:
        sheet = sheet.dropna(axis='index', how='all')

    # check for expected cols
    expected_columns = pd.read_sql(sql=f"SELECT * from {constants.DATABASE_CONFIG['schema_name']}.{database_table_name}", con=constants.ENGINE).columns
    
    expected_columns = expected_columns[:-3] 
   
    # TODO: Make unit test with mock data.
    assert list(expected_columns) == list(sheet.columns), ("Column names and/or positions not as expected")

    if '--production' not in sys.argv:
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
    # sheet = parse_booleans(sheet, boolean_columns)

    return sheet

def parse_dates(sheet, date_columns, date_format, soft=False):
    """
    Parse date columns in a Pandas DataFrame using specific date format.
    Dates are pased as follows with pd.to_datetime:    

    1  pd.to_datetime(arg='9-7-8', dayfirst=True)       = day: 9, month: 7, year: 2008 
    2  pd.to_datetime(arg='9-7-8', dayfirst=False)      = day: 7, month: 9, year: 2008 
    3  pd.to_datetime(arg='9-7-8', yearfirst=True)      = day: 8, month: 7, year: 2009 
    
    # IMPORTANT The below example shows that format should always be "mixed" if relying on dayfirst.
    # because no matter what a date will not have the month as the last digit.
    4  pd.to_datetime(arg='2009-7-8', dayfirst=True)    = day: 7, month: 8, year: 2009 
    4  pd.to_datetime(arg='2009-7-8', dayfirst=True, format="mixed)= day: 8, month: 7, year: 2009 
    
    5  pd.to_datetime(arg='2009-7-8', dayfirst=False)   = day: 8, month: 7, year: 2009 
    6  pd.to_datetime(arg='2009-7-8', yearfirst=True)   = day: 8, month: 7, year: 2009 
    7  pd.to_datetime(arg='9-7-2008', dayfirst=True)    = day: 9, month: 7, year: 2008 
    8  pd.to_datetime(arg='9-7-2008', dayfirst=False)   = day: 7, month: 9, year: 2008 
    9  pd.to_datetime(arg='9-7-2008', yearfirst=True)   = day: 7, month: 9, year: 2008 
    
    Parameters:
    - sheet (pandas.DataFrame): The DataFrame containing the data.
    - date_columns (list): A list of column names to be parsed as dates.
    - date_format (str): The format of the date columns. Supported formats are 'ymd' and 'dmy'.

    Returns:
    - pandas.DataFrame: The DataFrame with the specified columns parsed as datetime objects (ISO8601 format).

    Raises:
    - Exception: If an unsupported date format is provided.

    Example:
    ```python
    import pandas as pd

    data = {'Date1': ['2022-01-01', '2022-01-02'], 'Date2': ['10-01-2022 12:30:45', '11-01-2022 14:45:30']}
    df = pd.DataFrame(data)

    # Parse dates with 'ymd' format
    result_df = parse_dates(df, date_columns=['Date1', 'Date2'], date_format='ymd')
    ```
    """
    
    # Might work good for more than one format:
    
    # date1 = pd.to_datetime(df['date'], errors='coerce', format='%Y-%m-%d')
    # date2 = pd.to_datetime(df['date'], errors='coerce', format='%d.%m.%Y')
    # sheet['date'] = date1.fillna(date2)
    try:
        if soft:
            if date_format == 'YYYY-MM-DD':
                for ele in date_columns:
                    sheet[ele] = pd.to_datetime(sheet[ele], format='mixed', yearfirst=True)
                    sheet[ele] = sheet[ele].astype('datetime64[ns]')
            elif date_format == 'DD-MM-YYYY':
                for ele in date_columns:
                    sheet[ele] = pd.to_datetime(sheet[ele], format='mixed', dayfirst=True)
                    sheet[ele] = sheet[ele].astype('datetime64[ns]')
            else: 
                raise Exception('No date format chosen, try again.')
        else:
            
            if date_format == 'YYYY-MM-DD':
                for ele in date_columns:
                    sheet[ele] = pd.to_datetime(sheet[ele], format='ISO8601')
                    sheet[ele] = sheet[ele].astype('datetime64[ns]')
            elif date_format == 'DD-MM-YYYY':
                for ele in date_columns:
                    print(sheet[ele].dtype)
                    sheet[ele] = pd.to_datetime(sheet[ele], format='%d-%m-%Y')
                    sheet[ele] = sheet[ele].astype('datetime64[ns]')
            elif date_format == 'DD/MM/YYYY':
                for ele in date_columns:
                    print(sheet[ele].dtype)
                    sheet[ele] = pd.to_datetime(sheet[ele], format='%d/%m/%Y')
                    sheet[ele] = sheet[ele].astype('datetime64[ns]')
            elif date_format == 'YYYY/MM/DD':
                for ele in date_columns:
                    print(sheet[ele].dtype)
                    sheet[ele] = pd.to_datetime(sheet[ele], format='%Y/%m/%d')
                    sheet[ele] = sheet[ele].astype('datetime64[ns]')
            else: 
                raise Exception('No date format chosen, try again.')
    except Exception:
        raise Exception(f"Found time data in column {ele} that does not match chosen date format {date_format}.")
     
    return sheet

#TODO: What if not_relevant?
# Converts to float and throws error if string is not a float (for example if it contains thousands seperators)
def parse_floats(sheet, float_columns, decimal_point, thousands_seperator):
    
    '''
    Parses numeric data based on user input (decimal_point, thousands_seperator). Thousands seperator gets removed
    no matter what the user input is, because they are not used in the database. Decimal points gets converted to "." no matter what
    the user input it, because this is what the database accepts. It also checks that no unexpected decimal
    points or thousands seperators are found in the columns. For example if you if you input "," as decimal point
    and "not_relevant" as thousands seperator, it checks for any "." in the data and throws an error if it finds any.


    Parameters:
    - sheet (pandas.DataFrame): The DataFrame containing the data.
    - numeric_columns (list): A list of column names to be parsed as numeric values.
    - decimal_point (str): The character used as the decimal point in the numeric data.
    - thousands_separator (str): The character used as the thousands separator in the numeric data.

    Returns:
    - pandas.DataFrame: The DataFrame with the specified columns parsed as float values.

    Raises:
    - Exception: If inconsistencies are found in data and user input, or if expected columns are missing.

    Example:
    ```python
    import pandas as pd

    data = {'Amount1': ['1,000.25', '2,500.50'], 'Amount2': ['3.75', '4.80']}
    df = pd.DataFrame(data)

    # Parse numeric values with ',' as thousands separator and '.' as decimal point
    result_df = parse_numerics(df, numeric_columns=['Amount1', 'Amount2'], decimal_point='.', thousands_separator=',')
    ```
    '''
    
    for ele in float_columns:
        if ele in sheet.columns:
        
            # Checks for inconsistencies in data and user input
            match (decimal_point, thousands_seperator):
            
                case ("not_relevant", ","):
                    bad_rows = sheet[ele].apply(str).str.contains(".", regex=False)
                    if bad_rows.any():
                        raise Exception(f"Found . (period) in numeric data in the following rows, \
                                        but not in user input: \n \n {list(sheet[bad_rows].index + 1)}")
                    else:
                        sheet[ele] = sheet[ele].str.replace(thousands_seperator, "", regex=False)
                        
                case (",", "not_relevant"):
                    bad_rows = sheet[ele].apply(str).str.contains(".", regex=False)
                    if bad_rows.any():
                        raise Exception(f"Found . (period) in numeric data in the following rows, \
                                        but not in user input: \n \n {list(sheet[bad_rows].index + 1)}")
                    else:
                        sheet[ele] = sheet[ele].str.replace(decimal_point, ".", regex=False)
                        
                        
                case (".", "not_relevant"):
                    bad_rows = sheet[ele].apply(str).str.contains(",", regex=False)
                    if bad_rows.any():
                        raise Exception(f"Found , (comma) in numeric data in the following rows, \
                                        but not in user input: \n \n {list(sheet[bad_rows].index + 1)}")
                    
                case ("not_relevant", "."):
                    # returns the rows that contains ","
                    bad_rows = sheet[ele].apply(str).str.contains(",", regex=False)
                    if bad_rows.any():
                        raise Exception(f"Found , (comma) in numeric data in the following rows, \
                                        but not in user input: \n \n {list(sheet[bad_rows].index + 1)}")
                    else:
                        sheet[ele] = sheet[ele].str.replace(thousands_seperator, "")

                case ("not_relevant", "not_relevant"):
                    bad_rows = sheet[ele].apply(str).str.contains("\.|,", regex=True)
                    if bad_rows.any():
                        raise Exception(f"Found , (comma) or . (period) in numeric data in the following rows, \
                                        but not in user input: \n \n {list(sheet[bad_rows].index + 1)}")
                        
                case (",", "."):
                    sheet[ele] = sheet[ele].str.replace(thousands_seperator, "", regex=False)
                    sheet[ele] = sheet[ele].str.replace(decimal_point, ".", regex=False)
                        
                case (".", ","):
                    sheet[ele] = sheet[ele].str.replace(thousands_seperator, "", regex=False)
                
                case _:
                    raise Exception(f"case _ reached in {parse_floats.__name__}. Contact database admin.")
            
            sheet[ele] = sheet[ele].astype('float64')
            
        else:
            raise Exception(f"Did not find expected numeric column {ele} in input. \
                                Please make sure the format of your spreadsheet matches \
                                the the example sheet found on the upload website.\
                                Contact admin at {constants.ADMIN_EMAILS}")

    return sheet

# TODO: Test this function with unit test.
def validate_integers(sheet, integer_columns):
    
    for ele in integer_columns:
        if ele in sheet.columns:
            bad_rows = sheet[ele].apply(str).str.contains("[^\d]", regex=True)
            if bad_rows.any():
                raise Exception(f"Found non integer in expected integer data in the following rows\
                                : \n \n {list(sheet[bad_rows].index + 2)}")
            
            sheet[ele] = sheet[ele].astype('int64')
            
        else:
            raise Exception(f"Did not find expected numeric column {ele} in input. \
                                Please make sure the format of your spreadsheet matches \
                                the the example sheet found on the upload website.\
                                Contact admin at {constants.ADMIN_EMAILS}")
    return sheet
