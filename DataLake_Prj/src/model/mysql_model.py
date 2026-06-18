from pydantic import BaseModel
from typing import Union, Tuple
from ..enums.mysql_datatype import MYSQL_DType_From_DL

class Column:
    column_name:str
    column_type:MYSQL_DType_From_DL
    is_primary:bool=False
    max_length:int|None = None
    is_null:bool|None = None
    
    def __init__(self,column_name:str,column_type:MYSQL_DType_From_DL, is_primary:bool=False, max_length:int|None = None,is_null:bool|None = None):
        self.column_name = column_name
        self.column_type = column_type
        self.is_primary = is_primary
        self.max_length = max_length
        self.is_null = is_null        
    
    def _column_create_str(self)->str:
        column_type = self.column_type.value
        
        match self.column_type.name:
            case 'string':
                column_type = 'VARCHAR(255)'
                if self.max_length:
                    column_type = f"VARCHAR({self.max_length})"
            
            case 'object':
                column_type = 'VARCHAR(255)'
                
        return ' '.join([
            self.column_name,
            column_type,
            'PRIMARY KEY' if self.is_primary else '',
            'NULL' if self.is_null else 'NOT NULL'
        ])
    

class Table:
    table_name:str
    
    def __init__(self, table_name:str):
        self.table_name = table_name
        self._columns:list[Column] = []
        self._values:list[list] = []
        self._primary_key = []
        self._if_not_exists = False
    
    def columns(self, columns:list[Column]):
        for column in list(columns):
            self._columns.append(column)
        return self
    
    def primary_key(self, *columns: Union[str, Column]):
        self._primary_key = [(column if isinstance(column, Column) else Column(column)) for column in columns]
        return self
        
    def if_not_exists(self):
        self._if_not_exists = True
        return self
    
    def build_create_query(self) -> str:
        if not self._columns:
            return ''
        
        # if not self._primary_key:
        #     return ''
    
        if self._if_not_exists:
            if_not_exists = 'IF NOT EXISTS'
            
        table_fields = []
        table_fields = ','.join((map(lambda col: f"{col._column_create_str()}", self._columns)))
        
        # for column in self._columns:
        #     print(column.column_name)
                
    
        sql = f"""CREATE TABLE {if_not_exists} {self.table_name} ({table_fields}
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP )"""
        
        return sql
    
    
    def build_insert_query(self):
        if not self._columns or not self._values:
            return ''
        
        table_fields = ','.join((map(lambda col: col.column_name, self._columns)))
        
        # table_fields_values = map(lambda val: val, self._values)

        sql = f"""INSERT INTO {self.table_name}  VALUES ({table_fields})"""