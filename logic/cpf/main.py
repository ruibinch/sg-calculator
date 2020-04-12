import datetime as dt
import logging

from . import constants, cpfhelpers, genhelpers
from utils import strings

logger = logging.getLogger(__name__)

"""
Main file serving as the entry point to the CPF module.
"""

def calculate_cpf_contribution(salary: float,
                               bonus: float,
                               dob: str,
                               period: str,
                               age: int=None) -> dict:
    """Calculates the CPF contribution for the year/month.
    
    Takes into account the Ordinary Wage (OW) Ceiling and Additional Wage (AW) Ceiling.

    Reference: <https://www.cpf.gov.sg/Assets/employers/Documents/Table%201_Pte%20and%20Npen%20CPF%20contribution%20rates%20for%20Singapore%20Citizens%20and%203rd%20year%20SPR%20Jan%202016.pdf>

    Steps for calculation:
    1. Compute total CPF contribution, rounded to the nearest dollar.
    2. Compute the employees' share (drop the cents).
    3. Employers' share = Total contribution - employees' share.

    Args:
        salary (float): Annual salary of employee
        bonus (float): Bonus represented as a multiplier of monthly salary
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

    if period == strings.MONTH:
        cont_total += cpfhelpers._get_monthly_contribution_amount(salary / 12,
                                                                  bonus,
                                                                  age,
                                                                  entity=strings.COMBINED)
        cont_employee += cpfhelpers._get_monthly_contribution_amount(salary / 12,
                                                                     bonus,
                                                                     age,
                                                                     entity=strings.EMPLOYEE)
    elif period == strings.YEAR:
        for i in range(1, 13):
            # default `bonus_in_month` to only be applicable in Dec
            bonus_in_month = bonus if i == 12 else 0

            cont_total += cpfhelpers._get_monthly_contribution_amount(salary / 12,
                                                                      bonus_in_month,
                                                                      age,
                                                                      entity=strings.COMBINED)
            cont_employee += cpfhelpers._get_monthly_contribution_amount(salary / 12,
                                                                         bonus_in_month,
                                                                         age,
                                                                         entity=strings.EMPLOYEE)

    return {
        strings.VALUES: {
            strings.CONT_EMPLOYEE: str(round(cont_employee, 2)), 
            strings.CONT_EMPLOYER: str(round(cont_total - cont_employee, 2)),
        },
        strings.RATES: cont_rates,
    }

def calculate_cpf_allocation(salary: float,
                             bonus: float,
                             dob: str,
                             age: int=None) -> dict:
    """Calculates the annual allocation into the 3 CPF accounts.

    Reference <https://www.cpf.gov.sg/Assets/employers/Documents/Table%2011_Pte%20and%20Npen_CPF%20Allocation%20Rates%20Jan%202016.pdf/>`

    Steps for calculation:
    1. From the total contribution amount, derive the amount allocated into SA and MA using the respective multiplier corresponding to the age.
    2. OA allocation = Total contribution - SA allocation - MA allocation.
    
    Args:
        salary (float): Annual salary of employee
        bonus (float): Bonus represented as a multiplier of monthly salary
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
    cont_monthly = cpfhelpers._get_monthly_contribution_amount(salary / 12,
                                                               bonus,
                                                               age,
                                                               entity=strings.COMBINED)
    logger.info(f'Total CPF monthly contribution is {cont_monthly}')

    # then, get the individual amounts allocated to each account
    sa_alloc = cpfhelpers._get_allocation_amount(age,
                                                 cont_monthly,
                                                 account=strings.SA)
    ma_alloc = cpfhelpers._get_allocation_amount(age,
                                                 cont_monthly,
                                                 account=strings.MA)
    oa_alloc = cont_monthly - sa_alloc - ma_alloc
    logger.debug(f'Allocation amounts: OA = {round(oa_alloc, 2)}, SA = {sa_alloc}, MA = {ma_alloc}')

    # get the allocation rates
    alloc_rates = cpfhelpers._get_allocation_rates(age)

    return {
        strings.VALUES: {
            strings.OA: str(round(oa_alloc * 12, 2)),
            strings.SA: str(round(sa_alloc * 12, 2)),
            strings.MA: str(round(ma_alloc * 12, 2)),
        },
        strings.RATES: alloc_rates,
    }

def calculate_cpf_projection(salary: float,
                             bonus: float,
                             yoy_increase_salary: float,
                             dob: str,
                             base_cpf: dict,
                             bonus_month: int,
                             n_years: int,
                             target_year: int,
                             account_deltas: list,
                             age: int=None,
                             proj_start_date: dt=None) -> dict: 
    """Calculates the projected account balance in the CPF accounts after `n_years` or in `target_year`.

    Reference <https://www.cpf.gov.sg/Assets/common/Documents/InterestRate.pdf/>

    Args:
        salary (float): Annual salary of employee
        bonus (float): Bonus represented as a multiplier of monthly salary
        yoy_increase_salary (float): Projected year-on-year percentage increase in salary
        dob (str): Date of birth of employee in YYYYMM format
        base_cpf (dict): Contains the current balance in the CPF accounts
            - `oa`: current amount in OA
            - `sa`: current amount in SA
            - `ma`: current amount in MA
        bonus_month (int): Month where bonus is received (1-12)
        n_years (int): Number of years into the future to project
        target_year (int): Target end year of projection
        account_deltas (list): List of topups/withdrawals to be made to the accounts
        age (int): Age of employee (*only used for testing purposes*)
        proj_start_date (date): Starting date of projection (*only used for testing purposes*)

    Returns a dict:
        - `values`: a dict containing keys (1, 2, ..., "final") corresponding 
                    to n projected years, where each child object contains the
                    OA, SA, MA balances at the end of that year as well as the
                    interest accumulated in OA, SA, MA in that year  
    """
    
    logger.debug('/cpf/projection')
    values = {}
    
    # getting base amounts in OA, SA, MA and number of years to project for
    oa, sa, ma = float(base_cpf[strings.OA]), float(base_cpf[strings.SA]), float(base_cpf[strings.MA])
    n_years = genhelpers._get_num_projection_years(target_year) if n_years is None else n_years

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

        # calculated projected salary for this year
        salary_proj = salary * pow(1 + yoy_increase_salary, i)

        # get the account deltas applicable in this year
        account_deltas_year = [e for e in account_deltas if int(e[strings.PERIOD][:4]) == date_start.year]

        logger.debug(f'Year {i + 1} projection')
        results_annual = cpfhelpers.calculate_annual_change(salary_proj,
                                                            bonus,
                                                            oa,
                                                            sa,
                                                            ma,
                                                            account_deltas_year,
                                                            bonus_month, 
                                                            date_start=date_start,
                                                            dob=dob)

        # update with the new CPF account balances
        oa = float(results_annual[strings.OA])
        sa = float(results_annual[strings.SA])
        ma = float(results_annual[strings.MA])

        # set key to "final" if it is the last year
        key = strings.FINAL if i == (n_years - 1) else str(i + 1)
        values[key] = results_annual

    return {
        strings.VALUES: values,
    }
