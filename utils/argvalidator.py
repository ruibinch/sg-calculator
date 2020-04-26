from http import HTTPStatus
import json
import logging
from typing import Any

from . import endpoints, strings
from logic.housing import constants as hsg_constants
from logic.housing.hdb import constants as hdb_constants

logger = logging.getLogger(__name__)

###############################################################################
#                                 HELPER METHODS                              #
###############################################################################

def extract_param(body: dict,
                  output: dict,
                  param: str,
                  mould: Any = None,
                  required: bool = True,
                  allowed_values: list = None,
                  default_value: Any = None) -> dict:
    """Extracts parameters from the request body and converts it to the appropriate type.
       
    Checks for 2 potential errors:
        1. KeyError - parameter does not exist
        2. ValueError - parameter is of invalid type thus preventing the type conversion

    Args:
        body (dict): Contents of request body
        output (dict): Output to be returned
        param (str): Name of desired parameter
        mould (*): Serves as a mould for typecasting numbers
        required (bool): Denote whether this parameter is required
        allowed_values (list): List of allowed values for this parameter
        default_value (*): Denotes the default value if the desired parameter is not found in the body;
            mandatory if `required` is set to False

    Returns an output dict with an additional entry, either in output[strings.PARAMS][param] or
    output[strings.ERROR][param].
        
    If there is an error, output[strings.STATUSCODE] will be populated as well.
    """

    try:
        # extract param value and typecast it if applicable
        if mould is not None and (type(mould) is int or type(mould) is float):
            param_value = type(mould)(body[param])
        else:
            param_value = body[param]

        if allowed_values is not None and param_value not in allowed_values:
            # param value is not allowed
            logger.error(f'"{param_value}" is an invalid value for parameter "{param}"')
            output[strings.ERROR][param] = f'"{param_value}" is an invalid value'
            output[strings.STATUSCODE] = HTTPStatus.UNPROCESSABLE_ENTITY
        else:
            # param value is allowed
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
        logger.error(f'"{param}" is \'{type(body[param]).__name__}\', '
                     f'unable to convert to \'{type(mould).__name__}\'',
                     exc_info=True)
        output[strings.ERROR][param] = ('Unable to convert '
                                        f'\'{type(body[param]).__name__}\''
                                        f' to \'{type(mould).__name__}\'')
        output[strings.STATUSCODE] = HTTPStatus.UNPROCESSABLE_ENTITY
    except Exception:
        # catch all other general exceptions
        logger.exception('No idea what happened here, gotta take a look at the stack trace')
        output[strings.ERROR][param] = 'Some unforeseen exception happened here'
        output[strings.STATUSCODE] = HTTPStatus.INTERNAL_SERVER_ERROR

    return output

def check_conditional_params(body: dict,
                             output: dict,
                             params_req: list) -> dict:
    """Checks that at least one of the specified parameters is present in the request body. 
        
    If none of them are present, then throw an error.

    Args:
        body (dict): Contents of request body
        output (dict): Output to be returned
        params_req (list): List of parameter names, whereby at least one must be present

    Returns the output dict with modifications if an error is encountered.
    """

    params_req_present = [param for param in params_req if param in body.keys()]

    if not params_req_present:
        output[strings.STATUSCODE] = HTTPStatus.BAD_REQUEST
        params_str = ', '.join(params_req)
        logger.debug(f'None of ({params_str}) are present')

        # add an error message for each of the params
        for param in params_req:
            output[strings.ERROR][param] = (f'At least one of ({params_str})'
                                            'must be present')

    return output

###############################################################################
#                                   MAIN METHOD                               #
###############################################################################

