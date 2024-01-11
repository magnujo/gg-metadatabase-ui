import os
import pandas as pd
import numpy as np
    
def clean_up(tsv_file_path, database_table_name):
    sheet = pd.read_csv(tsv_file_path, sep='\t', encoding='utf_16')
    sheet = sheet.dropna(axis='columns', how='all')
    sheet = sheet.dropna(axis='index', how='all')

    if database_table_name == 'archive_sample':
        # For drop testing:
        l1 = len(sheet[sheet['Archive TUBE barcode'].notnull()])
         
        sheet = sheet.dropna(axis='index', how='all', subset=['Archive TUBE barcode'])

        if 'Sampled by \n(KU-ID)' in sheet.columns:
            sheet = sheet.rename(columns={'Sampled by \n(KU-ID)': 'Sampled by 1 (initials)'})
            sheet['Sampled by 2 (initials)'] = np.nan
            sheet.insert(sheet.columns.get_loc('Sampled by 1 (initials)')+1, 'Sampled by 2 (initials)', sheet.pop('Sampled by 2 (initials)'))
        if 'Submitter\n(KU-ID)' in sheet.columns:
            sheet = sheet.rename(columns={'Submitter\n(KU-ID)': 'Submitter\n(initials)'})
        if 'Remarks from sampling (real Calibration tape depth)' in sheet.columns:
            sheet = sheet.rename(columns={'Remarks from sampling (real Calibration tape depth)': 'Remarks from sampling (optional)'})
        
    elif database_table_name == 'robot_sample':
        # For drop testing
        l1 = len(sheet[sheet["Robot TUBE barcode"].notnull()])

        if 'Robot TUBE barcode' in sheet.columns:
            sheet = sheet.dropna(axis='index', how='all', subset=["Robot TUBE barcode"])
        else:
            raise Exception ("Upload failed. Expected column 'Robot TUBE barcode' not found. Are you sure you uploaded the correct spreadsheet?")
        
        # Drop test:
        if len(sheet) != l1:
            raise Exception('Error dropping null values. Contact admin for help.')
        
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
            sheet[ele] = pd.to_datetime(sheet[ele], format='ISO8601')

    return sheet;
    #return(sheet)
    # return len(sheet)

        