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

# Threshold for CPF contribution
THRESHOLD_CPF = 6000

# CPF contribution and allocation rates
rates = {
    '35': {
        'employee': 0.2,
        'employer': 0.17,
        'OA': 0.23,
        'SA': 0.06,
        'MA': 0.08
    },
    '45': {
        'employee': 0.2,
        'employer': 0.17,
        'OA': 0.21,
        'SA': 0.07,
        'MA': 0.09
    },
    '50': {
        'employee': 0.2,
        'employer': 0.17,
        'OA': 0.19,
        'SA': 0.08,
        'MA': 0.1
    },
    '55': {
        'employee': 0.2,
        'employer': 0.17,
        'OA': 0.15,
        'SA': 0.115,
        'MA': 0.105
    }
    # '60': {
    #     'employee': 0.13,
    #     'employer': 0.13,
    #     'RA': 0.155,
    #     'MA': 0.105
    # },
    # '65': {
    #     'employee': 0.075,
    #     'employer': 0.09,
    #     'RA': 0.06,
    #     'MA': 0.105
    # },
    # '150': {
    #     'employee': 0.05,
    #     'employer': 0.075,
    #     'RA': 0.02,
    #     'MA': 0.105
    # }
}