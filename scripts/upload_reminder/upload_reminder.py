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
    f'''postgresql
    ://{DATABASE_CONFIG_READ_ONLY['user']}
    :{DATABASE_CONFIG_READ_ONLY['password']}
    @{DATABASE_CONFIG_READ_ONLY['host']}
    :{DATABASE_CONFIG_READ_ONLY['port']}
    /{DATABASE_CONFIG_READ_ONLY['database']}''')

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

wlr = data.edna_wetlab_report()
r = data.edna_robot_sample()
a = data.edna_archive_sample()



query = lambda library_ids: f'''
WITH filtered_table AS (
    select distinct {wlr.library_id()}, {robot_sample_id} from {edna_wetlab_report} 
    where {library_id} in {library_ids})
select filtered_table.{library_id}, ers.{robot_sample_id}, eas.{archive_sample_id}, fs.{field_sample_id}
FROM filtered_table
left JOIN {edna_robot_sample} ers on filtered_table.{robot_sample_id} = ers.{robot_sample_id}
left join {edna_archive_sample} eas on ers.{archive_sample_id} = eas.{archive_sample_id}
left join {field_sample} fs on eas.{field_sample_id} = fs.{field_sample_id}
order by {library_id};
'''

df = pd.read_sql(query(tuple(input)), ENGINE_READ_ONLY)
missing_lib_ids = set(input) - set(df[data.edna_wetlab_report.library_id()])

if len(missing_lib_ids) > 0:         
    # Create the email
    message["To"] = xihan_email
    
    file_path = "missing_ids.txt"
    file_name = "missing_ids.txt"  # Name to appear in the email

    with open(file_path, "w") as file:
        for item in missing_lib_ids:
            file.write(f"{item}\n")
    
    # Attach the file
    with open(file_path, "rb") as file:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(file.read())

    # Encode the file for email
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename={file_name}",
    )

    message.attach(part)
    try:
        with smtplib.SMTP("localhost", 25) as server:  # Postfix typically listens on port 25
            server.send_message(message)
            print("Email sent successfully with attachment!")
    except Exception as e:
        print(f"Error: {e}")


if df.isna().any().any():
    file_path = "missing_ids.xlsx"
    file_name = "missing_ids.xlsx"  # Name to appear in the email

    df.to_excel(file_path)
    
    # Create the email
    message["To"] = jesper_email
    
        # Attach the file
    with open(file_path, "rb") as file:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(file.read())

    # Encode the file for email
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename={file_name}",
    )

    message.attach(part) 
    
    # Send the email via Postfix
    try:
        with smtplib.SMTP("localhost", 25) as server:  # Postfix typically listens on port 25
            server.send_message(message)
            print("Email sent successfully with attachment!")
    except Exception as e:
        print(f"Error: {e}")