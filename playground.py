import pandas as pd
from utils import queries
from constants import postgres_types

df = queries.get_table_dtypes('field_sample_internal', 'test')

print(list(df[df['data_type'].isin(postgres_types['floating_point'])]['column_name']))

