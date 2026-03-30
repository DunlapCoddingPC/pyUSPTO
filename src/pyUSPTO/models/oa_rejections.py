"""models.oa_rejections - Data models for USPTO Office Action Rejections API.

This module provides data models for representing responses from the USPTO
Office Action Rejections API (v2). These models cover rejection-level data
from Office Actions including rejection type indicators, claim arrays, and
examiner classification metadata.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from pyUSPTO.models.utils import parse_to_datetime_utc, serialize_datetime_as_naive


@dataclass(frozen=True)
class OARejectionsRecord:
    """A single rejection record from the OA Rejections API.

    Attributes:
        id: Unique record identifier (hex hash).
        patent_application_number: USPTO patent application number.
        legacy_document_code_identifier: Document code (e.g., ``"CTNF"``, ``"NOA"``).
        action_type_category: Type of office action (e.g., ``"rejected"``).
        legal_section_code: Legal provision under which the action was taken.
        group_art_unit_number: Examiner group art unit (e.g., ``"1713"``).
        national_class: USPC national class code.
        national_subclass: USPC national subclass code.
        paragraph_number: Paragraph number referenced in the action.
        obsolete_document_identifier: Legacy IFW document identifier.
        create_user_identifier: Job identifier that inserted this record.
        claim_number_array_document: Claim numbers referenced in this record,
            split from the API's comma-separated string format.
        submission_date: Date the office action was submitted.
        create_date_time: Timestamp when this record was inserted into the database.
        has_rej_101: Whether a 35 U.S.C. § 101 rejection was raised.
        has_rej_102: Whether a 35 U.S.C. § 102 rejection was raised.
        has_rej_103: Whether a 35 U.S.C. § 103 rejection was raised.
        has_rej_112: Whether a 35 U.S.C. § 112 rejection was raised.
        has_rej_dp: Whether a non-statutory double patenting rejection was raised.
        cite_103_max: Largest number of references in any single § 103 rejection.
        cite_103_eq1: Whether exactly one reference was cited in a § 103 rejection.
        cite_103_gt3: Whether more than three references were cited in a § 103 rejection.
        closing_missing: Whether the closing paragraph is missing from the action.
        reject_form_missmatch: Whether the form content doesn't match the document code.
            Note: field name preserves the API's original spelling.
        form_paragraph_missing: Whether a required form paragraph is missing.
        header_missing: Whether the standard metadata header is missing.
        bilski_indicator: Whether the Bilski v. Kappos decision is referenced.
        mayo_indicator: Whether the Mayo v. Prometheus decision is referenced.
        alice_indicator: Whether the Alice/Mayo framework is applied for § 101 review.
        myriad_indicator: Whether the Myriad Genetics decision is applied.
        allowed_claim_indicator: Whether the application contains allowed claims.
    """

    id: str = ""
    patent_application_number: str | None = None
    legacy_document_code_identifier: str | None = None
    action_type_category: str | None = None
    legal_section_code: str | None = None
    group_art_unit_number: str | None = None
    national_class: str | None = None
    national_subclass: str | None = None
    paragraph_number: str | None = None
    obsolete_document_identifier: str | None = None
    create_user_identifier: str | None = None
    claim_number_array_document: list[str] = field(default_factory=list)
    submission_date: datetime | None = None
    create_date_time: datetime | None = None
    has_rej_101: bool | None = None
    has_rej_102: bool | None = None
    has_rej_103: bool | None = None
    has_rej_112: bool | None = None
    has_rej_dp: bool | None = None
    cite_103_max: int | None = None
    cite_103_eq1: int | None = None
    cite_103_gt3: int | None = None
    closing_missing: int | None = None
    reject_form_missmatch: int | None = None
    form_paragraph_missing: int | None = None
    header_missing: int | None = None
    bilski_indicator: bool | None = None
    mayo_indicator: bool | None = None
    alice_indicator: bool | None = None
    myriad_indicator: bool | None = None
    allowed_claim_indicator: bool | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OARejectionsRecord":
        """Create an OARejectionsRecord from a dictionary.

        Args:
            data: Dictionary containing rejection record data from API response.

        Returns:
            OARejectionsRecord: An instance of OARejectionsRecord.
        """

        def _get_bool(key: str) -> bool | None:
            val = data.get(key)
            if val is None:
                return None
            return bool(val)

        def _get_int(key: str) -> int | None:
            val = data.get(key)
            if val is None:
                return None
            return int(val)

        # Split comma-separated claim numbers from the list-of-strings API format
        raw_claims = data.get("claimNumberArrayDocument", [])
        if not isinstance(raw_claims, list):
            raw_claims = []
        claim_number_array_document: list[str] = []
        for item in raw_claims:
            if isinstance(item, str):
                claim_number_array_document.extend(
                    s.strip() for s in item.split(",") if s.strip()
                )

        return cls(
            id=data.get("id", ""),
            patent_application_number=data.get("patentApplicationNumber"),
            legacy_document_code_identifier=data.get("legacyDocumentCodeIdentifier"),
            action_type_category=data.get("actionTypeCategory"),
            legal_section_code=data.get("legalSectionCode"),
            group_art_unit_number=data.get("groupArtUnitNumber"),
            national_class=data.get("nationalClass"),
            national_subclass=data.get("nationalSubclass"),
            paragraph_number=data.get("paragraphNumber"),
            obsolete_document_identifier=data.get("obsoleteDocumentIdentifier"),
            create_user_identifier=data.get("createUserIdentifier"),
            claim_number_array_document=claim_number_array_document,
            submission_date=parse_to_datetime_utc(data.get("submissionDate")),
            create_date_time=parse_to_datetime_utc(data.get("createDateTime")),
            has_rej_101=_get_bool("hasRej101"),
            has_rej_102=_get_bool("hasRej102"),
            has_rej_103=_get_bool("hasRej103"),
            has_rej_112=_get_bool("hasRej112"),
            has_rej_dp=_get_bool("hasRejDP"),
            cite_103_max=_get_int("cite103Max"),
            cite_103_eq1=_get_int("cite103EQ1"),
            cite_103_gt3=_get_int("cite103GT3"),
            closing_missing=_get_int("closingMissing"),
            reject_form_missmatch=_get_int("rejectFormMissmatch"),
            form_paragraph_missing=_get_int("formParagraphMissing"),
            header_missing=_get_int("headerMissing"),
            bilski_indicator=_get_bool("bilskiIndicator"),
            mayo_indicator=_get_bool("mayoIndicator"),
            alice_indicator=_get_bool("aliceIndicator"),
            myriad_indicator=_get_bool("myriadIndicator"),
            allowed_claim_indicator=_get_bool("allowedClaimIndicator"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the OARejectionsRecord instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary with camelCase keys matching the API format.
                Claim numbers are joined back to a comma-separated string in a list.
                None values and empty lists are omitted.
        """
        claims_serialized = (
            [",".join(self.claim_number_array_document)]
            if self.claim_number_array_document
            else []
        )
        d: dict[str, Any] = {
            "id": self.id,
            "patentApplicationNumber": self.patent_application_number,
            "legacyDocumentCodeIdentifier": self.legacy_document_code_identifier,
            "actionTypeCategory": self.action_type_category,
            "legalSectionCode": self.legal_section_code,
            "groupArtUnitNumber": self.group_art_unit_number,
            "nationalClass": self.national_class,
            "nationalSubclass": self.national_subclass,
            "paragraphNumber": self.paragraph_number,
            "obsoleteDocumentIdentifier": self.obsolete_document_identifier,
            "createUserIdentifier": self.create_user_identifier,
            "claimNumberArrayDocument": claims_serialized,
            "submissionDate": (
                serialize_datetime_as_naive(self.submission_date)
                if self.submission_date
                else None
            ),
            "createDateTime": (
                serialize_datetime_as_naive(self.create_date_time)
                if self.create_date_time
                else None
            ),
            "hasRej101": self.has_rej_101,
            "hasRej102": self.has_rej_102,
            "hasRej103": self.has_rej_103,
            "hasRej112": self.has_rej_112,
            "hasRejDP": self.has_rej_dp,
            "cite103Max": self.cite_103_max,
            "cite103EQ1": self.cite_103_eq1,
            "cite103GT3": self.cite_103_gt3,
            "closingMissing": self.closing_missing,
            "rejectFormMissmatch": self.reject_form_missmatch,
            "formParagraphMissing": self.form_paragraph_missing,
            "headerMissing": self.header_missing,
            "bilskiIndicator": self.bilski_indicator,
            "mayoIndicator": self.mayo_indicator,
            "aliceIndicator": self.alice_indicator,
            "myriadIndicator": self.myriad_indicator,
            "allowedClaimIndicator": self.allowed_claim_indicator,
        }
        return {
            k: v
            for k, v in d.items()
            if v is not None and (not isinstance(v, list) or v)
        }


