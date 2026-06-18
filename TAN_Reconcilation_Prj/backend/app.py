from flask import Flask, send_file, Response, request, abort, render_template, jsonify, send_from_directory
from flask_cors import CORS
from functools import wraps
import webbrowser
from threading import Timer
# from flask_socketio import SocketIO, emit
import pandas as pd
import json
import base64
from io import BytesIO
# from tqdm import tqdm
import time
# from getmac import get_mac_address as gma
import uuid
import itertools
# from datetime import timedelta

# from waitress import serve

# Custom Import 
from src.tan_working import TAN_Working
from src.default_code import TAN, TAN_L2_AMNT, TAN_SEC, TAN_SEC_L1_AMNT, TAN_SEC_L2_AMNT, Sheets, ALL_COLUMNS
from src.sample_tan import generate_sample_file

# app = Flask(__name__)
app = Flask(__name__, static_folder='./static', static_url_path='')
CORS(app)
# socketio = SocketIO(app)

def get_mac_address():
    """
    Retrieves and formats the MAC address of the current system.
    """
    mac_int = uuid.getnode()
    # Convert the 48-bit integer to a zero-padded 12-digit hex string
    mac_hex = '{:012x}'.format(mac_int)
    # Format the hex string with colons
    mac_address = ':'.join(mac_hex[i:i+2] for i in range(0, 12, 2))
    return mac_address

def custom_tqdm(tan_wk: TAN_Working, groupbyCol, tol, remark, level, to_process = True):
    if not to_process:
        return

    groupby = tan_wk.tan_df.groupby(groupbyCol)
    total_steps =len(groupby)
    i = 0
    # for tan, gtan in tqdm(groupby):
    for tan, gtan in groupby:
        i += 1
        progress_percentage = (i / total_steps) * 100
        tan_wk.match_entries_new(gtan, tol, remark, level=level)
        # p_time = timedelta(seconds=time.process_time())
        p_time = time.process_time()
        p_time_str = f"{int(p_time/3600)} h {int(p_time/60) % 60} min {int(p_time/3600) % 60} sec" if p_time > 3600 else f"{int(p_time/60)} min {int(p_time) % 60} sec" if p_time > 60 else f"{int(p_time)} sec"
        # print(p_time_str)
        # message = remark + " [" + str(i) + "/" + str(total_steps) + "] " + str(int(time.process_time())) + " sec"
        message = f"[ {progress_percentage:.0f}% ] {remark} [ {p_time_str} ] [ {i}/{total_steps} ]"
        yield json.dumps({"data": {"TAN": tan[0], "progress": progress_percentage, "message":message}})+"\n"
        # Emit progress to the client
        # socket.emit('progress', {'progress': progress_percentage, 'remaining_time': remaining_time})

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
@app.route('/')
# @ip_restricted
def serve_nextjs_app():
    return send_from_directory(app.static_folder, 'index.html')

# Serve other static files (like JS and CSS) directly
@app.route('/<path:path>')
# @ip_restricted
def serve_static_files(path):
    return send_from_directory(app.static_folder, path)

# ---------- Routes ----------
# @app.route("/")
# def index():
#     return render_template("./_next/server/app/index.html")


@app.route("/api/download_file", methods=["GET"])
# @ip_restricted
def download_sample_excel():
    output = generate_sample_file()
    excel_base64 = base64.b64encode(output.getvalue()).decode('utf-8')
    response_data = {
        "filename": "sample_file.xlsx",
        "file_content": excel_base64,
        "mimetype":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "message": "Sample Excel file successfully generated."
    }
    return jsonify(response_data)

# @app.route("/upload", methods=["POST"])
# def upload_file():
#     if "file" not in request.files:
#         return jsonify({"status": "error", "message": "No file uploaded"}), 400

#     file = request.files["file"]
#     file_bytes = file.read()

#     result = match_books_tds(file_bytes)
#     return jsonify(result)


