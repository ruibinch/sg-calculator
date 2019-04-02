import logic.cpf_constants as constants
import math


def calculate_cpf_contribution(age, salary, bonus):
    """
    Calculates the CPF contribution for the year.
    Taking into account the Ordinary Wage (OW) Ceiling and Additional Wage (AW) Ceiling.
    Reference: https://www.cpf.gov.sg/Assets/employers/Documents/Table%201_Pte%20and%20Npen%20CPF%20contribution%20rates%20for%20Singapore%20Citizens%20and%203rd%20year%20SPR%20Jan%202016.pdf

    Steps for calculation:
    1. Compute total CPF contribution, rounded to the nearest dollar.
    2. Compute the employees' share (drop the cents).
    3. Employers' share = Total contribution - employees' share

    Args:
        - age (int): Age of employee
        - salary (float): Annual salary of employee
        - bonus (float): Bonus/commission received in the year

    Returns:
        - (float): Amount contributed by the employee in the year
        - (float): Amount contributed by the employer in the year
    """

    cont_total = get_contribution_amount(age, salary, bonus, entity=constants.STR_COMBINED)
    cont_employee = get_contribution_amount(age, salary, bonus, entity=constants.STR_EMPLOYEE)
    cont_employer = cont_total - cont_employee

    return cont_employee, cont_employer


def calculate_cpf_allocation(age, salary, bonus):
    """
    Calculates the CPF allocation for the month.
    Reference: https://www.cpf.gov.sg/Assets/employers/Documents/Table%2011_Pte%20and%20Npen_CPF%20Allocation%20Rates%20Jan%202016.pdf

    Steps for calculation:
    1. From the total contribution amount, derive the amount allocated into SA and MA using the 
       respective multiplier corresponding to the age.
    2. OA allocation = Total contribution - SA allocation - MA allocation
    
    Args:
        - age (int): Age of employee
        - salary (float): Annual salary of employee
        - bonus (float): Bonus/commission received in the year

    Returns:
        - (float): Allocation amount into OA
        - (float): Allocation amount into SA
        - (float): Allocation amount into MA
    """

    cont_monthly = get_contribution_amount(age, salary, bonus, entity=constants.STR_COMBINED) / 12
    sa_alloc = get_allocation_amount(age, cont_monthly, account=constants.STR_SA)
    ma_alloc = get_allocation_amount(age, cont_monthly, account=constants.STR_MA)
    oa_alloc = cont_monthly - sa_alloc - ma_alloc

    return oa_alloc, sa_alloc, ma_alloc


def calculate_cpf_projection(age, salary, yoy_increase, base_cpf, n_years):
    """
    Calculates the account balance in the CPF accounts after `n_years` based on the input parameters.

    Args:
        - age (int): Age of employee
        - salary (int): Salary of employee
        - yoy_increase (float): Projected year-on-year percentage increase in salary
        - base_cpf (list): Contains the current CPF account balance
        - n_years (int): Number of years into the future to predict

    Returns:
        - (float): OA balance after `n_years`
        - (float): SA balance after `n_years`
        - (float): MA balance after `n_years`
    """

    oa, sa, ma = base_cpf['oa'], base_cpf['sa'], base_cpf['ma']

    for i in range(n_years):
        salary_proj = salary * pow(1 + yoy_increase, i)
        oa, sa, ma = calculate_annual_change(age+i, salary_proj, oa, sa, ma)

    return oa, sa, ma


###################################################################################################
#                                       HELPER FUNCTIONS                                          #
###################################################################################################

def get_age_bracket(age, purpose):
    """
    Gets the age bracket for the specified purpose and age.

    Args:
        - age (int): Age of employee
        - purpose (str): Either 'contribution' or 'allocation'
    
    Returns:
        - (str): Age bracket of employee
    """
    if purpose == constants.STR_CONTRIBUTION:
        keys = constants.rates_cont.keys()
    elif purpose == constants.STR_ALLOCATION:
        keys = constants.rates_alloc.keys()

    for key in keys:
        if age <= int(key):
            return key
    
    return '150' # return max by default


