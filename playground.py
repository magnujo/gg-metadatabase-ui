import pandas as pd

# Sample DataFrame
data = {'A': [1, 2, None], 'B': [None, None, 6]}
df = pd.DataFrame(data)

# Check for rows with no data
no_data_rows = df

# Return False if there are any rows with no data
result = no_data_rows.any()

print(result)  # This will print False if there are one or more empty rows
print(df)

