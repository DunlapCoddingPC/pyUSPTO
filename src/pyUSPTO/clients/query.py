"""query - Shared builders for Lucene query clauses.

Each builder returns one ``field:value`` clause, or ``None`` when the filter is
absent (``None`` or ``""``), and formats every value with ``str()``. A filter
takes one value or a list (or tuple) of values; several values become
``field:(a OR b)``. An empty list, or an empty item in a list, raises
``ValueError``, so a mistaken ``[]`` never runs an unfiltered search.

Values are literal. ``text`` quotes a value that contains whitespace or a
Lucene special character, with backslashes and double quotes escaped.
``code`` sends a value exactly as given and rejects one that is not a single
code. The identifier builders convert each value to the form the API stores
and reject one they cannot read. A single word containing ``*`` or ``?`` is a
wildcard pattern in every builder.
"""

import re
from typing import NoReturn

_PHRASE_SPECIAL = frozenset('+-&|!(){}[]^"~:\\/<>=')
# Lucene reads these words as operators when they stand alone.
_OPERATOR_WORDS = frozenset({"AND", "OR", "NOT", "TO"})

_PUBLICATION_NUMBER_RE = re.compile(
    r"^(?:US)?[\s/\-,]*(\d{4})[\s/\-,]*(\d{7})[\s/\-,]*(?:[A-Z]\d)?$"
)
_CODE_RE = re.compile(r"^[A-Za-z0-9*?][A-Za-z0-9._*?-]*$")
_WILDCARD_RE = re.compile(r"^[A-Za-z0-9*?]+$")
_PATENT_NUMBER_RE = re.compile(r"^(?:US)?(D|RE|PP|H|T)?(\d{1,8})(?:[A-Z]\d?)?$")
# Current form WO + 4-digit year + 6-digit serial; before 2004, WO + 2-digit
# year + 5- or 6-digit serial (WO 03/106655). The API stores the current form.
_PCT_PUBLICATION_RE = re.compile(
    r"^WO(?:(\d{4})(\d{6})|(\d{2})(\d{5,6}))(?:[A-Z]\d?)?$"
)
_CPC_SYMBOL_RE = re.compile(r"^([A-HY]\d{2}[A-Z])\s*(\d{1,4})\s*/\s*(\d{1,6})$")
_CPC_GROUP_RE = re.compile(r"^([A-HY]\d{2}[A-Z])\s*(\d{1,4})$")
_CPC_GROUP_WILDCARD_RE = re.compile(r"^([A-HY]\d{2}[A-Z])\s*(\d{1,4})\*$")
_CPC_SUBCLASS_RE = re.compile(r"^[A-HY]\d{2}[A-Z]$")

_RAW_QUERY_HINT = (
    "In a search filter, pass a list for several values, or put other search "
    "syntax in the raw query string (`query`, or `criteria` on "
    "OAActionsClient, OACitationsClient, and OARejectionsClient)."
)
# A main-group prefix is sent unquoted, so its padding spaces and the slash
# are backslash-escaped: ``A61N\ \ \ 2\/*``.
_ESCAPED_SPACE = "\\ "
_ESCAPED_SLASH_WILDCARD = "\\/*"


def _is_absent(value: object) -> bool:
    """Return True for a filter value that should add no clause."""
    return value is None or (isinstance(value, str) and value.strip() == "")


def _has_whitespace(value: str) -> bool:
    """Return True if the value contains any whitespace character."""
    return any(c.isspace() for c in value)


