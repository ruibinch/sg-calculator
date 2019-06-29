from logic import cpf_constants as constants
import math
import datetime as dt


###################################################################################################
#                                      MAIN API FUNCTIONS                                         #
###################################################################################################

def calculate_cpf_contribution(salary, bonus, bonus_month=12, age=None, dob=None):
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
        bonus_month (int): Month where bonus is received (1-12)
        age (int): Age of employee
        dob (str): Date of birth of employee in YYYYMM format

    Returns:
        *tuple*: Tuple containing
            - (*float*): Amount contributed by the employee in the year
            - (*float*): Amount contributed by the employer in the year

    """
    
    cont_total, cont_employee = (0, 0)

    for i in range(1, 13):
        bonus_annual = bonus if i == bonus_month else 0

        cont_total += _get_monthly_contribution_amount(salary / 12, bonus_annual, age, dob, entity=constants.STR_COMBINED)
        cont_employee += _get_monthly_contribution_amount(salary / 12, bonus_annual, age, dob, entity=constants.STR_EMPLOYEE)

    return cont_employee, cont_total - cont_employee


def calculate_cpf_allocation(salary_monthly, bonus, age=None, dob=None):
    """Calculates the CPF allocation for the month.

    `Reference <https://www.cpf.gov.sg/Assets/employers/Documents/Table%2011_Pte%20and%20Npen_CPF%20Allocation%20Rates%20Jan%202016.pdf/>`_

    Steps for calculation:

    1. From the total contribution amount, derive the amount allocated into SA and MA using the respective multiplier corresponding to the age.
    2. OA allocation = Total contribution - SA allocation - MA allocation.
    
    Args:
        salary_monthly (float): Monthly salary of employee
        bonus (float): Bonus/commission received in the year; only applicable in the month when bonus is disbursed
        age (int): Age of employee
        dob (str): Date of birth of employee in YYYYMM format

    Returns:
        *tuple*: Tuple containing
            - (*float*): Allocation amount into OA
            - (*float*): Allocation amount into SA
            - (*float*): Allocation amount into MA
    """

    cont_monthly = _get_monthly_contribution_amount(salary_monthly, bonus, age, dob, entity=constants.STR_COMBINED)
    sa_alloc = _get_allocation_amount(age, dob, cont_monthly, account=constants.STR_SA)
    ma_alloc = _get_allocation_amount(age, dob, cont_monthly, account=constants.STR_MA)
    oa_alloc = cont_monthly - sa_alloc - ma_alloc

    return round(oa_alloc, 2), sa_alloc, ma_alloc


def calculate_cpf_projection(salary, bonus, yoy_increase_salary, yoy_increase_bonus,
                             base_cpf, bonus_month=12, age=None, dob=None,
                             proj_start_date=None, n_years=None, target_year=None, 
                             oa_topups=None, oa_withdrawals=None,
                             sa_topups=None, sa_withdrawals=None,
                             ma_topups=None, ma_withdrawals=None):
    """Calculates the projected account balance in the CPF accounts after `n_years` or in `target_year`.

    `Reference <https://www.cpf.gov.sg/Assets/common/Documents/InterestRate.pdf/>`_

    Args:
        salary (float): Annual salary of employee
        bonus (float): Bonus/commission received in the year
        yoy_increase_salary (float): Projected year-on-year percentage increase in salary
        yoy_increase_bonus (float): Projected year-on-year percentage increase in bonus
        base_cpf (list of floats): Contains the current balance in the CPF accounts 
        bonus_month (int): Month where bonus is received (1-12)
        age (int): Age of employee
        dob (str): Date of birth of employee in YYYYMM format
        proj_start_date (date): Starting date of projection (*only used for testing purposes*)
        n_years (int): Number of years into the future to project
        target_year (int): Target end year of projection
        oa_topups (list): Cash top-ups to the OA; each entry is a tuple containing:
            - *str*: year of cash topup in YYYY or YYYYMM format
            - *float*: amount to topup
        oa_withdrawals (list): Withdrawals from the OA; each entry is a tuple containing:
            - *str*: year of cash withdrawal in YYYY or YYYYMM format
            - *float*: amount to withdraw
        sa_topups (list): Cash top-ups to the SA; each entry is a tuple containing:
            - *str*: year of cash topup in YYYY or YYYYMM format
            - *float*: amount to topup
            - *boolean*: whether this amount is coming from the OA
        sa_withdrawals (list): Withdrawals from the SA
            - *str*: year of cash withdrawal in YYYY or YYYYMM format
            - *float*: amount to withdraw
        ma_topups (list): Cash top-ups to the MA
            - *str*: year of cash topup in YYYY or YYYYMM format
            - *float*: amount to topup
        ma_withdrawals (list): Withdrawals from the MA
            - *str*: year of cash withdrawal in YYYY or YYYYMM format
            - *float*: amount to withdraw

    Returns:
        *tuple*: Tuple containing
            - (*float*): OA balance after `n_years`
            - (*float*): SA balance after `n_years`
            - (*float*): MA balance after `n_years`
    """

    oa, sa, ma = base_cpf[0], base_cpf[1], base_cpf[2]
    n_years = _get_num_projection_years(target_year) if n_years is None else n_years

    # convert all topup/withdrawal tuples to zero-indexing of year
    oa_topups = _convert_year_to_zero_indexing(oa_topups)
    oa_withdrawals = _convert_year_to_zero_indexing(oa_withdrawals)
    sa_topups = _convert_year_to_zero_indexing(sa_topups)
    sa_withdrawals = _convert_year_to_zero_indexing(sa_withdrawals)
    ma_topups = _convert_year_to_zero_indexing(ma_topups)
    ma_withdrawals = _convert_year_to_zero_indexing(ma_withdrawals)

    for i in range(n_years):
        # default day to 1 as it is not used
        if i == 0:
            # it is the first year, so the starting month would be different
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
        oa_topups_year = _get_account_deltas_year(oa_topups, i)
        oa_withdrawals_year = _get_account_deltas_year(oa_withdrawals, i)
        sa_topups_year = _get_account_deltas_year(sa_topups, i)
        sa_withdrawals_year = _get_account_deltas_year(sa_withdrawals, i)
        ma_topups_year = _get_account_deltas_year(ma_topups, i)
        ma_withdrawals_year = _get_account_deltas_year(ma_withdrawals, i)
        account_deltas = (oa_topups_year, oa_withdrawals_year, sa_topups_year, sa_withdrawals_year, ma_topups_year, ma_withdrawals_year)

        # get SA topup/OA withdrawal details
        # oa_withdrawal = oa_withdrawals.get(i, 0)
        # sa_topup_details = sa_topups.get(i, [])
        # sa_topup = sa_topup_details[0] if sa_topup_details != [] else 0
        # sa_topup_from_oa = sa_topup_details[1] if sa_topup_details != [] else None

        oa, sa, ma = calculate_annual_change(salary_proj, bonus_proj, oa, sa, ma,
                                             account_deltas, bonus_month, 
                                             date_start=date_start, age=age, dob=dob)
        # print('Year {}: {}, {}, {}'.format(i, round(oa, 2), round(sa, 2), round(ma, 2)))

    return round(oa, 2), round(sa, 2), round(ma, 2)


###################################################################################################
#                               CPF-RELATED HELPER FUNCTIONS                                      #
###################################################################################################

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


def calculate_annual_change(salary, bonus, oa_curr, sa_curr, ma_curr,
                            account_deltas=None, bonus_month=12, 
                            date_start=None, age=None, dob=None):
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
        account_deltas (list): List of topups/withdrawals to the OA/SA/MA accounts respectively
        bonus_month (int): Month where bonus is received (1-12)
        date_start (date): Start date of the year to calculate from
        age (int): Age of employee
        dob (str): Date of birth of employee in YYYYMM format

    Returns:
        *tuple*: Tuple containing
            - (*float*): New amount in OA, after contributions and interest for this year
            - (*float*): New amount in SA, after contributions and interest for this year
            - (*float*): New amount in MA, after contributions and interest for this year
    """

    oa_accumulated, sa_accumulated, ma_accumulated = oa_curr, sa_curr, ma_curr
    oa_interest_total, sa_interest_total, ma_interest_total = (0, 0, 0)
    
    # iterate through the months in the year
    month_start = date_start.month if date_start is not None else 1
    for month in range(month_start, 13):
        if dob is not None:
            # wrap the date in a datetime object
            date_start_iter = dt.date(date_start.year, month, 1)
            age = _get_age(dob, date_start_iter)
            # print('Month: {}/{}, Age: {}'.format(date_start_iter.year, i, age))
        # else:
        #     # else-condition only applies for unit testing of class TestCpfCalculateAnnualChange1
        #     bonus_annual = bonus if month == bonus_month else 0
        
        # check if this month is the month where bonus is received
        bonus_annual = bonus if month == bonus_month else 0
        
        # add the CPF allocation for this month
        # this is actually the contribution for the previous month's salary
        oa_alloc, sa_alloc, ma_alloc = calculate_cpf_allocation(salary / 12, bonus_annual, age=age)
        oa_accumulated += oa_alloc
        sa_accumulated += sa_alloc
        ma_accumulated += ma_alloc

        if account_deltas is not None:
            # if there have been topups/withdrawals in the accounts this month
            (delta_oa, delta_sa, delta_ma) = _get_account_deltas_month(account_deltas, month)
            oa_accumulated += delta_oa
            sa_accumulated += delta_sa
            ma_accumulated += delta_ma
        # for now, assume that OA withdrawals and SA top-ups are done in January
        # if month == 1 and all(v is not None for v in [oa_withdrawal, sa_topup, sa_topup_from_oa]):
        #     oa_accumulated -= oa_withdrawal
        #     sa_accumulated += sa_topup
        #     if sa_topup_from_oa is True:
        #         oa_accumulated -= sa_topup
        print('Algo - Month {}: {}'.format(month, sa_accumulated))

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

    # print(oa_interest_total, sa_interest_total, ma_interest_total)

    # interest added at the end of the year
    oa_new = oa_accumulated + oa_interest_total
    sa_new = sa_accumulated + sa_interest_total
    ma_new = ma_accumulated + ma_interest_total

    return oa_new, sa_new, ma_new


