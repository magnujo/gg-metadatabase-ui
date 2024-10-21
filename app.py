import generate_template
import numpy as np
import constants.db_connections
from constants.db_names.names import data
from constants.db_connections import ENGINE, ENGINE_READ_ONLY, SQL_ALCH_CONFIG, PSY_CONN
from constants.db_table_related_constants import DBTableRelated
from constants.db_names.name_maps import sheet_to_db_rename_map, db_to_sheet_rename_map
from utils.db_utils import get_ordinal_position_maps
from pathlib import Path
import constants.db_table_related_constants as db_table_related_constants
from utils.misc import make_dir_on_network_mount
from validation_tools import validate_enum_columns
from scripts import deleted_schema_management
import zipfile
from scripts import fid_query, library_id_query, get_all_query
import time
from threading import Lock
lock = Lock()
download_lock = Lock()
upload_lock = Lock()
import seq_center_sample_sheet_parser
from utils import misc
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import Email, DataRequired
import send_email
import lane_barcode_parser
from sqlalchemy.exc import SQLAlchemyError
import psycopg2
from psycopg2 import Error
import traceback
import inspect
import shutil
import constants.misc_constants as misc_constants
import log_util
from utils import queries
from flask import Flask, render_template, jsonify, after_this_request, render_template_string, request, send_file, redirect, url_for, send_from_directory, session, has_request_context
import os
import sys
from constants.misc_constants import SHEET_TYPES, ADMIN_EMAIL, PARSED_SHEETS_FOLDER, ORIGINAL_FILES
from constants import paths
from scripts.ETLFunctions import clean_up
import pandas as pd
import numpy as np
from pandas import testing
import logging
from constants.misc_constants import UPLOADED_FILES, ALLOWED_EXTENSIONS, ALLOWED_DATE_FORMATS
from exception_utils import delete_files, delete_db_entries
from utils.CustomExceptions import DontTriggerFileDeletion
from utils import parsers
import decorators
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import uuid


search_id = 0
env_vars = {'PRODUCTION': None}

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()
    
files_to_del = {'Before Upload': {'original': False, 'parsed': False, 'uploaded': False},
                'After Upload': {'original': False, 'parsed': False, 'uploaded': True}}

logger = log_util.setup()

# # Set log level
app.logger.setLevel(logging.DEBUG)

@app.route('/', methods=['POST', 'GET'])
@decorators.log_info(app)
def index():
    app.logger.info("Index")
    
    if os.environ.get('MAINTAINANCE') and os.environ.get('MAINTAINANCE').lower() == "yes":
        return render_template('maintainance.html')
    else:
        if 'error' not in session:
            session['error'] = False 
        if 'error_message_user' not in session:  
            session['error_message_user'] = None
        if 'error_message_admin' not in session:
            session['error_message_admin'] = None
        
        example_sheets = os.listdir(misc_constants.PATH_TO_STANDARD_SHEETS)
    
        return render_template('index.html', example_sheets=example_sheets, SHEET_TYPES=SHEET_TYPES, ALLOWED_DATE_FORMATS=ALLOWED_DATE_FORMATS)
 

