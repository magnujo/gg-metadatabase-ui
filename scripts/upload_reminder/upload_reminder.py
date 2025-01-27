import os
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import os, sys
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
from constants.misc_constants import RESPONSIBLE_UPLOADERS, ADMIN_EMAIL
from utils.send_email import send_email
from pathlib import Path

def find_project_root():
    path = Path(__file__).resolve()
    while path != path.root:
        if (path / 'very_rootsy_file.txt').exists():
            return path
        path = path.parent
    return None  # Project root not found

def run(input_libs, customer_emails, test):
    
    if test:
        print("Running tests...")

    project_root = find_project_root()

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
    admin_email = ADMIN_EMAIL
    sender_email = "glj523@dandyweb01fl.unicph.domain"
    xihan_email = 'xihan.chen@sund.ku.dk'
    subject = "Missing metadata"
    

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
    
    if not len(input_libs) > 0:
        raise Exception('No input')
    
    query_input = tuple(input_libs)
    
    
    if len(input_libs) == 1:
        query_input = f"('{input_libs[0]}')" # Otherwise a single element tupe will look like this: ('id',), but sql wants ('id')
    
    df = pd.read_sql(query(query_input), ENGINE_READ_ONLY)
    temp_path = os.path.join(project_root, 'temp')
    missing_lib_ids = set(input_libs) - set(df[data.edna_wetlab_report.library_id()])
    file_path_xihan = os.path.join(temp_path, 'missing_ids.txt')
    file_path_rest = os.path.join(temp_path, 'missing_ids.xlsx')
    
    try:
        if len(missing_lib_ids) > 0:         
            # Create the email
            recipients = [xihan_email, admin_email]
            
            if test:
                recipients = admin_email
            
            with open(file_path_xihan, "w") as file:
                for item in missing_lib_ids:
                    file.write(f"{item}\n")
                    
            body = f'''
            THIS EMAIL IS AUTO-GENERATED. DO NOT REPLY. If you have any questions write to {ADMIN_EMAIL}
            \n
            Dear Xihan,           
            \n
            The sample metadata database (SMDB) is missing data about certain libraries. See attached document to see which. 
            \n 
            Please upload the missing data as soon as possible by going to http://dandyweb01fl.unicph.domain:5100/
            '''
            
            send_email(sender=sender_email,
                    receivers=recipients,
                    message=body,
                    paths_to_attachments=[file_path_xihan],
                    subject=subject)

        _map = {wr_table_name: lib_pk_col_name,
                rs_table_name: rs_pk_col_name,
                as_table_name: as_pk_col_name,
                md_table_name: master_depth_col_name,
                adm_table_name: mean_age_col_name,
                fs_table_name: fs_pk_col_name,
                data.flowcell(): data.flowcell.fastq_file_id(),
                data.seq_sample_sheet(): data.seq_sample_sheet.fastq_file_id()}
        
        mapped_responsible_uploaders = {key: [_map[ele] for ele in val] for key, val in RESPONSIBLE_UPLOADERS.items()}
        
        recipients = []
        for key, val in mapped_responsible_uploaders.items():
            cols = list(set(val) & set(df.columns))
            if len(cols) > 0:  
                if df[cols].isna().any().any():
                    if test:
                        recipients.append(admin_email)
                    else: 
                        recipients.append(key)        
            
        if len(recipients) > 0:
           
            recipients.append(admin_email)

            df.to_excel(file_path_rest)
            
            body = f'''
            THIS EMAIL IS AUTO-GENERATED. DO NOT REPLY. If you have any questions write to {ADMIN_EMAIL}
            \n
            Dear Jesper, Marie-Louise and Nicolaj,           
            \n
            The sample metadata database (SMDB) is missing data from you. 
            See attached document to see which data is missing (the empty cells), and what IDs they should reference 
            (the non-empty cells). 
            \n 
            Please upload the missing data as soon as possible by going to http://dandyweb01fl.unicph.domain:5100/
            '''
            
            send_email(sender=sender_email,
                    receivers=recipients,
                    message=body,
                    paths_to_attachments=[file_path_rest],
                    subject=subject)
            
    finally:
        if os.path.exists(file_path_rest):
            os.remove(file_path_rest)
        if os.path.exists(file_path_xihan):
            os.remove(file_path_xihan)
            
if __name__ == "__main__":
        # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Send emails reminding people to upload missing meta data")
    parser.add_argument(
        "-l",
        "--library_ids",
        type=str,
        nargs="+",
        required=True,
        help="List of library IDs to process (space-separated)."
    )
    parser.add_argument(
        "-c",
        "--customer_emails",
        type=str,
        required=False,
        nargs="+",
        help="Email of customer(s) that should receive an overview of missing metadata (space-separated). NOT IMPLEMENTED."
    )
    
    parser.add_argument(
        "-t",
        "--test",
        action='store_true',
        required=False,
        help="Only for testing the script"
    )

    args = parser.parse_args()
    
    run(args.library_ids, args.customer_emails, args.test)
    
