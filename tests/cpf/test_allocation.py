from typing import Tuple

from logic.cpf.main import calc_cpf_allocation
from logic.cpf import cpfhelpers, genhelpers
from utils import strings

class TestCalcCpfAllocation(object):
    """Tests the `calc_cpf_allocation()` method in cpf.py.
   
    Assumption: `calc_cpf_contribution()` method is correct.

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
    bonus = 2.5     # i.e. $10k

    def _get_contribution_amount_by_age(self, age: int) -> float:
        """Returns the total contribution amount for both with-bonus and without-bonus scenarios."""

        cont_with_bonus = cpfhelpers._get_monthly_contribution_amount(self.salary, self.bonus, age=age, entity=strings.COMBINED)
        cont_wo_bonus = cpfhelpers._get_monthly_contribution_amount(self.salary, 0, age=age, entity=strings.COMBINED)
        return cont_with_bonus, cont_wo_bonus

    def _get_alloc_amount(self,
                          cont: float,
                          sa_ratio: float,
                          ma_ratio: float) -> Tuple[float, float, float]:
        """Given a total contribution amount and the MA/SA contribution ratios,
        return the annual allocation amounts into all 3 accounts."""

        sa_alloc = genhelpers._truncate(sa_ratio * cont)
        ma_alloc = genhelpers._truncate(ma_ratio * cont)
        oa_alloc = cont - sa_alloc - ma_alloc
        return round(oa_alloc * 12, 2), round(sa_alloc * 12, 2), round(ma_alloc * 12, 2)

    def _perform_assertions(self,
                           age: int,
                           alloc_with_bonus_exp: list,
                           alloc_wo_bonus_exp: list):
        """
        Helper class to perform assertion checks.
        Round the values to 2 decimal places when checking for equality.

        Args:
            bonus (float): Bonus/commission received in the year
            age (int): Age of employee
            alloc_exp (list): Expected amount to be allocated into the CPF accounts [OA, SA, MA]
        """
        
        # with bonus
        allocations = calc_cpf_allocation(self.salary * 12, self.bonus, None, age=age)
        assert alloc_with_bonus_exp[0] == float(allocations[strings.VALUES][strings.OA])
        assert alloc_with_bonus_exp[1] == float(allocations[strings.VALUES][strings.SA])
        assert alloc_with_bonus_exp[2] == float(allocations[strings.VALUES][strings.MA])

        # without bonus
        allocations = calc_cpf_allocation(self.salary * 12, 0, None, age=age)
        assert alloc_wo_bonus_exp[0] == float(allocations[strings.VALUES][strings.OA])
        assert alloc_wo_bonus_exp[1] == float(allocations[strings.VALUES][strings.SA])
        assert alloc_wo_bonus_exp[2] == float(allocations[strings.VALUES][strings.MA])

    def test_calc_cpf_allocation_1(self):
        age = 35
        cont_with_bonus, cont_wo_bonus = self._get_contribution_amount_by_age(age)
        oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus = self._get_alloc_amount(cont_with_bonus, 0.1621, 0.2162)
        oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus = self._get_alloc_amount(cont_wo_bonus, 0.1621, 0.2162)

        self._perform_assertions(age,
                                 [oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus],
                                 [oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus]
                                )
    
    def test_calc_cpf_allocation_2(self):
        age = 45
        cont_with_bonus, cont_wo_bonus = self._get_contribution_amount_by_age(age)
        oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus = self._get_alloc_amount(cont_with_bonus, 0.1891, 0.2432)
        oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus = self._get_alloc_amount(cont_wo_bonus, 0.1891, 0.2432)

        self._perform_assertions(age,
                                 [oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus],
                                 [oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus]
                                )

    def test_calc_cpf_allocation_3(self):
        age = 50
        cont_with_bonus, cont_wo_bonus = self._get_contribution_amount_by_age(age)
        oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus = self._get_alloc_amount(cont_with_bonus, 0.2162, 0.2702)
        oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus = self._get_alloc_amount(cont_wo_bonus, 0.2162, 0.2702)

        self._perform_assertions(age,
                                 [oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus],
                                 [oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus]
                                )

    def test_calc_cpf_allocation_4(self):
        age = 55
        cont_with_bonus, cont_wo_bonus = self._get_contribution_amount_by_age(age)
        oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus = self._get_alloc_amount(cont_with_bonus, 0.3108, 0.2837)
        oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus = self._get_alloc_amount(cont_wo_bonus, 0.3108, 0.2837)

        self._perform_assertions(age,
                                 [oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus],
                                 [oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus]
                                )
    
    def test_calc_cpf_allocation_5(self):
        age = 60
        cont_with_bonus, cont_wo_bonus = self._get_contribution_amount_by_age(age)
        oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus = self._get_alloc_amount(cont_with_bonus, 0.1346, 0.4038)
        oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus = self._get_alloc_amount(cont_wo_bonus, 0.1346, 0.4038)

        self._perform_assertions(age,
                                 [oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus],
                                 [oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus]
                                )

    def test_calc_cpf_allocation_6(self):
        age = 65
        cont_with_bonus, cont_wo_bonus = self._get_contribution_amount_by_age(age)
        oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus = self._get_alloc_amount(cont_with_bonus, 0.1515, 0.6363)
        oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus = self._get_alloc_amount(cont_wo_bonus, 0.1515, 0.6363)

        self._perform_assertions(age,
                                 [oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus],
                                 [oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus]
                                )

    def test_calc_cpf_allocation_7(self):
        age = 80
        cont_with_bonus, cont_wo_bonus = self._get_contribution_amount_by_age(age)
        oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus = self._get_alloc_amount(cont_with_bonus, 0.08, 0.84)
        oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus = self._get_alloc_amount(cont_wo_bonus, 0.08, 0.84)

        self._perform_assertions(age,
                                 [oa_alloc_with_bonus, sa_alloc_with_bonus, ma_alloc_with_bonus],
                                 [oa_alloc_wo_bonus, sa_alloc_wo_bonus, ma_alloc_wo_bonus]
                                )
