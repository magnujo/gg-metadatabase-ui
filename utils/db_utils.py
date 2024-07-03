from utils.queries import get_table_information
import pandas as pd
from sqlalchemy import inspect 
import pandas as pd
 
class OrdinalPositionMaps:
    def __init__(self, pos_to_col, col_to_pos) -> None:
        self.pos_to_col = pos_to_col
        self.col_to_pos = col_to_pos
    

def get_ordinal_position_maps(table_name, schema_name, engine):
    '''
    Returns maps from ordinal_position to column name and vice versa.
    '''
    
    # Execute a query to get the column names
    q = f"""
        SELECT column_name, ordinal_position
        FROM information_schema.columns 
        WHERE table_name = '{table_name}' AND table_schema = '{schema_name}'
        ORDER BY ordinal_position
    """
    columns = pd.read_sql(q, con=engine)
    ordinal_pos_to_col_name = columns.set_index('ordinal_position')["column_name"].to_dict()
    col_name_to_ord_pos = {val: key for key, val in ordinal_pos_to_col_name.items()}
    
    for key, val in ordinal_pos_to_col_name.items():
        assert key == col_name_to_ord_pos[val]

    for key, val in ordinal_pos_to_col_name.items():
        assert key == col_name_to_ord_pos[val]
 
    return OrdinalPositionMaps(pos_to_col=ordinal_pos_to_col_name, col_to_pos=col_name_to_ord_pos)


# class PostgresTableDataframe(pd.DataFrame):
#     '''
#     Can use Postgres ordinal_position to access columns dynamically. 
#     IMPORTANT: This will create and store mapper from ordinal_position to column name, so it is no 100% guaranteed to be synced.
#     To get 100% sync guarantee, the dataframe needs to be updated everytime a __getitem__ is called.
#     '''
#     @classmethod
#     def from_postgres(cls, table_name: str, schema_name: str, engine, dtype=None):
#         cls.custom_column_mapper = get_column_mapper(table_name, schema_name, engine)
    
#         q = f'select * from "{schema_name}"."{table_name}"'
#         df = pd.read_sql(q, dtype=dtype, con=engine)
      
#         df = cls(df)

#         return df
    
#     # def col(cls, idx):
#     #     '''
#     #     Uses ordinal_position to access column(s).
#     #     '''
#     #     if isinstance(idx, list):
#     #         x = [cls.custom_column_mapper[key] for key in idx]
            
#     #     elif isinstance(idx, int):
#     #         x = cls.custom_column_mapper[idx]
        
#     #     else:
#     #         raise Exception("Not valid type")
        
#     #     return cls[x]
    
    
import pandas as pd
from sqlalchemy import create_engine, inspect
import psycopg2

class PostgresTableDataFrame(pd.DataFrame):
    '''
   Can use Postgres ordinal_position to access columns dynamically. 
   IMPORTANT: This will create and store mapper from ordinal_position to column name, so it is no 100% guaranteed to be synced.
   To get 100% sync guarantee, the dataframe needs to be updated everytime a get_column_by_position is called.
   '''

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)
        self._column_positions = None

    def load_from_postgres(self, engine, table_name, schema_name, dtype=None):
            q = f'select * from "{schema_name}"."{table_name}"'
            df = pd.read_sql(q, dtype=dtype, con=engine)
            super().__init__(df)
            self._column_positions = get_ordinal_position_maps(table_name, schema_name, engine)

    def col(self, ordinal_position):
        '''
        Uses ordinal_position to access column
        '''
        if self._column_positions is None:
            raise ValueError("DataFrame is not loaded from a PostgreSQL table.")
        # column_name = self._column_positions.get(position)
        if isinstance(ordinal_position, list):
            x = [self._column_positions[key] for key in ordinal_position]      
        elif isinstance(ordinal_position, int):
            x = self._column_positions[ordinal_position]  
        else:
            raise Exception("Not valid type")  
        
        if x is None:
            raise ValueError(f"No column found at position {ordinal_position}")
        
        return self[x]
        

# Usage example
# connection_string = "postgresql+psycopg2://user:password@host:port/database"
# table_name = "your_table_name"
# df = CustomDataFrame()
# df.load_from_postgres(connection_string, table_name)
# column_data = df.get_column_by_position(1)  # Access column by ordinal position
