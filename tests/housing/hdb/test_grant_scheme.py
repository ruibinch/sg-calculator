from logic.housing.hdb import constants, hdbhelpers
from utils import strings

class TestGrantSchemeBeforeSep2019New(object):
    """

    For applications of BTO flats that were received before Sep 2019.

    Test scenarios (divided by applicant profile):

    1. Both FT, mature estate, income <=$5k
    2. Both FT, mature estate, income >$5k
    3. Both FT, non-mature estate (2/3/4rm), income <=$5k
    4. Both FT, non-mature estate (2/3/4rm), income >$5k & <=$8.5k
    5. Both FT, non-mature estate (2/3/4rm), income >$8.5k
    6. Both FT, non-mature estate (5rm/3gen/exec), income <=$5k
    7. Both FT, non-mature estate (5rm/3gen/exec), income >$5k
    8. FT/ST, mature estate, income <=$5k
    9. FT/ST, mature estate, income >$5k
    10. FT/ST, non-mature estate (2/3/4rm), income <=$5k
    11. FT/ST, non-mature estate (2/3/4rm), income >$8.5k
    12. FT/ST, non-mature estate (2/3/4rm), income >$5k & <=$8.5k
    13. FT/ST, non-mature estate (5rm/3gen/exec), income <=$5k
    14. FT/ST, non-mature estate (5rm/3gen/exec), income >$5k
    15. Both ST, non-mature estate (3rm), income <=$7k
    16. Both ST, non-mature estate (3rm), income >$7k
    17. Both ST, non-mature estate (any except 3rm), income <=$7k
    18. Both ST, mature estate (3rm), income <=$7k

    """

    def _perform_assertion(self,
                           profile: str,
                           estate: str,
                           income: float,
                           exp_result: dict,
                           flat_size: str = None):
        valid_schemes = hdbhelpers.find_grant_schemes_prev_bto(
            profile, income, estate, flat_size)
        for scheme in exp_result:
            assert scheme in valid_schemes
            assert valid_schemes[scheme] == exp_result[scheme]

    def test_both_ft_1(self):
        profile = constants.PROFILE_BOTH_FT
        estate = strings.MATURE
        income = 5000
        exp_result = {
            constants.GRANT_AHG: {
                strings.ELIGIBILITY: True,
                strings.REMARKS: None,
            },
            constants.GRANT_SHG: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_SHG_MATURE_ESTATE_NA,
            },
        }
        self._perform_assertion(profile, estate, income, exp_result)

    def test_both_ft_2(self):
        profile = constants.PROFILE_BOTH_FT
        estate = strings.MATURE
        income = 5001
        exp_result = {
            constants.GRANT_AHG: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_AHG_INCOME_ABOVE,
            },
            constants.GRANT_SHG: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_SHG_MATURE_ESTATE_NA,
            },
        }
        self._perform_assertion(profile, estate, income, exp_result)
        
    def test_both_ft_3(self):
        profile = constants.PROFILE_BOTH_FT
        estate = strings.NONMATURE
        flat_size = constants.SIZE_4RM
        income = 5000
        exp_result = {
            constants.GRANT_AHG: {
                strings.ELIGIBILITY: True,
                strings.REMARKS: None,
            },
            constants.GRANT_SHG: {
                strings.ELIGIBILITY: True,
                strings.REMARKS: None,
            },
        }
        self._perform_assertion(profile, estate, income, exp_result, flat_size=flat_size)

    def test_both_ft_4(self):
        profile = constants.PROFILE_BOTH_FT
        estate = strings.NONMATURE
        flat_size = constants.SIZE_4RM
        income = 5001
        exp_result = {
            constants.GRANT_AHG: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_AHG_INCOME_ABOVE,
            },
            constants.GRANT_SHG: {
                strings.ELIGIBILITY: True,
                strings.REMARKS: None,
            },
        }
        self._perform_assertion(profile, estate, income, exp_result, flat_size=flat_size)

    def test_both_ft_5(self):
        profile = constants.PROFILE_BOTH_FT
        estate = strings.NONMATURE
        flat_size = constants.SIZE_4RM
        income = 8501
        exp_result = {
            constants.GRANT_AHG: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_AHG_INCOME_ABOVE,
            },
            constants.GRANT_SHG: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_SHG_INCOME_ABOVE,
            },
        }
        self._perform_assertion(profile, estate, income, exp_result, flat_size=flat_size)
    
    def test_both_ft_6(self):
        profile = constants.PROFILE_BOTH_FT
        estate = strings.NONMATURE
        flat_size = constants.SIZE_5RM
        income = 5000
        exp_result = {
            constants.GRANT_AHG: {
                strings.ELIGIBILITY: True,
                strings.REMARKS: None,
            },
            constants.GRANT_SHG: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_SHG_FLAT_SIZE_NA,
            },
        }
        self._perform_assertion(profile, estate, income, exp_result, flat_size=flat_size)
           
    def test_both_ft_7(self):
        profile = constants.PROFILE_BOTH_FT
        estate = strings.NONMATURE
        flat_size = constants.SIZE_5RM
        income = 5001
        exp_result = {
            constants.GRANT_AHG: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_AHG_INCOME_ABOVE,
            },
            constants.GRANT_SHG: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_SHG_FLAT_SIZE_NA,
            },
        }
        self._perform_assertion(profile, estate, income, exp_result, flat_size=flat_size)

    # def test_ft_st_8(self):
    #     profile = constants.PROFILE_BOTH_FT
    #     estate = strings.MATURE
    #     income = 5000
    #     exp_result = [constants.GRANT_AHG_SINGLES]

    # def test_ft_st_9(self):
    #     profile = constants.PROFILE_BOTH_FT
    #     estate = strings.MATURE
    #     income = 5001
    #     exp_result = []
        
    # def test_ft_st_10(self):
    #     profile = constants.PROFILE_BOTH_FT
    #     estate = strings.NONMATURE
    #     flat_size = constants.SIZE_4RM
    #     income = 5000
    #     exp_result = [constants.GRANT_AHG_SINGLES, constants.GRANT_SHG_SINGLES]

    # def test_ft_st_11(self):
    #     profile = constants.PROFILE_BOTH_FT
    #     estate = strings.NONMATURE
    #     flat_size = constants.SIZE_4RM
    #     income = 5001
    #     exp_result = [constants.GRANT_SHG_SINGLES]

    # def test_ft_st_12(self):
    #     profile = constants.PROFILE_BOTH_FT
    #     estate = strings.NONMATURE
    #     flat_size = constants.SIZE_4RM
    #     income = 8501
    #     exp_result = []
    
    # def test_ft_st_13(self):
    #     profile = constants.PROFILE_BOTH_FT
    #     estate = strings.NONMATURE
    #     flat_size = constants.SIZE_5RM
    #     income = 5000
    #     exp_result = [constants.GRANT_AHG_SINGLES]
           
    # def test_ft_st_14(self):
    #     profile = constants.PROFILE_BOTH_FT
    #     estate = strings.NONMATURE
    #     flat_size = constants.SIZE_5RM
    #     income = 5001
    #     exp_result = []
           
    # def test_both_st_15(self):
    #     profile = constants.PROFILE_BOTH_ST
    #     estate = strings.NONMATURE
    #     flat_size = constants.SIZE_3RM
    #     income = 7000
    #     exp_result = [constants.GRANT_STEPUP]
           
    # def test_both_st_16(self):
    #     profile = constants.PROFILE_BOTH_ST
    #     estate = strings.NONMATURE
    #     flat_size = constants.SIZE_3RM
    #     income = 7001
    #     exp_result = []
           
    # def test_both_st_17(self):
    #     profile = constants.PROFILE_BOTH_ST
    #     estate = strings.NONMATURE
    #     flat_size = constants.SIZE_4RM
    #     income = 7000
    #     exp_result = []
    
    # def test_both_st_18(self):
    #     profile = constants.PROFILE_BOTH_ST
    #     estate = strings.MATURE
    #     flat_size = constants.SIZE_3RM
    #     income = 7000
    #     exp_result = []


