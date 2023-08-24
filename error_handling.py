from flask import jsonify

def handle_registration_error(message, status_code):
    return jsonify({"error": message}), status_code

def handle_sync_error(message, status_code):
    return jsonify({"error": message}), status_code
