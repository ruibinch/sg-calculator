import json
import requests

from utils import http_codes
from utils import endpoints

# AWS config
RESTAPI_ID = '3myv824x89'
REGION = 'ap-southeast-1'
STAGE_NAME = 'alpha'
# API Gateway URLs
URL_CPF_CONTRIBUTION = f'https://{RESTAPI_ID}.execute-api.{REGION}.amazonaws.com/{STAGE_NAME}{endpoints.ENDPOINT_CPF_CONTRIBUTION}'
URL_CPF_ALLOCATION = f'https://{RESTAPI_ID}.execute-api.{REGION}.amazonaws.com/{STAGE_NAME}{endpoints.ENDPOINT_CPF_ALLOCATION}'
URL_CPF_PROJECTION = f'https://{RESTAPI_ID}.execute-api.{REGION}.amazonaws.com/{STAGE_NAME}{endpoints.ENDPOINT_CPF_PROJECTION}'

class TestLambdaFunction(object):
    """
    Tests the Lambda functions via the exposed endpoints on API Gateway.

    Performs assertions on just the returned status code; logic testing is handled in `test_cpf.py`.
    """

    def test_contribution_1(self):
        request = { "salary": "6000", "bonus": "0", "dob": "199001" }
        response = requests.post(URL_CPF_CONTRIBUTION, json.dumps(request))
        assert response.status_code == http_codes.HTTPCODE_OK

    def test_contribution_2(self):
        request = { "bonus": "0", "dob": "199001" }
        response = requests.post(URL_CPF_CONTRIBUTION, json.dumps(request))
        assert response.status_code == http_codes.HTTPCODE_INFO_INCOMPLETE

    def test_contribution_3(self):
        request = { "salary": "6000", "dob": "199001" }
        response = requests.post(URL_CPF_CONTRIBUTION, json.dumps(request))
        assert response.status_code == http_codes.HTTPCODE_INFO_INCOMPLETE

    def test_contribution_4(self):
        request = { "salary": "6000", "bonus": "0" }
        response = requests.post(URL_CPF_CONTRIBUTION, json.dumps(request))
        assert response.status_code == http_codes.HTTPCODE_INFO_INCOMPLETE
    
    def test_contribution_5(self):
        request = { "salary": "(6000)", "bonus": "0", "dob": "199001" }
        response = requests.post(URL_CPF_CONTRIBUTION, json.dumps(request))
        assert response.status_code == http_codes.HTTPCODE_INFO_INVALID
    
    def test_contribution_6(self):
        request = { "salary": "6000", "bonus": "('0')", "dob": "199001" }
        response = requests.post(URL_CPF_CONTRIBUTION, json.dumps(request))
        assert response.status_code == http_codes.HTTPCODE_INFO_INVALID
    
    def test_allocation_1(self):
        request = { "salary": "6000", "bonus": "0", "dob": "199001" }
        response = requests.post(URL_CPF_ALLOCATION, json.dumps(request))
        assert response.status_code == http_codes.HTTPCODE_OK

    def test_allocation_2(self):
        request = { "bonus": "0", "dob": "199001" }
        response = requests.post(URL_CPF_ALLOCATION, json.dumps(request))
        assert response.status_code == http_codes.HTTPCODE_INFO_INCOMPLETE

    def test_allocation_3(self):
        request = { "salary": "6000", "dob": "199001" }
        response = requests.post(URL_CPF_ALLOCATION, json.dumps(request))
        assert response.status_code == http_codes.HTTPCODE_INFO_INCOMPLETE

    def test_allocation_4(self):
        request = { "salary": "6000", "bonus": "0" }
        response = requests.post(URL_CPF_ALLOCATION, json.dumps(request))
        assert response.status_code == http_codes.HTTPCODE_INFO_INCOMPLETE

    def test_allocation_5(self):
        request = { "salary": "(6000)", "bonus": "0", "dob": "199001" }
        response = requests.post(URL_CPF_ALLOCATION, json.dumps(request))
        assert response.status_code == http_codes.HTTPCODE_INFO_INVALID

    def test_allocation_6(self):
        request = { "salary": "6000", "bonus": "('0')", "dob": "199001" }
        response = requests.post(URL_CPF_ALLOCATION, json.dumps(request))
        assert response.status_code == http_codes.HTTPCODE_INFO_INVALID

    def test_projection_1(self):
        request = {
            "salary": "50000",
            "bonus": "20000",
            "yoy_increase_salary": "0.05",
            "yoy_increase_bonus": "0.05",
            "base_cpf": {
                "oa": "1000",
                "sa": "1000",
                "ma": "1000"
            },
            "dob": "198403",
            "n_years": "5",
            "oa_withdrawals": {
                "202001": {
                    "amount": "5000"
                }
            },
            "ma_withdrawals": {
                "202001": {
                    "amount": "10000"
                }
            },
            "sa_topups": {
                "202003": {
                    "amount": "5000",
                    "is_sa_topup_from_oa": False
                }
            }
        }
        response = requests.post(URL_CPF_PROJECTION, json.dumps(request))
        assert response.status_code == http_codes.HTTPCODE_OK

    def test_projection_2(self):
        # `base_cpf` in wrong structure
        request = {
            "salary": "50000",
            "bonus": "20000",
            "yoy_increase_salary": "0.05",
            "yoy_increase_bonus": "0.05",
            "base_cpf": ["1000"],
            "dob": "198403",
            "n_years": "5"
        }
        response = requests.post(URL_CPF_PROJECTION, json.dumps(request))
        assert response.status_code == http_codes.HTTPCODE_INFO_INVALID

    def test_projection_3(self):
        # both `n_years` and `target_year` missing
        request = {
            "salary": "50000",
            "bonus": "20000",
            "yoy_increase_salary": "0.05",
            "yoy_increase_bonus": "0.05",
            "base_cpf": {
                "oa": "1000",
                "sa": "1000",
                "ma": "1000"
            },
            "dob": "198403"
        }
        response = requests.post(URL_CPF_PROJECTION, json.dumps(request))
        assert response.status_code == http_codes.HTTPCODE_INFO_INCOMPLETE
