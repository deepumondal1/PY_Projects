from functools import wraps
import uuid
import webbrowser

from flask import Flask, send_file, Response, request, abort, render_template, jsonify, send_from_directory
from flask_cors import CORS
from threading import Timer
# from flask_socketio import SocketIO, emit
# import pathlib
# import pandas as pd
import json

import pandas as pd
# import base64
# from io import BytesIO

# from jc_working import JCard_Working
# from tqdm import tqdm
# import time
# from getmac import get_mac_address as gma
# import uuid
# from datetime import timedelta

# from waitress import serve

# Custom Import 
from src.jc_working import JCard_Working

# app = Flask(__name__)
app = Flask(__name__, static_folder='./static', static_url_path='')
CORS(app)
# socketio = SocketIO(app)

def get_mac_address():
    mac_int = uuid.getnode()
    mac_hex = '{:012x}'.format(mac_int)
    mac_address = ':'.join(mac_hex[i:i+2] for i in range(0, 12, 2))
    return mac_address


ALLOWED_MAC = ['f4:ee:08:a4:84:22', '']

# ---------- Static ----------
# Serve the static files from the Next.js build

def ip_restricted(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        mac = get_mac_address()
        if mac.lower() not in ALLOWED_MAC:
            # Abort the request and trigger the 403 error handler
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# Serve the static files from the Next.js build
# @app.route('/')
# # @ip_restricted
# def serve_nextjs_app():
#     return send_from_directory(app.static_folder, 'index.html')

# Serve other static files (like JS and CSS) directly
@app.route('/<path:path>')
# @ip_restricted
def serve_static_files(path):
    return send_from_directory(app.static_folder, path)

# ---------- Routes ----------
# @app.route("/")
# def index():
#     return render_template("./_next/server/app/index.html")


# @app.route("/api/download_file", methods=["GET"])
# # @ip_restricted
# def download_sample_excel():
#     # output = generate_sample_file()
#     output=BytesIO()
#     output.seek(0)
#     excel_base64 = base64.b64encode(output.getvalue()).decode('utf-8')
#     response_data = {
#         "filename": "sample_file.xlsx",
#         "file_content": excel_base64,
#         "mimetype":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         "message": "Sample Excel file successfully generated."
#     }
#     return jsonify(response_data)


@app.route("/api/start_task", methods=["POST"])
# @ip_restricted
def start_task():
    try:
        # print(request.form, request.content_encoding, request.get_json())
        jc_list:list = json.loads(request.form.get("jc_list"))
        jc_list = jc_list if isinstance(jc_list, list) else []

        print(jc_list)
        if len(jc_list) == 0:
            # return Response(json.dumps({"status": "error", "message": "No file uploaded"}), content_type='text/event-stream')
            return Response(json.dumps({"data":{"error": "Invalid Job Card Entry."}})+"\n", content_type='text/event-stream')

        jc_df = JCard_Working()

        # jc_list = list(json.load(jc_list))
        # jc_file_list = find_jc_path(jc_list)

        # for file in jc_file_list:
        

        # def download_file():
        #     output=BytesIO()
        #     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        #         tan_wk.remark_summary().to_excel(writer, sheet_name='Remark Summary')
        #         tan_wk.tan_summary().to_excel(writer, sheet_name='TAN Summary')
        #         tan_wk.tan_df[ALL_COLUMNS].to_excel(writer,sheet_name='data')

        #     output.seek(0)
        #     excel_base64 = base64.b64encode(output.getvalue()).decode('utf-8')
        #     response_data = {
        #         "filename": "Reconciled_TAN_Data.xlsx",
        #         "file_content": excel_base64,
        #         "mimetype":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        #         "message": "Excel file successfully generated and encoded."
        #     }
        #     # print(len(excel_base64))
        #     yield json.dumps({"data":{"download":response_data}})+"\n"


        def generate_multiple_tasks():
            try:
                yield from jc_df.find_jc_path(jc_list)
                yield from jc_df.generate_consump_df()
                yield from jc_df.transform_to_pivot_data()
            #     yield from download_file()
            #     # Complete Tag
                yield json.dumps({"data":{"download": jc_df.to_json(),"message":"JobCard Data to Json()","original":jc_df.org_jc_df.to_json()}})+"\n"

                yield json.dumps({"data":{"complete":True}})
            
            except Exception as err:
                error = f"[{err}] [LineNo-{err.__traceback__.tb_lineno}]"
                print(error)
                yield json.dumps({"data":{"error":f"{error}"}})+"\n"
            
        return Response(generate_multiple_tasks(), content_type='text/event-stream')

    except Exception as e:
        print(f"Error: {e}, {e.__traceback__.tb_lineno}")
        # raise e
        return Response(json.dumps({"data":{"error": f"{e}"}})+"\n", content_type='text/event-stream')
        # return jsonify({"error": f"Error on process {e}"}), 400



@app.route("/api/refresh_task", methods=["POST"])
# @ip_restricted
def refresh_task():
    try:
        # print(request.form, request.content_encoding, request.get_json())
        if not request.is_json:
            raise Exception('Invalid MIMETYPE. mimetype should be \'application/json\'')
        
        orginal_df_data:dict = json.loads(request.get_json(force=True,silent=True))

        df = JCard_Working()
        df.jc_df = pd.DataFrame(orginal_df_data)

        def generate_multiple_tasks():
            try:
                yield from df.transform_to_pivot_data()
            #     yield from download_file()
            #     # Complete Tag
                yield json.dumps({"data":{"download": df.to_json(),"message":"JobCard Data to Json()","original":df.org_jc_df.to_json()}})+"\n"

                yield json.dumps({"data":{"complete":True}})
            
            except Exception as err:
                error = f"[{err}] [LineNo-{err.__traceback__.tb_lineno}]"
                print(error)
                yield json.dumps({"data":{"error":f"{error}"}})+"\n"
            
        return Response(generate_multiple_tasks(), content_type='text/event-stream')

    except Exception as e:
        print(f"Error: {e}, {e.__traceback__.tb_lineno}")
        # raise e
        return Response(json.dumps({"data":{"error": f"{e}"}})+"\n", content_type='text/event-stream')
        # return jsonify({"error": f"Error on process {e}"}), 400



def open_browser():
    Timer(1, lambda: webbrowser.open_new("http://localhost:5000")).start()

if __name__ == "__main__":
    # app.run(debug=True)
    open_browser()
    app.run(host="0.0.0.0", port=5000)
    # app.run(debug=True, host="192.168.97.205", port=5000)
    # serve(app, host="0.0.0.0", port=8080)
