import os
import pandas as pd
from sqlalchemy import create_engine
import numpy as np
import re
from glob import glob
import scripts.ETLFunctions as etl
import psycopg2 as psycop
import sys
from datetime import datetime

file_path = r'c:\Users\glj523\Downloads\sheets\archive sample\eDNA_Archive_sampling_(231201_NKL_Hollerup_interglacial).txt'
database_table_name = 'archive_sample'
date_format = "ymd"
decimal_point = ","
thousands_seperator = 'not_relevant'

clean_sheet = etl.clean_up(tsv_file_path=file_path, 
                        database_table_name=database_table_name, 
                        date_format=date_format,
                        decimal_point=decimal_point,
                        thousands_seperator=thousands_seperator)