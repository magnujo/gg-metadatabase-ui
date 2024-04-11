import pandas as pd
import constants
df = pd. read_csv(r"static/demo_data/Standardized example sheets/230929_SampleSheet_RunA.txt", sep='\t', encoding='utf_16', dtype=str)
indicators = ["[Header]", "[Reads]", "[Settings]", "[Data]"]
indicator_indices = df[df['Column1'].isin(indicators)].index.tolist()
sections = {}
# Iterate over the indicator indices to create sections
for i in range(len(indicator_indices) - 1):
    start_index = indicator_indices[i]
    end_index = indicator_indices[i + 1]
    section_name = df.at[start_index, 'Column1']
    section_data = df.iloc[start_index + 1: end_index]
    sections[section_name] = section_data

# Adding the last section
last_section_name = df.at[indicator_indices[-1], 'Column1']
last_section_data = df.iloc[indicator_indices[-1] + 1:]
sections[last_section_name] = last_section_data



if sections["[Header]"].iloc[:, 2:].isna().all().all() == False:
    raise Exception("Parser only expects vales in Column1 and Column2 from [Header] but values were found in other columns")
if sections["[Data]"].iloc[:, 9:].isna().all().all() == False:
    raise Exception("Parser does not expect values in Column10 from [Data] but values were found")
if sections["[Data]"].iloc[:, :9].iloc[0].isna().any():
    raise Exception("Column name missing from [Data] section. Parser expect column names in Column1-Column9")

data = sections["[Data]"].drop(sections["[Data]"].columns[9], axis="columns")
data = data.reset_index(drop=True)
data.columns = data.iloc[0]
data = data.drop(0)

header = sections["[Header]"].dropna(axis="columns", how="all")
header = header.dropna(how="all")

reads = sections["[Reads]"].dropna(how="all", axis="columns")
reads = reads.dropna(axis="rows")
if not reads.dropna(axis="rows").shape == (2,1):
    raise Exception(f"Shape of [Reads] not as expected. Expects: 2 rows and 1 column, got {reads.shape[0]} rows and {reads.shape[1]} col")

for i in range(len(header)):
    col = header.iloc[i].iloc[0]
    val = header.iloc[i].iloc[1]
    data[col] = val

for i in range(len(reads)):
    col = f"Reads_{i}"
    val = reads.iloc[i].iloc[0]
    data[col] = val

