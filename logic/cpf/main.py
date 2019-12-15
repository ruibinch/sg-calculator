import datetime as dt
import logging

from logic.cpf import constants
from logic.cpf import cpfhelpers
from logic.cpf import genhelpers
from utils import strings

logger = logging.getLogger(__name__)

"""
Main file serving as the entry point to the CPF module.
"""

def calculate_cpf_contribution(salary, bonus, dob, period, age=None):
    """Calculates the CPF contribution for the year/month.
    
    Takes into account the Ordinary Wage (OW) Ceiling and Additional Wage (AW) Ceiling.

    Reference: <https://www.cpf.gov.sg/Assets/employers/Documents/Table%201_Pte%20and%20Npen%20CPF%20contribution%20rates%20for%20Singapore%20Citizens%20and%203rd%20year%20SPR%20Jan%202016.pdf>

    Steps for calculation:
    1. Compute total CPF contribution, rounded to the nearest dollar.
    2. Compute the employees' share (drop the cents).
    3. Employers' share = Total contribution - employees' share.

    Args:
        salary (str): Annual salary of employee
        bonus (str): Bonus/commission received in the year; assume to be credited in December
        dob (str): Date of birth of employee in YYYYMM format
        period (str): Time period of contribution; either "year" or "month"
        age (int): Age of employee (*only used for testing purposes*)

    Returns a dict:
        - `cont_employee`: Amount contributed by the employee in the year
        - `cont_employer`: Amount contributed by the employer in the year
    """
    
    logger.debug('/cpf/contribution')
    if age is None:
        age = genhelpers._get_age(dob)

    cont_rates = cpfhelpers._get_contribution_rates(salary / 12, age)
    cont_total, cont_employee = (0, 0)

    if period == strings.STR_MONTH:
        cont_total += cpfhelpers._get_monthly_contribution_amount(salary / 12, bonus, age, entity=constants.STR_COMBINED)
        cont_employee += cpfhelpers._get_monthly_contribution_amount(salary / 12, bonus, age, entity=constants.STR_EMPLOYEE)
    elif period == strings.STR_YEAR:
        for i in range(1, 13):
            # default `bonus_in_month` to only be applicable in Dec
            bonus_in_month = bonus if i == 12 else 0

            cont_total += cpfhelpers._get_monthly_contribution_amount(salary / 12, bonus_in_month, age, entity=constants.STR_COMBINED)
            cont_employee += cpfhelpers._get_monthly_contribution_amount(salary / 12, bonus_in_month, age, entity=constants.STR_EMPLOYEE)

    return {
        strings.KEY_VALUES: {
            strings.KEY_CONT_EMPLOYEE: str(round(cont_employee, 2)), 
            strings.KEY_CONT_EMPLOYER: str(round(cont_total - cont_employee, 2))
        },
        strings.KEY_RATES: cont_rates
    }

def calculate_cpf_allocation(salary, bonus, dob, age=None):
    """Calculates the monthly allocation into the 3 CPF accounts.

    Reference <https://www.cpf.gov.sg/Assets/employers/Documents/Table%2011_Pte%20and%20Npen_CPF%20Allocation%20Rates%20Jan%202016.pdf/>`

    Steps for calculation:
    1. From the total contribution amount, derive the amount allocated into SA and MA using the respective multiplier corresponding to the age.
    2. OA allocation = Total contribution - SA allocation - MA allocation.
    
    Args:
        salary (str): Annual salary of employee
        bonus (str): Bonus/commission received in the year; only applicable in the month when bonus is disbursed
        dob (str): Date of birth of employee in YYYYMM format
        age (int): Age of employee (*only used for testing purposes*)

    Returns a dict:
        - `oa_alloc`: Allocation amount into OA
        - `sa_alloc`: Allocation amount into SA
        - `ma_alloc`: Allocation amount into MA
    """
    
    logger.debug('/cpf/allocation')
    if age is None:
        age = genhelpers._get_age(dob)

    # get contribution amount for the month first
    cont_monthly = cpfhelpers._get_monthly_contribution_amount(salary / 12, bonus, age, entity=constants.STR_COMBINED)
    logger.debug(f'Total CPF monthly contribution is {cont_monthly}')

    # then, get the individual amounts allocated to each account
    sa_alloc = cpfhelpers._get_allocation_amount(age, cont_monthly, account=constants.STR_SA)
    ma_alloc = cpfhelpers._get_allocation_amount(age, cont_monthly, account=constants.STR_MA)
    oa_alloc = cont_monthly - sa_alloc - ma_alloc
    logger.debug(f'Allocation amounts: OA = {oa_alloc}, MA = {ma_alloc}, SA = {sa_alloc}')

    # get the allocation rates
    alloc_rates = cpfhelpers._get_allocation_rates(age)

    return {
        strings.KEY_VALUES: {
            strings.KEY_OA: str(round(oa_alloc, 2)), 
            strings.KEY_SA: str(sa_alloc),
            strings.KEY_MA: str(ma_alloc)
        },
        strings.KEY_RATES: alloc_rates
    }

