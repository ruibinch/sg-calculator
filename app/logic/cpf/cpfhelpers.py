import datetime as dt
import logging
import math

from . import constants, genhelpers, main
from app.utils import strings

logger = logging.getLogger(__name__)

"""
Stores all CPF module helper methods that contain some element of CPF-related logic.
"""

###############################################################################
#                               CPF CONTRIBUTIONS                             #
###############################################################################

def _get_monthly_contribution_amount(salary: float,
                                     bonus: float,
                                     age: int,
                                     entity: str) -> float:
    """Gets the monthly CPF contribution amount for the specified entity corresponding to the 
    correct age and income bracket.

    OW Ceiling: $6k a month. \\
    AW Ceiling: $102k - OW amount subject to CPF in the year.

    Args:
        salary (float): Monthly salary of employee
        bonus (float): Bonus/commission received in the month
        age (int): Age of employee
        entity (str): Either "combined" or "employee"
    
    Returns the CPF contribution amount for the month.
    """

    age_bracket = genhelpers._get_age_bracket(age, constants.STR_CONTRIBUTION)
    rates = constants.rates_cont
    amount_tw = salary + bonus # only needed if income is in income brackets 2 or 3

    if salary <= constants.INCOME_BRACKET_1:
        cont = 0
        # logger.debug('Salary <=$50/month, total contribution is zero')
    elif salary <= constants.INCOME_BRACKET_2:
        cont = rates[age_bracket][1][entity] * amount_tw
        # logger.debug(f'Salary >$50 to <=$500/month, contribution from TW is {cont}')
    elif salary <= constants.INCOME_BRACKET_3:
        cont_from_tw = rates[age_bracket][2][entity] * amount_tw
        cont_misc = rates[age_bracket][2][constants.STR_MISC] * (amount_tw - 500)
        cont = cont_from_tw + cont_misc
        # logger.debug(f'Salary >$500 to <=$749/month, contribution from OW is {cont}')
    else:
        amount_ow_eligible_for_cpf = min(salary, constants.CEILING_OW)
        cont_from_ow = rates[age_bracket][3][entity] * amount_ow_eligible_for_cpf
        # logger.debug(f'Salary >=$750/month, contribution from OW is {cont_from_ow}')

        cont_from_aw = 0
        if bonus > 0:
            # need to consider AW
            ceiling_aw = constants.CEILING_AW - (amount_ow_eligible_for_cpf * 12)
            amount_aw_eligible_for_cpf = min(bonus, ceiling_aw)
            cont_from_aw = rates[age_bracket][3][entity] * amount_aw_eligible_for_cpf
            # logger.debug(f'Salary >=$750/month with bonus, contribution from AW is {cont_from_aw}')

        cont_total = cont_from_ow + cont_from_aw
        if entity == constants.STR_COMBINED:
            cont = genhelpers._round_half_up(cont_total)
        elif entity == constants.STR_EMPLOYEE:
            cont = math.floor(cont_total)

    return cont

def _get_contribution_rates(salary: float,
                            age: int) -> dict:
    """Returns the contribution rates of the employee and employer.
    
    Args:
        salary (float): Monthly salary of employee
        age (int): Age of employee
    """

    logger.debug(f'Monthly salary = {salary}, age = {age}')
    cont_rates = {}

    # get age bracket
    age_bracket = genhelpers._get_age_bracket(age, constants.STR_CONTRIBUTION)
    rates = constants.rates_cont[age_bracket]

    # get income bracket
    if salary <= constants.INCOME_BRACKET_1:
        cont_rates = {
            strings.KEY_CONT_EMPLOYEE: {},
            strings.KEY_CONT_EMPLOYER: {}
        }
    elif salary <= constants.INCOME_BRACKET_2:
        cont_rates = {
            strings.KEY_CONT_EMPLOYEE: {},
            strings.KEY_CONT_EMPLOYER: {
                'TW': str(rates[1][constants.STR_COMBINED])
            }
        }
    elif salary <= constants.INCOME_BRACKET_3:
        cont_rates = {
            strings.KEY_CONT_EMPLOYEE: {
                'TW - $500': str(rates[2][constants.STR_MISC])
            },
            strings.KEY_CONT_EMPLOYER: {
                'TW': str(rates[2][constants.STR_COMBINED])
            } 
        }
    else:
        cont_employer_rate = round(rates[3][constants.STR_COMBINED] - rates[3][constants.STR_EMPLOYEE], 2)
        cont_rates = {
            strings.KEY_CONT_EMPLOYEE: {
                'OW': str(rates[3][constants.STR_EMPLOYEE]),
                'AW': str(rates[3][constants.STR_EMPLOYEE])
            },
            strings.KEY_CONT_EMPLOYER: {
                'OW': str(cont_employer_rate),
                'AW': str(cont_employer_rate)
            },
        }

    return cont_rates

