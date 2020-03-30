from http import HTTPStatus
import json
import logging
from typing import Any

from . import endpoints, strings

logger = logging.getLogger(__name__)

"""
Handles parsing and conversion into the appropriate types of request arguments.
"""

###############################################################################
#                                 HELPER METHODS                              #
###############################################################################

def parse_into_json_format(str_raw: str) -> str:
    """Parses the input string into a valid string for JSON serialisation.

    Args:
        str_raw (str): Input raw string
    """

    s = str_raw
    try:
        s = s.replace('\'', '"')
        s = s.replace('True', 'true')
        s = s.replace('False', 'false')
    except AttributeError:
        # `str_raw` is not a string
        pass

    logger.debug(f'Parsed {str_raw} into {s}')
    return s

def extract_param(body: dict,
                  output: dict,
                  param: str,
                  mould: Any,
                  required: bool=True,
                  allowed_values: list=None,
                  default_value: Any=None) -> dict:
    """Extracts parameters from the request body and converts it to the appropriate type.
       
    Checks for 2 potential errors:
        1. KeyError - parameter does not exist
        2. ValueError - parameter is of invalid type preventing the type conversion
        3. TypeError - if parameter is to be of dict type but the input cannot be JSON-serialised

    Args:
        body (dict): Contents of request body
        output (dict): Output to be returned
        param (str): Name of desired parameter
        mould (*): Serves as a mould for typecasting
        required (bool): Denote whether this parameter is required
        allowed_values (list): List of allowed values for this parameter
        default_value (*): Denotes the default value if the desired parameter is not found
            in the body; mandatory if `required` is set to False

    Returns an output dict with an additional entry, either in output[strings.PARAMS][param] or
    output[strings.ERROR][param].
        
    If there is an error, output[strings.STATUSCODE] will be populated as well.
    """

    try:
        if type(body[param]) is str and type(mould) is dict:
            # special handling for str->dict conversions is required
            # i.e. parse string into a JSON-appropriate format before converting to dict type
            logger.debug(f'Mould is of dict type, param value "{body[param]}" is of {type(body[param])} type')
            param_str = parse_into_json_format(body[param])
            param_json = json.loads(param_str)
            param_value = type(mould)(param_json)
        else:
            param_value = type(mould)(body[param])

        # check if extracted param value is allowed
        is_param_value_ok = False
        if allowed_values is not None:
            if param_value in allowed_values:
                is_param_value_ok = True
            else:
                logger.error(f'"{param_value}" is an invalid value for parameter "{param}"')
                output[strings.ERROR][param] = f'"{param_value}" is an invalid value'
                output[strings.STATUSCODE] = HTTPStatus.UNPROCESSABLE_ENTITY
        else:
            is_param_value_ok = True

        if is_param_value_ok:
            logger.info(f'Setting "{param}" to {param_value}')
            output[strings.PARAMS][param] = param_value

    except KeyError:
        # param not found
        if required:
            logger.error(f'"{param}" parameter not found')
            output[strings.ERROR][param] = 'Parameter not found'
            output[strings.STATUSCODE] = HTTPStatus.BAD_REQUEST
        else:
            logger.info(f'Setting "{param}" to the default value of {default_value}')
            output[strings.PARAMS][param] = default_value
    except ValueError:
        # param found but unable to do type conversion
        logger.error(f'"{param}" is \'{type(body[param]).__name__}\', unable to convert to \'{type(mould).__name__}\'', exc_info=True)
        output[strings.ERROR][param] = f'Unable to convert \'{type(body[param]).__name__}\' to \'{type(mould).__name__}\''
        output[strings.STATUSCODE] = HTTPStatus.UNPROCESSABLE_ENTITY
    except TypeError:
        # mould is of dict type, but input is not of a JSON-appropriate format
        logger.error(f'"{param}" should be of dict/object structure but it is not JSON-serialisable', exc_info=True)
        output[strings.ERROR][param] = f'Should be of dict structure but it is not JSON-serialisable'
        output[strings.STATUSCODE] = HTTPStatus.UNPROCESSABLE_ENTITY
    except Exception:
        # catch all other general exceptions
        logger.exception('No idea what happened here, gotta take a look at the stack trace')
        output[strings.ERROR][param] = 'No idea what happened here'
        output[strings.STATUSCODE] = HTTPStatus.INTERNAL_SERVER_ERROR

    return output

