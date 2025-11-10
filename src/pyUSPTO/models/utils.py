"""
models.utils - Utility functions for USPTO data models

This module provides utility functions for parsing, serializing, and converting
data used across USPTO API data models. These utilities handle date/datetime
conversions, boolean string representations, and string transformations.
"""

import warnings
from datetime import date, datetime, timezone, tzinfo
from typing import Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pyUSPTO.warnings import (
    USPTOBooleanParseWarning,
    USPTODateParseWarning,
    USPTOTimezoneWarning,
)

# --- Timezone and Parsing Utilities ---
ASSUMED_NAIVE_TIMEZONE_STR = "America/New_York"
try:
    ASSUMED_NAIVE_TIMEZONE: Optional[tzinfo] = ZoneInfo(ASSUMED_NAIVE_TIMEZONE_STR)
except ZoneInfoNotFoundError:
    warnings.warn(
        f"Timezone '{ASSUMED_NAIVE_TIMEZONE_STR}' not found. "
        f"Naive datetimes will be treated as UTC.",
        category=USPTOTimezoneWarning,
        stacklevel=1,
    )
    ASSUMED_NAIVE_TIMEZONE = timezone.utc


def parse_to_date(date_str: Optional[str], fmt: str = "%Y-%m-%d") -> Optional[date]:
    """Parses a string representation of a date into a date object.

    Args:
        date_str (Optional[str]): The string to parse as a date.
        fmt (str, optional): The expected strptime format string for parsing
            the date. Defaults to "%Y-%m-%d".

    Returns:
        Optional[date]: A date object if parsing is successful and `date_str`
            is not None. Returns None if `date_str` is None or if parsing fails.

    Warns:
        USPTODateParseWarning: If the date string cannot be parsed.
    """

    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, fmt).date()
    except ValueError:
        warnings.warn(
            f"Could not parse date string '{date_str}' with format '{fmt}'",
            category=USPTODateParseWarning,
            stacklevel=2,
        )
        return None


def parse_to_datetime_utc(datetime_str: Optional[str]) -> Optional[datetime]:
    """Parses a string representation of a datetime into a UTC datetime object.

    Attempts to parse ISO format strings. If the input string contains timezone
    information, it's used. If the string is a naive datetime (no timezone),
    it's assumed to be in the `ASSUMED_NAIVE_TIMEZONE` (e.g., "America/New_York")
    and then converted to UTC.

    Args:
        datetime_str (Optional[str]): The string to parse as a datetime.
            Supports ISO 8601 format, including those ending with "Z".

    Returns:
        Optional[datetime]: A timezone-aware datetime object in UTC if parsing
            is successful and `datetime_str` is not None. Returns None if
            `datetime_str` is None or if parsing/conversion fails.

    Warns:
        USPTODateParseWarning: If the datetime string cannot be parsed.
        USPTOTimezoneWarning: If timezone localization fails.
    """

    if not datetime_str:
        return None
    dt_obj: Optional[datetime] = None
    parsed_successfully = False
    if isinstance(datetime_str, str):
        try:
            if datetime_str.endswith("Z"):
                dt_obj = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
            else:
                dt_obj = datetime.fromisoformat(datetime_str)
            parsed_successfully = True
        except ValueError:
            pass
    if not parsed_successfully or dt_obj is None:
        warnings.warn(
            f"Could not parse datetime string '{datetime_str}' with any known format",
            category=USPTODateParseWarning,
            stacklevel=2,
        )
        return None
    if dt_obj.tzinfo is None or dt_obj.tzinfo.utcoffset(dt_obj) is None:
        if ASSUMED_NAIVE_TIMEZONE:
            try:
                aware_dt = dt_obj.replace(tzinfo=ASSUMED_NAIVE_TIMEZONE)
                return aware_dt.astimezone(timezone.utc)
            except Exception as e:
                warnings.warn(
                    f"Error localizing naive datetime '{datetime_str}': {e}",
                    category=USPTOTimezoneWarning,
                    stacklevel=2,
                )
                if ASSUMED_NAIVE_TIMEZONE == timezone.utc:
                    return dt_obj.replace(tzinfo=timezone.utc)
        return None
    else:
        return dt_obj.astimezone(timezone.utc)


def serialize_date(d: Optional[date]) -> Optional[str]:
    """Serializes a date object into an ISO 8601 string (YYYY-MM-DD).

    Args:
        d (Optional[date]): The date object to serialize.

    Returns:
        Optional[str]: The date as an ISO 8601 formatted string, or None
            if the input is None.
    """
    return d.isoformat() if d else None


def serialize_datetime_as_iso(dt: Optional[datetime]) -> Optional[str]:
    """Serializes a datetime object to an ISO 8601 string in UTC, using 'Z'.

    If the input datetime object is timezone-aware, it is converted to UTC.
    If it is naive (lacks timezone information), it is assumed to be UTC.
    The resulting UTC datetime is then formatted as an ISO 8601 string,
    with the UTC timezone explicitly indicated by 'Z'.

    Args:
        dt (Optional[datetime]): The datetime object to serialize.
            Can be naive or timezone-aware.

    Returns:
        Optional[str]: The datetime as a UTC ISO 8601 formatted string
            (e.g., "YYYY-MM-DDTHH:MM:SS.ffffffZ" or "YYYY-MM-DDTHH:MM:SSZ"),
            or None if the input `dt` is None.
    """

    if not dt:
        return None
    dt_utc = (
        dt.astimezone(timezone.utc) if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    )
    return dt_utc.isoformat().replace("+00:00", "Z")


def parse_yn_to_bool(value: Optional[str]) -> Optional[bool]:
    """Converts a 'Y'/'N' (case-insensitive) string to a boolean.

    Args:
        value (Optional[str]): The string value to convert. Expected to be
            'Y', 'y', 'N', or 'n'.

    Returns:
        Optional[bool]: True if `value` is 'Y' or 'y', False if `value` is
            'N' or 'n'. Returns None if `value` is None or any other string.

    Warns:
        USPTOBooleanParseWarning: If the value is not 'Y' or 'N'.
    """

    if value is None:
        return None
    if value.upper() == "Y":
        return True
    if value.upper() == "N":
        return False
    warnings.warn(
        f"Unexpected value for Y/N boolean string: '{value}'. Treating as None.",
        category=USPTOBooleanParseWarning,
        stacklevel=2,
    )
    return None


def serialize_bool_to_yn(value: Optional[bool]) -> Optional[str]:
    """Converts a boolean value to its 'Y'/'N' string representation.

    Args:
        value (Optional[bool]): The boolean value to convert.

    Returns:
        Optional[str]: "Y" if `value` is True, "N" if `value` is False.
            Returns None if `value` is None.
    """

    if value is None:
        return None
    return "Y" if value else "N"


def to_camel_case(snake_str: str) -> str:
    """Converts a snake_case string to lowerCamelCase.

    For example, "example_snake_string" becomes "exampleSnakeString".

    Args:
        snake_str (str): The input string in snake_case.

    Returns:
        str: The converted string in lowerCamelCase.
    """
    parts = snake_str.split("_")
    return parts[0] + "".join(x.title() for x in parts[1:])
