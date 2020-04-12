from logic.cpf import main as cpf_main
from utils import endpoints, strings

def execute(endpoint: str, params: dict) -> dict:
    """Executes the call to the function corresponding to the input endpoint.

    Args:
        endpoint (str): Name of endpoint
        params (dict): Input parameters

    Returns the results of the function call.
    """

    if endpoint == endpoints.CPF_CONTRIBUTION:
        results = cpf_main.calculate_cpf_contribution(
            params[strings.PARAM_SALARY],
            params[strings.PARAM_BONUS],
            params[strings.PARAM_DOB],
            params[strings.PARAM_PERIOD],
        )
    elif endpoint == endpoints.CPF_ALLOCATION:
        results = cpf_main.calculate_cpf_allocation(
            params[strings.PARAM_SALARY],
            params[strings.PARAM_BONUS],
            params[strings.PARAM_DOB],
        )
    elif endpoint == endpoints.CPF_PROJECTION:
        results = cpf_main.calculate_cpf_projection(
            params[strings.PARAM_SALARY],
            params[strings.PARAM_BONUS],
            params[strings.PARAM_YOY_INCREASE_SALARY],
            params[strings.PARAM_DOB],
            params[strings.PARAM_BASE_CPF],
            params[strings.PARAM_BONUS_MONTH],
            params[strings.PARAM_N_YEARS],
            params[strings.PARAM_TARGET_YEAR],
            params[strings.PARAM_OA_TOPUPS],
            params[strings.PARAM_OA_WITHDRAWALS],
            params[strings.PARAM_SA_TOPUPS],
            params[strings.PARAM_SA_WITHDRAWALS],
            params[strings.PARAM_MA_TOPUPS],
            params[strings.PARAM_MA_WITHDRAWALS],
        )

    return results
