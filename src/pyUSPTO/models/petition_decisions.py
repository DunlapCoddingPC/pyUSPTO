"""models.petition_decisions - Data models for the USPTO Petition Decisions API.

This module provides data models, primarily using frozen dataclasses, for
representing responses from the USPTO Petition Decisions API. These models
cover petition decision records, associated documents, and download options.
"""

import json
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any

# Import parsing utilities from models utils module
from pyUSPTO.models.utils import (
    parse_to_date,
    parse_to_datetime_utc,
    serialize_date,
    serialize_datetime_as_naive,
)


# --- Enums for Categorical Data ---
class DecisionTypeCode(Enum):
    """Represents the decided type of a petition decision.

    Values match ``decidedPetitionTypeCodeDescriptionText``; the single-letter
    aliases match ``decidedPetitionTypeCode``.
    """

    GRANTED = "GRANTED"
    GRANTED_IN_PART = "GRANTED-IN-PART"
    DENIED = "DENIED"
    DISMISSED = "DISMISSED"
    A = GRANTED
    B = GRANTED_IN_PART
    C = DENIED
    D = DISMISSED

    @classmethod
    def _missing_(cls, value: Any) -> "DecisionTypeCode":
        """Handle case-insensitive lookup by description or letter code."""
        if isinstance(value, str):
            val_upper = value.upper()
            for member in cls:
                if member.value == val_upper:
                    return member
            if val_upper in cls.__members__:
                return cls.__members__[val_upper]
        raise ValueError(f"{value!r} is not a valid {cls.__name__}")