def check_conditional_params(body: dict,
                             output: dict,
                             params: list) -> dict:
    """Checks that at least one of the specified parameters is present in the request body. 
        
    If none of them are present, then throw an error.

    Args:
        body (dict): Contents of request body
        output (dict): Output to be returned
        params (list): List of parameter names, whereby at least one must be present

    Returns the output dict with modifications if an error is encountered.
    """

    body_params = list(body.keys())
    params_present = [param for param in params if param in body_params]

    if len(params_present) == 0:
        output[strings.STATUSCODE] = HTTPStatus.BAD_REQUEST
        params_str = ', '.join(params)
        logger.debug(f'None of ({params_str}) are present')

        for param in params:
            output[strings.ERROR][param] = f'At least one of ({params_str}) must be present'

    return output

###############################################################################
#                                   MAIN METHOD                               #
###############################################################################

def parse_args(body: dict,
               path: str) -> dict:  
    """Extracts and parses the arguments passed in the request body to their appropriate types.

    Args:
        body (dict): Contents of request body
        path (str): Path of endpoint

    Returns a dict with 3 main keys:
        1. `params` - an object with the following key-value pairs:
            - key: name of parameter
            - value: extracted value of parameter
        2. `error` - an object with the following key-value pairs:
            - key: name of parameter
            - value: error reason
        3. `statusCode` - if there is any error, a HTTP status code will be stored here;
            else it will be empty
    """

    # moulds for typecasting
    MOULD_INT = 0
    MOULD_FLOAT = 0.0
    MOULD_STR = '0'
    MOULD_DICT = {'a': 1}

    logger.debug(f'Calling endpoint {path}')
    keys = [strings.PARAMS, strings.ERROR, strings.STATUSCODE]
    output = {key: {} for key in keys}

    if path == endpoints.CPF_CONTRIBUTION:
        output = extract_param(body, output, strings.PARAM_SALARY, MOULD_FLOAT)
        output = extract_param(body, output, strings.PARAM_BONUS, MOULD_FLOAT)
        output = extract_param(body, output, strings.PARAM_DOB, MOULD_STR)
        output = extract_param(body, output, strings.PARAM_PERIOD, MOULD_STR,
                               allowed_values=[strings.YEAR, strings.MONTH])

    elif path == endpoints.CPF_ALLOCATION:
        output = extract_param(body, output, strings.PARAM_SALARY, MOULD_FLOAT)
        output = extract_param(body, output, strings.PARAM_BONUS, MOULD_FLOAT)
        output = extract_param(body, output, strings.PARAM_DOB, MOULD_STR)

    elif path == endpoints.CPF_PROJECTION:
        logger.debug(f'Calling endpoint {path}')
        output = extract_param(body, output, strings.PARAM_SALARY, MOULD_FLOAT)
        output = extract_param(body, output, strings.PARAM_BONUS, MOULD_FLOAT)
        output = extract_param(body, output, strings.PARAM_YOY_INCREASE_SALARY, MOULD_FLOAT)
        output = extract_param(body, output, strings.PARAM_YOY_INCREASE_BONUS, MOULD_FLOAT)
        output = extract_param(body, output, strings.PARAM_DOB, MOULD_STR)
        output = extract_param(body, output, strings.PARAM_BASE_CPF, MOULD_DICT)
        output = extract_param(body, output, strings.PARAM_BONUS_MONTH, MOULD_INT,
                               required=False, default_value=12,
                               allowed_values=range(1, 13))
        output = extract_param(body, output, strings.PARAM_N_YEARS, MOULD_INT,
                               required=False, default_value=None)
        output = extract_param(body, output, strings.PARAM_TARGET_YEAR, MOULD_INT,
                               required=False, default_value=None)
        output = extract_param(body, output, strings.PARAM_OA_TOPUPS, MOULD_DICT,
                               required=False, default_value={})
        output = extract_param(body, output, strings.PARAM_OA_WITHDRAWALS, MOULD_DICT,
                               required=False, default_value={})
        output = extract_param(body, output, strings.PARAM_SA_TOPUPS, MOULD_DICT,
                               required=False, default_value={})
        output = extract_param(body, output, strings.PARAM_SA_WITHDRAWALS, MOULD_DICT,
                               required=False, default_value={})
        output = extract_param(body, output, strings.PARAM_MA_TOPUPS, MOULD_DICT,
                               required=False, default_value={})
        output = extract_param(body, output, strings.PARAM_MA_WITHDRAWALS, MOULD_DICT,
                               required=False, default_value={})

        output = check_conditional_params(body, 
                                          output, 
                                          [strings.PARAM_N_YEARS, strings.PARAM_TARGET_YEAR]
                                         )

    return output
