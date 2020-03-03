from flask import request
from flask_restful import Resource, reqparse
from http import HTTPStatus

from . import argparser
from .logic.cpf import main as cpf_main
from .utils import endpoints, strings

# For data validation
parser = reqparse.RequestParser()
# General
parser.add_argument('salary', help='Annual salary')
parser.add_argument('bonus', help='Bonus/commission received in the year')
parser.add_argument('age', help='Age')
parser.add_argument('dob', help='Date of birth in YYYYMM format')
parser.add_argument('period', help='Time period; either year or month')
# Projection-specific
parser.add_argument('bonus_month', help='Month where bonus is received')
parser.add_argument('yoy_increase_salary', help='Projected YoY increase of salary')
parser.add_argument('yoy_increase_bonus', help='Projected YoY increase of bonus')
parser.add_argument('base_cpf', help='Base amount in CPF accounts')
parser.add_argument('n_years', help='Number of years into the future')
parser.add_argument('target_year', help='Target year in the future to project for')
parser.add_argument('oa_topups', help='Top-ups to the OA')
parser.add_argument('oa_withdrawals', help='Withdrawals from the OA')
parser.add_argument('sa_topups', help='Top-ups to the SA')
parser.add_argument('sa_withdrawals', help='Withdrawals from the SA')
parser.add_argument('ma_topups', help='Top-ups to the MA')
parser.add_argument('ma_withdrawals', help='Withdrawals from the MA')
# For future authentication methods
# parser.add_argument('Authentication', location='headers')

class CpfContribution(Resource):
    def post(self):
        args = parser.parse_args()
        args = {k:v for k,v in args.items() if v is not None}
        output = argparser.parse_args(args, endpoints.CPF_CONTRIBUTION)

        if output[strings.KEY_STATUSCODE] != {}:
            status_code = output[strings.KEY_STATUSCODE]
            response = {strings.KEY_ERROR: output[strings.KEY_ERROR]}
        else:
            status_code = HTTPStatus.OK
            params = output[strings.KEY_PARAMS]
            results = cpf_main.calculate_cpf_contribution(
                params['salary'],
                params['bonus'],
                params['dob'],
                params['period']
            )
            response = {strings.KEY_RESULTS: results}

        return response, status_code

class CpfAllocation(Resource):
    def post(self):
        args = parser.parse_args()
        args = {k:v for k,v in args.items() if v is not None}
        output = argparser.parse_args(args, endpoints.CPF_ALLOCATION)

        if output[strings.KEY_STATUSCODE] != {}:
            status_code = output[strings.KEY_STATUSCODE]
            response = {strings.KEY_ERROR: output[strings.KEY_ERROR]}
        else:
            status_code = HTTPStatus.OK
            params = output[strings.KEY_PARAMS]
            results = cpf_main.calculate_cpf_allocation(
                params['salary'],
                params['bonus'],
                params['dob']
            )
            response = {strings.KEY_RESULTS: results}
                                                                
        return response, status_code

class CpfProjection(Resource):
    def post(self):
        args = parser.parse_args()
        args = {k:v for k,v in args.items() if v is not None}
        output = argparser.parse_args(args, endpoints.CPF_PROJECTION)

        if output[strings.KEY_STATUSCODE] != {}:
            status_code = output[strings.KEY_STATUSCODE]
            response = {strings.KEY_ERROR: output[strings.KEY_ERROR]}
        else:
            status_code = HTTPStatus.OK
            params = output[strings.KEY_PARAMS]
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

        return response, status_code