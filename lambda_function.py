from http import HTTPStatus
import json

from logic import router
from utils import argvalidator, endpoints, strings

def handler(event: dict, context: dict) -> dict:
    """Handler for AWS Lambda function calls.

    Args:
        event (dict): Contains information on the function call event
        context (dict): Provides information about the invocation, function and execution environment
        
    Returns an object with the following keys:
        - `statusCode` - HTTP status code
        - `body` - Response body
    """

    body = json.loads(event[strings.BODY])
    output = argvalidator.run(body, event[strings.PATH])

    if output[strings.STATUSCODE]:
        # there is a status code denoting an error
        status_code = output[strings.STATUSCODE]
        response = {strings.ERROR: output[strings.ERROR]}
    else:
        status_code = HTTPStatus.OK
        params = output[strings.PARAMS]
        results = router.execute(event[strings.PATH], params)
        response = {strings.RESULTS: results}

    return {
        strings.STATUSCODE: status_code,
        strings.BODY: json.dumps(response)
    }
