from http import HTTPStatus
import json
import logging

from .utils import endpoints, strings

logger = logging.getLogger(__name__)

"""
Handles parsing and conversion into the appropriate types of request arguments.
"""

###############################################################################
#                                 HELPER METHODS                              #
###############################################################################

def parse_into_json_format(str_raw):
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

def extract_param(body, output, param, mould, required=True, allowed_values=None, default_value=None):
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

    Returns an output dict with an additional entry, either in output[strings.KEY_PARAMS][param] or
    output[strings.KEY_ERROR][param].
        
    If there is an error, output[strings.KEY_STATUSCODE] will be populated as well.
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
                output[strings.KEY_ERROR][param] = f'"{param_value}" is an invalid value'
                output[strings.KEY_STATUSCODE] = HTTPStatus.UNPROCESSABLE_ENTITY
        else:
            is_param_value_ok = True

        if is_param_value_ok:
            logger.info(f'Setting "{param}" to {param_value}')
            output[strings.KEY_PARAMS][param] = param_value

    except KeyError:
        # param not found
        if required:
            logger.error(f'"{param}" parameter not found')
            output[strings.KEY_ERROR][param] = 'Parameter not found'
            output[strings.KEY_STATUSCODE] = HTTPStatus.BAD_REQUEST
        else:
            logger.info(f'Setting "{param}" to the default value of {default_value}')
            output[strings.KEY_PARAMS][param] = default_value
    except ValueError:
        # param found but unable to do type conversion
        logger.error(f'"{param}" is \'{type(body[param]).__name__}\', unable to convert to \'{type(mould).__name__}\'', exc_info=True)
        output[strings.KEY_ERROR][param] = f'Unable to convert \'{type(body[param]).__name__}\' to \'{type(mould).__name__}\''
        output[strings.KEY_STATUSCODE] = HTTPStatus.UNPROCESSABLE_ENTITY
    except TypeError:
        # mould is of dict type, but input is not of a JSON-appropriate format
        logger.error(f'"{param}" should be of dict/object structure but it is not JSON-serialisable', exc_info=True)
        output[strings.KEY_ERROR][param] = f'Should be of dict structure but it is not JSON-serialisable'
        output[strings.KEY_STATUSCODE] = HTTPStatus.UNPROCESSABLE_ENTITY
    except Exception:
        # catch all other general exceptions
        logger.exception('No idea what happened here, gotta take a look at the stack trace')
        output[strings.KEY_ERROR][param] = 'No idea what happened here'
        output[strings.KEY_STATUSCODE] = HTTPStatus.INTERNAL_SERVER_ERROR

    return output

def check_conditional_params(body, output, params):
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
        output[strings.KEY_STATUSCODE] = HTTPStatus.BAD_REQUEST
        params_str = ', '.join(params)
        logger.debug(f'None of ({params_str}) are present')

        for param in params:
            output[strings.KEY_ERROR][param] = f'At least one of ({params_str}) must be present'

    return output

###############################################################################
#                                   MAIN METHOD                               #
###############################################################################

def parse_args(body, path):
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
    keys = [strings.KEY_PARAMS, strings.KEY_ERROR, strings.KEY_STATUSCODE]
    output = {key: {} for key in keys}

    if path == endpoints.CPF_CONTRIBUTION:
        output = extract_param(body, output, 'salary', MOULD_FLOAT)
        output = extract_param(body, output, 'bonus', MOULD_FLOAT)
        output = extract_param(body, output, 'dob', MOULD_STR)
        output = extract_param(body, output, 'period', MOULD_STR,
                    allowed_values=[strings.STR_YEAR, strings.STR_MONTH])

    elif path == endpoints.CPF_ALLOCATION:
        output = extract_param(body, output, 'salary', MOULD_FLOAT)
        output = extract_param(body, output, 'bonus', MOULD_FLOAT)
        output = extract_param(body, output, 'dob', MOULD_STR)

    elif path == endpoints.CPF_PROJECTION:
        logger.debug(f'Calling endpoint {path}')
        output = extract_param(body, output, 'salary', MOULD_FLOAT)
        output = extract_param(body, output, 'bonus', MOULD_FLOAT)
        output = extract_param(body, output, 'yoy_increase_salary', MOULD_FLOAT)
        output = extract_param(body, output, 'yoy_increase_bonus', MOULD_FLOAT)
        output = extract_param(body, output, 'dob', MOULD_STR)
        output = extract_param(body, output, 'base_cpf', MOULD_DICT)
        output = extract_param(body, output, 'bonus_month', MOULD_INT,
                    required=False, default_value=12,
                    allowed_values=range(1, 13))
        output = extract_param(body, output, 'n_years', MOULD_INT,
                    required=False, default_value=None)
        output = extract_param(body, output, 'target_year', MOULD_INT,
                    required=False, default_value=None)
        output = extract_param(body, output, 'oa_topups', MOULD_DICT,
                    required=False, default_value={})
        output = extract_param(body, output, 'oa_withdrawals', MOULD_DICT,
                    required=False, default_value={})
        output = extract_param(body, output, 'sa_topups', MOULD_DICT,
                    required=False, default_value={})
        output = extract_param(body, output, 'sa_withdrawals', MOULD_DICT,
                    required=False, default_value={})
        output = extract_param(body, output, 'ma_topups', MOULD_DICT,
                    required=False, default_value={})
        output = extract_param(body, output, 'ma_withdrawals', MOULD_DICT,
                    required=False, default_value={})

        output = check_conditional_params(body, output, ['n_years', 'target_year'])

    return output
