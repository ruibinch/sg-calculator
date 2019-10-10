from flask import Flask
from flask_restful import Resource, Api, reqparse

from logic.cpf import calculate_cpf_contribution
from logic.cpf import calculate_cpf_allocation
from logic.cpf import calculate_cpf_projection
from common import endpoints
from lambda_function import parse_params

app = Flask(__name__)
api = Api(app)

# For data validation
parser = reqparse.RequestParser()
# General
parser.add_argument('salary', type=str, help='Annual salary')
parser.add_argument('bonus', type=str, help='Bonus/commission received in the year')
parser.add_argument('bonus_month', type=str, help='Month where bonus is received')
parser.add_argument('age', type=str, help='Age')
parser.add_argument('dob', type=str, help='Date of birth in YYYYMM format')
# Projection-specific
parser.add_argument('yoy_increase_salary', type=str, help='Projected YoY increase of salary')
parser.add_argument('yoy_increase_bonus', type=str, help='Projected YoY increase of bonus')
parser.add_argument('base_cpf', type=dict, help='Base amount in CPF accounts')
parser.add_argument('n_years', type=str, help='Number of years into the future')
parser.add_argument('target_year', type=str, help='Target year in the future to project for')
parser.add_argument('oa_topups', type=dict, help='Top-ups to the OA')
parser.add_argument('oa_withdrawals', type=dict, help='Withdrawals from the OA')
parser.add_argument('sa_topups', type=dict, help='Top-ups to the SA')
parser.add_argument('sa_withdrawals', type=dict, help='Withdrawals from the SA')
parser.add_argument('ma_topups', type=dict, help='Top-ups to the MA')
parser.add_argument('ma_withdrawals', type=dict, help='Withdrawals from the MA')
# For future authentication methods
# parser.add_argument('Authentication', location='headers')

class CpfContribution(Resource):
    def post(self):
        args = parser.parse_args()
        params = parse_params(args, endpoints.ENDPOINT_CPF_CONTRIBUTION)

        body = calculate_cpf_contribution(
            params['salary'],
            params['bonus'],
            params['dob'],
            params['bonus_month']
        )

        return { 'statusCode': 200, 'body': body }

class CpfAllocation(Resource):
    def post(self):
        args = parser.parse_args()
        params = parse_params(args, endpoints.ENDPOINT_CPF_ALLOCATION)

        body = calculate_cpf_allocation(
            params['salary'],
            params['bonus'],
            params['dob']
        )
                                                                
        return { 'statusCode': 200, 'body': body }

class CpfProjection(Resource):
    def post(self):
        args = parser.parse_args()
        params = parse_params(args, endpoints.ENDPOINT_CPF_PROJECTION)

        body = calculate_cpf_projection(
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
                                              
        return { 'statusCode': 200, 'body': body }

api.add_resource(CpfContribution, '/cpf/contribution')
api.add_resource(CpfAllocation, '/cpf/allocation')
api.add_resource(CpfProjection, '/cpf/projection')

if (__name__ == '__main__'):
    app.debug = True
    app.run(host='127.0.0.1', port=5000)