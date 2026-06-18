import cv2
import os
import sys
import face_recognition
import numpy as np
from datetime import datetime
import base64
from PIL import Image

# from src
from src.attendance_df_db import Attendance_df_db
from src.helper import jsondumps

# testing
import time
# from multiprocessing import Process, Queue
import queue

MODEL = 'hog'
TOLERANCE = 0.4

def info(title):
    print(title)
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())
    

def match_capture_img(img_str:str):
    try:
        cam = cv2.VideoCapture(0)
        
        if "data:image/jpeg" in img_str and ";base64," in img_str:
            header, encoded_data = img_str.split(",")
        else:
            encoded_data = img_str
        src_img_bytes = base64.b64decode(encoded_data)
        nparr = np.frombuffer(src_img_bytes, np.uint8)
        src_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        src_img_encoding = face_recognition.face_encodings(src_img)[0]
        encoding_arr = [src_img_encoding]
        src_img_arr = [src_img]
        
        timeout_start = time.time()
        def test_thread(Execute=False):
            isMatched = False
            isFaceCaptured = False
            while True:
                if time.time() > timeout_start + 30:
                    break
                isImgCaptured, target_frame = cam.read()
                ret, enc = cv2.imencode('.jpg',img=target_frame) 
                yield jsondumps({"data":{'isMatched':isMatched, 'isFaceCaptured':isFaceCaptured, "test":1, 'base64img': f"data:image/jpeg;base64,{base64.b64encode(enc).decode()}"}})
                if Execute:           
                    if isImgCaptured and ret:
                        target_face_locs = face_recognition.face_locations(target_frame)                    
                        
                        for loc in target_face_locs:
                            top, right, bottom, left = loc
                            top -= 10
                            right += 10
                            bottom += 10
                            left -= 10
                            src_img = cv2.rectangle(target_frame, (left, top), (right, bottom), (0,255,0), 2)
                            ret, enc = cv2.imencode('.jpg',img=src_img)
                            target_crop_img = target_frame[top:bottom, left:right]
                        
                            try:
                                rgb_cropped_image = cv2.cvtColor(target_crop_img, cv2.COLOR_BGR2RGB)
                            except:
                                continue
                            
                            crop_img_encoding = face_recognition.face_encodings(rgb_cropped_image)
                            
                            if crop_img_encoding:
                                isFaceCaptured = True
                                compares = face_recognition.compare_faces(encoding_arr, crop_img_encoding[0], TOLERANCE)
                                ret, enc = cv2.imencode('.jpg',img=target_crop_img)
                                if any(compares):
                                    src_img_arr[compares.index(True)]
                                    isMatched = True
                                    
                                break
                        
                        if isFaceCaptured:
                            break
                        
                yield jsondumps({"data":{'isMatched':isMatched, 'isFaceCaptured':isFaceCaptured, "test":1, 'base64img': f"data:image/jpeg;base64,{base64.b64encode(enc).decode()}"}})
                # queue.put(jsondumps({"data":{'isMatched':isMatched, "test":1, 'base64img': f"data:image/jpeg;base64,{base64.b64encode(enc).decode()}"}}))
                
            yield jsondumps({"data":{'isMatched':isMatched, 'isFaceCaptured':isFaceCaptured, "test":2, 'base64img': f"data:image/jpeg;base64,{base64.b64encode(enc).decode()}"}})
            # queue.put(jsondumps({"data":{'isMatched':isMatched, "test":2, 'base64img': f"data:image/jpeg;base64,{base64.b64encode(enc).decode()}"}}))
        
        
        
        # queue = Queue()
        # p1 = Process(target=test_thread, args=(queue,), daemon=True)
        # # p2 = Process(target=test_thread, args=(queue, True))
        # # yield from test_thread()
        # print(p1)
        # p1.start()
        # # p2.start()
        # print(queue.get())
        
        # yield queue.get()
        yield from test_thread(True)
            
    
    except Exception as err:
        print(err.__traceback__.tb_lineno, err)


