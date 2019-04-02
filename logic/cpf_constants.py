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

# For CPF allocation
STR_ALLOCATION = 'allocation'
STR_OA = 'OA'
STR_SA = 'SA'
STR_MA = 'MA'
STR_RA = 'RA'

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
        'MA': 0.08,
        'OA_ratio': 0.6217,
        'SA_ratio': 0.1621,
        'MA_ratio': 0.2162
    },
    '45': {
        'OA': 0.21,
        'SA': 0.07,
        'MA': 0.09,
        'OA_ratio': 0.5677,
        'SA_ratio': 0.1891,
        'MA_ratio': 0.2432
    },
    '50': {
        'OA': 0.19,
        'SA': 0.08,
        'MA': 0.1,
        'OA_ratio': 0.5136,
        'SA_ratio': 0.2162,
        'MA_ratio': 0.2702
    },
    '55': {
        'OA': 0.15,
        'SA': 0.115,
        'MA': 0.105,
        'OA_ratio': 0.4055,
        'SA_ratio': 0.3108,
        'MA_ratio': 0.2837
    },
    '60': {
        'OA': 0.12,
        'SA': 0.035,
        'MA': 0.105,
        'OA_ratio': 0.4616,
        'SA_ratio': 0.1346,
        'MA_ratio': 0.4038
    },
    '65': {
        'OA': 0.035,
        'SA': 0.025,
        'MA': 0.105,
        'OA_ratio': 0.2122,
        'SA_ratio': 0.1515,
        'MA_ratio': 0.6363
    },
    '150': {
        'OA': 0.01,
        'SA': 0.01,
        'MA': 0.105,
        'OA_ratio': 0.08,
        'SA_ratio': 0.08,
        'MA_ratio': 0.84
    }
}