import logic.cpf_constants as constants
import logic.cpf as cpf

class TestCalculateCpfContribution(object):
    """
    Tests the `calculate_cpf_contribution()` method in cpf.py.

    Test scenarios: 
    1. Age <=55
        a. Salary <=$50/month
        b. Salary >$50 to <=$500/month
        c. Salary >$500 to <$750/month
        d. Salary above $750/month and below OW Ceiling, bonus below AW Ceiling
        e. Salary above $750/month and below OW Ceiling, bonus above AW Ceiling
        f. Salary above $750/month and above OW Ceiling, bonus below AW Ceiling
        g. Salary above $750/month and above OW Ceiling, bonus above AW Ceiling
    """

    def perform_assertion(self, salary, bonus, age, cont_employee, cont_employer):
        cont_employee_test, cont_employer_test = cpf.calculate_cpf_contribution(salary, bonus, age=age)
        assert round(cont_employee, 2) == round(cont_employee_test, 2)
        assert round(cont_employer, 2) == round(cont_employer_test, 2)

    def test_scenario_1a(self):
        salary, bonus, age = (50 * 12, 0, 30)
        cont_employee = 0
        cont_employer = 0
        self.perform_assertion(salary, bonus, age, cont_employee, cont_employer)

    def test_scenario_1b(self):
        salary, bonus, age = (500 * 12, 0, 30)
        cont_employee = 0
        cont_employer = 0.17 * salary
        self.perform_assertion(salary, bonus, age, cont_employee, cont_employer)

    def test_scenario_1c(self):
        salary, bonus, age = (749 * 12, 0, 30)
        cont_total = (0.17 * salary) + (0.6 * (salary - (500 * 12)))
        cont_employee = 0.6 * (salary - (500 * 12))
        cont_employer = cont_total - cont_employee
        self.perform_assertion(salary, bonus, age, cont_employee, cont_employer)

    def test_scenario_1d(self):
        salary, bonus, age = (4000 * 12, 20000, 30)
        cont_total = (0.37 * salary) + (0.37 * bonus)
        cont_employee = (0.2 * salary) + (0.2 * bonus)
        cont_employer = cont_total - cont_employee
        self.perform_assertion(salary, bonus, age, cont_employee, cont_employer)

    def test_scenario_1e(self):
        salary, bonus, age = (4000 * 12, 100000, 30)
        cont_total = (0.37 * salary) + (0.37 * (102000 - salary))
        cont_employee = (0.2 * salary) + (0.2 * (102000 - salary))
        cont_employer = cont_total - cont_employee
        self.perform_assertion(salary, bonus, age, cont_employee, cont_employer)

    def test_scenario_1f(self):
        salary, bonus, age = (8000 * 12, 20000, 30)
        cont_total = (0.37 * 72000) + (0.37 * bonus)
        cont_employee = (0.2 * 72000) + (0.2 * bonus)
        cont_employer = cont_total - cont_employee
        self.perform_assertion(salary, bonus, age, cont_employee, cont_employer)

    def test_scenario_1g(self):
        salary, bonus, age = (8000 * 12, 100000, 30)
        cont_total = (0.37 * 72000) + (0.37 * (102000 - 72000))
        cont_employee = (0.2 * 72000) + (0.2 * (102000 - 72000))
        cont_employer = cont_total - cont_employee
        self.perform_assertion(salary, bonus, age, cont_employee, cont_employer)


