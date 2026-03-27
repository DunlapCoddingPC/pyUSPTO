"""models.enriched_citations - Data models for USPTO Enriched Citations API.

This module provides data models for representing responses from the USPTO
Enriched Cited Reference Metadata API (v3). These models cover enriched citation
records extracted from patent office actions using AI/NLP algorithms.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from pyUSPTO.models.utils import (
    parse_to_datetime_utc,
    serialize_datetime_as_naive,
)


# --- Enums for Categorical Data ---
class CitationCategoryCode(Enum):
    """Citation category codes indicating the relevance of cited documents.

    These are standard patent citation categories used in search reports:
        X - Particularly relevant if taken alone
        Y - Particularly relevant if combined with another document
        A - Technological background
        E - Earlier patent document published on or after the filing date
        L - Document cited for other reasons
        O - Non-written disclosure
        T - Theory or principle underlying the invention
        P - Intermediate document
        & - Member of the same patent family
        D - Document cited in the application
    """

    X = "X"
    Y = "Y"
    A = "A"
    E = "E"
    L = "L"
    O = "O"  # noqa: E741
    T = "T"
    P = "P"
    AMPERSAND = "&"
    D = "D"

    @classmethod
    def _missing_(cls, value: Any) -> "CitationCategoryCode":
        """Handle case-insensitive lookup and ampersand alias."""
        if isinstance(value, str):
            val_upper = value.upper()
            for member in cls:
                if member.value.upper() == val_upper:
                    return member
        raise ValueError(f"{value!r} is not a valid {cls.__name__}")


# --- Data Models ---
@dataclass(frozen=True)
class EnrichedCitation:
    """Represent a single enriched citation record from an office action.

    Attributes:
        id: Unique identifier for this citation record.
        patent_application_number: The application number (series code + serial number).
        cited_document_identifier: Identification of the cited patent document.
        publication_number: Publication number of the cited document.
        kind_code: Kind code of the cited document (e.g., "A1", "B2").
        country_code: Country code of the cited document.
        inventor_name_text: Inventor or owner name from the cited document.
        office_action_date: The date the office action was recorded.
        office_action_category: Category of the office action (e.g., "CTNF", "CTFR").
        citation_category_code: Relevance category code (X, Y, A, E, L, O, T, P, &, D).
        related_claim_number_text: Comma-separated claim numbers related to this citation.
        examiner_cited_reference_indicator: Whether the reference was cited by the examiner (Form PTO-892).
        applicant_cited_examiner_reference_indicator: Whether the citation was from Form PTO-1449.
        npl_indicator: Whether this is a non-patent literature citation.
        work_group_number: The work group number.
        group_art_unit_number: Four-digit art unit code for examiner assignment.
        tech_center: Technology center code (first two digits of art unit).
        quality_summary_text: Quality summary of the review status.
        passage_location_text: Pipe-delimited passage locations related to the citation.
        obsolete_document_identifier: Legacy document identifier from the IFW repository.
        create_user_identifier: Job identifier that created this record.
        create_date_time: Date and time the record was inserted in the database.
    """

    id: str = ""
    patent_application_number: str | None = None
    cited_document_identifier: str | None = None
    publication_number: str | None = None
    kind_code: str | None = None
    country_code: str | None = None
    inventor_name_text: str | None = None
    office_action_date: datetime | None = None
    office_action_category: str | None = None
    citation_category_code: str | None = None
    related_claim_number_text: str | None = None
    examiner_cited_reference_indicator: bool | None = None
    applicant_cited_examiner_reference_indicator: bool | None = None
    npl_indicator: bool | None = None
    work_group_number: str | None = None
    group_art_unit_number: str | None = None
    tech_center: str | None = None
    quality_summary_text: str | None = None
    passage_location_text: list[str] = field(default_factory=list)
    obsolete_document_identifier: str | None = None
    create_user_identifier: str | None = None
    create_date_time: datetime | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EnrichedCitation":
        """Create an EnrichedCitation instance from a dictionary.

        Args:
            data: Dictionary containing enriched citation data from API response.

        Returns:
            EnrichedCitation: An instance of EnrichedCitation.
        """
        # Defensive handling for passage_location_text
        passage_location = data.get("passageLocationText", [])
        if not isinstance(passage_location, list):
            passage_location = []

        return cls(
            id=data.get("id", ""),
            patent_application_number=data.get("patentApplicationNumber"),
            cited_document_identifier=data.get("citedDocumentIdentifier"),
            publication_number=data.get("publicationNumber"),
            kind_code=data.get("kindCode"),
            country_code=data.get("countryCode"),
            inventor_name_text=data.get("inventorNameText"),
            office_action_date=parse_to_datetime_utc(data.get("officeActionDate")),
            office_action_category=data.get("officeActionCategory"),
            citation_category_code=data.get("citationCategoryCode"),
            related_claim_number_text=data.get("relatedClaimNumberText"),
            examiner_cited_reference_indicator=data.get(
                "examinerCitedReferenceIndicator"
            ),
            applicant_cited_examiner_reference_indicator=data.get(
                "applicantCitedExaminerReferenceIndicator"
            ),
            npl_indicator=data.get("nplIndicator"),
            work_group_number=data.get("workGroupNumber"),
            group_art_unit_number=data.get("groupArtUnitNumber"),
            tech_center=data.get("techCenter"),
            quality_summary_text=data.get("qualitySummaryText"),
            passage_location_text=passage_location,
            obsolete_document_identifier=data.get("obsoleteDocumentIdentifier"),
            create_user_identifier=data.get("createUserIdentifier"),
            create_date_time=parse_to_datetime_utc(data.get("createDateTime")),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the EnrichedCitation instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation with camelCase keys.
        """
        d = {
            "id": self.id,
            "patentApplicationNumber": self.patent_application_number,
            "citedDocumentIdentifier": self.cited_document_identifier,
            "publicationNumber": self.publication_number,
            "kindCode": self.kind_code,
            "countryCode": self.country_code,
            "inventorNameText": self.inventor_name_text,
            "officeActionDate": (
                serialize_datetime_as_naive(self.office_action_date)
                if self.office_action_date
                else None
            ),
            "officeActionCategory": self.office_action_category,
            "citationCategoryCode": self.citation_category_code,
            "relatedClaimNumberText": self.related_claim_number_text,
            "examinerCitedReferenceIndicator": self.examiner_cited_reference_indicator,
            "applicantCitedExaminerReferenceIndicator": self.applicant_cited_examiner_reference_indicator,
            "nplIndicator": self.npl_indicator,
            "workGroupNumber": self.work_group_number,
            "groupArtUnitNumber": self.group_art_unit_number,
            "techCenter": self.tech_center,
            "qualitySummaryText": self.quality_summary_text,
            "passageLocationText": self.passage_location_text,
            "obsoleteDocumentIdentifier": self.obsolete_document_identifier,
            "createUserIdentifier": self.create_user_identifier,
            "createDateTime": (
                serialize_datetime_as_naive(self.create_date_time)
                if self.create_date_time
                else None
            ),
        }
        return {
            k: v
            for k, v in d.items()
            if v is not None and (not isinstance(v, list) or v)
        }


