from flask_restful import Resource
from http import HTTPStatus
from utils import endpoints, strings

from . import api_manager
from logic.cpf import main as cpf_main

class CpfContribution(Resource):
    def post(self):
        response, status_code, params = api_manager.handle_api_request(endpoints.CPF_CONTRIBUTION)

        if status_code == HTTPStatus.OK:
            results = cpf_main.calculate_cpf_contribution(
                params[strings.PARAM_SALARY],
                params[strings.PARAM_BONUS],
                params[strings.PARAM_DOB],
                params[strings.PARAM_PERIOD],
            )
            response = {strings.RESULTS: results}

        return response, status_code

class CpfAllocation(Resource):
    def post(self):
        response, status_code, params = api_manager.handle_api_request(endpoints.CPF_ALLOCATION)

        if status_code == HTTPStatus.OK:
            results = cpf_main.calculate_cpf_allocation(
                params[strings.PARAM_SALARY],
                params[strings.PARAM_BONUS],
                params[strings.PARAM_DOB],
            )
            response = {strings.RESULTS: results}
                                                                
        return response, status_code

class CpfProjection(Resource):
    def post(self):
        response, status_code, params = api_manager.handle_api_request(endpoints.CPF_PROJECTION)
        
        if status_code == HTTPStatus.OK:
            results = cpf_main.calculate_cpf_projection(
                params[strings.PARAM_SALARY],
                params[strings.PARAM_BONUS],
                params[strings.PARAM_YOY_INCREASE_SALARY],
                params[strings.PARAM_DOB],
                params[strings.PARAM_BASE_CPF],
                params[strings.PARAM_BONUS_MONTH],
                params[strings.PARAM_N_YEARS],
                params[strings.PARAM_TARGET_YEAR],
                params[strings.PARAM_OA_TOPUPS],
                params[strings.PARAM_OA_WITHDRAWALS],
                params[strings.PARAM_SA_TOPUPS],
                params[strings.PARAM_SA_WITHDRAWALS],
                params[strings.PARAM_MA_TOPUPS],
                params[strings.PARAM_MA_WITHDRAWALS],
            )
            response = {strings.RESULTS: results}

        return response, status_code
