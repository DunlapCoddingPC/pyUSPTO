"""
Tests for PTAB models.

This module contains unit tests for the PTAB model classes.
"""

from typing import Any, Dict

import pytest

from pyUSPTO.models.ptab import (
    PTABAppealDecision,
    PTABAppealResponse,
    PTABInterferenceDecision,
    PTABInterferenceResponse,
    PTABTrialProceeding,
    PTABTrialProceedingResponse,
    RegularPetitionerData,
    RespondentData,
    DerivationPetitionerData,
    AppellantData,
    RequestorData,
    AppealDocumentData,
    SeniorPartyData,
    JuniorPartyData,
    AdditionalPartyData,
)


class TestPTABTrialModels:
    """Tests for PTAB trial proceeding models."""

    def test_regular_petitioner_data_from_dict(self) -> None:
        """Test RegularPetitionerData.from_dict()."""
        data = {
            "counselName": "Test Counsel",
            "realPartyInInterestName": "Real Party",
        }
        result = RegularPetitionerData.from_dict(data)
        assert result.counsel_name == "Test Counsel"
        assert result.real_party_in_interest_name == "Real Party"

    def test_respondent_data_from_dict(self) -> None:
        """Test RespondentData.from_dict()."""
        data = {
            "counselName": "Respondent Counsel",
            "realPartyInInterestName": "Respondent Party",
        }
        result = RespondentData.from_dict(data)
        assert result.counsel_name == "Respondent Counsel"
        assert result.real_party_in_interest_name == "Respondent Party"

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
        assert result.patent_number == "US1234567"
        assert result.patent_owner_name == "Derivation Owner"

    def test_trial_proceeding_with_all_nested_objects(self) -> None:
        """Test PTABTrialProceeding with all nested objects."""
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
        assert result.regular_petitioner_data is not None
        assert result.regular_petitioner_data.counsel_name == "Petitioner Counsel"
        assert result.respondent_data is not None
        assert result.respondent_data.counsel_name == "Respondent Counsel"
        assert result.derivation_petitioner_data is not None
        assert result.derivation_petitioner_data.patent_number == "US7654321"


class TestPTABAppealModels:
    """Tests for PTAB appeal decision models."""

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

    def test_requestor_data_from_dict(self) -> None:
        """Test RequestorData.from_dict()."""
        data = {"thirdPartyName": "Third Party Inc"}
        result = RequestorData.from_dict(data)
        assert result.third_party_name == "Third Party Inc"

    def test_appeal_document_data_from_dict(self) -> None:
        """Test AppealDocumentData.from_dict()."""
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
        assert result.document_name == "Appeal Brief"
        assert result.document_size_quantity == 12345
        assert result.document_ocr_text == "Full OCR text content"

    def test_appeal_decision_with_all_nested_objects(self) -> None:
        """Test PTABAppealDecision with all nested objects."""
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
                "decisionDate": "2023-06-01",
            },
        }
        result = PTABAppealDecision.from_dict(data)
        assert result.appeal_number == "2023-001234"
        assert result.appellant_data is not None
        assert result.appellant_data.counsel_name == "Test Counsel"
        assert result.requestor_data is not None
        assert result.requestor_data.third_party_name == "Third Party Inc"
        assert result.document_data is not None
        assert result.document_data.document_name == "Final Decision"


class TestPTABInterferenceModels:
    """Tests for PTAB interference decision models."""

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

    def test_interference_decision_with_all_nested_objects(self) -> None:
        """Test PTABInterferenceDecision with all nested objects."""
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
        assert result.senior_party_data is not None
        assert result.senior_party_data.patent_owner_name == "Senior Inc"
        assert result.junior_party_data is not None
        assert result.junior_party_data.patent_owner_name == "Junior LLC"
        assert len(result.additional_party_data_bag) == 2
        assert result.additional_party_data_bag[0].additional_party_name == "Additional Party 1"
        assert result.additional_party_data_bag[1].additional_party_name == "Additional Party 2"
