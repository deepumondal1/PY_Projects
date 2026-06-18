from enum import Enum


class MYSQL_DType_From_DL(Enum):
    integer = 'INTEGER'
    string = 'VARCHAR'
    object = 'Any'
    number = 'FLOAT'
    boolean = 'BOOLEAN'
    