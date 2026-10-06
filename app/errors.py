from flask import jsonify


class APIError(Exception):
    def __init__(self, code, message, status=400):
        super().__init__(message)
        self.code, self.message, self.status = code, message, status


def success(data):
    return jsonify(success=True, data=data)


def failure(error, data=None):
    payload = {"success": False, "error": {"code": error.code, "message": error.message}}
    if data is not None:
        payload["data"] = data
    return jsonify(payload), error.status
