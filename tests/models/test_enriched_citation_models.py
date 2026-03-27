"""Tests for the enriched_citations models.

This module contains comprehensive tests for all classes in pyUSPTO.models.enriched_citations.
"""

from datetime import datetime
from typing import Any

import pytest

from pyUSPTO.models.enriched_citations import (
    CitationCategoryCode,
    EnrichedCitation,
    EnrichedCitationFieldsResponse,
    EnrichedCitationResponse,
)


@pytest.fixture
def sample_enriched_citation_dict() -> dict[str, Any]:
    """Provide a sample enriched citation dictionary matching the API response."""
    return {
        "relatedClaimNumberText": "1,7",
        "officeActionDate": "2019-10-21T00:00:00",
        "createUserIdentifier": "ETL_SYS",
        "applicantCitedExaminerReferenceIndicator": False,
        "kindCode": "A1",
        "nplIndicator": False,
        "workGroupNumber": "2830",
        "patentApplicationNumber": "15739603",
        "officeActionCategory": "CTNF",
        "inventorNameText": "Supriya; Amrit",
        "groupArtUnitNumber": "2837",
        "qualitySummaryText": "AOK",
        "createDateTime": "2026-03-02T21:36:52",
        "techCenter": "2800",
        "citedDocumentIdentifier": "US 20190165601 A1",
        "countryCode": "US",
        "passageLocationText": [
            "c. 112|figure 3|claim 9|claims 1-23|c. 103|claim 1"
        ],
        "obsoleteDocumentIdentifier": "K1V5RMZ8RXEAPX0",
        "id": "d7e95803517f677b3875dc476a61a817",
        "citationCategoryCode": "Y",
        "examinerCitedReferenceIndicator": True,
        "publicationNumber": "20190165601",
    }


@pytest.fixture
def sample_enriched_citation_response_dict(
    sample_enriched_citation_dict: dict[str, Any],
) -> dict[str, Any]:
    """Provide a sample response dictionary with the outer envelope."""
    return {
        "response": {
            "start": 0,
            "numFound": 3,
            "docs": [
                sample_enriched_citation_dict,
                {
                    "id": "06cce55e4608f90c57ff7fdf2d6cc031",
                    "patentApplicationNumber": "15739603",
                    "citationCategoryCode": "Y",
                },
                {
                    "id": "fa9ab8672e7cdc4f08b3ae43f8dd794b",
                    "patentApplicationNumber": "15739603",
                    "citationCategoryCode": "X",
                },
            ],
        }
    }


@pytest.fixture
def sample_fields_response_dict() -> dict[str, Any]:
    """Provide a sample fields response dictionary."""
    return {
        "apiKey": "enriched_cited_reference_metadata",
        "apiVersionNumber": "v3",
        "apiUrl": "https://api.uspto.gov/api/v1/patent/oa/enriched_cited_reference_metadata/v3/fields",
        "apiDocumentationUrl": "https://data.uspto.gov/swagger/index.html?urls.primaryName=USPTO%20Enriched%20Citation%20API%20v3",
        "apiStatus": "PUBLISHED",
        "fieldCount": 22,
        "fields": [
            "officeActionDate",
            "relatedClaimNumberText",
            "applicantCitedExaminerReferenceIndicator",
            "createUserIdentifier",
            "kindCode",
            "nplIndicator",
            "workGroupNumber",
            "officeActionCategory",
            "patentApplicationNumber",
            "inventorNameText",
            "groupArtUnitNumber",
            "qualitySummaryText",
            "createDateTime",
            "techCenter",
            "citedDocumentIdentifier",
            "countryCode",
            "passageLocationText",
            "obsoleteDocumentIdentifier",
            "citationCategoryCode",
            "id",
            "examinerCitedReferenceIndicator",
            "publicationNumber",
        ],
        "lastDataUpdatedDate": "2024-07-11 11:33:41.0",
    }