@dataclass(frozen=True)
class OARejectionsResponse:
    """Response from the OA Rejections API search endpoint.

    The API returns a Solr-style response with ``start``, ``numFound``, and ``docs``.
    The outer envelope key is ``"response"``.

    Attributes:
        num_found: Total number of matching records.
        start: The start index of the first result in this page.
        docs: List of rejection records in this page.
        raw_data: Optional raw JSON data from the API response (for debugging).
    """

    num_found: int = 0
    start: int = 0
    docs: list[OARejectionsRecord] = field(default_factory=list)
    raw_data: str | None = field(default=None, compare=False, repr=False)

    @property
    def count(self) -> int:
        """Return total result count for pagination compatibility."""
        return self.num_found

    @classmethod
    def from_dict(
        cls, data: dict[str, Any], include_raw_data: bool = False
    ) -> "OARejectionsResponse":
        """Create an OARejectionsResponse from a dictionary.

        Handles both the raw API envelope (``{"response": {...}}``) and
        a pre-unwrapped dictionary.

        Args:
            data: Dictionary containing API response data.
            include_raw_data: If True, store the raw JSON for debugging.

        Returns:
            OARejectionsResponse: An instance of OARejectionsResponse.
        """
        inner = data.get("response", data)

        docs_data = inner.get("docs", [])
        docs = (
            [
                OARejectionsRecord.from_dict(doc)
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
        """Convert the OARejectionsResponse instance to a dictionary.

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
class OARejectionsFieldsResponse:
    """Response from the OA Rejections API fields endpoint.

    Contains metadata about the API including available field names
    and the last data update timestamp.

    Attributes:
        api_key: The dataset key (e.g., ``"oa_rejections"``).
        api_version_number: API version (e.g., ``"v2"``).
        api_url: The URL of this fields endpoint.
        api_documentation_url: URL to the Swagger documentation.
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
    ) -> "OARejectionsFieldsResponse":
        """Create an OARejectionsFieldsResponse from a dictionary.

        Args:
            data: Dictionary containing API response data.
            include_raw_data: Unused. Present for FromDictProtocol conformance.

        Returns:
            OARejectionsFieldsResponse: An instance of OARejectionsFieldsResponse.
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
        """Convert the OARejectionsFieldsResponse instance to a dictionary.

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
