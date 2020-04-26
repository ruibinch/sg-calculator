# CPF Housing Grant Types
GRANT_AHG = 'ahg'
GRANT_AHG_SINGLES = 'ahg_singles'
GRANT_EHG = 'ehg'
GRANT_EHG_SINGLES = 'ehg_singles'
GRANT_SHG = 'shg'
GRANT_SHG_SINGLES = 'shg_singles'
GRANT_STEPUP = 'stepup'
# Income thresholds for grants
INCOME_THRESH_AHG = 5000
INCOME_THRESH_EHG = 9000
INCOME_THRESH_SHG = 8500
INCOME_THRESH_STEPUP = 7000
# Remarks regarding grant ineligibility
REMARKS_AHG_INCOME_ABOVE = 'Your monthly household income is above the threshold of $5,000'
REMARKS_EHG_INCOME_ABOVE = 'Your monthly household income is above the threshold of $9,000'
REMARKS_SHG_FLAT_SIZE_NA = 'Your flat must be of one of the following types: 2-room, 3-room, 4-room'
REMARKS_SHG_INCOME_ABOVE = 'Your monthly household income is above the threshold of $8,500'
REMARKS_SHG_MATURE_ESTATE_NA = 'Your flat is not applicable for the SHG as it is located in a mature estate'

# Flat sizes
SIZE_2RM = '2rm'
SIZE_3RM = '3rm'
SIZE_4RM = '4rm'
SIZE_5RM = '5rm'
SIZE_3GEN = '3gen'
SIZE_EXEC = 'exec'
HDB_FLAT_SIZES = [
    SIZE_2RM, SIZE_3RM, SIZE_4RM, SIZE_5RM, SIZE_3GEN, SIZE_EXEC,
]

# Applicant profiles
PROFILE_BOTH_FT = 'ft_ft'
PROFILE_FT_ST = 'ft_st'
PROFILE_BOTH_ST = 'st_st'
PROFILE_NONSC_SPOUSE = 'nonsc_spouse'
PROFILE_SG_SINGLE = 'sg_single'
PROFILE_SG_SINGLE_ORPHAN = 'sg_single_orphan'
PROFILE_SC_SPR = 'sc_spr'   # (where SPR is taking up citizenship)
