"""Tests for the oa_citations models.

This module contains comprehensive tests for all classes in pyUSPTO.models.oa_citations.
"""

import warnings
from typing import Any

import pytest

from pyUSPTO.models.oa_citations import (
    OACitationRecord,
    OACitationsFieldsResponse,
    OACitationsResponse,
)
from pyUSPTO.warnings import USPTODateParseWarning


# --- Fixtures ---


@pytest.fixture
def sample_record_dict() -> dict[str, Any]:
    """Sample record from real API data."""
    return {
        "applicantCitedExaminerReferenceIndicator": False,
        "createUserIdentifier": "ETL_SYS",
        "workGroup": "2850",
        "officeActionCitationReferenceIndicator": True,
        "referenceIdentifier": "Itagaki; Takeshi US 20150044531 A1 ",
        "patentApplicationNumber": "17519936",
        "actionTypeCategory": "rejected",
        "legalSectionCode": "103",
        "groupArtUnitNumber": "2858",
        "createDateTime": "2025-07-03T13:51:37",
        "techCenter": "2800",
        "obsoleteDocumentIdentifier": "LD1Q0FKGXBLUEX4",
        "parsedReferenceIdentifier": "20150044531",
        "id": "90d4b51ab322a638b1327494a7129975",
        "examinerCitedReferenceIndicator": True,
    }


@pytest.fixture
def sample_record_dict_minimal() -> dict[str, Any]:
    """Sample record with mostly empty/default values."""
    return {
        "applicantCitedExaminerReferenceIndicator": False,
        "createUserIdentifier": "ETL_SYS",
        "workGroup": "3660",
        "officeActionCitationReferenceIndicator": False,
        "referenceIdentifier": "",
        "patentApplicationNumber": "16845502",
        "actionTypeCategory": "rejected",
        "legalSectionCode": "",
        "groupArtUnitNumber": "3663",
        "createDateTime": "2025-07-04T20:23:09",
        "techCenter": "3600",
        "obsoleteDocumentIdentifier": "KQ6WYGGVLDFLYX4",
        "parsedReferenceIdentifier": "",
        "id": "ba27780c738055eed0332b28b78ef6d6",
        "examinerCitedReferenceIndicator": False,
    }


@pytest.fixture
def sample_response_dict(sample_record_dict: dict[str, Any]) -> dict[str, Any]:
    """Sample full API response envelope."""
    return {
        "response": {
            "start": 0,
            "numFound": 133157634,
            "docs": [sample_record_dict],
        }
    }


@pytest.fixture
def sample_fields_response_dict() -> dict[str, Any]:
    """Sample fields endpoint response."""
    return {
        "apiKey": "oa_citations",
        "apiVersionNumber": "v2",
        "apiUrl": "https://api.uspto.gov/api/v1/patent/oa/oa_citations/v2/fields",
        "apiDocumentationUrl": "arn:aws:iam::831714700926:role/uspto-dev/uspto-dh-p-prod-service-role-1",
        "apiStatus": "PUBLISHED",
        "fieldCount": 16,
        "fields": [
            "applicantCitedExaminerReferenceIndicator",
            "createUserIdentifier",
            "workGroup",
            "officeActionCitationReferenceIndicator",
            "referenceIdentifier",
            "actionTypeCategory",
            "patentApplicationNumber",
            "legalSectionCode",
            "groupArtUnitNumber",
            "createDateTime",
            "techCenter",
            "paragraphNumber",
            "obsoleteDocumentIdentifier",
            "parsedReferenceIdentifier",
            "id",
            "examinerCitedReferenceIndicator",
        ],
        "lastDataUpdatedDate": "2019-06-26 11:20:17.0",
    }


# --- TestOACitationRecordFromDict ---


