import pandas as pd
import getpass
from sqlalchemy import create_engine
import os
# username = input("Enter your database username: ")
# password = getpass.getpass("Enter your password: ")


DATABASE_CONFIG = {
        'host': 'dandyweb01fl',
        'database': 'aedna_metadata_test',
        'port': '5432',
        'user': 'glj523',
        'password':'Wtcantfw36c!',
    }


ENGINE = create_engine(
    f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}")
pool_id = os.environ.get('POOL_ID')

schema = 'super_simple_db'
tube_tag = os.environ.get('TUBE_TAG')
field_sample_id = os.environ.get('FIELD_SAMPLE')
sequencing_file_id = os.environ.get('SEQUENCING_FILE_ID')
data_request = os.environ.get('DATA')

q = f'''
SELECT as2."ArchiveSampleID", as2."DepthSampledCalTape", as2."FieldSampleID", eas."Library ID", eas."Sequencing File ID", eas."Tube Tag Submitted to SeqC", 
csw."Country", csw."Lat", csw."Lon", csw."Date collected", cap."Country", cap."Lat", cap."Lon", cap."Date collected"
FROM {schema}.edna_archive_sample as2 
JOIN {schema}.edna_wetlab_report eas ON as2."ArchiveSampleID" = eas."LVL Tube Barcode"
JOIN {schema}.cgg_sediment_water csw on as2."FieldSampleID" = csw."CGG ID"
JOIN {schema}.cgg_animal_plant cap on as2."FieldSampleID" = cap."CGG ID" 
'''

