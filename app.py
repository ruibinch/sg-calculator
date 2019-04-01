from flask import Flask
from flask_restful import Resource, Api, reqparse

from logic.cpf import calculate_cpf_contribution
from logic.cpf import calculate_cpf_projection

app = Flask(__name__)
api = Api(app)

# for data validation
parser = reqparse.RequestParser()
parser.add_argument('age', type=int, help='Age')
parser.add_argument('salary', type=float, help='Annual salary')
parser.add_argument('bonus', type=float, help='Bonus/commission received in the year')
parser.add_argument('yoy_increase', type=float, help='Projected YoY increase of salary')
parser.add_argument('base_cpf', type=list, help='Base amount in CPF accounts')
parser.add_argument('n_years', type=int, help='Number of years into the future')

class CpfContribution(Resource):
    def post(self):
        args = parse.parse_args()
        cont_employee, cont_employer = calculate_cpf_contribution(args['age'],
                                                                  args['salary'],
                                                                  args['bonus'])
        return { 'cont_employee': cont_employee, 'cont_employer': cont_employer }

class CpfAllocation(Resource):
    def post(self):


class CpfProjection(Resource):
    def post(self):
        args = parser.parse_args()
        oa, sa, ma = calculate_cpf_projection(args['age'],
                                              args['salary'],
                                              args['yoy_increase'],
                                              args['base_cpf'],
                                              args['n_years'])

        return { 'oa': oa, 'sa': sa, 'ma': ma }

api.add_resource(CpfContribution, '/cpf/contribution')
api.add_resource(CpfAllocation, '/cpf/allocation')
api.add_resource(CpfProjection, '/cpf/projection')

if (__name__ == '__main__'):
    app.debug = True
    app.run(host='127.0.0.1', port=5000)