class TestOACitationRecordFromDict:
    def test_complete_record(self, sample_record_dict: dict[str, Any]) -> None:
        record = OACitationRecord.from_dict(sample_record_dict)
        assert record.id == "90d4b51ab322a638b1327494a7129975"
        assert record.patent_application_number == "17519936"
        assert record.action_type_category == "rejected"
        assert record.legal_section_code == "103"
        assert record.reference_identifier == "Itagaki; Takeshi US 20150044531 A1 "
        assert record.parsed_reference_identifier == "20150044531"
        assert record.group_art_unit_number == "2858"
        assert record.work_group == "2850"
        assert record.tech_center == "2800"
        assert record.applicant_cited_examiner_reference_indicator is False
        assert record.examiner_cited_reference_indicator is True
        assert record.office_action_citation_reference_indicator is True
        assert record.create_user_identifier == "ETL_SYS"
        assert record.obsolete_document_identifier == "LD1Q0FKGXBLUEX4"
        assert record.create_date_time is not None
        assert record.create_date_time.year == 2025
        assert record.create_date_time.month == 7
        assert record.create_date_time.day == 3

    def test_minimal_record(
        self, sample_record_dict_minimal: dict[str, Any]
    ) -> None:
        record = OACitationRecord.from_dict(sample_record_dict_minimal)
        assert record.id == "ba27780c738055eed0332b28b78ef6d6"
        assert record.patent_application_number == "16845502"
        assert record.action_type_category == "rejected"
        assert record.legal_section_code == ""
        assert record.reference_identifier == ""
        assert record.parsed_reference_identifier == ""
        assert record.examiner_cited_reference_indicator is False
        assert record.office_action_citation_reference_indicator is False

    def test_empty_dict(self) -> None:
        record = OACitationRecord.from_dict({})
        assert record.id == ""
        assert record.patent_application_number == ""
        assert record.action_type_category == ""
        assert record.legal_section_code == ""
        assert record.reference_identifier == ""
        assert record.parsed_reference_identifier == ""
        assert record.group_art_unit_number == ""
        assert record.work_group == ""
        assert record.tech_center == ""
        assert record.paragraph_number == ""
        assert record.applicant_cited_examiner_reference_indicator is None
        assert record.examiner_cited_reference_indicator is None
        assert record.office_action_citation_reference_indicator is None
        assert record.create_user_identifier == ""
        assert record.create_date_time is None
        assert record.obsolete_document_identifier == ""

    def test_bad_datetime(self) -> None:
        data = {"createDateTime": "not-a-date"}
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", USPTODateParseWarning)
            record = OACitationRecord.from_dict(data)
        assert record.create_date_time is None


# --- TestOACitationRecordToDict ---


class TestOACitationRecordToDict:
    def test_roundtrip(self, sample_record_dict: dict[str, Any]) -> None:
        record = OACitationRecord.from_dict(sample_record_dict)
        result = record.to_dict()
        assert result["id"] == "90d4b51ab322a638b1327494a7129975"
        assert result["patentApplicationNumber"] == "17519936"
        assert result["actionTypeCategory"] == "rejected"
        assert result["legalSectionCode"] == "103"
        assert result["examinerCitedReferenceIndicator"] is True
        assert result["officeActionCitationReferenceIndicator"] is True
        assert result["applicantCitedExaminerReferenceIndicator"] is False
        assert "createDateTime" in result

    def test_none_filtering(self) -> None:
        record = OACitationRecord(id="test123")
        result = record.to_dict()
        assert result["id"] == "test123"
        assert "applicantCitedExaminerReferenceIndicator" not in result
        assert "examinerCitedReferenceIndicator" not in result
        assert "officeActionCitationReferenceIndicator" not in result
        assert "createDateTime" not in result


# --- TestOACitationsResponseFromDict ---