@app.route("/api/start_task", methods=["POST"])
# @ip_restricted
def start_task():
    try:
        print(request.form)
        if "file" not in request.files:
            # return Response(json.dumps({"status": "error", "message": "No file uploaded"}), content_type='text/event-stream')
            return jsonify({"status": "error", "message": "No file uploaded"}), 400

        file = request.files["file"]
        file_bytes = file.read()

        process_level = request.form.get("processingLevels")
        l1, l2, l3, l4, l5, l6, l7 = list(json.loads(process_level).values()) if process_level else list(itertools.repeat(True, 7))
        print("ok", process_level)

        xlsx = pd.ExcelFile(BytesIO(file_bytes), engine="openpyxl")

        if not (all(x in [Sheets.BOOKS.value,Sheets.TDS.value] for x in xlsx.sheet_names)):
            return Response(json.dumps({"data":{"error":"Wrong Uploaded file. Please download sample file again."}})+"\n", content_type='text/event-stream')
        

        # books and tds dataframe
        books_df = pd.read_excel(xlsx, sheet_name=Sheets.BOOKS.value)
        tds_df = pd.read_excel(xlsx, sheet_name=Sheets.TDS.value)


        if not all(x in ALL_COLUMNS for x in list(books_df.columns)) or not all(x in ALL_COLUMNS for x in list(tds_df.columns)):
            return Response(json.dumps({"data":{"error":"Sheets columns are missmatched or interrupted. Please download sample file again."}})+"\n", content_type='text/event-stream')


        tan_wk = TAN_Working(books=books_df, tds=tds_df)

        def download_file():
            output=BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                tan_wk.remark_summary().to_excel(writer, sheet_name='Remark Summary')
                tan_wk.tan_summary().to_excel(writer, sheet_name='TAN Summary')
                tan_wk.tan_df[ALL_COLUMNS].to_excel(writer,sheet_name='data')

            output.seek(0)
            excel_base64 = base64.b64encode(output.getvalue()).decode('utf-8')
            response_data = {
                "filename": "Reconciled_TAN_Data.xlsx",
                "file_content": excel_base64,
                "mimetype":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "message": "Excel file successfully generated and encoded."
            }
            # print(len(excel_base64))
            yield json.dumps({"data":{"download":response_data}})+"\n"


        def generate_multiple_tasks():
            # Level 1
            # yield from custom_tqdm(tan_wk=tan_wk, groupbyCol=G_TAN, tol=0, remark=Sheets.ONE_TAN.value, level=10)
            yield from custom_tqdm(tan_wk=tan_wk, groupbyCol=TAN, tol=100, remark=Sheets.TAN_FULL_M_LT_100.value, level=0, to_process = l1)
            # Level 2
            yield from custom_tqdm(tan_wk=tan_wk, groupbyCol=TAN_SEC_L1_AMNT, tol=1, remark=Sheets.OWN_TAN_M.value, level=0, to_process = l2)
            # Level 3
            yield from custom_tqdm(tan_wk=tan_wk, groupbyCol=TAN_SEC_L2_AMNT, tol=1, remark=Sheets.S_TAN_M_LT_1.value, level=0, to_process = l3)
            # Level 4
            yield from custom_tqdm(tan_wk=tan_wk, groupbyCol=TAN_L2_AMNT, tol=1, remark=Sheets.S_TAN_DIFFSEC_M_LT_1.value, level=0, to_process = l4)
            # Level 5
            yield from custom_tqdm(tan_wk=tan_wk, groupbyCol=TAN, tol=1, remark=Sheets.G_TAN_M_LT_1.value, level=2, to_process = l5)
            # Level 6
            yield from custom_tqdm(tan_wk=tan_wk, groupbyCol=TAN, tol=50, remark=Sheets.G_TAN_M_LT_50.value, level=2, to_process = l6)
            # Level 7
            yield from custom_tqdm(tan_wk=tan_wk, groupbyCol=TAN, tol=1, remark=Sheets.M_TAN_M_LT_1.value, level=5, to_process = l7)
            # Final Reconciled Data
            yield from download_file()
            # Complete Tag
            yield json.dumps({"data":{"complete":True}})
            
        return Response(generate_multiple_tasks(), content_type='text/event-stream')

    except Exception as e:
        print(f"Error: {e}")
        # raise e
        # return Response(json.dumps({"status": "error", "message": "Error on process"}), content_type='text/event-stream')
        return jsonify({"status": "error", "message": err}), 400


def open_browser():
    Timer(1, lambda: webbrowser.open_new("http://localhost:8080")).start()

if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=8080)
    # app.run(debug=True, host="192.168.97.205", port=5000)
    # serve(app, host="0.0.0.0", port=8080)
