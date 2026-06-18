import pandas as pd
from .default_code import DEFAULT_JOB_CARD_FOLDER, DEFAULT_WITEM_FOLDER


class DataFrameNew(pd.DataFrame):        
    def find_str(self, search_str:str|list, frow:int|None=None, trow:int|None=None, cols:int|None=None):
        newdf = self
        cols = len(newdf.columns) if cols is None else cols if cols > 0 else 1
        rw_slice = slice(frow,trow)
        index = False
        found=0
        try:
            for i in range(0,cols):
                if type(search_str) is str:
                    search_str = [search_str]
                for txt in search_str:
                    if found: break
                    ret1 = newdf.iloc[rw_slice,i].astype(str).str.startswith(txt, na=False)
                    if any(ret1):
                        index = ret1.idxmax(), i, txt
                        found=1
                        # print(txt)
                        break
        except Exception as err:
            pass
        return index

# def find_jc_path(jc_list:list)->list:
#     file = pathlib.Path(DEFAULT_JOB_CARD_FOLDER)
#     file_list = []
#     total_steps = len(jc_list)
#     for i, jc in enumerate(jc_list):
#         percentage = round(((i+1)/total_steps)*100)
#         file_list.extend(list(file.glob("**/*"+jc+"*.xls*")))
#         yield json.dumps({"data":{"jobcard":jc,"progress":percentage,"message":f"Finding... {jc} path"}})+"\n"

#     return file_list


def witem_file_generate(df2:pd.DataFrame)->pd.DataFrame:
    filename = "witem_format.xlsx"
    path = DEFAULT_WITEM_FOLDER + filename
    src_df = pd.DataFrame
    try:
        src_df = pd.read_excel(path)
        src_df.set_index('Key', inplace=True)
        drop_df2 = df2["Key"].drop_duplicates()
        filter_df2 = drop_df2[~drop_df2.isin(src_df.index)]
        
        src_df2 = pd.DataFrame(columns=["Key", "WItems", "RouteCode"])
        src_df2["Key"] = filter_df2
        src_df2.set_index('Key', inplace=True)
        src_df2["WItems"].fillna("",inplace=True)
        src_df2["RouteCode"].fillna(0,inplace=True)
        
        # src_df = src_df.merge(src_df2, how="outer")
        if not src_df2.empty:
            src_df = pd.concat([src_df,src_df2])
            src_df.to_excel(path)

    except FileNotFoundError:
        src_df = pd.DataFrame(columns=["Key", "WItems", "RouteCode"])
        src_df["Key"] = df2["Key"].drop_duplicates()
        src_df.set_index('Key', inplace=True)
        # print(df)
        src_df.to_excel(path)
    except Exception as err:
        print(err)

    src_df["WItems"].fillna("",inplace=True)
    src_df["RouteCode"].fillna(0,inplace=True)

    return src_df