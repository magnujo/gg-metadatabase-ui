from constants.db_connections import RUN_MODE_OPTIONS, pw
from constants.db_names.names import data
import os
from flask import Flask
import platform



VALIDATION_SCHEMA_LINKS = {"LIBRARY": 'https://raw.githubusercontent.com/SPAAM-community/AncientMetagenomeDir/master/ancientmetagenome-environmental/libraries/ancientmetagenome-environmental_libraries_schema.json',
                           "SAMPLE": 'https://raw.githubusercontent.com/SPAAM-community/AncientMetagenomeDir/master/ancientmetagenome-environmental/samples/ancientmetagenome-environmental_samples_schema.json'}


SESSION_DATA = "session_data"

if str(platform.system()) == "Windows":
    PATH_TO_MOUNT = os.path.join("N:", os.path.sep)
else:
    PATH_TO_MOUNT = os.path.join("/", "mnt")
    
GEO_DATA_NETWORK_DIR = os.path.join("SUN-GI-metadb-test", "Field Sample Geo Files")
GEO_DATA_NETWORK_DIR_DELETIONS = os.path.join("SUN-GI-metadb-test", "Deleted (DO NOT TOUCH)")
GEO_DATA_PROJECTS_DIR_PATH = os.path.join(PATH_TO_MOUNT, GEO_DATA_NETWORK_DIR, "Project specific files")
GEO_DATA_SAMPLES_DIR = os.path.join(PATH_TO_MOUNT, GEO_DATA_NETWORK_DIR, "Sample specific files")

ADMIN_EMAIL = "magnus.johannsen@sund.ku.dk"
UPLOADED_FILES = 'uploaded_sheets'
ALLOWED_EXTENSIONS = {'txt', 'html', 'csv'}
PARSED_SHEETS_FOLDER = 'parsed_sheets'
DELETED_SESSION_DATA = "deleted_session_data"
TEMP_FOLDER = 'temp'
ORIGINAL_FILES = 'original_sheets'

STATIC_DIR = os.path.join(os.getcwd(), 'static')
# PATH_TO_STANDARD_SHEETS = os.path.join(STATIC_DIR, 'example_sheets_online')
PATH_TO_STANDARD_SHEETS = os.path.join(PATH_TO_MOUNT, "SUN-GI-metadb-test", "standard_spreadsheet_templates")
# MANUAL = os.path.join('latest_manual', os.listdir('latest_manual')[0])
MANUAL_DIR = os.path.join(PATH_TO_MOUNT, "SUN-GI-metadb-test", "manuals", "latest_manual")
MANUAL = os.path.join(MANUAL_DIR, os.listdir(MANUAL_DIR)[0])


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




ALLOWED_PRIVILIGES = ["INSERT", "DELETE", "SELECT"]

    

ENUM_TABLES = [data.field_sample_types(),
               data.field_sample_material_type(),
               data.field_sample_context_types(),
               data.field_sample_environment_types()]


# If you add to this, make sure to include the table information in dbtable class
SHEET_TYPES = {
    'field_sample': 'Field samples',
    'edna_archive_sample': 'eDNA archive sampling',
    'edna_robot_sample': 'eDNA robot sampling',
    'edna_wetlab_report': 'eDNA Wet lab final report',
    'adna_wetlab_report': 'aDNA Wet lab final report',
    'cgg_sediment_water': 'CGG Sediment Water',
    'cgg_animal_plant': 'CGG Animal Plant',
    'lane_barcode_html': 'Lane Barcode HTML',
    'seq_sample_sheet': 'Sequencing Center Sample Sheet',
    'master_depth': 'Master Depths sheet',
    'age_depth_model': 'Age Depth Model',
    'initials_translator': 'Initials Translator'
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
    'seq_sample_sheet': '.xlsx',
    'master_depth': '.xlsx'
}


ALLOWED_DATE_FORMATS = ['YYYY-MM-DD', 'DD-MM-YYYY', 'DD/MM/YYYY', 'YYYY/MM/DD', 'My data doesn\'t contain dates']


POSTGRES_TYPES = {'floating_point': ['double precision', 'numeric', 'real', 'decimal', 'float4', 'float8', 'float'],
                  'integer': ['smallint', 'integer', 'bigint', 'int', 'int2', 'int4', 'int8'],
                  'date': ['date', 'timestamptz', 'timestamp', 'time_stamp', 'timestamp with time zone',
                           'timestamp without time zone'],
                  'int_range': ['int4range', 'int8range']}

AUTO_GENERATED_COLUMNS = ['database_insert_by', 
                          'from_spreadsheet', 
                          'database_insert_datetime_utc', 
                          'uid', 
                          'database_insert_date_utc', 
                          'upload_uuid',
                          'depth_id',
                          'fastq_path',
                          'prod_res_path']


DB_CHARACTER_ENCODING = 'UTF-8'


'''
The following is a translator from CGG DB column names to SPAAM defined in https://github.com/SPAAM-community/AncientMetagenomeDir
'''
TO_SPAAM_COLUMN_NAMES = {data.field_sample(): {data.field_sample.country_ocean(): "geo_loc_name",
                                                    data.field_sample.sample_context(): "feature"}}

FROM_SPAAM_COLUMN_NAMES = lambda table_name: {value: key for key, value in TO_SPAAM_COLUMN_NAMES[table_name].items()} if table_name in TO_SPAAM_COLUMN_NAMES else None

        
        