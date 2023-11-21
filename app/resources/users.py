from flask_restful import Resource


class Users(Resource):
    def get(self, user_id: int):
        ...

    def post(self, user_id: int):
        ...