@app.route('/upload', methods=['POST'])
@decorators.log_info(app)
def upload_file():
    with upload_lock:
        # logger.info('Running: ' + str(index.__name__))
       
        session.clear()
        session['email'] = None
        session['error'] = False
        session['error_message_user'] = None
        session['error_message_admin'] = None
        session['visited_success'] = False
        session['email_send'] = False
        session['session_dir_created'] = False
        
        file = request.files['file']
        file_name = file.filename
        session['session_id'] = uuid.uuid4()
        session['session_dir'] = os.path.join(misc_constants.SESSION_DATA, str(session.get("session_id")))
        
        try:
            if file.filename == '':
                raise DontTriggerFileDeletion('No selected file')
            
            session['file_name'] = file_name

            session_dir = str(str(session.get("session_dir"))) 
        
            if os.path.exists(session_dir):
                raise DontTriggerFileDeletion("Session dir already exists")
            
            if file and allowed_file(file.filename):
                file_path = os.path.join(session_dir, ORIGINAL_FILES, file.filename)
            else:
                raise DontTriggerFileDeletion('Invalid file type. Please upload a tab seperated .txt or html file. See manual for help')
            
            if '--no_file_test' in sys.argv:
                pass
            else:
                # TODO Make more general
                if os.path.exists(os.path.join(UPLOADED_FILES, file.filename)) and file_name != "laneBarcode.html":
                    raise DontTriggerFileDeletion(f'A file with the exact same name has already been uploaded to the database. Contact admin you believe this is an error, or if you want to re-upload the file')
                
            database_table_name = request.form.get('database_table_name')
            session['database_table_name'] = database_table_name
            table_splits = db_table_related_constants.DBTableRelated.TABLE_SPLITTER.get(database_table_name)
            
            if database_table_name == 'field_sample':
                if len(table_splits) != 1:
                    raise Exception(f"Tried to split upload sheet into {len(table_splits)} tables, but folder generation is only compatible with 1. Report to admin below.")
            
            date_format = request.form.get('date_format')
            decimal_point = request.form.get('decimal_point')
            thousands_seperator = request.form.get('thousands_seperator')
            
            if thousands_seperator == "no_choice" or not thousands_seperator:
                raise DontTriggerFileDeletion('Please select a thousands seperator character')

            if decimal_point == "no_choice" or not decimal_point:
                raise DontTriggerFileDeletion('Please select a decimal point character')
            
            if decimal_point == thousands_seperator and (decimal_point != "not_relevant" and thousands_seperator != "not_relevant"):
                raise DontTriggerFileDeletion('Decimal point has to be different from thousands seperator')
            
            if date_format == "no_choice" or not date_format:
                raise DontTriggerFileDeletion('Please select a date format type')
            
            if database_table_name == "no_choice" or not database_table_name:
                raise DontTriggerFileDeletion('Please select a spreadsheet type')
            
            os.makedirs(session_dir)
        
        # Dont delete session dir on error before the session dir has been created. This might otherwise delete a dir by mistake.
        except Exception as e:
            return general_error_handling(message=e, delete_session_dir=False, files_to_del=files_to_del['Before Upload'])
            
        try:
            parsed_dir = os.path.join(session_dir, PARSED_SHEETS_FOLDER)
            os.mkdir(os.path.join(session_dir, ORIGINAL_FILES))
            os.mkdir(parsed_dir)
            os.mkdir(os.path.join(session_dir, UPLOADED_FILES))
            
            for table_name in db_table_related_constants.DBTableRelated.TABLE_SPLITTER[database_table_name]:
                os.mkdir(os.path.join(parsed_dir, table_name))
            
            if not os.path.exists(file_path):
                file.save(file_path)
            else:
                raise DontTriggerFileDeletion(f'File {file_path} is trying to be uploaded by other user')

            #TODO only from here can user report error. Solution: only send file in error report if it exists
            
            
            sheets_to_parse = []
            if database_table_name == "lane_barcode_html":
                # TODO: Make more general:
                sheet = pd.read_html(file_path, thousands=thousands_seperator, decimal=decimal_point)

                flowcell_data, top_unknown_barcodes = lane_barcode_parser.parse(df=sheet)
                sheets_to_parse.append(flowcell_data)
                sheets_to_parse.append(top_unknown_barcodes)
            else:       
                if database_table_name == data.seq_sample_sheet():
                    l = []
                    for i in range(10):
                        l.append(f"Column{i+1}")
                    sheet = pd.read_csv(file_path, sep=",", dtype=str, header=None, names=l)
                    sheet = seq_center_sample_sheet_parser.parse(sheet)
                elif database_table_name == data.age_depth_model():
                    sheet = pd.read_csv(file_path, sep='\t', encoding='utf_8', dtype=str)
                else:
                    sheet = pd.read_csv(file_path, sep='\t', encoding='utf_16', dtype=str)
                sheets_to_parse.append(sheet)
            
            clean_sheets = []
            
            for i, sheet in enumerate(sheets_to_parse):
                split_database_table_name = db_table_related_constants.DBTableRelated.TABLE_SPLITTER[database_table_name][i]
                sheet_to_db_col_name_map = sheet_to_db_rename_map(schema_name=SQL_ALCH_CONFIG['schema_name'], table_name=split_database_table_name)
                
                #  Remove trailing and leading whitespace  
                sheet = sheet.applymap(lambda x: x.strip() if isinstance(x, str) else x)
                
                clean_sheet = parsers.parse(sheet=sheet,
                                            database_table_name=split_database_table_name,
                                            date_format=date_format,
                                            decimal_point=decimal_point,
                                            thousands_seperator=thousands_seperator)    
                       
                
                clean_sheet.columns = clean_sheet.columns.str.strip()
                clean_sheet = clean_sheet.rename(columns=sheet_to_db_col_name_map, errors="raise")     
                
                # TODO: Check that no two columns are the same with lower()
            
                
                # Adds rows about which user was responsible for the upload:
                clean_sheet['database_insert_by'] = request.form['email']
                
                # Adds information about which file the data came from:
                clean_sheet['from_spreadsheet'] = file_name

                # Adds infomation about what date and time the upload took place (only UTC seems to work, when testing below, because postgres converts any timezone to UTC)
                clean_sheet['database_insert_datetime_utc'] = pd.Timestamp.now(tz='UTC')
                # Convert to ns to enable testing (postgres converts to ns, when uploading)
                clean_sheet['database_insert_datetime_utc'] = clean_sheet['database_insert_datetime_utc'].astype('datetime64[ns, UTC]')
                
                clean_sheet['upload_uuid'] = 'not_uploaded'
                
                if split_database_table_name == data.edna_wetlab_report():
                    
                    schema_name = SQL_ALCH_CONFIG["schema_name"]
                    id_col_name_sheet = data.edna_wetlab_report.fastq_file_id()
                    id_col_name_table = data.flowcell.fastq_file_id()
                    sheet_ids_not_found_in_flowcell_table = misc.find_missing_ids(sheet=clean_sheet, 
                                                                                  table=data.flowcell(), 
                                                                                  id_col_sheet=id_col_name_sheet, 
                                                                                  id_col_table=id_col_name_table,
                                                                                  engine=ENGINE,
                                                                                  schema=schema_name)
                    lib_id_col_name = data.edna_wetlab_report.library_id()
                    
                    #  If there are some IDs found in the sheet that are not in the flowcell table, it means Julie didn't upload her meta data when she finished sequencing
                    if len(sheet_ids_not_found_in_flowcell_table) != 0:
                        raise Exception(f''' The data cannot be uploaded because the following {id_col_name_sheet}'s 
                                        has not been uploaded to the {data.flowcell()} table, which is needed to generate the file paths: {sheet_ids_not_found_in_flowcell_table} \n
                                            Upload the missing data and try again.''')
                               
                    else:
                        
                        
                        clean_sheet['prod_res_path'] = paths.prod_res_path(clean_sheet[lib_id_col_name])
                        
                        
                if split_database_table_name == data.flowcell():
                    flowcell_id_col_name = data.flowcell.flowcell_id()
                    fastq_id_col_name = data.flowcell.fastq_file_id()
                    flowcell_ids = clean_sheet[flowcell_id_col_name]
                    fastq_ids = clean_sheet[fastq_id_col_name]
                    
                    clean_sheet['fastq_path'] = paths.fastq_path(flowcell_ids, fastq_ids)
                                         
                        
                if split_database_table_name == data.age_depth_model():
                    master_ids = {str(Path(str(file_name)).stem)}
                
                if split_database_table_name == data.master_depth():
                    master_ids = clean_sheet[data.master_depth.master_field_sample_id()].unique()

                if split_database_table_name == data.age_depth_model() or split_database_table_name == data.master_depth():
                    if master_ids == None or len(master_ids) < 1:
                        raise Exception("master_ids is None or empty")
 
                    unique_master_IDs_in_db = queries.get_unique_values_from_db_column(column=data.field_sample.master_id_parent_sample_id(), 
                                                                                      engine=ENGINE, 
                                                                                      schema=SQL_ALCH_CONFIG["schema_name"], 
                                                                                      table=data.field_sample())
                
                    unique_master_IDs_in_db = {s.lower() for s in unique_master_IDs_in_db}

                    for master_id in master_ids:
                        if master_id == None or unique_master_IDs_in_db == None:
                            raise Exception("master_id or master_ids_in_database is None")
                        
                        if master_id.lower() in unique_master_IDs_in_db and master_id != "unknown":
                            if split_database_table_name == data.age_depth_model():
                                clean_sheet[data.field_sample.master_id_parent_sample_id()] = master_id
                            elif split_database_table_name == data.master_depth():
                                pass
                            else:
                                raise Exception("didnt find table name")
                        
                        else:
                            raise Exception(f"Master ID '{master_id}' is not allowed or does not exist in the database. Please rename your Master ID(s) so it refers to an existing Master ID or upload the missing Field Samples data")
                
                if split_database_table_name == data.field_sample():
                    parent_col = data.field_sample.master_id_parent_sample_id()
                    project_col = data.field_sample.running_project_title()
                    id_col = data.field_sample.field_sample_id()
                    
                    unique_master_IDs_in_db = queries.get_unique_values_from_db_column(column=parent_col, 
                                                                                      engine=ENGINE, 
                                                                                      schema=SQL_ALCH_CONFIG["schema_name"], 
                                                                                      table=data.field_sample())
                    
                    unique_project_IDs_in_db = queries.get_unique_values_from_db_column(column=project_col, 
                                                                                      engine=ENGINE, 
                                                                                      schema=SQL_ALCH_CONFIG["schema_name"], 
                                                                                      table=data.field_sample())
                    
  
                    if not parent_col in clean_sheet.columns:
                        raise Exception(f"Expected column {parent_col}, but column was not found in the uploaded file")
                    
                    
                    if not project_col in clean_sheet.columns:
                        raise Exception(f"Expected column {project_col}, but column was not found in the uploaded file")
                        
                    unique_master_IDs_in_parsed_sheet = set(clean_sheet[parent_col].str.lower().unique())
                    unique_project_IDs_in_parsed_sheet = set(clean_sheet[project_col].str.lower().unique())
                                        
                    
                    bad_master_ids = [id for id in unique_master_IDs_in_parsed_sheet if id in unique_master_IDs_in_db]
                    
                    bad_project_ids = [id for id in unique_project_IDs_in_parsed_sheet if id in unique_project_IDs_in_db]
                    
                    if len(bad_master_ids) > 0 or len(bad_project_ids) > 0:
                        raise Exception(f''' The data cannot be uploaded because the following '{parent_col}' values already exists in the database: {bad_master_ids} \n
                                        and/or the following '{project_col}' values already exist in the database {bad_project_ids}. \n
                                        If you want to add the data anyways, contact {ADMIN_EMAIL}
                                        ''') 
                
                db_table_data = pd.read_sql(sql=f"SELECT * from {SQL_ALCH_CONFIG['schema_name']}.{split_database_table_name} LIMIT 1;", con=ENGINE)

                db_generated_uuid = misc.get_db_generated_uuid_col(split_database_table_name, schema_name=SQL_ALCH_CONFIG['schema_name'])
                db_table_data = db_table_data.drop(columns=db_generated_uuid)
                
                if database_table_name in db_table_related_constants.DBTableRelated.DB_GENERATED_COLUMNS:
                    for db_generated_col in db_table_related_constants.DBTableRelated.DB_GENERATED_COLUMNS.get(database_table_name):
                        if db_generated_col in list(db_table_data.columns):
                            db_table_data.drop(db_generated_col, axis=1, inplace=True)
                clean_sheet = misc.match_column_positions(clean_sheet, db_table_data)
                assert list(db_table_data.columns) == list(clean_sheet.columns), ("Column names and/or positions not as expected")

                if split_database_table_name in db_table_related_constants.DBTableRelated.PARENTS.keys():
                    
                    # Check parents precense in DB
                    
                    parents = db_table_related_constants.DBTableRelated.PARENTS[split_database_table_name]
                    
                    for sheet_key, val in parents.items():
                       
                        for db_table, table_keys in val.items():
                            
                            unique_vals_in_sheet = set(clean_sheet[sheet_key].dropna().astype(str).str.lower().unique())
                            for db_key in table_keys:
                                
                                unique_vals_in_db = queries.get_unique_values_from_db_column(column=db_key, 
                                                                                            engine=ENGINE, 
                                                                                            schema=SQL_ALCH_CONFIG["schema_name"], 
                                                                                            table=db_table)
                                diff = unique_vals_in_sheet.difference(unique_vals_in_db)
                                
       
                                if len(diff) != 0:                                
                                    raise Exception(f"Following required IDs in column {sheet_key} where not found in table {db_table} in the database: \n \
                                                    {diff} \n \
                                                        Tell the responsible uploader to upload the missing data first, \
                                                            or make sure that there are no typos in the IDs.")
                
                clean_sheets.append((clean_sheet, split_database_table_name))
                

            for i, (clean_sheet, table_name) in enumerate(clean_sheets):
                db_to_sheet_col_name_map = db_to_sheet_rename_map(schema_name=SQL_ALCH_CONFIG['schema_name'], table_name=table_name)
                suf = str(Path(str(file_name)).suffix)
                stem = str(Path(str(file_name)).stem)
                write_path = os.path.join(session_dir, PARSED_SHEETS_FOLDER, f'{stem}_{table_name}{suf}')
                if not os.path.exists(write_path): 
                    clean_sheet = clean_sheet.rename(columns=db_to_sheet_col_name_map, errors="raise")      
                    clean_sheet.to_csv(write_path, index=False, encoding='utf_16', sep="\t")
                else:
                    raise Exception("Error happened during writing parsed sheet. Contact admin.")

            return redirect(url_for("confirmation_request"))
        
                
        except Exception as e:
            return general_error_handling(message=e, delete_session_dir=True, files_to_del=files_to_del['Before Upload'])


