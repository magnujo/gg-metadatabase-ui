import pandas as pd

# Example DataFrame
data = {'Name': ['Alice', 'Bob', 'Charlie'],
        'Age': [25, 30, 35]}

df = pd.DataFrame(data)

# Iterate over a specific column (e.g., 'Name')
column_name = 'Name'
for index, value in df[column_name].items():
    print(f"Index: {index}, Value: {value}")
