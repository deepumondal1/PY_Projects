from flask import Flask, send_file, Response, request, abort, jsonify
from flask_cors import CORS
# import json
import threading 

from src.attendance_df_db import Attendance_df_db
from src.helper import RespMessage, jsondumps
from src.capture_attendance import match_capture_img, Capture_Cam

from src.testImg_show import checking_image

# test
import cv2
import base64
import time
import queue
from websockets.sync.server import serve



app = Flask(__name__, static_folder='./static', static_url_path='')
CORS(app)


# lock = threading.Lock

@app.route("/api/matching_captured", methods=['POST'])
def matching_captured():
    try:
        if not (request.form):
            raise Exception("Body Not Found.")
        
        src_img_str = request.form.get('src_img')
        return Response(match_capture_img(src_img_str))
        
    except Exception as err:
        print("Error -> ", "LineNo - ",err.__traceback__,", ErrMsg - ", err)
        return Response(jsondumps({'complete':True}))


@app.route("/api/live_camera_feed", methods=['GET'])
def live_camera_feed():
    try:
        # detect = request.args.get('detect', type=bool)
        # detect = detect if detect else False
        
        def handle_queue_msg(q:queue.Queue):
            while True:
                try:
                    q_data = q.get()
                    if q_data is None:
                        break
                    yield f"{q_data}"
                    q.task_done()
                except:
                    q.put(None)
                    continue
                
        cap_cam = Capture_Cam()
        # q = [queue.Queue(),queue.Queue()]
        q = queue.Queue()
        def thread_start():
            threading.Thread(name="T0", target=cap_cam.capture_live_camera_feed, args=(q, ), daemon=True).start()
            # threading.Thread(name="T2", target=cap_cam.capture_live_camera_feed, args=(q, True,), daemon=True).start()
        
        def generator():
            thread_start()
            yield from handle_queue_msg(q)
            yield jsondumps({'complete':True})
            cap_cam.cam.release()
            
        return Response(generator())
        
    except Exception as err:
        print("Error -> ", "LineNo - ",err.__traceback__,", ErrMsg - ", err)
        return Response(jsondumps({'complete':True}))


@app.route("/api/video_feed")
def video_feed():
    # cam = cv2.VideoCapture(0)
    try:
        # def generator():
        #     # timeout_start = time.time()
        #     # while True:
        #     #     s, img = cam.read()
        #     #     if time.time() > timeout_start + 10:
        #     #         break
        #     #     if s:
        #     #         ret, enc = cv2.imencode('.jpg',img=img)
        #     #         if ret:
        #     #             yield jsondumps({"base64img":f"data:image/jpeg;base64,{base64.b64encode(enc).decode()}"})
            
        #     app = Attendance_df_db()
        #     df = app.get_employees()
        #     img_str = df['photo'].get(0)
        #     yield from match_capture_img(img_str)
        
        def generator1(sleep:int, name:str, q:queue.Queue):
            for i in range(1,100):
                s = True
                ret = True
                if s:
                    if ret:
                        time.sleep(sleep)
                        print(name, i*sleep, time.strftime("%H:%M:%S"))
                        q.put({"a":f"{i*sleep}"})
                        # yield jsondumps({"a":f"{i}"})
            q.put(None)
            
        def show_queue_data_gen(q:queue.Queue):
            while True:
                item = q.get()
                print('queue.get()->',item, q.empty())
                if item is None:
                    break
                yield f"{item}"
                q.task_done()
             
        q = queue.Queue()
        def thread_start():           
            # threading.Thread(target=generator1, args=(3,"t1"), daemon=True).start()
            # threading.Thread(target=generator1, args=(5,"t2"), daemon=True).start()
            t1 = threading.Thread(name="THREAD1", target=generator1, args=(0,"t1",q), daemon=True)
            t2 = threading.Thread(name="THREAD2", target=generator1, args=(5,"t2",q), daemon=True)
            # t3 = threading.Thread(name="THREAD3", target=show_queue_data_gen, args=(q,), daemon=True)
            t1.start()
            t2.start()
            # t3.start()
            # t2.join()
            print(t1.is_alive(), t2.is_alive())
            # time.sleep(5)

        def gen():
            thread_start()
            yield from show_queue_data_gen(q)
            print('q.empty()', q.empty(), q.full())
        # return Response(generator(), mimetype='multipart/x-mixed-replace; boundary=frame')
        # return Response(generator1(2))
        return Response(gen())
    
    except Exception as err:
        print(err.__traceback__.tb_lineno, err)
        # cam.release()
        return Response('complete')

