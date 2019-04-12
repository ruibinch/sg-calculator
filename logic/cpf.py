from logic import cpf_constants as constants
import math
import datetime as dt


def calculate_cpf_contribution(salary, bonus, age=None, dob=None):
    # TODO: further enhancement to specify bonus month
    """Calculates the CPF contribution for the year.
    
    Takes into account the Ordinary Wage (OW) Ceiling and Additional Wage (AW) Ceiling.

    `Reference <https://www.cpf.gov.sg/Assets/employers/Documents/Table%201_Pte%20and%20Npen%20CPF%20contribution%20rates%20for%20Singapore%20Citizens%20and%203rd%20year%20SPR%20Jan%202016.pdf/>`_

    Steps for calculation:

    1. Compute total CPF contribution, rounded to the nearest dollar.
    2. Compute the employees' share (drop the cents).
    3. Employers' share = Total contribution - employees' share.

    Args:
        salary (float): Annual salary of employee
        bonus (float): Bonus/commission received in the year; assume to be credited in December
        age (int): Age of employee
        dob (str): Date of birth of employee in YYYYMM format

    Returns:
        *tuple*: Tuple containing
            - (float): Amount contributed by the employee in the year
            - (float): Amount contributed by the employer in the year

    """
    
    cont_total, cont_employee = (0, 0)

    for i in range(1, 13):
        # bonus is only calculated in the month of December
        bonus_annual = bonus if i == 12 else 0

        cont_total += _get_monthly_contribution_amount(salary / 12, bonus_annual, age, dob, entity=constants.STR_COMBINED)
        cont_employee += _get_monthly_contribution_amount(salary / 12, bonus_annual, age, dob, entity=constants.STR_EMPLOYEE)

    return cont_employee, cont_total - cont_employee


def calculate_cpf_allocation(salary_month, bonus, age=None, dob=None):
    """Calculates the CPF allocation for the month.

    `Reference <https://www.cpf.gov.sg/Assets/employers/Documents/Table%2011_Pte%20and%20Npen_CPF%20Allocation%20Rates%20Jan%202016.pdf/>`_

    Steps for calculation:

    1. From the total contribution amount, derive the amount allocated into SA and MA using the respective multiplier corresponding to the age.
    2. OA allocation = Total contribution - SA allocation - MA allocation.
    
    Args:
        salary (float): Monthly salary of employee
        bonus (float): Bonus/commission received in the year; only applicable in the month when bonus is disbursed
        age (int): Age of employee
        dob (str): Date of birth of employee in YYYYMM format

    Returns:
        *tuple*: Tuple containing
            - (float): Allocation amount into OA
            - (float): Allocation amount into SA
            - (float): Allocation amount into MA
    """

    cont_monthly = _get_monthly_contribution_amount(salary_month, bonus, age, dob, entity=constants.STR_COMBINED)
    sa_alloc = _get_allocation_amount(age, dob, cont_monthly, account=constants.STR_SA)
    ma_alloc = _get_allocation_amount(age, dob, cont_monthly, account=constants.STR_MA)
    oa_alloc = cont_monthly - sa_alloc - ma_alloc

    return round(oa_alloc, 2), sa_alloc, ma_alloc


def calculate_cpf_projection(salary, bonus, yoy_increase_salary, yoy_increase_bonus,
                            base_cpf, n_years, age=None, dob=None):
    """Calculates the projected account balance in the CPF accounts after `n_years`.

    `Reference <https://www.cpf.gov.sg/Assets/common/Documents/InterestRate.pdf/>`_

    Args:
        salary (float): Annual salary of employee
        bonus (float): Bonus/commission received in the year
        yoy_increase_salary (float): Projected year-on-year percentage increase in salary
        yoy_increase_bonus (float): Projected year-on-year percentage increase in bonus
        base_cpf (list of floats): Contains the current balance in the CPF accounts 
        n_years (int): Number of years into the future to predict
        age (int): Age of employee
        dob (str): Date of birth of employee in YYYYMM format

    Returns:
        *tuple*: Tuple containing
            - (float): OA balance after `n_years`
            - (float): SA balance after `n_years`
            - (float): MA balance after `n_years`
    """

    oa, sa, ma = base_cpf['oa'], base_cpf['sa'], base_cpf['ma']

    for i in range(n_years):
        # default day to 1 as it is not used
        date_start = dt.date(dt.date.today().year + i, dt.date.today().month, 1)

        salary_proj = salary * pow(1 + yoy_increase_salary, i)
        bonus_proj = bonus * pow(1 + yoy_increase_bonus, i)
        oa, sa, ma = _calculate_annual_change(salary_proj, bonus_proj, oa, sa, ma, 
                                              date_start=date_start, dob=dob)

    return oa, sa, ma


