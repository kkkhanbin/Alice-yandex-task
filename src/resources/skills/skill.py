from abc import abstractmethod
import logging

from flask import request
from flask_restful import Resource


class Skill(Resource):
    sessionStorage = {}

    @abstractmethod
    def post(self):
        logging.info(f'Request: {request.json!r}')

        response = {
            'session': request.json['session'],
            'version': request.json['version'],
            'response': {
                'end_session': False,
                'buttons': []
            }
        }

        logging.info(f'Response:  {response!r}')

        self.handle_dialog(request.json, response)

        return response

        # return json.dumps(response, ensure_ascii=False)

    @abstractmethod
    def handle_dialog(self, request, response):
        pass
