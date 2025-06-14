"""
models.patent_data - Data models for USPTO patent data API

This module provides Pydantic-style data models, primarily using frozen
dataclasses, for representing responses from the USPTO Patent Data API.
It aims to offer more Pythonic representations (e.g., Enums, native
date/datetime objects) of the API's JSON data. Models cover aspects like
application metadata, party information (applicants, inventors, attorneys),
document details, continuity, assignments, and more.
"""

import csv
import io
import json
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone, tzinfo
from enum import Enum
from typing import Any, Dict, Iterator, List, Optional, Union
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# --- Timezone and Parsing Utilities ---
ASSUMED_NAIVE_TIMEZONE_STR = "America/New_York"
try:
    ASSUMED_NAIVE_TIMEZONE: Optional[tzinfo] = ZoneInfo(ASSUMED_NAIVE_TIMEZONE_STR)
except ZoneInfoNotFoundError:
    print(
        f"Warning: Timezone '{ASSUMED_NAIVE_TIMEZONE_STR}' not found. Naive datetimes will be treated as UTC or may cause errors."
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
            is not None. Returns None if `date_str` is None or if parsing fails,
            printing a warning in case of failure.
    """

    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, fmt).date()
    except ValueError:
        print(f"Warning: Could not parse date string '{date_str}' with format '{fmt}'")
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
            `datetime_str` is None or if parsing/conversion fails (in which
            case warnings may be printed).
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
        print(
            f"Warning: Could not parse datetime string '{datetime_str}' with any known format."
        )
        return None
    if dt_obj.tzinfo is None or dt_obj.tzinfo.utcoffset(dt_obj) is None:
        if ASSUMED_NAIVE_TIMEZONE:
            try:
                aware_dt = dt_obj.replace(tzinfo=ASSUMED_NAIVE_TIMEZONE)
                return aware_dt.astimezone(timezone.utc)
            except Exception as e:
                print(
                    f"Warning: Error localizing naive datetime '{datetime_str}': {e}."
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
            'N' or 'n'. Returns None if `value` is None or any other string
            (in which case a warning is printed for unexpected strings).
    """

    if value is None:
        return None
    if value.upper() == "Y":
        return True
    if value.upper() == "N":
        return False
    print(
        f"Warning: Unexpected value for Y/N boolean string: '{value}'. Treating as None."
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


# --- Enums for Categorical Data ---
class DirectionCategory(Enum):
    """Represents the direction of a document relative to the USPTO (e.g., INCOMING, OUTGOING)."""

    INCOMING = "INCOMING"
    OUTGOING = "OUTGOING"


class ActiveIndicator(Enum):
    """Represents an active or inactive status, often used for practitioners or entities.

    This Enum is designed to flexibly parse common string representations of
    active/inactive or true/false states (e.g., "Y", "N", "true", "false", "Active")
    into standardized Enum members.
    """

    YES = "Y"
    NO = "N"
    TRUE = "true"
    FALSE = "false"
    ACTIVE = "Active"

    @classmethod
    def _missing_(cls, value: Any) -> "ActiveIndicator":
        if isinstance(value, str):
            val_upper = value.upper()
            if val_upper == "Y":
                return cls.YES
            if val_upper == "N":
                return cls.NO
            if val_upper == "TRUE":
                return cls.TRUE
            if val_upper == "FALSE":
                return cls.FALSE
            if val_upper == "ACTIVE":
                return cls.ACTIVE
        return super()._missing_(value=value)  # type: ignore[no-any-return]


# --- Data Models ---
@dataclass(frozen=True)
class DocumentFormat:
    """Represents an available download format for a specific document.

    Attributes:
        mime_type_identifier: The MIME type of the downloadable file (e.g., "PDF").
        download_url: The URL from which the document format can be downloaded.
        page_total_quantity: The total number of pages in this document format.
    """

    mime_type_identifier: Optional[str] = None
    download_url: Optional[str] = None
    page_total_quantity: Optional[int] = None

    def __str__(self) -> str:
        return (
            f"{self.mime_type_identifier} format with {self.page_total_quantity} pages"
        )

    def __repr__(self) -> str:
        return f"DocumentFormat(mime_type={self.mime_type_identifier}, pages={self.page_total_quantity})"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentFormat":
        """Creates a `DocumentFormat` instance from a dictionary representation.

        This factory method is typically used to construct `DocumentFormat`
        objects from data parsed from an API JSON response. It maps
        dictionary keys (expected in camelCase) to the class attributes.

        Args:
            data (Dict[str, Any]): A dictionary containing the data for a
                `DocumentFormat`. Expected keys from the API are
                "mimeTypeIdentifier", "downloadUrl", and "pageTotalQuantity".

        Returns:
            DocumentFormat: An instance of `DocumentFormat` initialized with
                data from the input dictionary.
        """

        return cls(
            mime_type_identifier=data.get("mimeTypeIdentifier"),
            download_url=data.get("downloadUrl"),
            page_total_quantity=data.get("pageTotalQuantity"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the `DocumentFormat` instance to a dictionary.

        This method serializes the `DocumentFormat` object into a dictionary,
        mapping the instance's attributes to camelCase keys. This is typically
        useful for generating JSON representations compatible with API expectations.

        Returns:
            Dict[str, Any]: A dictionary representation of the `DocumentFormat`
                instance with keys "mimeTypeIdentifier", "downloadUrl", and
                "pageTotalQuantity".
        """

        return {
            "mimeTypeIdentifier": self.mime_type_identifier,
            "downloadUrl": self.download_url,
            "pageTotalQuantity": self.page_total_quantity,
        }


@dataclass(frozen=True)
class Document:
    """Represents a single document associated with a patent application.

    This includes metadata such as its identifier, official date, code, description,
    direction (incoming/outgoing), and available download formats.

    Attributes:
        application_number_text: The application number this document belongs to.
        official_date: The official date of the document.
        document_identifier: A unique identifier for this document.
        document_code: A code representing the type of document.
        document_code_description_text: A textual description of the document code.
        direction_category: The direction of the document (e.g., INCOMING, OUTGOING).
        document_formats: A list of available download formats for this document.
    """

    application_number_text: Optional[str] = None
    official_date: Optional[datetime] = None
    document_identifier: Optional[str] = None
    document_code: Optional[str] = None
    document_code_description_text: Optional[str] = None
    direction_category: Optional[DirectionCategory] = None
    document_formats: List[DocumentFormat] = field(default_factory=list)

    def __str__(self) -> str:
        date_str = (
            self.official_date.strftime("%Y-%m-%d") if self.official_date else "No date"
        )
        return f"Document {self.document_identifier} ({self.document_code}): {self.document_code_description_text} - {date_str}"

    def __repr__(self) -> str:
        return f"Document(id={self.document_identifier}, code={self.document_code}, date={self.official_date.strftime('%Y-%m-%d') if self.official_date else 'None'})"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Document":
        """Creates a `Document` instance from a dictionary representation.

        Maps API JSON keys (camelCase) to class attributes, parsing nested
        objects like `DocumentFormat` and `DirectionCategory`.

        Args:
            data (Dict[str, Any]): A dictionary containing document data,
                typically from an API response.

        Returns:
            Document: An instance of `Document`.
        """

        dl_formats = [
            DocumentFormat.from_dict(f)
            for f in data.get("downloadOptionBag", [])
            if isinstance(f, dict)
        ]
        dir_val = data.get("documentDirectionCategory")
        dir_cat = None
        if dir_val:
            try:
                dir_cat = DirectionCategory(dir_val)
            except ValueError:
                print(f"Warning: Unknown document direction category '{dir_val}'.")
        return cls(
            application_number_text=data.get("applicationNumberText"),
            official_date=parse_to_datetime_utc(data.get("officialDate")),
            document_identifier=data.get("documentIdentifier"),
            document_code=data.get("documentCode"),
            document_code_description_text=data.get("documentCodeDescriptionText"),
            direction_category=dir_cat,
            document_formats=dl_formats,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the `Document` instance to a dictionary for API compatibility.

        Serializes attributes to camelCase keys and handles nested objects.
        Omits keys with None values or empty lists.

        Returns:
            Dict[str, Any]: A dictionary representation of the `Document`.
        """

        d = {
            "applicationNumberText": self.application_number_text,
            "officialDate": serialize_datetime_as_iso(self.official_date),
            "documentIdentifier": self.document_identifier,
            "documentCode": self.document_code,
            "documentCodeDescriptionText": self.document_code_description_text,
            "documentDirectionCategory": (
                self.direction_category.value if self.direction_category else None
            ),
            "downloadOptionBag": [df.to_dict() for df in self.document_formats],
        }
        return {
            k: v
            for k, v in d.items()
            if v is not None and (not isinstance(v, list) or v)
        }


class DocumentBag:
    """A collection of Document objects associated with a patent application.

    Provides iterable access and standard collection methods like `len` and `getitem`.
    This class is immutable by convention after initialization.

    Attributes:
        documents (tuple[Document, ...]): An immutable tuple of `Document` objects.
    """

    def __init__(self, documents: List[Document]):
        """Initializes the DocumentBag with a list of documents.

        Args:
            documents (List[Document]): A list of `Document` instances.
        """
        self._documents = tuple(documents)

    @property
    def documents(self) -> tuple[Document, ...]:
        """Provides access to the tuple of documents."""
        return self._documents

    def __iter__(self) -> Iterator[Document]:
        return iter(self._documents)

    def __len__(self) -> int:
        return len(self._documents)

    def __getitem__(self, index: int) -> Document:
        return self._documents[index]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentBag":
        """Creates a `DocumentBag` instance from a dictionary representation.

        Expects a dictionary with a "documentBag" key containing a list of
        document data dictionaries.

        Args:
            data (Dict[str, Any]): A dictionary, typically from an API response,
                containing the document bag.

        Returns:
            DocumentBag: An instance of `DocumentBag`.
        """
        docs_data = data.get("documentBag", [])
        docs = (
            [Document.from_dict(dd) for dd in docs_data if isinstance(dd, dict)]
            if isinstance(docs_data, list)
            else []
        )
        return cls(documents=docs)

    def to_dict(self) -> Dict[str, Any]:
        """Converts the `DocumentBag` instance to a dictionary.

        Serializes the collection into a dictionary with a "documentBag" key,
        containing a list of `Document` dictionaries.

        Returns:
            Dict[str, Any]: A dictionary representation of the `DocumentBag`.
        """
        return {"documentBag": [doc.to_dict() for doc in self._documents]}


@dataclass(frozen=True)
class Address:
    """Represents a postal address with fields for street, city, region, country, and postal code.

    It can be used for various entities like applicants, inventors, or correspondence.

    Attributes:
        name_line_one_text: First line of the name (e.g., company name).
        name_line_two_text: Second line of the name.
        address_line_one_text: First line of the street address.
        address_line_two_text: Second line of the street address.
        address_line_three_text: Third line of the street address.
        address_line_four_text: Fourth line of the street address.
        geographic_region_name: Name of the geographic region (e.g., state, province).
        geographic_region_code: Code for the geographic region.
        postal_code: Postal or ZIP code.
        city_name: Name of the city.
        country_code: Two-letter country code (e.g., "US").
        country_name: Full name of the country (e.g., "United States").
        postal_address_category: Category of the address (e.g., "MAILING_ADDRESS").
        correspondent_name_text: Name of the correspondent at this address.
    """

    name_line_one_text: Optional[str] = None
    name_line_two_text: Optional[str] = None
    address_line_one_text: Optional[str] = None
    address_line_two_text: Optional[str] = None
    address_line_three_text: Optional[str] = None
    address_line_four_text: Optional[str] = None
    geographic_region_name: Optional[str] = None
    geographic_region_code: Optional[str] = None
    postal_code: Optional[str] = None
    city_name: Optional[str] = None
    country_code: Optional[str] = None
    country_name: Optional[str] = None
    postal_address_category: Optional[str] = None
    correspondent_name_text: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Address":
        """Creates an `Address` instance from a dictionary representation.

        Maps camelCase keys from API data to class attributes.

        Args:
            data (Dict[str, Any]): Dictionary containing address data.

        Returns:
            Address: An instance of `Address`.
        """
        return cls(
            name_line_one_text=data.get("nameLineOneText"),
            name_line_two_text=data.get("nameLineTwoText"),
            address_line_one_text=data.get("addressLineOneText"),
            address_line_two_text=data.get("addressLineTwoText"),
            address_line_three_text=data.get("addressLineThreeText"),
            address_line_four_text=data.get("addressLineFourText"),
            geographic_region_name=data.get("geographicRegionName"),
            geographic_region_code=data.get("geographicRegionCode"),
            postal_code=data.get("postalCode"),
            city_name=data.get("cityName"),
            country_code=data.get("countryCode"),
            country_name=data.get("countryName"),
            postal_address_category=data.get("postalAddressCategory"),
            correspondent_name_text=data.get("correspondentNameText"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the `Address` instance to a dictionary with camelCase keys.

        Returns:
            Dict[str, Any]: A dictionary representation of the address.
        """

        return {
            "nameLineOneText": self.name_line_one_text,
            "nameLineTwoText": self.name_line_two_text,
            "addressLineOneText": self.address_line_one_text,
            "addressLineTwoText": self.address_line_two_text,
            "addressLineThreeText": self.address_line_three_text,
            "addressLineFourText": self.address_line_four_text,
            "geographicRegionName": self.geographic_region_name,
            "geographicRegionCode": self.geographic_region_code,
            "postalCode": self.postal_code,
            "cityName": self.city_name,
            "countryCode": self.country_code,
            "countryName": self.country_name,
            "postalAddressCategory": self.postal_address_category,
            "correspondentNameText": self.correspondent_name_text,
        }


@dataclass(frozen=True)
class Telecommunication:
    """Represents telecommunication details, such as phone or fax numbers.

    Attributes:
        telecommunication_number: The main number (e.g., phone number).
        extension_number: Any extension associated with the number.
        telecom_type_code: A code indicating the type of telecommunication (e.g., "TEL", "FAX").
    """

    telecommunication_number: Optional[str] = None
    extension_number: Optional[str] = None
    telecom_type_code: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Telecommunication":
        """Creates a `Telecommunication` instance from a dictionary.

        Args:
            data (Dict[str, Any]): Dictionary with telecommunication data.

        Returns:
            Telecommunication: An instance of `Telecommunication`.
        """
        return cls(
            telecommunication_number=data.get("telecommunicationNumber"),
            extension_number=data.get("extensionNumber"),
            telecom_type_code=data.get("telecomTypeCode"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the `Telecommunication` instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation with camelCase keys.
        """
        return {
            "telecommunicationNumber": self.telecommunication_number,
            "extensionNumber": self.extension_number,
            "telecomTypeCode": self.telecom_type_code,
        }


@dataclass(frozen=True)
class Person:
    """A base data class representing a person with common name and country attributes.

    This class is typically inherited by more specific types like Applicant, Inventor, or Attorney.

    Attributes:
        first_name: The first name of the person.
        middle_name: The middle name or initial of the person.
        last_name: The last name or surname of the person.
        name_prefix: A prefix for the name (e.g., "Dr.", "Mr.").
        name_suffix: A suffix for the name (e.g., "Jr.", "PhD").
        preferred_name: The person's preferred name, if different.
        country_code: The country code associated with the person (e.g., citizenship).
    """

    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    name_prefix: Optional[str] = None
    name_suffix: Optional[str] = None
    preferred_name: Optional[str] = None
    country_code: Optional[str] = None

    @classmethod
    def _extract_person_fields(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "first_name": data.get("firstName"),
            "middle_name": data.get("middleName"),
            "last_name": data.get("lastName"),
            "name_prefix": data.get("namePrefix"),
            "name_suffix": data.get("nameSuffix"),
            "preferred_name": data.get("preferredName"),
            "country_code": data.get("countryCode"),
        }

    def to_dict(self) -> Dict[str, Any]:
        """Converts the `Person` instance to a dictionary with camelCase keys.

        Omits attributes that are None.

        Returns:
            Dict[str, Any]: A dictionary representation of the person.
        """
        return {to_camel_case(k): v for k, v in asdict(self).items() if v is not None}


@dataclass(frozen=True)
class Applicant(Person):
    """Represents an applicant for a patent, inheriting from Person.

    Includes applicant-specific name text and a list of correspondence addresses.

    Attributes:
        applicant_name_text: The full name of the applicant as a single string.
        correspondence_address_bag: A list of `Address` objects for the applicant.
    """

    applicant_name_text: Optional[str] = None
    correspondence_address_bag: List[Address] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Applicant":
        """Creates an `Applicant` instance from a dictionary.

        Inherits person fields and adds applicant-specific fields.

        Args:
            data (Dict[str, Any]): Dictionary with applicant data.

        Returns:
            Applicant: An instance of `Applicant`.
        """
        pf = Person._extract_person_fields(data)
        addrs = [
            Address.from_dict(a)
            for a in data.get("correspondenceAddressBag", [])
            if isinstance(a, dict)
        ]
        return cls(
            **pf,
            applicant_name_text=data.get("applicantNameText"),
            correspondence_address_bag=addrs,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the `Applicant` instance to a dictionary.

        Includes inherited person fields and applicant-specific fields,
        using camelCase keys and omitting None values or empty lists.

        Returns:
            Dict[str, Any]: Dictionary representation of the applicant.
        """
        d = super().to_dict()
        d.update(
            {
                "applicantNameText": self.applicant_name_text,
                "correspondenceAddressBag": [
                    a.to_dict() for a in self.correspondence_address_bag
                ],
            }
        )
        return {
            k: v
            for k, v in d.items()
            if v is not None and (not isinstance(v, list) or v)
        }


@dataclass(frozen=True)
class Inventor(Person):
    """Represents an inventor for a patent application, inheriting from Person.

    Includes inventor-specific name text and a list of correspondence addresses.

    Attributes:
        inventor_name_text: The full name of the inventor as a single string.
        correspondence_address_bag: A list of `Address` objects for the inventor.
    """

    inventor_name_text: Optional[str] = None
    correspondence_address_bag: List[Address] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Inventor":
        """Creates an `Inventor` instance from a dictionary.

        Inherits person fields and adds inventor-specific fields.

        Args:
            data (Dict[str, Any]): Dictionary with inventor data.

        Returns:
            Inventor: An instance of `Inventor`.
        """
        pf = Person._extract_person_fields(data)
        addrs = [
            Address.from_dict(a)
            for a in data.get("correspondenceAddressBag", [])
            if isinstance(a, dict)
        ]
        return cls(
            **pf,
            inventor_name_text=data.get("inventorNameText"),
            correspondence_address_bag=addrs,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the `Inventor` instance to a dictionary.

        Includes inherited person fields and inventor-specific fields,
        using camelCase keys and omitting None values or empty lists.

        Returns:
            Dict[str, Any]: Dictionary representation of the inventor.
        """
        d = super().to_dict()
        d.update(
            {
                "inventorNameText": self.inventor_name_text,
                "correspondenceAddressBag": [
                    a.to_dict() for a in self.correspondence_address_bag
                ],
            }
        )
        return {
            k: v
            for k, v in d.items()
            if v is not None and (not isinstance(v, list) or v)
        }


@dataclass(frozen=True)
class Attorney(Person):
    """Represents an attorney or agent associated with a patent application, inheriting from Person.

    Includes registration number, active status, practitioner category, addresses, and telecommunication details.

    Attributes:
        registration_number: The attorney's USPTO registration number.
        active_indicator: Indicates if the attorney is currently active (e.g., "Y", "N").
        registered_practitioner_category: Category of the practitioner (e.g., "ATTORNEY", "AGENT").
        attorney_address_bag: List of `Address` objects for the attorney.
        telecommunication_address_bag: List of `Telecommunication` objects for the attorney.
    """

    registration_number: Optional[str] = None
    active_indicator: Optional[str] = None
    registered_practitioner_category: Optional[str] = None
    attorney_address_bag: List[Address] = field(default_factory=list)
    telecommunication_address_bag: List[Telecommunication] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Attorney":
        """Creates an `Attorney` instance from a dictionary.

        Inherits person fields and adds attorney-specific details.

        Args:
            data (Dict[str, Any]): Dictionary with attorney data.

        Returns:
            Attorney: An instance of `Attorney`.
        """
        pf = Person._extract_person_fields(data)
        addrs = [
            Address.from_dict(a)
            for a in data.get("attorneyAddressBag", [])
            if isinstance(a, dict)
        ]
        telecoms = [
            Telecommunication.from_dict(t)
            for t in data.get("telecommunicationAddressBag", [])
            if isinstance(t, dict)
        ]
        return cls(
            **pf,
            registration_number=data.get("registrationNumber"),
            active_indicator=data.get("activeIndicator"),
            registered_practitioner_category=data.get("registeredPractitionerCategory"),
            attorney_address_bag=addrs,
            telecommunication_address_bag=telecoms,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the `Attorney` instance to a dictionary.

        Includes inherited person fields and attorney-specific fields,
        using camelCase keys and omitting None values or empty lists.

        Returns:
            Dict[str, Any]: Dictionary representation of the attorney.
        """
        d = super().to_dict()
        d.update(
            {
                "registrationNumber": self.registration_number,
                "activeIndicator": self.active_indicator,
                "registeredPractitionerCategory": self.registered_practitioner_category,
                "attorneyAddressBag": [a.to_dict() for a in self.attorney_address_bag],
                "telecommunicationAddressBag": [
                    t.to_dict() for t in self.telecommunication_address_bag
                ],
            }
        )
        return {
            k: v
            for k, v in d.items()
            if v is not None and (not isinstance(v, list) or v)
        }


@dataclass(frozen=True)
class EntityStatus:
    """Represents the entity status of an applicant (e.g., small entity status).

    Attributes:
        small_entity_status_indicator: Boolean indicating if the applicant qualifies for small entity status.
        business_entity_status_category: String category of the business entity status (e.g., "Undiscounted").
    """

    small_entity_status_indicator: Optional[bool] = None
    business_entity_status_category: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EntityStatus":
        """Creates an `EntityStatus` instance from a dictionary.

        Args:
            data (Dict[str, Any]): Dictionary with entity status data.

        Returns:
            EntityStatus: An instance of `EntityStatus`.
        """
        return cls(
            small_entity_status_indicator=data.get("smallEntityStatusIndicator"),
            business_entity_status_category=data.get("businessEntityStatusCategory"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the `EntityStatus` instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation with camelCase keys.
        """
        return {
            "smallEntityStatusIndicator": self.small_entity_status_indicator,
            "businessEntityStatusCategory": self.business_entity_status_category,
        }


@dataclass(frozen=True)
class CustomerNumberCorrespondence:
    """Represents correspondence data associated with a USPTO customer number.

    Includes patron identifier, organization name, power of attorney addresses, and telecommunication details.

    Attributes:
        patron_identifier: The USPTO customer number.
        organization_standard_name: The name of the organization associated with the customer number.
        power_of_attorney_address_bag: List of `Address` objects for power of attorney.
        telecommunication_address_bag: List of `Telecommunication` objects.
    """

    patron_identifier: Optional[int] = None
    organization_standard_name: Optional[str] = None
    power_of_attorney_address_bag: List[Address] = field(default_factory=list)
    telecommunication_address_bag: List[Telecommunication] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CustomerNumberCorrespondence":
        """Creates a `CustomerNumberCorrespondence` instance from a dictionary.

        Args:
            data (Dict[str, Any]): Dictionary with customer number correspondence data.

        Returns:
            CustomerNumberCorrespondence: An instance of `CustomerNumberCorrespondence`.
        """
        addrs = [
            Address.from_dict(a)
            for a in data.get("powerOfAttorneyAddressBag", [])
            if isinstance(a, dict)
        ]
        telecoms = [
            Telecommunication.from_dict(t)
            for t in data.get("telecommunicationAddressBag", [])
            if isinstance(t, dict)
        ]
        return cls(
            patron_identifier=data.get("patronIdentifier"),
            organization_standard_name=data.get("organizationStandardName"),
            power_of_attorney_address_bag=addrs,
            telecommunication_address_bag=telecoms,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the `CustomerNumberCorrespondence` instance to a dictionary.

        Omits keys with None values or empty lists.

        Returns:
            Dict[str, Any]: Dictionary representation.
        """
        d = {
            "patronIdentifier": self.patron_identifier,
            "organizationStandardName": self.organization_standard_name,
            "powerOfAttorneyAddressBag": [
                a.to_dict() for a in self.power_of_attorney_address_bag
            ],
            "telecommunicationAddressBag": [
                t.to_dict() for t in self.telecommunication_address_bag
            ],
        }
        return {
            k: v
            for k, v in d.items()
            if v is not None and (not isinstance(v, list) or v)
        }


@dataclass(frozen=True)
class RecordAttorney:
    """Represents information about the attorney(s) of record for a patent application.

    Contains customer number correspondence data, power of attorney information, and listed attorneys.

    Attributes:
        customer_number_correspondence_data: List of `CustomerNumberCorrespondence` objects.
        power_of_attorney_bag: List of `Attorney` objects named in a power of attorney.
        attorney_bag: List of `Attorney` objects listed as attorneys of record.
    """

    customer_number_correspondence_data: List[CustomerNumberCorrespondence] = field(
        default_factory=list
    )
    power_of_attorney_bag: List[Attorney] = field(default_factory=list)
    attorney_bag: List[Attorney] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RecordAttorney":
        """Creates a `RecordAttorney` instance from a dictionary.

        Args:
            data (Dict[str, Any]): Dictionary with record attorney data.

        Returns:
            RecordAttorney: An instance of `RecordAttorney`.
        """
        cust_corr = [
            CustomerNumberCorrespondence.from_dict(c)
            for c in data.get("customerNumberCorrespondenceData", [])
            if isinstance(c, dict)
        ]
        poa_bag = [
            Attorney.from_dict(a)
            for a in data.get("powerOfAttorneyBag", [])
            if isinstance(a, dict)
        ]
        att_bag = [
            Attorney.from_dict(a)
            for a in data.get("attorneyBag", [])
            if isinstance(a, dict)
        ]
        return cls(
            customer_number_correspondence_data=cust_corr,
            power_of_attorney_bag=poa_bag,
            attorney_bag=att_bag,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the `RecordAttorney` instance to a dictionary.

        Omits keys with None values or empty lists.

        Returns:
            Dict[str, Any]: Dictionary representation.
        """
        d = {
            "customerNumberCorrespondenceData": [
                c.to_dict() for c in self.customer_number_correspondence_data
            ],
            "powerOfAttorneyBag": [p.to_dict() for p in self.power_of_attorney_bag],
            "attorneyBag": [a.to_dict() for a in self.attorney_bag],
        }
        return {
            k: v
            for k, v in d.items()
            if v is not None and (not isinstance(v, list) or v)
        }


@dataclass(frozen=True)
class Assignor:
    """Represents an assignor in a patent assignment.

    Attributes:
        assignor_name: The name of the assigning party.
        execution_date: The date the assignment was executed.
    """

    assignor_name: Optional[str] = None
    execution_date: Optional[date] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Assignor":
        """Creates an `Assignor` instance from a dictionary.

        Args:
            data (Dict[str, Any]): Dictionary with assignor data.

        Returns:
            Assignor: An instance of `Assignor`.
        """
        return cls(
            assignor_name=data.get("assignorName"),
            execution_date=parse_to_date(data.get("executionDate")),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the `Assignor` instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation with camelCase keys.
        """
        return {
            "assignorName": self.assignor_name,
            "executionDate": serialize_date(self.execution_date),
        }


@dataclass(frozen=True)
class Assignee:
    """Represents an assignee in a patent assignment.

    Attributes:
        assignee_name_text: The name of the party receiving the assignment.
        assignee_address: The `Address` of the assignee.
    """

    assignee_name_text: Optional[str] = None
    assignee_address: Optional[Address] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Assignee":
        """Creates an `Assignee` instance from a dictionary.

        Args:
            data (Dict[str, Any]): Dictionary with assignee data.

        Returns:
            Assignee: An instance of `Assignee`.
        """
        addr_data = data.get("assigneeAddress")
        addr = Address.from_dict(addr_data) if isinstance(addr_data, dict) else None
        return cls(
            assignee_name_text=data.get("assigneeNameText"), assignee_address=addr
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the `Assignee` instance to a dictionary.

        Omits keys with None values.

        Returns:
            Dict[str, Any]: Dictionary representation.
        """
        d = {
            "assigneeNameText": self.assignee_name_text,
            "assigneeAddress": (
                self.assignee_address.to_dict() if self.assignee_address else None
            ),
        }
        return {k: v for k, v in d.items() if v is not None}


@dataclass(frozen=True)
class Assignment:
    """Represents a patent assignment, detailing the transfer of rights.

    Includes information about the reel and frame, document location, dates, conveyance text,
    and bags of assignors, assignees, and correspondence addresses.

    Attributes:
        reel_number: Reel number for the assignment record.
        frame_number: Frame number for the assignment record.
        reel_and_frame_number: Combined reel and frame number.
        assignment_document_location_uri: URI for the assignment document.
        assignment_received_date: Date the assignment was received by USPTO.
        assignment_recorded_date: Date the assignment was recorded by USPTO.
        assignment_mailed_date: Date the assignment notification was mailed.
        conveyance_text: Text describing the nature of the conveyance.
        assignor_bag: List of `Assignor` objects.
        assignee_bag: List of `Assignee` objects.
        correspondence_address_bag: List of `Address` objects for correspondence.
    """

    reel_number: Optional[str] = None
    frame_number: Optional[str] = None
    reel_and_frame_number: Optional[str] = None
    assignment_document_location_uri: Optional[str] = None
    assignment_received_date: Optional[date] = None
    assignment_recorded_date: Optional[date] = None
    assignment_mailed_date: Optional[date] = None
    conveyance_text: Optional[str] = None
    assignor_bag: List[Assignor] = field(default_factory=list)
    assignee_bag: List[Assignee] = field(default_factory=list)
    correspondence_address_bag: List[Address] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Assignment":
        """Creates an `Assignment` instance from a dictionary.

        Args:
            data (Dict[str, Any]): Dictionary with assignment data.

        Returns:
            Assignment: An instance of `Assignment`.
        """
        assignors = [
            Assignor.from_dict(a)
            for a in data.get("assignorBag", [])
            if isinstance(a, dict)
        ]
        assignees = [
            Assignee.from_dict(a)
            for a in data.get("assigneeBag", [])
            if isinstance(a, dict)
        ]
        addrs = [
            Address.from_dict(a)
            for a in data.get("correspondenceAddressBag", [])
            if isinstance(a, dict)
        ]
        return cls(
            reel_number=data.get("reelNumber"),
            frame_number=data.get("frameNumber"),
            reel_and_frame_number=data.get("reelAndFrameNumber"),
            assignment_document_location_uri=data.get("assignmentDocumentLocationURI"),
            assignment_received_date=parse_to_date(data.get("assignmentReceivedDate")),
            assignment_recorded_date=parse_to_date(data.get("assignmentRecordedDate")),
            assignment_mailed_date=parse_to_date(data.get("assignmentMailedDate")),
            conveyance_text=data.get("conveyanceText"),
            assignor_bag=assignors,
            assignee_bag=assignees,
            correspondence_address_bag=addrs,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the `Assignment` instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation with camelCase keys.
        """
        return {
            "reelNumber": self.reel_number,
            "frameNumber": self.frame_number,
            "reelAndFrameNumber": self.reel_and_frame_number,
            "assignmentDocumentLocationURI": self.assignment_document_location_uri,
            "assignmentReceivedDate": serialize_date(self.assignment_received_date),
            "assignmentRecordedDate": serialize_date(self.assignment_recorded_date),
            "assignmentMailedDate": serialize_date(self.assignment_mailed_date),
            "conveyanceText": self.conveyance_text,
            "assignorBag": [a.to_dict() for a in self.assignor_bag],
            "assigneeBag": [a.to_dict() for a in self.assignee_bag],
            "correspondenceAddressBag": [
                a.to_dict() for a in self.correspondence_address_bag
            ],
        }


@dataclass(frozen=True)
class ForeignPriority:
    """Represents a foreign priority claim for a patent application.

    Attributes:
        ip_office_name: The name of the intellectual property office of the priority application.
        filing_date: The filing date of the priority application.
        application_number_text: The application number of the priority application.
    """

    ip_office_name: Optional[str] = None
    filing_date: Optional[date] = None
    application_number_text: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ForeignPriority":
        """Creates a `ForeignPriority` instance from a dictionary.

        Args:
            data (Dict[str, Any]): Dictionary with foreign priority data.

        Returns:
            ForeignPriority: An instance of `ForeignPriority`.
        """
        return cls(
            ip_office_name=data.get("ipOfficeName"),
            filing_date=parse_to_date(data.get("filingDate")),
            application_number_text=data.get("applicationNumberText"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the `ForeignPriority` instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation with camelCase keys.
        """
        return {
            "ipOfficeName": self.ip_office_name,
            "filingDate": serialize_date(self.filing_date),
            "applicationNumberText": self.application_number_text,
        }


@dataclass(frozen=True)
class Continuity:
    """Base class representing continuity data for a patent application.

    This includes details about the application's relationship to other applications (parent/child),
    its filing status under AIA (America Invents Act), and key identifiers.

    Attributes:
        first_inventor_to_file_indicator: Boolean indicating if the application is under First-Inventor-to-File provisions.
        application_number_text: The application number of the related (parent or child) application.
        filing_date: The filing date of the related application.
        status_code: The status code of the related application.
        status_description_text: The status description of the related application.
        patent_number: The patent number if the related application is granted.
        claim_parentage_type_code: Code indicating the type of continuity claim (e.g., "CON", "DIV").
        claim_parentage_type_code_description_text: Description of the continuity claim type.
    """

    first_inventor_to_file_indicator: Optional[bool] = None
    application_number_text: Optional[str] = None
    filing_date: Optional[date] = None
    status_code: Optional[int] = None
    status_description_text: Optional[str] = None
    patent_number: Optional[str] = None
    claim_parentage_type_code: Optional[str] = None
    claim_parentage_type_code_description_text: Optional[str] = None

    @property
    def is_aia(self) -> Optional[bool]:
        """Returns True if the application is AIA, False if pre-AIA, None if unknown."""
        return self.first_inventor_to_file_indicator

    @property
    def is_pre_aia(self) -> Optional[bool]:
        """Returns True if the application is pre-AIA, False if AIA, None if unknown."""
        if self.first_inventor_to_file_indicator is None:
            return None
        return not self.first_inventor_to_file_indicator

    def to_dict(self) -> Dict[str, Any]:
        """Converts the `Continuity` instance to a dictionary.

        Omits attributes that are None and property-derived fields.
        Keys are converted to camelCase.

        Returns:
            Dict[str, Any]: A dictionary representation of the continuity data.
        """
        return {
            to_camel_case(k): v
            for k, v in asdict(self).items()
            if v is not None and not k.startswith("is_")
        }


@dataclass(frozen=True)
class ParentContinuity(Continuity):
    """Represents a parent application in a patent application's continuity chain.

    Inherits from Continuity and adds specific fields for parent application details.

    Attributes:
        parent_application_status_code: Status code of the parent application.
        parent_patent_number: Patent number of the parent application, if granted.
        parent_application_status_description_text: Status description of the parent application.
        parent_application_filing_date: Filing date of the parent application.
        parent_application_number_text: Application number of the parent application.
        child_application_number_text: Application number of the child (current) application.
    """

    parent_application_status_code: Optional[int] = None
    parent_patent_number: Optional[str] = None
    parent_application_status_description_text: Optional[str] = None
    parent_application_filing_date: Optional[date] = None
    parent_application_number_text: Optional[str] = None
    child_application_number_text: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ParentContinuity":
        """Creates a `ParentContinuity` instance from a dictionary.

        Args:
            data (Dict[str, Any]): Dictionary with parent continuity data.

        Returns:
            ParentContinuity: An instance of `ParentContinuity`.
        """
        p_filing_date = parse_to_date(data.get("parentApplicationFilingDate"))
        return cls(
            first_inventor_to_file_indicator=data.get("firstInventorToFileIndicator"),
            parent_application_status_code=data.get("parentApplicationStatusCode"),
            parent_patent_number=data.get("parentPatentNumber"),
            parent_application_status_description_text=data.get(
                "parentApplicationStatusDescriptionText"
            ),
            parent_application_filing_date=p_filing_date,
            parent_application_number_text=data.get("parentApplicationNumberText"),
            child_application_number_text=data.get("childApplicationNumberText"),
            claim_parentage_type_code=data.get("claimParentageTypeCode"),
            claim_parentage_type_code_description_text=data.get(
                "claimParentageTypeCodeDescriptionText"
            ),
            application_number_text=data.get("parentApplicationNumberText"),
            filing_date=p_filing_date,
            status_code=data.get("parentApplicationStatusCode"),
            status_description_text=data.get("parentApplicationStatusDescriptionText"),
            patent_number=data.get("parentPatentNumber"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the `ParentContinuity` instance to a dictionary.

        Maps attributes to specific camelCase keys expected by the API for parent continuity.

        Returns:
            Dict[str, Any]: Dictionary representation.
        """
        return {
            "firstInventorToFileIndicator": self.first_inventor_to_file_indicator,
            "parentApplicationStatusCode": self.parent_application_status_code,
            "parentPatentNumber": self.parent_patent_number,
            "parentApplicationStatusDescriptionText": self.parent_application_status_description_text,
            "parentApplicationFilingDate": serialize_date(
                self.parent_application_filing_date
            ),
            "parentApplicationNumberText": self.parent_application_number_text,
            "childApplicationNumberText": self.child_application_number_text,
            "claimParentageTypeCode": self.claim_parentage_type_code,
            "claimParentageTypeCodeDescriptionText": self.claim_parentage_type_code_description_text,
        }


@dataclass(frozen=True)
class ChildContinuity(Continuity):
    """Represents a child application in a patent application's continuity chain.

    Inherits from Continuity and adds specific fields for child application details.

    Attributes:
        child_application_status_code: Status code of the child application.
        parent_application_number_text: Application number of the parent (current) application.
        child_application_number_text: Application number of the child application.
        child_application_status_description_text: Status description of the child application.
        child_application_filing_date: Filing date of the child application.
        child_patent_number: Patent number of the child application, if granted.
    """

    child_application_status_code: Optional[int] = None
    parent_application_number_text: Optional[str] = None
    child_application_number_text: Optional[str] = None
    child_application_status_description_text: Optional[str] = None
    child_application_filing_date: Optional[date] = None
    child_patent_number: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChildContinuity":
        """Creates a `ChildContinuity` instance from a dictionary.

        Args:
            data (Dict[str, Any]): Dictionary with child continuity data.

        Returns:
            ChildContinuity: An instance of `ChildContinuity`.
        """
        c_filing_date = parse_to_date(data.get("childApplicationFilingDate"))
        return cls(
            first_inventor_to_file_indicator=data.get("firstInventorToFileIndicator"),
            child_application_status_code=data.get("childApplicationStatusCode"),
            parent_application_number_text=data.get("parentApplicationNumberText"),
            child_application_number_text=data.get("childApplicationNumberText"),
            child_application_status_description_text=data.get(
                "childApplicationStatusDescriptionText"
            ),
            child_application_filing_date=c_filing_date,
            child_patent_number=data.get("childPatentNumber"),
            claim_parentage_type_code=data.get("claimParentageTypeCode"),
            claim_parentage_type_code_description_text=data.get(
                "claimParentageTypeCodeDescriptionText"
            ),
            application_number_text=data.get("childApplicationNumberText"),
            filing_date=c_filing_date,
            status_code=data.get("childApplicationStatusCode"),
            status_description_text=data.get("childApplicationStatusDescriptionText"),
            patent_number=data.get("childPatentNumber"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the `ChildContinuity` instance to a dictionary.

        Maps attributes to specific camelCase keys expected by the API for child continuity.

        Returns:
            Dict[str, Any]: Dictionary representation.
        """
        return {
            "childApplicationStatusCode": self.child_application_status_code,
            "parentApplicationNumberText": self.parent_application_number_text,
            "childApplicationNumberText": self.child_application_number_text,
            "childApplicationStatusDescriptionText": self.child_application_status_description_text,
            "childApplicationFilingDate": serialize_date(
                self.child_application_filing_date
            ),
            "firstInventorToFileIndicator": self.first_inventor_to_file_indicator,
            "childPatentNumber": self.child_patent_number,
            "claimParentageTypeCode": self.claim_parentage_type_code,
            "claimParentageTypeCodeDescriptionText": self.claim_parentage_type_code_description_text,
        }


@dataclass(frozen=True)
class PatentTermAdjustmentHistoryData:
    """Represents a single entry in the patent term adjustment (PTA) history for an application.

    Details specific events, dates, and day quantities affecting the patent term.

    Attributes:
        event_date: Date of the PTA event.
        applicant_day_delay_quantity: Number of days of delay attributable to the applicant for this event.
        event_description_text: Textual description of the PTA event.
        event_sequence_number: Sequence number of this event in the PTA history.
        ip_office_day_delay_quantity: Number of days of delay attributable to the IP office for this event.
        originating_event_sequence_number: Sequence number of an event that originated this event.
        pta_pte_code: Code indicating if the event relates to PTA or Patent Term Extension (PTE).
    """

    event_date: Optional[date] = None
    applicant_day_delay_quantity: Optional[float] = None
    event_description_text: Optional[str] = None
    event_sequence_number: Optional[float] = None
    ip_office_day_delay_quantity: Optional[float] = None
    originating_event_sequence_number: Optional[float] = None
    pta_pte_code: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PatentTermAdjustmentHistoryData":
        """Creates a `PatentTermAdjustmentHistoryData` instance from a dictionary.

        Args:
            data (Dict[str, Any]): Dictionary with PTA history event data.

        Returns:
            PatentTermAdjustmentHistoryData: An instance of `PatentTermAdjustmentHistoryData`.
        """
        return cls(
            event_date=parse_to_date(data.get("eventDate")),
            applicant_day_delay_quantity=data.get("applicantDayDelayQuantity"),
            event_description_text=data.get("eventDescriptionText"),
            event_sequence_number=data.get("eventSequenceNumber"),
            ip_office_day_delay_quantity=data.get("ipOfficeDayDelayQuantity"),
            originating_event_sequence_number=data.get(
                "originatingEventSequenceNumber"
            ),
            pta_pte_code=data.get("ptaPTECode"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the `PatentTermAdjustmentHistoryData` instance to a dictionary.

        Omits keys with None values.

        Returns:
            Dict[str, Any]: Dictionary representation with camelCase keys.
        """
        final_dict: Dict[str, Any] = {}
        if self.event_date is not None:
            final_dict["eventDate"] = serialize_date(self.event_date)
        if self.applicant_day_delay_quantity is not None:
            final_dict["applicantDayDelayQuantity"] = self.applicant_day_delay_quantity
        if self.event_description_text is not None:
            final_dict["eventDescriptionText"] = self.event_description_text
        if self.event_sequence_number is not None:
            final_dict["eventSequenceNumber"] = self.event_sequence_number
        if self.ip_office_day_delay_quantity is not None:
            final_dict["ipOfficeDayDelayQuantity"] = self.ip_office_day_delay_quantity
        if self.originating_event_sequence_number is not None:
            final_dict["originatingEventSequenceNumber"] = (
                self.originating_event_sequence_number
            )
        if self.pta_pte_code is not None:
            final_dict["ptaPTECode"] = self.pta_pte_code
        return final_dict


@dataclass(frozen=True)
class PatentTermAdjustmentData:
    """Represents the overall patent term adjustment (PTA) data for an application.

    Includes various delay quantities (A, B, C, applicant, IP office), total adjustment,
    and a history of PTA events.

    Attributes:
        a_delay_quantity: Number of days of 'A' delay.
        adjustment_total_quantity: Total calculated PTA in days.
        applicant_day_delay_quantity: Total days of delay attributable to the applicant.
        b_delay_quantity: Number of days of 'B' delay.
        c_delay_quantity: Number of days of 'C' delay.
        filing_date: The filing date of the application.
        grant_date: The grant date of the patent.
        non_overlapping_day_quantity: Number of non-overlapping delay days.
        overlapping_day_quantity: Number of overlapping delay days.
        ip_office_day_delay_quantity: Total days of delay attributable to the IP office.
        patent_term_adjustment_history_data_bag: List of `PatentTermAdjustmentHistoryData` events.
    """

    a_delay_quantity: Optional[float] = None
    adjustment_total_quantity: Optional[float] = None
    applicant_day_delay_quantity: Optional[float] = None
    b_delay_quantity: Optional[float] = None
    c_delay_quantity: Optional[float] = None
    filing_date: Optional[date] = None
    grant_date: Optional[date] = None
    non_overlapping_day_quantity: Optional[float] = None
    overlapping_day_quantity: Optional[float] = None
    ip_office_day_delay_quantity: Optional[float] = None
    patent_term_adjustment_history_data_bag: List[PatentTermAdjustmentHistoryData] = (
        field(default_factory=list)
    )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PatentTermAdjustmentData":
        """Creates a `PatentTermAdjustmentData` instance from a dictionary.

        Args:
            data (Dict[str, Any]): Dictionary with PTA data.

        Returns:
            PatentTermAdjustmentData: An instance of `PatentTermAdjustmentData`.
        """
        history = [
            PatentTermAdjustmentHistoryData.from_dict(h)
            for h in data.get("patentTermAdjustmentHistoryDataBag", [])
            if isinstance(h, dict)
        ]
        return cls(
            a_delay_quantity=data.get("aDelayQuantity"),
            adjustment_total_quantity=data.get("adjustmentTotalQuantity"),
            applicant_day_delay_quantity=data.get("applicantDayDelayQuantity"),
            b_delay_quantity=data.get("bDelayQuantity"),
            c_delay_quantity=data.get("cDelayQuantity"),
            filing_date=parse_to_date(data.get("filingDate")),
            grant_date=parse_to_date(data.get("grantDate")),
            non_overlapping_day_quantity=data.get("nonOverlappingDayQuantity"),
            overlapping_day_quantity=data.get("overlappingDayQuantity"),
            ip_office_day_delay_quantity=data.get("ipOfficeDayDelayQuantity"),
            patent_term_adjustment_history_data_bag=history,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the `PatentTermAdjustmentData` instance to a dictionary.

        Omits keys with None values or empty lists, and converts field names to camelCase.

        Returns:
            Dict[str, Any]: Dictionary representation.
        """
        d = asdict(self)
        d["filingDate"] = serialize_date(self.filing_date)
        d["grantDate"] = serialize_date(self.grant_date)
        d["patentTermAdjustmentHistoryDataBag"] = [
            h.to_dict() for h in self.patent_term_adjustment_history_data_bag
        ]
        return {
            to_camel_case(k): v
            for k, v in d.items()
            if v is not None and (not isinstance(v, list) or v)
        }


@dataclass(frozen=True)
class EventData:
    """Represents a single event in the transaction history of a patent application.

    Attributes:
        event_code: A code identifying the type of event.
        event_description_text: A textual description of the event.
        event_date: The date the event was recorded.
    """

    event_code: Optional[str] = None
    event_description_text: Optional[str] = None
    event_date: Optional[date] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EventData":
        """Creates an `EventData` instance from a dictionary.

        Args:
            data (Dict[str, Any]): Dictionary with event data.

        Returns:
            EventData: An instance of `EventData`.
        """
        return cls(
            event_code=data.get("eventCode"),
            event_description_text=data.get("eventDescriptionText"),
            event_date=parse_to_date(data.get("eventDate")),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the `EventData` instance to a dictionary.

        Omits keys with None values and converts field names to camelCase.

        Returns:
            Dict[str, Any]: Dictionary representation.
        """
        d = asdict(self)
        d["eventDate"] = serialize_date(self.event_date)
        return {to_camel_case(k): v for k, v in d.items() if v is not None}


@dataclass(frozen=True)
class PrintedMetaData:
    """Represents metadata for a specific archive file, such as a PGPUB or Grant XML file.

    Attributes:
        zip_file_name: The name of the ZIP archive.
        product_identifier: An identifier for the data product (e.g., "APPXML", "PTGRXML").
        file_location_uri: The URI where the document file can be accessed.
        file_create_date_time: The creation timestamp of the document file (UTC).
        xml_file_name: The name of the XML file within the ZIP archive.
    """

    zip_file_name: Optional[str] = None
    product_identifier: Optional[str] = None
    file_location_uri: Optional[str] = None
    file_create_date_time: Optional[datetime] = None
    xml_file_name: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PrintedMetaData":
        """Creates a `PrintedMetaData` instance from a dictionary.

        Args:
            data (Dict[str, Any]): Dictionary with printed metadata.

        Returns:
            PrintedMetaData: An instance of `PrintedMetaData`.
        """
        return cls(
            zip_file_name=data.get("zipFileName"),
            product_identifier=data.get("productIdentifier"),
            file_location_uri=data.get("fileLocationURI"),
            file_create_date_time=parse_to_datetime_utc(data.get("fileCreateDateTime")),
            xml_file_name=data.get("xmlFileName"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the `PrintedMetaData` instance to a dictionary.

        Omits keys with None values. Serializes datetime to ISO format with 'Z'.

        Returns:
            Dict[str, Any]: Dictionary representation with camelCase keys.
        """
        final_dict: Dict[str, Any] = {}
        if self.zip_file_name is not None:
            final_dict["zipFileName"] = self.zip_file_name
        if self.product_identifier is not None:
            final_dict["productIdentifier"] = self.product_identifier
        if self.file_location_uri is not None:
            final_dict["fileLocationURI"] = self.file_location_uri
        if self.file_create_date_time is not None:
            final_dict["fileCreateDateTime"] = serialize_datetime_as_iso(
                self.file_create_date_time
            )
        if self.xml_file_name is not None:
            final_dict["xmlFileName"] = self.xml_file_name
        return final_dict


@dataclass(frozen=True)
class ApplicationMetaData:
    """Represents the comprehensive metadata associated with a patent application.

    This class holds a wide range of information including application status,
    dates (filing, grant, publication), applicant and inventor details,
    classification data, and other identifying information.

    Attributes:
        national_stage_indicator: Indicates if the application is a national stage entry.
        entity_status_data: `EntityStatus` object detailing applicant's entity status.
        publication_date_bag: List of publication dates.
        publication_sequence_number_bag: List of publication sequence numbers.
        publication_category_bag: List of publication categories.
        docket_number: Applicant's or attorney's docket number.
        first_inventor_to_file_indicator: Boolean indicating if under First-Inventor-to-File.
        first_applicant_name: Name of the first listed applicant.
        first_inventor_name: Name of the first listed inventor.
        application_confirmation_number: USPTO confirmation number for the application.
        application_status_date: Date the current application status was set.
        application_status_description_text: Textual description of the current application status.
        filing_date: Official filing date of the application.
        effective_filing_date: Effective filing date, considering priority claims.
        grant_date: Date the patent was granted, if applicable.
        group_art_unit_number: USPTO Group Art Unit number.
        application_type_code: Code for the application type.
        application_type_label_name: Label for the application type (e.g., "Utility").
        application_type_category: Category of the application type.
        invention_title: Title of the invention.
        patent_number: USPTO patent number, if granted.
        application_status_code: Numeric code for the application status.
        earliest_publication_number: Number of the earliest pre-grant publication.
        earliest_publication_date: Date of the earliest pre-grant publication.
        pct_publication_number: PCT publication number, if applicable.
        pct_publication_date: PCT publication date, if applicable.
        international_registration_publication_date: Date of international registration publication.
        international_registration_number: International registration number.
        examiner_name_text: Name of the patent examiner.
        class_field: USPC main classification. (Named `class_field` to avoid keyword clash).
        subclass: USPC subclass.
        uspc_symbol_text: Full USPC classification symbol.
        customer_number: USPTO customer number associated with the application.
        cpc_classification_bag: List of CPC classification symbols.
        applicant_bag: List of `Applicant` objects.
        inventor_bag: List of `Inventor` objects.
        raw_data: Raw JSON string of the data used to create this instance (for debugging).
    """

    national_stage_indicator: Optional[bool] = None
    entity_status_data: Optional[EntityStatus] = None
    publication_date_bag: List[date] = field(default_factory=list)
    publication_sequence_number_bag: List[str] = field(default_factory=list)
    publication_category_bag: List[str] = field(default_factory=list)
    docket_number: Optional[str] = None
    first_inventor_to_file_indicator: Optional[bool] = None
    first_applicant_name: Optional[str] = None
    first_inventor_name: Optional[str] = None
    application_confirmation_number: Optional[str] = None
    application_status_date: Optional[date] = None
    application_status_description_text: Optional[str] = None
    filing_date: Optional[date] = None
    effective_filing_date: Optional[date] = None
    grant_date: Optional[date] = None
    group_art_unit_number: Optional[str] = None
    application_type_code: Optional[str] = None
    application_type_label_name: Optional[str] = None
    application_type_category: Optional[str] = None
    invention_title: Optional[str] = None
    patent_number: Optional[str] = None
    application_status_code: Optional[int] = None
    earliest_publication_number: Optional[str] = None
    earliest_publication_date: Optional[date] = None
    pct_publication_number: Optional[str] = None
    pct_publication_date: Optional[date] = None
    international_registration_publication_date: Optional[date] = None
    international_registration_number: Optional[str] = None
    examiner_name_text: Optional[str] = None
    class_field: Optional[str] = None
    subclass: Optional[str] = None
    uspc_symbol_text: Optional[str] = None
    customer_number: Optional[int] = None
    cpc_classification_bag: List[str] = field(default_factory=list)
    applicant_bag: List[Applicant] = field(default_factory=list)
    inventor_bag: List[Inventor] = field(default_factory=list)
    raw_data: Optional[str] = field(default=None, compare=False)

    @property
    def is_aia(self) -> Optional[bool]:
        """Returns True if the application is AIA, False if pre-AIA, None if unknown."""
        return self.first_inventor_to_file_indicator

    @property
    def is_pre_aia(self) -> Optional[bool]:
        """Returns True if the application is pre-AIA, False if AIA, None if unknown."""
        if self.first_inventor_to_file_indicator is None:
            return None
        return not self.first_inventor_to_file_indicator

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ApplicationMetaData":
        """Creates an `ApplicationMetaData` instance from a dictionary.

        Args:
            data (Dict[str, Any]): Dictionary with application metadata.

        Returns:
            ApplicationMetaData: An instance of `ApplicationMetaData`.
        """
        entity = (
            EntityStatus.from_dict(data["entityStatusData"])
            if isinstance(data.get("entityStatusData"), dict)
            else None
        )
        app_bag = [
            Applicant.from_dict(a)
            for a in data.get("applicantBag", [])
            if isinstance(a, dict)
        ]
        inv_bag = [
            Inventor.from_dict(i)
            for i in data.get("inventorBag", [])
            if isinstance(i, dict)
        ]
        pub_dates_str = data.get("publicationDateBag", [])
        pub_dates = (
            [parse_to_date(d) for d in pub_dates_str if isinstance(d, str)]
            if isinstance(pub_dates_str, list)
            else []
        )
        fitf_indicator_str = data.get("firstInventorToFileIndicator")
        fitf_indicator_bool = parse_yn_to_bool(fitf_indicator_str)
        return cls(
            national_stage_indicator=data.get("nationalStageIndicator"),
            entity_status_data=entity,
            publication_date_bag=[d for d in pub_dates if d is not None],
            publication_sequence_number_bag=data.get(
                "publicationSequenceNumberBag", []
            ),
            publication_category_bag=data.get("publicationCategoryBag", []),
            docket_number=data.get("docketNumber"),
            first_inventor_to_file_indicator=fitf_indicator_bool,
            first_applicant_name=data.get("firstApplicantName"),
            first_inventor_name=data.get("firstInventorName"),
            application_confirmation_number=data.get("applicationConfirmationNumber"),
            application_status_date=parse_to_date(data.get("applicationStatusDate")),
            application_status_description_text=data.get(
                "applicationStatusDescriptionText"
            ),
            filing_date=parse_to_date(data.get("filingDate")),
            effective_filing_date=parse_to_date(data.get("effectiveFilingDate")),
            grant_date=parse_to_date(data.get("grantDate")),
            group_art_unit_number=data.get("groupArtUnitNumber"),
            application_type_code=data.get("applicationTypeCode"),
            application_type_label_name=data.get("applicationTypeLabelName"),
            application_type_category=data.get("applicationTypeCategory"),
            invention_title=data.get("inventionTitle"),
            patent_number=data.get("patentNumber"),
            application_status_code=data.get("applicationStatusCode"),
            earliest_publication_number=data.get("earliestPublicationNumber"),
            earliest_publication_date=parse_to_date(
                data.get("earliestPublicationDate")
            ),
            pct_publication_number=data.get("pctPublicationNumber"),
            pct_publication_date=parse_to_date(data.get("pctPublicationDate")),
            international_registration_publication_date=parse_to_date(
                data.get("internationalRegistrationPublicationDate")
            ),
            international_registration_number=data.get(
                "internationalRegistrationNumber"
            ),
            examiner_name_text=data.get("examinerNameText"),
            class_field=data.get("class"),
            subclass=data.get("subclass"),
            uspc_symbol_text=data.get("uspcSymbolText"),
            customer_number=data.get("customerNumber"),
            cpc_classification_bag=data.get("cpcClassificationBag", []),
            applicant_bag=app_bag,
            inventor_bag=inv_bag,
            raw_data=json.dumps(data),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the `ApplicationMetaData` instance to a dictionary.

        Serializes attributes to camelCase keys suitable for API interaction or storage.
        Omits keys with None values or empty lists. Handles date and boolean serialization.

        Returns:
            Dict[str, Any]: Dictionary representation of the application metadata.
        """
        d = asdict(self)
        d.pop("raw_data", None)
        d.pop("is_aia", None)
        d.pop("is_pre_aia", None)
        date_fields = [
            "application_status_date",
            "filing_date",
            "effective_filing_date",
            "grant_date",
            "earliest_publication_date",
            "pct_publication_date",
            "international_registration_publication_date",
        ]
        for field_name in date_fields:
            camel_key = to_camel_case(field_name)
            d[camel_key] = serialize_date(getattr(self, field_name, None))
            if field_name != camel_key:
                d.pop(field_name, None)
        d["publicationDateBag"] = [
            serialize_date(dt) for dt in self.publication_date_bag if dt
        ]
        if (
            "publication_date_bag" in d
            and "publication_date_bag" != "publicationDateBag"
        ):
            d.pop("publication_date_bag")
        d["firstInventorToFileIndicator"] = serialize_bool_to_yn(
            self.first_inventor_to_file_indicator
        )
        if (
            "first_inventor_to_file_indicator" in d
            and "first_inventor_to_file_indicator" != "firstInventorToFileIndicator"
        ):
            d.pop("first_inventor_to_file_indicator")
        if self.entity_status_data:
            d["entityStatusData"] = self.entity_status_data.to_dict()
        else:
            d.pop("entityStatusData", None)
            d.pop("entity_status_data", None)
        d["applicantBag"] = [a.to_dict() for a in self.applicant_bag]
        if "applicant_bag" in d and "applicant_bag" != "applicantBag":
            d.pop("applicant_bag")
        d["inventorBag"] = [i.to_dict() for i in self.inventor_bag]
        if "inventor_bag" in d and "inventor_bag" != "inventorBag":
            d.pop("inventor_bag")
        if "class_field" in d:
            d["class"] = d.pop("class_field")
        if "class" in d and d["class"] is None:
            d.pop("class", None)
        final_data = {}
        for key_snake, v_obj in d.items():
            k_camel = to_camel_case(snake_str=key_snake)
            if key_snake in [
                "firstInventorToFileIndicator",
                "publicationDateBag",
                "entityStatusData",
                "applicantBag",
                "inventorBag",
            ] or any(to_camel_case(df) == key_snake for df in date_fields):
                k_camel = key_snake
            if v_obj is not None:
                if isinstance(v_obj, list) and not v_obj:
                    continue
                final_data[k_camel] = v_obj
        return final_data


@dataclass(frozen=True)
class PatentFileWrapper:
    """Represents the complete file wrapper for a single patent application.

    This is a top-level object containing all data sections related to an application,
    such as metadata, addresses, assignments, attorney information, continuity data,
    PTA data, transaction events, and associated document metadata.

    Attributes:
        application_number_text: The primary application number.
        application_meta_data: Comprehensive `ApplicationMetaData`.
        correspondence_address_bag: List of `Address` objects for correspondence.
        assignment_bag: List of `Assignment` records.
        record_attorney: Information about the `RecordAttorney`.
        foreign_priority_bag: List of `ForeignPriority` claims.
        parent_continuity_bag: List of `ParentContinuity` records.
        child_continuity_bag: List of `ChildContinuity` records.
        patent_term_adjustment_data: `PatentTermAdjustmentData` details.
        event_data_bag: List of `EventData` (transaction history).
        pgpub_document_meta_data: `PrintedMetaData` for Pre-Grant Publication.
        grant_document_meta_data: `PrintedMetaData` for the granted patent.
        last_ingestion_date_time: Timestamp of when this data was last ingested by the API (UTC).
    """

    application_number_text: Optional[str] = None
    application_meta_data: Optional[ApplicationMetaData] = None
    correspondence_address_bag: List[Address] = field(default_factory=list)
    assignment_bag: List[Assignment] = field(default_factory=list)
    record_attorney: Optional[RecordAttorney] = None
    foreign_priority_bag: List[ForeignPriority] = field(default_factory=list)
    parent_continuity_bag: List[ParentContinuity] = field(default_factory=list)
    child_continuity_bag: List[ChildContinuity] = field(default_factory=list)
    patent_term_adjustment_data: Optional[PatentTermAdjustmentData] = None
    event_data_bag: List[EventData] = field(default_factory=list)
    pgpub_document_meta_data: Optional[PrintedMetaData] = None
    grant_document_meta_data: Optional[PrintedMetaData] = None
    last_ingestion_date_time: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PatentFileWrapper":
        """Creates a `PatentFileWrapper` instance from a dictionary.

        Args:
            data (Dict[str, Any]): Dictionary with patent file wrapper data.

        Returns:
            PatentFileWrapper: An instance of `PatentFileWrapper`.
        """
        amd_json = data.get("applicationMetaData")
        amd = (
            ApplicationMetaData.from_dict(amd_json)
            if isinstance(amd_json, dict)
            else None
        )
        corr_addrs = [
            Address.from_dict(a)
            for a in data.get("correspondenceAddressBag", [])
            if isinstance(a, dict)
        ]
        assigns = [
            Assignment.from_dict(a)
            for a in data.get("assignmentBag", [])
            if isinstance(a, dict)
        ]
        rec_att_json = data.get("recordAttorney")
        rec_att = (
            RecordAttorney.from_dict(rec_att_json)
            if isinstance(rec_att_json, dict)
            else None
        )
        f_pris = [
            ForeignPriority.from_dict(fp)
            for fp in data.get("foreignPriorityBag", [])
            if isinstance(fp, dict)
        ]
        p_conts = [
            ParentContinuity.from_dict(pc)
            for pc in data.get("parentContinuityBag", [])
            if isinstance(pc, dict)
        ]
        c_conts = [
            ChildContinuity.from_dict(cc)
            for cc in data.get("childContinuityBag", [])
            if isinstance(cc, dict)
        ]
        pta_json = data.get("patentTermAdjustmentData")
        pta = (
            PatentTermAdjustmentData.from_dict(pta_json)
            if isinstance(pta_json, dict)
            else None
        )
        evts = [
            EventData.from_dict(e)
            for e in data.get("eventDataBag", [])
            if isinstance(e, dict)
        ]
        pgpub_json = data.get("pgpubDocumentMetaData")
        pgpub = (
            PrintedMetaData.from_dict(pgpub_json)
            if isinstance(pgpub_json, dict)
            else None
        )
        grant_json = data.get("grantDocumentMetaData")
        grant = (
            PrintedMetaData.from_dict(grant_json)
            if isinstance(grant_json, dict)
            else None
        )
        return cls(
            application_number_text=data.get("applicationNumberText"),
            application_meta_data=amd,
            correspondence_address_bag=corr_addrs,
            assignment_bag=assigns,
            record_attorney=rec_att,
            foreign_priority_bag=f_pris,
            parent_continuity_bag=p_conts,
            child_continuity_bag=c_conts,
            patent_term_adjustment_data=pta,
            event_data_bag=evts,
            pgpub_document_meta_data=pgpub,
            grant_document_meta_data=grant,
            last_ingestion_date_time=parse_to_datetime_utc(
                data.get("lastIngestionDateTime")
            ),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the `PatentFileWrapper` instance to a dictionary.

        Omits keys with None values or empty lists. Serializes nested objects.

        Returns:
            Dict[str, Any]: Dictionary representation.
        """
        _dict = {
            "applicationNumberText": self.application_number_text,
            "applicationMetaData": (
                self.application_meta_data.to_dict()
                if self.application_meta_data
                else None
            ),
            "correspondenceAddressBag": [
                a.to_dict() for a in self.correspondence_address_bag
            ],
            "assignmentBag": [a.to_dict() for a in self.assignment_bag],
            "recordAttorney": (
                self.record_attorney.to_dict() if self.record_attorney else None
            ),
            "foreignPriorityBag": [fp.to_dict() for fp in self.foreign_priority_bag],
            "parentContinuityBag": [pc.to_dict() for pc in self.parent_continuity_bag],
            "childContinuityBag": [cc.to_dict() for cc in self.child_continuity_bag],
            "patentTermAdjustmentData": (
                self.patent_term_adjustment_data.to_dict()
                if self.patent_term_adjustment_data
                else None
            ),
            "eventDataBag": [e.to_dict() for e in self.event_data_bag],
            "pgpubDocumentMetaData": (
                self.pgpub_document_meta_data.to_dict()
                if self.pgpub_document_meta_data
                else None
            ),
            "grantDocumentMetaData": (
                self.grant_document_meta_data.to_dict()
                if self.grant_document_meta_data
                else None
            ),
            "lastIngestionDateTime": serialize_datetime_as_iso(
                self.last_ingestion_date_time
            ),
        }
        return {
            k: v
            for k, v in _dict.items()
            if v is not None and (not isinstance(v, list) or v)
        }


@dataclass(frozen=True)
class PatentDataResponse:
    """Represents the overall response from a patent data API request.

    It typically includes a count of the results and a list of PatentFileWrapper objects,
    each containing detailed data for a patent application.

    Attributes:
        count: The total number of patent applications found matching the query.
        patent_file_wrapper_data_bag: A list of `PatentFileWrapper` objects.
    """

    count: int
    patent_file_wrapper_data_bag: List[PatentFileWrapper] = field(default_factory=list)
    # TODO: raw as response in json

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PatentDataResponse":
        """Creates a `PatentDataResponse` instance from a dictionary.

        Args:
            data (Dict[str, Any]): Dictionary with API response data.

        Returns:
            PatentDataResponse: An instance of `PatentDataResponse`.
        """
        wrappers = [
            PatentFileWrapper.from_dict(w)
            for w in data.get("patentFileWrapperDataBag", [])
            if isinstance(w, dict)
        ]
        return cls(count=data.get("count", 0), patent_file_wrapper_data_bag=wrappers)

    def to_dict(self) -> Dict[str, Any]:
        """Converts the `PatentDataResponse` instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation.
        """
        return {
            "count": self.count,
            "patentFileWrapperDataBag": [
                w.to_dict() for w in self.patent_file_wrapper_data_bag
            ],
        }

    def to_csv(self) -> str:
        """Converts the patent data in this response to a CSV formatted string.

        The CSV will contain key metadata fields for each application,
        such as invention title, application number, filing date, status, etc.

        Returns:
            str: A string containing the data in CSV format.
        """
        headers = [
            "inventionTitle",
            "applicationNumberText",
            "filingDate",
            "applicationTypeLabelName",
            "publicationCategoryBag",
            "applicationStatusDescriptionText",
            "applicationStatusDate",
            "firstInventorName",
        ]

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(headers)

        if not self.patent_file_wrapper_data_bag:
            return output.getvalue()

        for wrapper in self.patent_file_wrapper_data_bag:
            if not wrapper.application_meta_data:
                continue

            meta = wrapper.application_meta_data

            pub_category_str = (
                "|".join(meta.publication_category_bag)
                if meta.publication_category_bag
                else ""
            )

            row_data = [
                meta.invention_title or "",
                wrapper.application_number_text or "",
                serialize_date(meta.filing_date) or "",
                meta.application_type_label_name or "",
                pub_category_str,
                meta.application_status_description_text or "",
                serialize_date(meta.application_status_date) or "",
                meta.first_inventor_name or "",
            ]
            writer.writerow(row_data)

        return output.getvalue()


@dataclass(frozen=True)
class StatusCode:
    """Represents a USPTO application status code and its textual description.

    Attributes:
        code: The numeric status code.
        description: The textual description of the status code.
    """

    code: Optional[int] = None
    description: Optional[str] = None

    def __str__(self) -> str:
        """Returns a user-friendly string representation of the status code."""
        return f"{self.code}: {self.description}"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StatusCode":
        """Creates a `StatusCode` instance from a dictionary.

        Handles two possible key sets from the API for status information.

        Args:
            data (Dict[str, Any]): Dictionary with status code data.

        Returns:
            StatusCode: An instance of `StatusCode`.
        """
        if "code" in data:
            return cls(
                code=data.get("code"),
                description=data.get("description"),
            )
        else:
            return cls(
                code=data.get("applicationStatusCode"),
                description=data.get("applicationStatusDescriptionText"),
            )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the `StatusCode` instance to a dictionary.

        Uses keys "applicationStatusCode" and "applicationStatusDescriptionText"
        for consistency with some API response parts.

        Returns:
            Dict[str, Any]: Dictionary representation.
        """
        return {
            "applicationStatusCode": self.code,
            "applicationStatusDescriptionText": self.description,
        }


class StatusCodeCollection:
    """A collection of StatusCode objects.

    Provides iterable access and helper methods to find or filter status codes.
    This class is immutable by convention after initialization.

    Attributes:
        status_codes (tuple[StatusCode, ...]): An immutable tuple of `StatusCode` objects.
    """

    def __init__(self, status_codes: List[StatusCode]):
        """Initializes the StatusCodeCollection with a list of status codes.

        Args:
            status_codes (List[StatusCode]): A list of `StatusCode` instances.
        """
        self._status_codes: tuple[StatusCode, ...] = tuple(status_codes)

    def __iter__(self) -> Iterator[StatusCode]:
        return iter(self._status_codes)

    def __len__(self) -> int:
        return len(self._status_codes)

    def __getitem__(self, index: int) -> StatusCode:
        return self._status_codes[index]

    def __str__(self) -> str:
        return f"StatusCodeCollection with {len(self)} status codes."

    def __repr__(self) -> str:
        if not self._status_codes:
            return "StatusCodeCollection(empty)"

        if len(self._status_codes) <= 3:
            codes = ", ".join(str(s.code) for s in self._status_codes)
            return f"StatusCodeCollection({len(self)} status codes: {codes})"
        else:
            first_codes = ", ".join(str(s.code) for s in self._status_codes[:3])
            return f"StatusCodeCollection({len(self)} status codes: {first_codes}, ...)"

    def find_by_code(self, code_to_find: int) -> Optional[StatusCode]:
        """Finds a status code by its numeric code.

        Args:
            code_to_find (int): The numeric status code to search for.

        Returns:
            Optional[StatusCode]: The `StatusCode` object if found, otherwise None.
        """
        for status in self._status_codes:
            if status.code == code_to_find:
                return status
        return None

    def search_by_description(self, text: str) -> "StatusCodeCollection":
        """Searches for status codes by a case-insensitive text match in their description.

        Args:
            text (str): The text to search for within status code descriptions.

        Returns:
            StatusCodeCollection: A new collection containing matching status codes.
        """
        matching = [
            s
            for s in self._status_codes
            if s.description and text.lower() in s.description.lower()
        ]
        return StatusCodeCollection(status_codes=matching)

    def to_dict(self) -> List[Dict[str, Any]]:
        """Converts the collection of status codes to a list of dictionaries.

        Returns:
            List[Dict[str, Any]]: A list where each item is the dictionary
                representation of a `StatusCode`.
        """
        return [sc.to_dict() for sc in self._status_codes]


@dataclass(frozen=True)
class StatusCodeSearchResponse:
    """Represents the response from a search query for patent application status codes.

    Attributes:
        count: The total number of status codes found matching the query.
        status_code_bag: A `StatusCodeCollection` of the `StatusCode` objects returned.
        request_identifier: An identifier for the API request, if provided.
    """

    count: int
    status_code_bag: StatusCodeCollection
    request_identifier: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StatusCodeSearchResponse":
        """Creates a `StatusCodeSearchResponse` instance from a dictionary.

        Args:
            data (Dict[str, Any]): Dictionary with API response data for status codes.

        Returns:
            StatusCodeSearchResponse: An instance of `StatusCodeSearchResponse`.
        """
        codes_json = data.get("statusCodeBag", [])
        parsed_codes = (
            [StatusCode.from_dict(cd) for cd in codes_json if isinstance(cd, dict)]
            if isinstance(codes_json, list)
            else []
        )
        collection = StatusCodeCollection(parsed_codes)
        return cls(
            count=data.get("count", 0),
            status_code_bag=collection,
            request_identifier=data.get("requestIdentifier"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the `StatusCodeSearchResponse` instance to a dictionary.

        Omits keys with None values or empty lists.

        Returns:
            Dict[str, Any]: Dictionary representation.
        """
        _dict = {
            "count": self.count,
            "statusCodeBag": self.status_code_bag.to_dict(),
            "requestIdentifier": self.request_identifier,
        }
        return {
            k: v
            for k, v in _dict.items()
            if v is not None and (not isinstance(v, list) or v)
        }


@dataclass(frozen=True)
class ApplicationContinuityData:
    """Holds parent and child continuity application data for a specific patent application.

    This class consolidates lists of ParentContinuity and ChildContinuity objects,
    representing the lineage of an application.

    Attributes:
        parent_continuity_bag: List of `ParentContinuity` objects.
        child_continuity_bag: List of `ChildContinuity` objects.
    """

    parent_continuity_bag: List[ParentContinuity] = field(default_factory=list)
    child_continuity_bag: List[ChildContinuity] = field(default_factory=list)

    @classmethod
    def from_wrapper(cls, wrapper: PatentFileWrapper) -> "ApplicationContinuityData":
        """Creates an `ApplicationContinuityData` instance from a `PatentFileWrapper`.

        Extracts parent and child continuity bags from the wrapper.

        Args:
            wrapper (PatentFileWrapper): The patent file wrapper containing continuity data.

        Returns:
            ApplicationContinuityData: An instance of `ApplicationContinuityData`.
        """
        return cls(
            parent_continuity_bag=wrapper.parent_continuity_bag,
            child_continuity_bag=wrapper.child_continuity_bag,
        )

    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """Converts the `ApplicationContinuityData` instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation with "parentContinuityBag"
                and "childContinuityBag" keys.
        """
        return {
            "parentContinuityBag": [pc.to_dict() for pc in self.parent_continuity_bag],
            "childContinuityBag": [cc.to_dict() for cc in self.child_continuity_bag],
        }


@dataclass(frozen=True)
class PrintedPublication:
    """Holds metadata for associated documents like Pre-Grant Publications (PGPUB)
    and Grant documents for a specific patent application.

    Attributes:
        pgpub_document_meta_data: `PrintedMetaData` for the Pre-Grant Publication, if any.
        grant_document_meta_data: `PrintedMetaData` for the Grant document, if any.
    """

    pgpub_document_meta_data: Optional[PrintedMetaData] = None
    grant_document_meta_data: Optional[PrintedMetaData] = None

    @classmethod
    def from_wrapper(cls, wrapper: PatentFileWrapper) -> "PrintedPublication":
        """Creates a `PrintedPublication` instance from a `PatentFileWrapper`.

        Extracts PGPUB and Grant document metadata from the wrapper.

        Args:
            wrapper (PatentFileWrapper): The patent file wrapper.

        Returns:
            PrintedPublication: An instance of `PrintedPublication`.
        """
        return cls(
            pgpub_document_meta_data=wrapper.pgpub_document_meta_data,
            grant_document_meta_data=wrapper.grant_document_meta_data,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the `PrintedPublication` instance to a dictionary.

        Omits keys if their corresponding metadata is None.

        Returns:
            Dict[str, Any]: Dictionary representation.
        """
        return {
            "pgpubDocumentMetaData": (
                self.pgpub_document_meta_data.to_dict()
                if self.pgpub_document_meta_data
                else None
            ),
            "grantDocumentMetaData": (
                self.grant_document_meta_data.to_dict()
                if self.grant_document_meta_data
                else None
            ),
        }
