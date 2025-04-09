import re

# Matches comma as t sep and period as decimal
case_1 = re.compile(r'^-?(?:(?:[1-9]\d{0,2}(?:,\d{3})+)|(?:[1-9]\d*)|0)(?:\.\d*[1-9])?$')
print('testing case 1')
pattern = case_1
    # Test cases
should_match = [
    "1",
    "12",
    "123456",
    "-123456",
    "0.5",
    "-0.5",
    "123.45",
    "123456.789",
    "1,000",
    "10,000.25",
    "-123,456,789.99",
    "1,123",
    "12,123",
    "1,000",
    "123,123,123",
    "235,789.97",
    "0.1" 
]

should_not_match = [
    "0123",
    "00.5",
    "1,00",
    "1,000.00",  # optional based on rule – tweak if .00 is allowed
    "000",
    "123.",
    ",123",
    "1,000,00",
    "123,1236",
    "123,1236,",
    "123,1236.",
    ".5",
    "234.000,23",
    "23.341,930",
    "23.3.3",
    "0,1"
    
]

# Run tests
print("✅ Should Match:")
for test in should_match:
    result = pattern.fullmatch(test)
    print(f"{test:>20} -> {'PASS' if result else 'FAIL'}")

print("\n❌ Should Not Match:")
for test in should_not_match:
    result = pattern.fullmatch(test)
    print(f"{test:>20} -> {'FAIL' if result else 'PASS'}")

# Matches a period as t sep and comma as decimal
case_2 = re.compile(r'^-?(?:(?:[1-9]\d{0,2}(?:\.\d{3})+)|(?:[1-9]\d*)|0)(?:,\d*[1-9])?$')

print('testing case 2')
pattern = case_2

    # Test cases
should_match = [
    "1",
    "12",
    "123456",
    "-123456",
    "0,5",
    "-0,5",
    "123,45",
    "123456,789",
    "1.000",
    "10.000,25",
    "-123.456.789,99",
    "1.123",
    "12.123",
    "1.000",
    "123.123.123",
    "235.789,97",
    "123,1236",
    "234.000,23",
    "0,1"
]

should_not_match = [
    "0123",
    "00.5",
    "00,5",
    "1,00",
    "1.00",
    "1,000.00",
    "1.000,00",
    "000",
    "00",
    "123.",
    "123,",
    ",123",
    ".123",
    "1,000,00",
    "1.000.00",
    "123.1236",
    "123,1236,",
    "123,1236.",
    "123.1236,",
    "123.1236.",
    ".5",
    ",5",
    "23.3.3",
    "23,3,3",
    "23.341,930"
]

# Run tests
print("✅ Should Match:")
for test in should_match:
    result = pattern.fullmatch(test)
    print(f"{test:>20} -> {'PASS' if result else 'FAIL'}")

print("\n❌ Should Not Match:")
for test in should_not_match:
    result = pattern.fullmatch(test)
    print(f"{test:>20} -> {'FAIL' if result else 'PASS'}")


# Matches a period as decimal and no t sep
case_3 = re.compile(r'^-?(?:(?:[1-9]\d*)|0)(?:\.\d*[1-9])?$')

pattern = case_3

print('case 3')
    # Test cases
should_match = [
    "1",
    "12",
    "123456",
    "-123456",
    "1.123",
    "12.123",
    "123.1236",
    "1.01",
    "123.231"
]

should_not_match = [
    "0123",
    "0,5",
    "00.5",
    "1.000",
    "-123.456.789,99",
    "123456,789",
    "234.000,23",
    "-0,5",
    "123,45",
    "123,1236",
    "123.123.123",
    "235.789,97",
    "00,5",
    "10.000,25",
    "1,00",
    "1.00",
    "1,000.00",
    "1.000,00",
    "000",
    "00",
    "123.",
    "123,",
    ",123",
    ".123",
    "1,000,00",
    "1.000.00",
    "123,1236,",
    "123,1236.",
    "123.1236,",
    "123.1236.",
    ".5",
    ",5",
    "23.3.3",
    "23,3,3",
    "23.341,930",
    "1,000",
    "10,000.25",
    "-123,456,789.99",
    "1,123",
    "12,123",
    "1,000",
    "123,123,123",
    "235,789.97",
    "235.789.97",
    "235.789.971",
]