class Capture_Cam:
    def __init__(self):
        self.cam = cv2.VideoCapture(0)
        
    def capture_live_camera_feed_def(self, q: queue.Queue):
        isMatched = False
        cam = self.cam
        while True:
            haveImg , img = cam.read()
            img = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
            if not haveImg:
                raise Exception("Image not Captured. Or Maybe camera not detect.")
                                    
            ret, enc = cv2.imencode('.jpg',img=img)
            # yield jsondumps({"data":{"isMatched":isMatched, "base64img": f"data:image/jpeg;base64,{base64.b64encode(enc).decode()}"} })
            q.put_nowait(jsondumps({"data":{"isMatched":isMatched, "base64img": f"data:image/jpeg;base64,{base64.b64encode(enc).decode()}"} }))


        
    def capture_live_camera_feed(self, q:queue.Queue, is_Face_Detection_On:bool=False):
        try:
            app = Attendance_df_db()
            
            images = app.get_employees_photo_list()
            img_emp_ids = app.get_employees_by_col('emp_id')
            img_emp_names = app.get_employees_by_col('emp_name')
            img_encodings = []
            
            if images.__len__() ==0  or img_emp_ids.__len__() == 0:
                raise Exception('Empty Images or Emp Ids')

            for img_str in images:
                if "data:image/jpeg" in img_str and ";base64," in img_str:
                    header, encoded_data = img_str.split(",")
                else:
                    encoded_data = img_str
                src_img_bytes = base64.b64decode(encoded_data)
                nparr = np.frombuffer(src_img_bytes, np.uint8)
                src_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                encoding = face_recognition.face_encodings(src_img)[0]
                img_encodings.append(encoding)
                
                
            # cam = cv2.VideoCapture(0)
            timeout_start = time.time()
            cam = self.cam
            isMatched = False
            while True:
                haveImg , img = cam.read()
                if not haveImg:
                    raise Exception("Image not Captured. Or Maybe camera not detect.")
                               
                face_classifier = cv2.CascadeClassifier(
                    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
                )         
                # gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = face_classifier.detectMultiScale(img, 1.1, 5, minSize=(40, 40))
                print(faces)
                if len(faces)>0:
                    top, right, bottom, left = faces[0]
                    cv2.rectangle(img, (left,top),(right,bottom), (0,255,0), 2)
    
                # img = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
                ret, enc = cv2.imencode('.jpg',img=img)
                # yield jsondumps({"data":{"isMatched":isMatched, "base64img": f"data:image/jpeg;base64,{base64.b64encode(enc).decode()}"} })
                # if not is_Face_Detection_On:
                #     q.put(jsondumps({"data":{"isMatched":isMatched, "base64img": f"data:image/jpeg;base64,{base64.b64encode(enc).decode()}"} }))

                if is_Face_Detection_On:
                    # Detect Faces from Image generate from WebCam and crop it and compare from input folder.
                    face_locations = face_recognition.face_locations(img, model=MODEL)
                    # face_encodings = face_recognition.face_encodings(img, face_locations)
                    # for loc in location:
                    #     top, right, bottom, left = loc
                    #     top = top-10
                    #     left = left-10
                    #     bottom = bottom+10
                    #     right = right+10
                    #     cv2.rectangle(img, (left,top),(right,bottom), (0,255,0), 2)
                    #     ret, enc = cv2.imencode('.jpg',img=img)
                    #     cropped_image = img[top:bottom, left:right]

                    #     try:
                    #         rgb_cropped_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)
                    #     except:
                    #         continue
                    
                    # crop_img_encoding = face_recognition.face_encodings(rgb_cropped_image)[0]
                    # if crop_img_encoding:
                    #     isFaceCaptured = True
                    #     compares = face_recognition.compare_faces(img_encodings, crop_img_encoding, TOLERANCE)
                    #     print('compares',compares)
                    #     if any(compares): # and time.time() > timeout_start + 5:
                    #         idx = compares.index(True)
                    #         emp_id = img_emp_ids[idx]
                    #         emp_name = img_emp_names[idx]
                    #         isMatched = True
                    #         ret, enc = cv2.imencode('.jpg',img=img)
                    #         ret, enc_face = cv2.imencode('.jpg',img=cropped_image)
                    #         # yield jsondumps({"data":{"isMatched":isMatched, "emp_id": emp_id, "base64img": f"data:image/jpeg;base64,{base64.b64encode(enc).decode()}"} })
                    #         q.put(jsondumps({"data":{"isMatched":isMatched, "emp_id": emp_id, "emp_name": emp_name, "base64img": f"data:image/jpeg;base64,{base64.b64encode(enc).decode()}", "base64img_face": f"data:image/jpeg;base64,{base64.b64encode(enc_face).decode()}"} }))
                    #         # q.put(jsondumps({"data":{"isMatched":isMatched, "emp_id": emp_id} }))
                            
                    #         # remove idx row of found employee
                    #         img_emp_ids.pop(idx)
                    #         img_emp_names.pop(idx)
                    #         img_encodings.pop(idx)
                            
                    #         isMatched = False
                    #         timeout_start = time.time()
                    pass
                 
                # yield jsondumps({"data":{"isMatched":isMatched, "base64img": f"data:image/jpeg;base64,{base64.b64encode(enc).decode()}"} })
                q.put(jsondumps({"data":{"isMatched":isMatched, "base64img": f"data:image/jpeg;base64,{base64.b64encode(enc).decode()}"} }))
                # q.put(jsondumps({"data":{"isMatched":isMatched} }))
                            
            
            # cv2.waitKey(0)
        except Exception as err:
            print(f"Error: [LineNo-{err.__traceback__.tb_lineno}] [{err}]")
            # cam.release()
        finally:
            cam.release()
            self.cam.release()
            cv2.destroyAllWindows()