def sanitize_application_number(input_number: str) -> str:
    """Return an application number in the form the USPTO APIs store.

    See ``PatentDataClient.sanitize_application_number`` for the accepted
    formats and examples.

    Args:
        input_number: Raw application number input.

    Returns:
        str: "NNNNNNNN", or "PCT" + 2-char country + 4-digit year +
            6-digit serial.

    Raises:
        ValueError: If the format is invalid.
    """
    if not input_number or not input_number.strip():
        raise ValueError("Application number cannot be empty")

    raw = input_number.strip()

    # Handle PCT formats. Output is the standardized 15-char form:
    # "PCT" + 2-char country + 4-digit year + 6-digit zero-padded serial.
    # Example: "PCT/US2024/012345" -> "PCTUS2024012345"
    if raw.startswith("PCT"):
        parts = raw.split("/")
        if len(parts) == 1:
            # No slashes — only accept input that is already in the 15-char form.
            body = raw[3:]
            if len(body) == 12 and body[:2].isalpha() and body[2:].isdigit():
                return raw
            raise ValueError(
                f"Invalid PCT application format: {input_number}. "
                "Expected PCT/CCYYYY/NNNNNN or PCTCCYYYYNNNNNN."
            )
        if len(parts) != 3:
            raise ValueError(
                f"Invalid PCT application format: {input_number}. "
                "Expected PCT/CCYYYY/NNNNNN"
            )

        _, country_year, serial = parts

        # country_year can be "US2024" or "US24"
        country = country_year[:2]
        if len(country) != 2 or not country.isalpha():
            raise ValueError(
                f"Invalid PCT country code in: {country_year}. Expected 2 letters."
            )

        year_part = country_year[2:]
        if not year_part.isdigit():
            raise ValueError(f"Invalid PCT year in: {country_year}. Must be digits.")

        # Normalize to 4-digit year. 2-digit input uses a sliding window
        # tied to the PCT system's start year (1978): YY>=78 -> 19YY, else 20YY.
        if len(year_part) == 4:
            year = year_part
        elif len(year_part) == 2:
            yy = int(year_part)
            year = f"19{year_part}" if yy >= 78 else f"20{year_part}"
        else:
            raise ValueError(
                f"Invalid PCT year length in: {country_year}. Expected CCYYYY or CCYY."
            )

        # Serial must be digits only, and fit in 6 digits.
        if not serial.isdigit():
            raise ValueError(f"Invalid PCT serial: {serial}. Must be numeric.")
        if len(serial) > 6:
            raise ValueError(f"Invalid PCT serial: {serial}. Must be at most 6 digits.")

        return f"PCT{country}{year}{serial.zfill(6)}"

    # Strip whitespace and remove commas/spaces
    cleaned = raw.replace(",", "").replace(" ", "")

    # Check if this is series code format (NN/NNNNNN)
    if "/" in cleaned:
        parts = cleaned.split("/")
        if len(parts) != 2:
            raise ValueError(
                f"Invalid application number format: {input_number}. "
                "Expected format: NNNNNNNN or NN/NNNNNN"
            )

        series, serial = parts
        if not series.isdigit() or not serial.isdigit():
            raise ValueError(
                f"Invalid application number format: {input_number}. "
                "Series and serial must be numeric."
            )

        if len(series) != 2 or len(serial) != 6:
            raise ValueError(
                f"Invalid application number format: {input_number}. "
                "Expected series code format: NN/NNNNNN (2 digits / 6 digits)"
            )

        return series + serial

    # Standard 8-digit format
    if not cleaned.isdigit():
        raise ValueError(
            f"Invalid application number format: {input_number}. "
            "Must contain only digits."
        )

    if len(cleaned) != 8:
        raise ValueError(
            f"Invalid application number format: {input_number}. Expected 8 digits."
        )

    return cleaned


def _values(field: str, value: object) -> list[str]:
    """Return a filter value as a list of strings, applying the list rules.

    A ``list`` or ``tuple`` is several values; a string or number is one value.

    Raises:
        ValueError: If the list is empty or holds an empty item.
        TypeError: If the value is another collection, such as a set or a
            generator, whose order or contents would be sent as its repr.
    """
    if isinstance(value, (list, tuple)):
        items = list(value)
    elif hasattr(value, "__iter__") and not isinstance(value, (str, bytes)):
        raise TypeError(
            f"{field} filter takes one value or a list of values, not a "
            f"{type(value).__name__}."
        )
    else:
        items = [value]
    if not items:
        raise ValueError(
            f"{field} filter got an empty list; pass None to skip the filter."
        )
    for item in items:
        if _is_absent(item):
            raise ValueError(f"{field} filter got an empty value in its list.")
    return [str(item) for item in items]


def _group(field: str, parts: list[str]) -> str:
    """Return ``field:p`` for one part, or ``field:(p1 OR p2)`` for several."""
    if len(parts) == 1:
        return f"{field}:{parts[0]}"
    return f"{field}:({' OR '.join(parts)})"


def _reject(field: str, value: str, expected: str, detail: str = "") -> NoReturn:
    """Raise the shared error for a value a filter cannot read.

    Args:
        field: The API field the value was for.
        value: The value as the caller gave it.
        expected: The forms the builder accepts, as a noun phrase.
        detail: An optional, more specific reason, such as a sanitizer message.
    """
    reason = f" ({detail})" if detail else ""
    raise ValueError(
        f"{field} filter cannot read {value!r}{reason}. Expected {expected}. "
        + _RAW_QUERY_HINT
    )