def handle_enum_columns(parsed_sheet, table_name):
    allowed_values, invalid_values = validate_enum_columns.validate_enums_exp(parsed_sheet, table_name=table_name)
    if invalid_values:
        invalid_values_cols = list(map(lambda x: x[0], invalid_values))
        invalid_values = list(map(lambda x: (x[0], pd.DataFrame(x[1]).to_html(na_rep=" ", justify="center", classes="table table-striped", index=True, header=False)), invalid_values))
    allowed_values = [pd.DataFrame({item: allowed_values[item]}).to_html(na_rep=" ", justify="center", classes="table table-striped", index=False) for item in allowed_values if item in invalid_values_cols]

    return allowed_values, invalid_values

@app.route('/pretty_data')
def pretty_data():
    return render_template('confirmation_request copy.html')


#TODO: Catch errors and delete stuff if catched.
@app.route('/confirmation_request', methods=['GET'])
@decorators.log_info(app)
def confirmation_request():
    try:
        if session.get("error") == True:
            return redirect(url_for("index"))
        file_name = session.get('file_name')
        database_table_name = session.get('database_table_name')
        failed_validations = []
                       
        summaries = []
        clean_sheets = []
        for i, ele in enumerate(db_table_related_constants.DBTableRelated.TABLE_SPLITTER[database_table_name]):
            suf = str(Path(str(file_name)).suffix)
            stem = str(Path(str(file_name)).stem)
            clean_sheet = pd.read_csv(os.path.join(str(str(session.get("session_dir"))), PARSED_SHEETS_FOLDER, f'{stem}_{ele}{suf}'), encoding='utf_16', sep='\t')
            # Validate enum columns:   
            caption = lambda x: f'<br><h3 align="center" id="{ele}_{x}">Table {i+1}: {ele}</h3>'

            clean_sheet = misc.drop_auto_generated_columns(clean_sheet)
            summary = (
                clean_sheet
                .dropna(how="all", axis="columns")
                .astype(str)
                .describe()
                .T
                .drop(columns=["count"])
                .rename(columns={"unique": "num of unique values", "top": "mode", "freq": "frequency"})
                .to_html(classes='table table-striped', na_rep=" ", justify="center")
            )
            summary = caption('summary') + summary
            summaries.append(summary)
            clean_sheet = clean_sheet.to_html(na_rep=" ", justify="center", classes="table table-striped")
            html_table_with_caption = caption('table') + clean_sheet
            # allowed_values, invalid_values = handle_enum_columns(clean_sheet, table_name=ele)
            
            clean_sheets.append(html_table_with_caption)
            
            
        # if invalid_values:            
        #     return render_template('enum_validation_fail.html', validation_results=(invalid_values, allowed_values), file_name=file_name, database_table_name=database_table_name)
        # return render_template('confirmation_request copy.html', table=summaries[0])

    
    except Exception as e:
        return general_error_handling(message=e, delete_session_dir=True, files_to_del=files_to_del['Before Upload'])
    return render_template('confirmation_request.html', table_names=db_table_related_constants.DBTableRelated.TABLE_SPLITTER[database_table_name], 
                           clean_sheets=clean_sheets, summaries=summaries, file_name=file_name, database_table_name=database_table_name)

