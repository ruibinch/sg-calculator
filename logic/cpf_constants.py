# For CPF contribution calculations
CEILING_OW_ANNUAL = 6000 * 12
CEILING_OW = 6000
CEILING_AW = 102000
INCOME_BRACKET_1 = 50 * 12
INCOME_BRACKET_2 = 500 * 12
INCOME_BRACKET_3 = 749 * 12
STR_COMBINED = 'combined'
STR_EMPLOYEE = 'employee'
STR_MISC = 'misc'
STR_CONTRIBUTION = 'contribution'
STR_ALLOCATION = 'allocation'


# CPF interest rates
# these are only base rates, include the other rates in the future
INT_RATE_OA = 0.025
INT_RATE_SA = 0.04
INT_RATE_MA = 0.04
INT_RATE_RA = 0.04
INT_EXTRA = 0.01

# Thresholds for additional interest
THRESHOLD_EXTRAINT_OA = 20000
THRESHOLD_EXTRAINT_TOTAL = 60000



# CPF contribution and allocation rates
rates_cont = {
    '55': [
        {},
        { 'combined': 0.17, 'employee': 0.0 },
        { 'combined': 0.17, 'employee': 0.0, 'misc': 0.6 },
        { 'combined': 0.37, 'employee': 0.2 }
    ],
    '60': [
        {},
        { 'combined': 0.13, 'employee': 0.0 },
        { 'combined': 0.13, 'employee': 0.0, 'misc': 0.39 },
        { 'combined': 0.26, 'employee': 0.13 }
    ],
    '65': [
        {},
        { 'combined': 0.09, 'employee': 0.0 },
        { 'combined': 0.09, 'employee': 0.0, 'misc': 0.225 },
        { 'combined': 0.165, 'employee': 0.075 }
    ],
    '150': [
        {},
        { 'combined': 0.075, 'employee': 0.0 },
        { 'combined': 0.075, 'employee': 0.0, 'misc': 0.15 },
        { 'combined': 0.125, 'employee': 0.05 }
    ],
}


rates_alloc = {
    '35': {
        'OA': 0.23,
        'SA': 0.06,
        'MA': 0.08
    },
    '45': {
        'OA': 0.21,
        'SA': 0.07,
        'MA': 0.09
    },
    '50': {
        'OA': 0.19,
        'SA': 0.08,
        'MA': 0.1
    },
    '55': {
        'OA': 0.15,
        'SA': 0.115,
        'MA': 0.105
    }
    # '60': {
    #     'RA': 0.155,
    #     'MA': 0.105
    # },
    # '65': {
    #     'RA': 0.06,
    #     'MA': 0.105
    # },
    # '150': {
    #     'RA': 0.02,
    #     'MA': 0.105
    # }
}