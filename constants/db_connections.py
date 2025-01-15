import psycopg2
import os
from sqlalchemy import create_engine

RUN_MODE_OPTIONS = ['production', 'development']

if os.environ.get('RUN_MODE'):
    RUN_MODE = os.environ.get('RUN_MODE').lower()
    if not RUN_MODE in RUN_MODE_OPTIONS:
        raise Exception(f'Unknown value for RUN_MODE')

pw = os.environ.get('PGPASSWORD')
RUN_MODE = 'development'

if RUN_MODE == 'production':
    SQL_ALCH_CONFIG = {
        'host': 'dandypdb01fl',
        'database': 'aedna_metadata_test',
        'port': '5432',
        'user': 'upload_user',
        'password': pw,
        'schema_name': 'test_1'
    }

elif RUN_MODE == 'development':
    SQL_ALCH_CONFIG = {
        'host': 'dandypdb01fl',
        'database': 'aedna_metadata_test',
        'port': '5432',
        'user': 'upload_user',
        'password': pw,
        'schema_name': 'test_1'
    }

PSY_CONN = psycopg2.connect(
            dbname=SQL_ALCH_CONFIG["database"],
            user=SQL_ALCH_CONFIG["user"],
            password=SQL_ALCH_CONFIG["password"],
            host=SQL_ALCH_CONFIG["host"],
            port=SQL_ALCH_CONFIG["port"]
        )
DATABASE_CONFIG_READ_ONLY = {
    'host': SQL_ALCH_CONFIG['host'],
    'dbname': SQL_ALCH_CONFIG['database'],
    'port': SQL_ALCH_CONFIG['port'],
    'user': 'read_user',
    'password': r'mv5&8B%eKuoE8D',
}
ENGINE_READ_ONLY = create_engine(
    f"postgresql://{DATABASE_CONFIG_READ_ONLY['user']}:{DATABASE_CONFIG_READ_ONLY['password']}@{SQL_ALCH_CONFIG['host']}:{SQL_ALCH_CONFIG['port']}/{SQL_ALCH_CONFIG['database']}")
ENGINE = create_engine(
    f"postgresql://{SQL_ALCH_CONFIG['user']}:{SQL_ALCH_CONFIG['password']}@{SQL_ALCH_CONFIG['host']}:{SQL_ALCH_CONFIG['port']}/{SQL_ALCH_CONFIG['database']}")
PSYCON_CONFIG = {
    'host': SQL_ALCH_CONFIG['host'],
    'dbname': SQL_ALCH_CONFIG['database'],
    'port': SQL_ALCH_CONFIG['port'],
    'user': SQL_ALCH_CONFIG['user'],
    'password': SQL_ALCH_CONFIG['password'],
}

