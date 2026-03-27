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
    """
    Create an EnrichedCitationsClient instance for integration tests.

    Args:
        config: The configuration instance

    Returns:
        EnrichedCitationsClient: A client instance
    """
    return EnrichedCitationsClient(config=config)


class TestEnrichedCitationsSearch:
    """Integration tests for search_citations."""

    def test_search_by_application_number(
        self, enriched_citations_client: EnrichedCitationsClient
    ) -> None:
        """Test searching citations by application number."""
        response = enriched_citations_client.search_citations(
            patent_application_number_q="15739603",
            rows=10,
        )
        assert isinstance(response, EnrichedCitationResponse)
        assert response.num_found > 0
        assert len(response.docs) > 0
        assert response.docs[0].patent_application_number == "15739603"

    def test_search_by_tech_center(
        self, enriched_citations_client: EnrichedCitationsClient
    ) -> None:
        """Test searching citations by technology center."""
        response = enriched_citations_client.search_citations(
            tech_center_q="2800",
            rows=3,
        )
        assert isinstance(response, EnrichedCitationResponse)
        assert response.num_found > 0
        for doc in response.docs:
            assert doc.tech_center == "2800"


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
