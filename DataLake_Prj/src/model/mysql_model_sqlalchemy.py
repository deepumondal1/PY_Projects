from sqlalchemy import Table, Column, MetaData, String
from sqlalchemy.dialects.mysql import VARCHAR, INTEGER, FLOAT, BOOLEAN, DATETIME
from .object_model import ObjectModel
from enum import Enum
from typing import Any

metadata = MetaData()

class MYSQL_DataType(Enum):
    integer = INTEGER
    string = VARCHAR
    object = Any
    number = FLOAT
    boolean = BOOLEAN

# class SQL_Model:
#     def create_table_query(self):
#         pass
    
#     def insert_query(self):
#         pass
    
#     def update_query(self):
#         pass
    
#     def upsert_query(self):
#         pass
    
#     def delete_query(self):
#         pass

def create_mysql_dynamic_table(obj_model:ObjectModel):
    try:
        table_name = obj_model.table_name
        table_schemas = obj_model.table_schemas
        columns = []
        
        for sch in table_schemas:
            name = sch.name
            dtype = MYSQL_DataType[sch.datatype.name].value
            
            match sch.datatype.name:
                case 'string':
                    if sch.maxLength:
                        dtype = VARCHAR(sch.maxLength)
                
                case 'object':
                    dtype = VARCHAR
                    if sch.propertiesMaxLength:
                        dtype = VARCHAR(sch.propertiesMaxLength)
                        
            columns.append(Column(name, dtype, primary_key=sch.is_primarykey))
        
        table = Table(table_name, metadata, *columns)
        return table
    
    except Exception as err:
        print('[ERROR create_dynamic_table]', err.__traceback__.tb_lineno, err)
        return None