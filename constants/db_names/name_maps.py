'''
Helper file to maintain db column names.

If you want to change the naming of columns in the code simply refactor the variable names in this file.

If you want to change names in the database you can only do this if you also change the map tables in the database,
that map from code name to database name.
These are the maps that make sure that the code doesn't break if a column is renamed.

To make name callable without parentheses use a meta class like this:

# class MetaClass(type):
#      def __str__(cls):
#         return cls.name


'''

import pandas as pd
from utils import queries
from constants.db_connections import ENGINE_READ_ONLY, PSY_CONN_READ_ONLY



class NamedEntity(str):
	def __init__(self, db_id, db_name=None) -> None:
		self.__db_id = db_id
		self.__db_name = str(db_name)

	def __str__(self):
		return str(self.__db_name)

	def __repr__(self) -> str:
		return repr(self.__db_name)

	def get_id(self):
		return self.__db_id

	@classmethod
	def get_class_variables(cls):
		return {k: v for k, v in cls.__dict__.items() if not callable(v) and not k.startswith('__')}



class name_maps(NamedEntity):
	def __init__(self):
		super().__init__(db_name="name_maps", db_id=2)
  
	class column_names(NamedEntity):
		def __init__(self):
			super().__init__(db_name="column_names", db_id=20)

		# Columns:
		column_id = "column_id"
		column_name_db = "column_name_db"
		column_name_sheet = "column_name_sheet"
		table_id = "table_id"


	class table_names(NamedEntity):
		def __init__(self):
			super().__init__(db_name="table_names", db_id=19)

		# Columns:
		table_name = "table_name"
		sheet_template_name = "sheet_template_name"
		table_id = "table_id"
		schema_id = "schema_id"


	class schema_names(NamedEntity):
		def __init__(self):
			super().__init__(db_name="schema_names", db_id=21)
  
		# Columns:
		schema_name = "schema_name"
		schema_id = "schema_id"

def get_schema_name(schema_id: int):

	schema_name = name_maps()
	table_name = schema_name.schema_names()
	select_col = table_name.schema_name
	filter_col = table_name.schema_id

	query = f'''SELECT "{select_col}" FROM "{schema_name}"."{table_name}" WHERE "{filter_col}" = '%s' '''

	result = queries.execute_query(query, PSY_CONN_READ_ONLY, params=(schema_id,))

	if len(result) != 1:
		raise Exception("Admin error: Length of result not as expected")

	if len(result[0]) != 1:
		raise Exception("Admin error: Length of result not as expected")


	return str(result[0][0])


def get_table_name(table_id: int, template=False):

        schema = name_maps()
        table = schema.table_names()
        select_col = table.table_name
        if template:
            select_col = table.sheet_template_name
        filter_col = table.table_id

        query = f'''SELECT "{select_col}" FROM "{schema}"."{table}" WHERE "{filter_col}" = '%s' '''

        result = queries.execute_query(query, PSY_CONN_READ_ONLY, params=(table_id,))

        if len(result) != 1:
            raise Exception("Admin error: Length of result not as expected")

        if len(result[0]) != 1:
            raise Exception("Admin error: Length of result not as expected")


        return str(result[0][0])


def get_column_name(column_id: int, template=False):
    
	'''
	If template is set to True, the column name returned will be the column name in the Excel template.
	'''

	schema = name_maps()
	table = schema.column_names()
	select_col = table.column_name_db
	if template:
		select_col = table.column_name_sheet
	filter_col = table.column_id

	query = f'''SELECT "{select_col}" FROM "{schema}"."{table}" WHERE "{filter_col}" = %s '''

	result = queries.execute_query(query, PSY_CONN_READ_ONLY, params=(column_id,))

	if len(result) != 1:
		raise Exception("Admin error: Length of result not as expected")

	if len(result[0]) != 1:
		raise Exception("Admin error: Length of result not as expected")

	return str(result[0][0])   

def get_full_name_map():

    column_names = name_maps().column_names()
    table_names = name_maps().table_names()
    schema_names = name_maps().schema_names()

    q = f'''
	select * from "{name_maps()}"."{column_names}" cn 
	join "{name_maps()}"."{table_names}" tn on cn."{column_names.table_id}" = tn."{table_names.table_id}" 
	join "{name_maps()}"."{schema_names}" sn on tn."{table_names.schema_id}" = sn."{schema_names.schema_id}";
	'''

    df = pd.read_sql(q, ENGINE_READ_ONLY)

    return df


def sheet_to_db_rename_map(schema_name, table_name):
    # Check that schema and table exists:
    
    existing_tables = pd.read_sql(\
        f"select table_name from information_schema.tables where table_schema = '{schema_name}';", ENGINE_READ_ONLY)["table_name"]
    existing_tables_schemas = pd.read_sql(\
        f"select distinct table_schema from information_schema.tables;", ENGINE_READ_ONLY)["table_schema"]
    
    
    if schema_name in list(existing_tables_schemas) and table_name in list(existing_tables):
        pass
    else:
        raise Exception(f"Not able to make rename map because table {schema_name}.{table_name} does not exist")
    
    column_names = name_maps().column_names()
    table_names = name_maps().table_names()
    schema_names = name_maps().schema_names()

    q = f'''
	select "{column_names.column_name_sheet}", "{column_names.column_name_db}" from "{name_maps()}"."{column_names}" cn 
	join "{name_maps()}"."{table_names}" tn on cn."{column_names.table_id}" = tn."{table_names.table_id}" 
	join "{name_maps()}"."{schema_names}" sn on tn."{table_names.schema_id}" = sn."{schema_names.schema_id}"
 	where sn."{schema_names.schema_name}" = '{schema_name}' and tn."{table_names.table_name}" = '{table_name}' 
  	and cn."{column_names.column_name_sheet}" is not null;
	'''

    df = pd.read_sql(q, ENGINE_READ_ONLY)
    d = {key: value for (key, value) in df.values}

    return d


def db_to_sheet_rename_map(schema_name, table_name):
    rm = sheet_to_db_rename_map(schema_name, table_name)
    return {val: key for (key, val) in rm.items()}
    
