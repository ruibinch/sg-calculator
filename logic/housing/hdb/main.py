import logging

from . import hdbhelpers, constants
from utils import strings

logger = logging.getLogger(__name__)

def find_grant_schemes(application_period: str,
                       flat_type: str,
                       profile: str,
                       income: float,
                       estate: str,
                       flat_size: str,
                       near_parents: str) -> dict:
    """Finds the applicable CPF Housing grant schemes.
    
    Args:
        application_period (str): Either before Sep 2019, or Sep 2019 onwards
        flat_type (str): Either BTO or resale
        profile (str): Applicant profile to match to available HDB grant scheme
        income (float): Monthly household income
        estate (str): Either mature or non-mature
        flat_size (str): Either 2-room, 3-room, 4-room, 5-room, 3gen or executive
        near_parents (str): Either yes or no
    """

    if application_period == strings.BEFORE_SEP_2019:
        if flat_type == strings.BTO:
            schemes = hdbhelpers.find_grant_schemes_prev_bto(
                profile, income, estate, flat_size
            )
        elif flat_type == strings.RESALE:
            schemes = hdbhelpers.find_grant_schemes_prev_resale()
    elif application_period == strings.SEP_2019_ONWARDS:
        if flat_type == strings.BTO:
            schemes = hdbhelpers.find_grant_schemes_curr_bto(
                profile, income
            )
        elif flat_type == strings.RESALE:
            schemes = hdbhelpers.find_grant_schemes_curr_resale()


    return {
        strings.SCHEMES: schemes,
    }
