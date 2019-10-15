import json

from logic import cpf
from utils import common
from utils import endpoints
from utils import http_codes as http


def handler(event, context):
    body = json.loads(event['body'])
    output = common.parse_args(body, event['path'])

    if output['statusCode'] != {}:
        status_code = output['statusCode']
        response = { 'error': output['error'] }
    else:
        status_code = http.HTTPCODE_OK
        params = output['params']
        if event['path'] == endpoints.ENDPOINT_CPF_CONTRIBUTION:
            results = cpf.calculate_cpf_contribution(
                params['salary'],
                params['bonus'],
                params['dob'],
                params['bonus_month']
            )
        elif event['path'] == endpoints.ENDPOINT_CPF_ALLOCATION:
            results = cpf.calculate_cpf_allocation(
                params['salary'],
                params['bonus'],
                params['dob']
            )
        elif event['path'] == endpoints.ENDPOINT_CPF_PROJECTION:
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
        response = { 'results': results }

    return {
        'statusCode': status_code,
        'body': json.dumps(response)
    }
