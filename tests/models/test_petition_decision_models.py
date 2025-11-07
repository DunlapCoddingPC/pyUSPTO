"""
Tests for the petition_decisions models.

This module contains comprehensive tests for all classes in pyUSPTO.models.petition_decisions.
"""

from datetime import date, datetime, timezone
from typing import Any, Dict

import pytest

from pyUSPTO.models.petition_decisions import (
    DecisionTypeCode,
    DocumentDirectionCategory,
    DocumentDownloadOption,
    PetitionDecision,
    PetitionDecisionDocument,
    PetitionDecisionDownloadResponse,
    PetitionDecisionResponse,
)


@pytest.fixture
def sample_download_option_dict() -> Dict[str, Any]:
    """Provide a sample download option dictionary."""
    return {
        "mimeTypeIdentifier": "PDF",
        "downloadUrl": "https://api.test.uspto.gov/api/v1/download/applications/13815942/M98QOH0NWFYTX17.pdf",
        "pageTotalQuantity": 10,
    }


@pytest.fixture
def sample_document_dict() -> Dict[str, Any]:
    """Provide a sample petition decision document dictionary."""
    return {
        "applicationNumberText": "13815942",
        "officialDate": "2025-03-20T11:41:54+00:00",
        "documentIdentifier": "M98QOH0NWFYTX17",
        "documentCode": "PETDEC",
        "documentCodeDescriptionText": "Petition Decision",
        "documentDirectionCategory": "OUTGOING",
        "downloadOptionBag": [
            {
                "mimeTypeIdentifier": "PDF",
                "downloadUrl": "https://api.test.uspto.gov/api/v1/download/applications/13815942/M98QOH0NWFYTX17.pdf",
                "pageTotalQuantity": 10,
            },
            {
                "mimeTypeIdentifier": "XML",
                "downloadUrl": "https://api.test.uspto.gov/api/v1/download/applications/13815942/M98QOH0NWFYTX17/xmlarchive",
            },
        ],
    }


@pytest.fixture
def sample_petition_decision_dict() -> Dict[str, Any]:
    """Provide a sample petition decision dictionary."""
    return {
        "actionTakenByCourtName": "None",
        "applicationNumberText": "17765301",
        "businessEntityStatusCategory": "Regular Undiscounted",
        "courtActionIndicator": False,
        "customerNumber": 48980,
        "decisionDate": "2025-01-23",
        "decisionPetitionTypeCode": 652,
        "decisionTypeCode": "C",
        "decisionTypeCodeDescriptionText": "DENIED",
        "finalDecidingOfficeName": "OFFICE OF PETITIONS",
        "firstApplicantName": "SHANGSHUI SMARTECH LTD.",
        "firstInventorToFileIndicator": True,
        "groupArtUnitNumber": "1774",
        "inventionTitle": "Impeller Assembly For Dispersing Solid In Liquid",
        "inventorBag": ["Qiao Shi", "Shujuan Bai", "Tongzhu Li", "Quanxun Ou"],
        "lastIngestionDateTime": "2025-05-05T15:31:39",
        "petitionDecisionRecordIdentifier": "9f1a4a2b-eee1-58ec-a3aa-167c4075aed4",
        "petitionIssueConsideredTextBag": ["Make special: Patent Prosecution Highway"],
        "petitionMailDate": "2024-11-12",
        "prosecutionStatusCode": "160",
        "prosecutionStatusCodeDescriptionText": "Prior to examination",
        "ruleBag": ["37 CFR 1.102(a)"],
        "statuteBag": [],
        "technologyCenter": "1700",
    }


@pytest.fixture
def sample_petition_response_dict(
    sample_petition_decision_dict: Dict[str, Any],
) -> Dict[str, Any]:
    """Provide a sample petition decision response dictionary."""
    return {
        "count": 1,
        "requestIdentifier": "01f0c175-a9e7-4f2d-9781-9ba6c2203b51",
        "petitionDecisionDataBag": [sample_petition_decision_dict],
    }


@pytest.fixture
def sample_download_response_dict(
    sample_petition_decision_dict: Dict[str, Any],
) -> Dict[str, Any]:
    """Provide a sample download response dictionary."""
    return {"petitionDecisionData": [sample_petition_decision_dict]}