class TestCalculateCpfAllocation(object):
    """
    Tests the `calculate_cpf_allocation()` method in cpf.py. \\
    Assume that `calculate_cpf_contribution()` method is correct.

    Age is the only variable here. \\
    Each test scenario contains 2 assertions - one with bonus and one without bonus. \\
    Test scenarios: 
    1. Age <=35
    2. Age >35 to <=45
    3. Age >45 to <=50
    4. Age >50 to <=55
    5. Age >55 to <=60
    6. Age >60 to <=65
    7. Age >65
    """

    global salary, bonus
    salary, bonus = (4000, 10000)

    def get_contribution_amount_by_age(self, age, with_bonus):
        bonus_annual = bonus if with_bonus is True else 0
        cont = cpf.get_monthly_contribution_amount(salary, bonus_annual, age=age, dob=None, entity=constants.STR_COMBINED)
        return cont

    def truncate(self, n, decimals=2):
        before_dec, after_dec = str(n).split('.')
        return float('.'.join((before_dec, after_dec[0:2])))

    def get_alloc_amount(self, cont, sa_ratio, ma_ratio):
        sa_alloc = self.truncate(sa_ratio * cont)
        ma_alloc = self.truncate(ma_ratio * cont)
        oa_alloc = cont - sa_alloc - ma_alloc
        return oa_alloc, sa_alloc, ma_alloc

    def perform_assertion(self, salary, bonus, age, alloc_exp):
        """
        Helper class to perform assertion checks.
        Round the values to 2 decimal places when checking for equality.

        Args:
            - age (int): Age of employee
            - salary (float): Monthly salary of employee
            - bonus (float): Bonus/commission received in the year
            - alloc_exp (array): Expected amount to be allocated into the CPF accounts [OA, SA, MA]
        """
        
        oa_alloc_test, sa_alloc_test, ma_alloc_test = cpf.calculate_cpf_allocation(
                                                        salary, bonus, age=age)
        assert round(alloc_exp[0], 2) == round(oa_alloc_test, 2)
        assert round(alloc_exp[1], 2) == round(sa_alloc_test, 2)
        assert round(alloc_exp[2], 2) == round(ma_alloc_test, 2)

    def test_scenario_1(self):
        age = 35
        cont_with_bonus = self.get_contribution_amount_by_age(age, True)
        cont_wo_bonus = self.get_contribution_amount_by_age(age, False)
        oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus = self.get_alloc_amount(cont_with_bonus, 0.1621, 0.2162)
        oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus = self.get_alloc_amount(cont_wo_bonus, 0.1621, 0.2162)

        self.perform_assertion(salary, bonus, age, [oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus])
        self.perform_assertion(salary, 0, age, [oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus])
    
    def test_scenario_2(self):
        age = 45
        cont_with_bonus = self.get_contribution_amount_by_age(age, True)
        cont_wo_bonus = self.get_contribution_amount_by_age(age, False)
        oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus = self.get_alloc_amount(cont_with_bonus, 0.1891, 0.2432)
        oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus = self.get_alloc_amount(cont_wo_bonus, 0.1891, 0.2432)

        self.perform_assertion(salary, bonus, age, [oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus])
        self.perform_assertion(salary, 0, age, [oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus])

    def test_scenario_3(self):
        age = 50
        cont_with_bonus = self.get_contribution_amount_by_age(age, True)
        cont_wo_bonus = self.get_contribution_amount_by_age(age, False)
        oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus = self.get_alloc_amount(cont_with_bonus, 0.2162, 0.2702)
        oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus = self.get_alloc_amount(cont_wo_bonus, 0.2162, 0.2702)

        self.perform_assertion(salary, bonus, age, [oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus])
        self.perform_assertion(salary, 0, age, [oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus])

    def test_scenario_4(self):
        age = 55
        cont_with_bonus = self.get_contribution_amount_by_age(age, True)
        cont_wo_bonus = self.get_contribution_amount_by_age(age, False)
        oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus = self.get_alloc_amount(cont_with_bonus, 0.3108, 0.2837)
        oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus = self.get_alloc_amount(cont_wo_bonus, 0.3108, 0.2837)

        self.perform_assertion(salary, bonus, age, [oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus])
        self.perform_assertion(salary, 0, age, [oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus])
    
    def test_scenario_5(self):
        age = 60
        cont_with_bonus = self.get_contribution_amount_by_age(age, True)
        cont_wo_bonus = self.get_contribution_amount_by_age(age, False)
        oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus = self.get_alloc_amount(cont_with_bonus, 0.1346, 0.4038)
        oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus = self.get_alloc_amount(cont_wo_bonus, 0.1346, 0.4038)

        self.perform_assertion(salary, bonus, age, [oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus])
        self.perform_assertion(salary, 0, age, [oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus])

    def test_scenario_6(self):
        age = 65
        cont_with_bonus = self.get_contribution_amount_by_age(age, True)
        cont_wo_bonus = self.get_contribution_amount_by_age(age, False)
        oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus = self.get_alloc_amount(cont_with_bonus, 0.1515, 0.6363)
        oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus = self.get_alloc_amount(cont_wo_bonus, 0.1515, 0.6363)

        self.perform_assertion(salary, bonus, age, [oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus])
        self.perform_assertion(salary, 0, age, [oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus])

    def test_scenario_7(self):
        age = 80
        cont_with_bonus = self.get_contribution_amount_by_age(age, True)
        cont_wo_bonus = self.get_contribution_amount_by_age(age, False)
        oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus = self.get_alloc_amount(cont_with_bonus, 0.08, 0.84)
        oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus = self.get_alloc_amount(cont_wo_bonus, 0.08, 0.84)

        self.perform_assertion(salary, bonus, age, [oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus])
        self.perform_assertion(salary, 0, age, [oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus])