###################################################################################################
#                                   GENERIC HELPER FUNCTIONS                                      #
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
        *int*: Age of employee
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


def _get_num_projection_years(target_year):
    """Returns the number of years between this year and the target year.

    Args:
        target_year (int): Target year in the future to project for
    
    Returns:
        int: Number of years to project for
    """

    return target_year - dt.date.today().year + 1


def _convert_year_to_zero_indexing(list_orig):
    """Converts the year values in the list from the actual year to zero indexing based on the current year.

    Args:
        list_orig (list): Original list in structure - (date in YYYYMM or YYYY format, amount)

    Returns:
        *list*: Structure - (zero-indexed year, month, amount, optional boolean)
    """

    list_new = []

    if list_orig is not []:
        for item in list_orig:
            date = item[0] # in YYYY or YYYYMM format
            amount = item[1]

            # extract year and month (if applicable) from the date
            year = int(date[0:4])
            month = int(date[4:6]) if date[4:6] is not '' else 0

            year_zero_index = int(year) - dt.date.today().year
            try:
                # item[2] is only used if it is a SA topup
                list_new.append((year_zero_index, month, amount, item[2]))
            except IndexError:
                list_new.append((year_zero_index, month, amount))
                
    return list_new
            

def _get_account_deltas_year(list_entries, year):
    """
        Returns the topup/withdrawal entries in the list that correspond to the current year. \\
        Remove the zero-indexed year in the tuple.

        Args:
            list_entries (list): List of topup/withdrawal entries
            year (int): Zero-indexed year

        Returns:
            *list*: List of entries that correspond to the current year - (month, amount, boolean)
    """

    return [entry[1:] for entry in list_entries if entry[0] == year]


