from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import os
from scripts.ETLFunctions import clean_up
import pandas as pd
from sqlalchemy import create_engine
from utils.CustomExceptions import DontTriggerFileDeletion
import psycopg2
from psycopg2 import sql
import numpy as np
from pandas import testing


database_config = {
    'host': 'dandyweb01fl',
    'database': 'aedna_metadata',
    'port': '5432',
    'user': 'upload_user',
    'password': 'Ce65r-l+!D04',
    'schema_name': 'test'
}

database_config2 = {
    'host': database_config['host'],
    'dbname': database_config['database'],
    'port': database_config['port'],
    'user': database_config['user'],
    'password': database_config['password'],
}

engine = create_engine(f"postgresql://{database_config['user']}:{database_config['password']}@{database_config['host']}:{database_config['port']}/{database_config['database']}")
connection = psycopg2.connect(**database_config2)
cursor = connection.cursor()

app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/error')
def error():
    error_message = request.args.get('error_message', 'An error occurred.')
    return render_template('error.html', error_message=error_message)

@app.route('/success')
def success():
    message = request.args.get('message', 'Success.')
    return render_template('success.html', message=message)

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        file = request.files['file']

        if file.filename == '':
            raise DontTriggerFileDeletion('No selected file')
        
        database_table_name = request.form.get('database_table_name')
        if not database_table_name:
            raise DontTriggerFileDeletion('Please select a spreadsheet type')

        if file and allowed_file(file.filename):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)

            if os.path.exists(file_path):
                raise DontTriggerFileDeletion('A file with the exact same name has already been uploaded to the database. Contact database admin if you believe this is an error, or if you want to re-upload the file')
            
            else:
                # Use DontTriggerFileDelete before this and use Exception after. 
                file.save(file_path)
            
            file_name = os.path.split(file_path)[-1]

            clean_sheet = clean_up(tsv_file_path=file_path, database_table_name=database_table_name)

            # Adds rows about which user was responsible for the upload:
            clean_sheet['database_insert_by'] = database_config['user']

            # Adds information about which file the data came from:
            clean_sheet['from_spreadsheet'] = file_name

            # Adds infomation about what date and time the upload took place (only UTC seems to work, when testing below, because postgres converts any timezone to UTC)
            clean_sheet['database_insert_datetime_utc'] = pd.Timestamp.now(tz='UTC')
            # Convert to ns to enable testing (postgres converts to ns, when uploading)
            clean_sheet['database_insert_datetime_utc'] = clean_sheet['database_insert_datetime_utc'].astype('datetime64[ns, UTC]')

            clean_sheet.to_sql(name=database_table_name, schema=database_config['schema_name'], con=engine, if_exists='append', index=False)

            # Test that uploaded data equals data in file:
            uploaded_data = pd.read_sql(sql=f"SELECT * from {database_config['schema_name']}.{database_table_name} where from_spreadsheet = \'{file_name}\';", con=engine)
            uploaded_data = uploaded_data.fillna(value=np.nan).reset_index(drop=True)
            clean_sheet = clean_sheet.fillna(value=np.nan).reset_index(drop=True)

            print(clean_sheet.shape)
            print(uploaded_data.shape)
            testing.assert_frame_equal(uploaded_data, clean_sheet)

            if not clean_sheet.equals(uploaded_data):
                raise AssertionError("Upload failed. Contents of database is not equal to contents of file.")
            # Delete the file and the data in database, if above test fails.

            return redirect(url_for('success'))
        else:
            raise Exception('Invalid file type. Please upload a tab seperated .txt file. See manual below for help')

    except DontTriggerFileDeletion as tfd:
        print('File not deleted')
        #return render_template('index.html', error=str(tfd))
        return redirect(url_for('error', error_message=str(tfd)))

    except AssertionError as ae:
        if os.path.exists(file_path):
            os.remove(file_path)
        cursor.execute(f"DELETE FROM {database_config['schema_name']}.{database_table_name} where from_spreadsheet = \'{file_name}\';")
        connection.commit()
        cursor.close()
        connection.close()
        #return render_template('index.html', error=str(ae)) 
        return redirect(url_for('error', error_message=str(ae)))
    
    except Exception as e:
        print(f"Error: {e}")
        if os.path.exists(file_path):
            os.remove(file_path)
        print('deleted file')
        return redirect(url_for('error', error_message=str(e)))

@app.route('/download_manual')
def download_manual():
    manual_path = 'manual.txt'
    return send_file(manual_path, as_attachment=True)

@app.route('/download_robot_sampling_edna_example_sheet')
def download_robot_sampling_edna_example_sheet():
    file_path = 'example_sheets/robot sampling eDNA.xlsx'
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
