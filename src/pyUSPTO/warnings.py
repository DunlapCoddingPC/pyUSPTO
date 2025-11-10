"""
warnings - Warning classes for pyUSPTO data parsing issues

This module defines custom warning categories for different types of
data parsing issues encountered when working with USPTO API responses.
These warnings follow Python's standard warning framework and can be
controlled using warnings.filterwarnings().

Example:
    # Suppress all pyUSPTO data warnings
    import warnings
    from pyUSPTO.warnings import USPTODataWarning
    warnings.filterwarnings('ignore', category=USPTODataWarning)

    # Turn specific warnings into errors (strict mode)
    warnings.filterwarnings('error', category=USPTODateParseWarning)
"""


class USPTODataWarning(UserWarning):
    """Base warning class for USPTO data parsing issues.

    All pyUSPTO data-related warnings inherit from this class,
    allowing users to filter all data warnings at once.
    """

    pass


class USPTODateParseWarning(USPTODataWarning):
    """Warning for date/datetime string parsing failures.

    Raised when a date or datetime string from the API cannot be
    parsed into a Python date/datetime object. The field will be
    set to None.
    """

    pass


class USPTOBooleanParseWarning(USPTODataWarning):
    """Warning for Y/N boolean string parsing failures.

    Raised when a string that should be 'Y' or 'N' has an unexpected
    value. The field will be set to None.
    """

    pass


class USPTOTimezoneWarning(USPTODataWarning):
    """Warning for timezone-related issues.

    Raised when timezone data is not available or timezone conversion
    fails. Falls back to UTC timezone.
    """

    pass


class USPTOEnumParseWarning(USPTODataWarning):
    """Warning for enum value parsing failures.

    Raised when an API response contains a value that doesn't match
    any defined enum member. The field will be set to None.
    """

    pass
