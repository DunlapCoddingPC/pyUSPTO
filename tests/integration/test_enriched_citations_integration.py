"""
Integration tests for the USPTO Enriched Citations API client.

This module contains integration tests that make real API calls to the USPTO Enriched Citations API.
These tests are optional and are skipped by default unless the ENABLE_INTEGRATION_TESTS
environment variable is set to 'true'.
"""

import os

import pytest

from pyUSPTO.clients import EnrichedCitationsClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.enriched_citations import (
    EnrichedCitation,
    EnrichedCitationFieldsResponse,
    EnrichedCitationResponse,
)

# Skip all tests in this module unless ENABLE_INTEGRATION_TESTS is set to 'true'
pytestmark = pytest.mark.skipif(
    os.environ.get("ENABLE_INTEGRATION_TESTS", "").lower() != "true",
    reason="Integration tests are disabled. Set ENABLE_INTEGRATION_TESTS=true to enable.",
)


@pytest.fixture(scope="module")
def enriched_citations_client(config: USPTOConfig) -> EnrichedCitationsClient:
    """Create an EnrichedCitationsClient instance for integration tests."""
    return EnrichedCitationsClient(config=config)


class TestEnrichedCitationsSearch:
    """Integration tests for search_citations."""

    def test_search_by_application_number(
        self, enriched_citations_client: EnrichedCitationsClient
    ) -> None:
        """Test searching citations by application number."""
        response = enriched_citations_client.search_citations(
            patent_application_number_q="15061308",
        )
        assert isinstance(response, EnrichedCitationResponse)
        assert response.num_found > 0
        assert len(response.docs) > 0
        for doc in response.docs:
            assert doc.patent_application_number == "15061308"

    def test_search_by_citation_category_code(
        self, enriched_citations_client: EnrichedCitationsClient
    ) -> None:
        """Test searching citations by citation category code."""
        response = enriched_citations_client.search_citations(
            citation_category_code_q="X",
            rows=5,
        )
        assert isinstance(response, EnrichedCitationResponse)
        assert response.num_found > 0
        assert len(response.docs) <= 5
        for doc in response.docs:
            assert doc.citation_category_code == "X"

    def test_search_by_tech_center(
        self, enriched_citations_client: EnrichedCitationsClient
    ) -> None:
        """Test searching citations by technology center."""
        response = enriched_citations_client.search_citations(
            tech_center_q="2800",
            rows=5,
        )
        assert isinstance(response, EnrichedCitationResponse)
        assert response.num_found > 0
        for doc in response.docs:
            assert doc.tech_center == "2800"

    def test_search_by_group_art_unit(
        self, enriched_citations_client: EnrichedCitationsClient
    ) -> None:
        """Test searching citations by group art unit number."""
        response = enriched_citations_client.search_citations(
            group_art_unit_number_q="2837",
            rows=5,
        )
        assert isinstance(response, EnrichedCitationResponse)
        assert response.num_found > 0
        for doc in response.docs:
            assert doc.group_art_unit_number == "2837"

    def test_search_by_office_action_category(
        self, enriched_citations_client: EnrichedCitationsClient
    ) -> None:
        """Test searching citations by office action category."""
        response = enriched_citations_client.search_citations(
            office_action_category_q="CTNF",
            rows=5,
        )
        assert isinstance(response, EnrichedCitationResponse)
        assert response.num_found > 0
        for doc in response.docs:
            assert doc.office_action_category == "CTNF"

    def test_search_by_examiner_cited(
        self, enriched_citations_client: EnrichedCitationsClient
    ) -> None:
        """Test searching citations by examiner-cited indicator."""
        response = enriched_citations_client.search_citations(
            examiner_cited_q=True,
            rows=5,
        )
        assert isinstance(response, EnrichedCitationResponse)
        assert response.num_found > 0
        for doc in response.docs:
            assert doc.examiner_cited_reference_indicator is True

    def test_search_by_cited_document_identifier(
        self, enriched_citations_client: EnrichedCitationsClient
    ) -> None:
        """Test searching citations by cited document identifier."""
        response = enriched_citations_client.search_citations(
            cited_document_identifier_q="US 20190165601 A1",
            rows=5,
        )
        assert isinstance(response, EnrichedCitationResponse)
        assert response.num_found > 0
        for doc in response.docs:
            assert doc.cited_document_identifier == "US 20190165601 A1"

    def test_search_by_date_range(
        self, enriched_citations_client: EnrichedCitationsClient
    ) -> None:
        """Test searching citations by office action date range."""
        response = enriched_citations_client.search_citations(
            office_action_date_from_q="2019-01-01",
            office_action_date_to_q="2019-12-31",
            rows=5,
        )
        assert isinstance(response, EnrichedCitationResponse)
        assert response.num_found > 0
        for doc in response.docs:
            assert doc.office_action_date is not None
            assert doc.office_action_date.year == 2019

    def test_search_combined_params(
        self, enriched_citations_client: EnrichedCitationsClient
    ) -> None:
        """Test searching citations with multiple convenience params."""
        response = enriched_citations_client.search_citations(
            tech_center_q="2800",
            citation_category_code_q="Y",
            examiner_cited_q=True,
            rows=5,
        )
        assert isinstance(response, EnrichedCitationResponse)
        assert response.num_found > 0
        for doc in response.docs:
            assert doc.tech_center == "2800"
            assert doc.citation_category_code == "Y"
            assert doc.examiner_cited_reference_indicator is True

    def test_search_direct_query(
        self, enriched_citations_client: EnrichedCitationsClient
    ) -> None:
        """Test searching citations with a direct query string."""
        response = enriched_citations_client.search_citations(
            query="patentApplicationNumber:15739603",
        )
        assert isinstance(response, EnrichedCitationResponse)
        assert response.num_found > 0
        for doc in response.docs:
            assert doc.patent_application_number == "15739603"

    def test_search_with_sort(
        self, enriched_citations_client: EnrichedCitationsClient
    ) -> None:
        """Test searching citations with sort order."""
        response = enriched_citations_client.search_citations(
            tech_center_q="2800",
            sort="officeActionDate desc",
            rows=5,
        )
        assert isinstance(response, EnrichedCitationResponse)
        assert response.num_found > 0
        assert len(response.docs) <= 5

    def test_citation_fields_populated(
        self, enriched_citations_client: EnrichedCitationsClient
    ) -> None:
        """Test that returned citations have expected fields populated."""
        response = enriched_citations_client.search_citations(
            patent_application_number_q="15061308",
        )
        assert response.num_found > 0
        citation = response.docs[0]
        assert isinstance(citation, EnrichedCitation)
        assert citation.id != ""
        assert citation.patent_application_number == "15061308"
        assert citation.cited_document_identifier is not None
        assert citation.office_action_date is not None
        assert citation.office_action_category is not None
        assert citation.citation_category_code is not None
        assert citation.tech_center is not None
        assert citation.group_art_unit_number is not None


class TestEnrichedCitationsGetFields:
    """Integration tests for get_fields."""

    def test_get_fields(
        self, enriched_citations_client: EnrichedCitationsClient
    ) -> None:
        """Test retrieving API field metadata."""
        response = enriched_citations_client.get_fields()
        assert isinstance(response, EnrichedCitationFieldsResponse)
        assert response.api_status == "PUBLISHED"
        assert response.field_count == 22
        assert len(response.fields) == 22
        assert "patentApplicationNumber" in response.fields
        assert "citedDocumentIdentifier" in response.fields
        assert "officeActionDate" in response.fields
        assert "citationCategoryCode" in response.fields


class TestEnrichedCitationsPaginate:
    """Integration tests for paginate_citations."""

    def test_paginate_citations(
        self, enriched_citations_client: EnrichedCitationsClient
    ) -> None:
        """Test paginating through citation results."""
        count = 0
        for citation in enriched_citations_client.paginate_citations(
            tech_center_q="2800",
            rows=10,
        ):
            assert isinstance(citation, EnrichedCitation)
            assert citation.tech_center == "2800"
            count += 1
            if count >= 25:
                break

        assert count == 25
