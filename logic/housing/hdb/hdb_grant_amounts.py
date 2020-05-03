import logging

from . import constants, grants
from utils import strings

logger = logging.getLogger(__name__)

def calc_grant_values(schemes: dict,
                      income: float) -> dict:
    """Calculates the applicable value to be awarded for each grant type.

    Args:
        schemes (dict): Applicable grant schemes
        income (float): Monthly household income
    """

    for grant_type in schemes:
        if grant_type in [
            constants.GRANT_AHG,
            constants.GRANT_EHG,
            constants.GRANT_SHG,
        ]:
            schemes[grant_type][strings.AMOUNT] = (
                _calc_grant_common(grant_type, income)
                if schemes[grant_type][strings.ELIGIBILITY] else 0)
        elif grant_type in [
            constants.GRANT_AHG_SINGLES,
            constants.GRANT_EHG_SINGLES,
            constants.GRANT_SHG_SINGLES,
        ]:
            schemes[grant_type][strings.AMOUNT] = (
                _calc_grant_common(grant_type, income, singles=True)
                if schemes[grant_type][strings.ELIGIBILITY] else 0)
        elif grant_type == constants.GRANT_STEPUP:
            schemes[grant_type][strings.AMOUNT] = (
                grants.STEPUP if schemes[grant_type][strings.ELIGIBILITY] else 0
            )


    return schemes

"""
Types of grants:
1. AHG / AHG (Singles) / EHG / EHG (Singles) / SHG / SHG (Singles)
2. Citizen Top Up Grant
4. Half Housing Grant
5. PHG
7. Singles Grant
8. Step Up Grant
"""

def _calc_grant_common(grant_type: str,
                       income: float,
                       singles: bool = False) -> float:
    """Calculates the applicable grant amount for the following grants:
    AHG, AHG (Singles), EHG, EHG (Singles), SHG, SHG (Singles)

    Args:0
        grant_type (str): Grant scheme
        income (float): Monthly household income - maximum value of 9000
        singles (bool): Denotes if it is the (Singles) variant
    """

    if grant_type in [constants.GRANT_AHG, constants.GRANT_AHG_SINGLES]:
        grants_table = grants.AHG
    elif grant_type in [constants.GRANT_EHG, constants.GRANT_EHG_SINGLES]:
        grants_table = grants.EHG
    elif grant_type in [constants.GRANT_SHG, constants.GRANT_SHG_SINGLES]:
        grants_table = grants.SHG

    for ceiling, amount in grants_table.items():
        if income <= ceiling:
            return amount / 2 if singles else amount

    return -1   # this line should never be reached
