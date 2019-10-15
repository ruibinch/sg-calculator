""" Standard Statuses """

# all good
HTTPCODE_OK = 200
# all good, with no content to return
HTTPCODE_OK_EMPTY = 204
# unexpected error
HTTPCODE_ERROR = 500

""" Data Errors """

# the requested information is incomplete or malformed
HTTPCODE_INFO_INCOMPLETE = 400
# the requested information is ok but invalid
HTTPCODE_INFO_INVALID = 422
# resource does not exist
HTTPCODE_RESOURCE_MISSING = 404
# conflict of data exists
HTTPCODE_DATA_CONFLICT = 409

""" Auth Errors """

# missing or invalid access token
HTTPCODE_TOKEN_INVALID = 401
# access token valid but missing privileges 
HTTPCODE_TOKEN_INSUFFICIENT = 403