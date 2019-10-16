import json
import logging

from utils import endpoints
from utils import http_codes as http
from utils import strings

logger = logging.getLogger(__name__)

###################################################################################################
#                                    ARGS-PARSING METHODS                                         #
###################################################################################################

def parse_into_json_format(str_raw):
    """
        Parses the input string into a valid JSON string.

        Args:
            str_raw (str): Input string
        
        Returns:
            (str): JSON-appropriate string
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


def extract_param(body, output, param, mould, required=True, defaultValue=None):
    """
        Helper function for extraction of parameters.
        Checks for 2 potential errors:
        1. KeyError - parameter does not exist
        2. ValueError - parameter is of invalid type preventing the type conversion
        3. TypeError - if parameter is to be of dict type but the input cannot be JSON-serialised

        Args:
            body (dict): Contents of request body
            output (dict): Output to be returned
            param (str): Name of desired parameter
            mould (*): Serves as a mould for type-casting
            required (bool): Denote whether this parameter is required
            defaultValue (*): Denotes the default value if the desired parameter is not found
                in the body; mandatory if `required` is set to False

        Returns:
            (dict): Output with an additional entry
    """

    logger.debug(f'Extracting parameter "{param}"')
    try:
        if type(mould) is dict:
            logger.debug(f'Mould is of dict type, param value is {body[param]}')
            param_str = parse_into_json_format(body[param])
            param_json = json.loads(param_str)
            param_value = type(mould)(param_json)
        else:
            param_value = type(mould)(body[param])

        logger.info(f'Setting "{param}" to {param_value}')
        output[strings.KEY_PARAMS][param] = param_value
    except KeyError:
        # param not found
        if required is True:
            logger.error(f'"{param}" parameter not found')
            output[strings.KEY_ERROR][param] = 'Parameter not found'
            output[strings.KEY_STATUSCODE] = http.HTTPCODE_INFO_INCOMPLETE
        else:
            logger.info(f'Setting "{param}" to the default value of {defaultValue}')
            output[strings.KEY_PARAMS][param] = defaultValue
    except ValueError:
        # param found but unable to do type conversion
        logger.error(f'"{param}" is \'{type(body[param]).__name__}\', unable to convert to \'{type(mould).__name__}\'', exc_info=True)
        output[strings.KEY_ERROR][param] = f'Unable to convert \'{type(body[param]).__name__}\' to \'{type(mould).__name__}\''
        output[strings.KEY_STATUSCODE] = http.HTTPCODE_INFO_INVALID
    except TypeError:
        # mould is of dict type, but input is not of a JSON-appropriate format
        logger.error(f'"{param}" should be of dict/object structure but it is not JSON-serialisable', exc_info=True)
        output[strings.KEY_ERROR][param] = f'Should be of dict structure but it is not JSON-serialisable'
        output[strings.KEY_STATUSCODE] = http.HTTPCODE_INFO_INVALID
    except Exception:
        # catch all other general exceptions
        logger.exception('No idea what happened here, gotta take a look at the stack trace')
        output[strings.KEY_ERROR][param] = 'No idea what happened here'
        output[strings.KEY_STATUSCODE] = http.HTTPCODE_ERROR

    return output


def check_conditional_params(body, output, params):
    """
        Helper function to check the presence of parameters whereby at least one is required.
        If both are missing, then throw an error.

        Args:
            body (dict): Contents of request body
            output (dict): Output to be returned
            params (list): List of parameter names, whereby at least one must be present

        Returns:
            (dict): Output to be returned
    """

    body_params = list(body.keys())
    params_present = [param for param in params if param in body_params]

    if len(params_present) == 0:
        output[strings.KEY_STATUSCODE] = http.HTTPCODE_INFO_INCOMPLETE
        params_str = ', '.join(params)
        logger.debug(f'None of ({params_str}) are present')

        for param in params:
            output[strings.KEY_ERROR][param] = f'At least one of ({params_str}) must be present'

    return output
    

def parse_args(body, path):
    """
        Extracts and converts the parameters passed in the request body to the
        appropriate type, as well as handling for optional parameters.

        Args:
            body (dict): Contents of request body
            path (str): Path of endpoint

        Returns:
            (dict): Output of argument parsing process
    """

    MOULD_INT = 0
    MOULD_FLOAT = 0.0
    MOULD_STR = '0'
    MOULD_DICT = {'a': 1}

    keys = [strings.KEY_PARAMS, strings.KEY_ERROR, strings.KEY_STATUSCODE]
    output = {key: {} for key in keys}

    if path == endpoints.ENDPOINT_CPF_CONTRIBUTION:
        logger.debug(f'Calling endpoint {path}')
        output = extract_param(body, output, 'salary', MOULD_FLOAT)
        output = extract_param(body, output, 'bonus', MOULD_FLOAT)
        output = extract_param(body, output, 'dob', MOULD_STR)
        output = extract_param(body, output, 'bonus_month', MOULD_INT, required=False, defaultValue=12)

    elif path == endpoints.ENDPOINT_CPF_ALLOCATION:
        logger.debug(f'Calling endpoint {path}')
        output = extract_param(body, output, 'salary', MOULD_FLOAT)
        output = extract_param(body, output, 'bonus', MOULD_FLOAT)
        output = extract_param(body, output, 'dob', MOULD_STR)

    elif path == endpoints.ENDPOINT_CPF_PROJECTION:
        logger.debug(f'Calling endpoint {path}')
        output = extract_param(body, output, 'salary', MOULD_FLOAT)
        output = extract_param(body, output, 'bonus', MOULD_FLOAT)
        output = extract_param(body, output, 'yoy_increase_salary', MOULD_FLOAT)
        output = extract_param(body, output, 'yoy_increase_bonus', MOULD_FLOAT)
        output = extract_param(body, output, 'dob', MOULD_STR)
        output = extract_param(body, output, 'base_cpf', MOULD_DICT)
        output = extract_param(body, output, 'bonus_month', MOULD_INT, required=False, defaultValue=12)
        output = extract_param(body, output, 'n_years', MOULD_INT, required=False, defaultValue=None)
        output = extract_param(body, output, 'target_year', MOULD_INT, required=False, defaultValue=None)
        output = extract_param(body, output, 'oa_topups', MOULD_DICT, required=False, defaultValue={})
        output = extract_param(body, output, 'oa_withdrawals', MOULD_DICT, required=False, defaultValue={})
        output = extract_param(body, output, 'sa_topups', MOULD_DICT, required=False, defaultValue={})
        output = extract_param(body, output, 'sa_withdrawals', MOULD_DICT, required=False, defaultValue={})
        output = extract_param(body, output, 'ma_topups', MOULD_DICT, required=False, defaultValue={})
        output = extract_param(body, output, 'ma_withdrawals', MOULD_DICT, required=False, defaultValue={})
        output = check_conditional_params(body, output, ['n_years', 'target_year'])

    return output