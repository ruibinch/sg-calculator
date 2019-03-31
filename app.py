from flask import Flask
from flask_restful import Resource, Api, reqparse

from logic.cpf import calculate_future_cpf_balance

app = Flask(__name__)
api = Api(app)

# for data validation
parser = reqparse.RequestParser()
parser.add_argument('age', type=int, help='Age')
parser.add_argument('salary', type=int, help='Current salary')
parser.add_argument('yoy_increase', type=float, help='Projected YoY increase of salary')
parser.add_argument('base_cpf', type=list, help='Base amount in CPF accounts')
parser.add_argument('n_years', type=int, help='Number of years into the future')


class Cpf(Resource):
    def post(self):
        args = parser.parse_args()
        oa, sa, ma = calculate_future_cpf_balance(args['age'],
                                                  args['salary'],
                                                  args['yoy_increase'],
                                                  args['base_cpf'],
                                                  args['n_years'])

        return { 'oa': oa, 'sa': sa, 'ma': ma }

api.add_resource(Cpf, '/cpf')

if (__name__ == '__main__'):
    app.debug = True
    app.run(host='127.0.0.1', port=5000)