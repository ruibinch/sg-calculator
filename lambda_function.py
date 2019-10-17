import json

from logic import cpf
from utils import endpoints
from utils import helpers
from utils import http_codes as http
from utils import strings


def handler(event, context):
    body = json.loads(event[strings.KEY_BODY])
    output = helpers.parse_args(body, event[strings.KEY_PATH])

    if type(output[strings.KEY_STATUSCODE]) is int:
        # there is a status code denoting an error
        status_code = output[strings.KEY_STATUSCODE]
        response = { strings.KEY_ERROR: output[strings.KEY_ERROR] }
    else:
        status_code = http.HTTPCODE_OK
        params = output[strings.KEY_PARAMS]
        if event[strings.KEY_PATH] == endpoints.ENDPOINT_CPF_CONTRIBUTION:
            results = cpf.calculate_cpf_contribution(
                params['salary'],
                params['bonus'],
                params['dob'],
                params['bonus_month']
            )
        elif event[strings.KEY_PATH] == endpoints.ENDPOINT_CPF_ALLOCATION:
            results = cpf.calculate_cpf_allocation(
                params['salary'],
                params['bonus'],
                params['dob']
            )
        elif event[strings.KEY_PATH] == endpoints.ENDPOINT_CPF_PROJECTION:
            results = cpf.calculate_cpf_projection(
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

        response = { strings.KEY_RESULTS: results }

    return {
        strings.KEY_STATUSCODE: status_code,
        strings.KEY_BODY: json.dumps(response)
    }