class TestCitationCategoryCode:
    """Tests for CitationCategoryCode enum."""

    def test_standard_values(self) -> None:
        """Test that standard citation category codes are valid."""
        assert CitationCategoryCode("X") == CitationCategoryCode.X
        assert CitationCategoryCode("Y") == CitationCategoryCode.Y
        assert CitationCategoryCode("A") == CitationCategoryCode.A
        assert CitationCategoryCode("E") == CitationCategoryCode.E
        assert CitationCategoryCode("L") == CitationCategoryCode.L
        assert CitationCategoryCode("O") == CitationCategoryCode.O
        assert CitationCategoryCode("T") == CitationCategoryCode.T
        assert CitationCategoryCode("P") == CitationCategoryCode.P
        assert CitationCategoryCode("D") == CitationCategoryCode.D

    def test_ampersand(self) -> None:
        """Test ampersand citation category code."""
        assert CitationCategoryCode("&") == CitationCategoryCode.AMPERSAND
        assert CitationCategoryCode.AMPERSAND.value == "&"

    def test_case_insensitive(self) -> None:
        """Test case-insensitive lookup via _missing_."""
        assert CitationCategoryCode("x") == CitationCategoryCode.X
        assert CitationCategoryCode("y") == CitationCategoryCode.Y
        assert CitationCategoryCode("a") == CitationCategoryCode.A

    def test_invalid_value_raises(self) -> None:
        """Test that invalid values raise ValueError."""
        with pytest.raises(ValueError):
            CitationCategoryCode("Z")
        with pytest.raises(ValueError):
            CitationCategoryCode("invalid")


class TestEnrichedCitationFromDict:
    """Tests for EnrichedCitation.from_dict method."""

    def test_from_dict_complete(
        self, sample_enriched_citation_dict: dict[str, Any]
    ) -> None:
        """Test from_dict with complete data."""
        citation = EnrichedCitation.from_dict(sample_enriched_citation_dict)

        # Check string fields
        assert citation.id == "d7e95803517f677b3875dc476a61a817"
        assert citation.patent_application_number == "15739603"
        assert citation.cited_document_identifier == "US 20190165601 A1"
        assert citation.publication_number == "20190165601"
        assert citation.kind_code == "A1"
        assert citation.country_code == "US"
        assert citation.inventor_name_text == "Supriya; Amrit"
        assert citation.office_action_category == "CTNF"
        assert citation.citation_category_code == "Y"
        assert citation.related_claim_number_text == "1,7"
        assert citation.work_group_number == "2830"
        assert citation.group_art_unit_number == "2837"
        assert citation.tech_center == "2800"
        assert citation.quality_summary_text == "AOK"
        assert citation.obsolete_document_identifier == "K1V5RMZ8RXEAPX0"
        assert citation.create_user_identifier == "ETL_SYS"

        # Check boolean fields
        assert citation.examiner_cited_reference_indicator is True
        assert citation.applicant_cited_examiner_reference_indicator is False
        assert citation.npl_indicator is False

        # Check datetime fields
        assert citation.office_action_date is not None
        assert isinstance(citation.office_action_date, datetime)
        assert citation.create_date_time is not None
        assert isinstance(citation.create_date_time, datetime)

        # Check list fields
        assert len(citation.passage_location_text) == 1
        assert "c. 112|figure 3|claim 9" in citation.passage_location_text[0]

    def test_from_dict_minimal(self) -> None:
        """Test from_dict with minimal data (only id)."""
        data = {"id": "test-id-123"}
        citation = EnrichedCitation.from_dict(data)
        assert citation.id == "test-id-123"
        assert citation.patent_application_number is None
        assert citation.cited_document_identifier is None
        assert citation.office_action_date is None
        assert citation.examiner_cited_reference_indicator is None
        assert len(citation.passage_location_text) == 0

    def test_from_dict_empty(self) -> None:
        """Test from_dict with empty dictionary."""
        citation = EnrichedCitation.from_dict({})
        assert citation.id == ""
        assert citation.patent_application_number is None
        assert len(citation.passage_location_text) == 0

    def test_from_dict_passage_location_not_list(self) -> None:
        """Test from_dict when passageLocationText is not a list (defensive check)."""
        data = {
            "id": "test-id",
            "passageLocationText": "Not a list",
        }
        citation = EnrichedCitation.from_dict(data)
        assert len(citation.passage_location_text) == 0

    def test_from_dict_passage_location_none(self) -> None:
        """Test from_dict when passageLocationText is None."""
        data = {
            "id": "test-id",
            "passageLocationText": None,
        }
        citation = EnrichedCitation.from_dict(data)
        assert len(citation.passage_location_text) == 0

    def test_from_dict_empty_strings(self) -> None:
        """Test from_dict with empty string values."""
        data = {
            "id": "test-id",
            "kindCode": "",
            "countryCode": "",
            "publicationNumber": "",
        }
        citation = EnrichedCitation.from_dict(data)
        assert citation.kind_code == ""
        assert citation.country_code == ""
        assert citation.publication_number == ""