# TODO: lock this function so only 1 can happen at a time (alternatively 1 upload per table at a time)
@app.route('/confirmed', methods=['POST'])
@decorators.log_info(app)
def confirmed():
    with lock:
        print("Confirmed")
        try:
            if session.get("error") == True:
                return redirect(url_for("index"))
            file_name = session.get('file_name')
            database_table_name = session.get('database_table_name')
            table_splits = db_table_related_constants.DBTableRelated.TABLE_SPLITTER.get(database_table_name)
            tables_uploaded_to = []
            clean_sheets = {}
            row_counts_before_upload = {}
            row_counts_after_upload = {}
            row_count_errors = {}
            num_of_uploaded_rows = {}
            num_of_upload_ids_in_db = {}
            upload_id = uuid.uuid4()
            session['upload_id'] = upload_id
            upload_time = pd.Timestamp.now(tz='UTC')

            tables_with_uid = queries.check_if_upload_id_exists_in_schema(database=SQL_ALCH_CONFIG['database'], schema=SQL_ALCH_CONFIG['schema_name'], upload_id=session.get('upload_id'))
            if len(tables_with_uid) != 0:
                raise Exception(f"Found upload_id already in {tables_with_uid}")            
            
        except Exception as e:
            return general_error_handling(message=e, delete_session_dir=True, revert_db=False, files_to_del=files_to_del['Before Upload']) 
        
           
                
        
        # UPLOADING
        for i, table_name in enumerate(table_splits):
            try:
                suf = str(Path(str(file_name)).suffix)
                stem = str(Path(str(file_name)).stem)
                parsed_file_to_upload = os.path.join(str(session.get("session_dir")), PARSED_SHEETS_FOLDER, f'{stem}_{table_name}{suf}')
                clean_sheet = pd.read_csv(parsed_file_to_upload, encoding='utf_16', sep="\t")
               
                
                # clean_sheet = clean_sheet.map(lambda s: s.lower() if type(s) == str else s)
                
                #  Rename columns to DB columns
                rename_map = sheet_to_db_rename_map(schema_name=SQL_ALCH_CONFIG['schema_name'], table_name=table_name)
                
                clean_sheet = clean_sheet.rename(columns=rename_map, errors="raise")
                            
                clean_sheet['upload_uuid'] = session.get('upload_id')
                clean_sheet['database_insert_datetime_utc'] = upload_time
                # Convert to ns to enable testing (postgres converts to ns, when uploading)
                clean_sheet['database_insert_datetime_utc'] = clean_sheet['database_insert_datetime_utc'].astype('datetime64[ns, UTC]')

                clean_sheets[table_name] = clean_sheet
                row_count_errors[table_name] = []
                                    
                # Test that there is only 1 unique upload id in the parsed sheet
                upload_id = list(clean_sheet["upload_uuid"].unique())
                if len(upload_id) !=1:
                    raise Exception(f"Found multiple upload_ids in the data you are trying to upload")
                
                # Test that the upload id doesnt exist already in table
                # TODO: Should this operation be thread locked?
                else:
                    upload_id = upload_id[0]
                    if str(session.get("upload_id")) != str(upload_id):
                        raise Exception("Upload ID discreprancy accross parsed sheet and session variable")
                    uid_exists = queries.check_if_upload_id_exists_in_table(schema=SQL_ALCH_CONFIG["schema_name"], table=table_name, upload_id=upload_id)
                    if uid_exists:
                        raise Exception(f"Found upload id already in {table_name}")
        
                row_count_before_upload = queries.count_rows(SQL_ALCH_CONFIG['database'], SQL_ALCH_CONFIG['schema_name'], table_name=table_name)
                row_counts_before_upload[table_name] = row_count_before_upload
            
            except Exception as e:
                return general_error_handling(message=e, delete_session_dir=True, revert_db=False, files_to_del=files_to_del['Before Upload'])
    
        # Try to upload and rollback if errors happen
        with ENGINE.connect() as conn:
            with conn.begin() as trans:
                try:
                    # Everything that is created, uploaded etc, should be done within this try block.
                    # The rest of this view function is for validation.
                    
                    for i, table_name in enumerate(table_splits):    
                        clean_sheets[table_name].to_sql(name=table_name, 
                                            schema=SQL_ALCH_CONFIG['schema_name'], 
                                            con=conn, 
                                            if_exists='append', 
                                            index=False)

                except Exception as e:
                    try:
                        # Rolling back to conn.begin()
                        trans.rollback()
                        for table in tables_uploaded_to:
                            row_count_after_rollback = queries.count_rows(SQL_ALCH_CONFIG['database'], SQL_ALCH_CONFIG['schema_name'], table_name=table)
                            if row_count_after_rollback != row_counts_before_upload[table]:
                                # TODO: Remove only rows that were not rolled back?
                                raise Exception(f"!!!VERY IMPORTANT!!!: ROLLBACK FAILED: There was an unexpected error rolling back while trying to upload file {file_name} to table {table} with upload_id {upload_id} at {pd.Timestamp.now()}. Contact admin.")
                    except Exception as e:
                        return general_error_handling(message=e, delete_session_dir=True, revert_db=False, files_to_del=files_to_del['Before Upload']) 
                    else:
                        if isinstance(e, SQLAlchemyError):
                            return general_error_handling(message=e.orig, delete_session_dir=True, revert_db=False, files_to_del=files_to_del['Before Upload']) 
                        else:
                            return general_error_handling(message=e, delete_session_dir=True, revert_db=False, files_to_del=files_to_del['Before Upload'])        
                # Commit if no exception happened
                else:
                    trans.commit() 
        
        # The following is validation only. Nothing should be created, only moved.           
        try:
            for i, table_name in enumerate(table_splits):
                row_count_after_upload = queries.count_rows(SQL_ALCH_CONFIG['database'], SQL_ALCH_CONFIG['schema_name'], table_name=table_name)
                row_counts_after_upload[table_name] = row_count_after_upload
                expected_rows = len(clean_sheets[table_name])
                num_of_uploaded_rows[table_name] = row_counts_after_upload[table_name]-row_counts_before_upload[table_name]
                q = queries.upload_id_filter(schema=SQL_ALCH_CONFIG['schema_name'], table=table_name, upload_id=upload_id)
                num_of_upload_ids_in_db[table_name] = len(pd.read_sql(q, con=ENGINE))
            
        except Exception as e: 
            return general_error_handling(message=e, delete_session_dir=True, revert_db=True, files_to_del=files_to_del['Before Upload'])
        
        
        # Test that the amount of rows uploaded matches the lengths of the sheets             
        try:
            for i, table_name in enumerate(table_splits):
                    
                    # If the amount of uploaded rows is not equal to the amount of upload ids, then we cannot roll back automatically because we dont know how many rows to delete. 
                    # If there are more upload_ids then uploaded rows, then we might delete some data that is not supposed to be deleted and if there are less upload_ids then uploaded rows then it's impossible to revert using upload_id.
                    if num_of_uploaded_rows[table_name] != num_of_upload_ids_in_db[table_name]:
                        raise ValueError("!!!CRITICAL ERROR OCCURED!!!: IMPORTANT: Report error below to notify admin. Some rows were uploaded with incorrect upload_id")
                   
                    # Here we can trust upload_id to be correct because of the above conditional, so we can delete data based on it.
                    if expected_rows != num_of_uploaded_rows[table_name]:
                        row_count_errors[table_name].append(f"Error happened during upload. Expected to find {expected_rows} added rows in {table_name} but {num_of_uploaded_rows[table_name]} were found. Rolling back...")
             
        except ValueError as e:
            return general_error_handling(message=e, delete_session_dir=True, revert_db=True, files_to_del=files_to_del['Before Upload'])  
        
        except Exception as e:
            return general_error_handling(message=e, delete_session_dir=True, revert_db=True, files_to_del=files_to_del['Before Upload'])                          
        
        
        try:
            for table in row_count_errors:
                if len(row_count_errors[table_name]) > 0:
                    raise Exception("")
        
            
        except Exception as e:
            return general_error_handling(message=e, delete_session_dir=True, errors=row_count_errors, revert_db=True, rows_to_delete=num_of_uploaded_rows, files_to_del=files_to_del['Before Upload'])
        
            
        # Test that the uploaded data is equal to the parsed sheets
        try:
            for i, table_name in enumerate(table_splits):
                if '--no_upload_test' in sys.argv:
                    pass
                else:
                    integrity_test(table_name, file_name, clean_sheets[table_name], upload_id=session.get('upload_id'))
           
        except Exception as e:
            return general_error_handling(message=e, delete_session_dir=True, revert_db=True, files_to_del=files_to_del['Before Upload'])    
            
        try:
            if '--no_file_test' in sys.argv and os.path.exists(os.path.join(str(session.get("session_dir")), ORIGINAL_FILES, file_name)) or file_name=="laneBarcode.html":
                pass
            else:
                shutil.copy(os.path.join(str(session.get("session_dir")), ORIGINAL_FILES, file_name), UPLOADED_FILES)
                # shutil.move(os.path.join(ORIGINAL_FILES, file_name), UPLOAD_FOLDER)
                
                       
        except Exception as e:
            return general_error_handling(message=e, delete_session_dir=True, revert_db=True, files_to_del=files_to_del['Before Upload'])
        
        
        try:                        
            if database_table_name == 'field_sample':
                for table_name in table_splits:
                        clean_sheet = clean_sheets[table_name]
                        dirs_to_create = misc.generate_field_sample_dir_paths(clean_sheet, projects_root_dir=misc_constants.GEO_DATA_PROJECTS_DIR_PATH, 
                                                                                          samples_root_dir=misc_constants.GEO_DATA_SAMPLES_DIR)
                        created_dirs = []
                        for path in dirs_to_create:
                            os.makedirs(path)
                            created_dirs.append(path)
                                              
                        
        # except FileExistsError as e:
        #     return general_error_handling(message=e, delete_session_dir=True, revert_db=True, files_to_del=files_to_del['After Upload'])                       
        
        except Exception as e:
            
            if "created_dirs" in locals().keys():
                for dir_path in created_dirs:
                    # Check if dirpath exist and is not None (this is because make_dir_on_network_mount returns None if the folder already exists)
                    if dir_path != None:
                        if os.path.exists(dir_path):
                            if str(dir_path)[-1] == str(os.path.sep):
                                destination_path = os.path.join(misc_constants.PATH_TO_MOUNT, misc_constants.GEO_DATA_NETWORK_DIR_DELETIONS, os.path.normpath(dir_path))
                            else:
                                destination_path = os.path.join(misc_constants.PATH_TO_MOUNT, misc_constants.GEO_DATA_NETWORK_DIR_DELETIONS, os.path.basename(dir_path))
                            timestamp = time.strftime("%Y%m%d%H%M%S")
                            destination_path = f"{destination_path}_{timestamp}"
                            shutil.move(dir_path, destination_path)
            return general_error_handling(message=e, delete_session_dir=True, revert_db=True, files_to_del=files_to_del['After Upload'])
        
                        
        return redirect(url_for("success")) 

