"""
models.ptab - Data models for USPTO PTAB (Patent Trial and Appeal Board) APIs

This module provides data models, primarily using frozen dataclasses, for
representing responses from the USPTO PTAB APIs. These models cover:
- Patent trial proceedings (IPR, PGR, CBM, DER)
- Appeal decisions
- Interference decisions
"""

import json
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Dict, List, Optional

# Import parsing utilities from models utils module
from pyUSPTO.models.utils import (
    parse_to_date,
    parse_to_datetime_utc,
    serialize_date,
    serialize_datetime_as_iso,
)

# ============================================================================
# TRIAL PROCEEDINGS MODELS
# ============================================================================


@dataclass(frozen=True)
class TrialMetaData:
    """Trial metadata including status, dates, and download URI.

    Attributes:
        petition_filing_date: Date the petition was filed.
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
        return cls(
            petition_filing_date=parse_to_date(data.get("petitionFilingDate")),
            trial_last_modified_date_time=parse_to_datetime_utc(
                data.get("trialLastModifiedDateTime")
            ),
            trial_last_modified_date=parse_to_date(data.get("trialLastModifiedDate")),
            trial_status_category=data.get("trialStatusCategory"),
            trial_type_code=data.get("trialTypeCode"),
            file_download_uri=data.get("fileDownloadURI"),
            termination_date=parse_to_date(data.get("terminationDate")),
            latest_decision_date=parse_to_date(data.get("latestDecisionDate")),
            institution_decision_date=parse_to_date(
                data.get("institutionDecisionDate")
            ),
        )


@dataclass(frozen=True)
class PatentOwnerData:
    """Patent owner/respondent information.

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
    """

    application_number_text: Optional[str] = None
    counsel_name: Optional[str] = None
    grant_date: Optional[date] = None
    group_art_unit_number: Optional[str] = None
    inventor_name: Optional[str] = None
    patent_number: Optional[str] = None
    technology_center_number: Optional[str] = None
    real_party_in_interest_name: Optional[str] = None
    patent_owner_name: Optional[str] = None

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], include_raw_data: bool = False
    ) -> "PatentOwnerData":
        """Creates a PatentOwnerData instance from a dictionary.

        Args:
            data: Dictionary containing patent owner data from API response.
            include_raw_data: Ignored for this model.

        Returns:
            PatentOwnerData: An instance of PatentOwnerData.
        """
        return cls(
            application_number_text=data.get("applicationNumberText"),
            counsel_name=data.get("counselName"),
            grant_date=parse_to_date(data.get("grantDate")),
            group_art_unit_number=data.get("groupArtUnitNumber"),
            inventor_name=data.get("inventorName"),
            patent_number=data.get("patentNumber"),
            technology_center_number=data.get("technologyCenterNumber"),
            real_party_in_interest_name=data.get("realPartyInInterestName"),
            patent_owner_name=data.get("patentOwnerName"),
        )


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


@dataclass(frozen=True)
class RespondentData:
    """Respondent information (same structure as PatentOwnerData).

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
    """

    application_number_text: Optional[str] = None
    counsel_name: Optional[str] = None
    grant_date: Optional[date] = None
    group_art_unit_number: Optional[str] = None
    inventor_name: Optional[str] = None
    patent_number: Optional[str] = None
    technology_center_number: Optional[str] = None
    real_party_in_interest_name: Optional[str] = None
    patent_owner_name: Optional[str] = None

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], include_raw_data: bool = False
    ) -> "RespondentData":
        """Creates a RespondentData instance from a dictionary.

        Args:
            data: Dictionary containing respondent data from API response.
            include_raw_data: Ignored for this model.

        Returns:
            RespondentData: An instance of RespondentData.
        """
        return cls(
            application_number_text=data.get("applicationNumberText"),
            counsel_name=data.get("counselName"),
            grant_date=parse_to_date(data.get("grantDate")),
            group_art_unit_number=data.get("groupArtUnitNumber"),
            inventor_name=data.get("inventorName"),
            patent_number=data.get("patentNumber"),
            technology_center_number=data.get("technologyCenterNumber"),
            real_party_in_interest_name=data.get("realPartyInInterestName"),
            patent_owner_name=data.get("patentOwnerName"),
        )


@dataclass(frozen=True)
class DerivationPetitionerData:
    """Derivation petitioner information.

    Attributes:
        counsel_name: Name of counsel.
        grant_date: Patent grant date.
        group_art_unit_number: Art unit number.
        inventor_name: Name of inventor.
        patent_number: Patent number.
        technology_center_number: Technology center number.
        real_party_in_interest_name: Real party in interest name.
        patent_owner_name: Patent owner name.
    """

    counsel_name: Optional[str] = None
    grant_date: Optional[date] = None
    group_art_unit_number: Optional[str] = None
    inventor_name: Optional[str] = None
    patent_number: Optional[str] = None
    technology_center_number: Optional[str] = None
    real_party_in_interest_name: Optional[str] = None
    patent_owner_name: Optional[str] = None

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], include_raw_data: bool = False
    ) -> "DerivationPetitionerData":
        """Creates a DerivationPetitionerData instance from a dictionary.

        Args:
            data: Dictionary containing derivation petitioner data from API response.
            include_raw_data: Ignored for this model.

        Returns:
            DerivationPetitionerData: An instance of DerivationPetitionerData.
        """
        return cls(
            counsel_name=data.get("counselName"),
            grant_date=parse_to_date(data.get("grantDate")),
            group_art_unit_number=data.get("groupArtUnitNumber"),
            inventor_name=data.get("inventorName"),
            patent_number=data.get("patentNumber"),
            technology_center_number=data.get("technologyCenterNumber"),
            real_party_in_interest_name=data.get("realPartyInInterestName"),
            patent_owner_name=data.get("patentOwnerName"),
        )


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
    trial_record_identifier: Optional[str] = None
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
            trial_record_identifier=data.get("trialRecordIdentifier"),
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


@dataclass(frozen=True)
class PTABTrialProceedingResponse:
    """Response container for PTAB trial proceedings search.

    Attributes:
        count: Total number of matching results.
        request_identifier: UUID for the API request.
        patent_trial_proceeding_data_bag: List of trial proceedings.
        raw_data: Raw JSON response data (if include_raw_data=True).
    """

    count: Optional[int] = None
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
            count=data.get("count"),
            request_identifier=data.get("requestIdentifier"),
            patent_trial_proceeding_data_bag=proceedings,
            raw_data=data if include_raw_data else None,
        )


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
        return cls(
            appeal_filing_date=parse_to_date(data.get("appealFilingDate")),
            appeal_last_modified_date=parse_to_date(data.get("appealLastModifiedDate")),
            application_type_category=data.get("applicationTypeCategory"),
            docket_notice_mailed_date=parse_to_date(data.get("docketNoticeMailedDate")),
            file_download_uri=data.get("fileDownloadURI"),
        )


@dataclass(frozen=True)
class AppellantData:
    """Appellant information.

    Attributes:
        application_number_text: Application number.
        counsel_name: Name of counsel.
        group_art_unit_number: Art unit number.
        inventor_name: Name of inventor.
        real_party_in_interest_name: Real party in interest name.
        patent_owner_name: Patent owner name.
        publication_date: Publication date.
        publication_number: Publication number.
        technology_center_number: Technology center number.
    """

    application_number_text: Optional[str] = None
    counsel_name: Optional[str] = None
    group_art_unit_number: Optional[str] = None
    inventor_name: Optional[str] = None
    real_party_in_interest_name: Optional[str] = None
    patent_owner_name: Optional[str] = None
    publication_date: Optional[date] = None
    publication_number: Optional[str] = None
    technology_center_number: Optional[str] = None

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], include_raw_data: bool = False
    ) -> "AppellantData":
        """Creates an AppellantData instance from a dictionary.

        Args:
            data: Dictionary containing appellant data from API response.
            include_raw_data: Ignored for this model.

        Returns:
            AppellantData: An instance of AppellantData.
        """
        return cls(
            application_number_text=data.get("applicationNumberText"),
            counsel_name=data.get("counselName"),
            group_art_unit_number=data.get("groupArtUnitNumber"),
            inventor_name=data.get("inventorName"),
            real_party_in_interest_name=data.get("realPartyInInterestName"),
            patent_owner_name=data.get("patentOwnerName"),
            publication_date=parse_to_date(data.get("publicationDate")),
            publication_number=data.get("publicationNumber"),
            technology_center_number=data.get("technologyCenterNumber"),
        )


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
        return cls(
            document_filing_date=parse_to_date(data.get("documentFilingDate")),
            document_identifier=data.get("documentIdentifier"),
            document_name=data.get("documentName"),
            document_size_quantity=data.get("documentSizeQuantity"),
            document_ocr_text=data.get("documentOCRText"),
            document_type_description_text=data.get("documentTypeDescriptionText"),
            file_download_uri=data.get("fileDownloadURI"),
        )


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

        appellant = data.get("appellantData")
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


@dataclass(frozen=True)
class PTABAppealResponse:
    """Response container for PTAB appeals search.

    Attributes:
        count: Total number of matching results.
        request_identifier: UUID for the API request.
        patent_appeal_data_bag: List of appeal decisions.
        raw_data: Raw JSON response data (if include_raw_data=True).
    """

    count: Optional[int] = None
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
            count=data.get("count"),
            request_identifier=data.get("requestIdentifier"),
            patent_appeal_data_bag=appeals,
            raw_data=data if include_raw_data else None,
        )


# ============================================================================
# INTERFERENCE DECISIONS MODELS
# ============================================================================


@dataclass(frozen=True)
class InterferenceMetaData:
    """Interference metadata.

    Attributes:
        interference_style_name: Style name of the interference.
        interference_last_modified_date: Last modification date.
        file_download_uri: URI to download ZIP of interference documents.
    """

    interference_style_name: Optional[str] = None
    interference_last_modified_date: Optional[date] = None
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
        return cls(
            interference_style_name=data.get("interferenceStyleName"),
            interference_last_modified_date=parse_to_date(
                data.get("interferenceLastModifiedDate")
            ),
            file_download_uri=data.get("fileDownloadURI"),
        )


@dataclass(frozen=True)
class SeniorPartyData:
    """Senior party information in an interference.

    Attributes:
        application_number_text: Application number.
        counsel_name: Name of counsel.
        grant_date: Patent grant date.
        group_art_unit_number: Art unit number.
        real_party_in_interest_name: Real party in interest name.
        patent_number: Patent number.
        patent_owner_name: Patent owner name.
        publication_date: Publication date.
        publication_number: Publication number.
        technology_center_number: Technology center number.
    """

    application_number_text: Optional[str] = None
    counsel_name: Optional[str] = None
    grant_date: Optional[date] = None
    group_art_unit_number: Optional[str] = None
    real_party_in_interest_name: Optional[str] = None
    patent_number: Optional[str] = None
    patent_owner_name: Optional[str] = None
    publication_date: Optional[date] = None
    publication_number: Optional[str] = None
    technology_center_number: Optional[str] = None

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], include_raw_data: bool = False
    ) -> "SeniorPartyData":
        """Creates a SeniorPartyData instance from a dictionary.

        Args:
            data: Dictionary containing senior party data from API response.
            include_raw_data: Ignored for this model.

        Returns:
            SeniorPartyData: An instance of SeniorPartyData.
        """
        return cls(
            application_number_text=data.get("applicationNumberText"),
            counsel_name=data.get("counselName"),
            grant_date=parse_to_date(data.get("grantDate")),
            group_art_unit_number=data.get("groupArtUnitNumber"),
            real_party_in_interest_name=data.get("realPartyInInterestName"),
            patent_number=data.get("patentNumber"),
            patent_owner_name=data.get("patentOwnerName"),
            publication_date=parse_to_date(data.get("publicationDate")),
            publication_number=data.get("publicationNumber"),
            technology_center_number=data.get("technologyCenterNumber"),
        )


@dataclass(frozen=True)
class JuniorPartyData:
    """Junior party information in an interference.

    Attributes:
        publication_number: Publication number.
        counsel_name: Name of counsel.
        group_art_unit_number: Art unit number.
        inventor_name: Name of inventor.
        patent_owner_name: Patent owner name.
        publication_date: Publication date.
        real_party_in_interest_name: Real party in interest name.
        technology_center_number: Technology center number.
    """

    publication_number: Optional[str] = None
    counsel_name: Optional[str] = None
    group_art_unit_number: Optional[str] = None
    inventor_name: Optional[str] = None
    patent_owner_name: Optional[str] = None
    publication_date: Optional[date] = None
    real_party_in_interest_name: Optional[str] = None
    technology_center_number: Optional[str] = None

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], include_raw_data: bool = False
    ) -> "JuniorPartyData":
        """Creates a JuniorPartyData instance from a dictionary.

        Args:
            data: Dictionary containing junior party data from API response.
            include_raw_data: Ignored for this model.

        Returns:
            JuniorPartyData: An instance of JuniorPartyData.
        """
        return cls(
            publication_number=data.get("publicationNumber"),
            counsel_name=data.get("counselName"),
            group_art_unit_number=data.get("groupArtUnitNumber"),
            inventor_name=data.get("inventorName"),
            patent_owner_name=data.get("patentOwnerName"),
            publication_date=parse_to_date(data.get("publicationDate")),
            real_party_in_interest_name=data.get("realPartyInInterestName"),
            technology_center_number=data.get("technologyCenterNumber"),
        )


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
        decision_issue_date: Date the decision was issued.
        decision_type_category: Type of decision.
        file_download_uri: URI to download the document.
    """

    document_identifier: Optional[str] = None
    document_name: Optional[str] = None
    document_size_quantity: Optional[int] = None
    document_ocr_text: Optional[str] = None
    document_title_text: Optional[str] = None
    interference_outcome_category: Optional[str] = None
    decision_issue_date: Optional[date] = None
    decision_type_category: Optional[str] = None
    file_download_uri: Optional[str] = None

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
        return cls(
            document_identifier=data.get("documentIdentifier"),
            document_name=data.get("documentName"),
            document_size_quantity=data.get("documentSizeQuantity"),
            document_ocr_text=data.get("documentOCRText"),
            document_title_text=data.get("documentTitleText"),
            interference_outcome_category=data.get("interferenceOutcomeCategory"),
            decision_issue_date=parse_to_date(data.get("decisionIssueDate")),
            decision_type_category=data.get("decisionTypeCategory"),
            file_download_uri=data.get("fileDownloadURI"),
        )


