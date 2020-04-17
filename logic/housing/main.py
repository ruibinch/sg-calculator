import logging

logger = logging.getLogger(__name__)

from . import constants
from utils import strings

"""
Main file serving as the entry point to the housing module.
"""

def calc_max_mortgage(property_type: str,
                      fixed_income: float,
                      variable_income: float,
                      property_loans: float,
                      property_loans_guarantor: float,
                      other_loans: float) -> dict:
    """Calculates the maximum mortgage amount based on MSR (if applicable) and TDSR.
    
    Mortgage Servicing Ratio (MSR):
    - Maximum 30% of a borrower’s gross monthly income can be used towards repaying all property loans
    - Applies to HDBs and ECs

    Total Debt Servicing Ratio (TDSR):
    - Maximum 60% of a borrower’s gross monthly income can be used for all debt obligations
    - Applies to both public and private properties

    Args:
        property_type (str): Type of property to purchase
        fixed_income (float): Household income from fixed sources, e.g. salary
        variable_income (float): Household income from variable sources, e.g. bonus, commission, rental, dividends
        property_loans (float): Total obligation for other property loans
        property_loans_guarantor (float): Total obligation for other property loans, where you are the guarantor
        other_loans (float): Total obligation for any other loans, e.g. car, student, renovation
    """

    # combined effective obligation for other property loans
    property_loans_comb = (property_loans + 
        (constants.RATIO_PROPERTY_LOANS_GUARANTOR * property_loans_guarantor))
    # total obligation for all loans
    all_loans = property_loans_comb + other_loans
    # calc effective income level
    eff_income_level = fixed_income + (constants.RATIO_VARIABLE_INCOME * variable_income)

    max_based_on_msr = (constants.MSR * eff_income_level) - property_loans_comb
    max_based_on_tdsr = (constants.TDSR * eff_income_level) - all_loans
    
    if property_type == constants.PROPERTY_PRIVATE:
        max_mortgage = max_based_on_tdsr
        max_based_on_msr = 'N/A'
    elif property_type in [constants.PROPERTY_HDB, constants.PROPERTY_EC]:
        max_mortgage = min(max_based_on_msr, max_based_on_tdsr)

    return {
        strings.VALUES: {
            strings.MAX_MORTGAGE: max_mortgage,
            strings.MAX_MORTGAGE_MSR: max_based_on_msr,
            strings.MAX_MORTGAGE_TDSR: max_based_on_tdsr,
        },
        strings.VARIABLES: {
            strings.EFFECTIVE_INCOME_LEVEL: eff_income_level,
            strings.ALL_LOANS: all_loans,
            strings.ALL_PROPERTY_LOANS: property_loans_comb,
            strings.MSR: constants.MSR,
            strings.TDSR: constants.TDSR,
        },
    }
