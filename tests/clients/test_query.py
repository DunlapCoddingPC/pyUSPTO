"""Tests for the shared query clause builders in pyUSPTO.clients.query."""

from typing import Any

import pytest

from pyUSPTO.clients import query


@pytest.mark.parametrize(
    "value, expected",
    [
        ("CTNF", "f:CTNF"),
        (1700, "f:1700"),
        ("16*", "f:16*"),
        ("1700 OR 2800", "f:(1700 OR 2800)"),
        (None, None),
        ("", None),
    ],
)
def test_term(value: Any, expected: str | None) -> None:
    """Test code values are sent raw, and expressions are wrapped."""
    assert query.term("f", value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("Smith", "f:Smith"),
        ("Smith*", "f:Smith*"),
        ("John Smith", 'f:"John Smith"'),
        ("Block, Inc.", 'f:"Block, Inc."'),
        ("H01L21/02", 'f:"H01L21/02"'),
        ("E-Link", 'f:"E-Link"'),
        ("Smith-K*", 'f:"Smith-K*"'),
        ('Smith "John', 'f:"Smith \\"John"'),
        ("a\\b", 'f:"a\\\\b"'),
        ('"John Smith"', 'f:"\\"John Smith\\""'),
        (None, None),
        ("", None),
    ],
)
def test_phrase(value: Any, expected: str | None) -> None:
    """Test text values are quoted when needed, with quotes escaped."""
    assert query.phrase("f", value) == expected


def test_contains() -> None:
    """Test contains wraps the value in wildcards."""
    assert query.contains("f", "103") == "f:*103*"
    assert query.contains("f", "Final", quoted=True) == 'f:"*Final*"'
    assert query.contains("f", None) is None


@pytest.mark.parametrize(
    "value, expected",
    [
        ([1, "2"], "f:(1 OR 2)"),
        (150, "f:150"),
        ("150 OR 161", "f:(150 OR 161)"),
        (None, None),
    ],
)
def test_any_of(value: Any, expected: str | None) -> None:
    """Test lists become an OR group and single values a term."""
    assert query.any_of("f", value) == expected


def test_any_of_empty_list() -> None:
    """Test an empty list raises instead of silently dropping the filter."""
    with pytest.raises(ValueError, match="empty list"):
        query.any_of("f", [])


@pytest.mark.parametrize(
    "value, expected", [(True, "f:true"), (False, "f:false"), (None, None)]
)
def test_boolean(value: bool | None, expected: str | None) -> None:
    """Test booleans are lowercased, and False still adds a clause."""
    assert query.boolean("f", value) == expected


@pytest.mark.parametrize(
    "start, end, expected",
    [
        ("2023-01-01", "2023-12-31", "f:[2023-01-01 TO 2023-12-31]"),
        ("2023-01-01", None, "f:>=2023-01-01"),
        (None, "2023-12-31", "f:<=2023-12-31"),
        (None, None, None),
    ],
)
def test_date_range(start: str | None, end: str | None, expected: str | None) -> None:
    """Test the three date range forms."""
    assert query.date_range("f", start, end) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("14/412,875", "f:14412875"),
        ("14/412875", "f:14412875"),
        (14412875, "f:14412875"),
        ("PCT/US2024/012345", "f:PCTUS2024012345"),
        ("16*", "f:(16*)"),
        ("14412875 OR 14412876", "f:(14412875 OR 14412876)"),
        ("[16000000 TO 16999999]", "f:([16000000 TO 16999999])"),
        (None, None),
    ],
)
def test_application_number(value: Any, expected: str | None) -> None:
    """Test application numbers are sanitized, and expressions wrapped."""
    assert query.application_number("f", value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("2021/0138233", "f:*20210138233*"),
        ("US 2021/0138233 A1", "f:*20210138233*"),
        ("US2021*", "f:US2021*"),
        ("abc", "f:abc"),
        (None, None),
    ],
)
def test_publication_number(value: Any, expected: str | None) -> None:
    """Test publication numbers reduce to digits inside wildcards."""
    assert query.publication_number("f", value) == expected


def test_either() -> None:
    """Test either joins clauses with OR inside parentheses."""
    assert query.either("a:1", "b:2", None) == "(a:1 OR b:2)"
    assert query.either("a:1", None) == "a:1"
    assert query.either(None, None) is None


def test_all_of() -> None:
    """Test all_of joins clauses with AND, skipping absent ones."""
    assert query.all_of("a:1", None, "b:2") == "a:1 AND b:2"
    assert query.all_of(None) is None