@dataclass(frozen=True)
class PTABInterferenceDecision:
    """Individual PTAB interference decision record.

    Attributes:
        interference_number: Interference number.
        last_modified_date_time: Last modification timestamp.
        last_ingestion_date_time: Last ingestion timestamp (alternative field).
        interference_meta_data: Interference metadata.
        senior_party_data: Senior party information.
        junior_party_data: Junior party information.
        additional_party_data_bag: List of additional parties.
        document_data: Document metadata.
        raw_data: Raw JSON response data (if include_raw_data=True).
    """

    interference_number: Optional[str] = None
    last_modified_date_time: Optional[datetime] = None
    last_ingestion_date_time: Optional[datetime] = None
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

        document = data.get("documentData")
        document_data = (
            InterferenceDocumentData.from_dict(document) if document else None
        )

        return cls(
            interference_number=data.get("interferenceNumber"),
            last_modified_date_time=parse_to_datetime_utc(
                data.get("lastModifiedDateTime")
            ),
            last_ingestion_date_time=parse_to_datetime_utc(
                data.get("lastIngestionDateTime")
            ),
            interference_meta_data=interference_meta_data,
            senior_party_data=senior_party_data,
            junior_party_data=junior_party_data,
            additional_party_data_bag=additional_party_data_bag,
            document_data=document_data,
            raw_data=data if include_raw_data else None,
        )


@dataclass(frozen=True)
class PTABInterferenceResponse:
    """Response container for PTAB interferences search.

    Attributes:
        count: Total number of matching results.
        request_identifier: UUID for the API request.
        patent_interference_data_bag: List of interference decisions.
        raw_data: Raw JSON response data (if include_raw_data=True).
    """

    count: Optional[int] = None
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
            count=data.get("count"),
            request_identifier=data.get("requestIdentifier"),
            patent_interference_data_bag=interferences,
            raw_data=data if include_raw_data else None,
        )


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
