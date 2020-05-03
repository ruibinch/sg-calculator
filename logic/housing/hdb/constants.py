# CPF Housing Grant Types
GRANT_AHG = 'ahg'
GRANT_AHG_SINGLES = 'ahg_singles'
GRANT_EHG = 'ehg'
GRANT_EHG_SINGLES = 'ehg_singles'
GRANT_SHG = 'shg'
GRANT_SHG_SINGLES = 'shg_singles'
GRANT_STEPUP = 'stepup'
# Income thresholds for grants
INCOME_CEILING_AHG = 5000
INCOME_CEILING_EHG = 9000
INCOME_CEILING_SHG = 8500
INCOME_CEILING_STEPUP = 7000
# Remarks regarding grant ineligibility
REMARKS_AHG_INCOME_ABOVE = 'Your monthly household income is above the threshold of $5,000'
REMARKS_AHG_FLAT_SIZE_NA_2RM = 'Your flat must be a 2-room Flexi'
REMARKS_AHG_SINGLES_INCOME_ABOVE = 'Half of your monthly household income is above the threshold of $2,500'
REMARKS_AHG_SINGLES_INCOME_ABOVE_SINGLE = 'Your monthly household income is above the threshold of $2,500'
REMARKS_EHG_FLAT_SIZE_NA = 'Your flat must be a 2-room Flexi'
REMARKS_EHG_INCOME_ABOVE = 'Your monthly household income is above the threshold of $9,000'
REMARKS_EHG_SINGLES_INCOME_ABOVE = 'Half of your monthly household income is above the threshold of $4,500'
REMARKS_EHG_SINGLES_INCOME_ABOVE_SINGLE = 'Your monthly household income is above the threshold of $4,500'
REMARKS_GEN_MATURE_ESTATE_NA = 'Your flat is located in a mature estate'
REMARKS_SHG_FLAT_SIZE_NA = 'Your flat must be a 2-room Flexi, 3-room or 4-room flat'
REMARKS_SHG_FLAT_SIZE_NA_2RM = 'Your flat must be a 2-room Flexi'
REMARKS_SHG_INCOME_ABOVE = 'Your monthly household income is above the threshold of $8,500'
REMARKS_SHG_SINGLES_INCOME_ABOVE = 'Half of your monthly household income is above the threshold of $4,250'
REMARKS_SHG_SINGLES_INCOME_ABOVE_SINGLE = 'Your monthly household income is above the threshold of $4,250'
REMARKS_STEPUP_INCOME_ABOVE = 'Your monthly household income is above the threshold of $7,000'
REMARKS_STEPUP_FLAT_SIZE_NA_PREV = 'Your flat must be a 3-room flat'
REMARKS_STEPUP_FLAT_SIZE_NA_CURR = 'Your flat must be a 2-room Flexi or 3-room flat'

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
PROFILE_SG_JSS = 'sg_jss'
PROFILE_SG_ORPHAN = 'sg_orphan'
PROFILE_SC_SPR = 'sc_spr'   # (where SPR is taking up citizenship)
