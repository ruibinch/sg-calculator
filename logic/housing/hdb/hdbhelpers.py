from . import constants
from utils import strings

###############################################################################
# MAIN METHODS                                                                #
#                                                                             #
# 4 possible scenarios:                                                       #
# 1. prev_bto - Before Sep 2019, BTO                                          #
# 2. prev_resale - Before Sep 2019, Resale                                    #
# 3. curr_bto - Sep 2019 onwards, BTO                                         #
# 4. curr_resale - Sep 2019 onwards, Resale                                   #
###############################################################################

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
            constants.GRANT_AHG: _check_eligibility_ahg(income),
            constants.GRANT_SHG: _check_eligibility_shg(
                income, estate, flat_size),
        }
    # elif profile == constants.PROFILE_FT_ST:

    # elif profile == constants.PROFILE_BOTH_ST:
        
    # elif profile == constants.PROFILE_NONSC_SPOUSE:
        
    # elif profile == constants.PROFILE_SG_SINGLE:
        
    # elif profile == constants.PROFILE_SG_SINGLE_ORPHAN:

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
                                income: float):
    """Scenario: Sep 2019 onwards, BTO

    Args:
        profile (str): Applicant profile to match to available HDB grant scheme
        income (float): Monthly household income
    """

    schemes = {}

    if profile == constants.PROFILE_BOTH_FT:
        schemes = {
            constants.GRANT_EHG: _check_eligibility_ehg(income),
        }
    # elif profile == constants.PROFILE_FT_ST:

    # elif profile == constants.PROFILE_BOTH_ST:
        
    # elif profile == constants.PROFILE_NONSC_SPOUSE:
        
    # elif profile == constants.PROFILE_SG_SINGLE:
        
    # elif profile == constants.PROFILE_SG_SINGLE_ORPHAN:


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
    
###############################################################################
# GRANT ELIGIBILITY CHECKS                                                    #
#                                                                             #
# These methods will return a dict in the following structure:                #
# {                                                                           #
#     "eligibility": {True/False},                                            #
#     "remarks": {remarks}                                                    #
# }                                                                           #
#                                                                             #
# 1. AHG                                                                      #
# 2. Citizen Top Up Grant                                                     #
# 3. EHG                                                                      #
# 4. Half Housing Grant                                                       #
# 5. PHG                                                                      #
# 6. SHG                                                                      #
# 7. Singles Grant                                                            #
# 8. Step Up Grant                                                            #
###############################################################################

def _check_eligibility_ahg(income: float) -> dict:
    """Checks on eligibility for the AHG (Additional CPF Housing Grant).

    Args:
        income (float): Monthly household income
    """

    eligibility, remarks = None, None

    if income <= constants.INCOME_THRESH_AHG:
        eligibility = True
    else:
        eligibility = False
        remarks = constants.REMARKS_AHG_INCOME_ABOVE

    return {
        strings.ELIGIBILITY: eligibility,
        strings.REMARKS: remarks,
    }

def _check_eligibility_ehg(income: float) -> dict:
    """Checks on eligibility for the EHG (Enhanced CPF Housing Grant).

    Args:
        income (float): Monthly household income
    """

    eligibility, remarks = None, None

    if income <= constants.INCOME_THRESH_EHG:
        eligibility = True
    else:
        eligibility = False
        remarks = constants.REMARKS_EHG_INCOME_ABOVE

    return {
        strings.ELIGIBILITY: eligibility,
        strings.REMARKS: remarks,
    }

def _check_eligibility_shg(income: float,
                           estate: str,
                           flat_size: str) -> dict:
    """Checks on eligibility for the SHG (Special CPF Housing Grant).

    Args:
        income (float): Monthly household income
        estate (str): Either mature or non-mature
        flat_size (str): Either 2-room, 3-room, 4-room, 5-room, 3gen or executive
    """

    eligibility, remarks = None, None

    if estate == strings.MATURE:
        eligibility = False
        remarks = constants.REMARKS_SHG_MATURE_ESTATE_NA
    else:
        if flat_size not in [constants.SIZE_2RM, constants.SIZE_3RM, constants.SIZE_4RM]:
            eligibility = False
            remarks = constants.REMARKS_SHG_FLAT_SIZE_NA
        else:
            if income <= constants.INCOME_THRESH_SHG:
                eligibility = True
            else:
                eligibility = False
                remarks = constants.REMARKS_SHG_INCOME_ABOVE

    return {
        strings.ELIGIBILITY: eligibility,
        strings.REMARKS: remarks,
    }
