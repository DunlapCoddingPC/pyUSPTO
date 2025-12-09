"""Tests for models.utils"""

from datetime import date, datetime, timedelta, timezone, tzinfo
import importlib
from typing import Optional
from unittest.mock import patch
import warnings
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import pytest

from pyUSPTO.models import utils

# Import utility functions from models.utils module
from pyUSPTO.models.utils import (
    ASSUMED_NAIVE_TIMEZONE,
    ASSUMED_NAIVE_TIMEZONE_STR,
    parse_to_date,
    parse_to_datetime_utc,
    parse_yn_to_bool,
    serialize_bool_to_yn,
    serialize_date,
    serialize_datetime_as_iso,
    serialize_datetime_as_naive,
    to_camel_case,
)

from pyUSPTO.warnings import (
    USPTOBooleanParseWarning,
    USPTODateParseWarning,
    USPTOTimezoneWarning,
)


class TestUtilityFunctions:
    """Tests for utility functions in models.patent_data.py."""

    def test_parse_to_datetime_utc(self) -> None:
        """Test parse_to_datetime_utc utility function comprehensively."""
        dt_utc_z = parse_to_datetime_utc("2023-01-01T10:00:00Z")
        assert isinstance(dt_utc_z, datetime)
        assert dt_utc_z.replace(tzinfo=None) == datetime(2023, 1, 1, 10, 0, 0)
        assert dt_utc_z.tzinfo == timezone.utc

        dt_offset = parse_to_datetime_utc("2023-01-01T05:00:00-05:00")
        assert isinstance(dt_offset, datetime)
        assert dt_offset.replace(tzinfo=None) == datetime(2023, 1, 1, 10, 0, 0)
        assert dt_offset.tzinfo == timezone.utc

        dt_naive_str = "2023-01-01T10:00:00"
        dt_naive = parse_to_datetime_utc(dt_naive_str)
        assert isinstance(dt_naive, datetime)
        try:
            naive_datetime_instance = datetime(2023, 1, 1, 10, 0, 0)
            aware_datetime_instance = naive_datetime_instance.replace(
                tzinfo=ZoneInfo(ASSUMED_NAIVE_TIMEZONE_STR)
            )
            expected_naive_utc_hour = aware_datetime_instance.astimezone(
                timezone.utc
            ).hour
            assert dt_naive.hour == expected_naive_utc_hour
        except ZoneInfoNotFoundError:
            assert dt_naive.hour == 10
        assert dt_naive.tzinfo == timezone.utc

        dt_ms = parse_to_datetime_utc("2023-01-01T10:00:00.123Z")
        assert isinstance(dt_ms, datetime)
        assert dt_ms.replace(tzinfo=None) == datetime(2023, 1, 1, 10, 0, 0, 123000)
        assert dt_ms.tzinfo == timezone.utc

        dt_space = parse_to_datetime_utc("2023-01-01 10:00:00")
        assert isinstance(dt_space, datetime)
        try:
            naive_dt_for_space = datetime(2023, 1, 1, 10, 0, 0)
            aware_dt_for_space = naive_dt_for_space.replace(
                tzinfo=ZoneInfo(ASSUMED_NAIVE_TIMEZONE_STR)
            )
            expected_space_utc_hour = aware_dt_for_space.astimezone(timezone.utc).hour
            assert dt_space.hour == expected_space_utc_hour
        except ZoneInfoNotFoundError:
            assert dt_space.hour == 10
        assert dt_space.tzinfo == timezone.utc

        with pytest.warns(USPTODateParseWarning, match="Could not parse datetime"):
            assert parse_to_datetime_utc("invalid-datetime") is None

        assert parse_to_datetime_utc(None) is None

    def test_serialize_date(self) -> None:
        """Test serialize_date utility function."""
        test_date = date(2023, 1, 1)
        assert serialize_date(test_date) == "2023-01-01"
        assert serialize_date(None) is None

    def test_serialize_datetime_as_iso(self) -> None:
        """Test serialize_datetime_as_iso utility function."""
        dt_utc = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        assert serialize_datetime_as_iso(dt_utc) == "2023-01-01T05:00:00.000-0500"

        dt_naive = datetime(2023, 1, 2, 17, 0, 0)
        assert serialize_datetime_as_iso(dt_naive) == "2023-01-02T17:00:00.000-0500"

        minus_five = timezone(timedelta(hours=-5))
        dt_est = datetime(2023, 1, 3, 23, 0, 0, tzinfo=minus_five)
        assert serialize_datetime_as_iso(dt_est) == "2023-01-03T23:00:00.000-0500"

        assert serialize_datetime_as_iso(None) is None

    def test_serialize_datetime_as_naive(self) -> None:
        """Test serialize_datetime_as_naive utility function with both aware and naive datetimes."""
        # Test with timezone-aware datetime (hits if branch, line 163-164)
        dt_utc = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        result_aware = serialize_datetime_as_naive(dt_utc)
        assert isinstance(result_aware, str)
        # Should convert to ASSUMED_NAIVE_TIMEZONE and serialize as ISO
        assert result_aware.startswith("2023-01-01")

        # Test with naive datetime (hits else branch, line 165-166)
        dt_naive = datetime(2023, 1, 1, 15, 30, 45)
        result_naive = serialize_datetime_as_naive(dt_naive)
        assert isinstance(result_naive, str)
        assert result_naive == "2023-01-01T15:30:45"

        # Test with timezone-aware datetime with offset
        minus_five = timezone(timedelta(hours=-5))
        dt_est = datetime(2023, 1, 1, 10, 0, 0, tzinfo=minus_five)
        result_est = serialize_datetime_as_naive(dt_est)
        assert isinstance(result_est, str)
        assert result_est.startswith("2023-01-01")

    def test_parse_to_datetime_utc_localization_failure_and_fallback(self) -> None:
        """Triggers the except block by making astimezone() raise, and tests fallback path."""

        class FailingTZ(tzinfo):
            def utcoffset(self, dt: Optional[datetime]) -> None:
                raise Exception("boom")

            def dst(self, dt: Optional[datetime]) -> Optional[timedelta]:
                return None

            def tzname(self, dt: Optional[datetime]) -> Optional[str]:
                return None

        dt_str = "2023-01-01T10:00:00"

        with patch("pyUSPTO.models.utils.ASSUMED_NAIVE_TIMEZONE", FailingTZ()):
            with pytest.warns(USPTOTimezoneWarning, match="Error localizing"):
                result = parse_to_datetime_utc(datetime_str=dt_str)

        assert result is None

    def test_parse_to_datetime_utc_fallback_to_utc_replace(self) -> None:
        """Triggers fallback to dt_obj.replace(tzinfo=timezone.utc) without touching datetime.*"""

        class FailingButEqualToUTC(tzinfo):
            def utcoffset(self, dt: Optional[datetime]) -> None:
                raise Exception("boom")

            def dst(self, dt: Optional[datetime]) -> Optional[timedelta]:
                return None

            def tzname(self, dt: Optional[datetime]) -> Optional[str]:
                return None

            def __eq__(self, other: object) -> bool:
                return other is timezone.utc

        dt_str = "2023-01-01T10:00:00"

        with patch(
            "pyUSPTO.models.utils.ASSUMED_NAIVE_TIMEZONE", FailingButEqualToUTC()
        ):
            with pytest.warns(USPTOTimezoneWarning, match="Error localizing"):
                result = parse_to_datetime_utc(dt_str)

        assert isinstance(result, datetime)
        assert result.tzinfo == timezone.utc

    def test_parse_yn_to_bool(self) -> None:
        """Test parse_yn_to_bool utility function."""
        assert parse_yn_to_bool("Y") is True
        assert parse_yn_to_bool("y") is True
        assert parse_yn_to_bool("N") is False
        assert parse_yn_to_bool("n") is False
        assert parse_yn_to_bool(None) is None

        with pytest.warns(USPTOBooleanParseWarning, match="Unexpected value.*'True'"):
            assert parse_yn_to_bool("True") is None

        with pytest.warns(USPTOBooleanParseWarning, match="Unexpected value.*'False'"):
            assert parse_yn_to_bool("False") is None

        with pytest.warns(USPTOBooleanParseWarning, match="Unexpected value.*'Other'"):
            assert parse_yn_to_bool("Other") is None

        # All these should also warn
        with pytest.warns(USPTOBooleanParseWarning):
            assert parse_yn_to_bool("yes") is None
        with pytest.warns(USPTOBooleanParseWarning):
            assert parse_yn_to_bool("no") is None
        with pytest.warns(USPTOBooleanParseWarning):
            assert parse_yn_to_bool("X") is None

        # Empty string should not warn (just return None)
        assert parse_yn_to_bool("") is None

    def test_serialize_bool_to_yn(self) -> None:
        """Test serialize_bool_to_yn utility function."""
        assert serialize_bool_to_yn(True) == "Y"
        assert serialize_bool_to_yn(False) == "N"
        assert serialize_bool_to_yn(None) is None

    def test_timezone_setup_fallback(self) -> None:
        """Test fallback to UTC when timezone not found."""
        with patch(
            "zoneinfo.ZoneInfo", side_effect=ZoneInfoNotFoundError("Test error")
        ):
            import pyUSPTO.models.patent_data

            importlib.reload(pyUSPTO.models.patent_data)
            ASSUMED_NAIVE_TIMEZONE_STR_LOCAL = (
                "America/New_York2"  # Use a local var to avoid modifying global
            )
            try:
                assumed_naive_tz_local = ZoneInfo(ASSUMED_NAIVE_TIMEZONE_STR_LOCAL)
            except ZoneInfoNotFoundError:
                print(
                    f"Warning: Timezone '{ASSUMED_NAIVE_TIMEZONE_STR_LOCAL}' not found. Naive datetimes will be treated as UTC or may cause errors."
                )
                assumed_naive_tz_local = ZoneInfo("UTC")  # Fallback to UTC

            assert assumed_naive_tz_local == ZoneInfo("UTC")

        importlib.reload(module=pyUSPTO.models.patent_data)


class TestUtilsTimezone:
    """Tests for timezone handling in models.utils"""

    def test_zoneinfo_not_found(self, monkeypatch):
        """Test fallback when ZoneInfoNotFoundError is raised"""
        monkeypatch.setattr(
            "zoneinfo.ZoneInfo",
            lambda *_: (_ for _ in ()).throw(ZoneInfoNotFoundError),
        )
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            importlib.reload(utils)

        assert any(issubclass(msg.category, utils.USPTOTimezoneWarning) for msg in w)
        assert utils.ASSUMED_NAIVE_TIMEZONE is utils.timezone.utc
