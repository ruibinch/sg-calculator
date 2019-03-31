import logic.cpf_constants as constants

def calculate_future_cpf_balance(age, salary, yoy_increase, base_cpf, n_years):
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

def get_age_bracket(age):
    """
    Gets the age bracket based on the input age.

    Args:
        - age (int): Age of employee
    
    Returns:
        - (str): Age bracket of employee
    """

    for key in constants.rates.keys():
        if age < int(key):
            return key


def get_contribution(age, salary):
    """
    Gets the employee's and employer's CPF contribution amounts.
    Note that only the first $6k is subject to CPF.

    Args:
        - age (int): Age of employee
        - salary (int): Salary of employee
    
    Returns:
        - (float): Employee's contribution percentage
        - (float): Employer's contribution percentage
    """
    age_bracket = get_age_bracket(age)
    employee_cont = constants.rates[age_bracket]['employee'] * min(salary, constants.THRESHOLD_CPF)
    employer_cont = constants.rates[age_bracket]['employer'] * min(salary, constants.THRESHOLD_CPF)

    return employee_cont, employer_cont


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

    age_bracket = get_age_bracket(age)
    allocation_oa = constants.rates[age_bracket]['OA'] * min(salary, constants.THRESHOLD_CPF)
    allocation_sa = constants.rates[age_bracket]['SA'] * min(salary, constants.THRESHOLD_CPF)
    allocation_ma = constants.rates[age_bracket]['MA'] * min(salary, constants.THRESHOLD_CPF)

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