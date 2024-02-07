import unittest
import pandas as pd
from datetime import datetime

# Import the function to be tested
from utils.parsers import parse_dates

class TestParseDates(unittest.TestCase):

    def setUp(self):
        # Create sample data
        self.sheet = pd.DataFrame({
            'date_col1': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'date_col2': ['01-01-2023', '01-02-2023', '01-03-2023'],
            'date_col3': ['01/01/2023', '01/02/2023', '01/03/2023'],
            'date_col4': ['2023/01/01', '2023/01/02', '2023/01/03']
        })

    def test_parse_dates_iso8601(self):
        result = parse_dates(self.sheet, ['date_col1'], 'YYYY-MM-DD')
        self.assertEqual(result['date_col1'].dtype, 'datetime64[ns]')
        self.assertTrue(all(isinstance(date, pd.Timestamp) for date in result['date_col1']))

    def test_parse_dates_dd_mm_yyyy(self):
        result = parse_dates(self.sheet, ['date_col2'], 'DD-MM-YYYY')
        self.assertEqual(result['date_col2'].dtype, 'datetime64[ns]')
        self.assertTrue(all(isinstance(date, pd.Timestamp) for date in result['date_col2']))

    def test_parse_dates_dd_slash_mm_slash_yyyy(self):
        result = parse_dates(self.sheet, ['date_col3'], 'DD/MM/YYYY')
        self.assertEqual(result['date_col3'].dtype, 'datetime64[ns]')
        self.assertTrue(all(isinstance(date, pd.Timestamp) for date in result['date_col3']))

    def test_parse_dates_yyyy_slash_mm_slash_dd(self):
        result = parse_dates(self.sheet, ['date_col4'], 'YYYY/MM/DD')
        self.assertEqual(result['date_col4'].dtype, 'datetime64[ns]')
        self.assertTrue(all(isinstance(date, pd.Timestamp) for date in result['date_col4']))

    def test_parse_dates_soft_false(self):
        result = parse_dates(self.sheet, ['date_col1'], 'YYYY-MM-DD', soft=False)
        self.assertEqual(result['date_col1'].dtype, 'datetime64[ns]')
        self.assertTrue(all(isinstance(date, pd.Timestamp) for date in result['date_col1']))

    def test_parse_dates_invalid_format(self):
        with self.assertRaises(Exception):
            parse_dates(self.sheet, ['date_col1'], 'invalid-format')

if __name__ == '__main__':
    unittest.main()