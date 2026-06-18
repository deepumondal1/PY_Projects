from .auth_setup import AuthSetup
from .model.df_table_model import DF_TableModel
from .model.data_model import create_dynamic_data_model
import pandas as pd
import requests
from enum import Enum
import time
from datetime import datetime, timedelta
import json
from .dl_dataframe_db import DL_DataFrame_DB
from .db_store import DB_Table
from queue import Queue
from threading import Event

base_url = "https://mingle-ionapi.eu1.inforcloudsuite.com"
endpoint = f"{base_url}/LDX77VQ6U4GVV6M6_TST/DATAFABRIC/compass/v2"

# DATALAKE MANAGER
class JobStatus(Enum):
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"

class JobMethod(Enum):
    none = None
    start = "JOB_START"
    status = "JOB_STATUS"
    result = "JOB_RESULT"

class ProcessStatus(Enum):
    starting = "STARTING"
    waiting = "WAITING"
    running = "RUNNING"
    stopped = "STOPPED"
    completed = "COMPLETED"
    cancelled = "CANCELLED"

class DataLakeResponseManager:
    table_name:str=None
    db_table:DB_Table=None
    status:str=None
    query_id:str=None
    table_query:str=None
    next_url:str=None
    row_count:int=0
    code:int=0
    message:str=None
    method:JobMethod=JobMethod.none
    updated:str=datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    process_stat:ProcessStatus=ProcessStatus.waiting
    results:list=[]
    
    def __init__(self, index:int=0, table_name:str=None):
        self.table_name = table_name
        self.code = index
    
    def model_construct(self, **kwargs):
        # print(self.__dict__)
        self.table_name = kwargs.get('table_name',self.table_name)
        self.db_table = kwargs.get('db_table',self.db_table)
        self.status = kwargs.get('status',self.status)
        self.query_id = kwargs.get('query_id',self.query_id)
        self.table_query = kwargs.get('table_query',self.table_query)
        self.next_url = kwargs.get('next_url',self.next_url)
        self.row_count = kwargs.get('row_count',self.row_count)
        self.code = kwargs.get('code',self.code)
        self.message = kwargs.get('message',self.message)
        self.method = kwargs.get('method',self.method)
        self.updated = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        self.process_stat = kwargs.get('process_stat',self.process_stat)
        self.results = kwargs.get('results',self.results)

    def update_time(self):
        self.updated:str=datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    def to_table_str(self):
        return f"|{self.table_name}|{self.code}|{self.method}|{self.status}|{self.query_id}|{self.row_count}|{self.updated}|{self.process_stat}|"

    def view(self):
        method = f"[magenta]{self.method.value}[/magenta]" if self.method == JobMethod.start else f"[blue]{self.method.value}[/blue]" if self.method == JobMethod.status else f"[green]{self.method.value}[/green]" if self.method == JobMethod.result else f"{self.method.value}"
        process_stat = f"[yellow]{self.process_stat.value}[/yellow]" if self.process_stat == ProcessStatus.waiting else f"[green]{self.process_stat.value}[/green]" if self.process_stat == ProcessStatus.starting or self.process_stat == ProcessStatus.running else f"[red]{self.process_stat.value}[/red]"
        return {
            "Table Name":self.table_name,
            "Status":self.status,
            "Index":self.code,
            "Updated":self.updated,
            "Table Query":self.table_query,
            "Query Id":self.query_id,
            # "next_url":self.next_url,
            "Records":self.row_count,
            "Message":self.message,
            "Process":f"[bold]{method}[/bold]",
            "Process Status":f"[bold]{process_stat}[/bold]"
        }
        
    
