import pandas as pd
from io import BytesIO
from .default_code import SAMPLE_FILE, Sheets, COMMON_COLUMNS, BOOKS_COLUMN, TDS_COLUMN


def generate_sample_file():
    books_sheet_col = COMMON_COLUMNS + BOOKS_COLUMN 
    tds_sheet_col = COMMON_COLUMNS + TDS_COLUMN 

    books_df = pd.DataFrame(columns = books_sheet_col)
    tds_df = pd.DataFrame(columns = tds_sheet_col)

    output = BytesIO()
    # print(Sheets.BOOKS.name,Sheets.BOOKS.value)
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        books_df.to_excel(writer, sheet_name=Sheets.BOOKS.value, index=False)
        tds_df.to_excel(writer, sheet_name=Sheets.TDS.value, index=False)

    output.seek(0)

    return output


