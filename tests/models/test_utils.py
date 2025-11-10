"""Tests for models.utils"""

import importlib
import warnings
import zoneinfo

from pyUSPTO.models import utils


class TestUtilsTimezone:
    """Tests for timezone handling in models.utils"""

    def test_zoneinfo_not_found(self, monkeypatch):
        """Test fallback when ZoneInfoNotFoundError is raised"""
        monkeypatch.setattr(
            zoneinfo,
            "ZoneInfo",
            lambda *_: (_ for _ in ()).throw(zoneinfo.ZoneInfoNotFoundError),
        )
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            importlib.reload(utils)

        assert any(issubclass(msg.category, utils.USPTOTimezoneWarning) for msg in w)
        assert utils.ASSUMED_NAIVE_TIMEZONE is utils.timezone.utc
