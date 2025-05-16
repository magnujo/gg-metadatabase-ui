import pandas as pd
import numpy as np

# Create a sample dataframe
data = {
    'A': [1, 2, np.nan, 4, 5],
    'B': [10, np.nan, 30, np.nan, 50]
}

df = pd.DataFrame(data)

# Print the original dataframe
print("Original DataFrame:")
print(df)

# Fill NaN values in column B with corresponding values from column A
df['B'] = df['B'].fillna(df['A'])

# Print the updated dataframe
print("\nUpdated DataFrame:")
print(df)