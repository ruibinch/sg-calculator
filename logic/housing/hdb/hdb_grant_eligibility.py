from . import constants
from utils import strings

"""
Finds the eligible CPF grant schemes.

4 possible scenarios:
1. prev_bto         Before Sep 2019, BTO
2. prev_resale      Before Sep 2019, Resale
3. curr_bto         Sep 2019 onwards, BTO
4. curr_resale      Sep 2019 onwards, Resale
"""

def find_grant_schemes_prev_bto(profile: str,
                                income: float,
                                estate: str,
                                flat_size: str):
    """Scenario: Before Sep 2019, BTO

    Args:
        profile (str): Applicant profile to match to available HDB grant scheme
        income (float): Monthly household income
        estate (str): Either mature or non-mature
        flat_size (str): Either 2-room, 3-room, 4-room, 5-room, 3gen or executive
    """

    schemes = {}

    if profile == constants.PROFILE_BOTH_FT:
        schemes = {
            constants.GRANT_AHG: _check_eligibility_ahg(
                profile,
                income,
                estate,
                flat_size),
            constants.GRANT_SHG: _check_eligibility_shg(
                profile,
                income,
                estate,
                flat_size),
        }
    elif profile == constants.PROFILE_FT_ST:
        schemes = {
            constants.GRANT_AHG_SINGLES: _check_eligibility_ahg(
                profile,
                income,
                estate,
                flat_size,
                singles=True),
            constants.GRANT_SHG_SINGLES: _check_eligibility_shg(
                profile,
                income,
                estate,
                flat_size,
                singles=True),
        }
    elif profile == constants.PROFILE_BOTH_ST:
        schemes = {
            constants.GRANT_STEPUP: _check_eligibility_stepup(
                strings.BEFORE_SEP_2019,
                income,
                estate,
                flat_size)
        }
    elif profile == constants.PROFILE_NONSC_SPOUSE:
        schemes = {
            constants.GRANT_AHG_SINGLES: _check_eligibility_ahg(
                profile,
                income,
                estate,
                flat_size,
                singles=True),
            constants.GRANT_SHG_SINGLES: _check_eligibility_shg(
                profile,
                income,
                estate,
                flat_size,
                singles=True),
        }
    elif profile == constants.PROFILE_SG_SINGLE:
        schemes = {
            constants.GRANT_AHG_SINGLES: _check_eligibility_ahg(
                profile,
                income * 2,
                estate,
                flat_size,
                singles=True),
            constants.GRANT_SHG_SINGLES: _check_eligibility_shg(
                profile,
                income * 2,
                estate,
                flat_size,
                singles=True),
        }
    elif profile in [constants.PROFILE_SG_JSS, constants.PROFILE_SG_ORPHAN]:
        schemes = {
            constants.GRANT_AHG: _check_eligibility_ahg(
                profile,
                income,
                estate,
                flat_size),
            constants.GRANT_SHG: _check_eligibility_shg(
                profile,
                income,
                estate,
                flat_size),
        }

    return schemes

def find_grant_schemes_prev_resale():
    schemes = {}

    # if profile == constants.PROFILE_BOTH_FT:
    
    # elif profile == constants.PROFILE_FT_ST:

    # elif profile == constants.PROFILE_BOTH_ST:
        
    # elif profile == constants.PROFILE_NONSC_SPOUSE:
        
    # elif profile == constants.PROFILE_SG_SINGLE:
        
    # elif profile == constants.PROFILE_SG_SINGLE_ORPHAN:

    return schemes
    
