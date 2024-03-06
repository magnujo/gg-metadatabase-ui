import constants
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))  # Add parent directory to sys.path



data_types_descriptions = {
    'text': f"Free text. Can contain any amount of {constants.db_character_encoding} characters", 
    'smallint': 'Integer number. Minus sign allowed. Min allowed value: -32768 max allowed value: 32767', 
    'integer': 'Integer number. Minus sign allowed. Min allowed value: -2147483648 max allowed value: 2147483647', 
    'int4range': 'Restricted mathematical notation of the form [{integer}, {integer}). Meaning only use "[" as the opening bracket and ")" as the closing bracket.',
    'decimal(scale,precision)': 'A decimal number. The precision of a numeric is the total count of significant digits in the whole number, that is, the number of digits to both sides of the decimal point. The scale of a numeric is the count of decimal digits in the fractional part, to the right of the decimal point. So the number 23.5141 has a precision of 6 and a scale of 4.',
    'numeric(scale,precision)': 'Same as decimal',
    'real': '4 bytes decimal number. Max 6 decimal digits. Same as decimal',
    'date': 'Date input with the format YYYY-MM-DD', 
    'timestamp with time zone': 'Effectivly the same as "date"',
    'timestamp without time zone': 'Effectivly the same as "date"', 
    }

