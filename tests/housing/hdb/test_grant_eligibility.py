from logic.housing.hdb import constants, hdb_grant_eligibility
from utils import strings

class TestGrantEligibilityPrevBto(object):
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
    11. FT/ST, non-mature estate (2/3/4rm), income >$5k & <=$8.5k
    12. FT/ST, non-mature estate (2/3/4rm), income >$8.5k
    13. FT/ST, non-mature estate (5rm/3gen/exec), income <=$5k
    14. FT/ST, non-mature estate (5rm/3gen/exec), income >$5k
    15. Both ST, non-mature estate (3rm), income <=$7k
    16. Both ST, non-mature estate (3rm), income >$7k
    17. Both ST, non-mature estate (any except 3rm), income <=$7k
    18. Both ST, mature estate (3rm), income <=$7k
    19. Non-SC spouse, mature estate, income <=$5k
    20. Non-SC spouse, non-mature estate (any except 2rm), income <=$5k
    21. Non-SC spouse, non-mature estate (2rm), income <=$5k
    22. Non-SC spouse, non-mature estate (2rm), income >$5k & <=$8.5k
    23. Non-SC spouse, non-mature estate (2rm), income >$8.5k
    24. SG single, mature estate, income <=$2.5k
    25. SG single, non-mature estate (any except 2rm), income <=$2.5k
    26. SG single, non-mature estate (2rm), income <=$2.5k
    27. SG single, non-mature estate (2rm), income >$2.5k & <=$4.25k
    28. SG single, non-mature estate (2rm), income >$4.25k
    29. SG JSS, mature estate, income <=$5k
    30. SG JSS, non-mature estate (any except 2rm), income <=$5k
    31. SG JSS, non-mature estate (2rm), income <=$5k
    32. SG JSS, non-mature estate (2rm), income >$5k & <=$8.5k
    33. SG JSS, non-mature estate (2rm), income >$8.5k
    34. SG orphan, mature estate, income <=$5k
    35. SG orphan, mature estate, income >$5k
    36. SG orphan, non-mature estate (2/3/4rm), income <=$5k
    37. SG orphan, non-mature estate (2/3/4rm), income >$5k & <=$8.5k
    38. SG orphan, non-mature estate (2/3/4rm), income >$8.5k
    39. SG orphan, non-mature estate (5rm/3gen/exec), income <=$5k
    40. SG orphan, non-mature estate (5rm/3gen/exec), income >$5k
    """

    def _perform_assertion(self,
                           profile: str,
                           estate: str,
                           income: float,
                           exp_result: dict,
                           flat_size: str = None):
        eligible_schemes = hdb_grant_eligibility.find_grant_schemes_prev_bto(
            profile, income, estate, flat_size)
        for scheme in exp_result:
            assert scheme in eligible_schemes
            assert eligible_schemes[scheme] == exp_result[scheme]

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
                strings.REMARKS: constants.REMARKS_GEN_MATURE_ESTATE_NA,
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
                strings.REMARKS: constants.REMARKS_GEN_MATURE_ESTATE_NA,
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

    def test_ft_st_8(self):
        profile = constants.PROFILE_FT_ST
        estate = strings.MATURE
        income = 5000
        exp_result = {
            constants.GRANT_AHG_SINGLES: {
                strings.ELIGIBILITY: True,
                strings.REMARKS: None,
            },
            constants.GRANT_SHG_SINGLES: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_GEN_MATURE_ESTATE_NA,
            },
        }
        self._perform_assertion(profile, estate, income, exp_result)

    def test_ft_st_9(self):
        profile = constants.PROFILE_FT_ST
        estate = strings.MATURE
        income = 5001
        exp_result = {
            constants.GRANT_AHG_SINGLES: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_AHG_SINGLES_INCOME_ABOVE,
            },
            constants.GRANT_SHG_SINGLES: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_GEN_MATURE_ESTATE_NA,
            },
        }
        self._perform_assertion(profile, estate, income, exp_result)
        
    def test_ft_st_10(self):
        profile = constants.PROFILE_FT_ST
        estate = strings.NONMATURE
        flat_size = constants.SIZE_4RM
        income = 5000
        exp_result = {
            constants.GRANT_AHG_SINGLES: {
                strings.ELIGIBILITY: True,
                strings.REMARKS: None,
            },
            constants.GRANT_SHG_SINGLES: {
                strings.ELIGIBILITY: True,
                strings.REMARKS: None,
            },
        }
        self._perform_assertion(profile, estate, income, exp_result, flat_size=flat_size)

    def test_ft_st_11(self):
        profile = constants.PROFILE_FT_ST
        estate = strings.NONMATURE
        flat_size = constants.SIZE_4RM
        income = 5001
        exp_result = {
            constants.GRANT_AHG_SINGLES: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_AHG_SINGLES_INCOME_ABOVE,
            },
            constants.GRANT_SHG_SINGLES: {
                strings.ELIGIBILITY: True,
                strings.REMARKS: None,
            },
        }
        self._perform_assertion(profile, estate, income, exp_result, flat_size=flat_size)

    def test_ft_st_12(self):
        profile = constants.PROFILE_FT_ST
        estate = strings.NONMATURE
        flat_size = constants.SIZE_4RM
        income = 8501
        exp_result = {
            constants.GRANT_AHG_SINGLES: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_AHG_SINGLES_INCOME_ABOVE,
            },
            constants.GRANT_SHG_SINGLES: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_SHG_SINGLES_INCOME_ABOVE,
            },
        }
        self._perform_assertion(profile, estate, income, exp_result, flat_size=flat_size)
    
    def test_ft_st_13(self):
        profile = constants.PROFILE_FT_ST
        estate = strings.NONMATURE
        flat_size = constants.SIZE_5RM
        income = 5000
        exp_result = {
            constants.GRANT_AHG_SINGLES: {
                strings.ELIGIBILITY: True,
                strings.REMARKS: None,
            },
            constants.GRANT_SHG_SINGLES: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_SHG_FLAT_SIZE_NA,
            },
        }
        self._perform_assertion(profile, estate, income, exp_result, flat_size=flat_size)
           
    def test_ft_st_14(self):
        profile = constants.PROFILE_FT_ST
        estate = strings.NONMATURE
        flat_size = constants.SIZE_5RM
        income = 5001
        exp_result = {
            constants.GRANT_AHG_SINGLES: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_AHG_SINGLES_INCOME_ABOVE,
            },
            constants.GRANT_SHG_SINGLES: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_SHG_FLAT_SIZE_NA,
            },
        }
        self._perform_assertion(profile, estate, income, exp_result, flat_size=flat_size)
           
    def test_both_st_15(self):
        profile = constants.PROFILE_BOTH_ST
        estate = strings.NONMATURE
        flat_size = constants.SIZE_3RM
        income = 7000
        exp_result = {
            constants.GRANT_STEPUP: {
                strings.ELIGIBILITY: True,
                strings.REMARKS: None,
            },
        }
        self._perform_assertion(profile, estate, income, exp_result, flat_size=flat_size)
           
    def test_both_st_16(self):
        profile = constants.PROFILE_BOTH_ST
        estate = strings.NONMATURE
        flat_size = constants.SIZE_3RM
        income = 7001
        exp_result = {
            constants.GRANT_STEPUP: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_STEPUP_INCOME_ABOVE,
            },
        }
        self._perform_assertion(profile, estate, income, exp_result, flat_size=flat_size)
           
    def test_both_st_17(self):
        profile = constants.PROFILE_BOTH_ST
        estate = strings.NONMATURE
        flat_size = constants.SIZE_4RM
        income = 7000
        exp_result = {
            constants.GRANT_STEPUP: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_STEPUP_FLAT_SIZE_NA_PREV,
            },
        }
        self._perform_assertion(profile, estate, income, exp_result, flat_size=flat_size)
    
    def test_both_st_18(self):
        profile = constants.PROFILE_BOTH_ST
        estate = strings.MATURE
        flat_size = constants.SIZE_3RM
        income = 7000
        exp_result = {
            constants.GRANT_STEPUP: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_GEN_MATURE_ESTATE_NA,
            },
        }
        self._perform_assertion(profile, estate, income, exp_result, flat_size=flat_size)

    def test_nonsc_spouse_19(self):
        profile = constants.PROFILE_NONSC_SPOUSE
        estate = strings.MATURE
        income = 5000
        exp_result = {
            constants.GRANT_AHG_SINGLES: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_GEN_MATURE_ESTATE_NA,
            },
            constants.GRANT_SHG_SINGLES: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_GEN_MATURE_ESTATE_NA,
            },
        }
        self._perform_assertion(profile, estate, income, exp_result)

    def test_nonsc_spouse_20(self):
        profile = constants.PROFILE_NONSC_SPOUSE
        estate = strings.NONMATURE
        income = 5000
        exp_result = {
            constants.GRANT_AHG_SINGLES: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_AHG_FLAT_SIZE_NA_2RM,
            },
            constants.GRANT_SHG_SINGLES: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_SHG_FLAT_SIZE_NA_2RM,
            },
        }
        self._perform_assertion(profile, estate, income, exp_result)
        
    def test_nonsc_spouse_21(self):
        profile = constants.PROFILE_NONSC_SPOUSE
        estate = strings.NONMATURE
        flat_size = constants.SIZE_2RM
        income = 5000
        exp_result = {
            constants.GRANT_AHG_SINGLES: {
                strings.ELIGIBILITY: True,
                strings.REMARKS: None,
            },
            constants.GRANT_SHG_SINGLES: {
                strings.ELIGIBILITY: True,
                strings.REMARKS: None,
            },
        }
        self._perform_assertion(profile, estate, income, exp_result, flat_size=flat_size)

    def test_nonsc_spouse_22(self):
        profile = constants.PROFILE_NONSC_SPOUSE
        estate = strings.NONMATURE
        flat_size = constants.SIZE_2RM
        income = 5001
        exp_result = {
            constants.GRANT_AHG_SINGLES: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_AHG_SINGLES_INCOME_ABOVE,
            },
            constants.GRANT_SHG_SINGLES: {
                strings.ELIGIBILITY: True,
                strings.REMARKS: None,
            },
        }
        self._perform_assertion(profile, estate, income, exp_result, flat_size=flat_size)

    def test_nonsc_spouse_23(self):
        profile = constants.PROFILE_NONSC_SPOUSE
        estate = strings.NONMATURE
        flat_size = constants.SIZE_2RM
        income = 8501
        exp_result = {
            constants.GRANT_AHG_SINGLES: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_AHG_SINGLES_INCOME_ABOVE,
            },
            constants.GRANT_SHG_SINGLES: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_SHG_SINGLES_INCOME_ABOVE,
            },
        }
        self._perform_assertion(profile, estate, income, exp_result, flat_size=flat_size)
           
    def test_sg_single_24(self):
        profile = constants.PROFILE_SG_SINGLE
        estate = strings.MATURE
        income = 2500
        exp_result = {
            constants.GRANT_AHG_SINGLES: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_GEN_MATURE_ESTATE_NA,
            },
            constants.GRANT_SHG_SINGLES: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_GEN_MATURE_ESTATE_NA,
            },
        }
        self._perform_assertion(profile, estate, income, exp_result)

    def test_sg_single_25(self):
        profile = constants.PROFILE_SG_SINGLE
        estate = strings.NONMATURE
        flat_size = constants.SIZE_3RM
        income = 2500
        exp_result = {
            constants.GRANT_AHG_SINGLES: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_AHG_FLAT_SIZE_NA_2RM,
            },
            constants.GRANT_SHG_SINGLES: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_SHG_FLAT_SIZE_NA_2RM,
            },
        }
        self._perform_assertion(profile, estate, income, exp_result)
        
    def test_sg_single_26(self):
        profile = constants.PROFILE_SG_SINGLE
        estate = strings.NONMATURE
        flat_size = constants.SIZE_2RM
        income = 2500
        exp_result = {
            constants.GRANT_AHG_SINGLES: {
                strings.ELIGIBILITY: True,
                strings.REMARKS: None,
            },
            constants.GRANT_SHG_SINGLES: {
                strings.ELIGIBILITY: True,
                strings.REMARKS: None,
            },
        }
        self._perform_assertion(profile, estate, income, exp_result, flat_size=flat_size)

    def test_sg_single_27(self):
        profile = constants.PROFILE_SG_SINGLE
        estate = strings.NONMATURE
        flat_size = constants.SIZE_2RM
        income = 2501
        exp_result = {
            constants.GRANT_AHG_SINGLES: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_AHG_SINGLES_INCOME_ABOVE_SINGLE,
            },
            constants.GRANT_SHG_SINGLES: {
                strings.ELIGIBILITY: True,
                strings.REMARKS: None,
            },
        }
        self._perform_assertion(profile, estate, income, exp_result, flat_size=flat_size)

    def test_sg_single_28(self):
        profile = constants.PROFILE_SG_SINGLE
        estate = strings.NONMATURE
        flat_size = constants.SIZE_2RM
        income = 4251
        exp_result = {
            constants.GRANT_AHG_SINGLES: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_AHG_SINGLES_INCOME_ABOVE_SINGLE,
            },
            constants.GRANT_SHG_SINGLES: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_SHG_SINGLES_INCOME_ABOVE_SINGLE,
            },
        }
        self._perform_assertion(profile, estate, income, exp_result, flat_size=flat_size)
           
    def test_sg_jss_29(self):
        profile = constants.PROFILE_SG_JSS
        estate = strings.MATURE
        income = 5000
        exp_result = {
            constants.GRANT_AHG: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_GEN_MATURE_ESTATE_NA,
            },
            constants.GRANT_SHG: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_GEN_MATURE_ESTATE_NA,
            },
        }
        self._perform_assertion(profile, estate, income, exp_result)

    def test_sg_jss_30(self):
        profile = constants.PROFILE_SG_JSS
        estate = strings.NONMATURE
        income = 5000
        flat_size = constants.SIZE_3RM
        exp_result = {
            constants.GRANT_AHG: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_AHG_FLAT_SIZE_NA_2RM,
            },
            constants.GRANT_SHG: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_SHG_FLAT_SIZE_NA_2RM,
            },
        }
        self._perform_assertion(profile, estate, income, exp_result, flat_size=flat_size)
        
    def test_sg_jss_31(self):
        profile = constants.PROFILE_SG_JSS
        estate = strings.NONMATURE
        flat_size = constants.SIZE_2RM
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

    def test_sg_jss_32(self):
        profile = constants.PROFILE_SG_JSS
        estate = strings.NONMATURE
        flat_size = constants.SIZE_2RM
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

    def test_sg_jss_33(self):
        profile = constants.PROFILE_SG_JSS
        estate = strings.NONMATURE
        flat_size = constants.SIZE_2RM
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
           
    def test_sg_orphan_34(self):
        profile = constants.PROFILE_SG_ORPHAN
        estate = strings.MATURE
        income = 5000
        exp_result = {
            constants.GRANT_AHG: {
                strings.ELIGIBILITY: True,
                strings.REMARKS: None,
            },
            constants.GRANT_SHG: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_GEN_MATURE_ESTATE_NA,
            },
        }
        self._perform_assertion(profile, estate, income, exp_result)

    def test_sg_orphan_35(self):
        profile = constants.PROFILE_SG_ORPHAN
        estate = strings.MATURE
        income = 5001
        exp_result = {
            constants.GRANT_AHG: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_AHG_INCOME_ABOVE,
            },
            constants.GRANT_SHG: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_GEN_MATURE_ESTATE_NA,
            },
        }
        self._perform_assertion(profile, estate, income, exp_result)
        
    def test_sg_orphan_36(self):
        profile = constants.PROFILE_SG_ORPHAN
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

    def test_sg_orphan_37(self):
        profile = constants.PROFILE_SG_ORPHAN
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

    def test_sg_orphan_38(self):
        profile = constants.PROFILE_SG_ORPHAN
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
    
    def test_sg_orphan_39(self):
        profile = constants.PROFILE_SG_ORPHAN
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
           
    def test_sg_orphan_40(self):
        profile = constants.PROFILE_SG_ORPHAN
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
           

class TestGrantEligibilityPrevResale(object):
    """

    For applications of resale flats that were received before Sep 2019.
    """

class TestGrantEligibilityCurrBto(object):
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
    14. SG single, income <=$4.5k
    15. SG single, income >$4.5k
    16. SG JSS, non-mature estate (2rm), income <=$9k
    17. SG JSS, non-mature estate (2rm), income >$9k
    18. SG JSS, non-mature estate (any except 2rm), income <=$9k
    19. SG JSS, mature estate (2rm), income <=$9k
    20. SG orphan, income <=$9k
    21. SG orphan, income >$9k
    """

    def _perform_assertion(self,
                           profile: str,
                           income: float,
                           exp_result: dict,
                           estate: str = None,
                           flat_size: str = None):
        eligible_schemes = hdb_grant_eligibility.find_grant_schemes_curr_bto(
            profile, income, estate, flat_size)
        for scheme in exp_result:
            assert scheme in eligible_schemes
            assert eligible_schemes[scheme] == exp_result[scheme]

    def test_both_ft_1(self):
        profile = constants.PROFILE_BOTH_FT
        income = 9000
        exp_result = {
            constants.GRANT_EHG: {
                strings.ELIGIBILITY: True,
                strings.REMARKS: None,
            },
        }
        self._perform_assertion(profile, income, exp_result)

    def test_both_ft_2(self):
        profile = constants.PROFILE_BOTH_FT
        income = 9001
        exp_result = {
            constants.GRANT_EHG: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_EHG_INCOME_ABOVE,
            },
        }
        self._perform_assertion(profile, income, exp_result)

    def test_ft_st_3(self):
        profile = constants.PROFILE_FT_ST
        income = 9000
        exp_result = {
            constants.GRANT_EHG_SINGLES: {
                strings.ELIGIBILITY: True,
                strings.REMARKS: None,
            },
        }
        self._perform_assertion(profile, income, exp_result)

    def test_ft_st_4(self):
        profile = constants.PROFILE_FT_ST
        income = 9001
        exp_result = {
            constants.GRANT_EHG_SINGLES: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_EHG_SINGLES_INCOME_ABOVE,
            },
        }
        self._perform_assertion(profile, income, exp_result)

    def test_both_st_5(self):
        profile = constants.PROFILE_BOTH_ST
        estate = strings.NONMATURE
        flat_size = constants.SIZE_2RM
        income = 7000
        exp_result = {
            constants.GRANT_STEPUP: {
                strings.ELIGIBILITY: True,
                strings.REMARKS: None,
            },
        }
        self._perform_assertion(profile, income, exp_result, estate=estate, flat_size=flat_size)

    def test_both_st_6(self):
        profile = constants.PROFILE_BOTH_ST
        estate = strings.NONMATURE
        flat_size = constants.SIZE_3RM
        income = 7000
        exp_result = {
            constants.GRANT_STEPUP: {
                strings.ELIGIBILITY: True,
                strings.REMARKS: None,
            },
        }
        self._perform_assertion(profile, income, exp_result, estate=estate, flat_size=flat_size)

    def test_both_st_7(self):
        profile = constants.PROFILE_BOTH_ST
        estate = strings.NONMATURE
        flat_size = constants.SIZE_2RM
        income = 7001
        exp_result = {
            constants.GRANT_STEPUP: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_STEPUP_INCOME_ABOVE,
            },
        }
        self._perform_assertion(profile, income, exp_result, estate=estate, flat_size=flat_size)

    def test_both_st_8(self):
        profile = constants.PROFILE_BOTH_ST
        estate = strings.NONMATURE
        flat_size = constants.SIZE_3RM
        income = 7001
        exp_result = {
            constants.GRANT_STEPUP: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_STEPUP_INCOME_ABOVE,
            },
        }
        self._perform_assertion(profile, income, exp_result, estate=estate, flat_size=flat_size)

    def test_both_st_9(self):
        profile = constants.PROFILE_BOTH_ST
        estate = strings.NONMATURE
        flat_size = constants.SIZE_4RM
        income = 7000
        exp_result = {
            constants.GRANT_STEPUP: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_STEPUP_FLAT_SIZE_NA_CURR,
            },
        }
        self._perform_assertion(profile, income, exp_result, estate=estate, flat_size=flat_size)

    def test_both_st_10(self):
        profile = constants.PROFILE_BOTH_ST
        estate = strings.MATURE
        flat_size = constants.SIZE_2RM
        income = 7000
        exp_result = {
            constants.GRANT_STEPUP: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_GEN_MATURE_ESTATE_NA,
            },
        }
        self._perform_assertion(profile, income, exp_result, estate=estate, flat_size=flat_size)

    def test_both_st_11(self):
        profile = constants.PROFILE_BOTH_ST
        estate = strings.MATURE
        flat_size = constants.SIZE_3RM
        income = 7000
        exp_result = {
            constants.GRANT_STEPUP: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_GEN_MATURE_ESTATE_NA,
            },
        }
        self._perform_assertion(profile, income, exp_result, estate=estate, flat_size=flat_size)

    def test_nonsc_spouse_12(self):
        profile = constants.PROFILE_NONSC_SPOUSE
        income = 9000
        exp_result = {
            constants.GRANT_EHG_SINGLES: {
                strings.ELIGIBILITY: True,
                strings.REMARKS: None,
            },
        }
        self._perform_assertion(profile, income, exp_result)

    def test_nonsc_spouse_13(self):
        profile = constants.PROFILE_NONSC_SPOUSE
        income = 9001
        exp_result = {
            constants.GRANT_EHG_SINGLES: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_EHG_SINGLES_INCOME_ABOVE,
            },
        }
        self._perform_assertion(profile, income, exp_result)

    def test_sg_single_14(self):
        profile = constants.PROFILE_SG_SINGLE
        income = 4500
        exp_result = {
            constants.GRANT_EHG_SINGLES: {
                strings.ELIGIBILITY: True,
                strings.REMARKS: None,
            },
        }
        self._perform_assertion(profile, income, exp_result)

    def test_sg_single_15(self):
        profile = constants.PROFILE_SG_SINGLE
        income = 4501
        exp_result = {
            constants.GRANT_EHG_SINGLES: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_EHG_SINGLES_INCOME_ABOVE_SINGLE,
            },
        }
        self._perform_assertion(profile, income, exp_result)

    def test_sg_jss_16(self):
        profile = constants.PROFILE_SG_JSS
        income = 9000
        estate = strings.NONMATURE
        flat_size = constants.SIZE_2RM
        exp_result = {
            constants.GRANT_EHG: {
                strings.ELIGIBILITY: True,
                strings.REMARKS: None,
            },
        }
        self._perform_assertion(profile, income, exp_result, estate=estate, flat_size=flat_size)

    def test_sg_jss_17(self):
        profile = constants.PROFILE_SG_JSS
        income = 9001
        estate = strings.NONMATURE
        flat_size = constants.SIZE_2RM
        exp_result = {
            constants.GRANT_EHG: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_EHG_INCOME_ABOVE,
            },
        }
        self._perform_assertion(profile, income, exp_result, estate=estate, flat_size=flat_size)

    def test_sg_jss_18(self):
        profile = constants.PROFILE_SG_JSS
        income = 9000
        estate = strings.NONMATURE
        flat_size = constants.SIZE_3RM
        exp_result = {
            constants.GRANT_EHG: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_EHG_FLAT_SIZE_NA,
            },
        }
        self._perform_assertion(profile, income, exp_result, estate=estate, flat_size=flat_size)

    def test_sg_jss_19(self):
        profile = constants.PROFILE_SG_JSS
        income = 9000
        estate = strings.MATURE
        flat_size = constants.SIZE_2RM
        exp_result = {
            constants.GRANT_EHG: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_GEN_MATURE_ESTATE_NA,
            },
        }
        self._perform_assertion(profile, income, exp_result, estate=estate, flat_size=flat_size)

    def test_sg_orphan_20(self):
        profile = constants.PROFILE_SG_ORPHAN
        income = 9000
        exp_result = {
            constants.GRANT_EHG: {
                strings.ELIGIBILITY: True,
                strings.REMARKS: None,
            },
        }
        self._perform_assertion(profile, income, exp_result)

    def test_sg_orphan_21(self):
        profile = constants.PROFILE_SG_ORPHAN
        income = 9001
        exp_result = {
            constants.GRANT_EHG: {
                strings.ELIGIBILITY: False,
                strings.REMARKS: constants.REMARKS_EHG_INCOME_ABOVE,
            },
        }
        self._perform_assertion(profile, income, exp_result)

class TestGrantEligibilityCurrResale(object):
    """

    For applications of resale flats that were received from Sep 2019 onwards.
    """
