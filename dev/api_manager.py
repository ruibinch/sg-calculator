from flask_restful import Api, reqparse
from http import HTTPStatus
from typing import Tuple

from logic import router
from utils import argvalidator, endpoints, strings

parser = reqparse.RequestParser()

def add_arguments():
    """Adds expected arguments to the RequestParser."""

    # General
    parser.add_argument(strings.PARAM_SALARY, help='Annual salary')
    parser.add_argument(strings.PARAM_BONUS, help='Bonus represented as a multiplier of monthly salary')
    parser.add_argument(strings.PARAM_AGE, help='Age')
    parser.add_argument(strings.PARAM_DOB, help='Date of birth in YYYYMM format')
    parser.add_argument(strings.PARAM_PERIOD, help='Time period; either year or month')
    # Projection-specific
    parser.add_argument(strings.PARAM_BONUS_MONTH, help='Month where bonus is received')
    parser.add_argument(strings.PARAM_YOY_INCREASE_SALARY, help='Projected YoY increase of salary')
    parser.add_argument(strings.PARAM_BASE_CPF, type=dict, help='Base amount in CPF accounts')
    parser.add_argument(strings.PARAM_N_YEARS, help='Number of years into the future')
    parser.add_argument(strings.PARAM_TARGET_YEAR, help='Target year in the future to project for')
    parser.add_argument(strings.PARAM_ACCOUNT_DELTAS, type=dict, action='append', help='List of topups/withdrawals to be made to the accounts')
    # For future authentication methods
    # parser.add_argument('Authentication', location='headers')

def handler(endpoint: str) -> Tuple[dict, int]:
    """Handler for the Flask endpoints.
    
    Args:
        endpoint (str): Endpoint to connect to

    Returns a tuple:
        - `response` (dict) - only populated if there is an error in the params
        - `status_code` (int) - HTTP status code representation
    """
    
    response, params = None, None
    args = parser.parse_args()
    output = argvalidator.run(args, endpoint)
    
    if output[strings.STATUSCODE]:
        status_code = output[strings.STATUSCODE]
        response = {strings.ERROR: output[strings.ERROR]}
    else:
        status_code = HTTPStatus.OK
        params = output[strings.PARAMS]
        results = router.execute(endpoint, params)
        response = {strings.RESULTS: results}

    return response, status_code

def init(app):
    """Initialises the Flask app.

    Defines the following components of the REST API:
    - Argument parser
    - Routes
    """

    # parser for data validation
    add_arguments()

    # define API routes
    from .routes import CpfAllocation, CpfContribution, CpfProjection
    api = Api(app)
    
    api.add_resource(CpfContribution, endpoints.CPF_CONTRIBUTION)
    api.add_resource(CpfAllocation, endpoints.CPF_ALLOCATION)
    api.add_resource(CpfProjection, endpoints.CPF_PROJECTION)
