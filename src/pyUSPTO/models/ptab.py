"""
models.ptab - Data models for USPTO PTAB (Patent Trial and Appeal Board) APIs

This module provides data models, primarily using frozen dataclasses, for
representing responses from the USPTO PTAB APIs. These models cover:
- Patent trial proceedings (IPR, PGR, CBM, DER)
- Trial documents and decisions
- Appeal decisions
- Interference decisions
"""

import json
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import Any, Dict, List, Optional

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

# Import parsing utilities from models utils module
from pyUSPTO.models.utils import (
    parse_to_date,
    parse_to_datetime_utc,
    serialize_date,
    serialize_datetime_as_iso,
    serialize_datetime_as_naive,
    to_camel_case,
)


@dataclass(frozen=True)
class PartyData:
    """Base class for all party data models across PTAB endpoints.

    Attributes:
        application_number_text: Application number.
        counsel_name: Name of counsel.
        grant_date: Patent grant date.
        group_art_unit_number: Art unit number.
        inventor_name: Name of inventor.
        patent_number: Patent number.
        technology_center_number: Technology center number.
        real_party_in_interest_name: Real party in interest name.
        patent_owner_name: Patent owner name.
        publication_date: Publication date (if applicable).
        publication_number: Publication number (if applicable).
    """

    application_number_text: Optional[str] = None
    counsel_name: Optional[str] = None
    grant_date: Optional[date] = None
    group_art_unit_number: Optional[str] = None
    inventor_name: Optional[str] = None
    real_party_in_interest_name: Optional[str] = None
    patent_number: Optional[str] = None
    patent_owner_name: Optional[str] = None
    technology_center_number: Optional[str] = None
    publication_date: Optional[date] = None
    publication_number: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any], include_raw_data: bool = False) -> Self:
        """Creates a PartyData instance from a dictionary.

        Args:
            data: Dictionary containing party data from API response.
            include_raw_data: Ignored for this model.

        Returns:
            PartyData: A populated PartyData instance.
        """
        return cls(
            application_number_text=data.get("applicationNumberText"),
            counsel_name=data.get("counselName"),
            grant_date=parse_to_date(data.get("grantDate")),
            group_art_unit_number=data.get("groupArtUnitNumber"),
            inventor_name=data.get("inventorName"),
            real_party_in_interest_name=data.get("realPartyInInterestName"),
            patent_number=data.get("patentNumber"),
            patent_owner_name=data.get("patentOwnerName"),
            technology_center_number=data.get("technologyCenterNumber"),
            publication_date=parse_to_date(data.get("publicationDate")),
            publication_number=data.get("publicationNumber"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the PartyData instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary with camelCase keys and None values filtered.
        """
        result: Dict[str, Any] = {}
        for k, v in asdict(self).items():
            if v is not None:
                if isinstance(v, date):
                    result[to_camel_case(k)] = serialize_date(v)
                else:
                    result[to_camel_case(k)] = v
        return result


# ============================================================================
# TRIAL PROCEEDINGS MODELS
# ============================================================================


@dataclass(frozen=True)
class TrialMetaData:
    """Trial metadata including status, dates, and download URI.

    Attributes:
        petition_filing_date: Date the petition was filed.
        accorded_filing_date: The filing date accorded to the petition.
        trial_last_modified_date_time: Last modification timestamp.
        trial_last_modified_date: Last modification date.
        trial_status_category: Status of the trial (e.g., "Institution Denied", "Instituted").
        trial_type_code: Type of trial (IPR, PGR, CBM, DER).
        file_download_uri: URI to download ZIP of all trial documents.
        termination_date: Date the trial was terminated.
        latest_decision_date: Date of the most recent decision.
        institution_decision_date: Date of the institution decision.
    """

    petition_filing_date: Optional[date] = None
    accorded_filing_date: Optional[date] = None
    trial_last_modified_date_time: Optional[datetime] = None
    trial_last_modified_date: Optional[date] = None
    trial_status_category: Optional[str] = None
    trial_type_code: Optional[str] = None
    file_download_uri: Optional[str] = None
    termination_date: Optional[date] = None
    latest_decision_date: Optional[date] = None
    institution_decision_date: Optional[date] = None

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], include_raw_data: bool = False
    ) -> "TrialMetaData":
        """Creates a TrialMetaData instance from a dictionary.

        Args:
            data: Dictionary containing trial metadata from API response.
            include_raw_data: Ignored for this model (no raw_data field).

        Returns:
            TrialMetaData: An instance of TrialMetaData.
        """
        # Handle aliases
        file_download_uri = data.get("fileDownloadURI") or data.get("downloadURI")
        return cls(
            petition_filing_date=parse_to_date(data.get("petitionFilingDate")),
            accorded_filing_date=parse_to_date(data.get("accordedFilingDate")),
            trial_last_modified_date_time=parse_to_datetime_utc(
                data.get("trialLastModifiedDateTime")
            ),
            trial_last_modified_date=parse_to_date(data.get("trialLastModifiedDate")),
            trial_status_category=data.get("trialStatusCategory"),
            trial_type_code=data.get("trialTypeCode"),
            file_download_uri=file_download_uri,
            termination_date=parse_to_date(data.get("terminationDate")),
            latest_decision_date=parse_to_date(data.get("latestDecisionDate")),
            institution_decision_date=parse_to_date(
                data.get("institutionDecisionDate")
            ),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the TrialMetaData instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary with camelCase keys and None values filtered.
        """
        result: Dict[str, Any] = {}

        if self.petition_filing_date is not None:
            result["petitionFilingDate"] = serialize_date(self.petition_filing_date)
        if self.accorded_filing_date is not None:
            result["accordedFilingDate"] = serialize_date(self.accorded_filing_date)
        if self.trial_last_modified_date_time is not None:
            result["trialLastModifiedDateTime"] = serialize_datetime_as_naive(
                self.trial_last_modified_date_time
            )
        if self.trial_last_modified_date is not None:
            result["trialLastModifiedDate"] = serialize_date(
                self.trial_last_modified_date
            )
        if self.trial_status_category is not None:
            result["trialStatusCategory"] = self.trial_status_category
        if self.trial_type_code is not None:
            result["trialTypeCode"] = self.trial_type_code
        if self.file_download_uri is not None:
            result["fileDownloadURI"] = self.file_download_uri
        if self.termination_date is not None:
            result["terminationDate"] = serialize_date(self.termination_date)
        if self.latest_decision_date is not None:
            result["latestDecisionDate"] = serialize_date(self.latest_decision_date)
        if self.institution_decision_date is not None:
            result["institutionDecisionDate"] = serialize_date(
                self.institution_decision_date
            )

        return result


@dataclass(frozen=True)
class PatentOwnerData(PartyData):
    """Party data for a patent owner."""

    pass


@dataclass(frozen=True)
class RegularPetitionerData:
    """Regular petitioner information.

    Attributes:
        counsel_name: Name of counsel.
        real_party_in_interest_name: Real party in interest name.
    """

    counsel_name: Optional[str] = None
    real_party_in_interest_name: Optional[str] = None

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], include_raw_data: bool = False
    ) -> "RegularPetitionerData":
        """Creates a RegularPetitionerData instance from a dictionary.

        Args:
            data: Dictionary containing petitioner data from API response.
            include_raw_data: Ignored for this model.

        Returns:
            RegularPetitionerData: An instance of RegularPetitionerData.
        """
        return cls(
            counsel_name=data.get("counselName"),
            real_party_in_interest_name=data.get("realPartyInInterestName"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the RegularPetitionerData instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary with camelCase keys and None values filtered.
        """
        result: Dict[str, Any] = {}

        if self.counsel_name is not None:
            result["counselName"] = self.counsel_name
        if self.real_party_in_interest_name is not None:
            result["realPartyInInterestName"] = self.real_party_in_interest_name

        return result


@dataclass(frozen=True)
class RespondentData(PartyData):
    """Respondent party data."""

    pass


@dataclass(frozen=True)
class DerivationPetitionerData(PartyData):
    """Derivation petitioner data."""

    pass


@dataclass(frozen=True)
class PTABTrialProceeding:
    """Individual PTAB trial proceeding record.

    Attributes:
        trial_number: Trial number (e.g., "IPR2023-00123").
        trial_record_identifier: UUID identifier for the trial record.
        last_modified_date_time: Last modification timestamp.
        trial_meta_data: Trial metadata.
        patent_owner_data: Patent owner information.
        regular_petitioner_data: Regular petitioner information.
        respondent_data: Respondent information.
        derivation_petitioner_data: Derivation petitioner information.
        raw_data: Raw JSON response data (if include_raw_data=True).
    """

    trial_number: Optional[str] = None
    # trial_record_identifier: Optional[str] = None
    last_modified_date_time: Optional[datetime] = None
    trial_meta_data: Optional[TrialMetaData] = None
    patent_owner_data: Optional[PatentOwnerData] = None
    regular_petitioner_data: Optional[RegularPetitionerData] = None
    respondent_data: Optional[RespondentData] = None
    derivation_petitioner_data: Optional[DerivationPetitionerData] = None
    raw_data: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], include_raw_data: bool = False
    ) -> "PTABTrialProceeding":
        """Creates a PTABTrialProceeding instance from a dictionary.

        Args:
            data: Dictionary containing trial proceeding data from API response.
            include_raw_data: Whether to include raw JSON data in the instance.

        Returns:
            PTABTrialProceeding: An instance of PTABTrialProceeding.
        """
        # Parse nested objects
        trial_meta = data.get("trialMetaData")
        trial_meta_data = TrialMetaData.from_dict(trial_meta) if trial_meta else None

        patent_owner = data.get("patentOwnerData")
        patent_owner_data = (
            PatentOwnerData.from_dict(patent_owner) if patent_owner else None
        )

        reg_petitioner = data.get("regularPetitionerData")
        regular_petitioner_data = (
            RegularPetitionerData.from_dict(reg_petitioner) if reg_petitioner else None
        )

        respondent = data.get("respondentData")
        respondent_data = RespondentData.from_dict(respondent) if respondent else None

        deriv_petitioner = data.get("derivationPetitionerData")
        derivation_petitioner_data = (
            DerivationPetitionerData.from_dict(deriv_petitioner)
            if deriv_petitioner
            else None
        )

        return cls(
            trial_number=data.get("trialNumber"),
            # trial_record_identifier=data.get("trialRecordIdentifier"),
            last_modified_date_time=parse_to_datetime_utc(
                data.get("lastModifiedDateTime")
            ),
            trial_meta_data=trial_meta_data,
            patent_owner_data=patent_owner_data,
            regular_petitioner_data=regular_petitioner_data,
            respondent_data=respondent_data,
            derivation_petitioner_data=derivation_petitioner_data,
            raw_data=data if include_raw_data else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the PTABTrialProceeding instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary with camelCase keys and None values filtered.
        """
        result: Dict[str, Any] = {}

        if self.trial_number is not None:
            result["trialNumber"] = self.trial_number
        # if self.trial_record_identifier is not None:
        #     result["trialRecordIdentifier"] = self.trial_record_identifier
        if self.last_modified_date_time is not None:
            result["lastModifiedDateTime"] = serialize_datetime_as_naive(
                self.last_modified_date_time
            )
        if self.trial_meta_data is not None:
            result["trialMetaData"] = self.trial_meta_data.to_dict()
        if self.patent_owner_data is not None:
            result["patentOwnerData"] = self.patent_owner_data.to_dict()
        if self.regular_petitioner_data is not None:
            result["regularPetitionerData"] = self.regular_petitioner_data.to_dict()
        if self.respondent_data is not None:
            result["respondentData"] = self.respondent_data.to_dict()
        if self.derivation_petitioner_data is not None:
            result["derivationPetitionerData"] = (
                self.derivation_petitioner_data.to_dict()
            )

        return result


@dataclass(frozen=True)
class PTABTrialProceedingResponse:
    """Response container for PTAB trial proceedings search.

    Attributes:
        count: Total number of matching results.
        request_identifier: UUID for the API request.
        patent_trial_proceeding_data_bag: List of trial proceedings.
        raw_data: Raw JSON response data (if include_raw_data=True).
    """

    count: int = 0
    request_identifier: Optional[str] = None
    patent_trial_proceeding_data_bag: List[PTABTrialProceeding] = field(
        default_factory=list
    )
    raw_data: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], include_raw_data: bool = False
    ) -> "PTABTrialProceedingResponse":
        """Creates a PTABTrialProceedingResponse instance from a dictionary.

        Args:
            data: Dictionary containing response data from API.
            include_raw_data: Whether to include raw JSON data in the instance.

        Returns:
            PTABTrialProceedingResponse: An instance of PTABTrialProceedingResponse.
        """
        proceedings_data = data.get("patentTrialProceedingDataBag", [])
        proceedings = [
            PTABTrialProceeding.from_dict(item, include_raw_data=include_raw_data)
            for item in proceedings_data
        ]

        return cls(
            count=data.get("count", 0),
            request_identifier=data.get("requestIdentifier"),
            patent_trial_proceeding_data_bag=proceedings,
            raw_data=data if include_raw_data else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the PTABTrialProceedingResponse instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary with camelCase keys and None values filtered.
        """
        result: Dict[str, Any] = {}

        if self.count is not None:
            result["count"] = self.count
        if self.request_identifier is not None:
            result["requestIdentifier"] = self.request_identifier
        if (
            self.patent_trial_proceeding_data_bag is not None
            and len(self.patent_trial_proceeding_data_bag) > 0
        ):
            result["patentTrialProceedingDataBag"] = [
                proceeding.to_dict()
                for proceeding in self.patent_trial_proceeding_data_bag
            ]

        return result


@dataclass(frozen=True)
class TrialDocumentData:
    """Metadata for a document in a PTAB trial.

    Attributes:
        document_category: Category of the document.
        document_filing_date: Filing date.
        document_identifier: Unique ID.
        document_name: Filename.
        document_number: Document number in the proceeding.
        document_size_quantity: Size in bytes.
        document_ocr_text: OCR text content.
        document_title_text: Title of the document.
        document_type_description_text: Description of document type.
        file_download_uri: URL to download the file.
        filing_party_category: Who filed (e.g., "Petitioner").
        mime_type_identifier: MIME type (e.g., "application/pdf").
        document_status: Public status.
    """

    # document_category: Optional[str] = None
    document_filing_date: Optional[date] = None
    document_identifier: Optional[str] = None
    document_name: Optional[str] = None
    document_number: Optional[str] = None
    document_size_quantity: Optional[int] = None
    document_ocr_text: Optional[str] = None
    document_title_text: Optional[str] = None
    document_type_description_text: Optional[str] = None
    file_download_uri: Optional[str] = None
    filing_party_category: Optional[str] = None
    # mime_type_identifier: Optional[str] = None
    # document_status: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TrialDocumentData":
        # Handle aliases
        file_download_uri = data.get("fileDownloadURI") or data.get("downloadURI")
        return cls(
            # document_category=data.get("documentCategory"),
            document_filing_date=parse_to_date(data.get("documentFilingDate")),
            document_identifier=data.get("documentIdentifier"),
            document_name=data.get("documentName"),
            document_number=data.get("documentNumber"),
            document_size_quantity=data.get("documentSizeQuantity"),
            document_ocr_text=data.get("documentOCRText"),
            document_title_text=data.get("documentTitleText"),
            document_type_description_text=data.get("documentTypeDescriptionText"),
            file_download_uri=file_download_uri,
            filing_party_category=data.get("filingPartyCategory"),
            # mime_type_identifier=data.get("mimeTypeIdentifier"),
            # document_status=data.get("documentStatus"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the TrialDocumentData instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary with camelCase keys and None values filtered.
        """
        result: Dict[str, Any] = {}

        # if self.document_category is not None:
        #     result["documentCategory"] = self.document_category
        if self.document_filing_date is not None:
            result["documentFilingDate"] = serialize_date(self.document_filing_date)
        if self.document_identifier is not None:
            result["documentIdentifier"] = self.document_identifier
        if self.document_name is not None:
            result["documentName"] = self.document_name
        if self.document_number is not None:
            result["documentNumber"] = self.document_number
        if self.document_size_quantity is not None:
            result["documentSizeQuantity"] = self.document_size_quantity
        if self.document_ocr_text is not None:
            result["documentOCRText"] = self.document_ocr_text  # Uppercase OCR
        if self.document_title_text is not None:
            result["documentTitleText"] = self.document_title_text
        if self.document_type_description_text is not None:
            result["documentTypeDescriptionText"] = self.document_type_description_text
        if self.file_download_uri is not None:
            result["fileDownloadURI"] = self.file_download_uri  # Uppercase URI
        if self.filing_party_category is not None:
            result["filingPartyCategory"] = self.filing_party_category
        # if self.mime_type_identifier is not None:
        #     result["mimeTypeIdentifier"] = self.mime_type_identifier
        # if self.document_status is not None:
        #     result["documentStatus"] = self.document_status

        return result


@dataclass(frozen=True)
class TrialDecisionData:
    """Metadata for a decision in a PTAB trial.

    Attributes:
        statute_and_rule_bag: List of applicable statutes and rules.
        decision_issue_date: Date issued.
        decision_type_category: Type of decision (e.g. "Final Written Decision").
        issue_type_bag: List of issues addressed.
        trial_outcome_category: Outcome (e.g., "Denied").
    """

    statute_and_rule_bag: List[str] = field(default_factory=list)
    decision_issue_date: Optional[date] = None
    decision_type_category: Optional[str] = None
    issue_type_bag: List[str] = field(default_factory=list)
    trial_outcome_category: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TrialDecisionData":
        return cls(
            statute_and_rule_bag=data.get("statuteAndRuleBag", []),
            decision_issue_date=parse_to_date(data.get("decisionIssueDate")),
            decision_type_category=data.get("decisionTypeCategory"),
            issue_type_bag=data.get("issueTypeBag", []),
            trial_outcome_category=data.get("trialOutcomeCategory"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the TrialDecisionData instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary with camelCase keys and None values filtered.
        """
        result: Dict[str, Any] = {}

        if self.statute_and_rule_bag is not None and len(self.statute_and_rule_bag) > 0:
            result["statuteAndRuleBag"] = self.statute_and_rule_bag
        if self.decision_issue_date is not None:
            result["decisionIssueDate"] = serialize_date(self.decision_issue_date)
        if self.decision_type_category is not None:
            result["decisionTypeCategory"] = self.decision_type_category
        if self.issue_type_bag is not None and len(self.issue_type_bag) > 0:
            result["issueTypeBag"] = self.issue_type_bag
        if self.trial_outcome_category is not None:
            result["trialOutcomeCategory"] = self.trial_outcome_category

        return result


@dataclass(frozen=True)
class PTABTrialDocument:
    """Record representing a Trial Document or Decision from the search APIs.

    This differs from PTABTrialProceeding by including documentData/decisionData
    and often omitting some proceeding-level details or structuring them differently.
    """

    trial_document_category: Optional[str] = None
    last_modified_date_time: Optional[datetime] = None
    trial_number: Optional[str] = None
    trial_type_code: Optional[str] = None
    trial_meta_data: Optional[TrialMetaData] = None
    patent_owner_data: Optional[PatentOwnerData] = None
    regular_petitioner_data: Optional[RegularPetitionerData] = None
    respondent_data: Optional[RespondentData] = None
    derivation_petitioner_data: Optional[DerivationPetitionerData] = None
    document_data: Optional[TrialDocumentData] = None
    decision_data: Optional[TrialDecisionData] = None
    raw_data: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], include_raw_data: bool = False
    ) -> "PTABTrialDocument":
        trial_meta = data.get("trialMetaData")
        patent_owner = data.get("patentOwnerData")
        reg_petitioner = data.get("regularPetitionerData")
        respondent = data.get("respondentData")
        deriv_petitioner = data.get("derivationPetitionerData")
        doc_data = data.get("documentData")
        dec_data = data.get("decisionData")

        return cls(
            trial_document_category=data.get("trialDocumentCategory"),
            last_modified_date_time=parse_to_datetime_utc(
                data.get("lastModifiedDateTime")
            ),
            trial_number=data.get("trialNumber"),
            trial_meta_data=(
                TrialMetaData.from_dict(trial_meta) if trial_meta else None
            ),
            patent_owner_data=(
                PatentOwnerData.from_dict(patent_owner) if patent_owner else None
            ),
            regular_petitioner_data=(
                RegularPetitionerData.from_dict(reg_petitioner)
                if reg_petitioner
                else None
            ),
            respondent_data=(
                RespondentData.from_dict(respondent) if respondent else None
            ),
            derivation_petitioner_data=(
                DerivationPetitionerData.from_dict(deriv_petitioner)
                if deriv_petitioner
                else None
            ),
            document_data=(TrialDocumentData.from_dict(doc_data) if doc_data else None),
            decision_data=(TrialDecisionData.from_dict(dec_data) if dec_data else None),
            raw_data=data if include_raw_data else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the PTABTrialDocument instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary with camelCase keys and None values filtered.
        """
        result: Dict[str, Any] = {}

        if self.trial_document_category is not None:
            result["trialDocumentCategory"] = self.trial_document_category
        if self.last_modified_date_time is not None:
            result["lastModifiedDateTime"] = serialize_datetime_as_naive(
                self.last_modified_date_time
            )
        if self.trial_number is not None:
            result["trialNumber"] = self.trial_number
        if self.trial_meta_data is not None:
            result["trialMetaData"] = self.trial_meta_data.to_dict()
        if self.patent_owner_data is not None:
            result["patentOwnerData"] = self.patent_owner_data.to_dict()
        if self.regular_petitioner_data is not None:
            result["regularPetitionerData"] = self.regular_petitioner_data.to_dict()
        if self.respondent_data is not None:
            result["respondentData"] = self.respondent_data.to_dict()
        if self.derivation_petitioner_data is not None:
            result["derivationPetitionerData"] = (
                self.derivation_petitioner_data.to_dict()
            )
        if self.document_data is not None:
            result["documentData"] = self.document_data.to_dict()
        if self.decision_data is not None:
            result["decisionData"] = self.decision_data.to_dict()

        return result


@dataclass(frozen=True)
class PTABTrialDocumentResponse:
    """Response container for PTAB trial documents/decisions search."""

    count: int = 0
    request_identifier: Optional[str] = None
    patent_trial_document_data_bag: List[PTABTrialDocument] = field(
        default_factory=list
    )
    raw_data: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], include_raw_data: bool = False
    ) -> "PTABTrialDocumentResponse":
        docs_data = data.get("patentTrialDocumentDataBag", [])
        docs = [
            PTABTrialDocument.from_dict(item, include_raw_data=include_raw_data)
            for item in docs_data
        ]
        return cls(
            count=data.get("count", 0),
            patent_trial_document_data_bag=docs,
            request_identifier=data.get("requestIdentifier"),
            raw_data=data if include_raw_data else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the PTABTrialDocumentResponse instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary with camelCase keys and None values filtered.
        """
        result: Dict[str, Any] = {}

        if self.count is not None:
            result["count"] = self.count
        if self.request_identifier is not None:
            result["requestIdentifier"] = self.request_identifier
        if (
            self.patent_trial_document_data_bag is not None
            and len(self.patent_trial_document_data_bag) > 0
        ):
            result["patentTrialDocumentDataBag"] = [
                doc.to_dict() for doc in self.patent_trial_document_data_bag
            ]

        return result


# ============================================================================
# APPEAL DECISIONS MODELS
# ============================================================================


@dataclass(frozen=True)
class AppealMetaData:
    """Appeal metadata.

    Attributes:
        appeal_filing_date: Date the appeal was filed.
        appeal_last_modified_date: Last modification date.
        application_type_category: Type of application.
        docket_notice_mailed_date: Date the docket notice was mailed.
        file_download_uri: URI to download ZIP of appeal documents.
    """

    appeal_filing_date: Optional[date] = None
    appeal_last_modified_date: Optional[date] = None
    appeal_last_modified_date_time: Optional[datetime] = None
    application_type_category: Optional[str] = None
    docket_notice_mailed_date: Optional[date] = None
    file_download_uri: Optional[str] = None

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], include_raw_data: bool = False
    ) -> "AppealMetaData":
        """Creates an AppealMetaData instance from a dictionary.

        Args:
            data: Dictionary containing appeal metadata from API response.
            include_raw_data: Ignored for this model.

        Returns:
            AppealMetaData: An instance of AppealMetaData.
        """
        # Handle aliases
        file_download_uri = data.get("fileDownloadURI") or data.get("downloadURI")
        return cls(
            appeal_filing_date=parse_to_date(data.get("appealFilingDate")),
            appeal_last_modified_date=parse_to_date(data.get("appealLastModifiedDate")),
            appeal_last_modified_date_time=parse_to_datetime_utc(
                data.get("appealLastModifiedDateTime")
            ),
            application_type_category=data.get("applicationTypeCategory"),
            docket_notice_mailed_date=parse_to_date(data.get("docketNoticeMailedDate")),
            file_download_uri=file_download_uri,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the AppealMetaData instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary with camelCase keys and None values filtered.
        """
        result: Dict[str, Any] = {}

        if self.appeal_filing_date is not None:
            result["appealFilingDate"] = serialize_date(self.appeal_filing_date)
        if self.appeal_last_modified_date is not None:
            result["appealLastModifiedDate"] = serialize_date(
                self.appeal_last_modified_date
            )
        if self.appeal_last_modified_date_time is not None:
            result["appealLastModifiedDateTime"] = serialize_datetime_as_naive(
                self.appeal_last_modified_date_time
            )
        if self.application_type_category is not None:
            result["applicationTypeCategory"] = self.application_type_category
        if self.docket_notice_mailed_date is not None:
            result["docketNoticeMailedDate"] = serialize_date(
                self.docket_notice_mailed_date
            )
        if self.file_download_uri is not None:
            result["fileDownloadURI"] = self.file_download_uri

        return result


@dataclass(frozen=True)
class AppellantData(PartyData):
    """Appellant party data."""

    pass


@dataclass(frozen=True)
class RequestorData:
    """Third party requestor information.

    Attributes:
        third_party_name: Name of the third party.
    """

    third_party_name: Optional[str] = None

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], include_raw_data: bool = False
    ) -> "RequestorData":
        """Creates a RequestorData instance from a dictionary.

        Args:
            data: Dictionary containing requestor data from API response.
            include_raw_data: Ignored for this model.

        Returns:
            RequestorData: An instance of RequestorData.
        """
        return cls(
            third_party_name=data.get("thirdPartyName"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the RequestorData instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary with camelCase keys and None values filtered.
        """
        result: Dict[str, Any] = {}
        for k, v in asdict(self).items():
            if v is not None:
                result[to_camel_case(k)] = v
        return result


@dataclass(frozen=True)
class AppealDocumentData:
    """Appeal document metadata.

    Attributes:
        document_filing_date: Date the document was filed.
        document_identifier: Unique identifier for the document.
        document_name: Name of the document.
        document_size_quantity: Size of the document in bytes.
        document_ocr_text: Full OCR text of the document.
        document_type_description_text: Description of the document type.
        file_download_uri: URI to download the document.
    """

    document_filing_date: Optional[date] = None
    document_identifier: Optional[str] = None
    document_name: Optional[str] = None
    document_size_quantity: Optional[int] = None
    document_ocr_text: Optional[str] = None
    document_type_description_text: Optional[str] = None
    file_download_uri: Optional[str] = None

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], include_raw_data: bool = False
    ) -> "AppealDocumentData":
        """Creates an AppealDocumentData instance from a dictionary.

        Args:
            data: Dictionary containing document data from API response.
            include_raw_data: Ignored for this model.

        Returns:
            AppealDocumentData: An instance of AppealDocumentData.
        """
        # Handle aliases
        file_download_uri = data.get("fileDownloadURI") or data.get("downloadURI")
        doc_type = data.get("documentTypeDescriptionText") or data.get(
            "documentTypeCategory"
        )

        return cls(
            document_filing_date=parse_to_date(data.get("documentFilingDate")),
            document_identifier=data.get("documentIdentifier"),
            document_name=data.get("documentName"),
            document_size_quantity=data.get("documentSizeQuantity"),
            document_ocr_text=data.get("documentOCRText"),
            document_type_description_text=doc_type,
            file_download_uri=file_download_uri,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the AppealDocumentData instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary with camelCase keys and None values filtered.
        """
        result: Dict[str, Any] = {}

        if self.document_filing_date is not None:
            result["documentFilingDate"] = serialize_date(self.document_filing_date)
        if self.document_identifier is not None:
            result["documentIdentifier"] = self.document_identifier
        if self.document_name is not None:
            result["documentName"] = self.document_name
        if self.document_size_quantity is not None:
            result["documentSizeQuantity"] = self.document_size_quantity
        if self.document_ocr_text is not None:
            result["documentOCRText"] = self.document_ocr_text
        if self.document_type_description_text is not None:
            result["documentTypeDescriptionText"] = self.document_type_description_text
        if self.file_download_uri is not None:
            result["fileDownloadURI"] = self.file_download_uri

        return result


@dataclass(frozen=True)
class DecisionData:
    """Appeal decision information.

    Attributes:
        appeal_outcome_category: Outcome of the appeal.
        statute_and_rule_bag: List of applicable statutes and rules.
        decision_issue_date: Date the decision was issued.
        decision_type_category: Type of decision.
        issue_type_bag: List of issue types.
    """

    appeal_outcome_category: Optional[str] = None
    statute_and_rule_bag: List[str] = field(default_factory=list)
    decision_issue_date: Optional[date] = None
    decision_type_category: Optional[str] = None
    issue_type_bag: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], include_raw_data: bool = False
    ) -> "DecisionData":
        """Creates a DecisionData instance from a dictionary.

        Args:
            data: Dictionary containing decision data from API response.
            include_raw_data: Ignored for this model.

        Returns:
            DecisionData: An instance of DecisionData.
        """
        return cls(
            appeal_outcome_category=data.get("appealOutcomeCategory"),
            statute_and_rule_bag=data.get("statuteAndRuleBag", []),
            decision_issue_date=parse_to_date(data.get("decisionIssueDate")),
            decision_type_category=data.get("decisionTypeCategory"),
            issue_type_bag=data.get("issueTypeBag", []),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the DecisionData instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary with camelCase keys and None values filtered.
        """
        result: Dict[str, Any] = {}
        for k, v in asdict(self).items():
            if v is not None:
                if isinstance(v, date):
                    result[to_camel_case(k)] = serialize_date(v)
                elif isinstance(v, list) and len(v) == 0:
                    # Skip empty lists
                    continue
                else:
                    result[to_camel_case(k)] = v
        return result


@dataclass(frozen=True)
class PTABAppealDecision:
    """Individual PTAB appeal decision record.

    Attributes:
        appeal_number: Appeal number.
        last_modified_date_time: Last modification timestamp.
        appeal_document_category: Document category.
        appeal_meta_data: Appeal metadata.
        appellant_data: Appellant information.
        requestor_data: Third party requestor information.
        document_data: Document metadata.
        decision_data: Decision information.
        raw_data: Raw JSON response data (if include_raw_data=True).
    """

    appeal_number: Optional[str] = None
    last_modified_date_time: Optional[datetime] = None
    appeal_document_category: Optional[str] = None
    appeal_meta_data: Optional[AppealMetaData] = None
    appellant_data: Optional[AppellantData] = None
    requestor_data: Optional[RequestorData] = None
    document_data: Optional[AppealDocumentData] = None
    decision_data: Optional[DecisionData] = None
    raw_data: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], include_raw_data: bool = False
    ) -> "PTABAppealDecision":
        """Creates a PTABAppealDecision instance from a dictionary.

        Args:
            data: Dictionary containing appeal decision data from API response.
            include_raw_data: Whether to include raw JSON data in the instance.

        Returns:
            PTABAppealDecision: An instance of PTABAppealDecision.
        """
        # Parse nested objects
        appeal_meta = data.get("appealMetaData")
        appeal_meta_data = (
            AppealMetaData.from_dict(appeal_meta) if appeal_meta else None
        )

        # Handle potential typo 'appelantData' vs 'appellantData'
        appellant = data.get("appellantData") or data.get("appelantData")
        appellant_data = AppellantData.from_dict(appellant) if appellant else None

        requestor = data.get("requestorData")
        requestor_data = RequestorData.from_dict(requestor) if requestor else None

        document = data.get("documentData")
        document_data = AppealDocumentData.from_dict(document) if document else None

        decision = data.get("decisionData")
        decision_data = DecisionData.from_dict(decision) if decision else None

        return cls(
            appeal_number=data.get("appealNumber"),
            last_modified_date_time=parse_to_datetime_utc(
                data.get("lastModifiedDateTime")
            ),
            appeal_document_category=data.get("appealDocumentCategory"),
            appeal_meta_data=appeal_meta_data,
            appellant_data=appellant_data,
            requestor_data=requestor_data,
            document_data=document_data,
            decision_data=decision_data,
            raw_data=data if include_raw_data else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the PTABAppealDecision instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary with camelCase keys and None values filtered.
        """
        result: Dict[str, Any] = {}

        # Manually process each field to preserve nested objects
        if self.appeal_number is not None:
            result["appealNumber"] = self.appeal_number
        if self.last_modified_date_time is not None:
            result["lastModifiedDateTime"] = serialize_datetime_as_naive(
                self.last_modified_date_time
            )
        if self.appeal_document_category is not None:
            result["appealDocumentCategory"] = self.appeal_document_category
        if self.appeal_meta_data is not None:
            result["appealMetaData"] = self.appeal_meta_data.to_dict()
        if self.appellant_data is not None:
            result["appellantData"] = self.appellant_data.to_dict()
        if self.requestor_data is not None:
            result["requestorData"] = self.requestor_data.to_dict()
        if self.document_data is not None:
            result["documentData"] = self.document_data.to_dict()
        if self.decision_data is not None:
            result["decisionData"] = self.decision_data.to_dict()

        return result


@dataclass(frozen=True)
class PTABAppealResponse:
    """Response container for PTAB appeals search.

    Attributes:
        count: Total number of matching results.
        request_identifier: UUID for the API request.
        patent_appeal_data_bag: List of appeal decisions.
        raw_data: Raw JSON response data (if include_raw_data=True).
    """

    count: int = 0
    request_identifier: Optional[str] = None
    patent_appeal_data_bag: List[PTABAppealDecision] = field(default_factory=list)
    raw_data: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], include_raw_data: bool = False
    ) -> "PTABAppealResponse":
        """Creates a PTABAppealResponse instance from a dictionary.

        Args:
            data: Dictionary containing response data from API.
            include_raw_data: Whether to include raw JSON data in the instance.

        Returns:
            PTABAppealResponse: An instance of PTABAppealResponse.
        """
        appeals_data = data.get("patentAppealDataBag", [])
        appeals = [
            PTABAppealDecision.from_dict(item, include_raw_data=include_raw_data)
            for item in appeals_data
        ]

        return cls(
            count=data.get("count", 0),
            request_identifier=data.get("requestIdentifier"),
            patent_appeal_data_bag=appeals,
            raw_data=data if include_raw_data else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the PTABAppealResponse instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary with camelCase keys and None values filtered.
        """
        result: Dict[str, Any] = {}

        # Manually process each field
        if self.count is not None:
            result["count"] = self.count
        if self.request_identifier is not None:
            result["requestIdentifier"] = self.request_identifier
        if (
            self.patent_appeal_data_bag is not None
            and len(self.patent_appeal_data_bag) > 0
        ):
            result["patentAppealDataBag"] = [
                decision.to_dict() for decision in self.patent_appeal_data_bag
            ]

        return result


# ============================================================================
# INTERFERENCE DECISIONS MODELS
# ============================================================================


@dataclass(frozen=True)
class InterferenceMetaData:
    """Interference metadata.

    Attributes:
        interference_style_name: Style name of the interference.
        interference_last_modified_date: Last modification date.
        interference_last_modified_date_time: Last modification datetime.
        declaration_date: Declaration date.
        file_download_uri: URI to download ZIP of interference documents.
    """

    interference_style_name: Optional[str] = None
    interference_last_modified_date: Optional[date] = None
    interference_last_modified_date_time: Optional[datetime] = None
    declaration_date: Optional[date] = None
    file_download_uri: Optional[str] = None

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], include_raw_data: bool = False
    ) -> "InterferenceMetaData":
        """Creates an InterferenceMetaData instance from a dictionary.

        Args:
            data: Dictionary containing interference metadata from API response.
            include_raw_data: Ignored for this model.

        Returns:
            InterferenceMetaData: An instance of InterferenceMetaData.
        """
        # Handle aliases
        file_download_uri = data.get("fileDownloadURI") or data.get("downloadURI")
        return cls(
            interference_style_name=data.get("interferenceStyleName"),
            interference_last_modified_date=parse_to_date(
                data.get("interferenceLastModifiedDate")
            ),
            interference_last_modified_date_time=parse_to_datetime_utc(
                data.get("interferenceLastModifiedDateTime")
            ),
            declaration_date=parse_to_date(data.get("declarationDate")),
            file_download_uri=file_download_uri,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the InterferenceMetaData instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary with camelCase keys and None values filtered.
        """
        result: Dict[str, Any] = {}

        if self.interference_style_name is not None:
            result["interferenceStyleName"] = self.interference_style_name
        if self.interference_last_modified_date is not None:
            result["interferenceLastModifiedDate"] = serialize_date(
                self.interference_last_modified_date
            )
        if self.interference_last_modified_date_time is not None:
            result["interferenceLastModifiedDateTime"] = serialize_datetime_as_naive(
                self.interference_last_modified_date_time
            )
        if self.declaration_date is not None:
            result["declarationDate"] = serialize_date(self.declaration_date)
        if self.file_download_uri is not None:
            result["fileDownloadURI"] = self.file_download_uri

        return result


@dataclass(frozen=True)
class SeniorPartyData(PartyData):
    """Senior party information in an interference."""

    pass


@dataclass(frozen=True)
class JuniorPartyData(PartyData):
    """Junior party information in an interference."""

    pass


@dataclass(frozen=True)
class AdditionalPartyData:
    """Additional party information in an interference.

    Attributes:
        application_number_text: Application number.
        inventor_name: Name of inventor.
        patent_number: Patent number.
        additional_party_name: Name of additional party.
    """

    application_number_text: Optional[str] = None
    inventor_name: Optional[str] = None
    patent_number: Optional[str] = None
    additional_party_name: Optional[str] = None

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], include_raw_data: bool = False
    ) -> "AdditionalPartyData":
        """Creates an AdditionalPartyData instance from a dictionary.

        Args:
            data: Dictionary containing additional party data from API response.
            include_raw_data: Ignored for this model.

        Returns:
            AdditionalPartyData: An instance of AdditionalPartyData.
        """
        return cls(
            application_number_text=data.get("applicationNumberText"),
            inventor_name=data.get("inventorName"),
            patent_number=data.get("patentNumber"),
            additional_party_name=data.get("additionalPartyName"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the AdditionalPartyData instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary with camelCase keys and None values filtered.
        """
        result: Dict[str, Any] = {}

        if self.application_number_text is not None:
            result["applicationNumberText"] = self.application_number_text
        if self.inventor_name is not None:
            result["inventorName"] = self.inventor_name
        if self.patent_number is not None:
            result["patentNumber"] = self.patent_number
        if self.additional_party_name is not None:
            result["additionalPartyName"] = self.additional_party_name

        return result


@dataclass(frozen=True)
class InterferenceDocumentData:
    """Interference document metadata.

    Attributes:
        document_identifier: Unique identifier for the document.
        document_name: Name of the document.
        document_size_quantity: Size of the document in bytes.
        document_ocr_text: Full OCR text of the document.
        document_title_text: Title of the document.
        interference_outcome_category: Outcome of the interference.
        document_filing_date: Date the document was filed.
        decision_issue_date: Date the decision was issued.
        decision_type_category: Type of decision.
        file_download_uri: URI to download the document.
        statute_and_rule_bag: List of applicable statutes and rules.
        issue_type_bag: List of issues addressed.
    """

    document_identifier: Optional[str] = None
    document_name: Optional[str] = None
    document_size_quantity: Optional[int] = None
    document_ocr_text: Optional[str] = None
    document_title_text: Optional[str] = None
    interference_outcome_category: Optional[str] = None
    document_filing_date: Optional[date] = None
    decision_issue_date: Optional[date] = None
    decision_type_category: Optional[str] = None
    file_download_uri: Optional[str] = None
    statute_and_rule_bag: List[str] = field(default_factory=list)
    issue_type_bag: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], include_raw_data: bool = False
    ) -> "InterferenceDocumentData":
        """Creates an InterferenceDocumentData instance from a dictionary.

        Args:
            data: Dictionary containing document data from API response.
            include_raw_data: Ignored for this model.

        Returns:
            InterferenceDocumentData: An instance of InterferenceDocumentData.
        """
        # Handle aliases
        file_download_uri = data.get("fileDownloadURI") or data.get("downloadURI")

        return cls(
            document_identifier=data.get("documentIdentifier"),
            document_name=data.get("documentName"),
            document_size_quantity=data.get("documentSizeQuantity"),
            document_ocr_text=data.get("documentOCRText"),
            document_title_text=data.get("documentTitleText"),
            interference_outcome_category=data.get("interferenceOutcomeCategory"),
            document_filing_date=parse_to_date(data.get("documentFilingDate")),
            decision_issue_date=parse_to_date(data.get("decisionIssueDate")),
            decision_type_category=data.get("decisionTypeCategory"),
            file_download_uri=file_download_uri,
            statute_and_rule_bag=data.get("statuteAndRuleBag", []),
            issue_type_bag=data.get("issueTypeBag", []),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the InterferenceDocumentData instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary with camelCase keys and None values filtered.
        """
        result: Dict[str, Any] = {}

        if self.document_identifier is not None:
            result["documentIdentifier"] = self.document_identifier
        if self.document_name is not None:
            result["documentName"] = self.document_name
        if self.document_size_quantity is not None:
            result["documentSizeQuantity"] = self.document_size_quantity
        if self.document_ocr_text is not None:
            result["documentOCRText"] = self.document_ocr_text
        if self.document_title_text is not None:
            result["documentTitleText"] = self.document_title_text
        if self.interference_outcome_category is not None:
            result["interferenceOutcomeCategory"] = self.interference_outcome_category
        if self.document_filing_date is not None:
            result["documentFilingDate"] = serialize_date(self.document_filing_date)
        if self.decision_issue_date is not None:
            result["decisionIssueDate"] = serialize_date(self.decision_issue_date)
        if self.decision_type_category is not None:
            result["decisionTypeCategory"] = self.decision_type_category
        if self.file_download_uri is not None:
            result["fileDownloadURI"] = self.file_download_uri
        if self.statute_and_rule_bag is not None and len(self.statute_and_rule_bag) > 0:
            result["statuteAndRuleBag"] = self.statute_and_rule_bag
        if self.issue_type_bag is not None and len(self.issue_type_bag) > 0:
            result["issueTypeBag"] = self.issue_type_bag

        return result


@dataclass(frozen=True)
class PTABInterferenceDecision:
    """Individual PTAB interference decision record.

    Attributes:
        interference_number: Interference number.
        last_modified_date_time: Last modification timestamp.
        interference_meta_data: Interference metadata.
        senior_party_data: Senior party information.
        junior_party_data: Junior party information.
        additional_party_data_bag: List of additional parties.
        document_data: Document metadata.
        raw_data: Raw JSON response data (if include_raw_data=True).
    """

    interference_number: Optional[str] = None
    last_modified_date_time: Optional[datetime] = None
    interference_meta_data: Optional[InterferenceMetaData] = None
    senior_party_data: Optional[SeniorPartyData] = None
    junior_party_data: Optional[JuniorPartyData] = None
    additional_party_data_bag: List[AdditionalPartyData] = field(default_factory=list)
    document_data: Optional[InterferenceDocumentData] = None
    raw_data: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], include_raw_data: bool = False
    ) -> "PTABInterferenceDecision":
        """Creates a PTABInterferenceDecision instance from a dictionary.

        Args:
            data: Dictionary containing interference decision data from API response.
            include_raw_data: Whether to include raw JSON data in the instance.

        Returns:
            PTABInterferenceDecision: An instance of PTABInterferenceDecision.
        """
        # Parse nested objects
        interference_meta = data.get("interferenceMetaData")
        interference_meta_data = (
            InterferenceMetaData.from_dict(interference_meta)
            if interference_meta
            else None
        )

        senior_party = data.get("seniorPartyData")
        senior_party_data = (
            SeniorPartyData.from_dict(senior_party) if senior_party else None
        )

        junior_party = data.get("juniorPartyData")
        junior_party_data = (
            JuniorPartyData.from_dict(junior_party) if junior_party else None
        )

        additional_parties_data = data.get("additionalPartyDataBag", [])
        additional_party_data_bag = [
            AdditionalPartyData.from_dict(item) for item in additional_parties_data
        ]

        # Handle alias: documentData vs decisionDocumentData
        document = data.get("documentData") or data.get("decisionDocumentData")
        document_data = (
            InterferenceDocumentData.from_dict(document) if document else None
        )

        return cls(
            interference_number=data.get("interferenceNumber"),
            last_modified_date_time=parse_to_datetime_utc(
                data.get("lastModifiedDateTime")
            ),
            interference_meta_data=interference_meta_data,
            senior_party_data=senior_party_data,
            junior_party_data=junior_party_data,
            additional_party_data_bag=additional_party_data_bag,
            document_data=document_data,
            raw_data=data if include_raw_data else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the PTABInterferenceDecision instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary with camelCase keys and None values filtered.
        """
        result: Dict[str, Any] = {}

        # Manually process each field to preserve nested objects
        if self.interference_number is not None:
            result["interferenceNumber"] = self.interference_number
        if self.last_modified_date_time is not None:
            result["lastModifiedDateTime"] = serialize_datetime_as_naive(
                self.last_modified_date_time
            )
        if self.interference_meta_data is not None:
            result["interferenceMetaData"] = self.interference_meta_data.to_dict()
        if self.senior_party_data is not None:
            result["seniorPartyData"] = self.senior_party_data.to_dict()
        if self.junior_party_data is not None:
            result["juniorPartyData"] = self.junior_party_data.to_dict()
        if (
            self.additional_party_data_bag is not None
            and len(self.additional_party_data_bag) > 0
        ):
            result["additionalPartyDataBag"] = [
                party.to_dict() for party in self.additional_party_data_bag
            ]
        if self.document_data is not None:
            result["documentData"] = self.document_data.to_dict()

        return result


@dataclass(frozen=True)
class PTABInterferenceResponse:
    """Response container for PTAB interferences search.

    Attributes:
        count: Total number of matching results.
        request_identifier: UUID for the API request.
        patent_interference_data_bag: List of interference decisions.
        raw_data: Raw JSON response data (if include_raw_data=True).
    """

    count: int = 0
    request_identifier: Optional[str] = None
    patent_interference_data_bag: List[PTABInterferenceDecision] = field(
        default_factory=list
    )
    raw_data: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], include_raw_data: bool = False
    ) -> "PTABInterferenceResponse":
        """Creates a PTABInterferenceResponse instance from a dictionary.

        Args:
            data: Dictionary containing response data from API.
            include_raw_data: Whether to include raw JSON data in the instance.

        Returns:
            PTABInterferenceResponse: An instance of PTABInterferenceResponse.
        """
        interferences_data = data.get("patentInterferenceDataBag", [])
        interferences = [
            PTABInterferenceDecision.from_dict(item, include_raw_data=include_raw_data)
            for item in interferences_data
        ]

        return cls(
            count=data.get("count", 0),
            request_identifier=data.get("requestIdentifier"),
            patent_interference_data_bag=interferences,
            raw_data=data if include_raw_data else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the PTABInterferenceResponse instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary with camelCase keys and None values filtered.
        """
        result: Dict[str, Any] = {}

        # Manually process each field
        if self.count is not None:
            result["count"] = self.count
        if self.request_identifier is not None:
            result["requestIdentifier"] = self.request_identifier
        if (
            self.patent_interference_data_bag is not None
            and len(self.patent_interference_data_bag) > 0
        ):
            result["patentInterferenceDataBag"] = [
                decision.to_dict() for decision in self.patent_interference_data_bag
            ]

        return result


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Trial Proceedings Models
    "TrialMetaData",
    "PatentOwnerData",
    "RegularPetitionerData",
    "RespondentData",
    "DerivationPetitionerData",
    "PTABTrialProceeding",
    "PTABTrialProceedingResponse",
    # Trial Documents/Decisions Models
    "TrialDocumentData",
    "TrialDecisionData",
    "PTABTrialDocument",
    "PTABTrialDocumentResponse",
    # Appeal Decisions Models
    "AppealMetaData",
    "AppellantData",
    "RequestorData",
    "AppealDocumentData",
    "DecisionData",
    "PTABAppealDecision",
    "PTABAppealResponse",
    # Interference Decisions Models
    "InterferenceMetaData",
    "SeniorPartyData",
    "JuniorPartyData",
    "AdditionalPartyData",
    "InterferenceDocumentData",
    "PTABInterferenceDecision",
    "PTABInterferenceResponse",
]