def _get_account_deltas_month(account_deltas, month_curr):
    """
        Returns the amount deltas in the respective OA, SA and MA accounts.

        Args:
            account_deltas (list): List of topups/withdrawals to the OA/SA/MA accounts respectively in the year
            month_curr (int): Current month in numeric representation

        Returns:
            *tuple*: Tuple containing
                - (*float*): Delta change in OA in this month
                - (*float*): Delta change in SA in this month
                - (*float*): Delta change in MA in this month
    """
    delta_oa, delta_sa, delta_ma = (0, 0, 0)
    months_search = [month_curr]
    if month_curr == 1:
        # account topups/withdrawals with no specified month are defaulted to occur in Jan
        months_search.append(0)

    oa_topups_year, oa_withdrawals_year = account_deltas[0], account_deltas[1]
    sa_topups_year, sa_withdrawals_year = account_deltas[2], account_deltas[3]
    ma_topups_year, ma_withdrawals_year = account_deltas[4], account_deltas[5]

    for (month, amount) in oa_topups_year:
        delta_oa += amount if month in months_search else 0

    for (month, amount) in oa_withdrawals_year:
        delta_oa -= amount if month in months_search else 0

    for (month, amount, is_from_oa) in sa_topups_year:
        if month in months_search:
            delta_sa += amount
            delta_oa -= amount if is_from_oa else 0

    for (month, amount) in sa_withdrawals_year:
        delta_sa -= amount if month in months_search else 0

    for (month, amount) in ma_topups_year:
        delta_ma += amount if month in months_search else 0

    for (month, amount) in ma_withdrawals_year:
        delta_ma -= amount if month in months_search else 0

    return (delta_oa, delta_sa, delta_ma)


def _round_half_up(n, decimals=0):
    """Rounds the given monetary amount to the nearest dollar.
    
    An amount of 50 cents will be regarded as an additional dollar.

    Args:
        n (float): input amount

    Returns:
        *int*: rounded amount to the nearest dollar
    """

    multiplier = 10 ** decimals
    return math.floor(n*multiplier + 0.5) / multiplier


def _truncate(n, decimals=2):
    """Truncates the given monetary amount to the specified number of decimal places.

    Args:
        n (float): input amount

    Returns:
        *float*: truncated amount to `decimals` decimal places
    """
    before_dec, after_dec = str(n).split('.')
    return float('.'.join((before_dec, after_dec[0:2])))