class TestCpfCalculateAnnualChange(object):
    """
    Tests the `calculate_annual_change()` method in cpf.py.

    Test scenarios:
    1. OA < $20k, OA+SA+MA < $60k
    2. OA > $20k, $20k+SA+MA < $60k
    3. OA < $20k, OA+SA < $60k, OA+SA+MA > $60k
    4. OA < $20k, OA+SA > $60k after a few months
    5. OA > $20k, $20k+SA > $60k, $20k+SA+MA > $60k
    6. OA > $20k, $20k+SA < $60k, $20k+SA+MA > $60k
    7. OA > $20k after a few months, OA+SA+MA < $60k
    8. OA > $20k after a few months, OA+SA+MA > $60k after a few months
    """

    # Class variables
    #   age: immaterial here - for convenience, standardise to age 25
    #   salary: standardise to $4,000
    #   bonus: standardise to $10,000
    global age, salary, bonus, cont_oa, cont_sa, cont_ma, cont_oa_bonus, cont_sa_bonus, cont_ma_bonus
    age, salary, bonus = (25, 4000, 10000)
    # 0.6217, 0.1621. 0.2162 of contribution (approx. 23%, 6%, 8% of $4000/$14000)
    cont_oa, cont_sa, cont_ma = (920.11, 239.91, 319.98)
    cont_oa_bonus, cont_sa_bonus, cont_ma_bonus = (3220.40, 839.68, 1119.92)

    # helper function
    def add_monthly_contribution(self, oa, sa, ma, month):
        if month == 12: # month is December
            oa += cont_oa_bonus
            sa += cont_sa_bonus
            ma += cont_ma_bonus
        else:
            oa += cont_oa
            sa += cont_sa
            ma += cont_ma

        return oa, sa, ma
    
    def perform_assertion(self, balance_orig, balance_exp):
        """
        Helper class to perform assertion checks.

        Args:
        - balance_orig (array): Original balance in CPF accounts [OA, SA, MA]
        - balance_exp (array): Expected balance in CPF accounts [OA, SA, MA]
        """

        oa_test, sa_test, ma_test = cpf.calculate_annual_change(salary * 12, bonus,
                                        balance_orig[0], balance_orig[1], balance_orig[2], age=age)

        assert balance_exp[0] == oa_test
        assert balance_exp[1] == sa_test
        assert balance_exp[2] == ma_test


    def test_scenario_1(self):
        print('Test scenario 1: OA < $20k, OA+SA+MA < $60k')
        oa, sa, ma = (6000, 2000, 3000)
        int_oa, int_sa, int_ma = (0, 0, 0)

        # OA: 3.5%
        # SA: 5%
        # MA: 5%
        for i in range(1, 13):
            oa, sa, ma = self.add_monthly_contribution(oa, sa, ma, i)
            # add interest in this month
            int_oa += oa * (0.035 / 12)
            int_sa += sa * (0.05 / 12)
            int_ma += ma * (0.05 / 12)
        
        self.perform_assertion([6000, 2000, 3000], [oa + int_oa, sa + int_sa, ma + int_ma])

    def test_scenario_2(self):
        print('Test scenario 2: OA > $20k, $20k+SA+MA < $60k')
        oa, sa, ma = (35000, 2000, 3000)
        int_oa, int_sa, int_ma = (0, 0, 0)

        # OA (up to $20k): 3.5%, OA (after $20k): 2.5%
        # SA: 5%
        # MA: 5%
        for i in range(1, 13):
            oa, sa, ma = self.add_monthly_contribution(oa, sa, ma, i)
            # add interest in this month
            int_oa += 20000 * (0.035 / 12)
            int_oa += (oa - 20000) * (0.025 / 12)
            int_sa += sa * (0.05 / 12)
            int_ma += ma * (0.05 / 12)
        
        self.perform_assertion([35000, 2000, 3000], [oa + int_oa, sa + int_sa, ma + int_ma])

    def test_scenario_3(self):
        print('Test scenario 3: OA < $20k, OA+SA < $60k, OA+SA+MA > $60k')
        oa, sa, ma = (6000, 30000, 30000)
        int_oa, int_sa, int_ma = (0, 0, 0)

        # OA: 3.5%
        # SA: 5%
        # MA (for greatest MA value where $20k+SA+MA <= $60k): 5%, MA (remaining): 4%
        for i in range(1, 13):
            oa, sa, ma = self.add_monthly_contribution(oa, sa, ma, i)
            # add interest in this month
            int_oa += oa * (0.035 / 12)
            int_sa += sa * (0.05 / 12)
            print('Test - i: {}, SA amount: {}'.format(i, sa))
            print('Test - i: {}, SA interest this month: {}'.format(i, sa * (0.05 / 12)))
            amount_ma_eligible_for_extra_int = 60000 - oa - sa
            int_ma += amount_ma_eligible_for_extra_int * (0.05 / 12)
            int_ma += (ma - amount_ma_eligible_for_extra_int) * (0.04 / 12)
  
        self.perform_assertion([6000, 30000, 30000], [oa + int_oa, sa + int_sa, ma + int_ma])      

    def test_scenario_4(self):
        print('Test scenario 4: OA < $20k, OA+SA > $60k after a few months')
        oa, sa, ma = (6000, 40000, 30000)
        int_oa, int_sa, int_ma = (0, 0, 0)

        # OA: 3.5%
        # SA (for greatest SA value where OA+SA <= $60k): 5%, SA (remaining): 4%
        # MA (for greatest MA value where OA+SA+MA <= $60k): 5%, MA (remaining): 4%
        for i in range(1, 13):
            oa, sa, ma = self.add_monthly_contribution(oa, sa, ma, i)
            # add interest in this month
            int_oa += oa * (0.035 / 12)
            amount_sa_eligible_for_extra_int = 60000 - oa

            if sa > amount_sa_eligible_for_extra_int:
                int_sa += amount_sa_eligible_for_extra_int * (0.05 / 12)
                int_sa += (sa - amount_sa_eligible_for_extra_int) * (0.04 / 12)
            else:
                int_sa += sa * (0.05 / 12)

            amount_ma_eligible_for_extra_int = max(0, amount_sa_eligible_for_extra_int - sa)
            int_ma += amount_ma_eligible_for_extra_int * (0.05 / 12)
            int_ma += (ma - amount_ma_eligible_for_extra_int) * (0.04 / 12)

        self.perform_assertion([6000, 40000, 30000], [oa + int_oa, sa + int_sa, ma + int_ma])      


    def test_scenario_5(self):
        print('Test scenario 5: OA > $20k, $20k+SA > $60k, $20k+SA+MA > $60k')
        oa, sa, ma = (25000, 45000, 30000)
        int_oa, int_sa, int_ma = (0, 0, 0)

        # OA (up to $20k): 3.5%, OA (after $20k): 2.5%
        # SA (for greatest SA value where $20k+SA <= $60k): 5%, SA (remaining): 4%
        # MA: 4%
        for i in range(1, 13):
            oa, sa, ma = self.add_monthly_contribution(oa, sa, ma, i)
            # add interest in this month
            int_oa += 20000 * (0.035 / 12)
            int_oa += (oa - 20000) * (0.025 / 12)
            amount_sa_eligible_for_extra_int = 60000 - 20000
            int_sa += amount_sa_eligible_for_extra_int * (0.05 / 12)
            int_sa += (sa - amount_sa_eligible_for_extra_int) * (0.04 / 12)
            int_ma += ma * (0.04 / 12)

        self.perform_assertion([25000, 45000, 30000], [oa + int_oa, sa + int_sa, ma + int_ma])      

    def test_scenario_6(self):
        print('Test scenario 6: OA > $20k, $20k+SA < $60k, $20k+SA+MA > $60k')
        oa, sa, ma = (25000, 30000, 30000)
        int_oa, int_sa, int_ma = (0, 0, 0)

        # OA (up to $20k): 3.5%, OA (after $20k): 2.5%
        # SA: 5%
        # MA (for greatest MA value where $20k+SA+MA <= $60k): 5%, MA (remaining): 4%
        for i in range(1, 13):
            oa, sa, ma = self.add_monthly_contribution(oa, sa, ma, i)
            # add interest in this month
            int_oa += 20000 * (0.035 / 12)
            int_oa += (oa - 20000) * (0.025 / 12)
            int_sa += sa * (0.05 / 12)
            amount_ma_eligible_for_extra_int = 60000 -  20000 - sa
            int_ma += amount_ma_eligible_for_extra_int * (0.05 / 12)
            int_ma += (ma - amount_ma_eligible_for_extra_int) * (0.04 / 12)
        
        self.perform_assertion([25000, 30000, 30000], [oa + int_oa, sa + int_sa, ma + int_ma])      

    def test_scenario_7(self):
        print('Test scenario 7: OA > $20k after a few years, OA+SA+MA < $60k')
        oa, sa, ma = (15000, 5000, 5000)
        int_oa, int_sa, int_ma = (0, 0, 0)

        # OA (up to $20k): 3.5%, OA (after $20k): 2.5%
        # SA: 5%
        # MA: 5%
        for i in range(1, 13):
            oa, sa, ma = self.add_monthly_contribution(oa, sa, ma, i)
            # add interest in this month
            if oa <= 20000:
                int_oa += oa * (0.035 / 12)
            else:
                int_oa += 20000 * (0.035 / 12)
                int_oa += (oa - 20000) * (0.025 / 12)

            int_sa += sa * (0.05 / 12)
            int_ma += ma * (0.05 / 12)
        
        self.perform_assertion([15000, 5000, 5000], [oa + int_oa, sa + int_sa, ma + int_ma])      

    def test_scenario_8(self):
        print('Test scenario 8: OA > $20k after a few years, OA+SA+MA > $60k after a few years')
        oa, sa, ma = (18000, 39000, 5000)
        int_oa, int_sa, int_ma = (0, 0, 0)

        # OA (up to $20k): 3.5%, OA (after $20k): 2.5%
        # SA (for greatest SA value where $20k+SA <= $60k): 5%, SA (remaining): 4%
        # MA (for greatest MA value where $20k+SA+MA <= $60k): 5%, MA (remaining): 4%
        for i in range(1, 13):
            oa, sa, ma = self.add_monthly_contribution(oa, sa, ma, i)
            # add interest in this month
            if oa <= 20000:
                int_oa += oa * (0.035 / 12)
            else:
                int_oa += 20000 * (0.035 / 12)
                int_oa += (oa - 20000) * (0.025 / 12)

            amount_sa_eligible_for_extra_int = 60000 - min(oa, 20000)
            if sa <= amount_sa_eligible_for_extra_int:
                # some value of MA can get an additional 1% as well
                int_sa += sa * (0.05 / 12)
                amount_ma_eligible_for_extra_int = amount_sa_eligible_for_extra_int - sa
                if ma <= amount_ma_eligible_for_extra_int:
                    int_ma += ma * (0.05 / 12)
                else:
                    int_ma += amount_ma_eligible_for_extra_int * (0.05 / 12)
                    int_ma += (ma - amount_ma_eligible_for_extra_int) * (0.04 / 12)
            else:
                # not all SA can get an additional 1%
                int_sa += amount_sa_eligible_for_extra_int * (0.05 / 12)
                int_sa += (sa - amount_sa_eligible_for_extra_int) * (0.04 / 12)
                int_ma += ma * (0.04 / 12)
   
        self.perform_assertion([18000, 39000, 5000], [oa + int_oa, sa + int_sa, ma + int_ma])      


