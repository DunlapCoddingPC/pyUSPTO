"""models.oa_citations - Data models for USPTO Office Action Citations API.

This module provides data models for representing responses from the USPTO
Office Action Citations API (v2). These models cover citation data from
Office Actions mailed from October 1, 2017 to 30 days prior to the current
date, derived from Form PTO-892, Form PTO-1449, and Office Action text.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from pyUSPTO.models.utils import parse_to_datetime_utc, serialize_datetime_as_naive


@dataclass(frozen=True)
class OACitationRecord:
    """A single citation record from the OA Citations API.

    Attributes:
        id: Unique record identifier (hex hash).
        patent_application_number: Patent application number.
        action_type_category: Type of action (e.g., ``"rejected"``).
        legal_section_code: Legal section code (e.g., ``"101"``, ``"103"``).
        reference_identifier: Free-text citation reference string.
        parsed_reference_identifier: Extracted publication number from the reference.
        group_art_unit_number: Group art unit number.
        work_group: Work group code.
        tech_center: Technology center code.
        paragraph_number: Paragraph number within the Office Action.
        applicant_cited_examiner_reference_indicator: Whether the applicant cited
            this as an examiner reference.
        examiner_cited_reference_indicator: Whether the examiner cited this reference.
        office_action_citation_reference_indicator: Whether this is an Office Action
            citation reference.
        create_user_identifier: User who created the record (e.g., ``"ETL_SYS"``).
        create_date_time: Timestamp when this record was created.
        obsolete_document_identifier: Legacy IFW document identifier.
    """

    id: str = ""
    patent_application_number: str = ""
    action_type_category: str = ""
    legal_section_code: str = ""
    reference_identifier: str = ""
    parsed_reference_identifier: str = ""
    group_art_unit_number: str = ""
    work_group: str = ""
    tech_center: str = ""
    paragraph_number: str = ""
    applicant_cited_examiner_reference_indicator: bool | None = None
    examiner_cited_reference_indicator: bool | None = None
    office_action_citation_reference_indicator: bool | None = None
    create_user_identifier: str = ""
    create_date_time: datetime | None = None
    obsolete_document_identifier: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OACitationRecord":
        """Create an OACitationRecord from a dictionary.

        Args:
            data: Dictionary containing citation record data from API response.

        Returns:
            OACitationRecord: An instance of OACitationRecord.
        """
        return cls(
            id=data.get("id", ""),
            patent_application_number=data.get("patentApplicationNumber", ""),
            action_type_category=data.get("actionTypeCategory", ""),
            legal_section_code=data.get("legalSectionCode", ""),
            reference_identifier=data.get("referenceIdentifier", ""),
            parsed_reference_identifier=data.get("parsedReferenceIdentifier", ""),
            group_art_unit_number=data.get("groupArtUnitNumber", ""),
            work_group=data.get("workGroup", ""),
            tech_center=data.get("techCenter", ""),
            paragraph_number=data.get("paragraphNumber", ""),
            applicant_cited_examiner_reference_indicator=data.get(
                "applicantCitedExaminerReferenceIndicator"
            ),
            examiner_cited_reference_indicator=data.get(
                "examinerCitedReferenceIndicator"
            ),
            office_action_citation_reference_indicator=data.get(
                "officeActionCitationReferenceIndicator"
            ),
            create_user_identifier=data.get("createUserIdentifier", ""),
            create_date_time=parse_to_datetime_utc(data.get("createDateTime")),
            obsolete_document_identifier=data.get("obsoleteDocumentIdentifier", ""),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the OACitationRecord instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary with camelCase keys matching the API format.
                None values are omitted.
        """
        d: dict[str, Any] = {
            "id": self.id,
            "patentApplicationNumber": self.patent_application_number,
            "actionTypeCategory": self.action_type_category,
            "legalSectionCode": self.legal_section_code,
            "referenceIdentifier": self.reference_identifier,
            "parsedReferenceIdentifier": self.parsed_reference_identifier,
            "groupArtUnitNumber": self.group_art_unit_number,
            "workGroup": self.work_group,
            "techCenter": self.tech_center,
            "paragraphNumber": self.paragraph_number,
            "applicantCitedExaminerReferenceIndicator": self.applicant_cited_examiner_reference_indicator,
            "examinerCitedReferenceIndicator": self.examiner_cited_reference_indicator,
            "officeActionCitationReferenceIndicator": self.office_action_citation_reference_indicator,
            "createUserIdentifier": self.create_user_identifier,
            "createDateTime": (
                serialize_datetime_as_naive(self.create_date_time)
                if self.create_date_time
                else None
            ),
            "obsoleteDocumentIdentifier": self.obsolete_document_identifier,
        }
        return {k: v for k, v in d.items() if v is not None}


@dataclass(frozen=True)
class OACitationsResponse:
    """Response from the OA Citations API search endpoint.

    The API returns a Solr-style response with ``start``, ``numFound``, and ``docs``.
    The outer envelope key is ``"response"``.

    Attributes:
        num_found: Total number of matching records.
        start: The start index of the first result in this page.
        docs: List of citation records in this page.
        raw_data: Optional raw JSON data from the API response (for debugging).
    """

    num_found: int = 0
    start: int = 0
    docs: list[OACitationRecord] = field(default_factory=list)
    raw_data: str | None = field(default=None, compare=False, repr=False)

    @property
    def count(self) -> int:
        """Return total result count for pagination compatibility."""
        return self.num_found

    @classmethod
    def from_dict(
        cls, data: dict[str, Any], include_raw_data: bool = False
    ) -> "OACitationsResponse":
        """Create an OACitationsResponse from a dictionary.

        Handles both the raw API envelope (``{"response": {...}}``) and
        a pre-unwrapped dictionary.

        Args:
            data: Dictionary containing API response data.
            include_raw_data: If True, store the raw JSON for debugging.

        Returns:
            OACitationsResponse: An instance of OACitationsResponse.
        """
        inner = data.get("response", data)

        docs_data = inner.get("docs", [])
        docs = (
            [
                OACitationRecord.from_dict(doc)
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
        """Convert the OACitationsResponse instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary wrapped in the ``"response"`` envelope
                matching the API format.
        """
        return {
            "response": {
                "numFound": self.num_found,
                "start": self.start,
                "docs": [doc.to_dict() for doc in self.docs],
            }
        }


@dataclass(frozen=True)
class OACitationsFieldsResponse:
    """Response from the OA Citations API fields endpoint.

    Contains metadata about the API including available field names
    and the last data update timestamp.

    Attributes:
        api_key: The dataset key (e.g., ``"oa_citations"``).
        api_version_number: API version (e.g., ``"v2"``).
        api_url: The URL of this fields endpoint.
        api_documentation_url: URL to the API documentation.
        api_status: Publication status (e.g., ``"PUBLISHED"``).
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
    ) -> "OACitationsFieldsResponse":
        """Create an OACitationsFieldsResponse from a dictionary.

        Args:
            data: Dictionary containing API response data.
            include_raw_data: Unused. Present for FromDictProtocol conformance.

        Returns:
            OACitationsFieldsResponse: An instance of OACitationsFieldsResponse.
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
        """Convert the OACitationsFieldsResponse instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation with camelCase keys.
        """
        d: dict[str, Any] = {
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
