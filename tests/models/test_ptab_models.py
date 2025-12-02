"""
Tests for PTAB models.

This module contains unit tests for the PTAB model classes with full coverage.
"""

from datetime import date, datetime, timezone
from typing import Any, Dict

import pytest

from pyUSPTO.models.ptab import (
    # Base and shared models
    PartyData,
    # Trial Proceedings Models
    TrialMetaData,
    PatentOwnerData,
    RegularPetitionerData,
    RespondentData,
    DerivationPetitionerData,
    PTABTrialProceeding,
    PTABTrialProceedingResponse,
    # Trial Documents/Decisions Models
    TrialDocumentData,
    TrialDecisionData,
    PTABTrialDocument,
    PTABTrialDocumentResponse,
    # Appeal Decisions Models
    AppealMetaData,
    AppellantData,
    RequestorData,
    AppealDocumentData,
    DecisionData,
    PTABAppealDecision,
    PTABAppealResponse,
    # Interference Decisions Models
    InterferenceMetaData,
    SeniorPartyData,
    JuniorPartyData,
    AdditionalPartyData,
    InterferenceDocumentData,
    PTABInterferenceDecision,
    PTABInterferenceResponse,
)


class TestPartyData:
    """Tests for PartyData base class."""

    def test_party_data_from_dict_full(self) -> None:
        """Test PartyData.from_dict() with all fields."""
        data = {
            "applicationNumberText": "15/123456",
            "counselName": "Test Counsel",
            "grantDate": "2023-01-15",
            "groupArtUnitNumber": "3600",
            "inventorName": "John Inventor",
            "realPartyInInterestName": "Real Party Inc",
            "patentNumber": "US1234567",
            "patentOwnerName": "Patent Owner LLC",
            "technologyCenterNumber": "3600",
            "publicationDate": "2022-12-01",
            "publicationNumber": "US20220012345",
        }
        result = PartyData.from_dict(data)
        assert result.application_number_text == "15/123456"
        assert result.counsel_name == "Test Counsel"
        assert result.grant_date == date(2023, 1, 15)
        assert result.group_art_unit_number == "3600"
        assert result.inventor_name == "John Inventor"
        assert result.real_party_in_interest_name == "Real Party Inc"
        assert result.patent_number == "US1234567"
        assert result.patent_owner_name == "Patent Owner LLC"
        assert result.technology_center_number == "3600"
        assert result.publication_date == date(2022, 12, 1)
        assert result.publication_number == "US20220012345"

    def test_party_data_from_dict_empty(self) -> None:
        """Test PartyData.from_dict() with empty dict."""
        result = PartyData.from_dict({})
        assert result.application_number_text is None
        assert result.counsel_name is None
        assert result.grant_date is None
        assert result.group_art_unit_number is None
        assert result.inventor_name is None
        assert result.real_party_in_interest_name is None
        assert result.patent_number is None
        assert result.patent_owner_name is None
        assert result.technology_center_number is None
        assert result.publication_date is None
        assert result.publication_number is None

    def test_party_data_from_dict_ignores_include_raw_data(self) -> None:
        """Test PartyData.from_dict() ignores include_raw_data parameter."""
        data = {"counselName": "Test"}
        result = PartyData.from_dict(data, include_raw_data=True)
        assert result.counsel_name == "Test"


