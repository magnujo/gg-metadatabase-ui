import os
import pandas as pd
import numpy as np
import re

    
def clean_up(tsv_file_path, database_table_name, date_format):
    sheet = pd.read_csv(tsv_file_path, sep='\t', encoding='utf_16', dtype=str)
    sheet = sheet.dropna(axis='index', how='all')


    if database_table_name == 'archive_sample':
        
        # dtypes = {'Archive rack position': str,
        #           'Archive RACK name\n(eg. ARack0052)': str,
        #           'Archive RACK barcode': str,
        #           'Archive TUBE barcode': str,
        #           'Depth sampled (tape, cm)': float,
        #           'Organic content     (High /Low)': str,
        #           'Surface exposed? (ie Back wall hit?)\n(Yes / No)': str,
        #           'Remarks from sampling (optional)': str,
        #           'Sampled by 1 (initials)': str,
        #           'Sampled by 2 (initials)': str,
        #           'Sampled date (yyyy-mm-dd)': str,
        #           'No': int,
        #           'Submitter\n(initials)': str,
        #           'Submission date (yyyy-mm-dd)': str,
        #           'Core segment ID\n(fx ISL23_019_02A)': str,
        #           'Ordered depth (Calibration tape, cm)': str,
        #           'Notes from submitter (optional)': str
        #           }
                
        
        # TODO: Delete after deployment and ask make uploader responsible.
        sheet = sheet.dropna(axis='index', how='all')

        sheet['Depth sampled (tape, cm)'] = sheet['Depth sampled (tape, cm)'].astype(float)
        sheet['No'] = sheet['No'].astype(float)

        # For testing that the drops are made correctly:
        l1 = len(sheet[sheet['Archive TUBE barcode'].notnull()])

        if 'Archive TUBE barcode' in sheet.columns:
            # TODO: Remove dropna before deployment. Make users responsible for input to db.
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
    
    # # Date format validation and converting to datetime:
    date_columns = sheet.columns[sheet.columns.str.lower().str.contains('date')]
    if date_format == 'year_first':
        for ele in date_columns:
                sheet[ele] = pd.to_datetime(sheet[ele], format='ISO8601').astype('datetime64[ns]')
    elif date_format == 'day_first':
        for ele in date_columns:
                sheet[ele] = pd.to_datetime(sheet[ele], format='ISO8601', dayfirst=True).astype('datetime64[ns]')
    else: 
        raise Exception;

    return sheet;
    #return(sheet)
    # return len(sheet)