###############################################################################
#                                 CPF ALLOCATIONS                             #
###############################################################################

def _get_allocation_amount(age: int,
                           cont: int,
                           account: str) -> float:
    """Gets the amount allocated into the specified CPF account in a month.
    
    Returned amount is truncated to 2 decimal places.

    Args:
        age (int): Age of employee
        cont (int): Total CPF contribution for the month
        account (str): Either "SA" or "MA"

    Returns the amount allocated into the specified account.
    """

    age_bracket = genhelpers._get_age_bracket(age, constants.STR_ALLOCATION)
    alloc = genhelpers._truncate(constants.rates_alloc[age_bracket][f'{account}_ratio'] * cont)
    return alloc

def _get_allocation_rates(age: int) -> dict:
    """Returns the allocation rates into the 3 CPF accounts.

    2 representations:
    1. `pct_of_salary` - percentage of salary
    2. `ratio` - ratio of contribution amount in the month (for greater precision)
    
    Args:
        age (int): Age of employee
    """

    age_bracket = genhelpers._get_age_bracket(age, constants.STR_ALLOCATION)
    rates = constants.rates_alloc[age_bracket]

    alloc_rates = {
        'pct_of_salary': {
            strings.KEY_OA: str(rates[constants.STR_OA]),
            strings.KEY_SA: str(rates[constants.STR_SA]),
            strings.KEY_MA: str(rates[constants.STR_MA])
        },
        'ratio': {
            strings.KEY_OA: str(rates[f'{constants.STR_OA}_ratio']),
            strings.KEY_SA: str(rates[f'{constants.STR_SA}_ratio']),
            strings.KEY_MA: str(rates[f'{constants.STR_MA}_ratio'])
        }
    }

    return alloc_rates

###############################################################################
#                                 CPF INTEREST                                #
###############################################################################

def _calculate_monthly_interest_oa(oa_accumulated: float) -> float:
    """Calculates the interest to be added to the OA in a month period.

    Args:
        oa_accumulated (float): Current amount in OA
    """

    oa_interest = oa_accumulated * (constants.INT_RATE_OA / 12)
    return oa_interest

def _calculate_monthly_interest_sa(oa_accumulated: float,
                                   sa_accumulated: float,
                                   rem_amount_for_extra_int_sa_ma: float) -> float:
    """Calculates the interest to be added to the SA in a month period.
    
    Extra 1% interest earned on OA, if any, is credited to the SA.

    Args:
        oa_accumulated (float): Current amount in OA
        sa_accumulated (float): Current amount in SA
        rem_amount_for_extra_int_sa_ma (float): Remaining amount in SA and MA that is applicable for 1% extra interest
    """

    sa_interest = 0

    # first, add the extra 1% interest earned on OA 
    sa_interest += min(oa_accumulated, constants.THRESHOLD_EXTRAINT_OA) * (constants.INT_EXTRA / 12)

    # then, add the interest earned on SA
    if sa_accumulated > rem_amount_for_extra_int_sa_ma:
        sa_interest += rem_amount_for_extra_int_sa_ma * ((constants.INT_RATE_SA + constants.INT_EXTRA) / 12)
        sa_interest += (sa_accumulated - rem_amount_for_extra_int_sa_ma) * (constants.INT_RATE_SA / 12)
    else:
        sa_interest += sa_accumulated * ((constants.INT_RATE_SA + constants.INT_EXTRA) / 12)

    return sa_interest

def _calculate_monthly_interest_ma(ma_accumulated: float,
                                   rem_amount_for_extra_int_ma: float) -> float:
    """Calculates the interest to be added to the MA in a month period.

    Args:
        ma_accumulated (float): Current amount in MA
        rem_amount_for_extra_int_ma (float): Remaining amount in MA that is applicable for 1% extra interest
    """

    ma_interest = 0
    if ma_accumulated > rem_amount_for_extra_int_ma:
        ma_interest += rem_amount_for_extra_int_ma * ((constants.INT_RATE_MA + constants.INT_EXTRA) / 12)
        ma_interest += (ma_accumulated - rem_amount_for_extra_int_ma) * (constants.INT_RATE_MA / 12)
    else:
        ma_interest += ma_accumulated * ((constants.INT_RATE_MA + constants.INT_EXTRA) / 12)
    
    return ma_interest

