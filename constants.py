from sqlalchemy import create_engine

ADMIN_EMAILS = "magnus.johannsen@sund.ku.dk"
UPLOAD_FOLDER = 'uploaded_sheets'
ALLOWED_EXTENSIONS = {'txt'}
PARSED_SHEETS_FOLDER = 'parsed_sheets'
TEMP_FOLDER = 'temp'
ORIGINAL_FILES = 'orignal_sheets'

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
    'archive_sample': 'eDNA archive sampling',
    'robot_sample': 'eDNA robot sampling',
    'edna_wetlab_report': 'eDNA Wet lab final report',
    'adna_wetlab_report': 'aDNA Wet lab final report',
    'cgg_sediment_water': 'CGG Sediment Water',
    'cgg_animal_plant': 'CGG Animal Plant'
}

ALLOWED_DATE_FORMATS = ['YYYY-MM-DD', 'DD-MM-YYYY', 'DD/MM/YYYY', 'YYYY/MM/DD']
