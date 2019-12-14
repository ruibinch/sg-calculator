import datetime as dt

from logic.cpf.main import calculate_cpf_contribution
from logic.cpf.main import calculate_cpf_allocation
from logic.cpf.main import calculate_cpf_projection
from logic.cpf import constants
from logic.cpf import cpfhelpers
from logic.cpf import genhelpers
from utils import strings

class TestCalculateCpfContribution(object):
    """Tests the `calculate_cpf_contribution()` method in cpf.py.

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

    def _perform_assertion(self, salary, bonus, age, cont_employee, cont_employer):
        contributions = calculate_cpf_contribution(salary, bonus, None, 12, age=age)
        assert round(cont_employee, 2) == float(contributions[strings.KEY_VALUES][strings.KEY_CONT_EMPLOYEE])
        assert round(cont_employer, 2) == float(contributions[strings.KEY_VALUES][strings.KEY_CONT_EMPLOYER])

    def test_scenario_1a(self):
        salary, bonus, age = (50 * 12, 0, 30)
        cont_employee = 0
        cont_employer = 0
        self._perform_assertion(salary, bonus, age, cont_employee, cont_employer)

    def test_scenario_1b(self):
        salary, bonus, age = (500 * 12, 0, 30)
        cont_employee = 0
        cont_employer = 0.17 * salary
        self._perform_assertion(salary, bonus, age, cont_employee, cont_employer)

    def test_scenario_1c(self):
        salary, bonus, age = (749 * 12, 0, 30)
        cont_total = (0.17 * salary) + (0.6 * (salary - (500 * 12)))
        cont_employee = 0.6 * (salary - (500 * 12))
        cont_employer = cont_total - cont_employee
        self._perform_assertion(salary, bonus, age, cont_employee, cont_employer)

    def test_scenario_1d(self):
        salary, bonus, age = (4000 * 12, 20000, 30)
        cont_total = (0.37 * salary) + (0.37 * bonus)
        cont_employee = (0.2 * salary) + (0.2 * bonus)
        cont_employer = cont_total - cont_employee
        self._perform_assertion(salary, bonus, age, cont_employee, cont_employer)

    def test_scenario_1e(self):
        salary, bonus, age = (4000 * 12, 100000, 30)
        cont_total = (0.37 * salary) + (0.37 * (102000 - salary))
        cont_employee = (0.2 * salary) + (0.2 * (102000 - salary))
        cont_employer = cont_total - cont_employee
        self._perform_assertion(salary, bonus, age, cont_employee, cont_employer)

    def test_scenario_1f(self):
        salary, bonus, age = (8000 * 12, 20000, 30)
        cont_total = (0.37 * 72000) + (0.37 * bonus)
        cont_employee = (0.2 * 72000) + (0.2 * bonus)
        cont_employer = cont_total - cont_employee
        self._perform_assertion(salary, bonus, age, cont_employee, cont_employer)

    def test_scenario_1g(self):
        salary, bonus, age = (8000 * 12, 100000, 30)
        cont_total = (0.37 * 72000) + (0.37 * (102000 - 72000))
        cont_employee = (0.2 * 72000) + (0.2 * (102000 - 72000))
        cont_employer = cont_total - cont_employee
        self._perform_assertion(salary, bonus, age, cont_employee, cont_employer)


class TestCalculateCpfAllocation(object):
    """Tests the `calculate_cpf_allocation()` method in cpf.py.
   
    Assumption: `calculate_cpf_contribution()` method is correct.

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

    salary = 4000
    bonus = 10000

    def _get_contribution_amount_by_age(self, age, with_bonus):
        bonus_annual = self.bonus if with_bonus is True else 0
        cont = cpfhelpers._get_monthly_contribution_amount(self.salary, bonus_annual, age=age, entity=constants.STR_COMBINED)
        return cont

    def _get_alloc_amount(self, cont, sa_ratio, ma_ratio):
        sa_alloc = genhelpers._truncate(sa_ratio * cont)
        ma_alloc = genhelpers._truncate(ma_ratio * cont)
        oa_alloc = cont - sa_alloc - ma_alloc
        return oa_alloc, sa_alloc, ma_alloc

    def _perform_assertion(self, bonus, age, alloc_exp):
        """
        Helper class to perform assertion checks.
        Round the values to 2 decimal places when checking for equality.

        Args:
            age (int): Age of employee
            salary (float): Monthly salary of employee
            bonus (float): Bonus/commission received in the year
            alloc_exp (array): Expected amount to be allocated into the CPF accounts [OA, SA, MA]
        """
        
        allocations = calculate_cpf_allocation(self.salary * 12, bonus, None, age=age)
        assert round(alloc_exp[0], 2) == float(allocations[strings.KEY_VALUES][strings.KEY_OA])
        assert round(alloc_exp[1], 2) == float(allocations[strings.KEY_VALUES][strings.KEY_SA])
        assert round(alloc_exp[2], 2) == float(allocations[strings.KEY_VALUES][strings.KEY_MA])

    def test_scenario_1(self):
        age = 35
        cont_with_bonus = self._get_contribution_amount_by_age(age, True)
        cont_wo_bonus = self._get_contribution_amount_by_age(age, False)
        oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus = self._get_alloc_amount(cont_with_bonus, 0.1621, 0.2162)
        oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus = self._get_alloc_amount(cont_wo_bonus, 0.1621, 0.2162)

        self._perform_assertion(self.bonus, age, [oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus])
        self._perform_assertion(0, age, [oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus])
    
    def test_scenario_2(self):
        age = 45
        cont_with_bonus = self._get_contribution_amount_by_age(age, True)
        cont_wo_bonus = self._get_contribution_amount_by_age(age, False)
        oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus = self._get_alloc_amount(cont_with_bonus, 0.1891, 0.2432)
        oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus = self._get_alloc_amount(cont_wo_bonus, 0.1891, 0.2432)

        self._perform_assertion(self.bonus, age, [oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus])
        self._perform_assertion(0, age, [oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus])

    def test_scenario_3(self):
        age = 50
        cont_with_bonus = self._get_contribution_amount_by_age(age, True)
        cont_wo_bonus = self._get_contribution_amount_by_age(age, False)
        oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus = self._get_alloc_amount(cont_with_bonus, 0.2162, 0.2702)
        oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus = self._get_alloc_amount(cont_wo_bonus, 0.2162, 0.2702)

        self._perform_assertion(self.bonus, age, [oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus])
        self._perform_assertion(0, age, [oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus])

    def test_scenario_4(self):
        age = 55
        cont_with_bonus = self._get_contribution_amount_by_age(age, True)
        cont_wo_bonus = self._get_contribution_amount_by_age(age, False)
        oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus = self._get_alloc_amount(cont_with_bonus, 0.3108, 0.2837)
        oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus = self._get_alloc_amount(cont_wo_bonus, 0.3108, 0.2837)

        self._perform_assertion(self.bonus, age, [oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus])
        self._perform_assertion(0, age, [oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus])
    
    def test_scenario_5(self):
        age = 60
        cont_with_bonus = self._get_contribution_amount_by_age(age, True)
        cont_wo_bonus = self._get_contribution_amount_by_age(age, False)
        oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus = self._get_alloc_amount(cont_with_bonus, 0.1346, 0.4038)
        oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus = self._get_alloc_amount(cont_wo_bonus, 0.1346, 0.4038)

        self._perform_assertion(self.bonus, age, [oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus])
        self._perform_assertion(0, age, [oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus])

    def test_scenario_6(self):
        age = 65
        cont_with_bonus = self._get_contribution_amount_by_age(age, True)
        cont_wo_bonus = self._get_contribution_amount_by_age(age, False)
        oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus = self._get_alloc_amount(cont_with_bonus, 0.1515, 0.6363)
        oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus = self._get_alloc_amount(cont_wo_bonus, 0.1515, 0.6363)

        self._perform_assertion(self.bonus, age, [oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus])
        self._perform_assertion(0, age, [oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus])

    def test_scenario_7(self):
        age = 80
        cont_with_bonus = self._get_contribution_amount_by_age(age, True)
        cont_wo_bonus = self._get_contribution_amount_by_age(age, False)
        oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus = self._get_alloc_amount(cont_with_bonus, 0.08, 0.84)
        oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus = self._get_alloc_amount(cont_wo_bonus, 0.08, 0.84)

        self._perform_assertion(self.bonus, age, [oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus])
        self._perform_assertion(0, age, [oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus])


