from constants import DATABASE_CONFIG, ADMIN_EMAILS, ENGINE
import pandas as pd
from utils.parsers import parse_dates, parse_floats
import numpy as np

def parse(file_path, date_format, decimal_point, thousands_seperator):
    
    
    dtypes = {'ArchiveSampleID': str,
                'PositionInRack': str,
                'RackName': str,
                'RackID': str,
                'BulkSampleID': str,
                'DepthSampledCalTape': float,
                'DepthOrderedCalTape': str,
                'OrganicContent': str,
                'SurfaceExposed': str,
                'RemarksArchiveSampling': str,
                'SampledBy1': str,
                'SampledBy2': str,
                'SamplingDate': str,
                'Submitter': str,
                'SubmissionDate': str,
                'NotesSubmitter': str}

    # sheet = pd.read_csv(file_path, sep='\t', encoding='utf_16', dtype=dtypes, thousands='.', decimal=',')
    sheet = pd.read_csv(file_path, sep='\t', encoding='utf_16', dtype=str)
    
    expected_columns = pd.read_sql(sql=f"SELECT * from {DATABASE_CONFIG['schema_name']}.archive_sample", con=ENGINE).columns
    
    expected_columns = expected_columns[:-3] 
    expected_columns2 = expected_columns.copy().drop('SampledBy2')
    
    # TODO: Make unit test with mock data.
    assert list(expected_columns) == list(sheet.columns) or list(expected_columns2) == list(sheet.columns), ("Column names and/or positions not as expected")

    # Converts column names, if they are changes to KU ID format.
    if 'SampledBy' in sheet.columns:
        sheet = sheet.rename(columns={'SampledBy': 'SampledBy1'})
        sheet['SampledBy2'] = np.nan
        sheet.insert(sheet.columns.get_loc('SampledBy1')+1, 'SampledBy2', sheet.pop('SampledBy2'))
    elif 'SampleBy2' not in sheet.columns:
        #sheet = sheet.rename(columns={'SampledBy1': 'SampledBy'})
        sheet['SampledBy2'] = np.nan
        sheet.insert(sheet.columns.get_loc('SampledBy1')+1, 'SampledBy2', sheet.pop('SampledBy2'))
    if 'Submitter(KU-ID)' in sheet.columns:
        sheet = sheet.rename(columns={'Submitter(KU-ID)': 'Submitter'})
    
    # TODO: Delete after deployment and ask make uploader responsible.
    sheet = sheet.dropna(axis='index', how='all')
    
    # For testing that the drops are made correctly:
    l1 = len(sheet[sheet['ArchiveSampleID'].notnull()])

    # Drop all rows that does not contain ArchiveSampleID
    if 'ArchiveSampleID' in sheet.columns:
        print("dropping")
        # TODO: Remove dropna before deployment. Make users responsible for input to db.
        sheet = sheet.dropna(axis='index', how='all', subset=['ArchiveSampleID'])
    else:
        raise Exception ("Upload failed. Expected column 'ArchiveSampleID' not found. Are you sure you uploaded the correct spreadsheet?")
    assert l1 == len(sheet), "Dropna test failed"
    
    # Parse dates, throws error if formatting is wrong in the sheet
    date_columns = ['SubmissionDate', 'SamplingDate']
    sheet = parse_dates(sheet, date_columns=date_columns, date_format=date_format)

    # Convert float cols to float. Throws error if not a float.
    # sheet['DepthSampledCalTape'] = sheet['DepthSampledCalTape'].astype(float)
    
    float_cols = ['DepthSampledCalTape']
    sheet = parse_floats(sheet, float_cols, decimal_point, thousands_seperator)
        

    return sheet