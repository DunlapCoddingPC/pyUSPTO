"""Tests for the shared query clause builders in pyUSPTO.clients.query."""

from typing import Any

import pytest

from pyUSPTO.clients import query


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
        ("CTNF", "f:CTNF"),
        ("IPR2022-01094", "f:IPR2022-01094"),
        ("A.NE", "f:A.NE"),
        (1700, "f:1700"),
        ("16*", "f:16*"),
        (["IPR2022-01094", "IPR2022-01228"], "f:(IPR2022-01094 OR IPR2022-01228)"),
        ([150, "161"], "f:(150 OR 161)"),
        (None, None),
        ("", None),
    ],
)
def test_code(value: Any, expected: str | None) -> None:
    """Test code values are sent bare, and lists become an OR group."""
    assert query.code("f", value) == expected


@pytest.mark.parametrize(
    "value", ["CTNF OR CTFR", "[16000000 TO 16999999]", "a:b", "H01L 21/02"]
)
def test_code_rejects_non_code(value: str) -> None:
    """Test a value that is not one code raises."""
    with pytest.raises(ValueError, match="query"):
        query.code("f", value)


def test_code_list_and_tuple() -> None:
    """Test a tuple is treated as a list of values."""
    assert query.code("f", ("CTNF", "CTFR")) == "f:(CTNF OR CTFR)"


@pytest.mark.parametrize("value", [[], ["CTNF", ""], ["CTNF", None]])
def test_list_rules(value: Any) -> None:
    """Test an empty list, or a list with an empty item, raises."""
    with pytest.raises(ValueError):
        query.code("f", value)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("Smith", "f:Smith"),
        ("Garcia*", "f:Garcia*"),
        ("103", "f:103"),
        ("nonstatutory double patenting", 'f:"nonstatutory double patenting"'),
        ("Block, Inc.", 'f:"Block, Inc."'),
        ("E-Link", 'f:"E-Link"'),
        ('"John Smith"', 'f:"\\"John Smith\\""'),
        ("Smith-K*", 'f:"Smith-K*"'),
        ('Smith "John', 'f:"Smith \\"John"'),
        ("a\\b", 'f:"a\\\\b"'),
        ("SYSTEM AND METHOD FOR MIXING", 'f:"SYSTEM AND METHOD FOR MIXING"'),
        (
            ["103", "nonstatutory double patenting"],
            'f:(103 OR "nonstatutory double patenting")',
        ),
        (None, None),
        ("", None),
    ],
)
def test_text(value: Any, expected: str | None) -> None:
    """Test text values are quoted when needed, and lists become an OR group."""
    assert query.text("f", value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("14/412,875", "f:14412875"),
        ("14/412875", "f:14412875"),
        (14412875, "f:14412875"),
        ("16*", "f:16*"),
        ("PCT/US2024/012345", "f:PCTUS2024012345"),
        (["14412875", "19378371"], "f:(14412875 OR 19378371)"),
        (None, None),
    ],
)
def test_application_number(value: Any, expected: str | None) -> None:
    """Test application numbers are sanitized, and lists become an OR group."""
    assert query.application_number("f", value) == expected


@pytest.mark.parametrize(
    "value", ["14412875 OR 14412876", "[16000000 TO 16999999]", "1441287"]
)
def test_application_number_rejects(value: str) -> None:
    """Test a value that is not one application number raises."""
    with pytest.raises(ValueError, match="query"):
        query.application_number("f", value)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("2021/0138233", "f:*20210138233*"),
        ("US 2021/0138233 A1", "f:*20210138233*"),
        ("US2021*", "f:US2021*"),
        (
            ["2021/0138233", "20210138234"],
            "f:(*20210138233* OR *20210138234*)",
        ),
        (None, None),
    ],
)
def test_publication_number(value: Any, expected: str | None) -> None:
    """Test publication numbers reduce to digits inside wildcards."""
    assert query.publication_number("f", value) == expected


def test_publication_number_rejects() -> None:
    """Test a value that is not one publication number raises."""
    with pytest.raises(ValueError, match="query"):
        query.publication_number("f", "abc")


@pytest.mark.parametrize(
    "value, expected",
    [
        ("H01L21/02", 'f:"H01L  21/02"'),
        ("H01L 21/02", 'f:"H01L  21/02"'),
        ("h01l 21/02", 'f:"H01L  21/02"'),
        ("A61N   2/02", 'f:"A61N   2/02"'),
        ("B62B2205/02", 'f:"B62B2205/02"'),
        ("G06F16/9535", 'f:"G06F  16/9535"'),
        ("A61N2", "f:A61N\\ \\ \\ 2\\/*"),
        ("B62B 7", "f:B62B\\ \\ \\ 7\\/*"),
        ("B62B2205", "f:B62B2205\\/*"),
        ("A61N", "f:A61N*"),
        ("A61N*", "f:A61N*"),
        (["A61N2/02", "H01L21/02"], 'f:("A61N   2/02" OR "H01L  21/02")'),
        (None, None),
    ],
)
def test_cpc_classification(value: Any, expected: str | None) -> None:
    """Test CPC symbols are converted to the stored fixed-width form."""
    assert query.cpc_classification("f", value) == expected


@pytest.mark.parametrize("value", ["H01L21/02 OR A61N2/02", "Z99Z1/00", "electrodes"])
def test_cpc_classification_rejects(value: str) -> None:
    """Test a value that is not one CPC symbol raises."""
    with pytest.raises(ValueError, match="query"):
        query.cpc_classification("f", value)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("10000000", "f:10000000"),
        ("10,000,000", "f:10000000"),
        ("US 10,000,000 B2", "f:10000000"),
        ("US8620039", "f:8620039"),
        ("D1154285", "f:D1154285"),
        ("RE51038", "f:RE51038"),
        ("PP37744", "f:PP37744"),
        ("1000000*", "f:1000000*"),
        (["10000000", "10000001"], "f:(10000000 OR 10000001)"),
        (None, None),
    ],
)
def test_patent_number(value: Any, expected: str | None) -> None:
    """Test patent numbers drop the US prefix, commas, and kind code."""
    assert query.patent_number("f", value) == expected


@pytest.mark.parametrize("value", ["10000000 OR 10000001", "not-a-patent"])
def test_patent_number_rejects(value: str) -> None:
    """Test a value that is not one patent number raises."""
    with pytest.raises(ValueError, match="query"):
        query.patent_number("f", value)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("WO2026044302", "f:WO2026044302"),
        ("WO 2026/044302", "f:WO2026044302"),
        ("WO2026044302A1", "f:WO2026044302"),
        ("wo 2026/044302 a1", "f:WO2026044302"),
        ("WO2026*", "f:WO2026*"),
        (None, None),
    ],
)
def test_pct_publication_number(value: Any, expected: str | None) -> None:
    """Test PCT publication numbers drop separators and the kind code."""
    assert query.pct_publication_number("f", value) == expected


def test_pct_publication_number_rejects() -> None:
    """Test a value that is not one PCT publication number raises."""
    with pytest.raises(ValueError, match="query"):
        query.pct_publication_number("f", "PCTUS202501234567")


def test_either() -> None:
    """Test either joins clauses with OR inside parentheses."""
    assert query.either("a:1", "b:2", None) == "(a:1 OR b:2)"
    assert query.either("a:1", None) == "a:1"
    assert query.either(None, None) is None


def test_all_of() -> None:
    """Test all_of joins clauses with AND, skipping absent ones."""
    assert query.all_of("a:1", None, "b:2") == "a:1 AND b:2"
    assert query.all_of(None) is None
