import pandas as pd
from constants.db_connections import ENGINE
from utils import queries
from constants.db_connections import PSY_CONN

df = pd.read_excel("n:\SUN-GI-metadb-test\standard_spreadsheet_templates\Master Depths template.xlsx")
print(df)