#TODO: Catch errors and delete stuff if catched.
@app.route('/cancel_upload', methods=['POST'])
@decorators.log_info(app)
def cancel_upload():
    return redirect(url_for("index"))

@app.route('/success', methods=['GET'])
@decorators.log_info(app)
def success():
    try:
        if session.get('error') == True:
            return redirect(url_for("index"))
              
        file_name = session.get('file_name')
        database_table_name = session.get('database_table_name')
        summaries = []
        all_tables = []
        for i, table in enumerate(db_table_related_constants.DBTableRelated.TABLE_SPLITTER.get(database_table_name)):
            caption = f'<br><h3 align="center" id="{table}">Table {i+1}: {table}</h3>'
            
            uploaded_data = pd.read_sql(sql=f"SELECT * from {SQL_ALCH_CONFIG['schema_name']}.{table} where upload_uuid = \'{session.get('upload_id')}\';", con=ENGINE)
            uploaded_data = misc.drop_auto_generated_columns(uploaded_data) # To not display the auto generated columns
            summary = (
                uploaded_data
                .dropna(how="all", axis="columns")
                .astype(str)
                .describe()
                .T
                .drop(columns=["count"])
                .rename(columns={"unique": "num of unique values", "top": "mode", "freq": "frequency"})
                .to_html(classes='table table-striped', na_rep=" ", justify="center")
            )
            
            summary = caption + summary
            summaries.append(summary)
            uploaded_data = uploaded_data.to_html(na_rep=" ", justify="center", classes="table table-striped")
            uploaded_data = caption + uploaded_data
            all_tables.append(uploaded_data)
        return render_template('results.html',  admin_emails=ADMIN_EMAIL, table_names=db_table_related_constants.DBTableRelated.TABLE_SPLITTER[database_table_name], 
                           uploaded_data=all_tables, summaries=summaries, file_name=file_name, database_table_name=database_table_name)


    except Exception as e:
        return general_error_handling(message=e, delete_db_entries=True, 
                                      files_to_del=files_to_del['After Upload'])

@app.route('/error', methods=['GET'])
@decorators.log_info(app)
def error():
    error_messages = session.get('error_message_user')
    error_message_admin = session.get("error_message_admin")
    session['error'] = True

    #error_message = request.args.get('error_message', 'An error occurred.')
    return render_template('error_basic.html', email_send=session.get('email_send'), error_messages=error_messages, error_message_admin=error_message_admin, admin=ADMIN_EMAIL)

