from typing import Any, Literal
from pydantic import BaseModel, ValidationError
from ..enums.datalake_datatype import DataLakeDataType
import pandas as pd



class ObjectSchemaModel(BaseModel):
    name:str
    description: str
    type:str
    datatype:DataLakeDataType
    maxLength:int|None
    localized:bool|None
    propertiesMaxLength:int|None
    properties:Any|dict|None
    required:list[str]|None
    format:None|Literal['date-time']
    enum:list[str|int]|None
    is_primarykey:bool=False
    
class ObjectModel(BaseModel):
    table_name:str
    schema_name:str
    table_schemas:list[ObjectSchemaModel]
    primary_keys:list

# def create_object_model(table_name:str, data:dict[str,dict:str,str|int|dict]):
def create_object_model(table_name:str, object_schema:dict):
    '''
    Creating Object Model contains 'table_name', 'schema_name' and 'table_schemas'
    '''
    try:
        if object_schema:
            schema_name = object_schema.get('name', None)
            schema_type = object_schema.get('type', None)
            schema = object_schema.get('schema', None)
            properties = object_schema.get('properties', None)
            primary_keys = []
            
            if not schema_type or not schema_name:
                raise Exception("'Name' or 'Type' is not present in Table Schema")
            
            if schema:
                schema_properties = schema.get('properties', None)
                
                # Creating DataFrame from Schema Properties
                df_schema = pd.DataFrame(schema_properties)
                df_schema.mask(df_schema.isna(),None, inplace=True)
                df_schema = df_schema.transpose()[~df_schema.transpose().index.str.contains(r"_kw$|_ref_")].transpose()
            
                data = df_schema.to_dict()
            
                table_schemas = dict(list(map(lambda x: 
                                (
                                    x[0]
                                    , ObjectSchemaModel.model_construct(
                                        **x[1]
                                        , name=x[0]
                                        , localized=x[1]['x-localized']
                                        , propertiesMaxLength=x[1]['x-PropertiesMaxLength']
                                        , datatype=DataLakeDataType(x[1]['type'])
                                )
                            )
                        , data.items())))
                
            if properties:
                identifier = properties.get('IdentifierPaths', None)
                for i in identifier:
                    itm = i.replace("$['","").replace("']","")
                    if itm in table_schemas:
                        primary_keys.append(itm)
                        table_schemas[itm].is_primarykey = True
                
            
            obj_model = ObjectModel.model_construct(
                table_name=table_name, 
                schema_name=schema_name, 
                table_schemas=list(table_schemas.values()),
                primary_keys=primary_keys
            )
            return obj_model
    except ValidationError as err:
        print('[ERROR create_object_model]', err.__traceback__.tb_lineno, err)
        return None