class TestDocumentDownloadOptionFromDict:
    """Tests for DocumentDownloadOption.from_dict method."""

    def test_from_dict_complete(
        self, sample_download_option_dict: Dict[str, Any]
    ) -> None:
        """Test from_dict with complete data."""
        option = DocumentDownloadOption.from_dict(sample_download_option_dict)
        assert option.mime_type_identifier == "PDF"
        assert (
            option.download_url
            == "https://api.test.uspto.gov/api/v1/download/applications/13815942/M98QOH0NWFYTX17.pdf"
        )
        assert option.page_total_quantity == 10

    def test_from_dict_minimal(self) -> None:
        """Test from_dict with minimal data."""
        data = {"mimeTypeIdentifier": "PDF"}
        option = DocumentDownloadOption.from_dict(data)
        assert option.mime_type_identifier == "PDF"
        assert option.download_url is None
        assert option.page_total_quantity is None

    def test_from_dict_empty(self) -> None:
        """Test from_dict with empty dictionary."""
        option = DocumentDownloadOption.from_dict({})
        assert option.mime_type_identifier is None
        assert option.download_url is None
        assert option.page_total_quantity is None


class TestDocumentDownloadOptionToDict:
    """Tests for DocumentDownloadOption.to_dict method."""

    def test_to_dict_complete(
        self, sample_download_option_dict: Dict[str, Any]
    ) -> None:
        """Test to_dict with complete data."""
        option = DocumentDownloadOption.from_dict(sample_download_option_dict)
        result = option.to_dict()
        assert result["mimeTypeIdentifier"] == "PDF"
        assert (
            result["downloadUrl"]
            == "https://api.test.uspto.gov/api/v1/download/applications/13815942/M98QOH0NWFYTX17.pdf"
        )
        assert result["pageTotalQuantity"] == 10

    def test_to_dict_filters_none(self) -> None:
        """Test to_dict filters out None values."""
        option = DocumentDownloadOption(mime_type_identifier="PDF")
        result = option.to_dict()
        assert "mimeTypeIdentifier" in result
        assert "downloadUrl" not in result
        assert "pageTotalQuantity" not in result


class TestPetitionDecisionDocumentFromDict:
    """Tests for PetitionDecisionDocument.from_dict method."""

    def test_from_dict_complete(self, sample_document_dict: Dict[str, Any]) -> None:
        """Test from_dict with complete data."""
        doc = PetitionDecisionDocument.from_dict(sample_document_dict)
        assert doc.application_number_text == "13815942"
        assert doc.document_identifier == "M98QOH0NWFYTX17"
        assert doc.document_code == "PETDEC"
        assert doc.document_code_description_text == "Petition Decision"
        assert doc.document_direction_category == "OUTGOING"
        assert len(doc.download_option_bag) == 2
        assert doc.download_option_bag[0].mime_type_identifier == "PDF"
        assert doc.download_option_bag[1].mime_type_identifier == "XML"
        # Check datetime parsing
        assert doc.official_date is not None
        assert isinstance(doc.official_date, datetime)
        assert doc.official_date.tzinfo is not None

    def test_from_dict_empty_download_options(self) -> None:
        """Test from_dict with empty download options."""
        data = {
            "applicationNumberText": "12345678",
            "documentCode": "TEST",
            "downloadOptionBag": [],
        }
        doc = PetitionDecisionDocument.from_dict(data)
        assert doc.application_number_text == "12345678"
        assert len(doc.download_option_bag) == 0

    def test_from_dict_missing_download_options(self) -> None:
        """Test from_dict without downloadOptionBag key."""
        data = {"applicationNumberText": "12345678", "documentCode": "TEST"}
        doc = PetitionDecisionDocument.from_dict(data)
        assert len(doc.download_option_bag) == 0


class TestPetitionDecisionDocumentToDict:
    """Tests for PetitionDecisionDocument.to_dict method."""

    def test_to_dict_complete(self, sample_document_dict: Dict[str, Any]) -> None:
        """Test to_dict with complete data."""
        doc = PetitionDecisionDocument.from_dict(sample_document_dict)
        result = doc.to_dict()
        assert result["applicationNumberText"] == "13815942"
        assert result["documentIdentifier"] == "M98QOH0NWFYTX17"
        assert result["documentCode"] == "PETDEC"
        assert "downloadOptionBag" in result
        assert len(result["downloadOptionBag"]) == 2


