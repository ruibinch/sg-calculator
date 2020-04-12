import datetime as dt
import logging
import math
from typing import Tuple

from . import constants
from utils import strings

logger = logging.getLogger(__name__)

"""
Stores all generic helper methods for the CPF module.
"""

def _get_age(dob: str,
             date_curr: dt=None) -> int:
    """Returns the user's age given the user's date of birth.

    If a date is explicitly specified, calculate the user's age from the specified date. 
    Else, use today's date. \\
    Age is determined using this logic:
    "Your employee is considered to be 35, 45, 50, 55, 60 or 65 years old in the month
    of his 35th, 45th, 50th, 55th, 60th or 65th birthday. The employee will be above 
    35, 45, 50, 55, 60 or 65 years from the month after the month of his 
    35th, 45th, 50th, 55th, 60th or 65th birthday." \\
    Reference: https://www.cpf.gov.sg/Employers/EmployerGuides/employer-guides/paying-cpf-contributions/cpf-contribution-and-allocation-rates

    Args:
        dob (str): Date of birth of employee in YYYYMM format
    """

    birth_year, birth_month = int(dob[0:4]), int(dob[4:6])
    if date_curr is not None:
        curr_year, curr_month = (date_curr.year, date_curr.month)
    else:
        curr_year, curr_month = (dt.date.today().year, dt.date.today().month)

    year_diff, month_diff = (curr_year - birth_year, curr_month - birth_month)
    age = year_diff if month_diff <= 0 else year_diff + 1
    return age

def _get_age_bracket(age: int,
                     purpose: str) -> str:
    """Gets the age bracket for the specified purpose and age.

    Args:
        age (int): Age of employee
        purpose (str): Either "contribution" or "allocation"
    """

    if purpose == strings.CONTRIBUTION:
        keys = constants.rates_cont.keys()
    elif purpose == strings.ALLOCATION:
        keys = constants.rates_alloc.keys()

    for key in keys:
        if age <= int(key):
            return key
    
    return '150' # return max by default

def _get_num_projection_years(target_year: int) -> int:
    """Returns the number of years between this year and the target year (inclusive).

    Args:
        target_year (int): Target year in the future to project for
    """

    return target_year - dt.date.today().year + 1

def _extract_account_deltas(account_deltas: list) \
                            -> Tuple[float, float, float]:
    """Extracts the account deltas and computes the final delta amounts for the 3 accounts.

    Args:
        account_deltas (list): List of topups/withdrawals to be made to the accounts in the year

    Returns a tuple containing the deltas to the OA, SA and MA.
    """

    oa_delta, sa_delta, ma_delta = 0, 0, 0

    for delta in account_deltas:
        amount = float(delta[strings.AMOUNT])

        if delta[strings.TYPE] == strings.OA_TOPUP:
            oa_delta += amount
        elif delta[strings.TYPE] == strings.OA_WITHDRAWAL:
            oa_delta -= amount
        if delta[strings.TYPE] == strings.SA_TOPUP:
            sa_delta += amount
            if delta[strings.IS_SA_TOPUP_FROM_OA]:
                oa_delta -= amount
        elif delta[strings.TYPE] == strings.SA_WITHDRAWAL:
            sa_delta -= amount
        elif delta[strings.TYPE] == strings.MA_TOPUP:
            ma_delta += amount
        elif delta[strings.TYPE] == strings.MA_WITHDRAWAL:
            ma_delta -= amount
        
    return oa_delta, sa_delta, ma_delta

###############################################################################
#                                  MATH METHODS                               #
###############################################################################

def _round_half_up(n: float,
                   decimals: int=0) -> int:
    """Rounds the given monetary amount to the nearest dollar.
    
    An amount of 50 cents will be regarded as an additional dollar.

    Args:
        n (float): input amount
    """

    multiplier = 10 ** decimals
    return math.floor(n*multiplier + 0.5) / multiplier

def _truncate(n: float,
              decimals: int=2) -> float:
    """Truncates the given monetary amount to the specified number of decimal places.

    Args:
        n (float): input amount
    """

    before_dec, after_dec = str(n).split('.')
    return float('.'.join((before_dec, after_dec[0:2])))
