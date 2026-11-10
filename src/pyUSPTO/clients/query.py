"""query - Shared builders for Lucene query clauses.

Each builder returns one ``field:value`` clause, or ``None`` when the filter is
absent (``None`` or ``""``), and formats its value with ``str()``. An empty
list raises ``ValueError``, so a mistaken ``[]`` never runs an unfiltered search.
Text values (``phrase``) are quoted when they contain whitespace or a Lucene
special character, with backslashes and double quotes escaped inside the
quotes. Code values (``term``) are sent as is, inside parentheses when they
contain whitespace, so the field applies to every term of an expression.
"""

import re

_PHRASE_SPECIAL = frozenset('+-&|!(){}[]^"~:\\/')

_PUBLICATION_NUMBER_RE = re.compile(
    r"^(?:US)?[\s/\-,]*(\d{4})[\s/\-,]*(\d{7})[\s/\-,]*(?:[A-Z]\d)?$"
)


def _is_absent(value: object) -> bool:
    """Return True for a filter value that should add no clause."""
    return value is None or value == ""


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


def _application_number_value(value: object) -> str:
    """Return the search value for an application-number field.

    Values that look like an application number are sanitized, so
    ``14/412,875`` and ``14412875`` search the same way. Values that contain a
    wildcard, or that the sanitizer rejects (such as range or ``OR``
    expressions), are returned inside parentheses, so the field applies to
    every term of the expression.
    """
    text = str(value)
    if "*" not in text:
        try:
            return sanitize_application_number(text)
        except ValueError:
            pass
    return f"({text})"


def application_number(field: str, value: object) -> str | None:
    """Build a clause for an application-number field."""
    if _is_absent(value):
        return None
    return f"{field}:{_application_number_value(value)}"


def publication_number(field: str, value: object) -> str | None:
    """Build a clause for a US publication-number field.

    The API stores publication numbers as ``USyyyyNNNNNNNAn`` (e.g.
    ``US20210138233A1``). The value is reduced to its 11 digits (year +
    7-digit serial) inside wildcards, so any prefix or kind code matches.
    Values that already contain a wildcard, or that do not look like a US
    publication number, are sent unchanged.
    """
    if _is_absent(value):
        return None
    text = str(value)
    if "*" in text:
        return f"{field}:{text}"
    match = _PUBLICATION_NUMBER_RE.match(text.strip().upper())
    if match is None:
        return f"{field}:{text}"
    return f"{field}:*{match.group(1)}{match.group(2)}*"


def term(field: str, value: object) -> str | None:
    """Build a clause for a code or number field.

    A value containing whitespace is wrapped in parentheses, so the field
    applies to every term of an expression such as ``1700 OR 2800``.
    """
    if _is_absent(value):
        return None
    text = str(value)
    if _has_whitespace(text):
        return f"{field}:({text})"
    return f"{field}:{text}"


def phrase(field: str, value: object) -> str | None:
    """Build a clause for a text field (names, titles, categories).

    A single plain word is sent as is, so wildcards such as ``Smith*`` still
    work. Any other value is quoted, with backslashes and double quotes
    escaped. A wildcard inside a quoted value is searched as plain text, so
    ``Smith-K*`` does not expand.
    """
    if _is_absent(value):
        return None
    text = str(value)
    if not _has_whitespace(text) and not any(c in _PHRASE_SPECIAL for c in text):
        return f"{field}:{text}"
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    return f'{field}:"{escaped}"'


def contains(field: str, value: object, *, quoted: bool = False) -> str | None:
    """Build a clause that matches the value anywhere in the field.

    With ``quoted``, backslashes and double quotes in the value are escaped.
    """
    if _is_absent(value):
        return None
    if quoted:
        escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
        return f'{field}:"*{escaped}*"'
    return f"{field}:*{value}*"


def any_of(field: str, value: object) -> str | None:
    """Build ``field:(a OR b)`` for a list, or a ``term`` for one value.

    Raises:
        ValueError: If the value is an empty list.
    """
    if _is_absent(value):
        return None
    if isinstance(value, list):
        if not value:
            raise ValueError(
                f"{field} filter got an empty list; pass None to skip the filter."
            )
        return f"{field}:({' OR '.join(str(v) for v in value)})"
    return term(field, value)


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
