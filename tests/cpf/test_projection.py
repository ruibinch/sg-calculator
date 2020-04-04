import datetime as dt
from typing import Tuple

from logic.cpf.main import calculate_cpf_projection
from logic.cpf import constants, cpfhelpers, genhelpers
from utils import strings

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
    bonus = 2.5

    # helper function
    def _add_monthly_contribution(self,
                                  oa: float,
                                  sa: float,
                                  ma: float,
                                  month: int) -> Tuple[float, float, float]:
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
    
    def _perform_assertion(self,
                           balance_orig: list,
                           balance_exp: list):
        """
        Helper class to perform assertion checks.

        Args:
            balance_orig (list): Original balance in CPF accounts [OA, SA, MA]
            balance_exp (list): Expected balance in CPF accounts [OA, SA, MA]
        """

        results_annual = cpfhelpers.calculate_annual_change(
                            self.salary * 12,
                            self.bonus,
                            balance_orig[0],
                            balance_orig[1],
                            balance_orig[2], 
                            age=self.age)

        assert str(round(balance_exp[0], 2)) == results_annual[strings.OA]
        assert str(round(balance_exp[1], 2)) == results_annual[strings.SA]
        assert str(round(balance_exp[2], 2)) == results_annual[strings.MA]

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
    bonus = 2.5
    date_start = dt.date(dt.date.today().year, 1, 1)
    
    def _add_monthly_contribution(self,
                                  oa: float,
                                  sa: float,
                                  ma: float,
                                  cont_oa: float,
                                  cont_sa: float,
                                  cont_ma: float) -> Tuple[float, float, float]:
        oa += cont_oa
        sa += cont_sa
        ma += cont_ma

        return oa, sa, ma

    def _add_monthly_interest(self,
                              oa: float,
                              sa: float,
                              ma: float,
                              int_oa: float,
                              int_sa: float,
                              int_ma: float) -> Tuple[float, float, float]:
        int_oa += oa * (0.025 / 12)
        int_sa += min(oa, 20000) * (0.01 / 12)
        int_sa += sa * (0.05 / 12)
        int_ma += ma * (0.05 / 12)

        return int_oa, int_sa, int_ma

    def _perform_assertion(self,
                           balance_orig: list,
                           balance_exp: list,
                           dob: str):
        """
        Helper class to perform assertion checks.

        Args:
            balance_orig (list): Original balance in CPF accounts [OA, SA, MA]
            balance_exp (list): Expected balance in CPF accounts [OA, SA, MA]
        """

        results_annual = cpfhelpers.calculate_annual_change(
                            self.salary * 12, self.bonus,
                            balance_orig[0], balance_orig[1], balance_orig[2],
                            date_start=self.date_start, dob=dob)

        assert str(round(balance_exp[0], 2)) == results_annual[strings.OA]
        assert str(round(balance_exp[1], 2)) == results_annual[strings.SA]
        assert str(round(balance_exp[2], 2)) == results_annual[strings.MA]

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

    salary, bonus = (4000, 2.5)
    age = 25
    base_cpf = [6000, 2000, 3000]
    date_start = dt.date(dt.date.today().year, 1, 1)
    # standardise the month where the topup/withdrawal occurs
    delta_month = 5
    # standardise the topup/withdrawal amount too
    delta_amount = 1000

    def _add_monthly_contribution(self,
                                  oa: float,
                                  sa: float,
                                  ma: float,
                                  month: int) -> Tuple[float, float, float]:
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
    
    def _add_monthly_interest(self,
                              oa: float,
                              sa: float,
                              ma: float,
                              int_oa: float,
                              int_sa: float,
                              int_ma: float) -> Tuple[float, float, float]:
        int_oa += oa * (0.025 / 12)
        int_sa += min(oa, 20000) * (0.01 / 12)
        int_sa += sa * (0.05 / 12)
        int_ma += ma * (0.05 / 12)

        return int_oa, int_sa, int_ma

    def _perform_assertion(self,
                           balance_orig: list,
                           balance_exp: list,
                           account_deltas: dict):
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

        assert str(round(balance_exp[0], 2)) == results_annual[strings.OA]
        assert str(round(balance_exp[1], 2)) == results_annual[strings.SA]
        assert str(round(balance_exp[2], 2)) == results_annual[strings.MA]

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
        
        oa_topups = { self.delta_month: { strings.AMOUNT: self.delta_amount } }
        account_deltas = {
            strings.PARAM_OA_TOPUPS: oa_topups,
            strings.PARAM_OA_WITHDRAWALS: {},
            strings.PARAM_SA_TOPUPS: {},
            strings.PARAM_SA_WITHDRAWALS: {},
            strings.PARAM_MA_TOPUPS: {},
            strings.PARAM_MA_WITHDRAWALS: {}
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
        
        oa_withdrawals = { self.delta_month: { strings.AMOUNT: self.delta_amount } }
        account_deltas = {
            strings.PARAM_OA_TOPUPS: {},
            strings.PARAM_OA_WITHDRAWALS: oa_withdrawals,
            strings.PARAM_SA_TOPUPS: {},
            strings.PARAM_SA_WITHDRAWALS: {},
            strings.PARAM_MA_TOPUPS: {},
            strings.PARAM_MA_WITHDRAWALS: {}
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
        
        sa_topups = { self.delta_month: { strings.AMOUNT: self.delta_amount, strings.IS_SA_TOPUP_FROM_OA: False } }
        account_deltas = {
            strings.PARAM_OA_TOPUPS: {},
            strings.PARAM_OA_WITHDRAWALS: {},
            strings.PARAM_SA_TOPUPS: sa_topups,
            strings.PARAM_SA_WITHDRAWALS: {},
            strings.PARAM_MA_TOPUPS: {},
            strings.PARAM_MA_WITHDRAWALS: {}
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
        
        sa_topups = { self.delta_month: { strings.AMOUNT: self.delta_amount, strings.IS_SA_TOPUP_FROM_OA: True } }
        account_deltas = {
            strings.PARAM_OA_TOPUPS: {},
            strings.PARAM_OA_WITHDRAWALS: {},
            strings.PARAM_SA_TOPUPS: sa_topups,
            strings.PARAM_SA_WITHDRAWALS: {},
            strings.PARAM_MA_TOPUPS: {},
            strings.PARAM_MA_WITHDRAWALS: {}
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
        
        sa_withdrawals = { self.delta_month: { strings.AMOUNT: self.delta_amount } }
        account_deltas = {  
            strings.PARAM_OA_TOPUPS: {},
            strings.PARAM_OA_WITHDRAWALS: {},
            strings.PARAM_SA_TOPUPS: {},
            strings.PARAM_SA_WITHDRAWALS: sa_withdrawals,
            strings.PARAM_MA_TOPUPS: {},
            strings.PARAM_MA_WITHDRAWALS: {}
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
        
        ma_topups = { self.delta_month: { strings.AMOUNT: self.delta_amount } }
        account_deltas = {
            strings.PARAM_OA_TOPUPS: {},
            strings.PARAM_OA_WITHDRAWALS: {},
            strings.PARAM_SA_TOPUPS: {},
            strings.PARAM_SA_WITHDRAWALS: {},
            strings.PARAM_MA_TOPUPS: ma_topups,
            strings.PARAM_MA_WITHDRAWALS: {}
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
        
        ma_withdrawals = { self.delta_month: { strings.AMOUNT: self.delta_amount } }
        account_deltas = {
            strings.PARAM_OA_TOPUPS: {},
            strings.PARAM_OA_WITHDRAWALS: {},
            strings.PARAM_SA_TOPUPS: {},
            strings.PARAM_SA_WITHDRAWALS: {},
            strings.PARAM_MA_TOPUPS: {},
            strings.PARAM_MA_WITHDRAWALS: ma_withdrawals
        }
        self._perform_assertion([6000, 2000, 3000], [oa + int_oa, sa + int_sa, ma + int_ma], account_deltas)