###################################################################################################
#                                       HELPER FUNCTIONS                                          #
###################################################################################################

def _get_age(dob, date_curr=None):
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
    
    Returns:
        int: Age of employee
    """

    birth_year, birth_month = (int(dob[0:4]), int(dob[4:6]))
    if date_curr is not None:
        curr_year, curr_month = (date_curr.year, date_curr.month)
    else:
        curr_year, curr_month = (dt.date.today().year, dt.date.today().month)

    year_diff, month_diff = (curr_year - birth_year, curr_month - birth_month)
    age = year_diff if month_diff <= 0 else year_diff + 1
    # print('CPF:_get_age():', year_diff, month_diff, age)
    return age


def _get_age_bracket(age, purpose):
    """ Gets the age bracket for the specified purpose and age.

    Args:
        age (int): Age of employee
        purpose (str): Either 'contribution' or 'allocation'
    
    Returns:
        str: Age bracket of employee
    """
    if purpose == constants.STR_CONTRIBUTION:
        keys = constants.rates_cont.keys()
    elif purpose == constants.STR_ALLOCATION:
        keys = constants.rates_alloc.keys()

    for key in keys:
        if age <= int(key):
            return key
    
    return '150' # return max by default


def _round_half_up(n, decimals=0):
    """Rounds the given monetary amount to the nearest dollar.
    
    An amount of 50 cents will be regarded as an additional dollar:

    Args:
        n (float): input amount

    Returns:
        int: rounded amount to the nearest dollar
    """

    multiplier = 10 ** decimals
    return math.floor(n*multiplier + 0.5) / multiplier


def _truncate(n, decimals=2):
    """Truncates the given monetary amount to the specified number of decimal places.

    Args:
        n (float): input amount

    Returns:
        float: truncated amount to `decimals` decimal places
    """
    before_dec, after_dec = str(n).split('.')
    return float('.'.join((before_dec, after_dec[0:2])))


def _get_monthly_contribution_amount(salary, bonus, age, dob, entity):
    """Gets the monthly CPF contribution amount for the specified entity corresponding to the 
    correct age and income bracket.

    OW Ceiling: $6k a month. \\
    AW Ceiling: $102k - OW amount subject to CPF in the year.

    Args:
        salary (float): Monthly salary of employee
        bonus (float): Bonus/commission received in the year; assume to be credited in December
        age (int): Age of employee
        dob (str): Date of birth of employee in YYYYMM format
        entity (str): Either 'combined' or 'employee'
    
    Returns:
        int: CPF contribution amount for the month
    """

    if age is None:
        age = _get_age(dob)

    age_bracket = _get_age_bracket(age, constants.STR_CONTRIBUTION)
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
        amount_ow_eligible_for_cpf = min(salary, constants.CEILING_OW)
        cont_from_ow = rates[age_bracket][3][entity] * amount_ow_eligible_for_cpf

        cont_from_aw = 0
        if bonus > 0:
            # need to consider AW
            ceiling_aw = constants.CEILING_AW - (amount_ow_eligible_for_cpf * 12)
            amount_aw_eligible_for_cpf = min(bonus, ceiling_aw)
            cont_from_aw = rates[age_bracket][3][entity] * amount_aw_eligible_for_cpf

        cont_total = cont_from_ow + cont_from_aw
        if entity == constants.STR_COMBINED:
            cont = _round_half_up(cont_total)
        elif entity == constants.STR_EMPLOYEE:
            cont = math.floor(cont_total)

    return cont


def _get_allocation_amount(age, dob, cont, account):
    """Gets the amount allocated into the specified CPF account in a month.
    
    Returned amount is truncated to 2 decimal places.

    Args:
        age (int): Age of employee
        dob (str): Date of birth of employee in YYYYMM format
        cont (int): Total CPF contribution for the month
        account (str): Either 'SA' or MA'

    Returns:
        float: Amount allocated into the specified `account`
    """

    if age is None:
        age = _get_age(dob)

    age_bracket = _get_age_bracket(age, constants.STR_ALLOCATION)
    return _truncate(constants.rates_alloc[age_bracket][account + '_ratio'] * cont)


def _calculate_monthly_interest_oa(oa_accumulated):
    """Calculates the interest to be added to the OA in a month period.

    Args:
        oa_accumulated (float): Current amount in OA

    Returns:
        float: OA interest amount
    """

    oa_interest = oa_accumulated * (constants.INT_RATE_OA / 12)

    # if oa_accumulated > constants.THRESHOLD_EXTRAINT_OA:
    #     oa_interest += constants.THRESHOLD_EXTRAINT_OA * ((constants.INT_RATE_OA + constants.INT_EXTRA) / 12)
    #     oa_interest += (oa_accumulated - constants.THRESHOLD_EXTRAINT_OA) * (constants.INT_RATE_OA / 12)
    # else:
    #     oa_interest += oa_accumulated * ((constants.INT_RATE_OA + constants.INT_EXTRA) / 12)
    
    return oa_interest


def _calculate_monthly_interest_sa(oa_accumulated, sa_accumulated, rem_amount_for_extra_int_sa_ma):
    """Calculates the interest to be added to the SA in a month period.
    
    Extra 1% interest earned on OA, if any, is credited to the SA.

    Args:
        oa_accumulated (float): Current amount in OA
        sa_accumulated (float): Current amount in SA

    Returns:
        float: SA interest amount
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