def integrity_test(database_table_name, file_name, clean_sheet, upload_id):
    uploaded_data = pd.read_sql(sql=f"SELECT * from {SQL_ALCH_CONFIG['schema_name']}.{database_table_name} where upload_uuid = \'{upload_id}\';", con=ENGINE)

    uploaded_data = uploaded_data.fillna(value=np.nan).reset_index(drop=True)
    clean_sheet = clean_sheet.fillna(value=np.nan).reset_index(drop=True)
            
    clean_sheet = clean_sheet.astype(str)
    uploaded_data = uploaded_data.astype(str)
    
    clean_sheet = clean_sheet.replace("NaT", "nan")
    uploaded_data = uploaded_data.replace("NaT", "nan")
    
    # Converts everything to lowercase
    uploaded_data = uploaded_data.map(lambda x: x.lower() if isinstance(x, str) else x)
    clean_sheet = clean_sheet.map(lambda x: x.lower() if isinstance(x, str) else x)

    if database_table_name in db_table_related_constants.DBTableRelated.DB_GENERATED_COLUMNS:
        for db_generated_col in db_table_related_constants.DBTableRelated.DB_GENERATED_COLUMNS.get(database_table_name):
            if db_generated_col in list(uploaded_data.columns):
                uploaded_data.drop(db_generated_col, axis=1, inplace=True)
    
    clean_sheet = misc.match_column_positions(clean_sheet, uploaded_data)
    
    clean_sheet = clean_sheet.sort_values(by=clean_sheet.columns.tolist()).reset_index(drop=True)
    uploaded_data = uploaded_data.sort_values(by=uploaded_data.columns.tolist()).reset_index(drop=True)
    
    assert clean_sheet.shape == uploaded_data.shape, "Shape input file does not match shape of uploaded data."
    
    # for i in range(len(clean_sheet.dtypes)):
    #     print(clean_sheet.dtypes[i] + " " + uploaded_data.dtypes[i])
        
            # TODO: Before deployment: Try to remove any sql statements that delete data. It is too dangerous. ONLY delete data from db if below tests that compares uploaded data with the cleaned sheet fails. Otherwise we might delete data by mistake. Make a custom DeleteDataException to make sure only that exception will delete data. Also make sure that the deletion is not only based on from_spreadsheet column as there might be cases where the same file names occur.
            # TODO: Instead of deleting data that doesnt pass the tests, upload the sheet to a duplicate database first and test on that. If the tests gets approved, only then upload to the actual db. When everything is in the actual db, maybe delete from the duplicate db.

            # assert clean_sheet.dtypes.equals(uploaded_data.dtypes), f"Datatype mismatch between uploaded data and data in sheet, contact {constants.ADMIN_EMAILS}"
    
    print('Running integrity test')       
    testing.assert_frame_equal(uploaded_data, clean_sheet)
    print('Integrity test passed')
    
    print('Running extra integrity test')
    if not clean_sheet.equals(uploaded_data):
        raise AssertionError("Upload failed. Contents of database is not equal to contents of file.")
    print('Extra integrity test passed')
    
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/download_manual')
@decorators.log_info(app)
def download_manual():
    return send_file(misc_constants.MANUAL, as_attachment=True)

@app.route('/download/<path:filename>')
@decorators.log_info(app)
def download_file(filename): 
    if filename == 'Field Sampling Meta data reporting template.xlsx':
        save_path = os.path.join(misc_constants.PATH_TO_STANDARD_SHEETS, filename)
        generate_template.generate(data.field_sample(), data(), ENGINE_READ_ONLY, save_path=save_path)

    return send_from_directory(misc_constants.PATH_TO_STANDARD_SHEETS, filename, as_attachment=True)

def current_function_name():
    return inspect.currentframe().f_back.f_code.co_name

def generate_html_message(message):
    traceback_ = traceback.format_exc()
    app.logger.exception(traceback_)
    current_datetime = datetime.now()
    client_ip = request.remote_addr
    return f'''
<p>{message}</p>
''', traceback_

def general_error_handling(message, delete_session_dir=False, error_tables=None, errors=None, rows_to_delete=None, tables_uploaded_to=None, revert_db=False, 
                           num_of_uploaded_rows=-1, 
                           files_to_del={'original': False, 'parsed': False, 'uploaded': False}):
        '''Manages deletions to revert to original state'''
        print("\n General error handling... \n")
        session["error"] = True
        upload_id = session.get('upload_id')
        file_name = session.get('file_name')
        error_messages_user = []
        user_error, admin_error = generate_html_message(message)
        error_messages_user.append(user_error)
        
        if revert_db:
            if tables_uploaded_to:
                for i, table in enumerate(tables_uploaded_to):
                    suf = str(Path(str(file_name)).suffix)
                    stem = str(Path(str(file_name)).stem)
                    clean_sheet = pd.read_csv(os.path.join(str(session.get("session_dir")), PARSED_SHEETS_FOLDER, f'{stem}_{table}{suf}'), encoding='utf_16', sep="\t")
                    
                    # To make sure to delete the correct number of rows
                    if num_of_uploaded_rows == -1 or num_of_uploaded_rows == len(clean_sheet):
                        num_of_rows_to_del = len(clean_sheet)
                    else:
                        num_of_rows_to_del = num_of_uploaded_rows
                   
                    delete_db_entries(table, upload_id=upload_id, num_of_rows_to_del=num_of_rows_to_del)
            else:
                if errors:
                    for table in errors:
                        error_messages = errors[table]
                        for i, msg in enumerate(error_messages):
                            error_messages_user.append(f"Error {i}: {msg}")  
                        delete_db_entries(table, upload_id=upload_id, num_of_rows_to_del=rows_to_delete[table])
                else:        
                    database_table_name = session.get('database_table_name')
                    for i, table in enumerate(db_table_related_constants.DBTableRelated.TABLE_SPLITTER.get(database_table_name)):
                        suf = str(Path(str(file_name)).suffix)
                        stem = str(Path(str(file_name)).stem)
                        clean_sheet = pd.read_csv(os.path.join(str(session.get("session_dir")), PARSED_SHEETS_FOLDER, f'{stem}_{table}{suf}'), encoding='utf_16', sep="\t")
                        
                        # To make sure to delete the correct number of rows
                        if num_of_uploaded_rows == -1 or num_of_uploaded_rows == len(clean_sheet):
                            num_of_rows_to_del = len(clean_sheet)
                        else:
                            num_of_rows_to_del = num_of_uploaded_rows
                    
                        delete_db_entries(table, upload_id=upload_id, num_of_rows_to_del=num_of_rows_to_del)
                        
        delete_files(file_name=file_name, **files_to_del, session_dir=str(session.get("session_dir")), delete_session_dir=delete_session_dir)
        # session.clear()
        
        session['error_message_user'] = error_messages_user
        current_time = datetime.now()
        session['error_message_admin'] = f'{str(current_time)}: {str(admin_error)}'
        return redirect(url_for('error'))

@app.route('/send_error_details', methods=['POST'])
@decorators.log_info(app)
def send_error_details():
    email = request.form['text']
    error_message = session.get('error_message_admin')
    message = f'{email} \n {error_message}'
    file_name = session.get('file_name')
    failed_session = os.path.join("deleted_session_data", "failed_sessions", str(session.get("session_id")))
    # attachment_paths = [os.path.join(str(session.get("session_dir")), ORIGINAL_FILES, file_name)]
    attachment_paths = [os.path.join(failed_session, ORIGINAL_FILES, file_name)]
    send_email.send('Error on upload website', message, attachment_paths=attachment_paths)
    
    session['email_send'] = True
    return redirect(url_for('error'))

@app.errorhandler(Exception)
def handle_uncaught_exception(e):
    current_time = datetime.now()
    app.logger.exception('Unhandled Exception: %s', traceback.format_exc())
    app.logger.exception('Unhandled Exception: %s', e)
    message = "!!!!IMPORTANT!!!!: UNKNOWN ERROR OCCURED. THIS MIGHT BE CRUCIAL, SO REPORT TO ADMIN BELOW!"
    return general_error_handling(f"{message}: \n Error message: \n {str(e)}")


def make_search_folder(search_id):
    # Create directory if it doesn't exist
    if not os.path.exists(paths.QUERY_FILES):
        os.makedirs(paths.QUERY_FILES)
    
    # Creating directory path
    search_dir_path = os.path.join(paths.QUERY_FILES, str(search_id))
    
    if not os.path.exists(search_dir_path):
        os.makedirs(search_dir_path)
    else:
        raise Exception(f"Directory {search_id} already exists")

    return search_dir_path
    