def round_half_up(n, decimals=0):
    """
    Rounds the given monetary amount to the nearest dollar.
    An amount of 50 cents will be regarded as an additional dollar:

    Args:
        - n (float): input amount

    Returns:
        - (int): rounded amount to the nearest dollar
    """

    multiplier = 10 ** decimals
    return math.floor(n*multiplier + 0.5) / multiplier


def get_contribution_amount(age, salary, bonus, entity):
    """
    Gets the annual CPF contribution amount for the specified entity corresponding to the 
    correct age and income bracket.

    OW Ceiling: $6k a month, or $72k a year.
    AW Ceiling: $102k - OW amount subject to CPF.

    Args:
        - age (int): Age of employee
        - salary (float): Annual salary of employee
        - bonus (float): Bonus/commission received in the year
        - entity (str): Either 'combined' or 'employee'
    
    Returns:
        - (int): CPF contribution amount for the year
    """

    age_bracket = get_age_bracket(age, constants.STR_CONTRIBUTION)
    rates = constants.rates_cont
    amount_tw = salary + bonus # only needed if income is in income brackets 2 or 3

    if salary <= constants.INCOME_BRACKET_1:
        # salary is <=$50/month
        cont = 0
    elif salary <= constants.INCOME_BRACKET_2:
        # salary is >$50 to <=$500/month
        cont = rates[age_bracket][1][entity] * amount_tw
    elif salary <= constants.INCOME_BRACKET_3:
        # salary is >$500 to <=$749/month
        cont_from_tw = rates[age_bracket][2][entity] * amount_tw
        cont_misc = rates[age_bracket][2][constants.STR_MISC] * (amount_tw - 500)
        cont = cont_from_tw + cont_misc
    else:
        # salary is >=$750/month
        amount_ow_eligible_for_cpf = min(salary, constants.CEILING_OW_ANNUAL)
        cont_from_ow = rates[age_bracket][3][entity] * amount_ow_eligible_for_cpf

        ceiling_aw = constants.CEILING_AW - amount_ow_eligible_for_cpf
        amount_aw_eligible_for_cpf = min(bonus, ceiling_aw)
        cont_from_aw = rates[age_bracket][3][entity] * amount_aw_eligible_for_cpf

        cont_total = cont_from_ow + cont_from_aw
        if entity == constants.STR_COMBINED:
            cont = round_half_up(cont_total)
        elif entity == constants.STR_EMPLOYEE:
            cont = math.floor(cont_total)

    return cont


def get_allocation_amount(age, cont, account):
    """
    Gets the amount allocated into the specified CPF account in a month.

    Args:
        - age (int): Age of employee
        - cont (int): Total CPF contribution for the month
        - account (str): Either 'SA' or MA'

    Returns:
        - (float): Amount allocated into the specified `account`
    """

    age_bracket = get_age_bracket(age, constants.STR_ALLOCATION)
    return constants.rates_alloc[age_bracket][account + '_ratio'] * cont


def get_allocation(age, salary):
    """
    Gets the amount allocated into the individual CPF accounts.
    Note that only the first $6k is subject to CPF.

    Args:
        - age (int): Age of employee
        - salary (int): Salary of employee
    
    Returns:
        - (float): Allocation amount into OA
        - (float): Allocation amount into SA
        - (float): Allocation amount into MA
    """

    age_bracket = get_age_bracket(age, constants.STR_ALLOCATION)
    rates = constants.rates_alloc

    allocation_oa = rates[age_bracket]['OA'] * min(salary, constants.CEILING_OW)
    allocation_sa = rates[age_bracket]['SA'] * min(salary, constants.CEILING_OW)
    allocation_ma = rates[age_bracket]['MA'] * min(salary, constants.CEILING_OW)

    return allocation_oa, allocation_sa, allocation_ma


def calculate_monthly_interest_oa(oa_accumulated):
    """
    Calculates the interest to be added to the OA in a month period.

    Args:
        - oa_accumulated (float): Current amount in OA

    Returns:
        - (float): OA interest amount
    """

    oa_interest = 0
    if oa_accumulated > constants.THRESHOLD_EXTRAINT_OA:
        oa_interest += constants.THRESHOLD_EXTRAINT_OA * ((constants.INT_RATE_OA + constants.INT_EXTRA) / 12)
        oa_interest += (oa_accumulated - constants.THRESHOLD_EXTRAINT_OA) * (constants.INT_RATE_OA / 12)
    else:
        oa_interest += oa_accumulated * ((constants.INT_RATE_OA + constants.INT_EXTRA) / 12)
    
    return oa_interest