# Run tests
print("✅ Should Match:")
for test in should_match:
    result = pattern.fullmatch(test)
    print(f"{test:>20} -> {'PASS' if result else 'FAIL'}")

print("\n❌ Should Not Match:")
for test in should_not_match:
    result = pattern.fullmatch(test)
    print(f"{test:>20} -> {'FAIL' if result else 'PASS'}")


# Matches a comma as decimal and no t sep
case_4 = re.compile(r'^-?(?:(?:[1-9]\d*)|0)(?:,\d*[1-9])?$')

pattern = case_4
print('case 4')
    # Test cases
should_match = [
    "1",
    "12",
    "123456",
    "-123456",
    "1,123",
    "12,123",
    "123,1236",
    "1,01",
    "123,231",
    "0,5",
    "-0,5",
    "123456,789",
    "123,45",
    "123,1236",
    "1,123",
    "12,123",
]

should_not_match = [
    "0123",
    "00.5",
    "1.000",
    "-123.456.789,99",
    "234.000,23",
    "123.123.123",
    "235.789,97",
    "00,5",
    "10.000,25",
    "1,00",
    "1.00",
    "1,000.00",
    "1.000,00",
    "000",
    "00",
    "123.",
    "123,",
    ",123",
    ".123",
    "1,000,00",
    "1.000.00",
    "123,1236,",
    "123,1236.",
    "123.1236,",
    "123.1236.",
    ".5",
    ",5",
    "23.3.3",
    "23,3,3",
    "23.341,930",
    "1,000",
    "10,000.25",
    "-123,456,789.99",
    "1,000",
    "123,123,123",
    "235,789.97",
    "235.789.97",
    "235.789.971",
    "1.123",
    "12.123",
    "123.1236",
    "1.01",
    "123.231"
]

# Run tests
print("✅ Should Match:")
for test in should_match:
    result = pattern.fullmatch(test)
    print(f"{test:>20} -> {'PASS' if result else 'FAIL'}")

print("\n❌ Should Not Match:")
for test in should_not_match:
    result = pattern.fullmatch(test)
    print(f"{test:>20} -> {'FAIL' if result else 'PASS'}")



# Matches a comma as t sep and no decimal

case_5 = re.compile(r'^-?(?:(?:[1-9]\d{0,2}(?:,\d{3})+)|(?:[1-9]\d*)|0)$')

pattern = case_5
print('case 5')
    # Test cases
should_match = [
    "1",
    "12",
    "123456",
    "-123456",
    "1,123",
    "12,123",
    "123,231",
    "1,000",
    "123,123,123"
]

should_not_match = [
    "0123",
    "00.5",
    "123,45",
    "1.000",
    "0,5",
    "123,1236",
    "-0,5",
    "123456,789",
    "123,1236",
    "1,01",
    "-123.456.789,99",
    "234.000,23",
    "123.123.123",
    "235.789,97",
    "00,5",
    "10.000,25",
    "1,00",
    "1.00",
    "1,000.00",
    "1.000,00",
    "000",
    "00",
    "123.",
    "123,",
    ",123",
    ".123",
    "1,000,00",
    "1.000.00",
    "123,1236,",
    "123,1236.",
    "123.1236,",
    "123.1236.",
    ".5",
    ",5",
    "23.3.3",
    "23,3,3",
    "23.341,930",
    "10,000.25",
    "-123,456,789.99",
    "235,789.97",
    "235.789.97",
    "235.789.971",
    "1.123",
    "12.123",
    "123.1236",
    "1.01",
    "123.231"
]

# Run tests
print("✅ Should Match:")
for test in should_match:
    result = pattern.fullmatch(test)
    print(f"{test:>20} -> {'PASS' if result else 'FAIL'}")