@app.route("/api/dashboard", methods=["GET"])
def get_dashboard():
    db = Attendance_df_db()
    
    match request.method:
        case "GET":
            json_dashboard_data = db.get_dashboard_data()
            return RespMessage.success("Dashboard Data", json_dashboard_data)
        

@app.route("/api/masters", methods=["GET"])
def get_masters():
    db = Attendance_df_db()
    
    match request.method:
        case "GET":
            df_plant = db.get_plant_name()
            df_dept = db.get_department_name()
            df_shift = db.get_shifts()
            json_resp = {
                "plants": db.to_json(df_plant),
                "depts": db.to_json(df_dept),
                "shifts": db.to_json(df_shift)
            }
            return RespMessage.success("Master Data", json_resp)
            
            

@app.route("/api/plants", methods=["GET", "POST", "DELETE"])
def get_plant():
    db = Attendance_df_db()
    
    match request.method:
        case "GET":
            df = db.get_plant_name()
            return RespMessage.success("Plant Names", db.to_json(df))
        
        case "POST":
            data = request.get_json()
            db.set_plant_name(data["name"])
            df = db.get_plant_name()
            return RespMessage.success("Plant name added successfully.", db.to_json(df))
        
        case "DELETE":
            name = request.args.get('name')
            db.remove_plant_name(name)
            df = db.get_plant_name()
            return RespMessage.success("Plant name removed successfully.", db.to_json(df))


@app.route("/api/departments", methods=["GET", "POST", "DELETE"])
def get_department():
    db = Attendance_df_db()
    
    match request.method:
        case "GET":
            df = db.get_department_name()
            return RespMessage.success("Department Names", db.to_json(df))
        
        case "POST":
            data = request.get_json()
            db.set_department_name(data["name"])
            df = db.get_department_name()
            return RespMessage.success("Department name added successfully.", db.to_json(df))
        
        case "DELETE":
            name = request.args.get('name')
            db.remove_department_name(name)
            df = db.get_department_name()
            return RespMessage.success("Department name removed successfully.", db.to_json(df))


@app.route("/api/shifts", methods=["GET", "POST", "DELETE"])
def get_shift():
    db = Attendance_df_db()
    
    match request.method:
        case "GET":
            df = db.get_shifts()
            return RespMessage.success("Shift List", db.to_json(df))
        
        case "POST":
            data = request.get_json()
            db.set_shift(data["name"], data['from_time'], data['to_time'])
            df = db.get_shifts()
            return RespMessage.success("Shift name added successfully.", db.to_json(df))
        
        case "DELETE":
            name = request.args.get('name')
            db.remove_shift(name)
            df = db.get_shifts()
            return RespMessage.success("Shift name removed successfully.", db.to_json(df))
        

@app.route("/api/enrollments", methods=["GET","POST","DELETE"])
def get_enrollment_masters():
    db = Attendance_df_db()
    
    match request.method:
        case "GET":
            df_plant = db.get_plant_name()
            df_dept = db.get_department_name()
            df_shift = db.get_shifts()
            df_employee = db.get_employees()
            json_resp = {
                "plants": db.to_json(df_plant),
                "depts": db.to_json(df_dept),
                "shifts": db.to_json(df_shift),
                "employees": db.to_json(df_employee)
            }
            return RespMessage.success("Employee Masters Data", json_resp)
    
        case "POST":
            data = request.get_json()
            db.set_employee(emp_id=data["employeeId"], emp_name=data['name'], plant_name=data['plant'], dept_name=data['department'], shift=data['shift'], photo=data['photo'])
            df = db.get_employees()
            return RespMessage.success("Employee added successfully.", db.to_json(df))
        
        case "DELETE":
            empId = request.args.get('empId')
            db.remove_employee(empId)
            df = db.get_employees()
            return RespMessage.success("Employee removed successfully.", db.to_json(df))
            


@app.route("/api/attendance-records", methods=["GET", "POST"])
def get_attendance():
    db = Attendance_df_db()
    
    match request.method:
        case "GET":
            date = request.args.get('date')
            df_attendance = db.get_attendance_by_date(date)
            return RespMessage.success("Attendance Data", db.to_json(df_attendance))

        case "POST":
            data = request.get_json()
            date = data['date']
            db.set_attendance(date=data["date"], emp_id=data["employeeId"], present_absent=data["status"])
            df = db.get_attendance_by_date(date=date)
            return RespMessage.success("Attendance added successfully.", db.to_json(df))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
    # checking_image()