def _is_wildcard(text: str) -> bool:
    """Return True for a single-word wildcard pattern such as ``16*``."""
    return ("*" in text or "?" in text) and _WILDCARD_RE.match(text) is not None


def code(field: str, value: object) -> str | None:
    """Build a clause for a code field (numbers, type and category codes).

    Each value is sent exactly as given, so a hyphenated code such as
    ``IPR2022-01094`` matches; quoting or escaping it would not.

    Raises:
        ValueError: If a value is not a single code.
    """
    if _is_absent(value):
        return None
    parts = _values(field, value)
    for part in parts:
        if _CODE_RE.match(part) is None or part in _OPERATOR_WORDS:
            _reject(
                field,
                part,
                "a single code of letters, digits, '.', '_', or '-', such as "
                "CTNF or IPR2022-01094",
            )
    return _group(field, parts)


def text(field: str, value: object) -> str | None:
    """Build a clause for a text field (names, titles, categories).

    A single plain word is sent as is, so wildcards such as ``Smith*`` work.
    Any other value is quoted as a phrase, with backslashes and double quotes
    escaped. A wildcard inside a quoted value is searched as plain text. A
    word Lucene reads as an operator (``AND``, ``OR``, ``NOT``, ``TO``) is
    quoted, so it is searched as a word.
    """
    if _is_absent(value):
        return None
    parts = []
    for part in _values(field, value):
        plain = not _has_whitespace(part) and not any(
            c in _PHRASE_SPECIAL for c in part
        )
        if plain and part not in _OPERATOR_WORDS:
            parts.append(part)
        else:
            escaped = part.replace("\\", "\\\\").replace('"', '\\"')
            parts.append(f'"{escaped}"')
    return _group(field, parts)


def application_number(field: str, value: object) -> str | None:
    """Build a clause for an application-number field.

    Each value is converted with ``sanitize_application_number``, so
    ``14/412,875`` and ``14412875`` search the same way.

    Raises:
        ValueError: If a value is not one application number or a
            single-word wildcard pattern.
    """
    if _is_absent(value):
        return None
    parts = []
    for part in _values(field, value):
        if _is_wildcard(part):
            parts.append(part.upper())
            continue
        try:
            parts.append(sanitize_application_number(part))
        except ValueError as error:
            _reject(
                field,
                part,
                "an application number such as 14412875, 14/412,875, or "
                "PCT/US2024/012345, or a wildcard pattern such as 16*",
                str(error),
            )
    return _group(field, parts)


def publication_number(field: str, value: object) -> str | None:
    """Build a clause for a US publication-number field.

    The API stores publication numbers as ``USyyyyNNNNNNNAn`` (e.g.
    ``US20210138233A1``). Each value is reduced to its 11 digits (year +
    7-digit serial) inside wildcards, so any prefix or kind code matches.

    Raises:
        ValueError: If a value is not one publication number or a
            single-word wildcard pattern.
    """
    if _is_absent(value):
        return None
    parts = []
    for part in _values(field, value):
        if _is_wildcard(part):
            parts.append(part.upper())
            continue
        match = _PUBLICATION_NUMBER_RE.match(part.strip().upper())
        if match is None:
            _reject(
                field,
                part,
                "a US publication number such as 20210138233 or "
                "US 2021/0138233 A1, or a wildcard pattern such as US2021*",
            )
        parts.append(f"*{match.group(1)}{match.group(2)}*")
    return _group(field, parts)


def patent_number(field: str, value: object) -> str | None:
    """Build a clause for a patent-number field.

    The APIs store bare numbers (``10000000``, ``D1154285``, ``RE51038``).
    Each value loses a ``US`` prefix, whitespace, commas, hyphens, and a kind
    code, so ``US 10,000,000 B2`` searches for ``10000000``.

    Raises:
        ValueError: If a value is not one patent number or a single-word
            wildcard pattern.
    """
    if _is_absent(value):
        return None
    parts = []
    for part in _values(field, value):
        normalized = re.sub(r"[\s,\-]", "", part.upper())
        if _is_wildcard(normalized):
            parts.append(re.sub(r"^US(?=[0-9DRPHT*?])", "", normalized))
            continue
        match = _PATENT_NUMBER_RE.match(normalized)
        if match is None:
            _reject(
                field,
                part,
                "a patent number such as 10000000, D1154285, RE51038, or "
                "US 10,000,000 B2, or a wildcard pattern such as 1000000*",
            )
        parts.append(f"{match.group(1) or ''}{match.group(2)}")
    return _group(field, parts)


