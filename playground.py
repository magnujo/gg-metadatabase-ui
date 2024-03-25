import pandas as pd

# Example DataFrames
df1 = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6], 'D': [7, 8, 9]})
df2 = pd.DataFrame({'B': [10, 11, 12], 'A': [13, 14, 15], 'C': [16, 17, 18]})

print(len(df1.columns) == len(df2.columns))

print(df1.columns.sort_values()==df2.columns.sort_values())

# Reorder columns of df1 to match the column positions of df2

try:
    df1 = df1[df2.columns]
except KeyError as e:
    raise Exception(f"Columns in database table does match number of columns in upload file: {e.args[0]}")

print("DataFrame 1:")
print(df1)