print("\n❌ Should Not Match:")
for test in should_not_match:
    result = pattern.fullmatch(test)
    print(f"{test:>20} -> {'FAIL' if result else 'PASS'}")

# Matches a period as t sep and no decimal

case_6 = re.compile(r'^-?(?:(?:[1-9]\d{0,2}(?:\.\d{3})+)|(?:[1-9]\d*)|0)$')

pattern = case_6
print('case 6')
    # Test cases
should_match = [
    "1",
    "12",
    "123456",
    "-123456",
    "1.123",
    "12.123",
    "123.231",
    "1.000",
    "123.123.123",
    "235.789.971",
    "123.123.123",
    "1.123",
    "12.123",
    "123.231"
]

should_not_match = [
    "0123",
    "00.5",
    "00,5",
    "123,45",
    "123.45",
    "1,000",
    "0,5",
    "0.5",
    "123,1236",
    "123.1236",
    "-0,5",
    "-0.5",
    "123456,789",
    "123456.789",
    "123,1236",
    "123.1236",
    "1,01",
    "1.01",
    "-123.456.789,99",
    "-123,456,789.99",
    "234.000,23",
    "234,000.23",
    "123,123,123",
    "235.789,97",
    "235,789.97",
    "10.000,25",
    "10,000.25",
    "1,00",
    "1.00",
    "1,000.00",
    "1.000,00",
    "000",
    "00",
    "123.",
    "123,",
    ",123",
    ".123",
    "1,000,00",
    "1.000.00",
    "123,1236,",
    "123,1236.",
    "123.1236,",
    "123.1236.",
    ".5",
    ",5",
    "23.3.3",
    "23,3,3",
    "23.341,930",
    "10,000.25",
    "-123,456,789.99",
    "235,789.97",
    "235.789.97",
    "123.1236",
    "1.01",
]

# Run tests
print("✅ Should Match:")
for test in should_match:
    result = pattern.fullmatch(test)
    print(f"{test:>20} -> {'PASS' if result else 'FAIL'}")

print("\n❌ Should Not Match:")
for test in should_not_match:
    result = pattern.fullmatch(test)
    print(f"{test:>20} -> {'FAIL' if result else 'PASS'}")

# Matches integers

case_7 = re.compile(r'^-?(?:(?:[1-9]\d*)|0)$')

pattern = case_7
print('case 7')
    # Test cases
should_match = [
    "1",
    "12",
    "123456",
    "-123456"
]

should_not_match = [
    "0123",
    "00.5",
    "00,5",
    "123,45",
    "123.45",
    "1,000",
    "0,5",
    "0.5",
    "123,1236",
    "123.1236",
    "-0,5",
    "-0.5",
    "123456,789",
    "123456.789",
    "123,1236",
    "123.1236",
    "1,01",
    "1.01",
    "-123.456.789,99",
    "-123,456,789.99",
    "234.000,23",
    "234,000.23",
    "123,123,123",
    "235.789,97",
    "235,789.97",
    "10.000,25",
    "10,000.25",
    "1,00",
    "1.00",
    "1,000.00",
    "1.000,00",
    "000",
    "00",
    "123.",
    "123,",
    ",123",
    ".123",
    "1,000,00",
    "1.000.00",
    "123,1236,",
    "123,1236.",
    "123.1236,",
    "123.1236.",
    ".5",
    ",5",
    "23.3.3",
    "23,3,3",
    "23.341,930",
    "10,000.25",
    "-123,456,789.99",
    "235,789.97",
    "235.789.97",
    "123.1236",
    "1.01",
]

# Run tests
print("✅ Should Match:")
for test in should_match:
    result = pattern.fullmatch(test)
    print(f"{test:>20} -> {'PASS' if result else 'FAIL'}")

print("\n❌ Should Not Match:")
for test in should_not_match:
    result = pattern.fullmatch(test)
    print(f"{test:>20} -> {'FAIL' if result else 'PASS'}")




