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

    body = json.loads(event[strings.BODY])
    output = argparser.parse_args(body, event[strings.PATH])

    if type(output[strings.STATUSCODE]) is int:
        # there is a status code denoting an error
        status_code = output[strings.STATUSCODE]
        response = {strings.ERROR: output[strings.ERROR]}
    else:
        status_code = HTTPStatus.OK
        params = output[strings.PARAMS]

        if event[strings.PATH] == endpoints.CPF_CONTRIBUTION:
            results = cpf_main.calculate_cpf_contribution(
                params[strings.PARAM_SALARY],
                params[strings.PARAM_BONUS],
                params[strings.PARAM_DOB],
                params[strings.PARAM_PERIOD],
            )
        elif event[strings.PATH] == endpoints.CPF_ALLOCATION:
            results = cpf_main.calculate_cpf_allocation(
                params[strings.PARAM_SALARY],
                params[strings.PARAM_BONUS],
                params[strings.PARAM_DOB],
            )
        elif event[strings.PATH] == endpoints.CPF_PROJECTION:
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

    return {
        strings.STATUSCODE: status_code,
        strings.BODY: json.dumps(response)
    }
