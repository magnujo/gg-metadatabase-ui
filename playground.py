import re


def parse_numbers(input_list, thousand_sep='', decimal_sep=''): 
    # Check that list contains , or . or both
        
    assert not any(thousand_sep in item for item in input_list), f'Did not find specified thousand seperator {thousand_sep} in data'
    assert not any(decimal_sep in item for item in input_list), f'Did not find specified thousand seperator {thousand_sep} in data'
    
    if thousand_sep and thousand_sep == decimal_sep:
        return False, "Thousand separator and decimal point cannot be the same."
        

def validate_number_input_1(input_list, thousand_sep=None, decimal_sep=None):
    """
    Validates a number input string according to the user-specified thousand and decimal separators.

    Parameters:
      input_str (str): The number string to validate.
      thousand_sep (str): The thousand separator character, or empty string if not used.
      decimal_sep (str): The decimal separator character, or empty string if not used.

    Returns:
      tuple: (bool, error_message or None)
    """
    # Normalize None to empty string
    thousand_sep = thousand_sep or ""
    decimal_sep = decimal_sep or ""

    # If both are provided, they must not be the same.
    if thousand_sep and thousand_sep == decimal_sep:
        return False, "Thousand separator and decimal point cannot be the same."

    
    
    # Check the decimal separator count if one is specified.
    if decimal_sep:
        if input_list.count(decimal_sep) > 1:
            return False, "Max 1 decimal point expected per number."
    
    if thousand_sep:
        if input_list.count(thousand_sep) < 1:
            return False, "Atleast one thousand seperator expected."

    # If both separators are provided and the input contains a decimal part,
    # ensure no thousand separator appears after the decimal separator.
    if thousand_sep and decimal_sep:
        last_decimal_index = input_list.rfind(decimal_sep)
        last_thousand_index = input_list.rfind(thousand_sep)
        if last_thousand_index > last_decimal_index:
            return False, "Thousand separator found after the decimal point."

    # Build the regex pattern based on which separators are provided.
    if thousand_sep and decimal_sep:
        # Both thousand and decimal separators are provided.
        ts_escaped = re.escape(thousand_sep)
        ds_escaped = re.escape(decimal_sep)
        # Allow either:
        #   - a plain sequence of digits (e.g., "1234")
        #   - a properly grouped number with thousand separators (e.g., "1,234")
        # With an optional decimal part.
        pattern = rf"^(?:\d+|\d{{1,3}}(?:{ts_escaped}\d{{3}})+)(?:{ds_escaped}\d+)?$"
    elif thousand_sep and not decimal_sep:
        # Only thousand separator provided: only integer values allowed.
        ts_escaped = re.escape(thousand_sep)
        pattern = rf"^(?:\d+|\d{{1,3}}(?:{ts_escaped}\d{{3}})+)$"
    elif not thousand_sep and decimal_sep:
        # Only decimal separator provided: allow an optional decimal part without grouping.
        ds_escaped = re.escape(decimal_sep)
        pattern = rf"^\d+(?:{ds_escaped}\d+)?$"
    else:
        # Neither thousand_sep nor decimal_sep is provided: allow only integers.
        pattern = r"^\d+$"

    if not re.fullmatch(pattern, input_list):
        return False, "Number format does not match the expected pattern."

    return True, None


def parse_numbers_1(strings, decimal_point='.', thousand_sep=','):
    """
    Parses a list of strings into floats or integers based on the given decimal point
    and thousand separator characters, while handling user input errors.
    
    :param strings: List of number strings to parse
    :param decimal_point: Character used as the decimal point (default is '.')
    :param thousand_sep: Character used as the thousand separator (default is ',')
    :return: List of parsed numbers (ints or floats)
    """
    if len(decimal_point) != 1 or len(thousand_sep) != 1:
        raise ValueError("Decimal point and thousand separator must be single characters.")
    if decimal_point == thousand_sep:
        raise ValueError("Decimal point and thousand separator cannot be the same character.")
    
    parsed_numbers = []
    for s in strings:
        try:
            # Check for invalid character placement
            if s.count(decimal_point) > 1:
                raise ValueError(f"Invalid format in '{s}': multiple decimal points.")
            
            # Ensure thousand separator is correctly placed (not at the start, end, or next to decimal point)
            if thousand_sep in s:
                if s.startswith(thousand_sep) or s.endswith(thousand_sep):
                    raise ValueError(f"Invalid format in '{s}': misplaced thousand separator.")
                if f"{thousand_sep}{decimal_point}" in s or f"{decimal_point}{thousand_sep}" in s:
                    raise ValueError(f"Invalid format in '{s}': thousand separator next to decimal point.")
                
                # Remove valid thousand separators (assumes they are properly placed)
                s = s.replace(thousand_sep, '')
            
            # Convert to float, then to int if no decimal part
            if decimal_point in s:
                s = s.replace(decimal_point, '.')  # Convert to standard decimal format
                num = float(s)
            else:
                num = int(s)
            
            parsed_numbers.append(num)
        except ValueError as e:
            print(f"Error parsing '{s}': {e}")
        
    return parsed_numbers


# Examples to demonstrate:
if __name__ == "__main__":
    test_cases = [
        # Both separators provided
        ("1,234,567.89", ",", "."),
        ("1234", ",", "."),             # Invalid: 1234 should be written as 1,234 if expecting a comma
        ("1,234", ",", "."),
        ("0,8", ",", "."),              # Invalid: mistaken use of thousand separator

        # Only thousand separator provided (only integers allowed)
        ("1,234", ",", ""),
        ("1234", ",", ""),              # Valid here because we allow plain digits when expecting only integers
        ("1,23", ",", ""),              # Invalid grouping

        # Only decimal separator provided
        ("1234.56", "", "."),
        ("1234", "", "."),              # Valid integer
        ("0.9", "", "."),

        # Neither separator provided: only plain integer allowed.
        ("1234567", "", ""),
        ("1234.56", "", "")             # Invalid: decimals not allowed
    ]

    for s, ts, ds in test_cases:
        valid, error = validate_number_input(s, thousand_sep=ts, decimal_sep=ds)
        sep_info = f"ts='{ts}' ds='{ds}'"
        if valid:
            print(f"Valid: {s} ({sep_info})")
        else:
            print(f"Invalid: {s} ({sep_info}) -- {error}")


