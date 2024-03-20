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
import constants
import log_util
from flask import Flask, render_template, render_template_string, request, send_file, redirect, url_for, send_from_directory, session, has_request_context
import os
import sys
from constants import SHEET_TYPES, ADMIN_EMAIL, PARSED_SHEETS_FOLDER, ORIGINAL_FILES
from scripts.ETLFunctions import clean_up
import pandas as pd
import numpy as np
from pandas import testing
import logging
from constants import ENGINE, DATABASE_CONFIG, UPLOAD_FOLDER, ALLOWED_EXTENSIONS, ALLOWED_DATE_FORMATS
from exception_utils import delete_files, delete_db_entries
from utils.CustomExceptions import DontTriggerFileDeletion
from utils import parsers
import decorators
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler

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
    if 'error' not in session:
        session['error'] = False 
    if 'error_message_user' not in session:  
        session['error_message_user'] = None
    if 'error_message_admin' not in session:
        session['error_message_admin'] = None
    
    example_sheets = os.listdir(constants.PATH_TO_STANDARD_SHEETS)
    
    
    return render_template('index.html', example_sheets=example_sheets, SHEET_TYPES=SHEET_TYPES, ALLOWED_DATE_FORMATS=ALLOWED_DATE_FORMATS)
    

@app.route('/upload', methods=['POST'])
@decorators.log_info(app)
def upload_file():
    # logger.info('Running: ' + str(index.__name__))
    session.clear()
    session['email'] = None
    session['error'] = False
    session['error_message_user'] = None
    session['error_message_admin'] = None
    session['visited_success'] = False
    session['email_send'] = False
    file = request.files['file']
    file_name = file.filename
    try:
        if file.filename == '':
            raise DontTriggerFileDeletion('No selected file')
        
        session['file_name'] = file_name
        
        database_table_name = request.form.get('database_table_name')
        session['database_table_name'] = database_table_name
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

        if file and allowed_file(file.filename):
            file_path = os.path.join(ORIGINAL_FILES, file.filename)

            if '--no_file_test' in sys.argv:
                pass
            else:
                if os.path.exists(os.path.join(UPLOAD_FOLDER, file.filename)) and file_name != "laneBarcode.html":
                    raise DontTriggerFileDeletion(f'A file with the exact same name has already been uploaded to the database. Contact admin you believe this is an error, or if you want to re-upload the file')
            
            # else:
                # Use DontTriggerFileDelete before this and use Exception after. 
            file.save(file_path)
            
            # file_name = os.path.split(file_path)[-1]

            # clean_sheet = clean_up(tsv_file_path=file_path, 
            #                        database_table_name=database_table_name, 
            #                        date_format=date_format,
            #                        decimal_point=decimal_point,
            #                        thousands_seperator=thousands_seperator)
            
            sheets_to_parse = []
            if database_table_name in constants.MULTI_TABLE_SHEETS:
                
                sheet = pd.read_html(file_path, thousands=thousands_seperator, decimal=decimal_point)
                flowcell_data, top_unknown_barcodes = lane_barcode_parser.parse(df=sheet)
                sheets_to_parse.append(flowcell_data)
                sheets_to_parse.append(top_unknown_barcodes)
            else:
                sheet = pd.read_csv(file_path, sep='\t', encoding='utf_16', dtype=str)
                sheets_to_parse.append(sheet)
            
            clean_sheets = []
            
            for i, sheet in enumerate(sheets_to_parse):
                clean_sheet = parsers.parse(sheet=sheet,
                                            database_table_name=constants.TABLE_SPLITTER[database_table_name][i],
                                            date_format=date_format,
                                            decimal_point=decimal_point,
                                            thousands_seperator=thousands_seperator)
                
            
                # Adds rows about which user was responsible for the upload:
                clean_sheet['database_insert_by'] = DATABASE_CONFIG['user']
                
                # Adds information about which file the data came from:
                clean_sheet['from_spreadsheet'] = file_name
                

                # Adds infomation about what date and time the upload took place (only UTC seems to work, when testing below, because postgres converts any timezone to UTC)
                clean_sheet['database_insert_datetime_utc'] = pd.Timestamp.now(tz='UTC')
                # Convert to ns to enable testing (postgres converts to ns, when uploading)
                clean_sheet['database_insert_datetime_utc'] = clean_sheet['database_insert_datetime_utc'].astype('datetime64[ns, UTC]')
                clean_sheets.append(clean_sheet)

        else:
            raise DontTriggerFileDeletion('Invalid file type. Please upload a tab seperated .txt or html file. See manual for help')

        for i, clean_sheet in enumerate(clean_sheets):
            clean_sheet.to_csv(os.path.join(PARSED_SHEETS_FOLDER, f'{file.filename}_{i}'), index=False, encoding='utf_16', sep="\t")

        return redirect(url_for("confirmation_request"))
    
    # If user tries to upload a file that was already added we don't delete anything other than the session data, 
    # to make sure the original file and db data doesn't get deleted.
    except DontTriggerFileDeletion as e1:
        return general_error_handling(message=e1, files_to_del=files_to_del['Before Upload'])
            
    except Exception as e:
        return general_error_handling(message=e, files_to_del=files_to_del['Before Upload'])