# --- Data Models ---
@dataclass(frozen=True)
class DocumentDownloadOption:
    """Represent a download option for a petition decision document.

    Attributes:
        mime_type_identifier: The document format type (e.g., "PDF", "XML", "MS_WORD").
        download_url: The URL from which the document can be downloaded.
        page_total_quantity: The total number of pages in the document (if applicable).
    """

    mime_type_identifier: str | None = None
    download_url: str | None = None
    page_total_quantity: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DocumentDownloadOption":
        """Create a DocumentDownloadOption instance from a dictionary.

        Args:
            data: Dictionary containing download option data from API response.

        Returns:
            DocumentDownloadOption: An instance of DocumentDownloadOption.
        """
        return cls(
            mime_type_identifier=data.get("mimeTypeIdentifier"),
            download_url=data.get("downloadUrl"),
            page_total_quantity=data.get("pageTotalQuantity"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the DocumentDownloadOption instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation with camelCase keys.
        """
        d = {
            "mimeTypeIdentifier": self.mime_type_identifier,
            "downloadUrl": self.download_url,
            "pageTotalQuantity": self.page_total_quantity,
        }
        return {k: v for k, v in d.items() if v is not None}


@dataclass(frozen=True)
class PetitionDecisionDocument:
    """Represent a document associated with a petition decision.

    Attributes:
        official_date: The official date of the document.
        document_identifier: A unique identifier for the document.
        document_code: The code identifying the document type.
        document_code_description_text: Description of the document code.
        download_option_bag: List of available download options for the document.
    """

    official_date: datetime | None = None
    document_identifier: str | None = None
    document_code: str | None = None
    document_code_description_text: str | None = None
    download_option_bag: list[DocumentDownloadOption] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PetitionDecisionDocument":
        """Create a PetitionDecisionDocument instance from a dictionary.

        Args:
            data: Dictionary containing document data from API response.

        Returns:
            PetitionDecisionDocument: An instance of PetitionDecisionDocument.
        """
        # Parse download options
        download_options_data = data.get("downloadOptionBag", [])
        download_options = (
            [
                DocumentDownloadOption.from_dict(option)
                for option in download_options_data
                if isinstance(option, dict)
            ]
            if isinstance(download_options_data, list)
            else []
        )

        return cls(
            official_date=parse_to_datetime_utc(data.get("officialDate")),
            document_identifier=data.get("documentIdentifier"),
            document_code=data.get("documentCode"),
            document_code_description_text=data.get("documentCodeDescriptionText"),
            download_option_bag=download_options,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the PetitionDecisionDocument instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation with camelCase keys.
        """
        d = {
            "officialDate": (
                serialize_datetime_as_naive(self.official_date)
                if self.official_date
                else None
            ),
            "documentIdentifier": self.document_identifier,
            "documentCode": self.document_code,
            "documentCodeDescriptionText": self.document_code_description_text,
            "downloadOptionBag": [opt.to_dict() for opt in self.download_option_bag],
        }
        return {
            k: v
            for k, v in d.items()
            if v is not None and (not isinstance(v, list) or v)
        }


@dataclass(frozen=True)
class PetitionDecision:
    """Represent a petition decision record.

    This is the main data model representing a single petition decision from the
    USPTO Petition Decisions API. It contains comprehensive information about
    the decision, including application details, decision metadata, parties involved,
    and associated documents.

    Attributes:
        petition_decision_record_identifier: Unique identifier for the petition decision record.
        application_number_text: The USPTO application number.
        patent_number: The patent number if the application has been granted.
        decision_date: The date the decision was submitted for issuance or mailing.
        decision_mail_date: The date the decision was mailed.
        petition_mail_date: The date the decision was issued or mailed.
        decision_petition_type_code: Three-digit code for the petition type.
        decision_petition_type_code_description_text: Description of the petition type.
        decided_petition_type_code: Code for the decided type ("A" GRANTED,
            "B" GRANTED-IN-PART, "C" DENIED, "D" DISMISSED).
        decided_petition_type_code_description_text: Description of the decided type.
        final_petition_decision_indicator: Whether this is a final petition decision.
        final_deciding_office_name: The USPTO office that decided the petition.
        first_applicant_name: Name of the first applicant.
        first_inventor_name: Name of the first inventor (computed from inventor_bag).
        invention_title: Title of the invention/application.
        first_inventor_to_file_indicator: Whether this is a first-inventor-to-file application.
        business_entity_status_category: Entity status (e.g., "Small", "Micro", "Regular Undiscounted").
        customer_number: Customer number for correspondence.
        group_art_unit_number: The art unit number.
        technology_center: The technology center code.
        application_status_date: The date of the application's current status.
        application_status_description_text: Description of the application's
            current status.
        prosecution_status_code: Code for the disposition of the petition.
        prosecution_status_code_description_text: Description of the prosecution status.
        action_taken_by_court_name: Name of court if court action was taken.
        court_action_indicator: Whether court action was taken on the decision.
        inventor_bag: List of inventor names.
        petition_issue_considered_text_bag: Issues under review in the petition.
        statute_bag: Applicable laws under United States Code Title 35.
        rule_bag: Applicable rules under Title 37 CFR.
        document_bag: Associated documents for this petition decision.
        ocr_search_text: OCR text of the decision document (may be truncated).
        all_searchable_fields: The record's searchable text fields concatenated
            into one string, as returned by the API.
        last_modified_date_time: The last time the record was modified.
    """

    petition_decision_record_identifier: str
    application_number_text: str | None = None
    patent_number: str | None = None
    decision_date: date | None = None
    decision_mail_date: date | None = None
    petition_mail_date: date | None = None
    decision_petition_type_code: str | None = None
    decision_petition_type_code_description_text: str | None = None
    decided_petition_type_code: str | None = None
    decided_petition_type_code_description_text: str | None = None
    final_petition_decision_indicator: bool | None = None
    final_deciding_office_name: str | None = None
    first_applicant_name: str | None = None
    first_inventor_name: str | None = None
    invention_title: str | None = None
    first_inventor_to_file_indicator: bool | None = None
    business_entity_status_category: str | None = None
    customer_number: int | None = None
    group_art_unit_number: str | None = None
    technology_center: str | None = None
    application_status_date: date | None = None
    application_status_description_text: str | None = None
    prosecution_status_code: str | None = None
    prosecution_status_code_description_text: str | None = None
    action_taken_by_court_name: str | None = None
    court_action_indicator: bool | None = None
    inventor_bag: list[str] = field(default_factory=list)
    petition_issue_considered_text_bag: list[str] = field(default_factory=list)
    statute_bag: list[str] = field(default_factory=list)
    rule_bag: list[str] = field(default_factory=list)
    document_bag: list[PetitionDecisionDocument] = field(default_factory=list)
    ocr_search_text: str | None = None
    all_searchable_fields: str | None = None
    last_modified_date_time: datetime | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PetitionDecision":
        """Create a PetitionDecision instance from a dictionary.

        Args:
            data: Dictionary containing petition decision data from API response.

        Returns:
            PetitionDecision: An instance of PetitionDecision.
        """
        # Parse document bag
        documents_data = data.get("documentBag", [])
        documents = (
            [
                PetitionDecisionDocument.from_dict(doc)
                for doc in documents_data
                if isinstance(doc, dict)
            ]
            if isinstance(documents_data, list)
            else []
        )

        # Parse simple string lists
        inventor_bag = data.get("inventorBag", [])
        if not isinstance(inventor_bag, list):
            inventor_bag = []

        petition_issues = data.get("petitionIssueConsideredTextBag", [])
        if not isinstance(petition_issues, list):
            petition_issues = []

        statute_bag = data.get("statuteBag", [])
        if not isinstance(statute_bag, list):
            statute_bag = []

        rule_bag = data.get("ruleBag", [])
        if not isinstance(rule_bag, list):
            rule_bag = []

        # Compute first inventor name from inventor bag
        first_inventor_name = inventor_bag[0] if inventor_bag else None

        return cls(
            petition_decision_record_identifier=data.get(
                "petitionDecisionRecordIdentifier", ""
            ),
            application_number_text=data.get("applicationNumberText"),
            patent_number=data.get("patentNumber"),
            decision_date=parse_to_date(data.get("decisionDate")),
            decision_mail_date=parse_to_date(data.get("decisionMailDate")),
            petition_mail_date=parse_to_date(data.get("petitionMailDate")),
            decision_petition_type_code=data.get("decisionPetitionTypeCode"),
            decision_petition_type_code_description_text=data.get(
                "decisionPetitionTypeCodeDescriptionText"
            ),
            decided_petition_type_code=data.get("decidedPetitionTypeCode"),
            decided_petition_type_code_description_text=data.get(
                "decidedPetitionTypeCodeDescriptionText"
            ),
            final_petition_decision_indicator=data.get(
                "finalPetitionDecisionIndicator"
            ),
            final_deciding_office_name=data.get("finalDecidingOfficeName"),
            first_applicant_name=data.get("firstApplicantName"),
            first_inventor_name=first_inventor_name,
            invention_title=data.get("inventionTitle"),
            first_inventor_to_file_indicator=data.get("firstInventorToFileIndicator"),
            business_entity_status_category=data.get("businessEntityStatusCategory"),
            customer_number=data.get("customerNumber"),
            group_art_unit_number=data.get("groupArtUnitNumber"),
            technology_center=data.get("technologyCenter"),
            application_status_date=parse_to_date(data.get("applicationStatusDate")),
            application_status_description_text=data.get(
                "applicationStatusDescriptionText"
            ),
            prosecution_status_code=data.get("prosecutionStatusCode"),
            prosecution_status_code_description_text=data.get(
                "prosecutionStatusCodeDescriptionText"
            ),
            action_taken_by_court_name=data.get("actionTakenByCourtName"),
            court_action_indicator=data.get("courtActionIndicator"),
            inventor_bag=inventor_bag,
            petition_issue_considered_text_bag=petition_issues,
            statute_bag=statute_bag,
            rule_bag=rule_bag,
            document_bag=documents,
            ocr_search_text=data.get("ocrSearchText"),
            all_searchable_fields=data.get("allSearchableFields"),
            last_modified_date_time=parse_to_datetime_utc(
                data.get("lastModifiedDateTime")
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the PetitionDecision instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation with camelCase keys.
        """
        d = {
            "petitionDecisionRecordIdentifier": self.petition_decision_record_identifier,
            "applicationNumberText": self.application_number_text,
            "patentNumber": self.patent_number,
            "decisionDate": serialize_date(self.decision_date),
            "decisionMailDate": serialize_date(self.decision_mail_date),
            "petitionMailDate": serialize_date(self.petition_mail_date),
            "decisionPetitionTypeCode": self.decision_petition_type_code,
            "decisionPetitionTypeCodeDescriptionText": self.decision_petition_type_code_description_text,
            "decidedPetitionTypeCode": self.decided_petition_type_code,
            "decidedPetitionTypeCodeDescriptionText": self.decided_petition_type_code_description_text,
            "finalPetitionDecisionIndicator": self.final_petition_decision_indicator,
            "finalDecidingOfficeName": self.final_deciding_office_name,
            "firstApplicantName": self.first_applicant_name,
            "inventionTitle": self.invention_title,
            "firstInventorToFileIndicator": self.first_inventor_to_file_indicator,
            "businessEntityStatusCategory": self.business_entity_status_category,
            "customerNumber": self.customer_number,
            "groupArtUnitNumber": self.group_art_unit_number,
            "technologyCenter": self.technology_center,
            "applicationStatusDate": serialize_date(self.application_status_date),
            "applicationStatusDescriptionText": self.application_status_description_text,
            "prosecutionStatusCode": self.prosecution_status_code,
            "prosecutionStatusCodeDescriptionText": self.prosecution_status_code_description_text,
            "actionTakenByCourtName": self.action_taken_by_court_name,
            "courtActionIndicator": self.court_action_indicator,
            "inventorBag": self.inventor_bag,
            "petitionIssueConsideredTextBag": self.petition_issue_considered_text_bag,
            "statuteBag": self.statute_bag,
            "ruleBag": self.rule_bag,
            "documentBag": [doc.to_dict() for doc in self.document_bag],
            "ocrSearchText": self.ocr_search_text,
            "allSearchableFields": self.all_searchable_fields,
            "lastModifiedDateTime": (
                serialize_datetime_as_naive(self.last_modified_date_time)
                if self.last_modified_date_time
                else None
            ),
        }
        return {
            k: v
            for k, v in d.items()
            if v is not None and (not isinstance(v, list) or v)
        }


@dataclass(frozen=True)
class PetitionDecisionResponse:
    """Response from the Petition Decisions API search endpoint.

    This is the standard response format for search queries to the
    /api/v1/petition/decisions/search endpoint and the get-by-ID endpoint.

    Attributes:
        count: The number of petition decisions returned in this response.
        request_identifier: A unique identifier for the API request.
        petition_decision_data_bag: List of petition decision records.
        raw_data: Optional raw JSON data from the API response (for debugging).
    """

    count: int = 0
    request_identifier: str | None = None
    petition_decision_data_bag: list[PetitionDecision] = field(default_factory=list)
    raw_data: str | None = field(default=None, compare=False, repr=False)

    @classmethod
    def from_dict(
        cls, data: dict[str, Any], include_raw_data: bool = False
    ) -> "PetitionDecisionResponse":
        """Create a PetitionDecisionResponse instance from a dictionary.

        Args:
            data: Dictionary containing API response data.
            include_raw_data: If True, store the raw JSON for debugging.

        Returns:
            PetitionDecisionResponse: An instance of PetitionDecisionResponse.
        """
        # Parse petition decisions
        decisions_data = data.get("petitionDecisionDataBag", [])
        decisions = (
            [
                PetitionDecision.from_dict(decision)
                for decision in decisions_data
                if isinstance(decision, dict)
            ]
            if isinstance(decisions_data, list)
            else []
        )

        return cls(
            count=data.get("count", 0),
            request_identifier=data.get("requestIdentifier"),
            petition_decision_data_bag=decisions,
            raw_data=json.dumps(data) if include_raw_data else None,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the PetitionDecisionResponse instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation with camelCase keys.
        """
        d = {
            "count": self.count,
            "requestIdentifier": self.request_identifier,
            "petitionDecisionDataBag": [
                decision.to_dict() for decision in self.petition_decision_data_bag
            ],
        }
        return {
            k: v
            for k, v in d.items()
            if v is not None and (not isinstance(v, list) or v)
        }


@dataclass(frozen=True)
class PetitionDecisionDownloadResponse:
    """Response from the Petition Decisions API download endpoint.

    This is the response format for download queries to the
    /api/v1/petition/decisions/search/download endpoint when format=json.
    Note that the structure is slightly different from the search endpoint.

    Attributes:
        petition_decision_data: List of petition decision records.
    """

    petition_decision_data: list[PetitionDecision] = field(default_factory=list)

    @classmethod
    def from_dict(
        cls, data: dict[str, Any], include_raw_data: bool = False
    ) -> "PetitionDecisionDownloadResponse":
        """Create a PetitionDecisionDownloadResponse instance from a dictionary.

        Args:
            data: Dictionary containing download API response data.
            include_raw_data: Unused. Present for FromDictProtocol conformance.

        Returns:
            PetitionDecisionDownloadResponse: An instance of PetitionDecisionDownloadResponse.
        """
        # Parse petition decisions (note different key name for download endpoint)
        decisions_data = data.get("petitionDecisionData", [])
        decisions = (
            [
                PetitionDecision.from_dict(decision)
                for decision in decisions_data
                if isinstance(decision, dict)
            ]
            if isinstance(decisions_data, list)
            else []
        )

        return cls(petition_decision_data=decisions)

    def to_dict(self) -> dict[str, Any]:
        """Convert the PetitionDecisionDownloadResponse instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation with camelCase keys.
        """
        d = {
            "petitionDecisionData": [
                decision.to_dict() for decision in self.petition_decision_data
            ],
        }
        return {
            k: v
            for k, v in d.items()
            if v is not None and (not isinstance(v, list) or v)
        }
