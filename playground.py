import pandas as pd

# Example DataFrame
data = {'Name': ['John', 'Alice', 'John', 'Mike', 'Alice'],
        'Age': [25, 30, 25, 22, 30]}

df = pd.DataFrame(data)

# Remove duplicates
df_no_duplicates = df.drop_duplicates(subset=['Name'])

# Display result
print(df_no_duplicates)
