import inspect
import shutil
import constants
from flask import Flask, render_template, request, send_file, redirect, url_for, send_from_directory, session
import os
import sys
from constants import SHEET_TYPES, ADMIN_EMAILS, PARSED_SHEETS_FOLDER, ORIGINAL_FILES
from scripts.ETLFunctions import clean_up
import pandas as pd
import numpy as np
from pandas import testing
import traceback
from constants import ENGINE, DATABASE_CONFIG, UPLOAD_FOLDER, ALLOWED_EXTENSIONS, ALLOWED_DATE_FORMATS
from exception_utils import delete_files, delete_db_entries
from utils.CustomExceptions import DontTriggerFileDeletion

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html', SHEET_TYPES=SHEET_TYPES, ALLOWED_DATE_FORMATS=ALLOWED_DATE_FORMATS)

@app.route('/upload', methods=['POST'])
def upload_file():
    session.clear()
    session['visited_success'] = False
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
                if os.path.exists(os.path.join(UPLOAD_FOLDER, file.filename)):
                    raise DontTriggerFileDeletion(f'A file with the exact same name has already been uploaded to the database. Contact {constants.ADMIN_EMAILS} if you believe this is an error, or if you want to re-upload the file')
            
            # else:
                # Use DontTriggerFileDelete before this and use Exception after. 
            file.save(file_path)
            
            # file_name = os.path.split(file_path)[-1]

            clean_sheet = clean_up(tsv_file_path=file_path, 
                                   database_table_name=database_table_name, 
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
        else:
            raise DontTriggerFileDeletion('Invalid file type. Please upload a tab seperated .txt file. See manual for help')
    
        clean_sheet.to_csv(os.path.join(PARSED_SHEETS_FOLDER, file.filename), index=False, encoding='utf_16', sep="\t")

        return redirect(url_for("confirmation_request"))
    
    # If user tries to upload a file that was already added we don't delete anything other than the session data, 
    # to make sure the original file and db data doesn't get deleted.
    except DontTriggerFileDeletion as e1:
        print(str(e1))
        session.clear()
        delete_files(file_name=file_name, original=True, parsed=True)
        return redirect(url_for('error', error_message=str(traceback.format_exc())))
     
    except Exception as e:
        print(str(e))
        session.clear()
        delete_files(file_name=file_name, original=True, parsed=True)
        return redirect(url_for('error', error_message=str(traceback.format_exc())))


#TODO: Catch errors and delete stuff if catched.
@app.route('/confirmation_request', methods=['GET'])
def confirmation_request():
    try:
        if session['error'] == True:
            return redirect(url_for("index"))
        file_name = session.get('file_name')
        database_table_name = session.get('database_table_name')
        clean_sheet = pd.read_csv(os.path.join(PARSED_SHEETS_FOLDER, file_name), encoding='utf_16', sep='\t')
        # clean_sheet_json = session.get('clean_sheet')
        # clean_sheet = pd.read_json(clean_sheet_json)
        
        clean_sheet = clean_sheet.iloc[:, :-3] # To not display the auto generated columns
        clean_sheet = clean_sheet.to_html(na_rep=" ", justify="center", classes="table table-striped")
    
        return render_template('confirmation_request.html', clean_sheet=clean_sheet, file_name=file_name, database_table_name=database_table_name)
    except Exception as e:
        print(str(e))
        # Deletes file from original_sheets and parsed_sheets only, to restore original state 
        # of the folders.
        delete_files(file_name, original=True, parsed=True, uploaded=False)
        session.clear()
        return redirect(url_for('error', error_message=str(traceback.format_exc())))


#TODO: Catch errors and delete stuff if catched.
@app.route('/confirmed', methods=['POST'])
def confirmed():
    try:
        file_name = session.get('file_name')
        database_table_name = session.get('database_table_name')
        clean_sheet = pd.read_csv(os.path.join(PARSED_SHEETS_FOLDER, file_name), encoding='utf_16', sep="\t")
        
        clean_sheet.to_sql(name=database_table_name, 
                                schema=DATABASE_CONFIG['schema_name'], 
                                con=ENGINE, 
                                if_exists='append', 
                                index=False)
        # If errors happen from now on, delete the data just inserted to the database
    except Exception as e:
        print(str(e))
        # Deletes file from original_sheets and parsed_sheets only, to restore original state 
        # of the folders.
        delete_files(file_name, original=True, parsed=True, uploaded=False)
        session.clear()
        return redirect(url_for('error', error_message=str(traceback.format_exc())))
    
    else:
        try:
            if '--no_file_test' in sys.argv and os.path.exists(os.path.join(ORIGINAL_FILES, file_name)):
                pass
            else:
                shutil.move(os.path.join(ORIGINAL_FILES, file_name), UPLOAD_FOLDER)
            # If errors happen from now on, delete the file from the UPLOAD_FOLDER
            
        except Exception as e:
            print(str(e))
            # Deletes file from original_sheets and parsed_sheets only, to restore original state 
            # of the folders.
            delete_db_entries(database_table_name, file_name)
            delete_files(file_name, original=True, parsed=True, uploaded=False)
            session.clear()
            return redirect(url_for('error', error_message=str(traceback.format_exc())))
        
        else:    
            try:        
                # Test that uploaded data equals data in file:
                print(file_name)
                print(DATABASE_CONFIG['schema_name'])
                
                if '--no_upload_test' in sys.argv:
                    pass
                else:
                    integrity_test(database_table_name, file_name, clean_sheet)
                
            except Exception as e:
                print(f"Error: {e}")
                delete_files(file_name=file_name, original=True, parsed=True, uploaded=True)
                delete_db_entries(database_table_name=database_table_name, file_name=file_name)
                return redirect(url_for('error', error_message=str(traceback.format_exc())))
                        
            else:
                return redirect(url_for("success")) 

#TODO: Catch errors and delete stuff if catched.
@app.route('/cancel_upload', methods=['POST'])
def cancel_upload():
    # try:
    #     file_name = session.get('file_name')
    # except Exception as e:
    #     print(f"Error: {e}")
    #     session.clear()
    #     delete_files(file_name=file_name, original=True, parsed=True, uploaded=False)
    #     return redirect(url_for('error', error_message=str(traceback.format_exc())))
    # else:
    #     delete_files(file_name, original=True, parsed=True, uploaded=False)
    #     session.clear()
    return redirect(url_for("index"))

@app.route('/success', methods=['GET'])
def success():
    try:
        if session['error'] == True:
            return redirect(url_for("index"))
        
        file_name = session.get('file_name')
        database_table_name = session.get('database_table_name')
        # uploaded_data = session.get('uploaded data')
        # uploaded_data = pd.read_json(uploaded_data)
        uploaded_data = pd.read_sql(sql=f"SELECT * from {DATABASE_CONFIG['schema_name']}.{database_table_name} where from_spreadsheet = \'{file_name}\';", con=ENGINE)
        uploaded_data = uploaded_data.iloc[:, :-3] # To not display the auto generated columns
        uploaded_data = uploaded_data.to_html(na_rep=" ", justify="center", classes="table table-striped")
        # uploaded_data = build_table(uploaded_data, 'blue_light')
        # uploaded_data = pd.read_sql(sql=f"SELECT * from {DATABASE_CONFIG['schema_name']}.{database_table_name} where from_spreadsheet = \'{file_name}\';", con=ENGINE).iloc[:, :-3]
        #message = request.args.get('message', 'Success.')
        return render_template('results.html', uploaded_data=uploaded_data, admin_emails=ADMIN_EMAILS)

    except:
        session.clear()
        delete_db_entries(database_table_name=database_table_name, file_name=file_name)
        delete_files(file_name=file_name, original=True, uploaded=True, parsed=True)
        return redirect(url_for('error', error_message=str(traceback.format_exc())))

@app.route('/error')
def error():
    error_message = request.args.get('error_message', 'An error occurred.')
    session['error'] = True
    return render_template('error.html', error_message=error_message, admin=ADMIN_EMAILS)

def integrity_test(database_table_name, file_name, clean_sheet):
    uploaded_data = pd.read_sql(sql=f"SELECT * from {DATABASE_CONFIG['schema_name']}.{database_table_name} where from_spreadsheet = \'{file_name}\';", con=ENGINE)

    uploaded_data = uploaded_data.fillna(value=np.nan).reset_index(drop=True)
    clean_sheet = clean_sheet.fillna(value=np.nan).reset_index(drop=True)
            
    clean_sheet = clean_sheet.astype(str)
    uploaded_data = uploaded_data.astype(str)
            
    clean_sheet = clean_sheet.replace("NaT", "nan")
    uploaded_data = uploaded_data.replace("NaT", "nan")
            
            # for i in range(len(clean_sheet.dtypes)):
            #     print(clean_sheet.dtypes[i] + " " + uploaded_data.dtypes[i])
          
             # TODO: Before deployment: Try to remove any sql statements that delete data. It is too dangerous. ONLY delete data from db if below tests that compares uploaded data with the cleaned sheet fails. Otherwise we might delete data by mistake. Make a custom DeleteDataException to make sure only that exception will delete data. Also make sure that the deletion is not only based on from_spreadsheet column as there might be cases where the same file names occur.
             # TODO: Instead of deleting data that doesnt pass the tests, upload the sheet to a duplicate database first and test on that. If the tests gets approved, only then upload to the actual db. When everything is in the actual db, maybe delete from the duplicate db.

            # assert clean_sheet.dtypes.equals(uploaded_data.dtypes), f"Datatype mismatch between uploaded data and data in sheet, contact {constants.ADMIN_EMAILS}"
            # print(len(clean_sheet.columns))
            # print(len(uploaded_data.columns))
            
    testing.assert_frame_equal(uploaded_data, clean_sheet)

    if not clean_sheet.equals(uploaded_data):
        raise AssertionError("Upload failed. Contents of database is not equal to contents of file.")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/download_manual')
def download_manual():
    manual_path = 'manual.txt'
    return send_file(manual_path, as_attachment=True)

@app.route('/download_robot_sampling_edna_example_sheet', methods=['POST'])
def download_robot_sampling_edna_example_sheet():
    file_path = os.path.join('example_sheets', 'eDNA robot sampling.xlsx')
    return send_file(file_path, as_attachment=True)

@app.route('/download/<path:filename>')
def download_file(filename):
    example_sheets_directory = os.path.join(os.getcwd(), 'static', 'example_sheets')
    print(f"Downloading {example_sheets_directory} / {filename}")
    return send_from_directory(example_sheets_directory, filename, as_attachment=True)

def current_function_name():
    return inspect.currentframe().f_back.f_code.co_name

if __name__ == '__main__':
    app.run(debug=True)

