from typing import Any
from pypika import Table, Query, Column, CustomFunction
from pypika.dialects import MySQLQuery, MySQLQueryBuilder
from pypika.queries import ValueWrapper
from .object_model import ObjectModel, ObjectSchemaModel
from enum import Enum


class MYSQL_DataType(Enum):
    integer = 'INTEGER'
    string = 'VARCHAR'
    object = 'Any'
    number = 'FLOAT'
    boolean = 'BOOLEAN'
    datetime = 'DATETIME'
    tinytext = 'TINYTEXT'
    
def drop_table_query(table_name:str):
    q = str(Query.drop_table(table_name).if_exists().get_sql())
    q = q.replace("\"","")
    return q

def create_table_query(table_name:str, data:ObjectModel):
    table = Table(table_name)
    columns = []
    primary_columns = []
    
    for schema in data.table_schemas:
        name = schema.name
        dtype = MYSQL_DataType[schema.datatype.name].value
        
        match schema.datatype.name:
            case 'string':
                if schema.maxLength:
                    dtype = f"VARCHAR({schema.maxLength})"
                if schema.format == 'date-time':
                    # dtype = f"DATETIME"
                    dtype = MYSQL_DataType.tinytext.value
            
            case 'object':
                dtype = 'VARCHAR'
                if schema.propertiesMaxLength:
                    dtype = f"VARCHAR({schema.propertiesMaxLength})"
        
        columns.append(Column(name,dtype))
        if schema.is_primarykey:
            primary_columns.append(Column(name,dtype))
                    
    q = str(Query.create_table(table=table)\
            .if_not_exists()\
            .columns(*columns)\
            .columns('created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP')\
            .columns('updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')\
            .primary_key(*primary_columns)\
            .get_sql())
    q = q.replace("\"","")
    return q
    
def upsert_single_query(table_name:str, data:dict[str,Any]):
    
    '''
    UPSERT query of single entry for insert and update
    
    '''
    columns = data.keys()
    values = data.values()
    q = str(Query.into(table_name).columns(*columns).insert(*values).get_sql())
    q = q.replace("\"","")
    return q

def upsert_multi_query(table_name:str, data:list[dict[str,Any]], primary_keys:list=[]):
    
    '''
    UPSERT query of multiple values for insert and update
    
    '''
    if len(data) == 0:
        return ''
    
    table = Table(table_name)
    columns = data[0].keys()
    values = list(map(lambda x: tuple(x.values()), data))
    q = str(MySQLQuery.into(table)\
            .columns(*columns)\
            .insert(*values)\
            .get_sql())
    q = q.replace("\"","")
    
    not_including_primary_key_list = list(set(list(columns)).difference(set(primary_keys)))
    
    # header = ','.join(columns).replace("'","")
    # fields = ','.join(values)
    on_update_pair_mysql = ','.join(map(lambda x: f"`{x}`=VALUES(`{x}`)" , not_including_primary_key_list))

    # q = f"INSERT INTO {table_name} ({header}) VALUES {fields} AS new ON DUPLICATE KEY UPDATE {on_update_pair_mysql};"
    
    q += " AS new ON DUPLICATE KEY UPDATE " + on_update_pair_mysql
    return q

def insert_multi_query(table_name:str, data:list[dict[str,Any]]):
    
    '''
    INSERT multiple value query
    
    '''
    if len(data) == 0:
        return ''
    
    columns = data[0].keys()
    values = list(map(lambda x: tuple(x.values()), data))
    q = str(Query.into(table_name).columns(*columns).insert(*values).get_sql())
    q = q.replace("\"","")
    return q
