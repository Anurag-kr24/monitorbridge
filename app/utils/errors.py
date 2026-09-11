from flask import g, jsonify


def error_response(code, message, status_code):
    return jsonify({
        "error": {
            "code": code,
            "message": message,
            "request_id": g.request_id,
        }
    }), status_code