class TestGrantSchemeBeforeSep2019Resale(object):
    """

    For applications of resale flats that were received before Sep 2019.
    """

class TestGrantSchemeSep2019OnwardsNew(object):
    """

    For applications of BTO flats that were received from Sep 2019 onwards.
    
    Test scenarios:
    1. Both FT, income <=$9k
    2. Both FT, income >$9k 
    3. FT/ST, income <=$9k
    4. FT/ST, income >$9k
    5. Both ST, non-mature estate (2rm), income <=$7k
    6. Both ST, non-mature estate (3rm), income <=$7k
    7. Both ST, non-mature estate (2rm), income >$7k
    8. Both ST, non-mature estate (3rm), income >$7k
    9. Both ST, non-mature estate (any except 2rm/3rm), income <=$7k
    10. Both ST, mature estate (2rm), income <=$7k
    11. Both ST, mature estate (3rm), income <=$7k
    12. Non-SC spouse, income <=$9k
    13. Non-SC spouse, income >$9k
    """

    def _perform_assertion(self,
                           profile: str,
                           income: float,
                           exp_result: dict):
        valid_schemes = hdbhelpers.find_grant_schemes_curr_bto(profile, income)
        for scheme in exp_result:
            assert scheme in valid_schemes
            assert valid_schemes[scheme] == exp_result[scheme]

    def test_both_ft_1(self):
        profile = constants.PROFILE_BOTH_FT
        income = 9000
        exp_result = {
            constants.GRANT_EHG: {
                strings.ELIGIBILITY: True,
                strings.REMARKS: None,
            }
        }
        self._perform_assertion(profile, income, exp_result)

    def test_both_ft_2(self):
        profile = constants.PROFILE_BOTH_FT
        income = 9001
        exp_result = {
            constants.GRANT_EHG: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_EHG_INCOME_ABOVE,
            }
        }
        self._perform_assertion(profile, income, exp_result)

    # def test_ft_st_3(self):
    #     profile = constants.PROFILE_FT_ST
    #     income = 9000
    #     exp_result = [constants.GRANT_EHG_SINGLES]
    #     self._perform_assertion(profile, income, exp_result)

    # def test_ft_st_4(self):
    #     profile = constants.PROFILE_FT_ST
    #     income = 9001
    #     exp_result = []
    #     self._perform_assertion(profile, income, exp_result)

    # def test_both_st_5(self):
    #     profile = constants.PROFILE_BOTH_ST
    #     estate = strings.NONMATURE
    #     flat_size = constants.SIZE_2RM
    #     income = 7000
    #     exp_result = [constants.GRANT_STEPUP]
    #     self._perform_assertion(profile, income, exp_result)

    # def test_both_st_6(self):
    #     profile = constants.PROFILE_BOTH_ST
    #     estate = strings.NONMATURE
    #     flat_size = constants.SIZE_3RM
    #     income = 7000
    #     exp_result = [constants.GRANT_STEPUP]
    #     self._perform_assertion(profile, income, exp_result)

    # def test_both_st_7(self):
    #     profile = constants.PROFILE_BOTH_ST
    #     estate = strings.NONMATURE
    #     flat_size = constants.SIZE_2RM
    #     income = 7001
    #     exp_result = []
    #     self._perform_assertion(profile, income, exp_result)

    # def test_both_st_8(self):
    #     profile = constants.PROFILE_BOTH_ST
    #     estate = strings.NONMATURE
    #     flat_size = constants.SIZE_3RM
    #     income = 7001
    #     exp_result = []
    #     self._perform_assertion(profile, income, exp_result)

    # def test_both_st_9(self):
    #     profile = constants.PROFILE_BOTH_ST
    #     estate = strings.NONMATURE
    #     flat_size = constants.SIZE_4RM
    #     income = 7000
    #     exp_result = []
    #     self._perform_assertion(profile, income, exp_result)

    # def test_both_st_10(self):
    #     profile = constants.PROFILE_BOTH_ST
    #     estate = strings.MATURE
    #     flat_size = constants.SIZE_2RM
    #     income = 7000
    #     exp_result = []
    #     self._perform_assertion(profile, income, exp_result)

    # def test_both_st_11(self):
    #     profile = constants.PROFILE_BOTH_ST
    #     estate = strings.MATURE
    #     flat_size = constants.SIZE_3RM
    #     income = 7000
    #     exp_result = []
    #     self._perform_assertion(profile, income, exp_result)

    # def test_nonsc_spouse_12(self):
    #     profile = constants.PROFILE_NONSC_SPOUSE
    #     income = 9000
    #     exp_result = [constants.GRANT_EHG_SINGLES]
    #     self._perform_assertion(profile, income, exp_result)

    # def test_nonsc_spouse_13(self):
    #     profile = constants.PROFILE_NONSC_SPOUSE
    #     income = 9001
    #     exp_result = []
    #     self._perform_assertion(profile, income, exp_result)

class TestGrantSchemeSep2019OnwardsResale(object):
    """

    For applications of resale flats that were received from Sep 2019 onwards.
    """
