from flask import jsonify


class APIResponseMaker(object):

    def __init__(self):
        self.errors = []
        self.resp_data = None

    def error(self, title=None, detail=None, status=500):
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

    def get_response(self, data=None, status=200):
        if self.errors:
            return jsonify({"errors": self.errors}), 400

        if data:
            self.data(data)

        if not self.resp_data:
            raise ValueError(
                "Response has neither error objects nor response data.")

        return jsonify({"data": self.resp_data}), status