# class TestCalculateCpfProjection(object):
#     """
#     Tests the `calculate_cpf_projection()` method in cpf.py.

#     """

#     def test_scenario_1(self):
#         print('Test scenario 1: age=25, salary=4000, yoy_increase=0.05, n_years=1')
#         print('Test scenario 1: Base CPF amounts are equal to scenario 1 in TestCpfCalculateAnnualChange')
        
#         # only calculate for 1 year

#         oa, sa, ma = (6000, 2000, 3000)
#         oa_cont, sa_cont, ma_cont = (1150, 300, 400) # 23%, 6%, 8% of $5000
#         int_oa, int_sa, int_ma = (0, 0, 0)
#         # OA: 3.5%
#         # SA: 5%
#         # MA: 5%
#         for i in range(1, 13):
#             oa += oa_cont
#             sa += sa_cont
#             ma += ma_cont
#             # add interest in this month
#             int_oa += oa * (0.035 / 12)
#             int_sa += sa * (0.05 / 12)
#             int_ma += ma * (0.05 / 12)
        
#         oa += int_oa
#         sa += int_sa
#         ma += int_ma
        
#         base_cpf = { 'oa': 6000, 'sa': 2000, 'ma': 3000}
#         oa_test, sa_test, ma_test = cpf.calculate_cpf_projection(
#                                         25, 5000, 0.05, base_cpf, 1)
                        
#         assert oa == oa_test
#         assert sa == sa_test
#         assert ma == ma_test