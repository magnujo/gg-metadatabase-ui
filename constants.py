from sqlalchemy import create_engine

ADMIN_EMAILS = "magnus.johannsen@sund.ku.dk or julian.perez@sund.ku.dk"
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt'}

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
    # 'field_sample': 'Field sampling - NOT IMPLEMENTED',
    'archive_sample': 'eDNA archive sampling',
    'robot_sample': 'eDNA robot sampling',
#    'edna_wetlab_report': 'eDNA Wet lab final report - NOT IMPLEMENTED',
#    'adna_wetlab_report': 'aDNA Wet lab final report - NOT IMPLEMENTED',
#    'cgg_sediment': 'CGG Sediment - NOT IMPLEMENTED',
#    'cgg_animal_plant': 'CGG Plant Animal - NOT IMPLEMENTED'
}