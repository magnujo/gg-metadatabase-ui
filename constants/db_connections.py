import psycopg2
import os
from sqlalchemy import create_engine

active_database_name = 'smdb'
active_host = 'dandypdb01fl'
active_port = '5432'
pw = os.environ.get('PGPASSWORD')

DATABASE_CONFIG_READ_ONLY = {
    'host': active_host,
    'dbname': active_database_name,
    'port': active_port,
    'user': 'read_user',
    'password': pw,
}

ENGINE_READ_ONLY = create_engine(
    f"postgresql://{DATABASE_CONFIG_READ_ONLY['user']}:{DATABASE_CONFIG_READ_ONLY['password']}@{active_host}:{active_port}/{active_database_name}")

PSY_CONN_READ_ONLY = psycopg2.connect(
            dbname=DATABASE_CONFIG_READ_ONLY["dbname"],
            user=DATABASE_CONFIG_READ_ONLY["user"],
            password=DATABASE_CONFIG_READ_ONLY["password"],
            host=DATABASE_CONFIG_READ_ONLY["host"],
            port=DATABASE_CONFIG_READ_ONLY["port"]
        )


if pw:
    RUN_MODE_OPTIONS = ['production', 'development']

    if os.environ.get('RUN_MODE'):
        RUN_MODE = os.environ.get('RUN_MODE').lower()
        if not RUN_MODE in RUN_MODE_OPTIONS:
            raise Exception(f'Unknown value for RUN_MODE')


    RUN_MODE = 'development'

    if RUN_MODE == 'production':
        SQL_ALCH_CONFIG = {
            'host': active_host,
            'database': active_database_name,
            'port': active_port,
            'user': 'upload_user',
            'password': pw,
            'schema_name': 'uploaded_data'
        }

    elif RUN_MODE == 'development':
        SQL_ALCH_CONFIG = {
            'host': active_host,
            'database': active_database_name,
            'port': active_port,
            'user': 'upload_user',
            'password': pw,
            'schema_name': 'uploaded_data'
        }

    PSY_CONN = psycopg2.connect(
                dbname=SQL_ALCH_CONFIG["database"],
                user=SQL_ALCH_CONFIG["user"],
                password=SQL_ALCH_CONFIG["password"],
                host=SQL_ALCH_CONFIG["host"],
                port=SQL_ALCH_CONFIG["port"]
            )


    ENGINE = create_engine(
        f"postgresql://{SQL_ALCH_CONFIG['user']}:{SQL_ALCH_CONFIG['password']}@{SQL_ALCH_CONFIG['host']}:{SQL_ALCH_CONFIG['port']}/{SQL_ALCH_CONFIG['database']}")

    PSYCON_CONFIG = {
        'host': SQL_ALCH_CONFIG['host'],
        'dbname': SQL_ALCH_CONFIG['database'],
        'port': SQL_ALCH_CONFIG['port'],
        'user': SQL_ALCH_CONFIG['user'],
        'password': SQL_ALCH_CONFIG['password'],
    }


