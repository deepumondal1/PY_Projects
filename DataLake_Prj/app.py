from src.auth_setup import AuthSetup
from src.datalake_manager import DataLakeManager, DataLakeResponseManager
from src.dl_dataframe_db import DL_DataFrame_DB
from src.db_store import DBStoreManager, DB_Table
from src.helper.helper import clear
from src.helper.requests_helper import get_object_schema, post_object_schema
from src.model.object_model import create_object_model
from src.model.data_model import create_dynamic_data_model
from src.model.mysql_model_sqlalchemy import create_mysql_dynamic_table
from src.model.mysql_model_pypika import create_table_query, drop_table_query, insert_multi_query, upsert_multi_query, upsert_single_query
from src.helper.mysql_helper import mysql_create_table_query
import json
import time
from rich.console import Console
from rich.table import Table
import threading
from queue import Queue

from datetime import datetime
import pandas as pd

data = {'access_token': 'eyJraWQiOiJrZzpjZDU0MzcxOC04ZWJlLTQ1NWItOTdhMy05MWJhYmI0MTk3ODYiLCJhbGciOiJSUzI1NiJ9.eyJTZXJ2aWNlQWNjb3VudCI6IkxEWDc3VlE2VTRHVlY2TTZfVFNUI0IzNkNmNzhCUDR3V2U5akJ2ZEVOM1pVTGgyX2FOWWp0b3Bqc0JxUmYwNUNEX3RvYVpyNzJaOXpkdnkwd0JEYnhQd1hTdXhBT0trdklHdGNmd3F5THRnIiwiVGVuYW50IjoiTERYNzdWUTZVNEdWVjZNNl9UU1QiLCJJZGVudGl0eTIiOiJhMTAzZTg0YS0wODYzLTQ5MzMtYTcxNi02ZGEwZDcwZmMxYmQiLCJFbmZvcmNlU2NvcGVzRm9yQ2xpZW50IjoiMCIsImdyYW50X2lkIjoiZDBlYTU0MDgtOWU4ZS00Mzc1LThjZmUtYjZlMDM2MjIzZGZkIiwiSW5mb3JTVFNJc3N1ZWRUeXBlIjoiQVMiLCJjbGllbnRfaWQiOiJMRFg3N1ZRNlU0R1ZWNk02X1RTVH5sM0pMZDAtVDcwOW9Ja1dYS04xWWlGOFZQOHYyY1NON0QxUmp6MTVWdkVvIiwianRpIjoiNWZiMzY2ODUtZDNkMy00ZWMzLTg2OTgtNmMwY2YxYmRmNGQzIiwiaWF0IjoxNzY3MjY1MjYxLCJuYmYiOjE3NjcyNjUyNjEsImV4cCI6MTc2NzI3MjQ2MSwiaXNzIjoiaHR0cHM6Ly9taW5nbGUtc3NvLmV1MS5pbmZvcmNsb3Vkc3VpdGUuY29tOjQ0MyIsImF1ZCI6Imh0dHBzOi8vbWluZ2xlLWlvbmFwaS5ldTEuaW5mb3JjbG91ZHN1aXRlLmNvbSJ9.ea9rs9q0PGCptfUB5OVMb0ZrOh7Dx2QsJjETxG0bciOjQd0fjXv_lXzfPSwqehD4jpaIZ0hoZFeQ8R81Y4K5PyF8lQvNzYUhBO5rIPI5NIhBN6Aqx0wHXDtDPUxH3jJE7viqw-dFZJ3gfPZY7gQjCWaK3AnWiIUK2tMzwd6AlnFzkqwxPtCk2sy3jGo9cM8rm_V1cIwQyMCvsDKK80lxNUt9zQ5IdWVOICh5-ip6MKsJU5l-uFhDbIEXxpHxsDzKk6RwBSloFuF0QewuWttX9Es6cgcRFpKfy_fJ-QZHdxWfHQNNOnItwScVftlZ5CNzNXfsGB3eE_C3rM2dLCMvEw', 'refresh_token': 'UptvwBGeG1Hzlu8AGqI2A57YiaHkumqy', 'token_type': 'Bearer', 'expires_in': 7200, 'expires_at': 1767272538}


stop_event = threading.Event()