def _calculate_monthly_interest_ma(ma_accumulated, rem_amount_for_extra_int_ma):
    """Calculates the interest to be added to the MA in a month period.

    Args:
        ma_accumulated (float): Current amount in MA

    Returns:
        float: MA interest amount
    """

    ma_interest = 0
    if ma_accumulated > rem_amount_for_extra_int_ma:
        ma_interest += rem_amount_for_extra_int_ma * ((constants.INT_RATE_MA + constants.INT_EXTRA) / 12)
        ma_interest += (ma_accumulated - rem_amount_for_extra_int_ma) * (constants.INT_RATE_MA / 12)
    else:
        ma_interest += ma_accumulated * ((constants.INT_RATE_MA + constants.INT_EXTRA) / 12)
    
    return ma_interest


def _calculate_annual_change(salary, bonus, oa_curr, sa_curr, ma_curr, 
                            date_start=None, age=None, dob=None):
    """Calculates the total contributions and interest earned for the current year.

    Adds the interest, along with the contributions in the year, to the CPF account balances. \\
    Returns the projected amount in the CPF accounts at the end of the year.

    `date_start` and `dob` are used for actual scenarios. \\
    `age` is used for unit testing.

    Args:
        salary (float): Annual salary of employee
        bonus (float): Bonus/commission received in the year
        oa_curr (float): Current amount in OA
        sa_curr (float): Current amount in SA
        ma_curr (float): Current amount in MA
        date_start (date): Start date of the year
        age (int): Age of employee
        dob (str): Date of birth of employee in YYYYMM format

    Returns:
        float: New amount in OA, after contributions and interest for this year
        float: New amount in SA, after contributions and interest for this year
        float: New amount in MA, after contributions and interest for this year
    """

    oa_accumulated, sa_accumulated, ma_accumulated = oa_curr, sa_curr, ma_curr
    oa_interest_total, sa_interest_total, ma_interest_total = (0, 0, 0)
    
    # iterate through the 12 months in the year
    for i in range(12):
        # to check if this month contains a bonus
        if age is None:
            # add 1 month to the date for each iteration
            year_start, month_start = (date_start.year, date_start.month + i)
            if month_start > 12:
                year_start += 1
                month_start -= 12

            # wrap the date in a datetime object
            date_start = dt.date(year_start, month_start, 1)
            age = _get_age(dob, date_start)
            bonus_annual = bonus if month_start == 12 else 0
        else:
            # else-condition only applies for unit testing
            bonus_annual = bonus if i == 11 else 0

        # add the CPF allocation for this month
        # this is actually the contribution for the previous month's salary
        oa_alloc, sa_alloc, ma_alloc = calculate_cpf_allocation(salary / 12, bonus_annual, age=age)
        oa_accumulated += oa_alloc
        sa_accumulated += sa_alloc
        ma_accumulated += ma_alloc

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

        print(i, oa_interest, sa_interest, ma_interest)

    print(oa_interest_total, sa_interest_total, ma_interest_total)

    # interest added at the end of the year
    oa_new = oa_accumulated + oa_interest_total
    sa_new = sa_accumulated + sa_interest_total
    ma_new = ma_accumulated + ma_interest_total

    return oa_new, sa_new, ma_new