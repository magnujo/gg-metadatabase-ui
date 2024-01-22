import pandas as pd
import constants

def parse_dates(sheet, date_columns, date_format):
    if date_format == 'ymd':
        for ele in date_columns:
                sheet[ele] = pd.to_datetime(sheet[ele], format='ISO8601')
                sheet[ele] = sheet[ele].astype('datetime64[ns]')
    elif date_format == 'dmy':
        for ele in date_columns:
                sheet[ele] = pd.to_datetime(sheet[ele], format='%d-%m-%Y %H:%M:%S')
                sheet[ele] = sheet[ele].astype('datetime64[ns]')
    else: 
        raise Exception('No date format chosen, try again.')
    return sheet

#TODO: What if not_relevant?
# Converts to float and throws error if string is not a float (for example if it contains thousands seperators)
def parse_floats(sheet, float_columns, decimal_point, thousands_seperator):
    
    for ele in float_columns:
        if ele in sheet.columns:
        
            # Checks for inconsistencies in data and user input
            match (decimal_point, thousands_seperator):
            
                case ("not_relevant", ","):
                    bad_rows = sheet[ele].apply(str).str.contains(".", regex=False)
                    if bad_rows.any():
                        raise Exception(f"Found . (period) in numeric data in the following rows, \
                                        but not in user input: \n \n {list(sheet[bad_rows].index + 2)}")
                    else:
                        sheet[ele] = sheet[ele].str.replace(thousands_seperator, "", regex=False)
                        
                case (",", "not_relevant"):
                    bad_rows = sheet[ele].apply(str).str.contains(".", regex=False)
                    if bad_rows.any():
                        raise Exception(f"Found . (period) in numeric data in the following rows, \
                                        but not in user input: \n \n {list(sheet[bad_rows].index + 2)}")
                    else:
                        sheet[ele] = sheet[ele].str.replace(decimal_point, ".", regex=False)
                        
                case (".", "not_relevant"):
                    bad_rows = sheet[ele].apply(str).str.contains(",", regex=False)
                    if bad_rows.any():
                        raise Exception(f"Found , (comma) in numeric data in the following rows, \
                                        but not in user input: \n \n {list(sheet[bad_rows].index + 2)}")
                    
                case ("not_relevant", "."):
                    bad_rows = sheet[ele].apply(str).str.contains(",", regex=False)
                    if bad_rows.any():
                        raise Exception(f"Found , (comma) in numeric data in the following rows, \
                                        but not in user input: \n \n {list(sheet[bad_rows].index + 2)}")
                    else:
                        sheet[ele] = sheet[ele].str.replace(thousands_seperator, "")

                case ("not_relevant", "not_relevant"):
                    bad_rows = sheet[ele].apply(str).str.contains("\.|,", regex=True)
                    if bad_rows.any():
                        raise Exception(f"Found , (comma) or . (period) in numeric data in the following rows, \
                                        but not in user input: \n \n {list(sheet[bad_rows].index + 2)}")
                        
                case (",", "."):
                    sheet[ele] = sheet[ele].str.replace(thousands_seperator, "", regex=False)
                    sheet[ele] = sheet[ele].str.replace(decimal_point, ".", regex=False)
                        
                case (".", ","):
                    sheet[ele] = sheet[ele].str.replace(thousands_seperator, "", regex=False)
                
                case _:
                    raise Exception("case _ reached in parse floats. Contact database admin.")
                        
            sheet[ele] = sheet[ele].astype(float)   
            
        else:
            raise Exception(f"Did not find expected float column {ele} in input. Contact admin at {constants.admin_email}")

    return sheet