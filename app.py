from flask import Flask
from flask_restful import Resource, Api, reqparse

from logic.cpf import calculate_cpf_contribution
from logic.cpf import calculate_cpf_allocation
from logic.cpf import calculate_cpf_projection

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
parser.add_argument('base_cpf', type=list, help='Base amount in CPF accounts')
parser.add_argument('n_years', type=str, help='Number of years into the future')
parser.add_argument('target_year', type=str, help='Target year in the future to project for')
parser.add_argument('oa_topups', type=list, help='Top-ups to the OA')
parser.add_argument('oa_withdrawals', type=list, help='Withdrawals from the OA')
parser.add_argument('sa_topups', type=list, help='Top-ups to the SA')
parser.add_argument('sa_withdrawals', type=list, help='Withdrawals from the SA')
parser.add_argument('ma_topups', type=list, help='Top-ups to the MA')
parser.add_argument('ma_withdrawals', type=list, help='Withdrawals from the MA')
# For future authentication methods
# parser.add_argument('Authentication', location='headers')

class CpfContribution(Resource):
    def post(self):
        args = parser.parse_args()
        cont_employee, cont_employer = calculate_cpf_contribution(float(args['salary']),
                                                                  float(args['bonus']),
                                                                  bonus_month=int(args['bonus_month']),
                                                                  dob=args['dob'])
        return { 'cont_employee': cont_employee, 'cont_employer': cont_employer }

class CpfAllocation(Resource):
    def post(self):
        args = parser.parse_args()
        oa_alloc, sa_alloc, ma_alloc = calculate_cpf_allocation(float(args['salary']),
                                                                float(args['bonus']),
                                                                dob=args['dob'])
        return { 'oa_alloc': oa_alloc, 'sa_alloc': sa_alloc, 'ma_alloc': ma_alloc }

class CpfProjection(Resource):
    def post(self):
        args = parser.parse_args()
        oa, sa, ma = calculate_cpf_projection(float(args['salary']),
                                              float(args['bonus']),
                                              float(args['yoy_increase_salary']),
                                              float(args['yoy_increase_bonus']),
                                              args['base_cpf'],
                                              bonus_month=args['bonus_month'],
                                              dob=args['dob'],
                                              n_years=int(args['n_years']),
                                              target_year=int(args['target_year']),
                                              oa_topups=args['oa_topups'],
                                              oa_withdrawals=args['oa_withdrawals'],
                                              sa_topups=args['sa_topups'],
                                              sa_withdrawals=args['sa_withdrawals'],
                                              ma_topups=args['ma_topups'],
                                              ma_withdrawals=args['ma_withdrawals']
                                             )
                                              
        return { 'oa': oa, 'sa': sa, 'ma': ma }

api.add_resource(CpfContribution, '/cpf/contribution')
api.add_resource(CpfAllocation, '/cpf/allocation')
api.add_resource(CpfProjection, '/cpf/projection')

if (__name__ == '__main__'):
    app.debug = True
    app.run(host='127.0.0.1', port=5000)