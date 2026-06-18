import pandas as pd
import os
import sys
import pathlib as plib
from io import BytesIO
from datetime import datetime
# import xlsxwriter
# import openpyxl

class Employees:
    # "emp_id", "emp_name", "plant_name", "department_name", "shift", "photo1","photo2"
    EMP_ID = 'emp_id'
    EMP_NAME = 'emp_name'
    PLANT_NAME = 'plant_name'
    DEPARTMENT_NAME = 'department_name'
    SHIFT = 'shift'
    PHOTO_1 = 'photo1'
    PHOTO_2 = 'photo2'
    
    def index(self):
        return self.EMP_ID
    
    def to_array(self):
        return [self.EMP_ID, self.EMP_NAME, self.PLANT_NAME, self.DEPARTMENT_NAME, self.SHIFT, self.PHOTO_1, self.PHOTO_2]    

class Attendance_df_db:
    def __init__(self):
        self.__init_dir_or_file_setup__()
        
        file = plib.Path(self.file_path)
        
        if not file.exists():
            self.__create_default__()
        else:
            self.__get_default__()
            
    def __init_dir_or_file_setup__(self):
        self.file_name = "attendance_db.xlsx"
        curr_path = os.getcwd()
        dir_path = plib.Path(f"{curr_path}\\db")
        if not dir_path.exists():
            print(dir_path)
            os.mkdir(dir_path)
        self.file_path = plib.Path(f"{dir_path}\\{self.file_name}")
        
            
    def __create_default__(self):
        output=BytesIO()
        # df = pd.DataFrame([])
        # df.to_excel(self.file_path)
        self.df_dept = pd.DataFrame(columns=["department_name","name"]).set_index("department_name")
        self.df_plant = pd.DataFrame(columns=["plant_name","name"]).set_index("plant_name")
        self.df_shift = pd.DataFrame(columns=["shift", "from_time", "to_time"]).set_index("shift")
        self.df_employees = pd.DataFrame(columns=["emp_id", "emp_name", "plant_name", "department_name", "shift", "photo1","photo2"]).set_index("emp_id")
        # self.df_employees = pd.DataFrame(columns=Employees.to_array()).set_index(Employees.index())
        self.df_attendance = pd.DataFrame(columns=["date", "emp_id", "present_absent"]).set_index(["date","emp_id"])
        
        # self.df_dept = pd.DataFrame(columns=["department_name"])
        # self.df_plant = pd.DataFrame(columns=["plant_name"])
        # self.df_shift = pd.DataFrame(columns=["shift", "from_time", "to_time"])
        # self.df_employees = pd.DataFrame(columns=["emp_id", "emp_name", "plant_name", "department_name", "shift"])
        # self.df_attendance = pd.DataFrame(columns=["date", "emp_id", "present_absent"])
        
        # with pd.ExcelWriter(output) as writer:
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # with pd.ExcelWriter(self.file_path) as writer:
            self.df_plant.to_excel(writer, "Master_Plant")
            self.df_dept.to_excel(writer, "Master_Department")
            self.df_shift.to_excel(writer, "Master_Shift")
            self.df_employees.to_excel(writer, "Employees")
            # self.df_employees.to_excel(writer, Employees.__name__)
            self.df_attendance.to_excel(writer, "Attendance")
            
        output.seek(0)
        excel_data_bytes = output.getvalue()
        
        with open(self.file_path, 'wb') as f:
            f.write(excel_data_bytes)
    
    def __get_default__(self):  
        self.df_plant = pd.read_excel(self.file_path, sheet_name="Master_Plant").set_index("plant_name").drop(columns=['Unnamed: 0'],errors='ignore')
        self.df_dept = pd.read_excel(self.file_path, sheet_name="Master_Department").set_index("department_name").drop(columns=['Unnamed: 0'],errors='ignore')
        self.df_shift = pd.read_excel(self.file_path, sheet_name="Master_Shift").set_index("shift").drop(columns=['Unnamed: 0'],errors='ignore')
        self.df_employees = pd.read_excel(self.file_path, sheet_name="Employees").set_index("emp_id").drop(columns=['Unnamed: 0'],errors='ignore')
        # self.df_employees = pd.read_excel(self.file_path, sheet_name="Employees").set_index(Employees.index()).drop(columns=['Unnamed: 0'],errors='ignore')
        self.df_attendance = pd.read_excel(self.file_path, sheet_name="Attendance").set_index(["date","emp_id"]).drop(columns=['Unnamed: 0'],errors='ignore')
        
    def __modify_target_sheet__(self,df:pd.DataFrame, target_sheet):
        with pd.ExcelWriter(self.file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.reset_index().to_excel(writer, sheet_name=target_sheet)
        
        
    def to_json(self, df:pd.DataFrame):
        col_list = df.columns.values.tolist()
        rows_list = df.values
        json_data = [{ k: v for k, v in zip(col_list, rw_list.tolist())} for rw_list in rows_list]
        return json_data
    
        
    # ------------------ Plant Section ----------------
    
    def get_dashboard_data(self):
        try:
            df_attendance = self.df_attendance.reset_index()
            
            totalEmployees = len(self.df_employees)
            totalPresent = len(df_attendance[df_attendance[['date','present_absent']].isin([datetime.now().strftime('%Y-%m-%d'),'present']).all(axis=1)])
            totalAbsent = totalEmployees-totalPresent
            totalPlants = len(self.df_plant)
            totalDepartments = len(self.df_dept)
            
            # print(self.df_attendance)
            # print(df_attendance.index, df_attendance.columns, df_attendance, df_attendance.isin({'date':datetime.now().strftime('%Y-%m-%d'),'present_absent':'present'}))
            return {
                "totalEmployees" : totalEmployees,
                "totalPresent" : totalPresent,
                "totalAbsent" : totalAbsent,
                "totalPlants" : totalPlants,
                "totalDepartments" : totalDepartments,
            }
        except Exception as err:
            print('Error-> ', err.__traceback__.tb_lineno, err)
        
    # ------------------ Plant Section ----------------
    
    def get_plant_name(self):
        return self.df_plant
        
    def set_plant_name(self, name:str):
        name = name.upper()
        self.df_plant.loc[name]= name
        self.__modify_target_sheet__(self.df_plant, "Master_Plant")
    
    def remove_plant_name(self, name:str):
        name = name.upper()
        self.df_plant = self.df_plant[~self.df_plant.index.isin([name])]
        self.__modify_target_sheet__(self.df_plant, "Master_Plant")
        
    # ------------------- Department Section ------------------
    
    def get_department_name(self):
        return self.df_dept
    
    def set_department_name(self, name:str):
        name = name.upper()
        self.df_dept.loc[name]= name
        self.__modify_target_sheet__(self.df_dept, "Master_Department")
    
    def remove_department_name(self, name:str):
        name = name.upper()
        self.df_dept = self.df_dept[~self.df_dept.index.isin([name])]
        self.__modify_target_sheet__(self.df_dept, "Master_Department")
        
    # --------------------- Shift Section ----------------------
    
    def get_shifts(self):
        self.df_shift.reset_index(inplace=True)
        self.df_shift.rename(columns={"shift":"name", "from_time":"startTime", "to_time":"endTime"}, inplace=True)
        return self.df_shift
    
    def set_shift(self, name:str, from_time, to_time):
        name = name.upper()
        self.df_shift.loc[name]= [from_time, to_time]
        self.__modify_target_sheet__(self.df_shift, "Master_Shift")
    
    def remove_shift(self, name:str):
        name = name.upper()
        self.df_shift = self.df_shift[~self.df_shift.index.isin([name])]
        self.__modify_target_sheet__(self.df_shift, "Master_Shift")
        
    # --------------------- Employee Section ----------------------
        
    def get_employees(self):
        self.df_employees.reset_index(inplace=True)
        if self.df_employees.size > 0:
            self.df_employees["photo1"] = self.df_employees["photo1"].fillna("")
            self.df_employees["photo2"] = self.df_employees["photo2"].fillna("")
            self.df_employees["photo"] = self.df_employees[["photo1","photo2"]].agg(lambda x: "".join(x), axis=1)
        self.df_employees.rename(columns={"emp_id":"employeeId", "emp_name":"name", "plant_name":"plant", "department_name":"department"}, inplace=True)
        return self.df_employees
    
    
    def get_employees_photo_list(self):
        self.df_employees.reset_index(inplace=True)
        if self.df_employees.size > 0:
            if 'photo1' in list(self.df_employees.columns):
                self.df_employees["photo1"] = self.df_employees["photo1"].fillna("")
                self.df_employees["photo2"] = self.df_employees["photo2"].fillna("")
                self.df_employees["photo"] = self.df_employees[["photo1","photo2"]].agg(lambda x: "".join(x), axis=1)
                return self.df_employees["photo"].to_list()
        return []
    
    def get_employees_by_col(self, col_name:str):
        self.df_employees.reset_index(inplace=True)
        if col_name in list(self.df_employees.columns):
            return self.df_employees[col_name].to_list()
        return []
    
    
    def set_employee(self, emp_id:str, emp_name, plant_name, dept_name, shift, photo):
        emp_id = emp_id.upper()
        photo1 = photo[:32767]
        photo2 = photo[32767:]
        self.df_employees.loc[emp_id]= [emp_name, plant_name, dept_name, shift, photo1, photo2]
        self.__modify_target_sheet__(self.df_employees, "Employees")
    
    def remove_employee(self, empId:str):
        empId = empId
        self.df_employees = self.df_employees[~self.df_employees.index.isin([empId])]
        self.__modify_target_sheet__(self.df_employees, "Employees")
        
    # --------------------- Attendance Section ----------------------
        
    def get_attendance(self):
        # self.df_attendance.reset_index(inplace=True)
        # self.df_attendance.rename(columns={"emp_id":"employeeId", "":"employeeName"}, inplace=True)
        # return self.df_attendance
        pass
        
    def get_attendance_by_date(self, date):
        self.df_attendance.reset_index(inplace=True)
        if self.df_attendance.size > 0:
            df_attendance:pd.DataFrame = self.df_attendance[self.df_attendance['date']==date]
            df_attendance = df_attendance.merge(self.df_employees,left_on=['emp_id'],right_on=['emp_id'],how='left')
            df_attendance = df_attendance[["date","emp_id","present_absent","emp_name"]]
            df_attendance.rename(columns={"emp_id":"employeeId", "emp_name":"employeeName","present_absent":"status"}, inplace=True)
            return df_attendance
        else:
            return self.df_attendance
    
    def set_attendance(self, date, emp_id, present_absent):
        self.df_attendance.loc[(date,emp_id),:] = [present_absent]
        self.__modify_target_sheet__(self.df_attendance, "Attendance")
        
            
            
        