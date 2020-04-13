from flask_restful import Resource
from . import api_manager
from utils import endpoints

class CpfContribution(Resource):
    def post(self):
        return api_manager.handler(endpoints.CPF_CONTRIBUTION)

class CpfAllocation(Resource):
    def post(self):
        return api_manager.handler(endpoints.CPF_ALLOCATION)

class CpfProjection(Resource):
    def post(self):
        return api_manager.handler(endpoints.CPF_PROJECTION)