def run(body: dict, path: str) -> dict:  
    """Extracts and performs validation on the arguments passed in the request body.

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

    # filter out params where value is None
    body = {k:v for k,v in body.items() if v is not None}
    # moulds for typecasting of numbers
    MOULD_INT = 0
    MOULD_FLOAT = 0.0

    logger.debug(f'Calling endpoint {path}')
    keys = [strings.PARAMS, strings.ERROR, strings.STATUSCODE]
    output = {key: {} for key in keys}

    if path == endpoints.CPF_CONTRIBUTION:
        output = extract_param(
            body, output, strings.PARAM_SALARY,
            mould=MOULD_FLOAT)
        output = extract_param(
            body, output, strings.PARAM_BONUS,
            mould=MOULD_FLOAT)
        output = extract_param(
            body, output, strings.PARAM_DOB)
        output = extract_param(
            body, output, strings.PARAM_PERIOD,
            allowed_values=[strings.YEAR, strings.MONTH])

    elif path == endpoints.CPF_ALLOCATION:
        output = extract_param(
            body, output, strings.PARAM_SALARY,
            mould=MOULD_FLOAT)
        output = extract_param(
            body, output, strings.PARAM_BONUS,
            mould=MOULD_FLOAT)
        output = extract_param(
            body, output, strings.PARAM_DOB)

    elif path == endpoints.CPF_PROJECTION:
        output = extract_param(
            body, output, strings.PARAM_SALARY,
            mould=MOULD_FLOAT)
        output = extract_param(
            body, output, strings.PARAM_BONUS,
            mould=MOULD_FLOAT)
        output = extract_param(
            body, output, strings.PARAM_YOY_INCREASE_SALARY,
            mould=MOULD_FLOAT)
        output = extract_param(
            body, output, strings.PARAM_DOB)
        output = extract_param(
            body, output, strings.PARAM_BASE_CPF)
        output = extract_param(
            body, output, strings.PARAM_BONUS_MONTH,
            mould=MOULD_INT,
            required=False,
            default_value=12,
            allowed_values=range(1, 13))
        output = extract_param(
            body, output, strings.PARAM_N_YEARS,
            mould=MOULD_INT,
            required=False,
            default_value=None)
        output = extract_param(
            body, output, strings.PARAM_TARGET_YEAR,
            mould=MOULD_INT,
            required=False,
            default_value=None)
        output = extract_param(
            body, output, strings.PARAM_ACCOUNT_DELTAS,
            required=False,
            default_value=[])

        output = check_conditional_params(
            body, output, 
            [strings.PARAM_N_YEARS, strings.PARAM_TARGET_YEAR])

    elif path == endpoints.HOUSING_MAX_MORTGAGE:
        output = extract_param(
            body, output, strings.PARAM_PROPERTY_TYPE,
            allowed_values=[hsg_constants.PROPERTY_EC, hsg_constants.PROPERTY_HDB, hsg_constants.PROPERTY_PRIVATE])
        output = extract_param(
            body, output, strings.PARAM_FIXED_INCOME,
            mould=MOULD_FLOAT)
        output = extract_param(
            body, output, strings.PARAM_VARIABLE_INCOME,
            mould=MOULD_FLOAT,
            required=False,
            default_value=0)
        output = extract_param(
            body, output, strings.PARAM_PROPERTY_LOANS,
            mould=MOULD_FLOAT,
            required=False,
            default_value=0)
        output = extract_param(
            body, output, strings.PARAM_PROPERTY_LOANS_GUARANTOR,
            mould=MOULD_FLOAT,
            required=False,
            default_value=0)
        output = extract_param(
            body, output, strings.PARAM_OTHER_LOANS,
            mould=MOULD_FLOAT,
            required=False,
            default_value=0)

    elif path == endpoints.HOUSING_HDB_CPF_GRANTS:
        output = extract_param(
            body, output, strings.PARAM_APPL_PERIOD,
            allowed_values=[strings.BEFORE_SEP_2019, strings.SEP_2019_ONWARDS])
        output = extract_param(
            body, output, strings.PARAM_FLAT_TYPE,
            allowed_values=[strings.BTO, strings.RESALE])
        output = extract_param(
            body, output, strings.PARAM_PROFILE,
            allowed_values=[
                hdb_constants.PROFILE_BOTH_FT,
                hdb_constants.PROFILE_BOTH_ST,
                hdb_constants.PROFILE_FT_ST,
                hdb_constants.PROFILE_NONSC_SPOUSE,
                hdb_constants.PROFILE_SC_SPR,
                hdb_constants.PROFILE_SG_SINGLE,
                hdb_constants.PROFILE_SG_SINGLE_ORPHAN,
            ])
        output = extract_param(
            body, output, strings.PARAM_INCOME,
            mould=MOULD_FLOAT,
            default_value=0)
        output = extract_param(
            body, output, strings.PARAM_ESTATE,
            allowed_values=[strings.MATURE, strings.NONMATURE])
        output = extract_param(
            body, output, strings.PARAM_FLAT_SIZE,
            allowed_values=[
                hdb_constants.SIZE_2RM,
                hdb_constants.SIZE_3RM,
                hdb_constants.SIZE_4RM,
                hdb_constants.SIZE_5RM,
                hdb_constants.SIZE_3GEN,
                hdb_constants.SIZE_EXEC,
            ])
        output = extract_param(
            body, output, strings.PARAM_NEAR_PARENTS,
            required=False)
        
    return output
