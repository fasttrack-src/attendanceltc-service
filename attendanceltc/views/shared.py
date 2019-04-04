from flask import jsonify


class APIResponseMaker(object):

    def __init__(self):
        self.errors = []
        self.resp_data = None
        self.resp_message = None

    def error(self, title=None, detail=None, status=400):
        error = {}

        error["status"] = str(status)

        if title:
            error["title"] = str(title)

        if detail:
            error["detail"] = str(detail)

        self.errors.append(error)

    def data(self, data):
        if self.errors:
            return

        if self.resp_data:
            raise ValueError("A response object has already been added.")

        self.resp_data = data
    
    def message(self, message):
        if self.resp_message:
            raise ValueError("A message has already been added.")

        self.resp_message = str(message)

    def get_response(self, message=None, data=None, status=200):
        if message:
            self.message(message)

        if data:
            self.data(data)

        if self.errors:
            if status >= 400:
                return jsonify({"errors": self.errors, "message": self.resp_message}), status
            else:
                return jsonify({"errors": self.errors, "message": self.resp_message}), 400

        if not self.resp_data and not self.resp_message:
            raise ValueError(
                "Response has neither error objects nor response data.")

        return jsonify({"data": self.resp_data, "message": self.resp_message}), status
