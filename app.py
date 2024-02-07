import constants
from flask import Flask, render_template, request, send_file, redirect, url_for, send_from_directory, session
import os
from constants import SHEET_TYPES, ADMIN_EMAILS
from scripts.ETLFunctions import clean_up
import pandas as pd
from utils.CustomExceptions import DontTriggerFileDeletion
import psycopg2
import numpy as np
from pandas import testing
import traceback
from constants import ENGINE, DATABASE_CONFIG, DATABASE_CONFIG_2, UPLOAD_FOLDER, ALLOWED_EXTENSIONS, ALLOWED_DATE_FORMATS

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html', SHEET_TYPES=SHEET_TYPES, ALLOWED_DATE_FORMATS=ALLOWED_DATE_FORMATS)

@app.route('/error')
def error():
    error_message = request.args.get('error_message', 'An error occurred.')
    return render_template('error.html', error_message=error_message)

@app.route('/success')
def success():
    uploaded_data = session.get('uploaded data')
    uploaded_data = pd.read_json(uploaded_data)
    # uploaded_data = pd.read_sql(sql=f"SELECT * from {DATABASE_CONFIG['schema_name']}.{database_table_name} where from_spreadsheet = \'{file_name}\';", con=ENGINE).iloc[:, :-3]
    #message = request.args.get('message', 'Success.')
    return render_template('success.html', uploaded_data=uploaded_data.iloc[:, :-3], admin_emails=ADMIN_EMAILS)

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        file = request.files['file']

        if file.filename == '':
            raise DontTriggerFileDeletion('No selected file')
        
        database_table_name = request.form.get('database_table_name')
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
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)

            if os.path.exists(file_path):
                raise DontTriggerFileDeletion(f'A file with the exact same name has already been uploaded to the database. Contact {constants.ADMIN_EMAILS} if you believe this is an error, or if you want to re-upload the file')
            
            else:
                # Use DontTriggerFileDelete before this and use Exception after. 
                file.save(file_path)
            
            file_name = os.path.split(file_path)[-1]

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

            clean_sheet.to_sql(name=database_table_name, 
                               schema=DATABASE_CONFIG['schema_name'], 
                               con=ENGINE, 
                               if_exists='append', 
                               index=False)

            # Test that uploaded data equals data in file:
            print(file_name)
            print(DATABASE_CONFIG['schema_name'])
            
            uploaded_data = pd.read_sql(sql=f"SELECT * from {DATABASE_CONFIG['schema_name']}.{database_table_name} where from_spreadsheet = \'{file_name}\';", con=ENGINE)

            uploaded_data = uploaded_data.fillna(value=np.nan).reset_index(drop=True)
            clean_sheet = clean_sheet.fillna(value=np.nan).reset_index(drop=True)
            
            clean_sheet = clean_sheet.astype(str)
            uploaded_data = uploaded_data.astype(str)
            
            clean_sheet = clean_sheet.replace("NaT", "nan")
            uploaded_data = uploaded_data.replace("NaT", "nan")
            
            
            #clean_sheet = clean_sheet.fillna(value=np.nan)
            #uploaded_data = uploaded_data.fillna(value=np.nan)
            
            # for i in range(len(clean_sheet.dtypes)):
            #     print(clean_sheet.dtypes[i] + " " + uploaded_data.dtypes[i])
          
             # TODO: Before deployment: Try to remove any sql statements that delete data. It is too dangerous. ONLY delete data from db if below tests that compares uploaded data with the cleaned sheet fails. Otherwise we might delete data by mistake. Make a custom DeleteDataException to make sure only that exception will delete data. Also make sure that the deletion is not only based on from_spreadsheet column as there might be cases where the same file names occur.
             # TODO: Instead of deleting data that doesnt pass the tests, upload the sheet to a duplicate database first and test on that. If the tests gets approved, only then upload to the actual db. When everything is in the actual db, maybe delete from the duplicate db.

            assert clean_sheet.dtypes.equals(uploaded_data.dtypes), f"Datatype mismatch between uploaded data and data in sheet, contact {constants.ADMIN_EMAILS}"
            print(len(clean_sheet.columns))
            print(len(uploaded_data.columns))
            testing.assert_frame_equal(uploaded_data, clean_sheet)

            if not clean_sheet.equals(uploaded_data):
                raise AssertionError("Upload failed. Contents of database is not equal to contents of file.")
            #return render_template('success.html', uploaded_data=uploaded_data.iloc[:, :-3], admin_emails=ADMIN_EMAILS)

            session['uploaded data'] = uploaded_data.to_json()

            return redirect(url_for("success"))
        else:
            raise Exception('Invalid file type. Please upload a tab seperated .txt file. See manual for help')

    # If user tries to upload a file that was already added this error is triggered, to make sure the original file doesnt get deleted.
    except DontTriggerFileDeletion as tfd:
        return redirect(url_for('error', error_message=str(traceback.format_exc())))
        # return redirect(url_for('error', error_message=str(tfd)))

    except AssertionError as ae:
        if os.path.exists(file_path):
            os.remove(file_path)
        connection = psycopg2.connect(**DATABASE_CONFIG_2)
        cursor = connection.cursor()
        # TODO: Also check that the file was uploaded less than 10 seconds ago. It might happen that two files have the same file name.
        cursor.execute(f"DELETE FROM {DATABASE_CONFIG['schema_name']}.{database_table_name} where from_spreadsheet = \'{file_name}\';")
        connection.commit()
        cursor.close()
        connection.close()
        #return render_template('index.html', error=str(ae)) 
        return redirect(url_for('error', error_message=str(traceback.format_exc())))
        # return redirect(url_for('error', error_message=str(ae)))
    
    except Exception as e:
        print(f"Error: {e}")
        if os.path.exists(file_path):
            os.remove(file_path)
        print('deleted file')
        connection = psycopg2.connect(**DATABASE_CONFIG_2)
        cursor = connection.cursor()
        cursor.execute(f"DELETE FROM {DATABASE_CONFIG['schema_name']}.{database_table_name} where from_spreadsheet = \'{file_name}\';")
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('error', error_message=str(traceback.format_exc())))
        # return redirect(url_for('error', error_message=str(e)))

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

if __name__ == '__main__':
    app.run(debug=True)