@dataclass(frozen=True)
class EnrichedCitationResponse:
    """Response from the Enriched Citations API search endpoint.

    The API returns a Solr-style response with `start`, `numFound`, and `docs`.
    The outer envelope key is `"response"`.

    Attributes:
        num_found: Total number of matching records.
        start: The start index of the first result in this page.
        docs: List of enriched citation records in this page.
        raw_data: Optional raw JSON data from the API response (for debugging).
    """

    num_found: int = 0
    start: int = 0
    docs: list[EnrichedCitation] = field(default_factory=list)
    raw_data: str | None = field(default=None, compare=False, repr=False)

    @property
    def count(self) -> int:
        """Return total result count for pagination compatibility."""
        return self.num_found

    @classmethod
    def from_dict(
        cls, data: dict[str, Any], include_raw_data: bool = False
    ) -> "EnrichedCitationResponse":
        """Create an EnrichedCitationResponse instance from a dictionary.

        Handles both the raw API envelope (``{"response": {...}}``) and
        a pre-unwrapped dictionary.

        Args:
            data: Dictionary containing API response data.
            include_raw_data: If True, store the raw JSON for debugging.

        Returns:
            EnrichedCitationResponse: An instance of EnrichedCitationResponse.
        """
        # Unwrap the outer "response" envelope if present
        inner = data.get("response", data)

        # Parse citation docs
        docs_data = inner.get("docs", [])
        docs = (
            [
                EnrichedCitation.from_dict(doc)
                for doc in docs_data
                if isinstance(doc, dict)
            ]
            if isinstance(docs_data, list)
            else []
        )

        return cls(
            num_found=inner.get("numFound", 0),
            start=inner.get("start", 0),
            docs=docs,
            raw_data=json.dumps(data) if include_raw_data else None,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the EnrichedCitationResponse instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation with camelCase keys,
                wrapped in the ``"response"`` envelope matching the API format.
        """
        return {
            "response": {
                "numFound": self.num_found,
                "start": self.start,
                "docs": [doc.to_dict() for doc in self.docs],
            }
        }


@dataclass(frozen=True)
class EnrichedCitationFieldsResponse:
    """Response from the Enriched Citations API fields endpoint.

    Contains metadata about the API including available field names
    and the last data update timestamp.

    Attributes:
        api_key: The dataset key (e.g., "enriched_cited_reference_metadata").
        api_version_number: API version (e.g., "v3").
        api_url: The URL of this fields endpoint.
        api_documentation_url: URL to the Swagger documentation.
        api_status: Publication status (e.g., "PUBLISHED").
        field_count: Number of available fields.
        fields: List of available field names.
        last_data_updated_date: Timestamp of the last data update (non-standard format).
    """

    api_key: str | None = None
    api_version_number: str | None = None
    api_url: str | None = None
    api_documentation_url: str | None = None
    api_status: str | None = None
    field_count: int = 0
    fields: list[str] = field(default_factory=list)
    last_data_updated_date: str | None = None

    @classmethod
    def from_dict(
        cls, data: dict[str, Any], include_raw_data: bool = False
    ) -> "EnrichedCitationFieldsResponse":
        """Create an EnrichedCitationFieldsResponse instance from a dictionary.

        Args:
            data: Dictionary containing API response data.
            include_raw_data: Unused. Present for FromDictProtocol conformance.

        Returns:
            EnrichedCitationFieldsResponse: An instance of EnrichedCitationFieldsResponse.
        """
        fields_data = data.get("fields", [])
        if not isinstance(fields_data, list):
            fields_data = []

        return cls(
            api_key=data.get("apiKey"),
            api_version_number=data.get("apiVersionNumber"),
            api_url=data.get("apiUrl"),
            api_documentation_url=data.get("apiDocumentationUrl"),
            api_status=data.get("apiStatus"),
            field_count=data.get("fieldCount", 0),
            fields=fields_data,
            last_data_updated_date=data.get("lastDataUpdatedDate"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the EnrichedCitationFieldsResponse instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation with camelCase keys.
        """
        d = {
            "apiKey": self.api_key,
            "apiVersionNumber": self.api_version_number,
            "apiUrl": self.api_url,
            "apiDocumentationUrl": self.api_documentation_url,
            "apiStatus": self.api_status,
            "fieldCount": self.field_count,
            "fields": self.fields,
            "lastDataUpdatedDate": self.last_data_updated_date,
        }
        return {
            k: v
            for k, v in d.items()
            if v is not None and (not isinstance(v, list) or v)
        }
