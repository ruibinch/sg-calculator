# For CPF contribution calculations
CEILING_OW = 6000
CEILING_AW = 102000
INCOME_BRACKET_1 = 50
INCOME_BRACKET_2 = 500
INCOME_BRACKET_3 = 749

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

# CPF contribution rates
rates_cont = {
    '55': [
        {},
        { 'combined': 0.17, 'employee': 0.0 },
        { 'combined': 0.17, 'employee': 0.0, 'misc': 0.6 },
        { 'combined': 0.37, 'employee': 0.2 },
    ],
    '60': [
        {},
        { 'combined': 0.13, 'employee': 0.0 },
        { 'combined': 0.13, 'employee': 0.0, 'misc': 0.39 },
        { 'combined': 0.26, 'employee': 0.13 },
    ],
    '65': [
        {},
        { 'combined': 0.09, 'employee': 0.0 },
        { 'combined': 0.09, 'employee': 0.0, 'misc': 0.225 },
        { 'combined': 0.165, 'employee': 0.075 },
    ],
    '150': [
        {},
        { 'combined': 0.075, 'employee': 0.0 },
        { 'combined': 0.075, 'employee': 0.0, 'misc': 0.15 },
        { 'combined': 0.125, 'employee': 0.05 },
    ],
}

# CPF allocation rates
rates_alloc = {
    '35': {
        'oa': 0.23,
        'sa': 0.06,
        'ma': 0.08,
        'oa_ratio': 0.6217,
        'sa_ratio': 0.1621,
        'ma_ratio': 0.2162,
    },
    '45': {
        'oa': 0.21,
        'sa': 0.07,
        'ma': 0.09,
        'oa_ratio': 0.5677,
        'sa_ratio': 0.1891,
        'ma_ratio': 0.2432,
    },
    '50': {
        'oa': 0.19,
        'sa': 0.08,
        'ma': 0.1,
        'oa_ratio': 0.5136,
        'sa_ratio': 0.2162,
        'ma_ratio': 0.2702,
    },
    '55': {
        'oa': 0.15,
        'sa': 0.115,
        'ma': 0.105,
        'oa_ratio': 0.4055,
        'sa_ratio': 0.3108,
        'ma_ratio': 0.2837,
    },
    '60': {
        'oa': 0.12,
        'sa': 0.035,
        'ma': 0.105,
        'oa_ratio': 0.4616,
        'sa_ratio': 0.1346,
        'ma_ratio': 0.4038,
    },
    '65': {
        'oa': 0.035,
        'sa': 0.025,
        'ma': 0.105,
        'oa_ratio': 0.2122,
        'sa_ratio': 0.1515,
        'ma_ratio': 0.6363,
    },
    '150': {
        'oa': 0.01,
        'sa': 0.01,
        'ma': 0.105,
        'oa_ratio': 0.08,
        'sa_ratio': 0.08,
        'ma_ratio': 0.84,
    },
}