class TestEnrichedCitationToDict:
    """Tests for EnrichedCitation.to_dict method."""

    def test_to_dict_complete(
        self, sample_enriched_citation_dict: dict[str, Any]
    ) -> None:
        """Test to_dict with complete data."""
        citation = EnrichedCitation.from_dict(sample_enriched_citation_dict)
        result = citation.to_dict()

        assert result["id"] == "d7e95803517f677b3875dc476a61a817"
        assert result["patentApplicationNumber"] == "15739603"
        assert result["citedDocumentIdentifier"] == "US 20190165601 A1"
        assert result["citationCategoryCode"] == "Y"
        assert result["examinerCitedReferenceIndicator"] is True
        assert result["nplIndicator"] is False
        assert "passageLocationText" in result
        assert len(result["passageLocationText"]) == 1

    def test_to_dict_filters_none_and_empty_lists(self) -> None:
        """Test to_dict filters out None values and empty lists."""
        citation = EnrichedCitation(
            id="test-id",
            patent_application_number="15739603",
            cited_document_identifier=None,
            passage_location_text=[],
        )
        result = citation.to_dict()
        assert "id" in result
        assert "patentApplicationNumber" in result
        assert "citedDocumentIdentifier" not in result
        assert "passageLocationText" not in result


class TestEnrichedCitationResponseFromDict:
    """Tests for EnrichedCitationResponse.from_dict method."""

    def test_from_dict_with_envelope(
        self, sample_enriched_citation_response_dict: dict[str, Any]
    ) -> None:
        """Test from_dict unwraps the outer 'response' envelope."""
        response = EnrichedCitationResponse.from_dict(
            sample_enriched_citation_response_dict
        )
        assert response.num_found == 3
        assert response.start == 0
        assert len(response.docs) == 3
        assert response.docs[0].id == "d7e95803517f677b3875dc476a61a817"
        assert response.docs[1].id == "06cce55e4608f90c57ff7fdf2d6cc031"
        assert response.docs[2].id == "fa9ab8672e7cdc4f08b3ae43f8dd794b"

    def test_from_dict_without_envelope(self) -> None:
        """Test from_dict works when already unwrapped."""
        data = {
            "start": 10,
            "numFound": 50,
            "docs": [
                {"id": "abc123", "patentApplicationNumber": "12345678"},
            ],
        }
        response = EnrichedCitationResponse.from_dict(data)
        assert response.num_found == 50
        assert response.start == 10
        assert len(response.docs) == 1

    def test_count_property_returns_num_found(self) -> None:
        """Test that count property returns num_found for pagination compatibility."""
        response = EnrichedCitationResponse(num_found=42, start=0)
        assert response.count == 42

    def test_from_dict_empty(self) -> None:
        """Test from_dict with empty data."""
        response = EnrichedCitationResponse.from_dict({})
        assert response.num_found == 0
        assert response.start == 0
        assert len(response.docs) == 0

    def test_from_dict_empty_docs(self) -> None:
        """Test from_dict with empty docs list."""
        data = {"response": {"start": 0, "numFound": 0, "docs": []}}
        response = EnrichedCitationResponse.from_dict(data)
        assert response.num_found == 0
        assert len(response.docs) == 0

    def test_from_dict_include_raw_data(
        self, sample_enriched_citation_response_dict: dict[str, Any]
    ) -> None:
        """Test from_dict with include_raw_data=True stores raw JSON."""
        response = EnrichedCitationResponse.from_dict(
            sample_enriched_citation_response_dict, include_raw_data=True
        )
        assert response.raw_data is not None
        assert "d7e95803517f677b3875dc476a61a817" in response.raw_data

    def test_from_dict_include_raw_data_false(self) -> None:
        """Test from_dict with include_raw_data=False (default) has no raw data."""
        data = {"response": {"start": 0, "numFound": 0, "docs": []}}
        response = EnrichedCitationResponse.from_dict(data)
        assert response.raw_data is None