def capture_attendance():
    try:
        img_names = []
        img_encodings = []

        currPath = sys.path[0]
        INPUT_PATH = currPath + "\\Input\\"
        OUTPUT_PATH = currPath + "\\Output\\"

        # Carry list of name and encoding from Input folder files
        for filename in os.listdir(INPUT_PATH):
            image = face_recognition.load_image_file(f"{INPUT_PATH}{filename}")
            # image = cv2.colorChange(image, cv2.COLOR_BGR2GRAY)
            if isinstance(image, np.ndarray):
                name = "".join(filename.split(".")[:-1])
                encoding = face_recognition.face_encodings(image)[0]
                img_names.append(name)
                img_encodings.append(encoding)

        # return
    
        cam = cv2.VideoCapture(0)
        window_name = "Camera Feed"
        while True:
            haveImg , img = cam.read()

            if not haveImg:
                raise Exception("Image not Captured. Or Maybe camera not detect.")

            # Detect Faces from Image generate from WebCam and crop it and compare from input folder.
            location = face_recognition.face_locations(img, model=MODEL)
            # print(f"location->{location}")
            for i, loc in enumerate(location):
                top, right, bottom, left = loc
                top = top-10
                left = left-10
                bottom = bottom+10
                right = right+10
                cv2.rectangle(img, (left,top),(right,bottom), (0,255,0), 2)
                cropped_image = img[top:bottom, left:right]

                try:
                    rgb_cropped_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)
                except:
                    continue

                # path = f"{OUTPUT_PATH}IMG.jpg"
                # isFileSave = cv2.imwrite(path, rgb_cropped_image)
                crop_img_encoding = face_recognition.face_encodings(rgb_cropped_image)
                # print(crop_img_encoding)
                if crop_img_encoding:
                    compares = face_recognition.compare_faces(img_encodings, crop_img_encoding[0], TOLERANCE)
                    # print(f"compare->{compares}")
                    txt = "Unknown"
                    if any(compares): 
                        # filename = f"{img_names[compares.index(True)]}-{i}-{round(datetime.timestamp(datetime.now()))}.jpg"
                        # path = f"{OUTPUT_PATH}{filename}"
                        # isFileSave = cv2.imwrite(path, cropped_image)
                        # print(isFileSave)
                        
                        txt = f"{img_names[compares.index(True)]}"

                    cv2.putText(
                        img=img,
                        text=txt,
                        org=(left, top-10),  # Bottom-left corner of the text
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=0.5,
                        color=(0, 255, 0),  # Green color (B, G, R)
                        thickness=1,
                        lineType=cv2.LINE_AA
                    )

            # if len(location) != 0:
            #     filename = f"img{round(datetime.timestamp(datetime.now()))}.jpg"
            #     path = f"{OUTPUT_PATH}{filename}"
            #     print(filename, path)
            #     cv2.imwrite(path, img)
            cv2.namedWindow(window_name)
            cv2.imshow(window_name, img)
            # break
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # cv2.waitKey(0)
    except Exception as err:
        print(f"Error: [LineNo-{err.__traceback__.tb_lineno}] [{err}]")
        # cam.release()
    finally:
        cam.release()
        cv2.destroyAllWindows()

# capture_attendance()