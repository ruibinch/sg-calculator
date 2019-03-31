import logic.cpf_constants as constants
import logic.cpf as cpf

class TestCpfCalculateAnnualChange(object):
    """
    Tests the `calculate_annual_change()` method in cpf.py.

    Test scenarios:
        1. OA < $20k, OA+SA+MA < $60k
        2. OA > $20k, $20k+SA+MA < $60k
        3. OA < $20k, OA+SA < $60k, OA+SA+MA > $60k
        4. OA > $20k, $20k+SA > $60k, $20k+SA+MA > $60k
        5. OA > $20k, $20k+SA < $60k, $20k+SA+MA > $60k
        6. OA < $20k but OA > $20k after a few months, OA+SA+MA < $60k
        7. OA < $20k but OA > $20k after a few months, OA+SA < $60k but OA+SA > $60k after a few months
    """

    # Class variables
    #   age: immaterial here - for convenience, standardise to age 25
    #   income: standardise to $4k
    global age, salary, cont_oa, cont_sa, cont_ma
    age = 25
    salary = 4000
    cont_oa, cont_sa, cont_ma = (920, 240, 320) # 23%, 6%, 8% of $4000

    # helper function
    def add_monthly_contribution(self, oa, sa, ma):
        oa += cont_oa
        sa += cont_sa
        ma += cont_ma
        return oa, sa, ma
    

    def test_scenario_1(self):
        print('Test scenario 1: OA < $20k, OA+SA+MA < $60k')
        oa, sa, ma = (6000, 2000, 3000)
        int_oa, int_sa, int_ma = (0, 0, 0)

        # OA: 3.5%
        # SA: 5%
        # MA: 5%
        for i in range(1, 13):
            oa, sa, ma = self.add_monthly_contribution(oa, sa, ma)
            # add interest in this month
            int_oa += oa * (0.035 / 12)
            int_sa += sa * (0.05 / 12)
            int_ma += ma * (0.05 / 12)
        
        oa_test, sa_test, ma_test = cpf.calculate_annual_change(
                                        age, salary, 6000, 2000, 3000)
                        
        assert oa + int_oa == oa_test
        assert sa + int_sa == sa_test
        assert ma + int_ma == ma_test


    def test_scenario_2(self):
        print('Test scenario 2: OA > $20k, $20k+SA+MA < $60k')
        oa, sa, ma = (35000, 2000, 3000)
        int_oa, int_sa, int_ma = (0, 0, 0)

        # OA (up to $20k): 3.5%, OA (after $20k): 2.5%
        # SA: 5%
        # MA: 5%
        for i in range(1, 13):
            oa, sa, ma = self.add_monthly_contribution(oa, sa, ma)
            # add interest in this month
            int_oa += 20000 * (0.035 / 12)
            int_oa += (oa - 20000) * (0.025 / 12)
            int_sa += sa * (0.05 / 12)
            int_ma += ma * (0.05 / 12)
        
        oa_test, sa_test, ma_test = cpf.calculate_annual_change(
                                        age, salary, 35000, 2000, 3000)
                        
        assert oa + int_oa == oa_test
        assert sa + int_sa == sa_test
        assert ma + int_ma == ma_test
        

    def test_scenario_3(self):
        print('Test scenario 3: OA < $20k, OA+SA < $60k, OA+SA+MA > $60k')
        oa, sa, ma = (6000, 40000, 30000)
        int_oa, int_sa, int_ma = (0, 0, 0)

        # OA: 3.5%
        # SA: 5%
        # MA (for greatest MA value where $20k+SA+MA <= $60k): 5%, MA (remaining): 4%
        for i in range(1, 13):
            oa, sa, ma = self.add_monthly_contribution(oa, sa, ma)
            # add interest in this month
            int_oa += oa * (0.035 / 12)
            int_sa += sa * (0.05 / 12)
            amount_ma_eligible_for_extra_int = 60000 - oa - sa
            int_ma += amount_ma_eligible_for_extra_int * (0.05 / 12)
            int_ma += (ma - amount_ma_eligible_for_extra_int) * (0.04 / 12)
        
        oa_test, sa_test, ma_test = cpf.calculate_annual_change(
                                        age, salary, 6000, 40000, 30000)
                        
        assert oa + int_oa == oa_test
        assert sa + int_sa == sa_test
        assert ma + int_ma == ma_test
        

    def test_scenario_4(self):
        print('Test scenario 4: OA > $20k, $20k+SA > $60k, $20k+SA+MA > $60k')
        oa, sa, ma = (25000, 45000, 30000)
        int_oa, int_sa, int_ma = (0, 0, 0)

        # OA (up to $20k): 3.5%, OA (after $20k): 2.5%
        # SA (for greatest SA value where $20k+SA <= $60k): 5%, SA (remaining): 4%
        # MA: 4%
        for i in range(1, 13):
            oa, sa, ma = self.add_monthly_contribution(oa, sa, ma)
            # add interest in this month
            int_oa += 20000 * (0.035 / 12)
            int_oa += (oa - 20000) * (0.025 / 12)
            amount_sa_eligible_for_extra_int = 60000 - 20000
            int_sa += amount_sa_eligible_for_extra_int * (0.05 / 12)
            int_sa += (sa - amount_sa_eligible_for_extra_int) * (0.04 / 12)
            int_ma += ma * (0.04 / 12)
        
        oa_test, sa_test, ma_test = cpf.calculate_annual_change(
                                        age, salary, 25000, 45000, 30000)

        assert oa + int_oa == oa_test
        assert sa + int_sa == sa_test
        assert ma + int_ma == ma_test
               

    def test_scenario_5(self):
        print('Test scenario 5: OA > $20k, $20k+SA < $60k, $20k+SA+MA > $60k')
        oa, sa, ma = (25000, 30000, 30000)
        int_oa, int_sa, int_ma = (0, 0, 0)

        # OA (up to $20k): 3.5%, OA (after $20k): 2.5%
        # SA: 5%
        # MA (for greatest MA value where $20k+SA+MA <= $60k): 5%, MA (remaining): 4%
        for i in range(1, 13):
            oa, sa, ma = self.add_monthly_contribution(oa, sa, ma)
            # add interest in this month
            int_oa += 20000 * (0.035 / 12)
            int_oa += (oa - 20000) * (0.025 / 12)
            int_sa += sa * (0.05 / 12)
            amount_ma_eligible_for_extra_int = 60000 -  20000 - sa
            int_ma += amount_ma_eligible_for_extra_int * (0.05 / 12)
            int_ma += (ma - amount_ma_eligible_for_extra_int) * (0.04 / 12)
        
        oa_test, sa_test, ma_test = cpf.calculate_annual_change(
                                        age, salary, 25000, 30000, 30000)
        
        assert oa + int_oa == oa_test
        assert sa + int_sa == sa_test
        assert ma + int_ma == ma_test 
        

    def test_scenario_6(self):
        print('Test scenario 6: OA < $20k but OA > $20k after a few years, OA+SA+MA < $60k')
        oa, sa, ma = (15000, 5000, 5000)
        int_oa, int_sa, int_ma = (0, 0, 0)

        # OA (up to $20k): 3.5%, OA (after $20k): 2.5%
        # SA: 5%
        # MA: 5%
        for i in range(1, 13):
            oa, sa, ma = self.add_monthly_contribution(oa, sa, ma)
            # add interest in this month
            if oa <= 20000:
                int_oa += oa * (0.035 / 12)
            else:
                int_oa += 20000 * (0.035 / 12)
                int_oa += (oa - 20000) * (0.025 / 12)

            int_sa += sa * (0.05 / 12)
            int_ma += ma * (0.05 / 12)
        
        oa_test, sa_test, ma_test = cpf.calculate_annual_change(
                                        age, salary, 15000, 5000, 5000)
                        
        assert oa + int_oa == oa_test
        assert sa + int_sa == sa_test
        assert ma + int_ma == ma_test

        
    def test_scenario_7(self):
        print('Test scenario 7: OA < $20k but OA > $20k after a few years, \
                OA+SA+MA < $60k but OA+SA+MA > $60k after a few years')
        oa, sa, ma = (18000, 39000, 5000)
        int_oa, int_sa, int_ma = (0, 0, 0)

        # OA (up to $20k): 3.5%, OA (after $20k): 2.5%
        # SA (for greatest SA value where $20k+SA <= $60k): 5%, SA (remaining): 4%
        # MA (for greatest MA value where $20k+SA+MA <= $60k): 5%, MA (remaining): 4%
        for i in range(1, 13):
            oa, sa, ma = self.add_monthly_contribution(oa, sa, ma)
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
            
        oa_test, sa_test, ma_test = cpf.calculate_annual_change(
                                        age, salary, 18000, 39000, 5000)
                        
        assert oa + int_oa == oa_test
        assert sa + int_sa == sa_test
        assert ma + int_ma == ma_test
        