#TODO: Catch errors and delete stuff if catched.
@app.route('/confirmation_request', methods=['GET'])
@decorators.log_info(app)
def confirmation_request():
    try:
        if session['error'] == True:
            return redirect(url_for("index"))
        file_name = session.get('file_name')
        database_table_name = session.get('database_table_name')
        
        clean_sheets = []
        for i, ele in enumerate(constants.TABLE_SPLITTER[database_table_name]):
            clean_sheet = pd.read_csv(os.path.join(PARSED_SHEETS_FOLDER, f'{file_name}_{i}'), encoding='utf_16', sep='\t')
            clean_sheet = clean_sheet.iloc[:, :-3] # To not display the auto generated columns
            clean_sheet = clean_sheet.to_html(na_rep=" ", justify="center", classes="table table-striped")
            html_table_with_caption = f'<h3 id="{ele}">Table {i+1}: {ele}</h3>{clean_sheet}'
            clean_sheets.append(html_table_with_caption)
    
        return render_template('confirmation_request.html', table_names=constants.TABLE_SPLITTER[database_table_name], clean_sheets=clean_sheets, file_name=file_name, database_table_name=database_table_name)
    
    except Exception as e:
        return general_error_handling(message=e, files_to_del=files_to_del['Before Upload'])


#TODO: Catch errors and delete stuff if catched.
@app.route('/confirmed', methods=['POST'])
@decorators.log_info(app)
def confirmed():
    try:
        file_name = session.get('file_name')
        database_table_name = session.get('database_table_name')
    except Exception as e:
        return general_error_handling(message=e, files_to_del=files_to_del['Before Upload'])
    
    try:
        for i, table_name in enumerate(constants.TABLE_SPLITTER.get(database_table_name)):
            clean_sheet = pd.read_csv(os.path.join(PARSED_SHEETS_FOLDER, f'{file_name}_{i}'), encoding='utf_16', sep="\t")
            clean_sheet.to_sql(name=table_name, 
                                schema=DATABASE_CONFIG['schema_name'], 
                                con=ENGINE, 
                                if_exists='append', 
                                index=False)
            
            # Test that uploaded data equals data in file:
            
            if '--no_upload_test' in sys.argv:
                pass
            else:
                integrity_test(table_name, file_name, clean_sheet)
    
    except SQLAlchemyError as e:
        # Catch any SQLAlchemy-related errors
        return general_error_handling(message=e.orig, revert_db=True, files_to_del=files_to_del['Before Upload'])
    
    except Exception as e:
        return general_error_handling(message=e, revert_db=True, files_to_del=files_to_del['Before Upload'])
    
    try:
        if '--no_file_test' in sys.argv and os.path.exists(os.path.join(ORIGINAL_FILES, file_name)):
            pass
        else:
            shutil.move(os.path.join(ORIGINAL_FILES, file_name), UPLOAD_FOLDER)
        
    except Exception as e:
        return general_error_handling(message=e, revert_db=True, files_to_del=files_to_del['Before Upload'])
                
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
        if session['error'] == True:
            return redirect(url_for("index"))
        
        file_name = session.get('file_name')
        database_table_name = session.get('database_table_name')

        all_tables = []
        for i, table in enumerate(constants.TABLE_SPLITTER.get(database_table_name)):
            uploaded_data = pd.read_sql(sql=f"SELECT * from {DATABASE_CONFIG['schema_name']}.{table} where from_spreadsheet = \'{file_name}\';", con=ENGINE)
            uploaded_data = uploaded_data.iloc[:, :-3] # To not display the auto generated columns
            uploaded_data = uploaded_data.to_html(na_rep=" ", justify="center", classes="table table-striped")
            all_tables.append(uploaded_data)
        return render_template('results.html', uploaded_data=all_tables, admin_emails=ADMIN_EMAIL)

    except Exception as e:
        return general_error_handling(message=e, delete_db_entries=True, 
                                      files_to_del=files_to_del['After Upload'])

