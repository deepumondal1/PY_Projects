from pydantic import BaseModel, ValidationError
from .object_model import ObjectModel
from enum import Enum
from datetime import datetime

class DF_TableModel(BaseModel):
    index:int|None=None
    job_id:str
    table_name:str
    create_db_table:int
    name:str
    query:str
    interval:int=15
    last_updated:str
    primary_key:str
    obj_model:ObjectModel=None
    
    def update_time(self):
        self.last_updated:str=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
def create_df_table_models(table_records:list[dict]):
    try:
        df_table_models:list[DF_TableModel] = list(map(lambda x : DF_TableModel.model_construct(index=x[0], **x[1]), enumerate(table_records)))
        # print(df_table_models)
        return df_table_models
    
    except ValidationError as err:
        print('[ERROR create_df_table_model]', err.__traceback__.tb_lineno, err)
        return None