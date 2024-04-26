import psycopg2
from constants import DATABASE_CONFIG_2, DATABASE_CONFIG
schema = DATABASE_CONFIG['schema_name']
deleted_schema = f"{schema} deleted"
database_table_name = "flowcell"
upload_id = "asdasdsaadvsvs2231321assd"
q = f'''
BEGIN;

-- Delete data from the source table and return the deleted rows
WITH deleted_rows AS (
DELETE FROM "{schema}"."{database_table_name}" f 
WHERE upload_uuid = \'{upload_id}\'
RETURNING *
)
-- Insert the deleted rows into the destination table
INSERT INTO "{deleted_schema}"."{database_table_name}"  
SELECT *
FROM deleted_rows;

COMMIT;
'''
print(q)