class DataLakeManager:
    def __init__(self, auth:AuthSetup, db_df:DL_DataFrame_DB):
        self.auth = auth
        self.db_df = db_df
        self.drm_arr:dict[int, DataLakeResponseManager] = {}
        # self.drm_arr:dict = {}

    def runQuery1(self, table:dict|None=None, queue:Queue|None=None, stop_event:Event|None = None):
        while not stop_event.is_set():
            index = table.get('index',0)
            query:str = table.get('query',None)
            table_name = table.get('table_name', None)
            interval = table.get('interval', 3)
            last_updated = table.get('last_updated', None)
            table_fields = table.get('table_fields', None)
            bi_table_fields = table.get('bi_table_fields', None)
            drm = DataLakeResponseManager()
            print("runQuery1")
            
            # drm.table_name = table_name
            # drm.code = index
            # drm.process_stat = ProcessStatus.waiting
            drm.model_construct(table_name=table_name,code=index,process_stat=ProcessStatus.waiting)
            self.drm_arr[index] = drm
            queue.put(self.drm_arr)
            # time.sleep(5)
            stp1 = stop_event.wait(5)
            if stp1:
                print('stop_event_wait1')
                # stop_event.set()
            # yield query
            # print(query)
            drm.process_stat = ProcessStatus.running
            self.drm_arr[index] = drm
            queue.put(self.drm_arr)
            # time.sleep(5)
            if stop_event.wait(5):
                print('stop_event_wait2')
                stop_event.set()
            # yield 1
            # print(1)
            drm.process_stat = ProcessStatus.completed
            self.drm_arr[index] = drm
            queue.put(self.drm_arr)
            # time.sleep(5)
            if stop_event.wait(5):
                print('stop_event_wait3')
                # stop_event.set()
            # yield 'test'
            # print("test")
        
    def runQuery(self, table:DF_TableModel|None=None, queue:Queue|None=None, stop_event:Event|None = None, bypass_thread_func:bool=False):
        
        
        try:
            index = table.index
            table_name = table.table_name
            drm = DataLakeResponseManager(index=index, table_name=table_name)
            access_token=self.auth.access_token
                            
            query = table.query
            interval = table.interval
            obj_model = table.obj_model            
            
            
            def __init_setup__():
                # nonlocal query
                
                last_updated = table.last_updated
                
                if not query or not obj_model:
                    raise Exception('Table Query or Object Schema Model not present.')
                
                query2 = query
                if last_updated and table.create_db_table != 0:
                    last_updated_dt = datetime.strptime(last_updated,'%Y-%m-%d %H:%M:%S')
                    # last_updated_dt = last_updated_dt - timedelta(minutes=5)
                    # last_updated_dt = last_updated_dt - timedelta(hours=5,minutes=30) # TO UTC

                    # cond1= f'DATEDIFF(minute, \'{last_updated_dt}\', GETDATE()) > 0'
                    cond1= f'DATEDIFF(minute, \'{last_updated_dt}\', timestamp) > 0'
                    if query.lower().find('where') > -1:
                        query2 = f"{query2} and {cond1}"
                    else:
                        query2 = f"{query2} WHERE {cond1}"
                
                self.auth.fetch_refresh_token()
                # print(query)
                drm.table_query = query2
                self.drm_arr[index] = drm
                # print(query)
                # pass
            
            def __start_job__():
                # START JOB -------------------------------------------------------------
                drm.model_construct(process_stat=ProcessStatus.starting)
                resp = requests.post(f"{endpoint}/jobs/?access_token={access_token}", headers={"Content-Type":"text/plain","Accept": "application/json"}, data=query)
                drm.model_construct(method=JobMethod.start, process_stat=ProcessStatus.running)
                if resp.status_code != 202:
                    drm.model_construct(process_stat=ProcessStatus.starting, message=resp.json().get("message",None))
                    self.drm_arr[index] = drm
                    # queue.put(self.drm_arr)
                    raise Exception(f"Query Not Generated with status_code : {resp.status_code} | {resp.text}")

                resp_data = resp.json()
                drm.model_construct(query_id=resp_data["queryId"], status=resp_data["status"], next_url=resp_data["location"])
                self.drm_arr[index] = drm
                # -------------------------------------------------------------
            
            def __checking_job_status__():
                # CHECKING JOB STATUS -------------------------------------------------------------
                while True:
                    resp = requests.get(f"{endpoint}/jobs/{drm.query_id}/status/?timeout=0&access_token={access_token}", headers={"Accept": "application/json"})
                    drm.model_construct(method=JobMethod.status, process_stat=ProcessStatus.running)
                    if resp.status_code not in (201, 202):
                        drm.model_construct(message=resp.json().get("message",None), process_stat=ProcessStatus.stopped)
                        raise Exception(f"Query Not Generated with status_code : {resp.status_code} | {resp.text}")
                        
                    resp_data = resp.json()
                    if resp.status_code == 201:
                        drm.model_construct(status=resp_data["status"], row_count=resp_data.get("rowCount",0), next_url=resp_data["location"])
                        self.drm_arr[index] = drm
                        # queue.put(self.drm_arr)
                        break
                    
                    drm.model_construct(status=resp_data["status"], next_url=resp_data["location"])        
                    self.drm_arr[index] = drm
        
                    if drm.status == JobStatus.FAILED:
                        drm.model_construct(process_stat=ProcessStatus.stopped)
                        self.drm_arr[index] = drm
                        raise Exception(f"Query Not Generated with status_code : {resp.status_code} | {resp.text}")
            
                    time.sleep(5)                
                #  -------------------------------------------------------------
            
            def __fetch_result__():
                # FETCH RESULT -------------------------------------------------------------
                row_count = drm.row_count
                MAX_LIMIT = 100000
                offset = 0
                limit = MAX_LIMIT
                while True:
                    resp = requests.get(f"{endpoint}/jobs/{drm.query_id}/result/?offset={offset}&limit={limit}&access_token={access_token}", headers={"Accept": "application/json"})

                    drm.model_construct(method=JobMethod.result, process_stat=ProcessStatus.running)
                    if resp.status_code not in (200, 201, 202):
                        drm.model_construct(process_stat=ProcessStatus.stopped, message=resp.json().get("message",None))
                        raise Exception(f"Query Not Generated with status_code : {resp.status_code} | {resp.text}")
                        
                    resp_data = resp.json()
                    # print(resp_data)
                    drm.model_construct(process_stat=ProcessStatus.completed)
                    
                    # pure the data result by object model of schemas
                    data_results=[]
                    if resp_data and table.obj_model:
                        DataModel = create_dynamic_data_model(obj_model=table.obj_model)
                        data_results = list(map(lambda x: json.loads(DataModel(**x).model_dump_json(warnings='error')), resp_data))
                        # for result in drm.results:
                        #     data_model = DataModel(**result)
                        #     data_json = json.loads(data_model.model_dump_json(warnings='error'))
                        #     data_results.append(data_json)
                        
                        # update time
                    offset = limit + 1
                    limit += MAX_LIMIT
                    row_count -= limit
                    if row_count < limit:
                        break
                        
                table.update_time()
                drm.update_time()
                
                drm.results = data_results
                self.drm_arr[index] = drm 
                return drm.results
            
            # -------------------------------------------------------------------------------------------------
            
            if bypass_thread_func:
                __init_setup__()
                __start_job__()
                __checking_job_status__()
                result = __fetch_result__()
                return drm
            
            if not bypass_thread_func:
                while not stop_event.is_set():
                    
                    if not table:
                        raise Exception('Table Not Found')
                    
                    __init_setup__()
                    # print(table_name, index, query, last_updated, interval, self.drm_arr.get(index))
                    queue.put(self.drm_arr)    
                    __start_job__()
                    # print(table_name, index, query, last_updated, interval, self.drm_arr.get(index))
                    queue.put(self.drm_arr)
                    __checking_job_status__()
                    # print(table_name, index, query, last_updated, interval, self.drm_arr.get(index))
                    queue.put(self.drm_arr)
                    __fetch_result__()
                    # print(table_name, index, query, last_updated, interval, self.drm_arr.get(index))
                     
                    
                    queue.put(self.drm_arr)
                    stop_event.wait(timeout=5)
                    drm.model_construct(process_stat=ProcessStatus.waiting, method = JobMethod.none)
                    self.drm_arr[index] = drm  
                    queue.put(self.drm_arr)
                    
                    # print(self.drm_arr)
                    stop_ev = stop_event.wait(timeout=60*interval)
                    if stop_ev:
                        print('stop_ev')
                        return

            
        except Exception as err:
            if queue:
                queue.put(self.drm_arr)
                queue.put(None)
            if stop_event:
                stop_event.set()
            print('[ERROR runQuery]',err.__traceback__.tb_lineno, err)
            # return
            # drm.process_stat = ProcessStatus.waiting
            # raise Exception('ERROR in runQuery')
            

    def __map_fields__(self, resp_data, table_fields:str=None, bi_table_fields:str=None):
        # df = pd.DataFrame(resp_data)
        if resp_data:
            if table_fields:
                table_fields_arr = table_fields.split(",")
                df = pd.DataFrame(resp_data, columns=table_fields_arr)
                # print(df.to_json(orient="records"))
                if bi_table_fields:
                    bi_table_fields_arr = bi_table_fields.split(",")
                    mapper = {k:v for k,v in zip(table_fields_arr,bi_table_fields_arr)}
                    df.rename(columns=mapper, inplace=True, errors='ignore')
                    # print(df.to_json(orient="records"))

                return json.loads(df.to_json(orient="records"))
        return resp_data
