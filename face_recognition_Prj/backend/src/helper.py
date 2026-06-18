from flask import jsonify, Response
import json

class RespMessage:
    def success(message, data=None)->Response:
        return jsonify({
            "status": "success",
            "message": message,
            "data": data
        }), 200
    
    def error(message)->Response:
        return jsonify({
            "status": "error",
            "error": message
        }), 400
        
        
def jsondumps(obj):
    return f"{json.dumps(obj=obj)}|"