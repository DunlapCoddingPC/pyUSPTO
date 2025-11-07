"""
models.petition_decisions - Data models for USPTO Final Petition Decisions API

This module provides data models, primarily using frozen dataclasses, for
representing responses from the USPTO Final Petition Decisions API. These models
cover petition decision records, associated documents, and download options.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional

# Import parsing utilities from patent_data module
from pyUSPTO.models.patent_data import (
    parse_to_date,
    parse_to_datetime_utc,
    serialize_date,
    serialize_datetime_as_iso,
)


# --- Enums for Categorical Data ---
class DecisionTypeCode(Enum):
    """Represents the type of decision made on a petition.

    The only current value possible is "c" which indicates DENIED.
    Hopefully the USPTO will give access to others in the future.
    """

    # GRANTED = "GRANTED"
    DENIED = "DENIED"
    # DISMISSED = "DISMISSED"
    C = DENIED

    @classmethod
    def _missing_(cls, value: Any) -> "DecisionTypeCode":
        """Handle case-insensitive lookup and common aliases."""
        if isinstance(value, str):
            val_upper = value.upper()
            # if val_upper == "GRANTED":
            #     return cls.GRANTED
            if val_upper in ("DENIED", "C"):
                return cls.DENIED
            # if val_upper == "DISMISSED":
            #     return cls.DISMISSED
        return super()._missing_(value=value)  # type: ignore[no-any-return]


class DocumentDirectionCategory(Enum):
    """Represents the direction of a document relative to the USPTO."""

    INCOMING = "INCOMING"
    OUTGOING = "OUTGOING"

    @classmethod
    def _missing_(cls, value: Any) -> "DocumentDirectionCategory":
        """Handle case-insensitive lookup."""
        if isinstance(value, str):
            val_upper = value.upper()
            if val_upper == "INCOMING":
                return cls.INCOMING
            if val_upper == "OUTGOING":
                return cls.OUTGOING
        return super()._missing_(value=value)  # type: ignore[no-any-return]


# --- Data Models ---
@dataclass(frozen=True)
class DocumentDownloadOption:
    """Represents a download option for a petition decision document.

    Attributes:
        mime_type_identifier: The document format type (e.g., "PDF", "XML", "MS_WORD").
        download_url: The URL from which the document can be downloaded.
        page_total_quantity: The total number of pages in the document (if applicable).
    """

    mime_type_identifier: Optional[str] = None
    download_url: Optional[str] = None
    page_total_quantity: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentDownloadOption":
        """Creates a DocumentDownloadOption instance from a dictionary.

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

    def to_dict(self) -> Dict[str, Any]:
        """Converts the DocumentDownloadOption instance to a dictionary.

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
    """Represents a document associated with a petition decision.

    Attributes:
        application_number_text: The application number associated with the document.
        official_date: The official date of the document.
        document_identifier: A unique identifier for the document.
        document_code: The code identifying the document type.
        document_code_description_text: Description of the document code.
        document_direction_category: Whether the document is INCOMING or OUTGOING.
        download_option_bag: List of available download options for the document.
    """

    application_number_text: Optional[str] = None
    official_date: Optional[datetime] = None
    document_identifier: Optional[str] = None
    document_code: Optional[str] = None
    document_code_description_text: Optional[str] = None
    document_direction_category: Optional[str] = None
    download_option_bag: List[DocumentDownloadOption] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PetitionDecisionDocument":
        """Creates a PetitionDecisionDocument instance from a dictionary.

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
            application_number_text=data.get("applicationNumberText"),
            official_date=parse_to_datetime_utc(data.get("officialDate")),
            document_identifier=data.get("documentIdentifier"),
            document_code=data.get("documentCode"),
            document_code_description_text=data.get("documentCodeDescriptionText"),
            document_direction_category=data.get("documentDirectionCategory"),
            download_option_bag=download_options,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the PetitionDecisionDocument instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation with camelCase keys.
        """
        d = {
            "applicationNumberText": self.application_number_text,
            "officialDate": serialize_datetime_as_iso(self.official_date),
            "documentIdentifier": self.document_identifier,
            "documentCode": self.document_code,
            "documentCodeDescriptionText": self.document_code_description_text,
            "documentDirectionCategory": self.document_direction_category,
            "downloadOptionBag": [opt.to_dict() for opt in self.download_option_bag],
        }
        return {
            k: v
            for k, v in d.items()
            if v is not None and (not isinstance(v, list) or v)
        }


@dataclass(frozen=True)
class PetitionDecision:
    """Represents a final petition decision record.

    This is the main data model representing a single petition decision from the
    USPTO Final Petition Decisions API. It contains comprehensive information about
    the decision, including application details, decision metadata, parties involved,
    and associated documents.

    Attributes:
        petition_decision_record_identifier: Unique identifier for the petition decision record.
        application_number_text: The USPTO application number.
        patent_number: The patent number if the application has been granted.
        decision_date: The date the decision was submitted for issuance or mailing.
        petition_mail_date: The date the decision was issued or mailed.
        decision_petition_type_code: Three-digit code for the petition type.
        decision_type_code: Code indicating the decision type (e.g., "C" for DENIED).
        decision_type_code_description_text: Description of the decision type.
        final_deciding_office_name: The USPTO office that decided the petition.
        first_applicant_name: Name of the first applicant.
        first_inventor_name: Name of the first inventor (computed from inventor_bag).
        invention_title: Title of the invention/application.
        first_inventor_to_file_indicator: Whether this is a first-inventor-to-file application.
        business_entity_status_category: Entity status (e.g., "Small", "Micro", "Regular Undiscounted").
        customer_number: Customer number for correspondence.
        group_art_unit_number: The art unit number.
        technology_center: The technology center code.
        prosecution_status_code: Code for the disposition of the petition.
        prosecution_status_code_description_text: Description of the prosecution status.
        action_taken_by_court_name: Name of court if court action was taken.
        court_action_indicator: Whether court action was taken on the decision.
        inventor_bag: List of inventor names.
        petition_issue_considered_text_bag: Issues under review in the petition.
        statute_bag: Applicable laws under United States Code Title 35.
        rule_bag: Applicable rules under Title 37 CFR.
        document_bag: Associated documents for this petition decision.
        last_ingestion_datetime: The last time the record was ingested/updated.
    """

    petition_decision_record_identifier: Optional[str] = None
    application_number_text: Optional[str] = None
    patent_number: Optional[str] = None
    decision_date: Optional[date] = None
    petition_mail_date: Optional[date] = None
    decision_petition_type_code: Optional[int] = None
    decision_type_code: Optional[str] = None
    decision_type_code_description_text: Optional[str] = None
    final_deciding_office_name: Optional[str] = None
    first_applicant_name: Optional[str] = None
    first_inventor_name: Optional[str] = None
    invention_title: Optional[str] = None
    first_inventor_to_file_indicator: Optional[bool] = None
    business_entity_status_category: Optional[str] = None
    customer_number: Optional[int] = None
    group_art_unit_number: Optional[str] = None
    technology_center: Optional[str] = None
    prosecution_status_code: Optional[str] = None
    prosecution_status_code_description_text: Optional[str] = None
    action_taken_by_court_name: Optional[str] = None
    court_action_indicator: Optional[bool] = None
    inventor_bag: List[str] = field(default_factory=list)
    petition_issue_considered_text_bag: List[str] = field(default_factory=list)
    statute_bag: List[str] = field(default_factory=list)
    rule_bag: List[str] = field(default_factory=list)
    document_bag: List[PetitionDecisionDocument] = field(default_factory=list)
    last_ingestion_datetime: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PetitionDecision":
        """Creates a PetitionDecision instance from a dictionary.

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
                "petitionDecisionRecordIdentifier"
            ),
            application_number_text=data.get("applicationNumberText"),
            patent_number=data.get("patentNumber"),
            decision_date=parse_to_date(data.get("decisionDate")),
            petition_mail_date=parse_to_date(data.get("petitionMailDate")),
            decision_petition_type_code=data.get("decisionPetitionTypeCode"),
            decision_type_code=data.get("decisionTypeCode"),
            decision_type_code_description_text=data.get(
                "decisionTypeCodeDescriptionText"
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
            last_ingestion_datetime=parse_to_datetime_utc(
                data.get("lastIngestionDateTime")
            ),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the PetitionDecision instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation with camelCase keys.
        """
        d = {
            "petitionDecisionRecordIdentifier": self.petition_decision_record_identifier,
            "applicationNumberText": self.application_number_text,
            "patentNumber": self.patent_number,
            "decisionDate": serialize_date(self.decision_date),
            "petitionMailDate": serialize_date(self.petition_mail_date),
            "decisionPetitionTypeCode": self.decision_petition_type_code,
            "decisionTypeCode": self.decision_type_code,
            "decisionTypeCodeDescriptionText": self.decision_type_code_description_text,
            "finalDecidingOfficeName": self.final_deciding_office_name,
            "firstApplicantName": self.first_applicant_name,
            "inventionTitle": self.invention_title,
            "firstInventorToFileIndicator": self.first_inventor_to_file_indicator,
            "businessEntityStatusCategory": self.business_entity_status_category,
            "customerNumber": self.customer_number,
            "groupArtUnitNumber": self.group_art_unit_number,
            "technologyCenter": self.technology_center,
            "prosecutionStatusCode": self.prosecution_status_code,
            "prosecutionStatusCodeDescriptionText": self.prosecution_status_code_description_text,
            "actionTakenByCourtName": self.action_taken_by_court_name,
            "courtActionIndicator": self.court_action_indicator,
            "inventorBag": self.inventor_bag,
            "petitionIssueConsideredTextBag": self.petition_issue_considered_text_bag,
            "statuteBag": self.statute_bag,
            "ruleBag": self.rule_bag,
            "documentBag": [doc.to_dict() for doc in self.document_bag],
            "lastIngestionDateTime": serialize_datetime_as_iso(
                self.last_ingestion_datetime
            ),
        }
        return {
            k: v
            for k, v in d.items()
            if v is not None and (not isinstance(v, list) or v)
        }


@dataclass(frozen=True)
class PetitionDecisionResponse:
    """Response from the Final Petition Decisions API search endpoint.

    This is the standard response format for search queries to the
    /api/v1/petition/decisions/search endpoint and the get-by-ID endpoint.

    Attributes:
        count: The number of petition decisions returned in this response.
        request_identifier: A unique identifier for the API request.
        petition_decision_data_bag: List of petition decision records.
    """

    count: Optional[int] = None
    request_identifier: Optional[str] = None
    petition_decision_data_bag: List[PetitionDecision] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PetitionDecisionResponse":
        """Creates a PetitionDecisionResponse instance from a dictionary.

        Args:
            data: Dictionary containing API response data.

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
            count=data.get("count"),
            request_identifier=data.get("requestIdentifier"),
            petition_decision_data_bag=decisions,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the PetitionDecisionResponse instance to a dictionary.

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
    """Response from the Final Petition Decisions API download endpoint.

    This is the response format for download queries to the
    /api/v1/petition/decisions/search/download endpoint when format=json.
    Note that the structure is slightly different from the search endpoint.

    Attributes:
        petition_decision_data: List of petition decision records.
    """

    petition_decision_data: List[PetitionDecision] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PetitionDecisionDownloadResponse":
        """Creates a PetitionDecisionDownloadResponse instance from a dictionary.

        Args:
            data: Dictionary containing download API response data.

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

    def to_dict(self) -> Dict[str, Any]:
        """Converts the PetitionDecisionDownloadResponse instance to a dictionary.

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