def find_grant_schemes_curr_bto(profile: str,
                                income: float,
                                estate: str = None,
                                flat_size: str = None):
    """Scenario: Sep 2019 onwards, BTO

    Args:
        profile (str): Applicant profile to match to available HDB grant scheme
        income (float): Monthly household income
    """

    schemes = {}

    if profile == constants.PROFILE_BOTH_FT:
        schemes = {
            constants.GRANT_EHG: _check_eligibility_ehg(
                profile,
                income),
        }
    elif profile == constants.PROFILE_FT_ST:
        schemes = {
            constants.GRANT_EHG_SINGLES: _check_eligibility_ehg(
                profile,
                income,
                singles=True),
        }
    elif profile == constants.PROFILE_BOTH_ST:
        schemes = {
            constants.GRANT_STEPUP: _check_eligibility_stepup(
                strings.SEP_2019_ONWARDS,
                income,
                estate,
                flat_size)
        }
    elif profile == constants.PROFILE_NONSC_SPOUSE:
        schemes = {
            constants.GRANT_EHG_SINGLES: _check_eligibility_ehg(
                profile,
                income,
                singles=True),
        }
    elif profile == constants.PROFILE_SG_SINGLE:
        schemes = {
            constants.GRANT_EHG_SINGLES: _check_eligibility_ehg(
                profile,
                income * 2,
                singles=True),
        }
    elif profile in [constants.PROFILE_SG_JSS, constants.PROFILE_SG_ORPHAN]:
        schemes = {
            constants.GRANT_EHG: _check_eligibility_ehg(
                profile,
                income,
                estate=estate,
                flat_size=flat_size),
        }

    return schemes

def find_grant_schemes_curr_resale():
    schemes = {}

    # if profile == constants.PROFILE_BOTH_FT:
    
    # elif profile == constants.PROFILE_FT_ST:

    # elif profile == constants.PROFILE_BOTH_ST:
        
    # elif profile == constants.PROFILE_NONSC_SPOUSE:
        
    # elif profile == constants.PROFILE_SG_SINGLE:
        
    # elif profile == constants.PROFILE_SG_SINGLE_ORPHAN:

    return schemes
    
"""
Checks for the eligibility on the individual grant schemes.

These methods will return a dict in the following structure:
{
    "eligibility": {True/False},
    "remarks": {remarks}
}

1. AHG
2. Citizen Top Up Grant
3. EHG
4. Half Housing Grant
5. PHG
6. SHG
7. Singles Grant
8. Step Up Grant
"""

def _check_eligibility_ahg(profile: str,
                           income: float,
                           estate: str,
                           flat_size: str,
                           singles: bool = False) -> dict:
    """Checks on eligibility for the AHG or AHG (Singles).
    
    AHG = Additional CPF Housing Grant
        
    Requirements:
        - <=$5k income, or <=$2.5k income for Singles variant
        - (flat size requirements vary depending on profile)
            - (Both FT) 2-room Flexi or larger
            - (1 FT, 1 ST) 2-room Flexi or larger
            - (Non-SC spouse) Non-mature estate, 2-room Flexi
            - (SG single) Non-mature estate, 2-room Flexi
            - (SG JSS) Non-mature estate, 2-room Flexi
            - (SG orphan) 2-room Flexi or larger

    Args:
        profile (str): Applicant profile to match to available HDB grant scheme
        income (float): Monthly household income (for 2 pax)
        estate (str): Either mature or non-mature
        flat_size (str): Either 2-room, 3-room, 4-room, 5-room, 3gen or executive
        singles (bool): Denotes if it is the AHG (Singles) variant
    """

    eligibility, remarks = None, None

    if (profile in [
            constants.PROFILE_NONSC_SPOUSE,
            constants.PROFILE_SG_SINGLE,
            constants.PROFILE_SG_JSS,
        ]
        and estate == strings.MATURE
    ):
        eligibility = False
        remarks = constants.REMARKS_GEN_MATURE_ESTATE_NA
    elif (profile in [
            constants.PROFILE_NONSC_SPOUSE,
            constants.PROFILE_SG_SINGLE,
            constants.PROFILE_SG_JSS,
        ]
        and flat_size != constants.SIZE_2RM
    ):
        eligibility = False
        remarks = constants.REMARKS_AHG_FLAT_SIZE_NA_2RM
    else:
        if income <= constants.INCOME_CEILING_AHG:
            eligibility = True
        else:
            eligibility = False
            if singles:
                if profile in [
                    constants.PROFILE_BOTH_FT,
                    constants.PROFILE_FT_ST,
                    constants.PROFILE_NONSC_SPOUSE,
                ]:
                    remarks = constants.REMARKS_AHG_SINGLES_INCOME_ABOVE
                elif profile == constants.PROFILE_SG_SINGLE:
                    remarks = constants.REMARKS_AHG_SINGLES_INCOME_ABOVE_SINGLE
            else:
                remarks = constants.REMARKS_AHG_INCOME_ABOVE

    return {
        strings.ELIGIBILITY: eligibility,
        strings.REMARKS: remarks,
    }