def pct_publication_number(field: str, value: object) -> str | None:
    """Build a clause for a PCT publication-number field.

    The API stores ``WO`` plus a 4-digit year and a 6-digit serial
    (``WO2026044302``). Each value loses whitespace, slashes, hyphens, and a
    kind code, and a pre-2004 two-digit-year form (``WO 03/106655``) becomes
    the current form (``WO2003106655``).

    Raises:
        ValueError: If a value is not one PCT publication number or a
            single-word wildcard pattern.
    """
    if _is_absent(value):
        return None
    parts = []
    for part in _values(field, value):
        normalized = re.sub(r"[\s/\-]", "", part.upper())
        if _is_wildcard(normalized):
            parts.append(normalized)
            continue
        match = _PCT_PUBLICATION_RE.match(normalized)
        if match is None:
            _reject(
                field,
                part,
                "a PCT publication number such as WO2026044302, "
                "WO 2026/044302 A1, or WO 03/106655, or a wildcard pattern "
                "such as WO2026*",
            )
        year, serial, short_year, short_serial = match.groups()
        if year is None:
            # Same window as PCT application numbers: YY >= 78 is 19YY.
            year = ("19" if int(short_year) >= 78 else "20") + short_year
            serial = short_serial.zfill(6)
        parts.append(f"WO{year}{serial}")
    return _group(field, parts)


def cpc_classification(field: str, value: object) -> str | None:
    """Build a clause for the CPC classification field.

    The API stores CPC symbols in a fixed-width form: the 4-character
    subclass, the main group right-aligned in 4 characters, ``/``, and the
    subgroup (``H01L  21/02``). Each value may be a full symbol
    (``H01L21/02``), a main group (``H01L21`` or ``H01L21*``, matching its
    subgroups), or a subclass (``H01L``, matching everything in it).

    Raises:
        ValueError: If a value is not one of those forms or a single-word
            wildcard pattern.
    """
    if _is_absent(value):
        return None
    parts = []
    for part in _values(field, value):
        normalized = part.strip().upper()
        symbol = _CPC_SYMBOL_RE.match(normalized)
        if symbol is not None:
            subclass, main, subgroup = symbol.groups()
            parts.append(f'"{subclass}{str(int(main)):>4}/{subgroup}"')
            continue
        group = _CPC_GROUP_RE.match(normalized) or _CPC_GROUP_WILDCARD_RE.match(
            normalized
        )
        if group is not None:
            subclass, main = group.groups()
            main = str(int(main))
            padding = _ESCAPED_SPACE * (4 - len(main))
            parts.append(subclass + padding + main + _ESCAPED_SLASH_WILDCARD)
            continue
        if _CPC_SUBCLASS_RE.match(normalized) is not None:
            parts.append(f"{normalized}*")
            continue
        if _is_wildcard(normalized):
            parts.append(normalized)
            continue
        _reject(
            field,
            part,
            "a CPC symbol such as H01L21/02, a main group such as H01L21, a "
            "subclass such as H01L, or a wildcard pattern such as H01*",
        )
    return _group(field, parts)


def boolean(field: str, value: bool | None) -> str | None:
    """Build ``field:true`` or ``field:false``."""
    if value is None:
        return None
    return f"{field}:{str(value).lower()}"


def date_range(field: str, start: object, end: object) -> str | None:
    """Build a date range clause from optional start and end dates."""
    has_start = not _is_absent(start)
    has_end = not _is_absent(end)
    if has_start and has_end:
        return f"{field}:[{start} TO {end}]"
    if has_start:
        return f"{field}:>={start}"
    if has_end:
        return f"{field}:<={end}"
    return None


def either(*clauses: str | None) -> str | None:
    """Join the present clauses with OR inside parentheses."""
    present = [c for c in clauses if c]
    if not present:
        return None
    if len(present) == 1:
        return present[0]
    return f"({' OR '.join(present)})"


def all_of(*clauses: str | None) -> str | None:
    """Join the present clauses with AND."""
    present = [c for c in clauses if c]
    if not present:
        return None
    return " AND ".join(present)