def make_dirs_for_query_files(search_id):
    
    # Creating directory path
    search_dir_path = make_search_folder(search_id)
        
    raw_path = os.path.join(search_dir_path, 'raw_tables')
    
    if not os.path.exists(raw_path):
        os.makedirs(raw_path) 
    else:
        raise Exception(f"Directory {raw_path} already exists")
    
    return search_dir_path, raw_path
    
@app.route('/download_all_master_ids')
def get_master_ids():
    
    with download_lock:
    
        q = f'select distinct "{data.field_sample.master_id_parent_sample_id()}" from "{data()}"."{data.field_sample()}"'
        
        df = pd.read_sql(q, con=ENGINE_READ_ONLY)
        
        file_path = os.path.join('temp', 'master_ids.tsv')
        
        df.to_csv(file_path, sep="\t", index=False)
    
        
        return send_file(file_path, as_attachment=True)
    
@app.route('/download_all_field_sample_ids')
def download_all_field_sample_ids():
    
    with download_lock:
    
        q = f'select distinct "{data.field_sample.field_sample_id()}" from "{data()}"."{data.field_sample()}"'
        
        df = pd.read_sql(q, con=ENGINE_READ_ONLY)
        
        file_path = os.path.join('temp', 'field_sample_ids.tsv')
        
        df.to_csv(file_path, sep="\t", index=False)
    
        
        return send_file(file_path, as_attachment=True)


@app.route('/search', methods=['GET', 'POST'])
def search():
    error = ""
    if request.method == 'POST':
        with download_lock:
            input_values = request.form['input_values']                
            input_dropdown = request.form['search_type']
            encoding_type = request.form['encoding_type']
            
            
            
            # Remove trailing newline characters
            input_values = input_values.rstrip('\r\n')
            
            # Split the input values into a list
            values_list_original = input_values.split('\r\n')  # Assuming values are separated by newline character
                        
            values_list_original = list(map(lambda x: x.strip(), values_list_original))
            values_list = list(map(lambda x: x.upper(), values_list_original))
            
            
            global search_id 
            search_id = search_id + 1
            session["search_id"] = str(search_id)
            
            directory_path, raw_path = make_dirs_for_query_files(session.get("search_id"))
            data.edna_archive_sample()
            
            library_id_col_name = data.edna_wetlab_report.library_id() 
            country_col_name = data.cgg_sediment_water.country()
            
            try:
                match input_dropdown:
                    case "":
                        raise Exception("You need to choose a search type in the dropdown menu")
                    case "no_choice":
                        raise Exception("You need to choose a search type in the dropdown menu")
                    case "fID":
                        essential_merged_df, full_merged_df, raws = fid_query.get_meta_data(list(values_list))
                        path_essential = os.path.join(directory_path, 'essential_meta_data.csv')
                        path_all = os.path.join(directory_path, 'all_meta_data.csv')
                 
                    case "lID":
                        essential_merged_df, full_merged_df, raws = get_all_query.get_all_meta_data_using_fids()
                        essential_merged_df = essential_merged_df[essential_merged_df[library_id_col_name].str.upper().isin(list(values_list))] 
                        full_merged_df = full_merged_df[full_merged_df[library_id_col_name].str.upper().isin(list(values_list))] 
                        path_essential = os.path.join(directory_path, 'essential_meta_data.csv')
                        path_all = os.path.join(directory_path, 'all_meta_data.csv')
                        
                        # essential_merged_df, full_merged_df, raws = library_id_query.get_meta_data(list(values_list))
                        # path_essential = os.path.join(directory_path, 'essential_meta_data.csv')
                        # path_all = os.path.join(directory_path, 'all_meta_data.csv')
                        
                    case "country":
                        essential_merged_df, full_merged_df, raws = get_all_query.get_all_meta_data_using_fids()
                        essential_merged_df = essential_merged_df[essential_merged_df[country_col_name].str.upper().isin(list(values_list))] 
                        full_merged_df = full_merged_df[full_merged_df[country_col_name].str.upper().isin(list(values_list))] 
                        path_essential = os.path.join(directory_path, 'essential_meta_data.csv')
                        path_all = os.path.join(directory_path, 'all_meta_data.csv')
                        
                        # Test:
                        raws
                                           
                    case _:
                        raise Exception("You need to choose a search type in the dropdown menu")
                    
                full_merged_df.to_csv(path_or_buf=path_all, index=False, encoding=encoding_type)
                essential_merged_df.to_csv(path_or_buf=path_essential, index=False, encoding=encoding_type)
                zip_paths = []
                for key in raws:
                    path_full = os.path.join(raw_path, f'{key}.csv')
                    raws[key].to_csv(path_or_buf=path_full, index=False, encoding=encoding_type)
                    zip_paths.append(path_full)
                            
                path_zip_query = os.path.join(directory_path, 'individual_filtered_tables.zip')
                create_zip(zip_paths, path_zip_query)
                        
            except Exception as e:
                return general_error_handling(message=e, revert_db=False)
            
            # TODO: Save the dataframes somehow and load again when downloading instead of doing the whole parsing again 
            # Render the template again with the parsed values
            return render_template('search.html', parsed_values=values_list_original, results=essential_merged_df, table=essential_merged_df.to_html(classes='data', header=True))
    
    # Render the template for GET requests
    return render_template('search.html')

def create_zip(files, zip_path):
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in files:
            zipf.write(file)

@app.route('/get_all_data', methods=['POST'])
def get_all_data():
    with download_lock:
        
        encoding_type = request.form['encoding_type']

        
        zip_paths = []
        
        
        essential, full, raws = get_all_query.get_all_meta_data_using_fids()
        
        global search_id 
        search_id = search_id + 1
        session["search_id"] = str(search_id)
                
        directory_path, raw_path = make_dirs_for_query_files(session.get("search_id"))
                
        path_essential = os.path.join(directory_path, 'query_result_essential.csv')
        zip_paths.append(path_essential)
        path_full = os.path.join(directory_path, 'query_result_full.csv')
        zip_paths.append(path_full)
        path_zip_query = os.path.join(directory_path, 'query_all.zip')
        
        full.to_csv(path_or_buf=path_full, index=False, encoding=encoding_type)
        essential.to_csv(path_or_buf=path_essential, index=False, encoding=encoding_type)
        
        for key in raws:
            
            raw_path = os.path.join(directory_path, 'raw_tables', f'{key}.csv')
            zip_paths.append(raw_path)
            raws[key].to_csv(path_or_buf=raw_path, index=False, encoding=encoding_type)
        
        create_zip(zip_paths, path_zip_query)

        # Send the text file as a download to the user
        return send_file(path_zip_query, as_attachment=True)


@app.route('/download_all')
def download_all():
    path = os.path.join('query_files', str(session.get("search_id")), 'all_meta_data.csv')
    
    # Send the text file as a download to the user
    return send_file(path, as_attachment=True)

