
import os, sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
parent_dir)
sys.path.append(parent_dir)
from app import app

from pathlib import Path
import unittest
from io import BytesIO
from flask import Flask
import pandas as pd



class TestFileUpload(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
        
        # Path to your existing test files directory
        self.test_data_dir = Path('path/to/your/test/files')  # Update this path

    def test_successful_upload_file1(self):
        """Test successful file upload with first example file"""
        file_path = self.test_data_dir / 'example1.tsv'  # Update filename
        
        with open(file_path, 'rb') as file:
            data = {
                'date_format': '%Y-%m-%d',  # Update format to match your file
                'decimal_point': '.',
                'thousands_seperator': ',',
                'encoding_type': 'utf-8',
                'database_table_name': 'test_table',
                'file': (file, file_path.name)
            }
            
            response = self.client.post(
                '/upload',  # Replace with your actual endpoint
                data=data,
                content_type='multipart/form-data'
            )
            
            self.assertEqual(response.status_code, 200)
            # Add assertions to verify the data was processed correctly

    def test_successful_upload_file2(self):
        """Test successful file upload with second example file"""
        file_path = self.test_data_dir / 'example2.tsv'  # Update filename
        
        with open(file_path, 'rb') as file:
            data = {
                'date_format': '%d/%m/%Y',  # Update format to match your file
                'decimal_point': ',',
                'thousands_seperator': '.',
                'encoding_type': 'utf-8',
                'database_table_name': 'test_table',
                'file': (file, file_path.name)
            }
            
            response = self.client.post(
                '/upload',
                data=data,
                content_type='multipart/form-data'
            )
            
            self.assertEqual(response.status_code, 200)

    def test_missing_file(self):
        """Test upload without a file"""
        data = {
            'date_format': '%Y-%m-%d',
            'decimal_point': '.',
            'thousands_seperator': ',',
            'encoding_type': 'utf-8',
            'database_table_name': 'test_table'
        }
        
        response = self.client.post(
            '/upload',
            data=data,
            content_type='multipart/form-data'
        )
        
        self.assertEqual(response.status_code, 400)

    def test_invalid_date_format(self):
        """Test upload with invalid date format"""
        file_path = self.test_data_dir / 'example1.tsv'  # Update filename
        
        with open(file_path, 'rb') as file:
            data = {
                'date_format': '%m-%d-%Y',  # Intentionally wrong format
                'decimal_point': '.',
                'thousands_seperator': ',',
                'encoding_type': 'utf-8',
                'database_table_name': 'test_table',
                'file': (file, file_path.name)
            }
            
            response = self.client.post(
                '/upload',
                data=data,
                content_type='multipart/form-data'
            )
            
            self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()