class TestPTABTrialModels:
    """Tests for PTAB trial proceeding models."""

    def test_trial_metadata_from_dict_full(self) -> None:
        """Test TrialMetaData.from_dict() with all fields."""
        data = {
            "petitionFilingDate": "2023-01-15",
            "accordedFilingDate": "2023-01-16",
            "trialLastModifiedDateTime": "2023-06-01T10:30:00Z",
            "trialLastModifiedDate": "2023-06-01",
            "trialStatusCategory": "Instituted",
            "trialTypeCode": "IPR",
            "fileDownloadURI": "https://example.com/download.zip",
            "terminationDate": "2024-01-15",
            "latestDecisionDate": "2023-12-15",
            "institutionDecisionDate": "2023-07-15",
        }
        result = TrialMetaData.from_dict(data)
        assert result.petition_filing_date == date(2023, 1, 15)
        assert result.accorded_filing_date == date(2023, 1, 16)
        assert result.trial_last_modified_date_time == datetime(2023, 6, 1, 10, 30, 0, tzinfo=timezone.utc)
        assert result.trial_last_modified_date == date(2023, 6, 1)
        assert result.trial_status_category == "Instituted"
        assert result.trial_type_code == "IPR"
        assert result.file_download_uri == "https://example.com/download.zip"
        assert result.termination_date == date(2024, 1, 15)
        assert result.latest_decision_date == date(2023, 12, 15)
        assert result.institution_decision_date == date(2023, 7, 15)

    def test_trial_metadata_from_dict_empty(self) -> None:
        """Test TrialMetaData.from_dict() with empty dict."""
        result = TrialMetaData.from_dict({})
        assert result.petition_filing_date is None
        assert result.accorded_filing_date is None
        assert result.trial_last_modified_date_time is None
        assert result.trial_last_modified_date is None
        assert result.trial_status_category is None
        assert result.trial_type_code is None
        assert result.file_download_uri is None
        assert result.termination_date is None
        assert result.latest_decision_date is None
        assert result.institution_decision_date is None

    def test_patent_owner_data_from_dict(self) -> None:
        """Test PatentOwnerData.from_dict()."""
        data = {
            "patentOwnerName": "Owner Inc",
            "patentNumber": "US1234567",
            "counselName": "Owner Counsel",
        }
        result = PatentOwnerData.from_dict(data)
        assert result.patent_owner_name == "Owner Inc"
        assert result.patent_number == "US1234567"
        assert result.counsel_name == "Owner Counsel"

    def test_regular_petitioner_data_from_dict(self) -> None:
        """Test RegularPetitionerData.from_dict()."""
        data = {
            "counselName": "Test Counsel",
            "realPartyInInterestName": "Real Party",
        }
        result = RegularPetitionerData.from_dict(data)
        assert result.counsel_name == "Test Counsel"
        assert result.real_party_in_interest_name == "Real Party"

    def test_regular_petitioner_data_from_dict_empty(self) -> None:
        """Test RegularPetitionerData.from_dict() with empty dict."""
        result = RegularPetitionerData.from_dict({})
        assert result.counsel_name is None
        assert result.real_party_in_interest_name is None

    def test_respondent_data_from_dict(self) -> None:
        """Test RespondentData.from_dict()."""
        data = {
            "counselName": "Respondent Counsel",
            "realPartyInInterestName": "Respondent Party",
            "patentNumber": "US7654321",
        }
        result = RespondentData.from_dict(data)
        assert result.counsel_name == "Respondent Counsel"
        assert result.real_party_in_interest_name == "Respondent Party"
        assert result.patent_number == "US7654321"

    def test_derivation_petitioner_data_from_dict(self) -> None:
        """Test DerivationPetitionerData.from_dict()."""
        data = {
            "counselName": "Derivation Counsel",
            "grantDate": "2023-01-15",
            "groupArtUnitNumber": "3600",
            "inventorName": "John Inventor",
            "patentNumber": "US1234567",
            "technologyCenterNumber": "3600",
            "realPartyInInterestName": "Derivation Party",
            "patentOwnerName": "Derivation Owner",
        }
        result = DerivationPetitionerData.from_dict(data)
        assert result.counsel_name == "Derivation Counsel"
        assert result.grant_date == date(2023, 1, 15)
        assert result.patent_number == "US1234567"
        assert result.patent_owner_name == "Derivation Owner"

    def test_trial_proceeding_from_dict_full(self) -> None:
        """Test PTABTrialProceeding.from_dict() with all nested objects."""
        data = {
            "trialNumber": "IPR2023-00001",
            "trialRecordIdentifier": "uuid-1",
            "lastModifiedDateTime": "2023-01-15T10:30:00Z",
            "trialMetaData": {
                "petitionFilingDate": "2023-01-01",
                "trialStatusCategory": "Instituted",
                "trialTypeCode": "IPR",
            },
            "patentOwnerData": {
                "patentOwnerName": "Owner Inc",
                "patentNumber": "US1234567",
            },
            "regularPetitionerData": {
                "counselName": "Petitioner Counsel",
                "realPartyInInterestName": "Petitioner Party",
            },
            "respondentData": {
                "counselName": "Respondent Counsel",
                "realPartyInInterestName": "Respondent Party",
            },
            "derivationPetitionerData": {
                "counselName": "Derivation Counsel",
                "patentNumber": "US7654321",
            },
        }
        result = PTABTrialProceeding.from_dict(data)
        assert result.trial_number == "IPR2023-00001"
        assert result.trial_record_identifier == "uuid-1"
        assert result.last_modified_date_time == datetime(2023, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        assert result.trial_meta_data is not None
        assert result.trial_meta_data.trial_status_category == "Instituted"
        assert result.patent_owner_data is not None
        assert result.patent_owner_data.patent_owner_name == "Owner Inc"
        assert result.regular_petitioner_data is not None
        assert result.regular_petitioner_data.counsel_name == "Petitioner Counsel"
        assert result.respondent_data is not None
        assert result.respondent_data.counsel_name == "Respondent Counsel"
        assert result.derivation_petitioner_data is not None
        assert result.derivation_petitioner_data.patent_number == "US7654321"
        assert result.raw_data is None

    def test_trial_proceeding_from_dict_with_raw_data(self) -> None:
        """Test PTABTrialProceeding.from_dict() with include_raw_data=True."""
        data = {
            "trialNumber": "IPR2023-00001",
            "trialRecordIdentifier": "uuid-1",
        }
        result = PTABTrialProceeding.from_dict(data, include_raw_data=True)
        assert result.trial_number == "IPR2023-00001"
        assert result.raw_data == data

    def test_trial_proceeding_from_dict_empty(self) -> None:
        """Test PTABTrialProceeding.from_dict() with empty dict."""
        result = PTABTrialProceeding.from_dict({})
        assert result.trial_number is None
        assert result.trial_record_identifier is None
        assert result.last_modified_date_time is None
        assert result.trial_meta_data is None
        assert result.patent_owner_data is None
        assert result.regular_petitioner_data is None
        assert result.respondent_data is None
        assert result.derivation_petitioner_data is None
        assert result.raw_data is None

    def test_trial_proceeding_response_from_dict_full(self) -> None:
        """Test PTABTrialProceedingResponse.from_dict() with multiple proceedings."""
        data = {
            "count": 2,
            "requestIdentifier": "request-uuid-1",
            "patentTrialProceedingDataBag": [
                {
                    "trialNumber": "IPR2023-00001",
                    "trialRecordIdentifier": "uuid-1",
                },
                {
                    "trialNumber": "IPR2023-00002",
                    "trialRecordIdentifier": "uuid-2",
                },
            ],
        }
        result = PTABTrialProceedingResponse.from_dict(data)
        assert result.count == 2
        assert result.request_identifier == "request-uuid-1"
        assert len(result.patent_trial_proceeding_data_bag) == 2
        assert result.patent_trial_proceeding_data_bag[0].trial_number == "IPR2023-00001"
        assert result.patent_trial_proceeding_data_bag[1].trial_number == "IPR2023-00002"
        assert result.raw_data is None

    def test_trial_proceeding_response_from_dict_with_raw_data(self) -> None:
        """Test PTABTrialProceedingResponse.from_dict() with include_raw_data=True."""
        data = {
            "count": 1,
            "requestIdentifier": "request-uuid-1",
            "patentTrialProceedingDataBag": [
                {"trialNumber": "IPR2023-00001"},
            ],
        }
        result = PTABTrialProceedingResponse.from_dict(data, include_raw_data=True)
        assert result.count == 1
        assert result.raw_data == data
        assert len(result.patent_trial_proceeding_data_bag) == 1
        assert result.patent_trial_proceeding_data_bag[0].raw_data == {
            "trialNumber": "IPR2023-00001"
        }

    def test_trial_proceeding_response_from_dict_empty(self) -> None:
        """Test PTABTrialProceedingResponse.from_dict() with empty list."""
        data = {
            "count": 0,
            "patentTrialProceedingDataBag": [],
        }
        result = PTABTrialProceedingResponse.from_dict(data)
        assert result.count == 0
        assert len(result.patent_trial_proceeding_data_bag) == 0


class TestPTABTrialDocumentModels:
    """Tests for PTAB trial document models."""

    def test_trial_document_data_from_dict_full(self) -> None:
        """Test TrialDocumentData.from_dict() with all fields."""
        data = {
            "documentCategory": "Petition",
            "documentFilingDate": "2023-01-15",
            "documentIdentifier": "doc-uuid-1",
            "documentName": "Petition.pdf",
            "documentNumber": "1001",
            "documentSizeQuantity": 123456,
            "documentOCRText": "Full OCR text content here...",
            "documentTitleText": "Petition for IPR",
            "documentTypeDescriptionText": "Petition Document",
            "downloadURI": "https://example.com/doc1.pdf",
            "filingPartyCategory": "Petitioner",
            "mimeTypeIdentifier": "application/pdf",
            "documentStatus": "Public",
        }
        result = TrialDocumentData.from_dict(data)
        assert result.document_category == "Petition"
        assert result.document_filing_date == date(2023, 1, 15)
        assert result.document_identifier == "doc-uuid-1"
        assert result.document_name == "Petition.pdf"
        assert result.document_number == "1001"
        assert result.document_size_quantity == 123456
        assert result.document_ocr_text == "Full OCR text content here..."
        assert result.document_title_text == "Petition for IPR"
        assert result.document_type_description_text == "Petition Document"
        assert result.file_download_uri == "https://example.com/doc1.pdf"
        assert result.filing_party_category == "Petitioner"
        assert result.mime_type_identifier == "application/pdf"
        assert result.document_status == "Public"

    def test_trial_document_data_from_dict_empty(self) -> None:
        """Test TrialDocumentData.from_dict() with empty dict."""
        result = TrialDocumentData.from_dict({})
        assert result.document_category is None
        assert result.document_filing_date is None
        assert result.document_identifier is None
        assert result.document_name is None
        assert result.document_number is None
        assert result.document_size_quantity is None
        assert result.document_ocr_text is None
        assert result.document_title_text is None
        assert result.document_type_description_text is None
        assert result.file_download_uri is None
        assert result.filing_party_category is None
        assert result.mime_type_identifier is None
        assert result.document_status is None

    def test_trial_decision_data_from_dict_full(self) -> None:
        """Test TrialDecisionData.from_dict() with all fields."""
        data = {
            "statuteAndRuleBag": ["35 U.S.C. § 103", "37 CFR 42.100"],
            "decisionIssueDate": "2023-12-15",
            "decisionTypeCategory": "Final Written Decision",
            "issueTypeBag": ["Obviousness", "Claim Construction"],
            "trialOutcomeCategory": "Denied",
        }
        result = TrialDecisionData.from_dict(data)
        assert result.statute_and_rule_bag == ["35 U.S.C. § 103", "37 CFR 42.100"]
        assert result.decision_issue_date == date(2023, 12, 15)
        assert result.decision_type_category == "Final Written Decision"
        assert result.issue_type_bag == ["Obviousness", "Claim Construction"]
        assert result.trial_outcome_category == "Denied"

    def test_trial_decision_data_from_dict_empty(self) -> None:
        """Test TrialDecisionData.from_dict() with empty dict."""
        result = TrialDecisionData.from_dict({})
        assert result.statute_and_rule_bag == []
        assert result.decision_issue_date is None
        assert result.decision_type_category is None
        assert result.issue_type_bag == []
        assert result.trial_outcome_category is None

    def test_trial_document_from_dict_full(self) -> None:
        """Test PTABTrialDocument.from_dict() with all nested objects."""
        data = {
            "trialDocumentCategory": "Decision",
            "lastModifiedDateTime": "2023-12-15T10:30:00Z",
            "trialNumber": "IPR2023-00001",
            "trialTypeCode": "IPR",
            "trialMetaData": {
                "trialStatusCategory": "Terminated",
            },
            "patentOwnerData": {
                "patentOwnerName": "Owner Inc",
            },
            "regularPetitionerData": {
                "counselName": "Petitioner Counsel",
            },
            "respondentData": {
                "counselName": "Respondent Counsel",
            },
            "derivationPetitionerData": {
                "patentNumber": "US7654321",
            },
            "documentData": {
                "documentName": "Decision.pdf",
                "documentIdentifier": "doc-123",
            },
            "decisionData": {
                "decisionTypeCategory": "Final Written Decision",
                "trialOutcomeCategory": "Denied",
            },
        }
        result = PTABTrialDocument.from_dict(data)
        assert result.trial_document_category == "Decision"
        assert result.last_modified_date_time == datetime(2023, 12, 15, 10, 30, 0, tzinfo=timezone.utc)
        assert result.trial_number == "IPR2023-00001"
        assert result.trial_type_code == "IPR"
        assert result.trial_meta_data is not None
        assert result.trial_meta_data.trial_status_category == "Terminated"
        assert result.patent_owner_data is not None
        assert result.patent_owner_data.patent_owner_name == "Owner Inc"
        assert result.regular_petitioner_data is not None
        assert result.regular_petitioner_data.counsel_name == "Petitioner Counsel"
        assert result.respondent_data is not None
        assert result.respondent_data.counsel_name == "Respondent Counsel"
        assert result.derivation_petitioner_data is not None
        assert result.derivation_petitioner_data.patent_number == "US7654321"
        assert result.document_data is not None
        assert result.document_data.document_name == "Decision.pdf"
        assert result.decision_data is not None
        assert result.decision_data.decision_type_category == "Final Written Decision"
        assert result.raw_data is None

    def test_trial_document_from_dict_with_raw_data(self) -> None:
        """Test PTABTrialDocument.from_dict() with include_raw_data=True."""
        data = {
            "trialNumber": "IPR2023-00001",
            "trialDocumentCategory": "Document",
        }
        result = PTABTrialDocument.from_dict(data, include_raw_data=True)
        assert result.trial_number == "IPR2023-00001"
        assert result.raw_data == data

    def test_trial_document_from_dict_empty(self) -> None:
        """Test PTABTrialDocument.from_dict() with empty dict."""
        result = PTABTrialDocument.from_dict({})
        assert result.trial_document_category is None
        assert result.last_modified_date_time is None
        assert result.trial_number is None
        assert result.trial_type_code is None
        assert result.trial_meta_data is None
        assert result.patent_owner_data is None
        assert result.regular_petitioner_data is None
        assert result.respondent_data is None
        assert result.derivation_petitioner_data is None
        assert result.document_data is None
        assert result.decision_data is None
        assert result.raw_data is None

    def test_trial_document_response_from_dict_full(self) -> None:
        """Test PTABTrialDocumentResponse.from_dict() with multiple documents."""
        data = {
            "count": 2,
            "patentTrialDocumentDataBag": [
                {
                    "trialNumber": "IPR2023-00001",
                    "trialDocumentCategory": "Document",
                },
                {
                    "trialNumber": "IPR2023-00002",
                    "trialDocumentCategory": "Decision",
                },
            ],
        }
        result = PTABTrialDocumentResponse.from_dict(data)
        assert result.count == 2
        assert len(result.patent_trial_document_data_bag) == 2
        assert result.patent_trial_document_data_bag[0].trial_number == "IPR2023-00001"
        assert result.patent_trial_document_data_bag[0].trial_document_category == "Document"
        assert result.patent_trial_document_data_bag[1].trial_number == "IPR2023-00002"
        assert result.patent_trial_document_data_bag[1].trial_document_category == "Decision"
        assert result.raw_data is None

    def test_trial_document_response_from_dict_with_raw_data(self) -> None:
        """Test PTABTrialDocumentResponse.from_dict() with include_raw_data=True."""
        data = {
            "count": 1,
            "patentTrialDocumentDataBag": [
                {"trialNumber": "IPR2023-00001"},
            ],
        }
        result = PTABTrialDocumentResponse.from_dict(data, include_raw_data=True)
        assert result.count == 1
        assert result.raw_data == data
        assert len(result.patent_trial_document_data_bag) == 1
        assert result.patent_trial_document_data_bag[0].raw_data == {
            "trialNumber": "IPR2023-00001"
        }

    def test_trial_document_response_from_dict_empty(self) -> None:
        """Test PTABTrialDocumentResponse.from_dict() with empty list."""
        result = PTABTrialDocumentResponse.from_dict({})
        assert result.count is None
        assert len(result.patent_trial_document_data_bag) == 0
        assert result.raw_data is None


class TestPTABAppealModels:
    """Tests for PTAB appeal decision models."""

    def test_appeal_metadata_from_dict_full(self) -> None:
        """Test AppealMetaData.from_dict() with all fields."""
        data = {
            "appealFilingDate": "2023-01-15",
            "appealLastModifiedDate": "2023-06-01",
            "applicationTypeCategory": "Utility",
            "docketNoticeMailedDate": "2023-02-01",
            "fileDownloadURI": "https://example.com/appeal.zip",
        }
        result = AppealMetaData.from_dict(data)
        assert result.appeal_filing_date == date(2023, 1, 15)
        assert result.appeal_last_modified_date == date(2023, 6, 1)
        assert result.application_type_category == "Utility"
        assert result.docket_notice_mailed_date == date(2023, 2, 1)
        assert result.file_download_uri == "https://example.com/appeal.zip"

    def test_appeal_metadata_from_dict_empty(self) -> None:
        """Test AppealMetaData.from_dict() with empty dict."""
        result = AppealMetaData.from_dict({})
        assert result.appeal_filing_date is None
        assert result.appeal_last_modified_date is None
        assert result.application_type_category is None
        assert result.docket_notice_mailed_date is None
        assert result.file_download_uri is None

    def test_appellant_data_from_dict(self) -> None:
        """Test AppellantData.from_dict()."""
        data = {
            "applicationNumberText": "15/123456",
            "counselName": "Appellant Counsel",
            "groupArtUnitNumber": "3600",
            "inventorName": "Jane Inventor",
            "realPartyInInterestName": "Appellant Party",
            "patentOwnerName": "Appellant Owner",
            "publicationDate": "2023-01-15",
            "publicationNumber": "US20230012345",
            "technologyCenterNumber": "3600",
        }
        result = AppellantData.from_dict(data)
        assert result.application_number_text == "15/123456"
        assert result.counsel_name == "Appellant Counsel"
        assert result.inventor_name == "Jane Inventor"
        assert result.technology_center_number == "3600"
        assert result.publication_date == date(2023, 1, 15)

    def test_requestor_data_from_dict(self) -> None:
        """Test RequestorData.from_dict()."""
        data = {"thirdPartyName": "Third Party Inc"}
        result = RequestorData.from_dict(data)
        assert result.third_party_name == "Third Party Inc"

    def test_requestor_data_from_dict_empty(self) -> None:
        """Test RequestorData.from_dict() with empty dict."""
        result = RequestorData.from_dict({})
        assert result.third_party_name is None

    def test_appeal_document_data_from_dict_full(self) -> None:
        """Test AppealDocumentData.from_dict() with all fields."""
        data = {
            "documentFilingDate": "2023-01-15",
            "documentIdentifier": "doc-uuid-1",
            "documentName": "Appeal Brief",
            "documentSizeQuantity": 12345,
            "documentOCRText": "Full OCR text content",
            "documentTypeDescriptionText": "Brief",
            "fileDownloadURI": "https://example.com/download",
        }
        result = AppealDocumentData.from_dict(data)
        assert result.document_filing_date == date(2023, 1, 15)
        assert result.document_identifier == "doc-uuid-1"
        assert result.document_name == "Appeal Brief"
        assert result.document_size_quantity == 12345
        assert result.document_ocr_text == "Full OCR text content"
        assert result.document_type_description_text == "Brief"
        assert result.file_download_uri == "https://example.com/download"

    def test_appeal_document_data_from_dict_with_alias_downloaduri(self) -> None:
        """Test AppealDocumentData.from_dict() handles downloadURI alias."""
        data = {
            "documentName": "Brief.pdf",
            "downloadURI": "https://example.com/brief.pdf",
        }
        result = AppealDocumentData.from_dict(data)
        assert result.file_download_uri == "https://example.com/brief.pdf"

    def test_appeal_document_data_from_dict_with_alias_document_type(self) -> None:
        """Test AppealDocumentData.from_dict() handles documentTypeCategory alias."""
        data = {
            "documentName": "Decision.pdf",
            "documentTypeCategory": "Decision",
        }
        result = AppealDocumentData.from_dict(data)
        assert result.document_type_description_text == "Decision"

    def test_appeal_document_data_from_dict_empty(self) -> None:
        """Test AppealDocumentData.from_dict() with empty dict."""
        result = AppealDocumentData.from_dict({})
        assert result.document_filing_date is None
        assert result.document_identifier is None
        assert result.document_name is None
        assert result.document_size_quantity is None
        assert result.document_ocr_text is None
        assert result.document_type_description_text is None
        assert result.file_download_uri is None

    def test_decision_data_from_dict_full(self) -> None:
        """Test DecisionData.from_dict() with all fields."""
        data = {
            "appealOutcomeCategory": "Affirmed",
            "statuteAndRuleBag": ["35 U.S.C. § 103", "37 CFR 1.111"],
            "decisionIssueDate": "2023-12-15",
            "decisionTypeCategory": "Examiner Affirmed",
            "issueTypeBag": ["Obviousness", "Anticipation"],
        }
        result = DecisionData.from_dict(data)
        assert result.appeal_outcome_category == "Affirmed"
        assert result.statute_and_rule_bag == ["35 U.S.C. § 103", "37 CFR 1.111"]
        assert result.decision_issue_date == date(2023, 12, 15)
        assert result.decision_type_category == "Examiner Affirmed"
        assert result.issue_type_bag == ["Obviousness", "Anticipation"]

    def test_decision_data_from_dict_empty(self) -> None:
        """Test DecisionData.from_dict() with empty dict."""
        result = DecisionData.from_dict({})
        assert result.appeal_outcome_category is None
        assert result.statute_and_rule_bag == []
        assert result.decision_issue_date is None
        assert result.decision_type_category is None
        assert result.issue_type_bag == []

    def test_appeal_decision_from_dict_full(self) -> None:
        """Test PTABAppealDecision.from_dict() with all nested objects."""
        data = {
            "appealNumber": "2023-001234",
            "lastModifiedDateTime": "2023-06-15T10:30:00Z",
            "appealDocumentCategory": "Decision",
            "appealMetaData": {
                "appealFilingDate": "2023-01-15",
                "applicationTypeCategory": "Utility",
            },
            "appellantData": {
                "applicationNumberText": "15/123456",
                "counselName": "Test Counsel",
                "technologyCenterNumber": "3600",
            },
            "requestorData": {"thirdPartyName": "Third Party Inc"},
            "documentData": {
                "documentName": "Final Decision",
                "documentIdentifier": "doc-123",
            },
            "decisionData": {
                "decisionTypeCategory": "Affirmed",
                "decisionIssueDate": "2023-06-01",
            },
        }
        result = PTABAppealDecision.from_dict(data)
        assert result.appeal_number == "2023-001234"
        assert result.last_modified_date_time == datetime(2023, 6, 15, 10, 30, 0, tzinfo=timezone.utc)
        assert result.appeal_document_category == "Decision"
        assert result.appeal_meta_data is not None
        assert result.appeal_meta_data.application_type_category == "Utility"
        assert result.appellant_data is not None
        assert result.appellant_data.counsel_name == "Test Counsel"
        assert result.requestor_data is not None
        assert result.requestor_data.third_party_name == "Third Party Inc"
        assert result.document_data is not None
        assert result.document_data.document_name == "Final Decision"
        assert result.decision_data is not None
        assert result.decision_data.decision_type_category == "Affirmed"
        assert result.raw_data is None

    def test_appeal_decision_from_dict_with_typo_appelant(self) -> None:
        """Test PTABAppealDecision.from_dict() handles 'appelantData' typo."""
        data = {
            "appealNumber": "2023-001234",
            "appelantData": {
                "counselName": "Test Counsel",
            },
        }
        result = PTABAppealDecision.from_dict(data)
        assert result.appellant_data is not None
        assert result.appellant_data.counsel_name == "Test Counsel"

    def test_appeal_decision_from_dict_with_raw_data(self) -> None:
        """Test PTABAppealDecision.from_dict() with include_raw_data=True."""
        data = {
            "appealNumber": "2023-001234",
            "appealDocumentCategory": "Decision",
        }
        result = PTABAppealDecision.from_dict(data, include_raw_data=True)
        assert result.appeal_number == "2023-001234"
        assert result.raw_data == data

    def test_appeal_decision_from_dict_empty(self) -> None:
        """Test PTABAppealDecision.from_dict() with empty dict."""
        result = PTABAppealDecision.from_dict({})
        assert result.appeal_number is None
        assert result.last_modified_date_time is None
        assert result.appeal_document_category is None
        assert result.appeal_meta_data is None
        assert result.appellant_data is None
        assert result.requestor_data is None
        assert result.document_data is None
        assert result.decision_data is None
        assert result.raw_data is None

    def test_appeal_response_from_dict_full(self) -> None:
        """Test PTABAppealResponse.from_dict() with multiple appeals."""
        data = {
            "count": 2,
            "requestIdentifier": "request-uuid-1",
            "patentAppealDataBag": [
                {
                    "appealNumber": "2023-001234",
                    "appealDocumentCategory": "Decision",
                },
                {
                    "appealNumber": "2023-005678",
                    "appealDocumentCategory": "Brief",
                },
            ],
        }
        result = PTABAppealResponse.from_dict(data)
        assert result.count == 2
        assert result.request_identifier == "request-uuid-1"
        assert len(result.patent_appeal_data_bag) == 2
        assert result.patent_appeal_data_bag[0].appeal_number == "2023-001234"
        assert result.patent_appeal_data_bag[0].appeal_document_category == "Decision"
        assert result.patent_appeal_data_bag[1].appeal_number == "2023-005678"
        assert result.patent_appeal_data_bag[1].appeal_document_category == "Brief"
        assert result.raw_data is None

    def test_appeal_response_from_dict_with_raw_data(self) -> None:
        """Test PTABAppealResponse.from_dict() with include_raw_data=True."""
        data = {
            "count": 1,
            "requestIdentifier": "request-uuid-1",
            "patentAppealDataBag": [
                {"appealNumber": "2023-001234"},
            ],
        }
        result = PTABAppealResponse.from_dict(data, include_raw_data=True)
        assert result.count == 1
        assert result.raw_data == data
        assert len(result.patent_appeal_data_bag) == 1
        assert result.patent_appeal_data_bag[0].raw_data == {"appealNumber": "2023-001234"}

    def test_appeal_response_from_dict_empty(self) -> None:
        """Test PTABAppealResponse.from_dict() with empty list."""
        result = PTABAppealResponse.from_dict({})
        assert result.count is None
        assert result.request_identifier is None
        assert len(result.patent_appeal_data_bag) == 0
        assert result.raw_data is None


class TestPTABInterferenceModels:
    """Tests for PTAB interference decision models."""

    def test_interference_metadata_from_dict_full(self) -> None:
        """Test InterferenceMetaData.from_dict() with all fields."""
        data = {
            "interferenceStyleName": "Senior v. Junior",
            "interferenceLastModifiedDate": "2023-03-15",
            "fileDownloadURI": "https://example.com/interference.zip",
        }
        result = InterferenceMetaData.from_dict(data)
        assert result.interference_style_name == "Senior v. Junior"
        assert result.interference_last_modified_date == date(2023, 3, 15)
        assert result.file_download_uri == "https://example.com/interference.zip"

    def test_interference_metadata_from_dict_empty(self) -> None:
        """Test InterferenceMetaData.from_dict() with empty dict."""
        result = InterferenceMetaData.from_dict({})
        assert result.interference_style_name is None
        assert result.interference_last_modified_date is None
        assert result.file_download_uri is None

    def test_senior_party_data_from_dict(self) -> None:
        """Test SeniorPartyData.from_dict()."""
        data = {
            "applicationNumberText": "12/345678",
            "counselName": "Senior Counsel",
            "grantDate": "2023-01-15",
            "groupArtUnitNumber": "1600",
            "realPartyInInterestName": "Senior Party Inc",
            "patentNumber": "US1234567",
            "patentOwnerName": "Senior Owner",
            "technologyCenterNumber": "1600",
        }
        result = SeniorPartyData.from_dict(data)
        assert result.application_number_text == "12/345678"
        assert result.counsel_name == "Senior Counsel"
        assert result.grant_date == date(2023, 1, 15)
        assert result.patent_owner_name == "Senior Owner"
        assert result.patent_number == "US1234567"

    def test_junior_party_data_from_dict(self) -> None:
        """Test JuniorPartyData.from_dict()."""
        data = {
            "publicationNumber": "US20230012345",
            "counselName": "Junior Counsel",
            "groupArtUnitNumber": "1600",
            "inventorName": "Jane Inventor",
            "patentOwnerName": "Junior Owner",
            "publicationDate": "2023-02-20",
            "realPartyInInterestName": "Junior Party LLC",
            "technologyCenterNumber": "1600",
        }
        result = JuniorPartyData.from_dict(data)
        assert result.publication_number == "US20230012345"
        assert result.counsel_name == "Junior Counsel"
        assert result.inventor_name == "Jane Inventor"
        assert result.patent_owner_name == "Junior Owner"
        assert result.publication_date == date(2023, 2, 20)

    def test_additional_party_data_from_dict(self) -> None:
        """Test AdditionalPartyData.from_dict()."""
        data = {
            "applicationNumberText": "14/111222",
            "inventorName": "John Inventor",
            "additionalPartyName": "Additional Entity",
            "patentNumber": "US1112223",
        }
        result = AdditionalPartyData.from_dict(data)
        assert result.application_number_text == "14/111222"
        assert result.inventor_name == "John Inventor"
        assert result.additional_party_name == "Additional Entity"
        assert result.patent_number == "US1112223"

    def test_additional_party_data_from_dict_empty(self) -> None:
        """Test AdditionalPartyData.from_dict() with empty dict."""
        result = AdditionalPartyData.from_dict({})
        assert result.application_number_text is None
        assert result.inventor_name is None
        assert result.additional_party_name is None
        assert result.patent_number is None

    def test_interference_document_data_from_dict_full(self) -> None:
        """Test InterferenceDocumentData.from_dict() with all fields."""
        data = {
            "documentIdentifier": "doc-uuid-1",
            "documentName": "Final Decision.pdf",
            "documentSizeQuantity": 234567,
            "documentOCRText": "Full OCR content...",
            "documentTitleText": "Final Decision on Priority",
            "interferenceOutcomeCategory": "Priority to Senior Party",
            "decisionIssueDate": "2023-03-15",
            "decisionTypeCategory": "Final Decision",
            "fileDownloadURI": "https://example.com/decision.pdf",
            "statuteAndRuleBag": ["35 U.S.C. § 102", "37 CFR 41.125"],
            "issueTypeBag": ["Priority", "Patentability"],
        }
        result = InterferenceDocumentData.from_dict(data)
        assert result.document_identifier == "doc-uuid-1"
        assert result.document_name == "Final Decision.pdf"
        assert result.document_size_quantity == 234567
        assert result.document_ocr_text == "Full OCR content..."
        assert result.document_title_text == "Final Decision on Priority"
        assert result.interference_outcome_category == "Priority to Senior Party"
        assert result.decision_issue_date == date(2023, 3, 15)
        assert result.decision_type_category == "Final Decision"
        assert result.file_download_uri == "https://example.com/decision.pdf"
        assert result.statute_and_rule_bag == ["35 U.S.C. § 102", "37 CFR 41.125"]
        assert result.issue_type_bag == ["Priority", "Patentability"]

    def test_interference_document_data_from_dict_with_alias_downloaduri(self) -> None:
        """Test InterferenceDocumentData.from_dict() handles downloadURI alias."""
        data = {
            "documentName": "Decision.pdf",
            "downloadURI": "https://example.com/decision.pdf",
        }
        result = InterferenceDocumentData.from_dict(data)
        assert result.file_download_uri == "https://example.com/decision.pdf"

    def test_interference_document_data_from_dict_empty(self) -> None:
        """Test InterferenceDocumentData.from_dict() with empty dict."""
        result = InterferenceDocumentData.from_dict({})
        assert result.document_identifier is None
        assert result.document_name is None
        assert result.document_size_quantity is None
        assert result.document_ocr_text is None
        assert result.document_title_text is None
        assert result.interference_outcome_category is None
        assert result.decision_issue_date is None
        assert result.decision_type_category is None
        assert result.file_download_uri is None
        assert result.statute_and_rule_bag == []
        assert result.issue_type_bag == []

    def test_interference_decision_from_dict_full(self) -> None:
        """Test PTABInterferenceDecision.from_dict() with all nested objects."""
        data = {
            "interferenceNumber": "106123",
            "lastModifiedDateTime": "2023-03-15T10:30:00Z",
            "interferenceMetaData": {
                "interferenceStyleName": "Senior v. Junior",
                "interferenceLastModifiedDate": "2023-03-15",
            },
            "seniorPartyData": {
                "patentOwnerName": "Senior Inc",
                "applicationNumberText": "12/345678",
                "patentNumber": "US1234567",
            },
            "juniorPartyData": {
                "patentOwnerName": "Junior LLC",
                "publicationNumber": "US20230012345",
            },
            "additionalPartyDataBag": [
                {
                    "additionalPartyName": "Additional Party 1",
                    "applicationNumberText": "14/111222",
                },
                {
                    "additionalPartyName": "Additional Party 2",
                    "applicationNumberText": "14/333444",
                },
            ],
            "documentData": {
                "interferenceOutcomeCategory": "Priority to Senior Party",
                "decisionTypeCategory": "Final Decision",
            },
        }
        result = PTABInterferenceDecision.from_dict(data)
        assert result.interference_number == "106123"
        assert result.last_modified_date_time == datetime(2023, 3, 15, 10, 30, 0, tzinfo=timezone.utc)
        assert result.interference_meta_data is not None
        assert result.interference_meta_data.interference_style_name == "Senior v. Junior"
        assert result.senior_party_data is not None
        assert result.senior_party_data.patent_owner_name == "Senior Inc"
        assert result.junior_party_data is not None
        assert result.junior_party_data.patent_owner_name == "Junior LLC"
        assert len(result.additional_party_data_bag) == 2
        assert result.additional_party_data_bag[0].additional_party_name == "Additional Party 1"
        assert result.additional_party_data_bag[1].additional_party_name == "Additional Party 2"
        assert result.document_data is not None
        assert result.document_data.interference_outcome_category == "Priority to Senior Party"
        assert result.raw_data is None

    def test_interference_decision_from_dict_with_alias_decision_document_data(
        self,
    ) -> None:
        """Test PTABInterferenceDecision.from_dict() handles decisionDocumentData alias."""
        data = {
            "interferenceNumber": "106123",
            "decisionDocumentData": {
                "decisionTypeCategory": "Final Decision",
            },
        }
        result = PTABInterferenceDecision.from_dict(data)
        assert result.document_data is not None
        assert result.document_data.decision_type_category == "Final Decision"

    def test_interference_decision_from_dict_with_raw_data(self) -> None:
        """Test PTABInterferenceDecision.from_dict() with include_raw_data=True."""
        data = {
            "interferenceNumber": "106123",
        }
        result = PTABInterferenceDecision.from_dict(data, include_raw_data=True)
        assert result.interference_number == "106123"
        assert result.raw_data == data

    def test_interference_decision_from_dict_empty(self) -> None:
        """Test PTABInterferenceDecision.from_dict() with empty dict."""
        result = PTABInterferenceDecision.from_dict({})
        assert result.interference_number is None
        assert result.last_modified_date_time is None
        assert result.interference_meta_data is None
        assert result.senior_party_data is None
        assert result.junior_party_data is None
        assert len(result.additional_party_data_bag) == 0
        assert result.document_data is None
        assert result.raw_data is None

    def test_interference_response_from_dict_full(self) -> None:
        """Test PTABInterferenceResponse.from_dict() with multiple interferences."""
        data = {
            "count": 2,
            "requestIdentifier": "request-uuid-1",
            "patentInterferenceDataBag": [
                {
                    "interferenceNumber": "106123",
                },
                {
                    "interferenceNumber": "106456",
                },
            ],
        }
        result = PTABInterferenceResponse.from_dict(data)
        assert result.count == 2
        assert result.request_identifier == "request-uuid-1"
        assert len(result.patent_interference_data_bag) == 2
        assert result.patent_interference_data_bag[0].interference_number == "106123"
        assert result.patent_interference_data_bag[1].interference_number == "106456"
        assert result.raw_data is None

    def test_interference_response_from_dict_with_raw_data(self) -> None:
        """Test PTABInterferenceResponse.from_dict() with include_raw_data=True."""
        data = {
            "count": 1,
            "requestIdentifier": "request-uuid-1",
            "patentInterferenceDataBag": [
                {"interferenceNumber": "106123"},
            ],
        }
        result = PTABInterferenceResponse.from_dict(data, include_raw_data=True)
        assert result.count == 1
        assert result.raw_data == data
        assert len(result.patent_interference_data_bag) == 1
        assert result.patent_interference_data_bag[0].raw_data == {
            "interferenceNumber": "106123"
        }

    def test_interference_response_from_dict_empty(self) -> None:
        """Test PTABInterferenceResponse.from_dict() with empty list."""
        result = PTABInterferenceResponse.from_dict({})
        assert result.count is None
        assert result.request_identifier is None
        assert len(result.patent_interference_data_bag) == 0
        assert result.raw_data is None
