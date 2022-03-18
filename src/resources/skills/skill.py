from abc import abstractmethod

from flask_restful import Resource


class Skill(Resource):
    sessionStorage = {}

    @abstractmethod
    def post(self) -> str:
        pass