def calculate_annual_change(salary: float,
                            bonus: float,
                            oa_curr: float,
                            sa_curr: float,
                            ma_curr: float,
                            account_deltas: dict=None,
                            bonus_month: int=12,
                            date_start: dt=None,
                            age: int=None,
                            dob: str=None) -> dict:
    """Calculates the total contributions and interest earned for the current year.

    Adds the interest, along with the contributions in the year, to the CPF account balances. \\
    Returns the projected amount in the CPF accounts at the end of the year.

    Age variable is updated every month.

    Args:
        salary (float): Annual salary of employee
        bonus (float): Bonus/commission received in the year
        oa_curr (float): Current amount in OA
        sa_curr (float): Current amount in SA
        ma_curr (float): Current amount in MA
        account_deltas (dict): List of keys: 
            [`oa_topups`, `oa_withdrawals`, `sa_topups`, `sa_withdrawals`, `ma_topups`, `ma_withdrawals`]
        bonus_month (int): Month where bonus is received (1-12)
        date_start (date): Start date of the year to calculate from
        age (int): Age of employee
        dob (str): Date of birth of employee in YYYYMM format

    Returns a tuple containing:
        - New amount in OA, after contributions and interest for this year
        - New amount in SA, after contributions and interest for this year
        - New amount in MA, after contributions and interest for this year
    """

    oa_accumulated, sa_accumulated, ma_accumulated = oa_curr, sa_curr, ma_curr
    oa_interest_total, sa_interest_total, ma_interest_total = (0, 0, 0)
    
    # iterate through the months in the year
    month_start = date_start.month if date_start is not None else 1
    for month in range(month_start, 13):
        if dob is not None:
            # wrap the date in a datetime object
            date_start_iter = dt.date(date_start.year, month, 1)
            age = genhelpers._get_age(dob, date_start_iter)
            # print('Month: {}/{}, Age: {}'.format(date_start_iter.year, i, age))
        # else:
        #     # else-condition only applies for unit testing of class TestCpfCalculateAnnualChange1
        #     bonus_annual = bonus if month == bonus_month else 0
        
        # check if this month is the month where bonus is disbursed
        bonus_annual = bonus if month == bonus_month else 0
        
        # add the CPF allocation for this month
        # this is actually the contribution for the previous month's salary
        allocations = main.calculate_cpf_allocation(salary, bonus_annual, None, age=age)
        oa_accumulated += float(allocations[strings.KEY_VALUES][strings.KEY_OA])
        sa_accumulated += float(allocations[strings.KEY_VALUES][strings.KEY_SA])
        ma_accumulated += float(allocations[strings.KEY_VALUES][strings.KEY_MA])

        if account_deltas is not None and len(account_deltas.keys()) != 0:
            # if there have been topups/withdrawals in the accounts this month
            (delta_oa, delta_sa, delta_ma) = genhelpers._get_account_deltas_month(account_deltas, month)
            oa_accumulated += delta_oa
            sa_accumulated += delta_sa
            ma_accumulated += delta_ma

        ###########################################################################################
        #                                   INTEREST CALCULATION                                  #
        # Interest is calculated at the end of each month based on the lowest balance amount in   #
        # the month.                                                                              # 
        # But, it is only credited at the end of the year.                                        # 
        #                                                                                         #
        # Extra 1% interest is earned on first $60k of combined balance, with up to $20k coming   #
        # from OA.                                                                                #
        # Extra 1% interest earned on OA is credited to SA, not OA.                               #
        # Order priority: 1. OA, 2. SA, 3. MA                                                     #
        ###########################################################################################

        # first priority is OA
        oa_interest = _calculate_monthly_interest_oa(oa_accumulated)
        oa_interest_total += oa_interest

        # remaining amount available for extra interest to be received in SA/MA has a minimum of $40k
        rem_amount_for_extra_int_sa_ma = constants.THRESHOLD_EXTRAINT_TOTAL - \
                                            min(oa_accumulated, constants.THRESHOLD_EXTRAINT_OA)
        # second priority is SA
        sa_interest = _calculate_monthly_interest_sa(oa_accumulated,
                                                     sa_accumulated, 
                                                     rem_amount_for_extra_int_sa_ma)
        sa_interest_total += sa_interest

        # remaining amount available for extra interest to be received in MA depends on the amount in SA 
        rem_amount_for_extra_int_ma = max(rem_amount_for_extra_int_sa_ma - sa_accumulated, 0)
        # last priority is MA
        ma_interest = _calculate_monthly_interest_ma(ma_accumulated, rem_amount_for_extra_int_ma)
        ma_interest_total += ma_interest

        # print(i, oa_interest, sa_interest, ma_interest)

    # interest added at the end of the year
    logger.debug(f'Interest in year: OA = {oa_interest_total}, SA = {sa_interest_total}, MA = {ma_interest_total}')
    oa_new = oa_accumulated + oa_interest_total
    sa_new = sa_accumulated + sa_interest_total
    ma_new = ma_accumulated + ma_interest_total

    return {
        strings.KEY_OA: str(round(oa_new, 2)),
        strings.KEY_SA: str(round(sa_new, 2)),
        strings.KEY_MA: str(round(ma_new, 2)),
        strings.KEY_OA_INTEREST: str(round(oa_interest_total, 2)),
        strings.KEY_SA_INTEREST: str(round(sa_interest_total, 2)),
        strings.KEY_MA_INTEREST: str(round(ma_interest_total, 2)),
    }
