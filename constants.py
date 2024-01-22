from sqlalchemy import create_engine

admin_email = "magnus.johannsen@sund.ku.dk or julian.perez@sund.ku.dk"

database_config = {
    'host': 'dandyweb01fl',
    'database': 'aedna_metadata',
    'port': '5432',
    'user': 'upload_user',
    'password': 'Ce65r-l+!D04',
    'schema_name': 'test'
}

database_config2 = {
    'host': database_config['host'],
    'dbname': database_config['database'],
    'port': database_config['port'],
    'user': database_config['user'],
    'password': database_config['password'],
}

engine = create_engine(f"postgresql://{database_config['user']}:{database_config['password']}@{database_config['host']}:{database_config['port']}/{database_config['database']}")