class TestCpfCalculateFutureCpfBalance(object):
    """
    Tests the `calculate_future_cpf_balance()` method in cpf.py.

    """

    def test_scenario_1(self):
        print('Test scenario 1: age=25, salary=4000, yoy_increase=0.05, n_years=1')
        print('Test scenario 1: Base CPF amounts are equal to scenario 1 in TestCpfCalculateAnnualChange')
        
        # only calculate for 1 year

        oa, sa, ma = (6000, 2000, 3000)
        oa_cont, sa_cont, ma_cont = (1150, 300, 400) # 23%, 6%, 8% of $5000
        int_oa, int_sa, int_ma = (0, 0, 0)
        # OA: 3.5%
        # SA: 5%
        # MA: 5%
        for i in range(1, 13):
            oa += oa_cont
            sa += sa_cont
            ma += ma_cont
            # add interest in this month
            int_oa += oa * (0.035 / 12)
            int_sa += sa * (0.05 / 12)
            int_ma += ma * (0.05 / 12)
        
        oa += int_oa
        sa += int_sa
        ma += int_ma
        
        base_cpf = { 'oa': 6000, 'sa': 2000, 'ma': 3000}
        oa_test, sa_test, ma_test = cpf.calculate_future_cpf_balance(
                                        25, 5000, 0.05, base_cpf, 1)
                        
        assert oa == oa_test
        assert sa == sa_test
        assert ma == ma_test