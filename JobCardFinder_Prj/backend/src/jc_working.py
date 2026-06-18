import pathlib
import pandas as pd
import json
from .default_code import DEFAULT_JOB_CARD_FOLDER
from .helper import DataFrameNew, witem_file_generate

class JCard_Working:
    jc_df:pd.DataFrame = pd.DataFrame()   
    org_jc_df:pd.DataFrame = pd.DataFrame()   

    def find_jc_path(self, jc_list:list):
        try:
            print('DEFAULT_JOB_CARD_FOLDER',DEFAULT_JOB_CARD_FOLDER)
            file = pathlib.Path(DEFAULT_JOB_CARD_FOLDER)

            if not file.exists():
                raise Exception('[NETWORKERROR] File Path Not Found. Not connected to Local Server.')
            
            file_list = []
            total_steps = len(jc_list)
            for i, jc in enumerate(jc_list):
                percentage = round(((i+1)/total_steps)*100)
                glob_file = file.glob("**/*"+jc+"*.xls*")
                
                for fPath in glob_file:
                    file_list.append(fPath)
                
                yield json.dumps({"data":{"jobcard":jc,"progress":percentage,"message":f"Finding path of Job Card No. [{jc}]"}})+"\n"
            
            self.file_list = file_list

        except Exception as err:
            error = str('[find_jc_path]', err, err.__traceback__.tb_lineno)
            print(error)
            raise Exception(error)


    def to_json(self):
        jc_df = self.jc_df.round()
        col_list = jc_df.columns.values.tolist()
        rows_list = jc_df.values
        json_data = [{ k: v for k, v in zip(col_list, rw_list.tolist())} for rw_list in rows_list]
        return json_data

    def generate_consump_df(self):
        try:
            df2 = self.jc_df
            file_list = self.file_list
            total_steps = len(file_list)
            for i, a in enumerate(file_list):
                percentage = round(((i+1)/total_steps)*100)
                fname = "".join(a.name.split(".")[:-1])
                print(fname)
                df = pd.read_excel(a, sheet_name=None, keep_default_na=False)
                try:
                    for shtname in list(df):
                        try:
                            # print("------------------------")
                            print(shtname)
                            newdf = DataFrameNew(df[shtname])
                            idx = newdf.find_str(["HT", "LT", "CONTROL", "INSTRUMENTATION", "THERMOCOUPLE", "POWER"], trow=10)
                            # print(idx)
                            # idx = is_job_card(shtname)
                            if idx:
                                r, c, txt = idx
                                match txt:
                                    case "HT" | "LT" if c > 7:
                                        idx = newdf.find_str("RMC", 10, 15)
                                        if idx:
                                            r, c, txt = idx
                                            idx1 = newdf.find_str("Conductor", r, r+1)
                                            idx2 = newdf.find_str("Material", r, r+1)
                                            idx3 = newdf.find_str("Cross Sectional", r, r+1)
                                            # print(r,idx1,idx2,idx3)
                                            if not idx1 or not idx2 or not idx3: break
                                            r1, c1, txt1 = idx1
                                            r2, c2, txt2 = idx2
                                            r3, c3, txt3 = idx3
                                            c0 = 8 if not c1 else c1-1
                                            c1 = 9 if not c1 else c1
                                            c2 = 10 if not c2 else c2
                                            c3 = 11 if not c3 else c3
                                            # print(r,c)
                                            # df["4CX35 SQMM 2XFY "][df["4CX35 SQMM 2XFY "].iloc[:,24].replace(0,"").str.isalnum().fillna(True)].iloc[:,[8,9,10]].astype(str).agg(lambda x: "-".join(x),axis=1)
                                            newdf = newdf.iloc[r:,:c+1]
                                            # newdf = newdf[newdf.iloc[:,c].replace("NA",0).replace(0,"").str.isalnum().fillna(True)]
                                        
                                            newdf = newdf[newdf.iloc[:,c].replace("NA",0).replace(0,"").str.isnumeric().fillna(True)]
                                            newdf.iloc[:,c3] = newdf.iloc[:,c3].where(~newdf.iloc[:,c3].str.isnumeric().fillna(True)).fillna("") # remove number from c3 column and only word
                                            newdf["Key"] = newdf.iloc[:,[c0,c1,c2,c3]].astype(str).agg(lambda x: "-".join(x), axis=1)
                                            newdf["Value"] = newdf.iloc[:,c] #.astype(float).round(2)
                                            newdf = newdf[["Key","Value"]]
                                            # print(list(newdf["Key"]))
                                            # print(list(newdf["Value"]))   
                                            
                                
                                    case "HT" | "LT" if c < 3:
                                        idx = newdf.find_str("RMC", 20, 25)
                                        if idx:
                                            r, c, txt = idx
                                            idx1 = newdf.find_str("STAGE", r, r+1)
                                            idx2 = newdf.find_str("MATL", r, r+1)
                                            idx3 = newdf.find_str("TYPE", r, r+1)
                                            idx4 = newdf.find_str("APPX", r, r+1)
                                            if not idx1 or not idx2 or not idx3 or not idx4: break
                                            r1, c1, txt1 = idx1
                                            r2, c2, txt2 = idx2
                                            r3, c3, txt3 = idx3
                                            r4, c4, txt4 = idx4
                                            # print(r,c)
                                            newdf = newdf.iloc[r:,:c+1]
                                            newdf = newdf[newdf.iloc[:,c].replace("NA",0).replace(0,"").str.isnumeric().fillna(True)]
                                            newdf.iloc[:,c1] = newdf.iloc[:,c1].where(newdf.iloc[:,c1]!="").ffill()
                                            newdf.iloc[:,c4] = newdf.iloc[:,c4].where(newdf.iloc[:,c4].astype(str).str.contains("Total")).fillna("") # remove c4 number to blanck and leave only total
                                            newdf["Key"] = newdf.iloc[:,[c1,c2,c3,c4]].astype(str).agg(lambda x: "-".join(x), axis=1)
                                            # newdf["Key"] = newdf.loc[:,["Key",c4]].astype(str).agg(lambda x: "".join(x), axis=1)
                                            newdf["Value"] = newdf.iloc[:,c].astype(float).round(2)
                                            newdf = newdf[["Key","Value"]]
                                            # print(list(newdf["Key"]))
                                            # print(list(newdf["Value"]))
                                            
                                        
                                    case "CONTROL" | "INSTRUMENTATION" | "THERMOCOUPLE" | "POWER" if c < 3:
                                        idx1 = newdf.find_str("STANDARD", frow=10, cols=1)
                                        idx2 = newdf.find_str(["Total","TOTAL"], frow=10, cols=1)
                                        if idx1 and idx2:
                                            r1, c1, txt1 = idx1
                                            r2, c2, txt2 = idx2
                                            # print(r1,r2)
                                            # df["3CX6 SQMM "].iloc[69:82,:3][df["3CX6 SQMM "].iloc[69:82,:3].iloc[:,2].str.isalnum().fillna(True)]
                                            newdf = newdf.iloc[r1:r2+1,:3]
                                            newdf = newdf[newdf.iloc[:,2].replace("NA",0).replace(0,"").str.isnumeric().fillna(True)]
                                            newdf["Key"] = newdf.iloc[:,0]
                                            newdf["Value"] = newdf.iloc[:,2].astype(float).round(2)
                                            newdf = newdf[["Key","Value"]]
                                            # print(list(newdf["Key"]))
                                            # print(list(newdf["Value"]))
                                newdf["Key"] = newdf["Key"].str.upper().str.replace(" ","")
                                # print(list(newdf["Key"]))
                                newdf["FileName"] = fname
                                newdf["SheetName"] = shtname
                                newdf = newdf[["FileName","SheetName","Key","Value"]]
                                df2 = pd.concat([df2,newdf], ignore_index=True)
                            
                        except Exception as err:
                            print(f'Error in Sheet [{shtname}]', err, err.__traceback__.tb_lineno)
                            continue
                
                except Exception as err:
                    print(f'Error in Workbook [{fname}]', err, err.__traceback__.tb_lineno)
                    continue

                yield json.dumps({"data":{"progress":percentage, "message":f"Generating Consumption of [{fname}] file."}})+"\n"

            self.jc_df = df2
            
        except PermissionError:
            raise Exception("PermissionError: File Already Opened by another User")
        except Exception as err:
            error = f"[generate_consump_df] [{err}] [LineNo-{err.__traceback__.tb_lineno}]"
            print(error)
            # yield json.dumps({"data":{"error":err}})+"\n"
            raise Exception(error)
    

    def transform_to_pivot_data(self):
        try:
            self.org_jc_df = self.jc_df
            df2 = self.jc_df
            src_df = witem_file_generate(df2)
            df2 = df2[['FileName', 'SheetName', 'Key', 'Value']]
            # print(df2.tail(5))
            df2 = df2[~df2.duplicated(['FileName', 'SheetName', 'Key'])]
            df2 = df2.merge(src_df, how="left", left_on="Key", right_index=True)
            
            # df2["WItems"]=df2[df2["WItems"]==""]["Key"] # Replace Blank Cell with Key Item Name
            pivot_df = df2.pivot_table(columns=["RouteCode","WItems"],index=["FileName","SheetName"],values="Value",aggfunc='sum',fill_value=0)
            print(df2.tail(1).to_json())
            print(pivot_df.tail(1).to_json())
            flat_pivot_df = pivot_df.reset_index()
            flat_pivot_df.columns = ["-".join(tuple(map(str,i))).replace(".0","") for i in flat_pivot_df.columns.values]
            flat_pivot_df = flat_pivot_df.round(2)

            total = flat_pivot_df.filter(like='TOTAL').agg('sum',axis=1)
            print(total)
            diff = flat_pivot_df.select_dtypes(['float64','int64']).filter(regex='-W|0-$', axis=1).agg('sum',axis=1) - total
            flat_pivot_df = flat_pivot_df.loc[:,~flat_pivot_df.columns.str.contains('TOTAL')]
            flat_pivot_df.insert(2,'TOTAL',total)
            flat_pivot_df.insert(2,'Diff',diff)

            yield json.dumps({"data":{"progress":100, "message":f"Processing into DataTable"}})+"\n"

            self.jc_df = flat_pivot_df
        
        except Exception as err:
            error = f"[transform_to_pivot_data] [{err}] [LineNo-{err.__traceback__.tb_lineno}]"
            print(error)
            yield json.dumps({"data":{"error":error}})+"\n"
            # raise Exception(err)

