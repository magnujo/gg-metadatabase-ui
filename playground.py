import platform
import os
from utils import queries as q
from constants.misc_constants import ENGINE

b = q.get_table_as_dataframe(ENGINE, "test_1", "field_sample")

print(b["Master ID/Parent Sample ID"].unique())
           