class TestOACitationsResponseFromDict:
    def test_complete_response(
        self, sample_response_dict: dict[str, Any]
    ) -> None:
        response = OACitationsResponse.from_dict(sample_response_dict)
        assert response.num_found == 133157634
        assert response.start == 0
        assert len(response.docs) == 1
        assert response.docs[0].id == "90d4b51ab322a638b1327494a7129975"

    def test_count_property(
        self, sample_response_dict: dict[str, Any]
    ) -> None:
        response = OACitationsResponse.from_dict(sample_response_dict)
        assert response.count == 133157634
        assert response.count == response.num_found

    def test_empty_response(self) -> None:
        response = OACitationsResponse.from_dict(
            {"response": {"start": 0, "numFound": 0, "docs": []}}
        )
        assert response.num_found == 0
        assert response.start == 0
        assert response.docs == []

    def test_multiple_records(
        self, sample_record_dict: dict[str, Any],
        sample_record_dict_minimal: dict[str, Any],
    ) -> None:
        data = {
            "response": {
                "start": 0,
                "numFound": 2,
                "docs": [sample_record_dict, sample_record_dict_minimal],
            }
        }
        response = OACitationsResponse.from_dict(data)
        assert len(response.docs) == 2
        assert response.docs[0].id == "90d4b51ab322a638b1327494a7129975"
        assert response.docs[1].id == "ba27780c738055eed0332b28b78ef6d6"

    def test_raw_data_toggle(
        self, sample_response_dict: dict[str, Any]
    ) -> None:
        response_no_raw = OACitationsResponse.from_dict(
            sample_response_dict, include_raw_data=False
        )
        assert response_no_raw.raw_data is None

        response_with_raw = OACitationsResponse.from_dict(
            sample_response_dict, include_raw_data=True
        )
        assert response_with_raw.raw_data is not None
        assert "90d4b51ab322a638b1327494a7129975" in response_with_raw.raw_data

    def test_pre_unwrapped_dict(self) -> None:
        inner = {"start": 5, "numFound": 10, "docs": []}
        response = OACitationsResponse.from_dict(inner)
        assert response.num_found == 10
        assert response.start == 5

    def test_non_list_docs(self) -> None:
        data = {"response": {"start": 0, "numFound": 0, "docs": "not-a-list"}}
        response = OACitationsResponse.from_dict(data)
        assert response.docs == []

    def test_non_dict_doc_items_filtered(self) -> None:
        data = {
            "response": {
                "start": 0,
                "numFound": 1,
                "docs": ["not-a-dict", 42, None],
            }
        }
        response = OACitationsResponse.from_dict(data)
        assert response.docs == []


# --- TestOACitationsResponseToDict ---


class TestOACitationsResponseToDict:
    def test_roundtrip(
        self, sample_response_dict: dict[str, Any]
    ) -> None:
        response = OACitationsResponse.from_dict(sample_response_dict)
        result = response.to_dict()
        assert "response" in result
        assert result["response"]["numFound"] == 133157634
        assert result["response"]["start"] == 0
        assert len(result["response"]["docs"]) == 1


# --- TestOACitationsFieldsResponseFromDict ---


class TestOACitationsFieldsResponseFromDict:
    def test_complete_fields_response(
        self, sample_fields_response_dict: dict[str, Any]
    ) -> None:
        response = OACitationsFieldsResponse.from_dict(sample_fields_response_dict)
        assert response.api_key == "oa_citations"
        assert response.api_version_number == "v2"
        assert response.api_status == "PUBLISHED"
        assert response.field_count == 16
        assert len(response.fields) == 16
        assert "patentApplicationNumber" in response.fields
        assert "examinerCitedReferenceIndicator" in response.fields
        assert response.last_data_updated_date == "2019-06-26 11:20:17.0"

    def test_empty_dict(self) -> None:
        response = OACitationsFieldsResponse.from_dict({})
        assert response.api_key is None
        assert response.api_version_number is None
        assert response.api_status is None
        assert response.field_count == 0
        assert response.fields == []

    def test_non_list_fields(self) -> None:
        response = OACitationsFieldsResponse.from_dict({"fields": "not-a-list"})
        assert response.fields == []


# --- TestOACitationsFieldsResponseToDict ---


class TestOACitationsFieldsResponseToDict:
    def test_roundtrip(
        self, sample_fields_response_dict: dict[str, Any]
    ) -> None:
        response = OACitationsFieldsResponse.from_dict(sample_fields_response_dict)
        result = response.to_dict()
        assert result["apiKey"] == "oa_citations"
        assert result["apiVersionNumber"] == "v2"
        assert result["apiStatus"] == "PUBLISHED"
        assert result["fieldCount"] == 16
        assert len(result["fields"]) == 16

    def test_none_filtering(self) -> None:
        response = OACitationsFieldsResponse(field_count=0)
        result = response.to_dict()
        assert "apiKey" not in result
        assert "apiVersionNumber" not in result
        assert "apiStatus" not in result
        assert "lastDataUpdatedDate" not in result
        assert result["fieldCount"] == 0
