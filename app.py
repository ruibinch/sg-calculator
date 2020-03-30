from flask import Flask
from flask_restful import Api, Resource, reqparse
from http import HTTPStatus
from typing import Tuple

from logic.cpf import main as cpf_main
from utils import argparser, config, endpoints, strings

app = Flask(__name__)
api = Api(app)
parser = reqparse.RequestParser() # for data validation

###############################################################################
#                                  HELPER METHODS                             #
###############################################################################

def add_arguments(parser: reqparse.RequestParser):
    """Adds expected arguments to the RequestParser."""

    # General
    parser.add_argument(strings.PARAM_SALARY, help='Annual salary')
    parser.add_argument(strings.PARAM_BONUS, help='Bonus/commission received in the year')
    parser.add_argument(strings.PARAM_AGE, help='Age')
    parser.add_argument(strings.PARAM_DOB, help='Date of birth in YYYYMM format')
    parser.add_argument(strings.PARAM_PERIOD, help='Time period; either year or month')
    # Projection-specific
    parser.add_argument(strings.PARAM_BONUS_MONTH, help='Month where bonus is received')
    parser.add_argument(strings.PARAM_YOY_INCREASE_SALARY, help='Projected YoY increase of salary')
    parser.add_argument(strings.PARAM_YOY_INCREASE_BONUS, help='Projected YoY increase of bonus')
    parser.add_argument(strings.PARAM_BASE_CPF, help='Base amount in CPF accounts')
    parser.add_argument(strings.PARAM_N_YEARS, help='Number of years into the future')
    parser.add_argument(strings.PARAM_TARGET_YEAR, help='Target year in the future to project for')
    parser.add_argument(strings.PARAM_OA_TOPUPS, help='Top-ups to the OA')
    parser.add_argument(strings.PARAM_OA_WITHDRAWALS, help='Withdrawals from the OA')
    parser.add_argument(strings.PARAM_SA_TOPUPS, help='Top-ups to the SA')
    parser.add_argument(strings.PARAM_SA_WITHDRAWALS, help='Withdrawals from the SA')
    parser.add_argument(strings.PARAM_MA_TOPUPS, help='Top-ups to the MA')
    parser.add_argument(strings.PARAM_MA_WITHDRAWALS, help='Withdrawals from the MA')
    # For future authentication methods
    # parser.add_argument('Authentication', location='headers')

def handle_api_request(parser: reqparse.RequestParser, 
                       endpoint: str) -> Tuple[dict, int, dict]:
    """Defines the API handlers for the Flask endpoints.
    
    Args:
        parser (RequestParser): Argument parser of flask_restful library
        endpoint (str): Endpoint to connect to

    Returns a tuple:
        - `response` - only populated if there is an error in the params
        - `status_code` - HTTP status code representation
    """
    
    args = parser.parse_args()
    args = {k:v for k,v in args.items() if v is not None}
    output = argparser.parse_args(args, endpoint)

    if not output[strings.STATUSCODE]:
        status_code = output[strings.STATUSCODE]
        response = {strings.ERROR: output[strings.ERROR]}
    else:
        status_code = HTTPStatus.OK
        params = output[strings.PARAMS]

    return response, status_code, params

###############################################################################
#                                     ROUTES                                  #
###############################################################################

class CpfContribution(Resource):
    def post(self):
        response, status_code, params = handle_api_request(parser, endpoints.CPF_CONTRIBUTION)

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
        response, status_code, params = handle_api_request(parser, endpoints.CPF_ALLOCATION)

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
        response, status_code, params = handle_api_request(parser, endpoints.CPF_PROJECTION)
        
        if status_code == HTTPStatus.OK:
            results = cpf_main.calculate_cpf_projection(
                params[strings.PARAM_SALARY],
                params[strings.PARAM_BONUS],
                params[strings.PARAM_YOY_INCREASE_SALARY],
                params[strings.PARAM_YOY_INCREASE_BONUS],
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

api.add_resource(CpfContribution, endpoints.CPF_CONTRIBUTION)
api.add_resource(CpfAllocation, endpoints.CPF_ALLOCATION)
api.add_resource(CpfProjection, endpoints.CPF_PROJECTION)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config.FLASK_PORT, debug=True)