class TestCpfCalculateAnnualChange1(object):
    """Tests the `calculate_annual_change()` method in cpf.py.

    Focuses on interest calculation across different CPF account thresholds.
    Variable here is the original CPF account balances, age is kept fixed.

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

    age = 25
    salary = 4000
    bonus = 10000

    # helper function
    def _add_monthly_contribution(self, oa, sa, ma, month):
        # 0.6217, 0.1621. 0.2162 of contribution (approx. 23%, 6%, 8% of $4000/$14000)
        cont_oa, cont_sa, cont_ma = (920.13, 239.9, 319.97)
        cont_oa_bonus, cont_sa_bonus, cont_ma_bonus = (3220.42, 839.67, 1119.91)
        
        if month == 12: # month is December
            oa += cont_oa_bonus
            sa += cont_sa_bonus
            ma += cont_ma_bonus
        else:
            oa += cont_oa
            sa += cont_sa
            ma += cont_ma

        return oa, sa, ma
    
    def _perform_assertion(self, balance_orig, balance_exp):
        """
        Helper class to perform assertion checks.

        Args:
            balance_orig (list): Original balance in CPF accounts [OA, SA, MA]
            balance_exp (list): Expected balance in CPF accounts [OA, SA, MA]
        """

        results_annual = cpfhelpers.calculate_annual_change(
                            self.salary * 12, self.bonus,
                            balance_orig[0], balance_orig[1], balance_orig[2], 
                            age=self.age)

        assert str(round(balance_exp[0], 2)) == results_annual[strings.KEY_OA]
        assert str(round(balance_exp[1], 2)) == results_annual[strings.KEY_SA]
        assert str(round(balance_exp[2], 2)) == results_annual[strings.KEY_MA]

    def test_scenario_1(self):
        print('Test scenario 1: OA < $20k, OA+SA+MA < $60k')
        oa, sa, ma = (6000, 2000, 3000)
        int_oa, int_sa, int_ma = (0, 0, 0)

        # OA: 3.5%
        # SA: 5%
        # MA: 5%
        for i in range(1, 13):
            oa, sa, ma = self._add_monthly_contribution(oa, sa, ma, i)
            # add interest in this month
            int_oa += oa * (0.025 / 12)
            int_sa += min(oa, 20000) * (0.01 / 12)
            int_sa += sa * (0.05 / 12)
            int_ma += ma * (0.05 / 12)
        
        self._perform_assertion([6000, 2000, 3000], [oa + int_oa, sa + int_sa, ma + int_ma])

    def test_scenario_2(self):
        print('Test scenario 2: OA > $20k, $20k+SA+MA < $60k')
        oa, sa, ma = (35000, 2000, 3000)
        int_oa, int_sa, int_ma = (0, 0, 0)

        # OA (up to $20k): 3.5%, OA (after $20k): 2.5%
        # SA: 5%
        # MA: 5%
        for i in range(1, 13):
            oa, sa, ma = self._add_monthly_contribution(oa, sa, ma, i)
            # add interest in this month
            int_oa += oa * (0.025 / 12)
            int_sa += min(oa, 20000) * (0.01 / 12)
            int_sa += sa * (0.05 / 12)
            int_ma += ma * (0.05 / 12)
        
        self._perform_assertion([35000, 2000, 3000], [oa + int_oa, sa + int_sa, ma + int_ma])

    def test_scenario_3(self):
        print('Test scenario 3: OA < $20k, OA+SA < $60k, OA+SA+MA > $60k')
        oa, sa, ma = (6000, 30000, 30000)
        int_oa, int_sa, int_ma = (0, 0, 0)

        # OA: 3.5%
        # SA: 5%
        # MA (for greatest MA value where $20k+SA+MA <= $60k): 5%, MA (remaining): 4%
        for i in range(1, 13):
            oa, sa, ma = self._add_monthly_contribution(oa, sa, ma, i)
            # add interest in this month
            int_oa += oa * (0.025 / 12)
            int_sa += min(oa, 20000) * (0.01 / 12)
            int_sa += sa * (0.05 / 12)
            amount_ma_eligible_for_extra_int = 60000 - oa - sa
            int_ma += amount_ma_eligible_for_extra_int * (0.05 / 12)
            int_ma += (ma - amount_ma_eligible_for_extra_int) * (0.04 / 12)
  
        self._perform_assertion([6000, 30000, 30000], [oa + int_oa, sa + int_sa, ma + int_ma])      

    def test_scenario_4(self):
        print('Test scenario 4: OA < $20k, OA+SA > $60k after a few months')
        oa, sa, ma = (6000, 40000, 30000)
        int_oa, int_sa, int_ma = (0, 0, 0)

        # OA: 3.5%
        # SA (for greatest SA value where OA+SA <= $60k): 5%, SA (remaining): 4%
        # MA (for greatest MA value where OA+SA+MA <= $60k): 5%, MA (remaining): 4%
        for i in range(1, 13):
            oa, sa, ma = self._add_monthly_contribution(oa, sa, ma, i)
            # add interest in this month
            int_oa += oa * (0.025 / 12)
            int_sa += min(oa, 20000) * (0.01 / 12)
            amount_sa_eligible_for_extra_int = 60000 - oa

            if sa > amount_sa_eligible_for_extra_int:
                int_sa += amount_sa_eligible_for_extra_int * (0.05 / 12)
                int_sa += (sa - amount_sa_eligible_for_extra_int) * (0.04 / 12)
            else:
                int_sa += sa * (0.05 / 12)

            amount_ma_eligible_for_extra_int = max(0, amount_sa_eligible_for_extra_int - sa)
            int_ma += amount_ma_eligible_for_extra_int * (0.05 / 12)
            int_ma += (ma - amount_ma_eligible_for_extra_int) * (0.04 / 12)

        self._perform_assertion([6000, 40000, 30000], [oa + int_oa, sa + int_sa, ma + int_ma])      


    def test_scenario_5(self):
        print('Test scenario 5: OA > $20k, $20k+SA > $60k, $20k+SA+MA > $60k')
        oa, sa, ma = (25000, 45000, 30000)
        int_oa, int_sa, int_ma = (0, 0, 0)

        # OA (up to $20k): 3.5%, OA (after $20k): 2.5%
        # SA (for greatest SA value where $20k+SA <= $60k): 5%, SA (remaining): 4%
        # MA: 4%
        for i in range(1, 13):
            oa, sa, ma = self._add_monthly_contribution(oa, sa, ma, i)
            # add interest in this month
            int_oa += oa * (0.025 / 12)
            int_sa += min(oa, 20000) * (0.01 / 12)
            amount_sa_eligible_for_extra_int = 60000 - 20000
            int_sa += amount_sa_eligible_for_extra_int * (0.05 / 12)
            int_sa += (sa - amount_sa_eligible_for_extra_int) * (0.04 / 12)
            int_ma += ma * (0.04 / 12)

        self._perform_assertion([25000, 45000, 30000], [oa + int_oa, sa + int_sa, ma + int_ma])      

    def test_scenario_6(self):
        print('Test scenario 6: OA > $20k, $20k+SA < $60k, $20k+SA+MA > $60k')
        oa, sa, ma = (25000, 30000, 30000)
        int_oa, int_sa, int_ma = (0, 0, 0)

        # OA (up to $20k): 3.5%, OA (after $20k): 2.5%
        # SA: 5%
        # MA (for greatest MA value where $20k+SA+MA <= $60k): 5%, MA (remaining): 4%
        for i in range(1, 13):
            oa, sa, ma = self._add_monthly_contribution(oa, sa, ma, i)
            # add interest in this month
            int_oa += oa * (0.025 / 12)
            int_sa += min(oa, 20000) * (0.01 / 12)
            int_sa += sa * (0.05 / 12)
            amount_ma_eligible_for_extra_int = 60000 -  20000 - sa
            int_ma += amount_ma_eligible_for_extra_int * (0.05 / 12)
            int_ma += (ma - amount_ma_eligible_for_extra_int) * (0.04 / 12)
        
        self._perform_assertion([25000, 30000, 30000], [oa + int_oa, sa + int_sa, ma + int_ma])      

    def test_scenario_7(self):
        print('Test scenario 7: OA > $20k after a few years, OA+SA+MA < $60k')
        oa, sa, ma = (15000, 5000, 5000)
        int_oa, int_sa, int_ma = (0, 0, 0)

        # OA (up to $20k): 3.5%, OA (after $20k): 2.5%
        # SA: 5%
        # MA: 5%
        for i in range(1, 13):
            oa, sa, ma = self._add_monthly_contribution(oa, sa, ma, i)
            
            int_oa += oa * (0.025 / 12)
            int_sa += min(oa, 20000) * (0.01 / 12)
            int_sa += sa * (0.05 / 12)
            int_ma += ma * (0.05 / 12)
        
        self._perform_assertion([15000, 5000, 5000], [oa + int_oa, sa + int_sa, ma + int_ma])      

    def test_scenario_8(self):
        print('Test scenario 8: OA > $20k after a few years, OA+SA+MA > $60k after a few years')
        oa, sa, ma = (18000, 39000, 5000)
        int_oa, int_sa, int_ma = (0, 0, 0)

        # OA (up to $20k): 3.5%, OA (after $20k): 2.5%
        # SA (for greatest SA value where $20k+SA <= $60k): 5%, SA (remaining): 4%
        # MA (for greatest MA value where $20k+SA+MA <= $60k): 5%, MA (remaining): 4%
        for i in range(1, 13):
            oa, sa, ma = self._add_monthly_contribution(oa, sa, ma, i)
            # add interest in this month
            int_oa += oa * (0.025 / 12)
            int_sa += min(oa, 20000) * (0.01 / 12)

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
   
        self._perform_assertion([18000, 39000, 5000], [oa + int_oa, sa + int_sa, ma + int_ma])      


class TestCpfCalculateAnnualChange2(object):
    """Tests the `calculate_annual_change()` method in cpf.py.

    Focuses on cases where the age bracket changes during the year.
    Original CPF account balances are fixed here, corresponding to test scenario 1 in 
    TestCpfCalculateAnnualChange1.

    Test scenarios:
    1. Age 35 -> 36
    2. Age 45 -> 46
    3. Age 50 -> 51
    """

    salary = 4000
    bonus = 10000
    date_start = dt.date(dt.date.today().year, 1, 1)
    
    def _add_monthly_contribution(self, oa, sa, ma, cont_oa, cont_sa, cont_ma):
        oa += cont_oa
        sa += cont_sa
        ma += cont_ma

        return oa, sa, ma

    def _add_monthly_interest(self, oa, sa, ma, int_oa, int_sa, int_ma):
        int_oa += oa * (0.025 / 12)
        int_sa += min(oa, 20000) * (0.01 / 12)
        int_sa += sa * (0.05 / 12)
        int_ma += ma * (0.05 / 12)

        return int_oa, int_sa, int_ma

    def _perform_assertion(self, balance_orig, balance_exp, dob):
        """
        Helper class to perform assertion checks.

        Args:
            balance_orig (array): Original balance in CPF accounts [OA, SA, MA]
            balance_exp (array): Expected balance in CPF accounts [OA, SA, MA]
        """

        results_annual = cpfhelpers.calculate_annual_change(
                            self.salary * 12, self.bonus,
                            balance_orig[0], balance_orig[1], balance_orig[2],
                            date_start=self.date_start, dob=dob)

        assert str(round(balance_exp[0], 2)) == results_annual[strings.KEY_OA]
        assert str(round(balance_exp[1], 2)) == results_annual[strings.KEY_SA]
        assert str(round(balance_exp[2], 2)) == results_annual[strings.KEY_MA]

    def test_scenario_1(self):
        print('Test scenario 1: Age 35 -> 36')

        oa, sa, ma = (6000, 2000, 3000)
        cont_oa_under35, cont_sa_under35, cont_ma_under35 = (920.13, 239.9, 319.97)
        cont_oa_over35, cont_sa_over35, cont_ma_over35 = (840.21, 279.86, 359.93)
        # calculated based on age=36
        cont_oa_bonus, cont_sa_bonus, cont_ma_bonus = (2940.7, 979.53, 1259.77)

        dob = str(dt.date.today().year - 35) + '06' # default month to June
        int_oa, int_sa, int_ma = (0, 0, 0)

        for i in range(1, 13):
            if i <= 6:
                oa, sa, ma = self._add_monthly_contribution(oa, sa, ma,
                                                            cont_oa_under35, cont_sa_under35, cont_ma_under35)
            elif i == 12:
                oa, sa, ma = self._add_monthly_contribution(oa, sa, ma,
                                                            cont_oa_bonus, cont_sa_bonus, cont_ma_bonus)
            else:
                oa, sa, ma = self._add_monthly_contribution(oa, sa, ma,
                                                            cont_oa_over35, cont_sa_over35, cont_ma_over35)

            # add interest in this month
            int_oa, int_sa, int_ma = self._add_monthly_interest(oa, sa, ma, int_oa, int_sa, int_ma)
        
        self._perform_assertion([6000, 2000, 3000], [oa + int_oa, sa + int_sa, ma + int_ma], dob)
    
    def test_scenario_2(self):
        print('Test scenario 2: Age 45 -> 46')

        oa, sa, ma = (6000, 2000, 3000)
        cont_oa_under45, cont_sa_under45, cont_ma_under45 = (840.21, 279.86, 359.93)
        cont_oa_over45, cont_sa_over45, cont_ma_over45 = (760.14, 319.97, 399.89)
        # calculated based on age=46
        cont_oa_bonus, cont_sa_bonus, cont_ma_bonus = (2660.46, 1119.91, 1399.63)

        dob = str(dt.date.today().year - 45) + '06' # default month to June
        int_oa, int_sa, int_ma = (0, 0, 0)

        for i in range(1, 13):
            if i <= 6:
                oa, sa, ma = self._add_monthly_contribution(oa, sa, ma,
                                                            cont_oa_under45, cont_sa_under45, cont_ma_under45)
            elif i == 12:
                oa, sa, ma = self._add_monthly_contribution(oa, sa, ma,
                                                            cont_oa_bonus, cont_sa_bonus, cont_ma_bonus)
            else:
                oa, sa, ma = self._add_monthly_contribution(oa, sa, ma,
                                                            cont_oa_over45, cont_sa_over45, cont_ma_over45)

            # add interest in this month
            int_oa, int_sa, int_ma = self._add_monthly_interest(oa, sa, ma, int_oa, int_sa, int_ma)
        
        self._perform_assertion([6000, 2000, 3000], [oa + int_oa, sa + int_sa, ma + int_ma], dob)
    
    def test_scenario_3(self):
        print('Test scenario 3: Age 50 -> 51')

        oa, sa, ma = (6000, 2000, 3000)
        cont_oa_under50, cont_sa_under50, cont_ma_under50 = (760.14, 319.97, 399.89)
        cont_oa_over50, cont_sa_over50, cont_ma_over50 = (600.15, 459.98, 419.87)
        # calculated based on age=51
        cont_oa_bonus, cont_sa_bonus, cont_ma_bonus = (2100.5, 1609.94, 1469.56)

        dob = str(dt.date.today().year - 50) + '06' # default month to June
        int_oa, int_sa, int_ma = (0, 0, 0)

        for i in range(1, 13):
            if i <= 6:
                oa, sa, ma = self._add_monthly_contribution(oa, sa, ma,
                                                            cont_oa_under50, cont_sa_under50, cont_ma_under50)
            elif i == 12:
                oa, sa, ma = self._add_monthly_contribution(oa, sa, ma,
                                                            cont_oa_bonus, cont_sa_bonus, cont_ma_bonus)
            else:
                oa, sa, ma = self._add_monthly_contribution(oa, sa, ma,
                                                            cont_oa_over50, cont_sa_over50, cont_ma_over50)

            # add interest in this month
            int_oa, int_sa, int_ma = self._add_monthly_interest(oa, sa, ma, int_oa, int_sa, int_ma)
        
        self._perform_assertion([6000, 2000, 3000], [oa + int_oa, sa + int_sa, ma + int_ma], dob)


class TestCpfCalculateAnnualChange3(object):
    """Tests the `calculate_annual_change()` method in cpf.py.

    Focuses on cases where there are changes in withdrawals/topups from the OA/SA respectively
    in the year.
    Original CPF account balances are fixed here, corresponding to test scenario 1 in 
    TestCpfCalculateAnnualChange1.

    Test scenarios:
    1. Topup OA
    2. Withdraw from OA
    3. Topup SA via cash
    4. Topup SA via OA
    5. Withdraw from SA
    6. Topup MA
    7. Withdraw from MA
    """

    salary, bonus = (4000, 10000)
    age = 25
    base_cpf = [6000, 2000, 3000]
    date_start = dt.date(dt.date.today().year, 1, 1)
    # standardise the month where the topup/withdrawal occurs
    delta_month = 5
    # standardise the topup/withdrawal amount too
    delta_amount = 1000

    def _add_monthly_contribution(self, oa, sa, ma, month):
        # 0.6217, 0.1621. 0.2162 of contribution (approx. 23%, 6%, 8% of $4000/$14000)
        cont_oa, cont_sa, cont_ma = (920.13, 239.9, 319.97)
        cont_oa_bonus, cont_sa_bonus, cont_ma_bonus = (3220.42, 839.67, 1119.91)
        
        if month == 12: # month is December
            oa += cont_oa_bonus
            sa += cont_sa_bonus
            ma += cont_ma_bonus
        else:
            oa += cont_oa
            sa += cont_sa
            ma += cont_ma

        return oa, sa, ma
    

    def _add_monthly_interest(self, oa, sa, ma, int_oa, int_sa, int_ma):
        int_oa += oa * (0.025 / 12)
        int_sa += min(oa, 20000) * (0.01 / 12)
        int_sa += sa * (0.05 / 12)
        int_ma += ma * (0.05 / 12)

        return int_oa, int_sa, int_ma

    def _perform_assertion(self, balance_orig, balance_exp, account_deltas):
        """
        Helper class to perform assertion checks.

        Args:
            balance_orig (array): Original balance in CPF accounts [OA, SA, MA]
            balance_exp (array): Expected balance in CPF accounts [OA, SA, MA]
        """

        results_annual = cpfhelpers.calculate_annual_change(
                                        self.salary * 12, self.bonus,
                                        balance_orig[0], balance_orig[1], balance_orig[2],
                                        account_deltas=account_deltas,
                                        date_start=self.date_start, age=self.age)

        assert str(round(balance_exp[0], 2)) == results_annual[strings.KEY_OA]
        assert str(round(balance_exp[1], 2)) == results_annual[strings.KEY_SA]
        assert str(round(balance_exp[2], 2)) == results_annual[strings.KEY_MA]

    def test_scenario_1(self):
        print('Test scenario 1: Topup OA')
        
        oa, sa, ma = (6000, 2000, 3000)
        int_oa, int_sa, int_ma = (0, 0, 0)

        for i in range(1, 13):
            oa, sa, ma = self._add_monthly_contribution(oa, sa, ma, i)
            if i == self.delta_month:
                oa += self.delta_amount

            # add interest in this month
            int_oa, int_sa, int_ma = self._add_monthly_interest(oa, sa, ma, int_oa, int_sa, int_ma)
        
        oa_topups = { self.delta_month: { 'amount': self.delta_amount } }
        account_deltas = {
            'oa_topups': oa_topups,
            'oa_withdrawals': {},
            'sa_topups': {},
            'sa_withdrawals': {},
            'ma_topups': {},
            'ma_withdrawals': {}
        }
        self._perform_assertion([6000, 2000, 3000], [oa + int_oa, sa + int_sa, ma + int_ma], account_deltas)

    def test_scenario_2(self):
        print('Test scenario 2: Withdraw from OA')
        
        oa, sa, ma = (6000, 2000, 3000)
        int_oa, int_sa, int_ma = (0, 0, 0)

        for i in range(1, 13):
            oa, sa, ma = self._add_monthly_contribution(oa, sa, ma, i)
            if i == self.delta_month:
                oa -= self.delta_amount

            # add interest in this month
            int_oa, int_sa, int_ma = self._add_monthly_interest(oa, sa, ma, int_oa, int_sa, int_ma)
        
        oa_withdrawals = { self.delta_month: { 'amount': self.delta_amount } }
        account_deltas = {
            'oa_topups': {},
            'oa_withdrawals': oa_withdrawals,
            'sa_topups': {},
            'sa_withdrawals': {},
            'ma_topups': {},
            'ma_withdrawals': {}
        }
        self._perform_assertion([6000, 2000, 3000], [oa + int_oa, sa + int_sa, ma + int_ma], account_deltas)

    def test_scenario_3(self):
        print('Test scenario 3: Topup SA via cash')
        
        oa, sa, ma = (6000, 2000, 3000)
        int_oa, int_sa, int_ma = (0, 0, 0)

        for i in range(1, 13):
            oa, sa, ma = self._add_monthly_contribution(oa, sa, ma, i)
            if i == self.delta_month:
                sa += self.delta_amount

            # add interest in this month
            int_oa, int_sa, int_ma = self._add_monthly_interest(oa, sa, ma, int_oa, int_sa, int_ma)
        
        sa_topups = { self.delta_month: { 'amount': self.delta_amount, 'is_sa_topup_from_oa': False } }
        account_deltas = {
            'oa_topups': {},
            'oa_withdrawals': {},
            'sa_topups': sa_topups,
            'sa_withdrawals': {},
            'ma_topups': {},
            'ma_withdrawals': {}
        }
        self._perform_assertion([6000, 2000, 3000], [oa + int_oa, sa + int_sa, ma + int_ma], account_deltas)

    def test_scenario_4(self):
        print('Test scenario 4: Topup SA via OA')
        
        oa, sa, ma = (6000, 2000, 3000)
        int_oa, int_sa, int_ma = (0, 0, 0)

        for i in range(1, 13):
            oa, sa, ma = self._add_monthly_contribution(oa, sa, ma, i)
            if i == self.delta_month:
                sa += self.delta_amount
                oa -= self.delta_amount

            # add interest in this month
            int_oa, int_sa, int_ma = self._add_monthly_interest(oa, sa, ma, int_oa, int_sa, int_ma)
        
        sa_topups = { self.delta_month: { 'amount': self.delta_amount, 'is_sa_topup_from_oa': True } }
        account_deltas = {
            'oa_topups': {},
            'oa_withdrawals': {},
            'sa_topups': sa_topups,
            'sa_withdrawals': {},
            'ma_topups': {},
            'ma_withdrawals': {}
        }
        self._perform_assertion([6000, 2000, 3000], [oa + int_oa, sa + int_sa, ma + int_ma], account_deltas)

    def test_scenario_5(self):
        print('Test scenario 5: Withdraw from SA')
        
        oa, sa, ma = (6000, 2000, 3000)
        int_oa, int_sa, int_ma = (0, 0, 0)

        for i in range(1, 13):
            oa, sa, ma = self._add_monthly_contribution(oa, sa, ma, i)
            if i == self.delta_month:
                sa -= self.delta_amount

            # add interest in this month
            int_oa, int_sa, int_ma = self._add_monthly_interest(oa, sa, ma, int_oa, int_sa, int_ma)
        
        sa_withdrawals = { self.delta_month: { 'amount': self.delta_amount } }
        account_deltas = {
            'oa_topups': {},
            'oa_withdrawals': {},
            'sa_topups': {},
            'sa_withdrawals': sa_withdrawals,
            'ma_topups': {},
            'ma_withdrawals': {}
        }
        self._perform_assertion([6000, 2000, 3000], [oa + int_oa, sa + int_sa, ma + int_ma], account_deltas)

    def test_scenario_6(self):
        print('Test scenario 6: Topup MA')
        
        oa, sa, ma = (6000, 2000, 3000)
        int_oa, int_sa, int_ma = (0, 0, 0)

        for i in range(1, 13):
            oa, sa, ma = self._add_monthly_contribution(oa, sa, ma, i)
            if i == self.delta_month:
                ma += self.delta_amount

            # add interest in this month
            int_oa, int_sa, int_ma = self._add_monthly_interest(oa, sa, ma, int_oa, int_sa, int_ma)
        
        ma_topups = { self.delta_month: { 'amount': self.delta_amount } }
        account_deltas = {
            'oa_topups': {},
            'oa_withdrawals': {},
            'sa_topups': {},
            'sa_withdrawals': {},
            'ma_topups': ma_topups,
            'ma_withdrawals': {}
        }
        self._perform_assertion([6000, 2000, 3000], [oa + int_oa, sa + int_sa, ma + int_ma], account_deltas)

    def test_scenario_7(self):
        print('Test scenario 7: Withdraw from MA')
        
        oa, sa, ma = (6000, 2000, 3000)
        int_oa, int_sa, int_ma = (0, 0, 0)

        for i in range(1, 13):
            oa, sa, ma = self._add_monthly_contribution(oa, sa, ma, i)
            if i == self.delta_month:
                ma -= self.delta_amount

            # add interest in this month
            int_oa, int_sa, int_ma = self._add_monthly_interest(oa, sa, ma, int_oa, int_sa, int_ma)
        
        ma_withdrawals = { self.delta_month: { 'amount': self.delta_amount } }
        account_deltas = {
            'oa_topups': {},
            'oa_withdrawals': {},
            'sa_topups': {},
            'sa_withdrawals': {},
            'ma_topups': {},
            'ma_withdrawals': ma_withdrawals
        }
        self._perform_assertion([6000, 2000, 3000], [oa + int_oa, sa + int_sa, ma + int_ma], account_deltas)