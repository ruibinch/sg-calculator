from flask import Flask
from flask_restful import Api
import os

from . import config
from app.utils import endpoints

def create_app() -> Flask:
    """Application factory.

    Returns the Flask application object.
    """

    app = Flask(__name__)
    app.config.from_object(config.Config)

    with app.app_context():
        define_routes(app)
        return app

def define_routes(app: Flask):
    """Maps API endpoints to Flask resources.""" 

    from .routes import CpfContribution, CpfAllocation, CpfProjection

    api = Api(app)
    
    api.add_resource(CpfContribution, endpoints.CPF_CONTRIBUTION)
    api.add_resource(CpfAllocation, endpoints.CPF_ALLOCATION)
    api.add_resource(CpfProjection, endpoints.CPF_PROJECTION)
