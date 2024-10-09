from utils import misc
from constants.db_connections import PSY_CONN, DATABASE_CONFIG_READ_ONLY



df = misc.get_comments(DATABASE_CONFIG_READ_ONLY['dbname'], 'test_1', 'field_sample', psy_conn=PSY_CONN)
print(df)