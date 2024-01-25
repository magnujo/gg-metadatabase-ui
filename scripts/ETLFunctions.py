import os
import pandas as pd
import numpy as np
import re
import locale
import constants
from constants import ENGINE, DATABASE_CONFIG, DATABASE_CONFIG_2
from utils import robot_sample_sheet_parser, archive_sample_sheet_parser, edna_wetlab_report_parser

def clean_up(tsv_file_path, database_table_name, date_format, decimal_point, 
             thousands_seperator):
    
    if database_table_name == 'archive_sample':
        sheet = archive_sample_sheet_parser.parse(tsv_file_path, date_format, decimal_point, thousands_seperator)

    elif database_table_name == 'robot_sample':
        print("Robot sample")
        robot_sample_sheet_parser.parse(file_path=tsv_file_path, 
                                       date_format=date_format, 
                                       database_table_name=database_table_name,
                                       decimal_point=decimal_point,
                                       thousands_seperator=thousands_seperator)
        
    elif database_table_name == 'edna_wetlab_report':
        edna_wetlab_report_parser.parse(file_path=tsv_file_path, 
                                       date_format=date_format, 
                                       database_table_name=database_table_name,
                                       decimal_point=decimal_point,
                                       thousands_seperator=thousands_seperator)
    
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


    