@app.route('/error', methods=['GET'])
@decorators.log_info(app)
def error():
    error_message = session.get('error_message_user')
    session['error'] = True

    #error_message = request.args.get('error_message', 'An error occurred.')
    return render_template('error.html', email_send=session.get('email_send'), error_message=error_message, admin=ADMIN_EMAIL)

def integrity_test(database_table_name, file_name, clean_sheet):    
    uploaded_data = pd.read_sql(sql=f"SELECT * from {DATABASE_CONFIG['schema_name']}.{database_table_name} where from_spreadsheet = \'{file_name}\';", con=ENGINE)

    uploaded_data = uploaded_data.fillna(value=np.nan).reset_index(drop=True)
    clean_sheet = clean_sheet.fillna(value=np.nan).reset_index(drop=True)
            
    clean_sheet = clean_sheet.astype(str)
    uploaded_data = uploaded_data.astype(str)
            
    clean_sheet = clean_sheet.replace("NaT", "nan")
    uploaded_data = uploaded_data.replace("NaT", "nan")

    if database_table_name in constants.DB_GENERATED_COLUMNS:
        for db_generated_col in constants.DB_GENERATED_COLUMNS.get(database_table_name):
            if db_generated_col in list(uploaded_data.columns):
                uploaded_data.drop(db_generated_col, axis=1, inplace=True)
            
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
    return send_file(constants.MANUAL, as_attachment=True)

@app.route('/download/<path:filename>')
@decorators.log_info(app)
def download_file(filename): 
    return send_from_directory(constants.PATH_TO_STANDARD_SHEETS, filename, as_attachment=True)

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

def general_error_handling(message, revert_db=False, files_to_del={'original': False, 'parsed': False, 'uploaded': False}):
        '''Manages deletions to revert to original state'''
        file_name = session.get('file_name')
        user_error, admin_error = generate_html_message(message)
        if revert_db:
                database_table_name = session.get('database_table_name')
                for table in constants.TABLE_SPLITTER.get(database_table_name):
                    delete_db_entries(table, file_name=file_name)
        delete_files(file_name=file_name, **files_to_del)
        # session.clear()
        session['error_message_user'] = user_error
        current_time = datetime.now()
        session['error_message_admin'] = f'{str(current_time)}: {str(admin_error)}'
        return redirect(url_for('error'))

@app.route('/send_error_details', methods=['POST'])
@decorators.log_info(app)
def send_error_details():
    email = request.form['text']
    error_message = session.get('error_message_admin')
    message = f'{email} \n {error_message}'
    send_email.send('Error on upload website', message)
    session['email_send'] = True
    return redirect(url_for('error'))

@app.errorhandler(Exception)
def handle_uncaught_exception(e):
    current_time = datetime.now()
    app.logger.exception('Unhandled Exception: %s', traceback.format_exc())
    app.logger.exception('Unhandled Exception: %s', e)
    return f'Internal Server Error {current_time}', 500

if __name__ == '__main__':
    print("Start")
    production_args = constants.ALLOWED_COMMAND_LINE_ARGS['production']
    development_args = constants.ALLOWED_COMMAND_LINE_ARGS['development']

    if os.environ.get('RUN_MODE'):
        constants.RUN_MODE = os.environ.get('RUN_MODE').lower()
        if not constants.RUN_MODE in constants.RUN_MODE_OPTIONS:
            raise Exception(f'Unknown value for RUN_MODE')
    
    if constants.RUN_MODE == 'production':
        app.run(host='0.0.0.0', port=5100)
    elif constants.RUN_MODE == 'development':
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