def queue_handling(q:Queue): #, console:Console, table:Table):
    try:
        q_data:dict[int,DataLakeResponseManager] = q.get()
        # print('q_data', q.unfinished_tasks, q_data)
        if q_data is None:
            q.task_done()
            raise Exception('')
        
        if len(q_data) > 0:
            # Displaying the progress of each table records
            table = Table(title='DataLake Tables')
            header_list = list(DataLakeResponseManager().view().keys())
            for x in header_list: table.add_column(x, no_wrap = False)
            
            for k, d in q_data.items():
                table.add_row(*list(map(lambda x : str(x), list(d.view().values()))))
                
                if len(d.results) > 0:
                    with DBStoreManager() as db:
                        try:
                            db.cux.execute(upsert_multi_query(d.table_name, d.results))
                        except Exception as err:
                            print('[ERROR upsert]',err.__traceback__.tb_lineno, err)
                        db.conn.commit()
                # print('index no',k)
                dlm.db_df.update_time(k)
            
            console.clear()
            # clear()
            console.print(table)
        
        

        q.task_done()
    except Exception as err:
        print('[ERROR queue_handling]', err.__traceback__.tb_lineno, err)
        raise Exception('stopping q')
    

def quit(q:Queue):
    while not stop_event.is_set():
        # print('quit')
        q.put([])
        if stop_event.wait(1):
            stop_event.set()
        pass
    
    
    
if __name__ == '__main__': 
    console = Console()

    # auth = AuthSetup(access_token= data['access_token'], expires_at=data['expires_at'])
    auth = AuthSetup()
    db_df = DL_DataFrame_DB(file_name="datalake_db")

    dlm = DataLakeManager(auth, db_df)
    obj_schema_dict:dict[dict] = []

    print('test1')
    table_records = db_df.list_of_df_table_model()
    table_names = list(map(lambda x: x.name, table_records))
    obj_schema_dict:dict[dict] = post_object_schema(table_names, auth.access_token)
    table_records = db_df.list_of_df_table_model(obj_schema_dict=obj_schema_dict)
    print('test2')

    # # Mapping object_schema_model to table_records
    # for i, tbl in enumerate(table_records):
    #     if obj_schema_dict:
    #         obj_model = create_object_model(tbl.table_name, object_schema=obj_schema_dict[tbl.name])
    #         table_records[i].obj_model = obj_model
    #         # print(tbl.model_dump_json())
                
    # Looping all records which are yeilded to re-create the table.
    filter_table_records = list(filter(lambda x: x.create_db_table == 0, table_records))
    for i, tbl in enumerate(filter_table_records):  
        drm = dlm.runQuery(table=tbl, bypass_thread_func=True)
        # drm = DataLakeResponseManager()
        # drm.results = [{'ccal': 'test', 'ccal_ref_compnr': '7100', 'clan': 'ENG', 'clan_ref_compnr': '7100', 'clrt': '123', 'clrt_ref_compnr': '7100', 'compnr': '7100', 'cpcp': '', 'cpcp_ref_compnr': '7100', 'ctit': '', 'ctit_ref_compnr': '7100', 'cwoc': '', 'cwoc_ref_compnr': '7100', 'deleted': 'false', 'emno': 'KEI000092', 'guid': 'fZP+rGanSliTpzld4MiETQ', 'imag': 'URl/DxUmTZWQZsLOR/OORQ', 'loco': '', 'nama': 'RST4', 'namb': '', 'namc': '', 'namd': '', 'seak': 'RST4', 'sequencenumber': '16', 'timestamp': '2025-12-15T08:59:26.000Z', 'username': 'ravinder', 'pk': 'KEI000092'}, {'ccal': '', 'ccal_ref_compnr': '7100', 'clan': 'ENG', 'clan_ref_compnr': '7100', 'clrt': '', 'clrt_ref_compnr': '7100', 'compnr': '7100', 'cpcp': '', 'cpcp_ref_compnr': '7100', 'ctit': '', 'ctit_ref_compnr': '7100', 'cwoc': '', 'cwoc_ref_compnr': '7100', 'deleted': 'false', 'emno': 'KEI000091', 'guid': 'xWYD6JVlTBSBsb2fiNjq2g', 'imag': 'TLK1uOxfTpOzMYRd9rW/XQ', 'loco': 'ravinder', 'nama': 'RST3', 'namb': '', 'namc': '', 'namd': '', 'seak': 'RST3', 'sequencenumber': '16', 'timestamp': '2025-12-15T08:59:26.000Z', 'username': 'ravinder', 'pk': 'KEI000091'}, {'ccal': '', 'ccal_ref_compnr': '7100', 'clan': 'ENG', 'clan_ref_compnr': '7100', 'clrt': '', 'clrt_ref_compnr': '7100', 'compnr': '7100', 'cpcp': '', 'cpcp_ref_compnr': '7100', 'ctit': '', 'ctit_ref_compnr': '7100', 'cwoc': '', 'cwoc_ref_compnr': '7100', 'deleted': 'true', 'emno': 'KEI000093', 'guid': 'n4jMpsFQTU+rWIbXhxOw/A', 'imag': '6uqouXuqS8+N7Uv4AqTOow', 'loco': '', 'nama': 'RST5', 'namb': '', 'namc': '', 'namd': '', 'seak': 'RST5', 'sequencenumber': '19', 'timestamp': '2025-12-15T09:00:51.000Z', 'username': 'ravinder', 'pk': 'KEI000093'}]
        # print('results',len(drm.results))
        # if drm.results and tbl.obj_model:
        #     DataModel = create_dynamic_data_model(obj_model=tbl.obj_model)
        #     data_results=[]
        #     # data_results = map(lambda x: json.loads(DataModel(**x).model_dump_json(warnings='error')), drm.results)
        #     for result in drm.results:
        #         data_model = DataModel(**result)
        #         data_json = json.loads(data_model.model_dump_json(warnings='error'))
        #         data_results.append(data_json)
        #         pass
            
        print('---')
        print(drm.__dict__)
        # DROP - CREATE - UPSERT DATA
        if len(drm.results) > 0:
            data_results = drm.results
            with DBStoreManager() as db:
                db.cux.execute(drop_table_query(tbl.table_name))
                db.cux.execute(create_table_query(tbl.table_name, tbl.obj_model))
                try:
                    db.cux.execute(upsert_multi_query(tbl.table_name, data_results, primary_keys=tbl.obj_model.primary_keys))
                except Exception as err:
                    print('[ERROR upsert]',err.__traceback__.tb_lineno, err)
                db.conn.commit()
        
        # UPDATE TimeStamp and created fields in excel table
        dlm.db_df.update_column(tbl.index, 'create_db_table', 1)
        dlm.db_df.update_time(tbl.index)            
    
    # update table_records after updating the two fields['create_db_table', 'updated_at']
    # table_records = db_df.list_of_df_table_model(obj_schema_dict=obj_schema_dict)
    
    print('----completed upper part----')
    