def calculate_monthly_interest_sa(sa_accumulated, rem_amount_for_extra_int_sa_ma):
    """
    Calculates the interest to be added to the SA in a month period.

    Args:
        - sa_accumulated (float): Current amount in SA

    Returns:
        - (float): SA interest amount
    """

    sa_interest = 0
    if sa_accumulated > rem_amount_for_extra_int_sa_ma:
        sa_interest += rem_amount_for_extra_int_sa_ma * ((constants.INT_RATE_SA + constants.INT_EXTRA) / 12)
        sa_interest += (sa_accumulated - rem_amount_for_extra_int_sa_ma) * (constants.INT_RATE_SA / 12)
    else:
        sa_interest += sa_accumulated * ((constants.INT_RATE_SA + constants.INT_EXTRA) / 12)

    return sa_interest


def calculate_monthly_interest_ma(ma_accumulated, rem_amount_for_extra_int_ma):
    """
    Calculates the interest to be added to the MA in a month period.

    Args:
        - ma_accumulated (float): Current amount in MA

    Returns:
        - (float): MA interest amount
    """

    ma_interest = 0
    if ma_accumulated > rem_amount_for_extra_int_ma:
        ma_interest += rem_amount_for_extra_int_ma * ((constants.INT_RATE_MA + constants.INT_EXTRA) / 12)
        ma_interest += (ma_accumulated - rem_amount_for_extra_int_ma) * (constants.INT_RATE_MA / 12)
    else:
        ma_interest += ma_accumulated * ((constants.INT_RATE_MA + constants.INT_EXTRA) / 12)
    
    return ma_interest


def calculate_annual_change(age, salary, oa_curr, sa_curr, ma_curr):
    """
    Calculates the interest earned for the current year.
    Adds the interest, along with the contributions in the year, to the CPF account balances.

    Args:
        - age (int): Age of employee
        - salary (int): Salary of employee
        - oa_curr (float): Current amount in OA
        - sa_curr (float): Current amount in SA
        - ma_curr (float): Current amount in MA

    Returns:
        - (float): New amount in OA, after contributions and interest for this year
        - (float): New amount in SA, after contributions and interest for this year
        - (float): New amount in MA, after contributions and interest for this year
    """

    oa_accumulated, sa_accumulated, ma_accumulated = oa_curr, sa_curr, ma_curr
    oa_interest_total, sa_interest_total, ma_interest_total = (0, 0, 0)

    # iterate through the 12 months in the year
    for i in range(12):
        allocation_oa, allocation_sa, allocation_ma = get_allocation(age, salary)

        # add the CPF allocation for this month
        oa_accumulated += allocation_oa
        sa_accumulated += allocation_sa
        ma_accumulated += allocation_ma

        # interest is calculated at the end of each month
        # calculate the interest gained in this month

        # first priority is OA
        oa_interest_total += calculate_monthly_interest_oa(oa_accumulated)
        
        # remaining amount available for extra interest to be received in SA/MA has a minimum of $40k
        rem_amount_for_extra_int_sa_ma = constants.THRESHOLD_EXTRAINT_TOTAL - min(oa_accumulated, constants.THRESHOLD_EXTRAINT_OA)
        # second priority is SA
        sa_interest = calculate_monthly_interest_sa(sa_accumulated, rem_amount_for_extra_int_sa_ma)
        sa_interest_total += sa_interest

        # remaining amount available for extra interest to be received in MA depends on the amount in SA 
        rem_amount_for_extra_int_ma = max(rem_amount_for_extra_int_sa_ma - sa_accumulated, 0)
        # last priority is MA
        ma_interest = calculate_monthly_interest_ma(ma_accumulated, rem_amount_for_extra_int_ma)
        ma_interest_total += ma_interest

    # interest added at the end of the year
    oa_new = oa_accumulated + oa_interest_total
    sa_new = sa_accumulated + sa_interest_total
    ma_new = ma_accumulated + ma_interest_total

    return oa_new, sa_new, ma_new