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
import argparse
from constants.misc_constants import RESPONSIBLE_UPLOADERS



def run(input_libs):


    # # Parse command-line arguments
    # parser = argparse.ArgumentParser(description="Process a list of library IDs.")
    # parser.add_argument(
    #     "library_ids",
    #     type=str,
    #     nargs="+",
    #     help="List of library IDs to process (space-separated)."
    # )
    # parser.add_argument(
    #     "customer_email",
    #     type=str,
    #     nargs="+",
    #     help="Email of customer(s) that should receive an overview of missing metadata (space-separated)."
    # )

    # args = parser.parse_args()

    # # Use the provided library IDs
    # input_libs = args.library_ids
    # customer_email = args.customer_email

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
    admin_email = "magnus.johannsen@sund.ku.dk"
    subject = "Missing metadata"
    body = "The sample metadata database (SMDB) is missing data from you. See attached document to see the missing IDs."
    message = MIMEMultipart()
    message["From"] = sender_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))


    lib_pk_col_name = data.edna_wetlab_report.library_id()
    lib_fk_col_name = data.edna_wetlab_report.robot_sample_id()

    rs_pk_col_name = data.edna_robot_sample.robot_sample_id()
    rs_fk_col_name = data.edna_robot_sample.archivesampleid()

    as_pk_col_name = data.edna_archive_sample.archivesampleid()
    as_fk_col_name = data.edna_archive_sample.field_sample_id()

    md_fk_col_name = data.master_depth.depth_id()
    md_pk_col_name = data.master_depth.archive_sample_id()
    master_depth_col_name = data.master_depth.master_depth()

    adm_pk_col_name = data.age_depth_model.depth_id()
    mean_age_col_name = data.age_depth_model.mean()

    fs_pk_col_name = data.field_sample.field_sample_id()

    wr_table_name = data.edna_wetlab_report()
    rs_table_name = data.edna_robot_sample()
    as_table_name = data.edna_archive_sample()
    fs_table_name = data.field_sample()
    md_table_name = data.master_depth()
    adm_table_name = data.age_depth_model()


    query = lambda library_ids: f'''
    WITH filtered_table AS (
        select distinct {lib_pk_col_name}, {lib_fk_col_name} from {wr_table_name} 
        where {lib_pk_col_name} in {library_ids})
    select 
    filtered_table.{lib_pk_col_name}, 
    ers.{rs_pk_col_name}, 
    eas.{as_pk_col_name}, 
    md.{master_depth_col_name},
    adm.{mean_age_col_name},
    fs.{fs_pk_col_name}
    FROM filtered_table
    left JOIN {rs_table_name} ers on filtered_table.{lib_fk_col_name} = ers.{rs_pk_col_name}
    left join {as_table_name} eas on ers.{rs_fk_col_name} = eas.{as_pk_col_name}
    left join {md_table_name} md on eas.{as_pk_col_name} = md.{md_pk_col_name}
    left join {adm_table_name} adm on md.{md_fk_col_name} = adm.{adm_pk_col_name}
    left join {fs_table_name} fs on eas.{as_fk_col_name} = fs.{fs_pk_col_name}
    order by {lib_pk_col_name};
    '''


    df = pd.read_sql(query(tuple(input_libs)), ENGINE_READ_ONLY)

    missing_lib_ids = set(input_libs) - set(df[data.edna_wetlab_report.library_id()])

    if len(missing_lib_ids) > 0:         
        # Create the email
        recipients = [xihan_email, admin_email]
        message["To"] = ', '.join(recipients)
        
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

    _map = {wr_table_name: lib_pk_col_name,
            rs_table_name: rs_pk_col_name,
            as_table_name: as_pk_col_name,
            md_table_name: master_depth_col_name,
            adm_table_name: mean_age_col_name,
            fs_table_name: fs_pk_col_name,
            data.flowcell(): data.flowcell.fastq_file_id(),
            data.seq_sample_sheet(): data.seq_sample_sheet.fastq_file_id()}
    RESPONSIBLE_UPLOADERS = {key: [_map[ele] for ele in val] for key, val in RESPONSIBLE_UPLOADERS.items()}

    recipients = []
    for key, val in RESPONSIBLE_UPLOADERS.items():
        cols = list(set(val) & set(df.columns))
        if len(cols) > 0:  
            if df[cols].isna().any().any():
                recipients.append(key)

    if len(recipients) > 0:
        file_path = "missing_ids.xlsx"
        file_name = "missing_ids.xlsx"  # Name to appear in the email

        df.to_excel(file_path)
        
        # Create the email
        message["To"] = ", ".join(recipients)
        
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
        
if __name__ == "__main__":
    
    input_test_cases = [
        ['LV7001885838',
         'LV7008887632',
         'LV7009026245',],
        ['LV7001885838',
         'LV7008887632',
         'LV7009026245',
         'bad_id'],
        [],
        ['LV7009026245',
         'LV7009026245']
        ['bad_id'],
        ['bad_id',
         'bad_id'],
    ]
    
    for test in input_test_cases:
        run(test)