import datetime as dt
import logging
import math
from typing import Tuple

from . import constants
from app.utils import strings

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

    if purpose == constants.STR_CONTRIBUTION:
        keys = constants.rates_cont.keys()
    elif purpose == constants.STR_ALLOCATION:
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

def _convert_year_to_zero_indexing(dict_orig: dict) -> dict:
    """Converts the year values in the list from the actual year to zero indexing based on the current year.

    Args:
        dict_orig (dict): Original dict of topups/withdrawals, where key is date in YYYYMM format

    Returns a dict with the format:
        {
            <zero-indexed year>: { 
                <month>: {
                    'amount' : <amount>,
                    'is_sa_topup_from_oa': <boolean>
                }
            }
        }
    """

    dict_new = {}

    for key in dict_orig.keys():
        date = key # in YYYY or YYYYMM format
        amount = dict_orig[key][strings.KEY_AMOUNT]

        # extract year and month (if applicable) from the date
        year = int(date[0:4])
        month = int(date[4:6]) if date[4:6] is not '' else 0

        year_zero_index = int(year) - dt.date.today().year
        if year_zero_index not in dict_new.keys():
            # create an empty object if this year is not in the new dict yet
            dict_new[year_zero_index] = {}

        if strings.KEY_IS_SA_TOPUP_FROM_OA in dict_orig[key]:
            # this will be used only if it is a SA topup
            dict_new[year_zero_index][month] = {
                strings.KEY_AMOUNT: amount,
                strings.KEY_IS_SA_TOPUP_FROM_OA: dict_orig[key][strings.KEY_IS_SA_TOPUP_FROM_OA]
            }
        else:
            dict_new[year_zero_index][month] = {
                strings.KEY_AMOUNT: amount
            }

    return dict_new

def _get_account_deltas_year(deltas: dict,
                             year: int) -> dict:
    """Returns the topup/withdrawal entries in the list that correspond to the current year. \\

        Args:
            deltas (dict): Topup/withdrawal entries
            year (int): Zero-indexed year
    """
    
    return deltas[year] if year in deltas.keys() else {}

def _get_account_deltas_month(account_deltas: dict,
                              month_curr: int) -> Tuple[int, int, int]:
    """Returns the amount deltas in the respective OA, SA and MA accounts.

        Args:
            account_deltas (dict): List of keys:
                [`oa_topups`, `oa_withdrawals`, `sa_topups`, `sa_withdrawals`, `ma_topups`, `ma_withdrawals`]
            month_curr (int): Current month in numeric representation

        Returns a tuple containing:
            - Delta change in OA in this month
            - Delta change in SA in this month
            - Delta change in MA in this month
    """

    delta_oa, delta_sa, delta_ma = (0, 0, 0)
    months_search = [month_curr]
    if month_curr == 1:
        # account topups/withdrawals with no specified month are defaulted to occur in Jan
        months_search.append(0)

    for delta_type in account_deltas.keys():
        if delta_type == strings.KEY_OA_TOPUPS:
            for month in account_deltas[delta_type]:
                delta_oa += float(account_deltas[delta_type][month][strings.KEY_AMOUNT]) if month in months_search else 0
        elif delta_type == strings.KEY_OA_WITHDRAWALS:
            for month in account_deltas[delta_type]:
                delta_oa -= float(account_deltas[delta_type][month][strings.KEY_AMOUNT]) if month in months_search else 0
        elif delta_type == strings.KEY_SA_TOPUPS:
            for month in account_deltas[delta_type]:
                if month in months_search:
                    month_delta = account_deltas[delta_type][month]
                    delta_sa += float(month_delta[strings.KEY_AMOUNT])
                    delta_oa -= float(month_delta[strings.KEY_AMOUNT]) if month_delta[strings.KEY_IS_SA_TOPUP_FROM_OA] else 0
        elif delta_type == strings.KEY_SA_WITHDRAWALS:
            for month in account_deltas[delta_type]:
                delta_sa -= float(account_deltas[delta_type][month][strings.KEY_AMOUNT]) if month in months_search else 0
        elif delta_type == strings.KEY_MA_TOPUPS:
            for month in account_deltas[delta_type]:
                delta_ma += float(account_deltas[delta_type][month][strings.KEY_AMOUNT]) if month in months_search else 0
        elif delta_type == strings.KEY_MA_WITHDRAWALS:
            for month in account_deltas[delta_type]:
                delta_ma -= float(account_deltas[delta_type][month][strings.KEY_AMOUNT]) if month in months_search else 0

    return (delta_oa, delta_sa, delta_ma)

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