def _check_eligibility_ehg(profile: str,
                           income: float,
                           estate: str = None,
                           flat_size: str = None,
                           singles: bool = False) -> dict:
    """Checks on eligibility for the EHG or EHG (Singles).

    EHG = Enhanced CPF Housing Grant

    Requirements:
        - <=$9k income, or <=$4.5k income for Singles variant
        - (JSS) Non-mature estate, 2-room Flexi

    Args:
        profile (str): Applicant profile to match to available HDB grant scheme
        income (float): Monthly household income (for 2 pax)
        estate (str): Either mature or non-mature
        flat_size (str): Either 2-room, 3-room, 4-room, 5-room, 3gen or executive
        singles (bool): Denotes if it is the EHG (Singles) variant
    """

    eligibility, remarks = None, None

    if income <= constants.INCOME_CEILING_EHG:
        if profile == constants.PROFILE_SG_JSS:
            if estate == strings.MATURE:
                eligibility = False
                remarks = constants.REMARKS_GEN_MATURE_ESTATE_NA
            elif flat_size != constants.SIZE_2RM:
                eligibility = False
                remarks = constants.REMARKS_EHG_FLAT_SIZE_NA
            else:
                eligibility = True    
        else:
            eligibility = True
    else:
        eligibility = False
        if singles:
            if profile in [
                constants.PROFILE_FT_ST,
                constants.PROFILE_NONSC_SPOUSE,
            ]:
                remarks = constants.REMARKS_EHG_SINGLES_INCOME_ABOVE
            elif profile == constants.PROFILE_SG_SINGLE:
                remarks = constants.REMARKS_EHG_SINGLES_INCOME_ABOVE_SINGLE
        else:
            remarks = constants.REMARKS_EHG_INCOME_ABOVE

    return {
        strings.ELIGIBILITY: eligibility,
        strings.REMARKS: remarks,
    }

