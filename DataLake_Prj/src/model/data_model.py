from pydantic import create_model, Field, field_validator
from .object_model import ObjectModel, ObjectSchemaModel
from enum import Enum
from typing import Any, Optional, List
from datetime import datetime

class DM_DataType(Enum):
    integer = int
    string = str
    object = Any
    number = float
    boolean = bool
    datetime1 = datetime

def create_dynamic_data_model(obj_model:ObjectModel):
    fields = {}
    
    table_name = obj_model.table_name
    object_schemas = obj_model.table_schemas
    
    for obs in object_schemas:
        name = obs.name
        dtype = DM_DataType[obs.datatype.value].value
        
        # Handle Enums (Strings with restricted values)
        if hasattr(ObjectSchemaModel, 'enum'):
            dtype = Enum(f"{name}_enum", {str(val) if len(str(val))> 0 else 'None': str(val) for val in obs.enum})
        
        # if obs.format == 'date-time':
        #     dtype = DM_DataType.datetime1.value
        
        # Set constraints (max_length)
        field_constraints = Field(None)
        if obs.maxLength and dtype == str:
            field_constraints = Field(None, max_length=obs.maxLength)
            
        fields[name] = (Optional[dtype], field_constraints)
        
    return create_model(table_name, **fields)
    
    