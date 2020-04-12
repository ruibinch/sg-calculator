import datetime as dt
import logging
import math

from . import constants, genhelpers, main
from utils import strings

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
        bonus (float): Bonus represented as a multiplier of monthly salary
        age (int): Age of employee
        entity (str): Either "combined" or "employee"
    
    Returns the CPF contribution amount for the month.
    """
    
    logger.info(f'_get_monthly_contribution_amount() - salary {round(salary, 2)}; bonus {round(bonus, 2)}')

    age_bracket = genhelpers._get_age_bracket(age, strings.CONTRIBUTION)
    rates = constants.rates_cont
    amount_tw = salary + (bonus * salary) # only needed if income is in income brackets 2 or 3

    if salary <= constants.INCOME_BRACKET_1:
        cont = 0
        logger.debug('Salary <=$50/month, total contribution is zero')
    elif salary <= constants.INCOME_BRACKET_2:
        cont = rates[age_bracket][1][entity] * amount_tw
        logger.debug(f'Salary >$50 to <=$500/month, contribution from TW is {round(cont, 2)}')
    elif salary <= constants.INCOME_BRACKET_3:
        cont_from_tw = rates[age_bracket][2][entity] * amount_tw
        cont_misc = rates[age_bracket][2][strings.MISC] * (amount_tw - 500)
        cont = cont_from_tw + cont_misc
        logger.debug(f'Salary >$500 to <=$749/month, contribution from OW is {round(cont, 2)}')
    else:
        amount_ow_eligible_for_cpf = min(salary, constants.CEILING_OW)
        cont_from_ow = rates[age_bracket][3][entity] * amount_ow_eligible_for_cpf
        logger.debug(f'Salary >=$750/month, contribution from OW is {round(cont_from_ow, 2)}')

        cont_from_aw = 0
        if bonus > 0:
            # need to consider AW
            ceiling_aw = constants.CEILING_AW - (amount_ow_eligible_for_cpf * 12)
            amount_aw_eligible_for_cpf = min(bonus * salary, ceiling_aw)
            cont_from_aw = rates[age_bracket][3][entity] * amount_aw_eligible_for_cpf
            logger.debug(f'Salary >=$750/month with bonus, contribution from AW is {round(cont_from_aw, 2)}')

        cont_total = cont_from_ow + cont_from_aw
        if entity == strings.COMBINED:
            cont = genhelpers._round_half_up(cont_total)
        elif entity == strings.EMPLOYEE:
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
    age_bracket = genhelpers._get_age_bracket(age, strings.CONTRIBUTION)
    rates = constants.rates_cont[age_bracket]

    # get income bracket
    if salary <= constants.INCOME_BRACKET_1:
        cont_rates = {
            strings.CONT_EMPLOYEE: {},
            strings.CONT_EMPLOYER: {}
        }
    elif salary <= constants.INCOME_BRACKET_2:
        cont_rates = {
            strings.CONT_EMPLOYEE: {},
            strings.CONT_EMPLOYER: {
                'TW': str(rates[1][strings.COMBINED])
            }
        }
    elif salary <= constants.INCOME_BRACKET_3:
        cont_rates = {
            strings.CONT_EMPLOYEE: {
                'TW - $500': str(rates[2][strings.MISC])
            },
            strings.CONT_EMPLOYER: {
                'TW': str(rates[2][strings.COMBINED])
            } 
        }
    else:
        cont_employer_rate = round(rates[3][strings.COMBINED] - rates[3][strings.EMPLOYEE], 2)
        cont_rates = {
            strings.CONT_EMPLOYEE: {
                'OW': str(rates[3][strings.EMPLOYEE]),
                'AW': str(rates[3][strings.EMPLOYEE])
            },
            strings.CONT_EMPLOYER: {
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

    age_bracket = genhelpers._get_age_bracket(age, strings.ALLOCATION)
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

    age_bracket = genhelpers._get_age_bracket(age, strings.ALLOCATION)
    rates = constants.rates_alloc[age_bracket]

    alloc_rates = {
        'pct_of_salary': {
            strings.OA: str(rates[strings.OA]),
            strings.SA: str(rates[strings.SA]),
            strings.MA: str(rates[strings.MA])
        },
        'ratio': {
            strings.OA: str(rates[f'{strings.OA}_ratio']),
            strings.SA: str(rates[f'{strings.SA}_ratio']),
            strings.MA: str(rates[f'{strings.MA}_ratio'])
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
                            dob: str=None) -> dict:
    """Calculates the total contributions and interest earned for the current year.

    Adds the interest, along with the contributions in the year, to the CPF account balances. \\
    Returns the projected amount in the CPF accounts at the end of the year.

    Age variable is updated every month.

    Args:
        salary (float): Annual salary of employee
        bonus (float): Bonus represented as a multiplier of monthly salary
        oa_curr (float): Current amount in OA
        sa_curr (float): Current amount in SA
        ma_curr (float): Current amount in MA
        account_deltas (dict): List of keys: 
            [`oa_topups`, `oa_withdrawals`, `sa_topups`, `sa_withdrawals`, `ma_topups`, `ma_withdrawals`]
        bonus_month (int): Month where bonus is received (1-12)
        date_start (date): Start date of the year to calculate from
        dob (str): Date of birth of employee in YYYYMM format

    Returns a dict:
        - `oa`: OA balance at the end of the year
        - `sa`: SA balance at the end of the year
        - `ma`: MA balance at the end of the year
        - `oa_interest`: Interest earned in OA in the year
        - `sa_interest`: Interest earned in SA in the year
        - `ma_interest`: Interest earned in MA in the year
    """

    oa_accumulated, sa_accumulated, ma_accumulated = oa_curr, sa_curr, ma_curr
    oa_interest_total, sa_interest_total, ma_interest_total = 0, 0, 0
    # these will be updated in the for-loop iteration through the months in the year
    age, age_bracket = -1, -1
    # memoisation is required here as the person's age might change throughout the year
    # then, the allocation amount might change if the age crosses into the next bracket
    # hence memoisation prevents the allocation amount from being repeatedly calculated
    allocations_memoised = {}

    # iterate through the months in the year
    month_start = date_start.month if date_start is not None else 1
    logger.info(f'calculate_annual_change - from "{month_start}/{date_start.year}" to "12/{date_start.year}"')
    for month in range(month_start, 13):
        if dob is not None:
            # wrap the date in a datetime object
            date_start_iter = dt.date(date_start.year, month, 1)
            age = genhelpers._get_age(dob, date_start_iter)
            age_bracket = genhelpers._get_age_bracket(age, strings.ALLOCATION)

            # if age bracket has changed, then get the new allocation amounts
            if age_bracket not in allocations_memoised:
                logger.debug(f'Individual\'s age bracket is set at "{age_bracket}"')
                allocations_memoised[age_bracket] = {
                    strings.WITH_BONUS: main.calculate_cpf_allocation(salary, bonus, None, age=age),
                    strings.WITHOUT_BONUS: main.calculate_cpf_allocation(salary, 0, None, age=age),
                }
                
        # add the CPF allocation for this month
        # this is actually the contribution for the previous month's salary
        if month == bonus_month:
            oa_accumulated += float(allocations_memoised[age_bracket][strings.WITH_BONUS][strings.VALUES][strings.OA]) / 12
            sa_accumulated += float(allocations_memoised[age_bracket][strings.WITH_BONUS][strings.VALUES][strings.SA]) / 12
            ma_accumulated += float(allocations_memoised[age_bracket][strings.WITH_BONUS][strings.VALUES][strings.MA]) / 12
        else:
            oa_accumulated += float(allocations_memoised[age_bracket][strings.WITHOUT_BONUS][strings.VALUES][strings.OA]) / 12
            sa_accumulated += float(allocations_memoised[age_bracket][strings.WITHOUT_BONUS][strings.VALUES][strings.SA]) / 12
            ma_accumulated += float(allocations_memoised[age_bracket][strings.WITHOUT_BONUS][strings.VALUES][strings.MA]) / 12

        # amend the accumulated values if there are any topups/withdrawals in this month
        if any([month in account_deltas[key_month] for key_month in account_deltas]):
            oa_delta, sa_delta, ma_delta = genhelpers._get_account_deltas_month(account_deltas, month)
            logger.debug(f'Month = {month}; OA delta = {round(oa_delta, 2)}, SA delta = {round(sa_delta, 2)}, MA delta = {round(ma_delta, 2)}')
            
            oa_accumulated += oa_delta
            sa_accumulated += sa_delta
            ma_accumulated += ma_delta

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

        if month == bonus_month:
            logger.debug(f'Month = {month} (bonus); OA = {round(oa_accumulated, 2)}, SA = {round(sa_accumulated, 2)}, MA = {round(ma_accumulated, 2)}')
            logger.debug(f'Month = {month} (bonus); OA int = {round(oa_interest, 2)}, SA int = {round(sa_interest, 2)}, MA int = {round(ma_interest, 2)}')
        else:
            logger.debug(f'Month = {month}; OA = {round(oa_accumulated, 2)}, SA = {round(sa_accumulated, 2)}, MA = {round(ma_accumulated, 2)}')
            logger.debug(f'Month = {month}; OA int = {round(oa_interest, 2)}, SA int = {round(sa_interest, 2)}, MA int = {round(ma_interest, 2)}')

    # interest added at the end of the year
    logger.debug(f'Interest in year: OA = {round(oa_interest_total, 2)}, SA = {round(sa_interest_total, 2)}, MA = {round(ma_interest_total, 2)}')
    oa_new = oa_accumulated + oa_interest_total
    sa_new = sa_accumulated + sa_interest_total
    ma_new = ma_accumulated + ma_interest_total

    return {
        strings.AGE: age,
        strings.PARAM_SALARY: str(round(salary, 2)),
        strings.PARAM_BONUS: str(round(salary / 12 * bonus, 2)),
        # strings.DELTAS: {k:v for k,v in account_deltas.items() if v},
        strings.OA: str(round(oa_new, 2)),
        strings.SA: str(round(sa_new, 2)),
        strings.MA: str(round(ma_new, 2)),
        strings.OA_INTEREST: str(round(oa_interest_total, 2)),
        strings.SA_INTEREST: str(round(sa_interest_total, 2)),
        strings.MA_INTEREST: str(round(ma_interest_total, 2)),
    }
