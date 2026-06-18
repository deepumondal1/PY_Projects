import sqlite3
from enum import Enum
from typing import Any
from mysql.connector import connect
import os
import dotenv

dotenv.load_dotenv()

MYSQL_HOST = os.getenv('mysql_host')
MYSQL_PORT = os.getenv('mysql_port')
MYSQL_USER = os.getenv('mysql_user')
MYSQL_PASSWORD = os.getenv('mysql_password')
MYSQL_DB = os.getenv('mysql_database')

class DataType(Enum):
    text = 'TEXT'
    varchar255 = 'VARCHAR(255)'
    varchar = 'VARCHAR'
    integer = 'INTEGER'
    real = 'REAL'
    numeric = 'NUMERIC'
    boolean = 'BOOLEAN'
    datetime_ = 'DATETIME'

class Table_Fields:
    name:str
    datatype:DataType
    max_length:int
    enum:list[str|int]
    is_primarykey:bool
    is_null:bool

    def __init__(self, name:str, datatype:DataType, max_length:int, enum:list[str|int], is_primarykey:bool=False, is_null:bool=True):
        self.name = name
        self.datatype = datatype
        self.max_length = max_length
        self.enum = enum
        self.is_primarykey = is_primarykey
        self.is_null = is_null

class DB_Table:
    table_name:str
    length:int=0
    columns:list[str]
    rows:list[list[str]]
    table_fields:list[Table_Fields]

    def __init__(self, table_name:str, data:list[dict]):
        if len(data) > 0:
            self.table_name = table_name
            self.length = len(data)
            self.columns = list(data[0].keys())
            self.rows = list(map(lambda x: list(x.values()), data))
            # self.table_fields = list(map(lambda x: Table_Fields(x, DataType.text, is_primarykey= True if x=='pk' else False), self.columns))
            self.table_fields = list(map(lambda x: Table_Fields(x, DataType.varchar255, is_primarykey=True) if x=='pk' else Table_Fields(x, DataType.text), self.columns))

    def columns_to_tuple(self):
        return tuple(self.columns)

    def rows_to_tuple(self):
        return tuple(map(lambda x: tuple(x), self.rows))

    def columns_to_tuple_only_pk(self):
        data = []
        for x in self.table_fields: 
            if x.is_primarykey:
                data.append(x.name)
        return tuple(data)
        
    def columns_to_tuple_no_pk(self):
        data = []
        for x in self.table_fields: 
            if not x.is_primarykey:
                data.append(x.name)
        return tuple(data)
        # return tuple(map(lambda x: x.name if x.is_primarykey else None, self.table_fields))

class DBStoreManager:
    
    def __init__(self, db_name:str=None):
        # self.db_name = 
        self.db_name = db_name if db_name else MYSQL_DB

    def __enter__(self):
        # self.conn = sqlite3.connect(self.db_name)
        # self.conn.row_factory = sqlite3.Row 
        # self.cux = self.conn.cursor()   
        self.conn = connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=self.db_name)
        self.cux = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
        if exc_type:
            print(f"An exception occurred: {exc_val}")
            
        return False

    def close(self):
        self.cux.close()
        self.conn.close()
        
    def drop_table(self, table_name):
        self.cux.execute(f"DROP TABLE IF EXISTS {table_name}")
        
    def create_table(self, table_name:str, table_fields:list[Table_Fields]):
        table_fields_str = ','.join(map(lambda tf: ' '.join([tf.name, tf.datatype.value, 'NULL' if tf.is_null else 'NOT NULL', 'PRIMARY KEY' if tf.is_primarykey else '']), table_fields))
        query = f"""CREATE TABLE IF NOT EXISTS {table_name} ({table_fields_str}, 
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP )"""
        # print(query)
        self.cux.execute(query)

    def show_tables(self):
        # print(self.cux.execute("SELECT name FROM sqlite_schema WHERE type='table'").fetchall())
        records = self.cux.execute("SELECT * FROM sqlite_schema").fetchall()
        print(list(map(lambda row: dict(row) ,records)))

    def execute(self, query:str):
        if query.lower().find('select') > -1:
            return list(map(lambda x: dict(x), self.cux.execute(query).fetchall()))

    def insert_into(self, table_name:str, table:DB_Table):
        try:
            if table.length > 0:
                header = str(table.columns_to_tuple()).replace("'","")
                fields = ','.join(map(lambda x: str(x), table.rows_to_tuple()))
                pk_header = str(table.columns_to_tuple_only_pk()).replace(",)",")")
                on_update_pair_mysql = ','.join(map(lambda x: f"{x}=new.{x}" , table.columns_to_tuple_no_pk()))
                # on_update_pair_sqlite = ','.join(map(lambda x: f"{x}=EXCLUDED.{x}" , table.columns_to_tuple_no_pk()))
                # for x in table.columns: on_update_pair_sqlite += f"{x}=excluded.{x},"
                insert_query = f"INSERT INTO {table_name} {header} VALUES {fields} AS new ON DUPLICATE KEY UPDATE {on_update_pair_mysql};"
                # insert_query = f"INSERT INTO {table_name} {header} VALUES {fields} ON CONFLICT DO UPDATE SET {on_update_pair_sqlite};"
                # print(insert_query)
                self.cux.execute(insert_query)
                self.conn.commit()
                # self.fetch_all_from_table(table_name)

        except Exception as err:
            print('[ERROR Insert Into]', err)
        
    def fetch_all_from_table(self, table_name):
        records = self.cux.execute(f"SELECT * FROM {table_name}").fetchall()
        data = list(map(lambda row: dict(row) ,records))
        print(data)
        # print(pd.DataFrame(list(map(lambda row: dict(row) ,records))))
