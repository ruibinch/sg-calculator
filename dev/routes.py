from flask_restful import Resource
from http import HTTPStatus
from utils import endpoints, strings

from . import api_manager
from logic import router

class CpfContribution(Resource):
    def post(self):
        response, status_code, params = api_manager.handle_api_request(endpoints.CPF_CONTRIBUTION)

        if status_code == HTTPStatus.OK:
            results = router.execute(endpoints.CPF_CONTRIBUTION, params)
            response = {strings.RESULTS: results}

        return response, status_code

class CpfAllocation(Resource):
    def post(self):
        response, status_code, params = api_manager.handle_api_request(endpoints.CPF_ALLOCATION)

        if status_code == HTTPStatus.OK:
            results = router.execute(endpoints.CPF_ALLOCATION, params)
            response = {strings.RESULTS: results}
                                                                
        return response, status_code

class CpfProjection(Resource):
    def post(self):
        response, status_code, params = api_manager.handle_api_request(endpoints.CPF_PROJECTION)
        
        if status_code == HTTPStatus.OK:
            results = router.execute(endpoints.CPF_PROJECTION, params)
            response = {strings.RESULTS: results}

        return response, status_code
