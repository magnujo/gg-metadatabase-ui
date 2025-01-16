import os, sys
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(parent_dir)
from sqlalchemy import create_engine
import pandas as pd
from constants.db_names.names import data 
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

DATABASE_CONFIG_READ_ONLY = {
    'host': 'dandypdb01fl',
    'dbname': 'aedna_metadata_test',
    'port': '5432',
    'user': 'read_user',
    'password': r'mv5&8B%eKuoE8D',
}
ENGINE_READ_ONLY = create_engine(
    f"postgresql://{DATABASE_CONFIG_READ_ONLY['user']}:{DATABASE_CONFIG_READ_ONLY['password']}@{DATABASE_CONFIG_READ_ONLY['host']}:{DATABASE_CONFIG_READ_ONLY['port']}/{DATABASE_CONFIG_READ_ONLY['dbname']}")

# Email details
sender_email = "glj523@dandyweb01fl.unicph.domain"
xihan_email = "magnus.johannsen@sund.ku.dk"
jesper_email = "magnus.johannsen@sund.ku.dk"
subject = "Missing metadata"
body = "The sample metadata database (SMDB) is missing data from you. See attached document to see the missing IDs."
message = MIMEMultipart()
message["From"] = sender_email
message["Subject"] = subject
message.attach(MIMEText(body, "plain"))

input = [
    'LV7001885838',
    'LV7008887632',
    'LV7009026245',
    'LV7008886642',
    'LV7001884279',
    'LV7001884009',
    'LV7001884028',
    'test'
]

lib_id_col_name = data.edna_wetlab_report.library_id()
rs_id_col_name = data.edna_robot_sample.robot_sample_id()
as_id_col_name = data.edna_archive_sample.archivesampleid()
fs_id_col_name = data.field_sample.field_sample_id()

wr_table_name = data.edna_wetlab_report()
rs_table_name = data.edna_robot_sample()
as_table_name = data.edna_archive_sample()
fs_table_name = data.field_sample()


query = lambda library_ids: f'''
WITH filtered_table AS (
    select distinct {lib_id_col_name}, {rs_id_col_name} from {wr_table_name} 
    where {lib_id_col_name} in {library_ids})
select filtered_table.{lib_id_col_name}, ers.{rs_id_col_name}, eas.{as_id_col_name}, fs.{fs_id_col_name}
FROM filtered_table
left JOIN {rs_table_name} ers on filtered_table.{rs_id_col_name} = ers.{rs_id_col_name}
left join {as_table_name} eas on ers.{as_id_col_name} = eas.{as_id_col_name}
left join {fs_table_name} fs on eas.{fs_id_col_name} = fs.{fs_id_col_name}
order by {lib_id_col_name};
'''

df = pd.read_sql(query(tuple(input)), ENGINE_READ_ONLY)