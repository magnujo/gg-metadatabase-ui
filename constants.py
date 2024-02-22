import os
from sqlalchemy import create_engine
from flask import Flask


ADMIN_EMAILS = "magnus.johannsen@sund.ku.dk"
UPLOAD_FOLDER = 'uploaded_sheets'
ALLOWED_EXTENSIONS = {'txt'}
PARSED_SHEETS_FOLDER = 'parsed_sheets'
TEMP_FOLDER = 'temp'
ORIGINAL_FILES = 'orignal_sheets'
MANUAL = "Manual.pdf"

'''
Arguments you can use when starting the app
Development args are only allowed in development 
and production args are used for production (can also be used for development)

no_file_test: 
Skips the check that a file with the same name has already been uploaded

no_upload_test:
skips the test that the uploaded data equals the parsed sheet

production:
skips the dropping of null values. if used, the two others are not allowed.
'''
ALLOWED_COMMAND_LINE_ARGS = {'development': [],
                             'production': []}

DATABASE_CONFIG = {
    'host': 'dandyweb01fl',
    'database': 'aedna_metadata',
    'port': '5432',
    'user': 'upload_user',
    'password': 'Ce65r-l+!D04',
    'schema_name': 'test'
}

DATABASE_CONFIG_2 = {
    'host': DATABASE_CONFIG['host'],
    'dbname': DATABASE_CONFIG['database'],
    'port': DATABASE_CONFIG['port'],
    'user': DATABASE_CONFIG['user'],
    'password': DATABASE_CONFIG['password'],
}

ENGINE = create_engine(f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}")

SHEET_TYPES = {
    'field_sample_internal': 'Field sampling (internal)',
    'edna_archive_sample': 'eDNA archive sampling',
    'edna_robot_sample': 'eDNA robot sampling',
    'edna_wetlab_report': 'eDNA Wet lab final report',
    'adna_wetlab_report': 'aDNA Wet lab final report',
    'cgg_sediment_water': 'CGG Sediment Water',
    'cgg_animal_plant': 'CGG Animal Plant'
}

ALLOWED_DATE_FORMATS = ['YYYY-MM-DD', 'DD-MM-YYYY', 'DD/MM/YYYY', 'YYYY/MM/DD']

COLUMNS = {'field_sample_internal': 
    {'float_columns': 
        []}}

postgres_types = {'floating_point': ['double precision', 'numeric', 'real', 'decimal', 'float4', 'float8', 'float'],
                  'integer': ['smallint', 'integer', 'bigint', 'int', 'int2', 'int4', 'int8'],
                  'date': ['date', 'timestamptz', 'timestamp', 'time_stamp', 'timestamp with time zone', 'timestamp without timezone'],
                  'int_range': ['int4range', 'int8range']}


auto_generated_columns = ['database_insert_by', 'from_spreadsheet', 'database_insert_datetime_utc']

RUN_MODE = 'production'

RUN_MODE_OPTIONS = ['production', 'development']