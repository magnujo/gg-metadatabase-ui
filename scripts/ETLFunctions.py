import os
import pandas as pd
import numpy as np
import re
import locale
from utils.parsers import parse_dates, parse_floats
import constants
from constants import engine, database_config, database_config2

def clean_up(tsv_file_path, database_table_name, date_format, decimal_point, 
             thousands_seperator):
    
    sheet = pd.read_csv(tsv_file_path, sep='\t', encoding='utf_16', dtype=str)
    
    if database_table_name == 'archive_sample':
        print("check1")        
        sheet = parse_archive_sample(tsv_file_path, date_format, decimal_point, thousands_seperator)

    elif database_table_name == 'robot_sample':
        
        l1 = len(sheet[sheet["Robot TUBE barcode"].notnull()]) # For drop testing

        if 'Robot TUBE barcode' in sheet.columns:
            sheet = sheet.dropna(axis='index', how='all', subset=["Robot TUBE barcode"])
        else:
            raise Exception ("Upload failed. Expected column 'Robot TUBE barcode' not found. Are you sure you uploaded the correct spreadsheet?")
        
        # Drop test:
        if len(sheet) != l1:
            raise Exception(f'Error dropping null values. Contact {constants.admin_email} for help.')
        
        if 'Lab assistant (initials)' in sheet.columns:
            sheet = sheet.rename(columns={'Lab assistant (initials)': 'Lab assistant (KU ID(s seperated by semicolon))'})
        if 'Submitter\n(initials)' in sheet.columns:
            sheet = sheet.rename(columns={'Submitter\n(initials)': 'Submitter(KU ID(s seperated by semicolon))'})
        
    elif database_table_name == 'edna_wetlab_report':
       
        pass
    
    elif database_table_name == 'adna_wetlab_report':
        pass

    elif database_table_name == 'cgg_sediment':
        pass

    elif database_table_name == 'cgg_animal_plant':
        pass

    elif database_table_name == 'field_sample':
        pass

    else:
        raise Exception(f'No table named {database_table_name}')

    # Date parsing
    # Dates are pased as follows with pd.to_datetime:    

    # 1  pd.to_datetime(arg='9-7-8', dayfirst=True) is parsed as: day: 9, month: 7, year: 2008 
    # 2  pd.to_datetime(arg='9-7-8', dayfirst=False) is parsed as: day: 7, month: 9, year: 2008 
    # 3  pd.to_datetime(arg='9-7-8', yearfirst=True) is parsed as: day: 8, month: 7, year: 2009 
    # 4  pd.to_datetime(arg='2009-7-8', dayfirst=True) is parsed as: day: 7, month: 8, year: 2009 
    # 5  pd.to_datetime(arg='2009-7-8', dayfirst=False) is parsed as: day: 8, month: 7, year: 2009 
    # 6  pd.to_datetime(arg='2009-7-8', yearfirst=True) is parsed as: day: 8, month: 7, year: 2009 
    # 7  pd.to_datetime(arg='9-7-2008', dayfirst=True) is parsed as: day: 9, month: 7, year: 2008 
    # 8  pd.to_datetime(arg='9-7-2008', dayfirst=False) is parsed as: day: 7, month: 9, year: 2008 
    # 9  pd.to_datetime(arg='9-7-2008', yearfirst=True) is parsed as: day: 7, month: 9, year: 2008 
    
    # return format: ISO8601
    
    # TODO: Should be done in the seperate sheet parsing functions, to make it specific to each sheet
    # # Date format validation and converting to datetime:
    date_columns = sheet.columns[sheet.columns.str.lower().str.contains('date')]
    if date_format == 'ymd':
        for ele in date_columns:
                sheet[ele] = pd.to_datetime(sheet[ele], format='ISO8601').astype('datetime64[ns]')
    elif date_format == 'dmy':
        for ele in date_columns:
                sheet[ele] = pd.to_datetime(sheet[ele], format='%d-%m-%Y %H:%M:%S').astype('datetime64[ns]')
    else: 
        raise Exception('No date format chosen, try again.')

    return sheet;
    #return(sheet)
    # return len(sheet)

    

def parse_archive_sample(file_path, date_format, decimal_point, thousands_seperator):
    
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
    
    expected_columns = pd.read_sql(sql=f"SELECT * from {database_config['schema_name']}.archive_sample", con=engine).columns
    
    expected_columns = expected_columns[:-3] 
    expected_columns2 = expected_columns.copy().drop('SampledBy2')
    
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
    
