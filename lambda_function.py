import json
from logic import cpf


# Names of the endpoints used in AWS API Gateway
ENDPOINT_CPF_CONTRIBUTION = '/cpf/contribution'
ENDPOINT_CPF_ALLOCATION = '/cpf/allocation'
ENDPOINT_CPF_PROJECTION = '/cpf/projection'


def handler(event, context):
    body = json.loads(event['body'])
    params = parse_params(body, event['path'])

    if event['path'] == ENDPOINT_CPF_CONTRIBUTION:
        response = cpf.calculate_cpf_contribution(
            params['salary'],
            params['bonus'],
            params['dob'],
            params['bonus_month']
        )
    elif event['path'] == ENDPOINT_CPF_ALLOCATION:
        response = cpf.calculate_cpf_allocation(
            params['salary'],
            params['bonus'],
            params['dob']
        )
    elif event['path'] == ENDPOINT_CPF_PROJECTION:
        response = cpf.calculate_cpf_projection(
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

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }


def parse_params(body, path):
    """
        Extracts and converts the parameters passed in the request body to the
        appropriate type, as well as handling for optional parameters.
    """

    # TODO: some checking to ensure that all params in `body` are of types str/dict, else return a error

    if path == ENDPOINT_CPF_CONTRIBUTION:
        salary = float(body['salary'])
        bonus = float(body['bonus'])
        dob = body['dob']
        bonus_month = body['bonus_month'] if 'bonus_month' in body.keys() else 12

        return {
            'salary': salary,
            'bonus': bonus,
            'dob': dob,
            'bonus_month': bonus_month
        }
    elif path == ENDPOINT_CPF_ALLOCATION:
        salary = float(body['salary'])
        bonus = float(body['bonus'])
        dob = body['dob']

        return {
            'salary': salary,
            'bonus': bonus,
            'dob': dob
        }
    elif path == ENDPOINT_CPF_PROJECTION:
        salary = float(body['salary'])
        bonus = float(body['bonus'])
        yoy_increase_salary = float(body['yoy_increase_salary'])
        yoy_increase_bonus = float(body['yoy_increase_bonus'])
        dob = body['dob']
        base_cpf = body['base_cpf']
        bonus_month = body['bonus_month'] if 'bonus_month' in body.keys() else 12
        n_years = int(n_years) if n_years is not None else None
        target_year = int(target_year) if target_year is not None else None
        oa_topups = oa_topups if oa_topups is not None else {}
        oa_withdrawals = oa_withdrawals if oa_withdrawals is not None else {}
        sa_topups = sa_topups if sa_topups is not None else {}
        sa_withdrawals = sa_withdrawals if sa_withdrawals is not None else {}
        ma_topups = ma_topups if ma_topups is not None else {}
        ma_withdrawals = ma_withdrawals if ma_withdrawals is not None else {}

        return {
            'salary': salary,
            'bonus': bonus,
            'yoy_increase_salary': yoy_increase_salary,
            'yoy_increase_bonus': yoy_increase_bonus,
            'dob': dob,
            'base_cpf': base_cpf,
            'bonus_month': bonus_month,
            'n_years': n_years,
            'target_year': target_year,
            'oa_topups': oa_topups,
            'oa_withdrawals': oa_withdrawals,
            'sa_topups': sa_topups,
            'sa_withdrawals': sa_withdrawals,
            'ma_topups': ma_topups,
            'ma_withdrawals': ma_withdrawals
        }