def calculate_cpf_projection(salary, bonus, yoy_increase_salary, yoy_increase_bonus,
                             dob, base_cpf, bonus_month, n_years, target_year, 
                             oa_topups, oa_withdrawals, sa_topups, 
                             sa_withdrawals, ma_topups, ma_withdrawals,
                             age=None, proj_start_date=None): 
    """Calculates the projected account balance in the CPF accounts after `n_years` or in `target_year`.

    Reference <https://www.cpf.gov.sg/Assets/common/Documents/InterestRate.pdf/>

    Args:
        salary (str): Annual salary of employee
        bonus (str): Bonus/commission received in the year
        yoy_increase_salary (str): Projected year-on-year percentage increase in salary
        yoy_increase_bonus (str): Projected year-on-year percentage increase in bonus
        dob (str): Date of birth of employee in YYYYMM format
        base_cpf (dict): Contains the current balance in the CPF accounts
            - `oa`: current amount in OA
            - `sa`: current amount in SA
            - `ma`: current amount in MA
        bonus_month (str): Month where bonus is received (1-12)
        n_years (str): Number of years into the future to project
        target_year (str): Target end year of projection
        oa_topups (dict): Cash top-ups to the OA
            - `{date}`: date of cash topup in YYYYMM format
                - `amount`: Topup amount to OA
        oa_withdrawals (dict): Withdrawals from the OA
            - `{date}`: date of cash withdrawal in YYYYMM format
                - `amount`: Withdrawal amount from OA
        sa_topups (dict): Cash top-ups to the SA
            - `{date}`: date of cash topup in YYYYMM format
                - `amount`: Topup amount to SA
                - `is_sa_topup_from_oa`: Whether the SA topup funds are coming from the OA
        sa_withdrawals (dict): Withdrawals from the SA
            - `{date}`: date of cash withdrawal in YYYYMM format
                - `amount`: Withdrawal amount from SA
        ma_topups (dict): Cash top-ups to the MA
            - `{date}`: date of cash topup in YYYYMM format
                - `amount`: Topup amount to MA
        ma_withdrawals (dict): Withdrawals from the MA
            - `{date}`: date of cash withdrawal in YYYYMM format
                - `amount`: Withdrawal amount from MA
        age (int): Age of employee (*only used for testing purposes*)
        proj_start_date (date): Starting date of projection (*only used for testing purposes*)

    Returns a dict:
        - `oa`: OA balance after number of projected years
        - `sa`: SA balance after number of projected years
        - `ma`: MA balance after number of projected years
    """
    
    logger.debug('/cpf/projection')
    values = {}
    if age is None:
        age = genhelpers._get_age(dob)
    
    # getting base amounts in OA, SA, MA and number of years to project for
    oa, sa, ma = float(base_cpf['oa']), float(base_cpf['sa']), float(base_cpf['ma'])
    n_years = genhelpers._get_num_projection_years(target_year) if n_years is None else n_years

    # convert topup/withdrawal dicts to zero-indexed years as keys
    oa_topups = genhelpers._convert_year_to_zero_indexing(oa_topups)
    oa_withdrawals = genhelpers._convert_year_to_zero_indexing(oa_withdrawals)
    sa_topups = genhelpers._convert_year_to_zero_indexing(sa_topups)
    sa_withdrawals = genhelpers._convert_year_to_zero_indexing(sa_withdrawals)
    ma_topups = genhelpers._convert_year_to_zero_indexing(ma_topups)
    ma_withdrawals = genhelpers._convert_year_to_zero_indexing(ma_withdrawals)

    for i in range(n_years):
        if i == 0:
            # it is the first year, so the starting month would be different
            # default day to 1 as it is not used
            if proj_start_date is not None:
                date_start = dt.date(proj_start_date.year, proj_start_date.month, 1)
            else:
                date_start = dt.date(dt.date.today().year, dt.date.today().month, 1)
        else:
            # for the subsequent years, start the count from January
            date_start = dt.date(dt.date.today().year + i, 1, 1)

        salary_proj = salary * pow(1 + yoy_increase_salary, i)
        bonus_proj = bonus * pow(1 + yoy_increase_bonus, i)

        # get OA/SA/MA topup/withdrawal details in this year
        # package all into an `account_deltas` dict
        account_deltas = {
            strings.KEY_OA_TOPUPS: genhelpers._get_account_deltas_year(oa_topups, i),
            strings.KEY_OA_WITHDRAWALS: genhelpers._get_account_deltas_year(oa_withdrawals, i),
            strings.KEY_SA_TOPUPS: genhelpers._get_account_deltas_year(sa_topups, i),
            strings.KEY_SA_WITHDRAWALS: genhelpers._get_account_deltas_year(sa_withdrawals, i),
            strings.KEY_MA_TOPUPS: genhelpers._get_account_deltas_year(ma_topups, i),
            strings.KEY_MA_WITHDRAWALS: genhelpers._get_account_deltas_year(ma_withdrawals, i)
        }

        # get SA topup/OA withdrawal details
        # oa_withdrawal = oa_withdrawals.get(i, 0)
        # sa_topup_details = sa_topups.get(i, [])
        # sa_topup = sa_topup_details[0] if sa_topup_details != [] else 0
        # sa_topup_from_oa = sa_topup_details[1] if sa_topup_details != [] else None

        results_annual = cpfhelpers.calculate_annual_change(salary_proj, bonus_proj, oa, sa, ma,
                                                            account_deltas, bonus_month, 
                                                            date_start=date_start, age=age)

        # set key to `final` if it is the last year
        key = 'final' if i == (n_years - 1) else str(i+1)
        values[key] = results_annual

    return {
        strings.KEY_VALUES: values
    }