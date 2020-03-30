from http import HTTPStatus
import json

from logic.cpf import main as cpf_main
from utils import argparser, endpoints, strings

def handler(event: dict, context: dict) -> dict:
    """Handler for AWS Lambda function calls.

    Args:
        event (dict): Contains information on the function call event
        context (dict): Provides information about the invocation, function and execution environment
        
    Returns an object with the following keys:
        - `statusCode` - HTTP status code
        - `body` - Response body
    """

    body = json.loads(event[strings.KEY_BODY])
    output = argparser.parse_args(body, event[strings.KEY_PATH])

    if type(output[strings.KEY_STATUSCODE]) is int:
        # there is a status code denoting an error
        status_code = output[strings.KEY_STATUSCODE]
        response = {strings.KEY_ERROR: output[strings.KEY_ERROR]}
    else:
        status_code = HTTPStatus.OK
        params = output[strings.KEY_PARAMS]
        if event[strings.KEY_PATH] == endpoints.CPF_CONTRIBUTION:
            results = cpf_main.calculate_cpf_contribution(
                params['salary'],
                params['bonus'],
                params['dob'],
                params['period']
            )
        elif event[strings.KEY_PATH] == endpoints.CPF_ALLOCATION:
            results = cpf_main.calculate_cpf_allocation(
                params['salary'],
                params['bonus'],
                params['dob']
            )
        elif event[strings.KEY_PATH] == endpoints.CPF_PROJECTION:
            results = cpf_main.calculate_cpf_projection(
                params['salary'],
                params['bonus'],
                params['yoy_increase_salary'],
                params['yoy_increase_bonus'],
                params['dob'],
                params['base_cpf'],
                params['bonus_month'],
                params['n_years'],
                params['target_year'],
                params['oa_topups'],
                params['oa_withdrawals'],
                params['sa_topups'],
                params['sa_withdrawals'],
                params['ma_topups'],
                params['ma_withdrawals']
            )

        response = {strings.KEY_RESULTS: results}

    return {
        strings.KEY_STATUSCODE: status_code,
        strings.KEY_BODY: json.dumps(response)
    }
