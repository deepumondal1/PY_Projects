from ..model.object_model import ObjectModel
from ..model.mysql_model import Table, Column
from ..enums.mysql_datatype import MYSQL_DType_From_DL

def mysql_create_table_query(table_name:str, data:ObjectModel) -> str:
    # q = ''
    
    # table_name = table_name
    # schemas = data.table_schemas
    
    # for schema in schemas:
    #     name = schema.name
    #     dtype = MYSQL_DType_From_DL[schema.datatype.name].value
        
    #     match schema.datatype.name:
    #         case 'string':
    #             if schema.maxLength:
    #                 dtype = f"VARCHAR({schema.maxLength})"
            
    #         case 'object':
    #             dtype = 'VARCHAR'
    #             if schema.propertiesMaxLength:
    #                 dtype = f"VARCHAR({schema.propertiesMaxLength})"
    
    # return q
    
    table_name = table_name
    schemas = data.table_schemas
    
    columns = []
    
    for schema in schemas:
        columns.append(
            Column(
                column_name=schema.name,
                column_type=MYSQL_DType_From_DL[schema.datatype.value],
                is_primary=schema.is_primarykey
            )
        )
    
    table = Table(table_name).columns(columns).if_not_exists().build_query()
    print(table)
    pass