def _check_eligibility_shg(profile: str,
                           income: float,
                           estate: str,
                           flat_size: str,
                           singles: bool = False) -> dict:
    """Checks on eligibility for the SHG or SHG (Singles).
    
    SHG = Special CPF Housing Grant
    
    Requirements:
        - <=$8.5k income, or <=$4.25k income for Singles variant
        - Non-mature estate
        - (flat size requirements vary depending on profile)
            - (Both FT) 2-room Flexi, 3-room or 4-room flat
            - (1 FT, 1 ST) 2-room Flexi, 3-room or 4-room flat
            - (Non-SC spouse) 2-room Flexi
            - (SG single) 2-room Flexi
            - (SG JSS) 2-room Flexi
            - (SG orphan) 2-room Flexi, 3-room or 4-room flat

    Args:
        profile (str): Applicant profile to match to available HDB grant scheme
        income (float): Monthly household income (for 2 pax)
        estate (str): Either mature or non-mature
        flat_size (str): Either 2-room, 3-room, 4-room, 5-room, 3gen or executive
        singles (bool): Denotes if it is the SHG (Singles) variant
    """

    eligibility, remarks = None, None

    if estate == strings.MATURE:
        eligibility = False
        remarks = constants.REMARKS_GEN_MATURE_ESTATE_NA
    else:
        if (profile in [
                constants.PROFILE_BOTH_FT, 
                constants.PROFILE_FT_ST,
                constants.PROFILE_SG_ORPHAN,
            ]
            and flat_size not in [
                constants.SIZE_2RM,
                constants.SIZE_3RM,
                constants.SIZE_4RM,
            ]
        ):
            eligibility = False
            remarks = constants.REMARKS_SHG_FLAT_SIZE_NA
        elif (profile in [
                constants.PROFILE_NONSC_SPOUSE,
                constants.PROFILE_SG_SINGLE,
                constants.PROFILE_SG_JSS,
            ]
            and flat_size != constants.SIZE_2RM
        ):
            eligibility = False
            remarks = constants.REMARKS_SHG_FLAT_SIZE_NA_2RM
        else:
            if income <= constants.INCOME_CEILING_SHG:
                eligibility = True
            else:
                eligibility = False
                if singles:
                    if profile in [
                        constants.PROFILE_BOTH_FT,
                        constants.PROFILE_FT_ST,
                        constants.PROFILE_NONSC_SPOUSE,
                    ]:
                        remarks = constants.REMARKS_SHG_SINGLES_INCOME_ABOVE
                    elif profile == constants.PROFILE_SG_SINGLE:
                        remarks = constants.REMARKS_SHG_SINGLES_INCOME_ABOVE_SINGLE
                else:
                    remarks = constants.REMARKS_SHG_INCOME_ABOVE

    return {
        strings.ELIGIBILITY: eligibility,
        strings.REMARKS: remarks,
    }

def _check_eligibility_stepup(application_period: str,
                              income: float,
                              estate: str,
                              flat_size: str) -> dict:
    """Checks on eligibility for the Step-up CPF Housing Grant.

    Requirements:
        - <=$7k income
        - Non-mature estate
        - (flat size requirements vary depending on application period)
            - (before Sep 2019) 3-room flat
            - (from Sep 2019 onwards) 2-room or 3-room flat 

    Args:
        application_period (str): Either before Sep 2019, or Sep 2019 onwards
        income (float): Monthly household income
        estate (str): Either mature or non-mature
        flat_size (str): Either 2-room, 3-room, 4-room, 5-room, 3gen or executive
    """

    # Actually the changeover time period seems to be May 2019
    # https://www.hdb.gov.sg/cs/infoweb/residential/buying-a-flat/new/schemes-and-grants/cpf-housing-grants-for-hdb-flats/second-timer-applicants
    # will worry about this in the future
    # Also, it is stated that 
    # "income ceiling is $6,000 for applications received from May 2019 sales exercise to 10 Sep 2019."
    # But it doesn't mention about applications before May 2019...
    # So this is ignored for now and the income ceiling is just taken as $7,000

    eligibility, remarks = None, None

    if estate == strings.MATURE:
        eligibility = False
        remarks = constants.REMARKS_GEN_MATURE_ESTATE_NA
    else:
        if (application_period == strings.BEFORE_SEP_2019
            and flat_size != constants.SIZE_3RM):
            eligibility = False
            remarks = constants.REMARKS_STEPUP_FLAT_SIZE_NA_PREV
        elif (application_period == strings.SEP_2019_ONWARDS
            and flat_size not in [
                constants.SIZE_2RM, 
                constants.SIZE_3RM,
            ]):
            eligibility = False
            remarks = constants.REMARKS_STEPUP_FLAT_SIZE_NA_CURR
        else:
            if eligibility is None and remarks is None:
                if income <= constants.INCOME_CEILING_STEPUP:
                    eligibility = True
                else:
                    eligibility = False
                    remarks = constants.REMARKS_STEPUP_INCOME_ABOVE

    return {
        strings.ELIGIBILITY: eligibility,
        strings.REMARKS: remarks,
    }