def get_merged_standardized(qc_checked=False):
    
    if qc_checked:
        query = f"select * from {data()}.outer_coalesced_mega_table_full"
    
    else:
        query = f"select * from {data()}.outer_coalesced_mega_table_meta"
    
    df = pd.read_sql(query, con=ENGINE_READ_ONLY)
    
    return df
    

@app.route('/PI_download_standardized', methods=['POST'])
def PI_download_standardized():
    with download_lock:
        
        df = get_merged_standardized()
        
        
        
        columns = [
            "field_sample_parent_id",
            "field_sample_id",
            "archive_sample_id",
            "Master Depth (cm)",
            "ArchiveSampleDepthCalTape",
            "ArchiveSamplePositionInRack",
            "ArchiveSampleRackName",
            "ArchiveSampleRackID"
        ]
        
        df = df[columns]
        
        df = df.rename(columns={"field_sample_parent_id": "Master Field Sample ID",
                           "field_sample_id": "Field Sample ID",
                           "archive_sample_id": "Archive Sample ID"})
        
        encoding_type = request.form['encoding_type']
        
        input_values = request.form['input_values']    
        input_dropdown = request.form['search_type']
            
            
        # Remove trailing newline characters
        input_values = input_values.rstrip('\r\n')
        
        # Split the input values into a list
        values_list_original = input_values.split('\r\n')  # Assuming values are separated by newline character
                    
        values_list_original = list(map(lambda x: x.strip(), values_list_original))
        values_list = list(map(lambda x: x.lower(), values_list_original))
        
        zip_paths = []
                
        global search_id 
        search_id = search_id + 1
        session["search_id"] = str(search_id)
                
        directory_path, raw_path = make_dirs_for_query_files(session.get("search_id"))
                
        path_full = os.path.join(directory_path, 'master_depths_etc.csv')
        # zip_paths.append(path_full)
        # path_zip_query = os.path.join(directory_path, 'query_all.zip')
        
        match input_dropdown:
            case "":
                raise Exception("You need to choose a search type in the dropdown menu")
            case "no_choice":
                raise Exception("You need to choose a search type in the dropdown menu")
            case "fID":
                filter = df["Field Sample ID"].str.lower().isin(values_list)
            
            case "mID":
                filter = df["Master Field Sample ID"].str.lower().isin(values_list)
                
            case _:
                raise Exception("You need to choose a search type in the dropdown menu")
        
        
        df = df[filter]
        df = df.drop_duplicates(subset=["Archive Sample ID"])
        
        df.to_csv(path_or_buf=path_full, index=False, encoding=encoding_type)
        
        # create_zip(zip_paths, path_zip_query)

        # Send the text file as a download to the user
        return send_file(path_full, as_attachment=True)
    
    
    

@app.route('/download_merged_standardized', methods=['POST'])
def download_merged_standardized():
    
    
    with download_lock:
        qc_checked = 'checkbox_qc' in request.form
        
        
        
        df = get_merged_standardized(qc_checked)
        
        encoding_type = request.form['encoding_type']

        zip_paths = []
                
        global search_id 
        search_id = search_id + 1
        session["search_id"] = str(search_id)
                
        directory_path, raw_path = make_dirs_for_query_files(session.get("search_id"))
                
        path_full = os.path.join(directory_path, 'query_result_full.csv')
        zip_paths.append(path_full)
        path_zip_query = os.path.join(directory_path, 'query_all.zip')
        
        
        df.to_csv(path_or_buf=path_full, index=False, encoding=encoding_type)
        
        create_zip(zip_paths, path_zip_query)

        # Send the text file as a download to the user
        return send_file(path_zip_query, as_attachment=True)
    
    
    

@app.route('/download_all_individual_tables', methods=['POST'])
def download_all_individual_tables():
    
    with download_lock:
        encoding_type = request.form['encoding_type']    
        zip_paths = []
        
        global search_id 
        search_id = search_id + 1
        session["search_id"] = str(search_id) 
        
        directory_path, raw_path = make_dirs_for_query_files(session.get("search_id"))
        
        path_zip = os.path.join(directory_path, 'all_tables.zip')
        
        schema_name = constants.db_connections.SQL_ALCH_CONFIG["schema_name"]
        database_name = constants.db_connections.SQL_ALCH_CONFIG["database"]
        
        tables = queries.get_table_names(schema_name=schema_name, database_name=database_name)
        tables = set(tables) - set(DBTableRelated.UTIL_TABLES_LEAFS)
        
        for table_name in tables:
            df = pd.read_sql(f'select * from {schema_name}.{table_name}', con=ENGINE_READ_ONLY)
            # if encoding_type == "ascii":
            #     df = df.applymap(lambda x: ascii(x) if isinstance(x, str) else x)
            table_path = os.path.join(raw_path, f"{table_name}.tsv")
            df.to_csv(table_path, encoding=encoding_type, sep="\t")
            zip_paths.append(table_path)
            
        create_zip(zip_paths, path_zip)


        # Send the text file as a download to the user
        return send_file(path_zip, as_attachment=True)


@app.route('/download_essential')
def download_essential():
    path = os.path.join('query_files', str(session.get("search_id")), 'essential_meta_data.csv')


    # Send the text file as a download to the user
    return send_file(path, as_attachment=True)

@app.route('/download_individual_unfiltered_tables')
def download_individual_unfiltered_tables():
    path = os.path.join('query_files', str(session.get("search_id")), 'individual_filtered_tables.zip')
    
    # Send the text file as a download to the user
    return send_file(path, as_attachment=True)



if __name__ == '__main__':
    print("Start")
    db_table_related_constants.DBTableRelated.check_for_table_name_inconsistencies()
    db_table_related_constants.DBTableRelated.check_for_duplicates()
    production_args = misc_constants.ALLOWED_COMMAND_LINE_ARGS['production']
    development_args = misc_constants.ALLOWED_COMMAND_LINE_ARGS['development']
    current_date = datetime.now().strftime('%Y%m%d')

    if os.environ.get('RUN_MODE'):
        constants.db_connections.RUN_MODE = os.environ.get('RUN_MODE').lower()
        if not constants.db_connections.RUN_MODE in constants.db_connections.RUN_MODE_OPTIONS:
            raise Exception(f'Unknown value for RUN_MODE')
    print(f"RUNMODE:{constants.db_connections.RUN_MODE}")
    
    deleted_schema_management.copy_or_generate(constants.db_connections.SQL_ALCH_CONFIG["schema_name"], database_name=constants.db_connections.SQL_ALCH_CONFIG["database"], alch_engine=ENGINE, psy_conn=constants.db_connections.PSY_CONN)
    misc.empty_folder("query_files", exclude=[".gitignore"])
    
    if constants.db_connections.RUN_MODE == 'production':
        app.run(host='0.0.0.0', port=5100)
    elif constants.db_connections.RUN_MODE == 'development':
        app.run(debug=True)
    else:
        raise Exception('Error')    

    # if "--production" in sys.argv:
    #     for arg in sys.argv[1:]:
    #         if not arg in production_args or arg in development_args:
    #                 raise Exception(f"Argument {arg} only allowed for development")
    #     app.run(host='0.0.0.0', port=5100)
    # else:
    #     for arg in sys.argv[1:]:
    #         if not arg in production_args + development_args:
    #                 raise Exception(f"Argument {arg} not allowed")
    #     app.run(debug=True)