class TestPetitionDecisionFromDict:
    """Tests for PetitionDecision.from_dict method."""

    def test_from_dict_complete(
        self, sample_petition_decision_dict: Dict[str, Any]
    ) -> None:
        """Test from_dict with complete data."""
        decision = PetitionDecision.from_dict(sample_petition_decision_dict)

        # Check string fields
        assert decision.application_number_text == "17765301"
        assert (
            decision.petition_decision_record_identifier
            == "9f1a4a2b-eee1-58ec-a3aa-167c4075aed4"
        )
        assert decision.decision_type_code == "C"
        assert decision.decision_type_code_description_text == "DENIED"
        assert decision.final_deciding_office_name == "OFFICE OF PETITIONS"
        assert decision.first_applicant_name == "SHANGSHUI SMARTECH LTD."
        assert (
            decision.invention_title
            == "Impeller Assembly For Dispersing Solid In Liquid"
        )
        assert decision.business_entity_status_category == "Regular Undiscounted"
        assert decision.group_art_unit_number == "1774"
        assert decision.technology_center == "1700"
        assert decision.prosecution_status_code == "160"
        assert decision.action_taken_by_court_name == "None"

        # Check numeric fields
        assert decision.customer_number == 48980
        assert decision.decision_petition_type_code == 652

        # Check boolean fields
        assert decision.first_inventor_to_file_indicator is True
        assert decision.court_action_indicator is False

        # Check date fields
        assert decision.decision_date == date(2025, 1, 23)
        assert decision.petition_mail_date == date(2024, 11, 12)

        # Check datetime fields
        assert decision.last_ingestion_datetime is not None
        assert isinstance(decision.last_ingestion_datetime, datetime)

        # Check list fields
        assert len(decision.inventor_bag) == 4
        assert "Qiao Shi" in decision.inventor_bag
        assert decision.first_inventor_name == "Qiao Shi"

        assert len(decision.petition_issue_considered_text_bag) == 1
        assert (
            "Make special: Patent Prosecution Highway"
            in decision.petition_issue_considered_text_bag
        )

        assert len(decision.rule_bag) == 1
        assert "37 CFR 1.102(a)" in decision.rule_bag

        assert len(decision.statute_bag) == 0
        assert len(decision.document_bag) == 0

    def test_from_dict_with_patent_number(self) -> None:
        """Test from_dict with patent number."""
        data = {
            "applicationNumberText": "12345678",
            "patentNumber": "11000000",
            "decisionDate": "2022-01-01",
        }
        decision = PetitionDecision.from_dict(data)
        assert decision.patent_number == "11000000"

    def test_from_dict_with_documents(
        self, sample_document_dict: Dict[str, Any]
    ) -> None:
        """Test from_dict with document bag."""
        data = {
            "applicationNumberText": "13815942",
            "documentBag": [sample_document_dict],
        }
        decision = PetitionDecision.from_dict(data)
        assert len(decision.document_bag) == 1
        assert decision.document_bag[0].document_code == "PETDEC"

    def test_from_dict_empty_lists(self) -> None:
        """Test from_dict properly handles empty lists."""
        data = {
            "applicationNumberText": "12345678",
            "inventorBag": [],
            "petitionIssueConsideredTextBag": [],
            "statuteBag": [],
            "ruleBag": [],
            "documentBag": [],
        }
        decision = PetitionDecision.from_dict(data)
        assert len(decision.inventor_bag) == 0
        assert decision.first_inventor_name is None
        assert len(decision.petition_issue_considered_text_bag) == 0
        assert len(decision.statute_bag) == 0
        assert len(decision.rule_bag) == 0
        assert len(decision.document_bag) == 0

    def test_from_dict_minimal(self) -> None:
        """Test from_dict with minimal data."""
        data = {"applicationNumberText": "12345678"}
        decision = PetitionDecision.from_dict(data)
        assert decision.application_number_text == "12345678"
        assert decision.patent_number is None
        assert decision.decision_date is None
        assert len(decision.inventor_bag) == 0

    def test_from_dict_invalid_inventor_bag_type(self) -> None:
        """Test from_dict when inventorBag is not a list (defensive check)."""
        data = {
            "applicationNumberText": "12345678",
            "inventorBag": "Not a list",  # Invalid type
        }
        decision = PetitionDecision.from_dict(data)
        assert len(decision.inventor_bag) == 0  # Should default to empty list

    def test_from_dict_invalid_petition_issues_type(self) -> None:
        """Test from_dict when petitionIssueConsideredTextBag is not a list."""
        data = {
            "applicationNumberText": "12345678",
            "petitionIssueConsideredTextBag": {"not": "a list"},  # Invalid type
        }
        decision = PetitionDecision.from_dict(data)
        assert len(decision.petition_issue_considered_text_bag) == 0

    def test_from_dict_invalid_statute_bag_type(self) -> None:
        """Test from_dict when statuteBag is not a list."""
        data = {
            "applicationNumberText": "12345678",
            "statuteBag": 12345,  # Invalid type
        }
        decision = PetitionDecision.from_dict(data)
        assert len(decision.statute_bag) == 0

    def test_from_dict_invalid_rule_bag_type(self) -> None:
        """Test from_dict when ruleBag is not a list."""
        data = {
            "applicationNumberText": "12345678",
            "ruleBag": None,  # Invalid type
        }
        decision = PetitionDecision.from_dict(data)
        assert len(decision.rule_bag) == 0