class TestEnrichedCitationResponseToDict:
    """Tests for EnrichedCitationResponse.to_dict method."""

    def test_to_dict_wraps_in_envelope(
        self, sample_enriched_citation_response_dict: dict[str, Any]
    ) -> None:
        """Test to_dict wraps output in 'response' envelope."""
        response = EnrichedCitationResponse.from_dict(
            sample_enriched_citation_response_dict
        )
        result = response.to_dict()
        assert "response" in result
        assert result["response"]["numFound"] == 3
        assert result["response"]["start"] == 0
        assert len(result["response"]["docs"]) == 3


class TestEnrichedCitationFieldsResponseFromDict:
    """Tests for EnrichedCitationFieldsResponse.from_dict method."""

    def test_from_dict_complete(
        self, sample_fields_response_dict: dict[str, Any]
    ) -> None:
        """Test from_dict with complete data."""
        response = EnrichedCitationFieldsResponse.from_dict(
            sample_fields_response_dict
        )
        assert response.api_key == "enriched_cited_reference_metadata"
        assert response.api_version_number == "v3"
        assert response.api_status == "PUBLISHED"
        assert response.field_count == 22
        assert len(response.fields) == 22
        assert "officeActionDate" in response.fields
        assert "citedDocumentIdentifier" in response.fields
        assert response.last_data_updated_date == "2024-07-11 11:33:41.0"
        assert response.api_url is not None
        assert response.api_documentation_url is not None

    def test_from_dict_empty(self) -> None:
        """Test from_dict with empty data."""
        response = EnrichedCitationFieldsResponse.from_dict({})
        assert response.api_key is None
        assert response.api_version_number is None
        assert response.field_count == 0
        assert len(response.fields) == 0

    def test_from_dict_fields_not_list(self) -> None:
        """Test from_dict when fields is not a list (defensive check)."""
        data = {"fields": "not a list", "fieldCount": 1}
        response = EnrichedCitationFieldsResponse.from_dict(data)
        assert len(response.fields) == 0


class TestEnrichedCitationFieldsResponseToDict:
    """Tests for EnrichedCitationFieldsResponse.to_dict method."""

    def test_to_dict_complete(
        self, sample_fields_response_dict: dict[str, Any]
    ) -> None:
        """Test to_dict with complete data."""
        response = EnrichedCitationFieldsResponse.from_dict(
            sample_fields_response_dict
        )
        result = response.to_dict()
        assert result["apiKey"] == "enriched_cited_reference_metadata"
        assert result["apiVersionNumber"] == "v3"
        assert result["fieldCount"] == 22
        assert len(result["fields"]) == 22

    def test_to_dict_filters_none_and_empty_lists(self) -> None:
        """Test to_dict filters out None values and empty lists."""
        response = EnrichedCitationFieldsResponse(
            api_key="test",
            api_version_number=None,
            fields=[],
        )
        result = response.to_dict()
        assert "apiKey" in result
        assert "apiVersionNumber" not in result
        assert "fields" not in result
