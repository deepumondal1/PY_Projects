import pathlib
from datetime import datetime
import pandas as pd
import numpy as np
import json

from .model.object_model import create_object_model
from .model.df_table_model import create_df_table_models, DF_TableModel

# DATLAKE EXCEL TABLE DATA
class DL_DataFrame_DB():
    def __init__(self, file_name:str="datalake_db"):
        self.file = f"{file_name}.xlsx"
        path = pathlib.Path(f".\\{self.file}")
        if not path.exists():
            self.__create_default__()

        self.refresh_df()

    def __create_default__(self):
        columns = ['job_id','table_name', 'query', 'interval', 'last_updated', 'table_fields', 'bi_table', 'bi_table_fields']
        self.df = pd.DataFrame({},columns=columns)
        self.df.to_excel(self.file, index=False, sheet_name='dl_table')

    def refresh_df(self):
        df = pd.read_excel(self.file, keep_default_na=False, na_values=" ")
        if 'create_db_table' in df.columns:
            df['create_db_table'] = df['create_db_table'].mask(df['create_db_table'] == "", 0)
        self.df = df 

    def update_column(self, i:int, col_name:str, col_val):
        if col_name in self.df.columns:
            self.df.at[i, col_name] = col_val
            with pd.ExcelWriter(self.file, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                self.df.to_excel(writer, index=False, sheet_name='dl_table')
                
    def update_time(self, i):
        if any(self.df.columns.isin(['last_updated'])):
            self.df.at[i, 'last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with pd.ExcelWriter(self.file, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                self.df.to_excel(writer, index=False, sheet_name='dl_table')
 
    def to_dict(self):
        table_records:list[dict] = json.loads(self.df.to_json(orient="records"))
        return table_records
    
    def list_of_df_table_model(self, obj_schema_dict:dict[dict]=None)->list[DF_TableModel]|None:
        self.refresh_df()
        table_records = json.loads(self.df.to_json(orient="records"))
        table_records = create_df_table_models(table_records=table_records)
        if obj_schema_dict:
            # Mapping object_schema_model to table_records
            for i, tbl in enumerate(table_records):
                if obj_schema_dict:
                    obj_model = create_object_model(tbl.table_name, object_schema=obj_schema_dict[tbl.name])
                    table_records[i].obj_model = obj_model
                    
        return table_records