class TestPetitionDecisionToDict:
    """Tests for PetitionDecision.to_dict method."""

    def test_to_dict_complete(
        self, sample_petition_decision_dict: Dict[str, Any]
    ) -> None:
        """Test to_dict with complete data."""
        decision = PetitionDecision.from_dict(sample_petition_decision_dict)
        result = decision.to_dict()

        # Check that all major fields are present
        assert result["applicationNumberText"] == "17765301"
        assert (
            result["petitionDecisionRecordIdentifier"]
            == "9f1a4a2b-eee1-58ec-a3aa-167c4075aed4"
        )
        assert result["decisionTypeCode"] == "C"
        assert result["decisionDate"] == "2025-01-23"
        assert result["petitionMailDate"] == "2024-11-12"
        assert result["inventorBag"] == [
            "Qiao Shi",
            "Shujuan Bai",
            "Tongzhu Li",
            "Quanxun Ou",
        ]
        assert result["ruleBag"] == ["37 CFR 1.102(a)"]

    def test_to_dict_filters_none_and_empty_lists(self) -> None:
        """Test to_dict filters out None values and empty lists."""
        decision = PetitionDecision(
            application_number_text="12345678",
            patent_number=None,
            inventor_bag=[],
        )
        result = decision.to_dict()
        assert "applicationNumberText" in result
        assert "patentNumber" not in result
        assert "inventorBag" not in result


class TestPetitionDecisionResponseFromDict:
    """Tests for PetitionDecisionResponse.from_dict method."""

    def test_from_dict_complete(
        self, sample_petition_response_dict: Dict[str, Any]
    ) -> None:
        """Test from_dict with complete data."""
        response = PetitionDecisionResponse.from_dict(sample_petition_response_dict)
        assert response.count == 1
        assert response.request_identifier == "01f0c175-a9e7-4f2d-9781-9ba6c2203b51"
        assert len(response.petition_decision_data_bag) == 1
        assert (
            response.petition_decision_data_bag[0].application_number_text == "17765301"
        )

    def test_from_dict_empty(self) -> None:
        """Test from_dict with empty data."""
        response = PetitionDecisionResponse.from_dict({})
        assert response.count is None
        assert response.request_identifier is None
        assert len(response.petition_decision_data_bag) == 0

    def test_from_dict_multiple_decisions(self) -> None:
        """Test from_dict with multiple decisions."""
        data = {
            "count": 2,
            "requestIdentifier": "test-id",
            "petitionDecisionDataBag": [
                {"applicationNumberText": "12345678"},
                {"applicationNumberText": "87654321"},
            ],
        }
        response = PetitionDecisionResponse.from_dict(data)
        assert response.count == 2
        assert len(response.petition_decision_data_bag) == 2
        assert (
            response.petition_decision_data_bag[0].application_number_text == "12345678"
        )
        assert (
            response.petition_decision_data_bag[1].application_number_text == "87654321"
        )