# if __name__ == '__main__':    
#     # console = Console()
#     # table = Table(title='DataLake Tables')
    
#     # header_list = list(DataLakeResponseManager().view().keys())
#     # for x in header_list: table.add_column(x)

    
#     auth = AuthSetup(access_token= data['access_token'], expires_at=data['expires_at'])
#     db_df = DL_DataFrame_DB(file_name="datalake_db")
#     db_df.refresh_df()
#     dlm = DataLakeManager(auth, db_df)
#     table_records = json.loads(db_df.df.to_json(orient="records"))
#     # for tbl in json.loads(db_df.to_json(orient="records")):
    
#     # # By Constant Interval
#     # while True:
#     #     for i, tbl in enumerate(table_records):
#     #         tbl['index'] = i
#     #         gen = dlm.runQuery(table=tbl)
#     #         table.add_row(*list(map(lambda x: str(x), list(gen.values()))))
#     #         console.print(table)
#     #     time.sleep(60*2)
    
    # By Threading
    threads:list[threading.Thread] = []
    q = Queue()
    q_thread = None

    try:
        q_thread = threading.Thread(target=quit, args=(q,), daemon=True)
        q_thread.start()
        threads.append(q_thread)
        
        for i, tbl in enumerate(table_records):
            # tbl['index'] = i
            
            # print("-------------------")
            # print(datetime.now())
            # print("-------------------")
            
            
            thread = threading.Thread(target=dlm.runQuery, args=(tbl,q,stop_event,False,), daemon=True)
            thread.start()
            threads.append(thread)
            
            # # thread.join()
            # if (i+1) % 3 == 0 or len(table_records)==(i+1):
            #     # print('thread', thread)
            #     if thread:
            #         thread.join()
            
        # print(threads)
        while(t.is_alive() for t in threads):
            # print('----------------------')
            # print('threads',threads)
            queue_handling(q)
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        stop_event.set()
        
    except Exception as err:
        print('err', err)
    
    finally:
        pass
        print('a')
        stop_event.set()
        for t in threads: t.join()
        for t in threads: print(t.is_alive())
        
        print(q.empty(), q.unfinished_tasks)
        while not q.empty():
            q.get()
            q.task_done()
        print('Queue empty',q.empty(), q.unfinished_tasks)
        
