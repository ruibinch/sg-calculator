from logic.cpf import main as cpf_main
from logic.housing import main as housing_main
from logic.housing.hdb import main as housing_hdb_main
from utils import endpoints, strings

def execute(endpoint: str, params: dict) -> dict:
    """Executes the call to the function corresponding to the input endpoint.

    Args:
        endpoint (str): Name of endpoint
        params (dict): Input parameters

    Returns the results of the function call.
    """

    if endpoint == endpoints.CPF_CONTRIBUTION:
        results = cpf_main.calc_cpf_contribution(
            params[strings.PARAM_SALARY],
            params[strings.PARAM_BONUS],
            params[strings.PARAM_DOB],
            params[strings.PARAM_PERIOD])

    elif endpoint == endpoints.CPF_ALLOCATION:
        results = cpf_main.calc_cpf_allocation(
            params[strings.PARAM_SALARY],
            params[strings.PARAM_BONUS],
            params[strings.PARAM_DOB])

    elif endpoint == endpoints.CPF_PROJECTION:
        results = cpf_main.calc_cpf_projection(
            params[strings.PARAM_SALARY],
            params[strings.PARAM_BONUS],
            params[strings.PARAM_YOY_INCREASE_SALARY],
            params[strings.PARAM_DOB],
            params[strings.PARAM_BASE_CPF],
            params[strings.PARAM_BONUS_MONTH],
            params[strings.PARAM_N_YEARS],
            params[strings.PARAM_TARGET_YEAR],
            params[strings.PARAM_ACCOUNT_DELTAS])

    elif endpoint == endpoints.HOUSING_MAX_MORTGAGE:
        results = housing_main.calc_max_mortgage(
            params[strings.PARAM_PROPERTY_TYPE],
            params[strings.PARAM_FIXED_INCOME],
            params[strings.PARAM_VARIABLE_INCOME],
            params[strings.PARAM_PROPERTY_LOANS],
            params[strings.PARAM_PROPERTY_LOANS_GUARANTOR],
            params[strings.PARAM_OTHER_LOANS])

    elif endpoint == endpoints.HOUSING_HDB_CPF_GRANTS:
        results = housing_hdb_main.find_grant_schemes(
            params[strings.PARAM_APPL_PERIOD],
            params[strings.PARAM_FLAT_TYPE],
            params[strings.PARAM_PROFILE],
            params[strings.PARAM_INCOME],
            params[strings.PARAM_ESTATE],
            params[strings.PARAM_FLAT_SIZE],
            params[strings.PARAM_NEAR_PARENTS]
        )

    return results
