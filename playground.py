import getpass
import pandas as pd
import constants.misc_constants as constants
from sqlalchemy import create_engine




d = {"name": 
    [
        "unknown",
        "dental calculus",
        "palaeofaeces",
        "birch pitch",
        "bone",
        "tooth",
        "permafrost",
        "lake sediment",
        "marine sediment",
        "shallow marine sediment",
        "peat soil",
        "midden",
        "rock shelter",
        "calcified nodule",
        "digestive tract contents",
        "muscle tissue",
        "buccal fat pad",
        "omentum",
        "peritoneum",
        "intestine",
        "caecum",
        "lung tissue",
        "isolate",
        "large intestine",
        "skin",
        "sediment",
        "soil",
        "liver",
        "tissue",
        "blood",
        "thoracic segment of trunk",
        "abdomen",
        "leaf",
        "bodily fluid material",
        "medical instrument",
        "keratinous claw",
        "latrine",
        "skull",
        "shell",
        "skin of leg",
        "strand of hair",
        "brain",
        "dura mater",
        "stomach",
        "lung",
        "skeleton",
        "kidney stone"]
    }

def upload_data(dataframe, schema_name, table_name, database, host, port):
    user = input("Enter your db super username: ")
    password = getpass.getpass("Enter your password: ")
    dataframe = dataframe.map(lambda s: s.lower() if type(s) == str else s)
    DATABASE_CONFIG = {
            'host': host,
            'database': database,
            'port': port,
            'user': user,
            'password': password,
            'schema_name': schema_name
        }

    engine = create_engine(
        f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}")
        
    with engine.connect() as connection:
        dataframe.to_sql(name=table_name, con=connection, schema=schema_name, if_exists="append", index=False)
    engine.dispose()

upload_data(pd.DataFrame(d), 'test_1', 'field_sample_material_type', 'aedna_metadata_test', 'dandyweb01fl', '5432')