import os
import pandas as pd
import numpy as np
import re
import locale
import constants
from constants import ENGINE, DATABASE_CONFIG, DATABASE_CONFIG_2
from utils import cgg_animal_plant_parser, robot_sample_sheet_parser, archive_sample_sheet_parser, cgg_sediment_water_parser
from utils import edna_wetlab_report_parser, adna_wetlab_report_parser, field_sample_internal_parser

def clean_up(tsv_file_path, database_table_name, date_format, decimal_point, 
             thousands_seperator):
    
    if database_table_name == 'archive_sample':
        sheet = archive_sample_sheet_parser.parse(tsv_file_path, date_format, decimal_point, thousands_seperator)

    elif database_table_name == 'robot_sample':
        print("Robot sample")
        sheet = robot_sample_sheet_parser.parse(file_path=tsv_file_path, 
                                       date_format=date_format, 
                                       database_table_name=database_table_name,
                                       decimal_point=decimal_point,
                                       thousands_seperator=thousands_seperator)
        
    elif database_table_name == 'edna_wetlab_report':
        sheet = edna_wetlab_report_parser.parse(file_path=tsv_file_path, 
                                       date_format=date_format, 
                                       database_table_name=database_table_name,
                                       decimal_point=decimal_point,
                                       thousands_seperator=thousands_seperator)
    
    elif database_table_name == 'adna_wetlab_report':
        sheet = adna_wetlab_report_parser.parse(file_path=tsv_file_path, 
                                                        date_format=date_format, 
                                                        database_table_name=database_table_name,
                                                        decimal_point=decimal_point,
                                                        thousands_seperator=thousands_seperator)

    elif database_table_name == 'cgg_sediment_water':
        sheet = cgg_sediment_water_parser.parse(file_path=tsv_file_path, 
                                                    date_format=date_format, 
                                                    database_table_name=database_table_name,
                                                    decimal_point=decimal_point,
                                                    thousands_seperator=thousands_seperator)

    elif database_table_name == 'cgg_animal_plant':
        sheet = cgg_animal_plant_parser.parse(file_path=tsv_file_path, 
                                                        date_format=date_format, 
                                                        database_table_name=database_table_name,
                                                        decimal_point=decimal_point,
                                                        thousands_seperator=thousands_seperator)

    elif database_table_name == 'field_sample_internal':
        sheet = field_sample_internal_parser.parse(file_path=tsv_file_path, 
                                                        date_format=date_format, 
                                                        database_table_name=database_table_name,
                                                        decimal_point=decimal_point,
                                                        thousands_seperator=thousands_seperator)

    else:
        raise Exception(f'No table named {database_table_name}')

    return sheet;
    #return(sheet)
    # return len(sheet)


    
