import os
import pandas as pd
import numpy as np
import re

    
def clean_up(tsv_file_path, database_table_name):
    sheet = pd.read_csv(tsv_file_path, sep='\t', encoding='utf_16')
    sheet = sheet.dropna(axis='index', how='all')

    if database_table_name == 'archive_sample':
        
        # For drop testing:
        l1 = len(sheet[sheet['Archive TUBE barcode'].notnull()])

        if 'Archive TUBE barcode' in sheet.columns:
            sheet = sheet.dropna(axis='index', how='all', subset=['Archive TUBE barcode'])
        else:
            raise Exception ("Upload failed. Expected column 'Archive TUBE barcode' not found. Are you sure you uploaded the correct spreadsheet?")
            
        if 'Sampled by \n(KU-ID)' in sheet.columns:
            sheet = sheet.rename(columns={'Sampled by \n(KU-ID)': 'Sampled by 1 (initials)'})
            sheet['Sampled by 2 (initials)'] = np.nan
            sheet.insert(sheet.columns.get_loc('Sampled by 1 (initials)')+1, 'Sampled by 2 (initials)', sheet.pop('Sampled by 2 (initials)'))
        if 'Submitter\n(KU-ID)' in sheet.columns:
            sheet = sheet.rename(columns={'Submitter\n(KU-ID)': 'Submitter\n(initials)'})
        if 'Remarks from sampling (real Calibration tape depth)' in sheet.columns:
            sheet = sheet.rename(columns={'Remarks from sampling (real Calibration tape depth)': 'Remarks from sampling (optional)'})
        
    elif database_table_name == 'robot_sample':
        
        l1 = len(sheet[sheet["Robot TUBE barcode"].notnull()]) # For drop testing

        if 'Robot TUBE barcode' in sheet.columns:
            sheet = sheet.dropna(axis='index', how='all', subset=["Robot TUBE barcode"])
        else:
            raise Exception ("Upload failed. Expected column 'Robot TUBE barcode' not found. Are you sure you uploaded the correct spreadsheet?")
        
        # Drop test:
        if len(sheet) != l1:
            raise Exception('Error dropping null values. Contact admin for help.')
        
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

    # Date format validation and converting to datetime:
    date_columns = sheet.columns[sheet.columns.str.lower().str.contains('date')]
    for ele in date_columns:
            sheet[ele] = pd.to_datetime(sheet[ele], format='ISO8601').astype('datetime64[ns]')

    return sheet;
    #return(sheet)
    # return len(sheet)



# Enables automatic formatting for archive samples (not done)
def clean_up_advanced(tsv_file_path, database_table_name):
    sheet = pd.read_csv(tsv_file_path, sep='\t', encoding='utf_16')
    sheet = sheet.dropna(axis='columns', how='all')
    sheet = sheet.dropna(axis='index', how='all')
    sheet.where(sheet.notnull(), None)


    if database_table_name == 'archive_sample':
        # For drop testing:
        l1 = len(sheet[sheet['Archive TUBE barcode'].notnull()])

        if 'Archive TUBE barcode' in sheet.columns:
            sheet = sheet.dropna(axis='index', how='all', subset=['Archive TUBE barcode'])
        else:
            raise Exception ("Upload failed. Expected column 'Archive TUBE barcode' not found. Are you sure you uploaded the correct spreadsheet?")
        
        # If the sheet is old, the two sampled by columns will be converted into one column.
        if 'Sampled by 1 (initials)' in sheet.columns and 'Sampled by 2 (initials)' in sheet.columns:
            sheet.apply(lambda row: row['Sampled by 1 (initials)'] + '; ' + row['Sampled by 2 (initials)'] if pd.notna(row['Sampled by 2 (initials)']) and bool(re.search(pattern=r'[a-zA-Z]{2,6}', string=row['Sampled by 2 (initials)'])) else row['Sampled by 1 (initials)'], axis=1)
            sheet = sheet.rename(columns={'Sampled by 1 (initials)': 'Sampled by (KU ID(\'s seperated by semicolon))'})
            sheet = sheet.drop('Sampled by 2 (initials)', axis=1)
        elif 'Sampled by (KU ID(\'s seperated by semicolon))':
            pass
        else:
            raise Exception('Didnt find expected columns Sampled by 2 (initials)')
            
        if 'Submitter\n(KU-ID)' in sheet.columns:
            sheet = sheet.rename(columns={'Submitter\n(KU-ID)': 'Submitter\n(initials)'})
        if 'Remarks from sampling (real Calibration tape depth)' in sheet.columns:
            sheet = sheet.rename(columns={'Remarks from sampling (real Calibration tape depth)': 'Remarks from sampling (optional)'})

        if 'Sampled by \n(KU-ID)' in sheet.columns:
            sheet = sheet.rename(columns={'Sampled by \n(KU-ID)': 'Sampled by 1 (initials)'})
            sheet['Sampled by 2 (initials)'] = np.nan
            sheet.insert(sheet.columns.get_loc('Sampled by 1 (initials)')+1, 'Sampled by 2 (initials)', sheet.pop('Sampled by 2 (initials)'))
        if 'Submitter\n(KU-ID)' in sheet.columns:
            sheet = sheet.rename(columns={'Submitter\n(KU-ID)': 'Submitter\n(initials)'})
        if 'Remarks from sampling (real Calibration tape depth)' in sheet.columns:
            sheet = sheet.rename(columns={'Remarks from sampling (real Calibration tape depth)': 'Remarks from sampling (optional)'})
        
    elif database_table_name == 'robot_sample':
        
        l1 = len(sheet[sheet["Robot TUBE barcode"].notnull()]) # For drop testing

        if 'Robot TUBE barcode' in sheet.columns:
            sheet = sheet.dropna(axis='index', how='all', subset=["Robot TUBE barcode"])
        else:
            raise Exception ("Upload failed. Expected column 'Robot TUBE barcode' not found. Are you sure you uploaded the correct spreadsheet?")
        
        # Drop test:
        if len(sheet) != l1:
            raise Exception('Error dropping null values. Contact admin for help.')
        
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

    # Date format validation and converting to datetime:
    date_columns = sheet.columns[sheet.columns.str.lower().str.contains('date')]
    for ele in date_columns:
            sheet[ele] = pd.to_datetime(sheet[ele], format='ISO8601').astype('datetime64[ns]')

    return sheet;
    #return(sheet)
    # return len(sheet)