class TestPetitionDecisionResponseToDict:
    """Tests for PetitionDecisionResponse.to_dict method."""

    def test_to_dict_complete(
        self, sample_petition_response_dict: Dict[str, Any]
    ) -> None:
        """Test to_dict with complete data."""
        response = PetitionDecisionResponse.from_dict(sample_petition_response_dict)
        result = response.to_dict()
        assert result["count"] == 1
        assert result["requestIdentifier"] == "01f0c175-a9e7-4f2d-9781-9ba6c2203b51"
        assert "petitionDecisionDataBag" in result
        assert len(result["petitionDecisionDataBag"]) == 1


class TestPetitionDecisionDownloadResponseFromDict:
    """Tests for PetitionDecisionDownloadResponse.from_dict method."""

    def test_from_dict_complete(
        self, sample_download_response_dict: Dict[str, Any]
    ) -> None:
        """Test from_dict with complete data."""
        response = PetitionDecisionDownloadResponse.from_dict(
            sample_download_response_dict
        )
        assert len(response.petition_decision_data) == 1
        assert response.petition_decision_data[0].application_number_text == "17765301"

    def test_from_dict_empty(self) -> None:
        """Test from_dict with empty data."""
        response = PetitionDecisionDownloadResponse.from_dict({})
        assert len(response.petition_decision_data) == 0


class TestPetitionDecisionDownloadResponseToDict:
    """Tests for PetitionDecisionDownloadResponse.to_dict method."""

    def test_to_dict_complete(
        self, sample_download_response_dict: Dict[str, Any]
    ) -> None:
        """Test to_dict with complete data."""
        response = PetitionDecisionDownloadResponse.from_dict(
            sample_download_response_dict
        )
        result = response.to_dict()
        assert "petitionDecisionData" in result
        assert len(result["petitionDecisionData"]) == 1


class TestDecisionTypeCodeEnum:
    """Tests for DecisionTypeCode enum."""

    def test_enum_values(self) -> None:
        """Test enum has expected values."""
        assert DecisionTypeCode.DENIED == DecisionTypeCode.DENIED
        assert DecisionTypeCode.C == DecisionTypeCode.C
        # assert DecisionTypeCode.DISMISSED == DecisionTypeCode.DISMISSED
        # assert DecisionTypeCode.GRANTED == DecisionTypeCode.GRANTED

    def test_missing_case_insensitive(self) -> None:
        """Test _missing_ handles case-insensitive lookup."""
        assert DecisionTypeCode("c") == DecisionTypeCode.DENIED
        assert DecisionTypeCode("C") == DecisionTypeCode.DENIED
        with pytest.raises(ValueError):
            DecisionTypeCode("not_a_real_code")
        # assert DecisionTypeCode("DISMISSED") == DecisionTypeCode.DISMISSED
        # assert DecisionTypeCode("granted") == DecisionTypeCode.GRANTED
        # assert DecisionTypeCode("GRANTED") == DecisionTypeCode.GRANTED
        # assert DecisionTypeCode("dismissed") == DecisionTypeCode.DISMISSED


class TestDocumentDirectionCategoryEnum:
    """Tests for DocumentDirectionCategory enum."""

    def test_enum_values(self) -> None:
        """Test enum has expected values."""
        assert DocumentDirectionCategory.INCOMING == DocumentDirectionCategory.INCOMING
        assert DocumentDirectionCategory.OUTGOING == DocumentDirectionCategory.OUTGOING

    def test_missing_case_insensitive(self) -> None:
        """Test _missing_ handles case-insensitive lookup."""
        assert (
            DocumentDirectionCategory("incoming") == DocumentDirectionCategory.INCOMING
        )
        assert (
            DocumentDirectionCategory("outgoing") == DocumentDirectionCategory.OUTGOING
        )
        with pytest.raises(ValueError):
            DocumentDirectionCategory("not_a_real_category")
