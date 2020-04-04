from logic.cpf.main import calculate_cpf_contribution
from utils import strings

class TestCalculateCpfContribution(object):
    """Tests the `calculate_cpf_contribution()` method in cpf/main.py.

    Test scenarios: 
    1. Age <=55
        a. Salary <=$50/month
        b. Salary >$50 to <=$500/month
        c. Salary >$500 to <$750/month
        d. Salary >=$750/month and below OW Ceiling, bonus below AW Ceiling
        e. Salary >=$750/month and below OW Ceiling, bonus above AW Ceiling
        f. Salary >=$750/month and above OW Ceiling, bonus below AW Ceiling
        g. Salary >=$750/month and above OW Ceiling, bonus above AW Ceiling
    """

    def _perform_assertion(self,
                           salary: float,
                           bonus: float,
                           age: int,
                           cont_employee: float,
                           cont_employer: float):
        contributions = calculate_cpf_contribution(salary, bonus, None, strings.YEAR, age=age)
        assert round(cont_employee, 2) == float(contributions[strings.VALUES][strings.CONT_EMPLOYEE])
        assert round(cont_employer, 2) == float(contributions[strings.VALUES][strings.CONT_EMPLOYER])

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
        # salary: $48k; bonus: $20k
        salary, bonus, age = (4000 * 12, 5, 30)
        bonus_amount = 4000 * bonus
        cont_total = (0.37 * salary) + (0.37 * bonus_amount)
        cont_employee = (0.2 * salary) + (0.2 * bonus_amount)
        cont_employer = cont_total - cont_employee
        self._perform_assertion(salary, bonus, age, cont_employee, cont_employer)

    def test_scenario_1e(self):
        # salary: $48k; bonus: $100k
        salary, bonus, age = (4000 * 12, 25, 30)
        cont_total = (0.37 * salary) + (0.37 * (102000 - salary))
        cont_employee = (0.2 * salary) + (0.2 * (102000 - salary))
        cont_employer = cont_total - cont_employee
        self._perform_assertion(salary, bonus, age, cont_employee, cont_employer)

    def test_scenario_1f(self):
        # salary: $96k; bonus: $20k
        salary, bonus, age = (8000 * 12, 2.5, 30)
        bonus_amount = 8000 * bonus
        cont_total = (0.37 * 72000) + (0.37 * bonus_amount)
        cont_employee = (0.2 * 72000) + (0.2 * bonus_amount)
        cont_employer = cont_total - cont_employee
        self._perform_assertion(salary, bonus, age, cont_employee, cont_employer)

    def test_scenario_1g(self):
        # salary: $96k; bonus: $100k
        salary, bonus, age = (8000 * 12, 8.5, 30)
        cont_total = (0.37 * 72000) + (0.37 * (102000 - 72000))
        cont_employee = (0.2 * 72000) + (0.2 * (102000 - 72000))
        cont_employer = cont_total - cont_employee
        self._perform_assertion(salary, bonus, age, cont_employee, cont_employer)
