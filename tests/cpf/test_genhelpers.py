import datetime as dt

from logic.cpf import genhelpers
from utils import strings

class TestAge(object):
    """Tests the `_get_age()` method in genhelpers.py."""

    dob = '198502'

    def test_age_1(self):
        date_curr = dt.datetime(2020, 1, 1) # Jan 2020
        assert genhelpers._get_age(self.dob, date_curr) == 35
        
    def test_age_2(self):
        date_curr = dt.datetime(2020, 2, 1) # Feb 2020
        assert genhelpers._get_age(self.dob, date_curr) == 35
        
    def test_age_3(self):
        date_curr = dt.datetime(2020, 3, 1) # Mar 2020
        assert genhelpers._get_age(self.dob, date_curr) == 36


class TestDecompressAccountDeltas(object):
    """Tests the `_decompress_account_deltas()` method in genhelpers.py."""

    def test_decompress_account_deltas_1(self):
        deltas = [
            {
                strings.TYPE: strings.OA_TOPUP,
                strings.PERIOD: '202006',
                strings.AMOUNT: '10000',
                strings.RECURRENCE: {
                    strings.FREQUENCY: strings.ANNUALLY,
                    strings.DURATION: '5',
                },
            },
        ]

        decompressed_deltas = [
            {strings.TYPE: strings.OA_TOPUP, strings.PERIOD: '202006', strings.AMOUNT: '10000'},
            {strings.TYPE: strings.OA_TOPUP, strings.PERIOD: '202106', strings.AMOUNT: '10000'},
            {strings.TYPE: strings.OA_TOPUP, strings.PERIOD: '202206', strings.AMOUNT: '10000'},
            {strings.TYPE: strings.OA_TOPUP, strings.PERIOD: '202306', strings.AMOUNT: '10000'},
            {strings.TYPE: strings.OA_TOPUP, strings.PERIOD: '202406', strings.AMOUNT: '10000'},
        ]

        assert genhelpers._decompress_account_deltas(deltas) == decompressed_deltas

    def test_decompress_account_deltas_2(self):
        deltas = [
            {
                strings.TYPE: strings.OA_WITHDRAWAL,
                strings.PERIOD: '202101',
                strings.AMOUNT: '5000',
                strings.RECURRENCE: {
                    strings.FREQUENCY: strings.MONTHLY,
                    strings.DURATION: '6',
                },
            },
        ]

        decompressed_deltas = [
            {strings.TYPE: strings.OA_WITHDRAWAL, strings.PERIOD: '202101', strings.AMOUNT: '5000'},
            {strings.TYPE: strings.OA_WITHDRAWAL, strings.PERIOD: '202102', strings.AMOUNT: '5000'},
            {strings.TYPE: strings.OA_WITHDRAWAL, strings.PERIOD: '202103', strings.AMOUNT: '5000'},
            {strings.TYPE: strings.OA_WITHDRAWAL, strings.PERIOD: '202104', strings.AMOUNT: '5000'},
            {strings.TYPE: strings.OA_WITHDRAWAL, strings.PERIOD: '202105', strings.AMOUNT: '5000'},
            {strings.TYPE: strings.OA_WITHDRAWAL, strings.PERIOD: '202106', strings.AMOUNT: '5000'},
        ]

        assert genhelpers._decompress_account_deltas(deltas) == decompressed_deltas

    def test_decompress_account_deltas_3(self):
        deltas = [
            {
                strings.TYPE: strings.SA_TOPUP,
                strings.PERIOD: '202201',
                strings.AMOUNT: '10000',
                strings.IS_SA_TOPUP_FROM_OA: True,
                strings.RECURRENCE: {
                    strings.FREQUENCY: strings.ANNUALLY,
                    strings.DURATION: '3',
                },
            },
        ]

        decompressed_deltas = [
            {strings.TYPE: strings.SA_TOPUP, strings.PERIOD: '202201', strings.AMOUNT: '10000', strings.IS_SA_TOPUP_FROM_OA: True},
            {strings.TYPE: strings.SA_TOPUP, strings.PERIOD: '202301', strings.AMOUNT: '10000', strings.IS_SA_TOPUP_FROM_OA: True},
            {strings.TYPE: strings.SA_TOPUP, strings.PERIOD: '202401', strings.AMOUNT: '10000', strings.IS_SA_TOPUP_FROM_OA: True},
        ]

        assert genhelpers._decompress_account_deltas(deltas) == decompressed_deltas


class TestExtractAccountDeltas(object):
    """Tests the `_extract_account_deltas()` method in genhelpers.py."""

    def test_extract_account_deltas_1(self):
        deltas = [
            {strings.TYPE: strings.OA_WITHDRAWAL, strings.PERIOD: '202201', strings.AMOUNT: '3000'},
        ]

        assert genhelpers._extract_account_deltas(deltas) == (-3000, 0, 0)

    def test_extract_account_deltas_2(self):
        deltas = [
            {strings.TYPE: strings.OA_WITHDRAWAL, strings.PERIOD: '202201', strings.AMOUNT: '3000'},
            {strings.TYPE: strings.MA_WITHDRAWAL, strings.PERIOD: '202201', strings.AMOUNT: '1000'},
        ]

        assert genhelpers._extract_account_deltas(deltas) == (-3000, 0, -1000)

    def test_extract_account_deltas_3(self):
        deltas = [
            {strings.TYPE: strings.SA_TOPUP, strings.PERIOD: '202201', strings.AMOUNT: '8000', strings.IS_SA_TOPUP_FROM_OA: True},
        ]

        assert genhelpers._extract_account_deltas(deltas) == (-8000, 8000, 0)


class TestIncrementPeriod(object):
    """Tests the `_increment_period()` method in genhelpers.py."""

    period = '202001'

    def _perform_assertion(self,
                           add_years: int,
                           add_months: int,
                           exp_result: str):
        
        result = genhelpers._increment_period(
            self.period,
            add_years=add_years,
            add_months=add_months)
        assert result == exp_result

    def test_increment_period_1(self):
        years, months = 1, 0
        self._perform_assertion(years, months, '202101')
        
    def test_increment_period_2(self):
        years, months = 10, 0
        self._perform_assertion(years, months, '203001')

    def test_increment_period_3(self):
        years, months = 0, 11
        self._perform_assertion(years, months, '202012')
        
    def test_increment_period_4(self):
        years, months = 0, 12
        self._perform_assertion(years, months, '202101')

    def test_increment_period_5(self):
        years, months = 0, 360
        self._perform_assertion(years, months, '205001')
        
    def test_increment_period_6(self):
        years, months = 5, 11
        self._perform_assertion(years, months, '202512')
        
    def test_increment_period_7(self):
        years, months = 10, 100
        self._perform_assertion(years, months, '203805')
    