import pandas as pd
from utils import queries
from constants import postgres_types

df = queries.get_table_dtypes('field_sample_internal', 'test')


