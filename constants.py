import os
from sqlalchemy import create_engine
from flask import Flask

ADMIN_EMAIL = "magnus.johannsen@sund.ku.dk"
UPLOADED_FILES = 'uploaded_sheets'
ALLOWED_EXTENSIONS = {'txt', 'html', 'csv'}
PARSED_SHEETS_FOLDER = 'parsed_sheets'
TEMP_FOLDER = 'temp'
ORIGINAL_FILES = 'original_sheets'
RUN_MODE = 'development'
RUN_MODE_OPTIONS = ['production', 'development']
STATIC_DIR = os.path.join(os.getcwd(), 'static')
PATH_TO_STANDARD_SHEETS = os.path.join(STATIC_DIR, 'example_sheets_online')

if os.environ.get('RUN_MODE'):
    RUN_MODE = os.environ.get('RUN_MODE').lower()
    if not RUN_MODE in RUN_MODE_OPTIONS:
        raise Exception(f'Unknown value for RUN_MODE')

MANUAL = os.path.join('latest_manual', os.listdir('latest_manual')[0])

EMAIL_SENDER = 'cgg.metadb.ui.website@gmail.com'

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

pw = os.environ.get('DB_PASSWORD')

if RUN_MODE == 'production':
    DATABASE_CONFIG = {
        'host': 'dandyweb01fl',
        'database': 'aedna_metadata_test',
        'port': '5432',
        'user': 'upload_user',
        'password': pw,
        'schema_name': 'test_1'
    }

elif RUN_MODE == 'development':
    DATABASE_CONFIG = {
        'host': 'dandyweb01fl',
        'database': 'aedna_metadata_test',
        'port': '5432',
        'user': 'upload_user',
        'password': pw,
        'schema_name': 'test_1'
    }

DATABASE_CONFIG_2 = {
    'host': DATABASE_CONFIG['host'],
    'dbname': DATABASE_CONFIG['database'],
    'port': DATABASE_CONFIG['port'],
    'user': DATABASE_CONFIG['user'],
    'password': DATABASE_CONFIG['password'],
}

DATABASE_CONFIG_READ_ONLY = {
    'host': DATABASE_CONFIG['host'],
    'dbname': DATABASE_CONFIG['database'],
    'port': DATABASE_CONFIG['port'],
    'user': 'read_user',
    'password': DATABASE_CONFIG['password'],
}

ENGINE = create_engine(
    f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}")

ENGINE_READ_ONLY = create_engine(
    f"postgresql://{DATABASE_CONFIG_READ_ONLY['user']}:{DATABASE_CONFIG_READ_ONLY['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}")

SHEET_TYPES = {
    'field_sample': 'Field samples',
    'edna_archive_sample': 'eDNA archive sampling',
    'edna_robot_sample': 'eDNA robot sampling',
    'edna_wetlab_report': 'eDNA Wet lab final report',
    'adna_wetlab_report': 'aDNA Wet lab final report',
    'cgg_sediment_water': 'CGG Sediment Water',
    'cgg_animal_plant': 'CGG Animal Plant',
    'lane_barcode_html': 'Lane Barcode HTML',
    'seq_sample_sheet': 'Sequencing Center Sample Sheet'
}

FILE_EXTENSIONS = {
    'field_sample': '.xlsx',
    'edna_archive_sample': '.xlsx',
    'edna_robot_sample': '.xlsx',
    'edna_wetlab_report': '.xlsx',
    'adna_wetlab_report': '.xlsx',
    'cgg_sediment_water': '.xlsx',
    'cgg_animal_plant': '.xlsx',
    'lane_barcode_html': '.html',
    'seq_sample_sheet': '.xlsx'
}

DB_GENERATED_COLUMNS = {'top_unknown_seq_barcodes': ['uid']}

TABLE_SPLITTER = {
    'field_sample': ['field_sample'],
    'edna_archive_sample': ['edna_archive_sample'],
    'edna_robot_sample': ['edna_robot_sample'],
    'edna_wetlab_report': ['edna_wetlab_report'],
    'adna_wetlab_report': ['adna_wetlab_report'],
    'cgg_sediment_water': ['cgg_sediment_water'],
    'cgg_animal_plant': ['cgg_animal_plant'],
    'lane_barcode_html': ['flowcell', 'top_unknown_seq_barcodes'],
    'seq_sample_sheet': ['seq_sample_sheet']
}


# Sheets that are split into multiple tables:
# Value: Tables in the database that the sheet is split into
MULTI_TABLE_SHEETS = {'lane_barcode_html': ['flowcell', 'top_unknown_seq_barcodes']}

ALLOWED_DATE_FORMATS = ['YYYY-MM-DD', 'DD-MM-YYYY', 'DD/MM/YYYY', 'YYYY/MM/DD', 'My data doesn\'t contain dates']

COLUMNS = {'field_sample':
               {'float_columns':
                    []}}

POSTGRES_TYPES = {'floating_point': ['double precision', 'numeric', 'real', 'decimal', 'float4', 'float8', 'float'],
                  'integer': ['smallint', 'integer', 'bigint', 'int', 'int2', 'int4', 'int8'],
                  'date': ['date', 'timestamptz', 'timestamp', 'time_stamp', 'timestamp with time zone',
                           'timestamp without time zone'],
                  'int_range': ['int4range', 'int8range']}

AUTO_GENERATED_COLUMNS = ['database_insert_by', 'from_spreadsheet', 'database_insert_datetime_utc', 'uid', 'database_insert_date_utc', 'upload_uuid']


DB_CHARACTER_ENCODING = 'UTF-8'


COLUMN_TRANSLATER = {'ArchiveSampleID': 'Archive Sample ID'}