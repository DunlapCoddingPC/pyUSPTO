"""
Integration tests for the USPTO PTAB Interferences API client.

This module contains integration tests that make real API calls to the USPTO PTAB Interferences API.
These tests are optional and are skipped by default unless the ENABLE_INTEGRATION_TESTS
environment variable is set to 'true'.
"""

import os
from typing import Iterator

import pytest

from pyUSPTO.clients import PTABInterferencesClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.exceptions import USPTOApiError
from pyUSPTO.models.ptab import PTABInterferenceDecision, PTABInterferenceResponse

# Skip all tests in this module unless ENABLE_INTEGRATION_TESTS is set to 'true'
pytestmark = pytest.mark.skipif(
    os.environ.get("ENABLE_INTEGRATION_TESTS", "").lower() != "true",
    reason="Integration tests are disabled. Set ENABLE_INTEGRATION_TESTS=true to enable.",
)


@pytest.fixture
def ptab_interferences_client(config: USPTOConfig) -> PTABInterferencesClient:
    """
    Create a PTABInterferencesClient instance for integration tests.

    Args:
        config: The configuration instance

    Returns:
        PTABInterferencesClient: A client instance
    """
    return PTABInterferencesClient(config=config)


class TestPTABInterferencesIntegration:
    """Integration tests for the PTABInterferencesClient."""

    def test_search_decisions_get(
        self, ptab_interferences_client: PTABInterferencesClient
    ) -> None:
        """Test searching PTAB interference decisions using GET method."""
        try:
            response = ptab_interferences_client.search_decisions(
                query="interferenceNumber:*",
                limit=2,
            )

            assert response is not None
            assert isinstance(response, PTABInterferenceResponse)
            assert response.count >= 0

            if response.count > 0:
                assert response.patent_interference_data_bag is not None
                assert len(response.patent_interference_data_bag) > 0
                assert len(response.patent_interference_data_bag) <= 2

                decision = response.patent_interference_data_bag[0]
                assert isinstance(decision, PTABInterferenceDecision)
                assert decision.interference_number is not None

        except USPTOApiError as e:
            pytest.skip(f"PTAB Interferences API error during search_decisions GET: {e}")

    def test_search_decisions_with_convenience_params(
        self, ptab_interferences_client: PTABInterferencesClient
    ) -> None:
        """Test searching interference decisions with convenience parameters."""
        try:
            response = ptab_interferences_client.search_decisions(
                interference_outcome_category_q="Priority",
                limit=2,
            )

            assert response is not None
            assert isinstance(response, PTABInterferenceResponse)
            assert response.count >= 0

            if response.count > 0:
                assert response.patent_interference_data_bag is not None
                for decision in response.patent_interference_data_bag:
                    assert isinstance(decision, PTABInterferenceDecision)
                    # Verify outcome if document data present
                    if decision.document_data:
                        if decision.document_data.interference_outcome_category:
                            assert (
                                "Priority"
                                in decision.document_data.interference_outcome_category
                            )

        except USPTOApiError as e:
            pytest.skip(
                f"PTAB Interferences API error during search_decisions with convenience params: {e}"
            )

    def test_search_decisions_post(
        self, ptab_interferences_client: PTABInterferencesClient
    ) -> None:
        """Test searching PTAB interference decisions using POST method."""
        post_body = {
            "q": "interferenceNumber:*",
            "pagination": {"offset": 0, "limit": 2},
        }

        try:
            response = ptab_interferences_client.search_decisions(post_body=post_body)

            assert response is not None
            assert isinstance(response, PTABInterferenceResponse)
            assert response.count >= 0

            if response.count > 0:
                assert response.patent_interference_data_bag is not None
                assert len(response.patent_interference_data_bag) <= 2

        except USPTOApiError as e:
            pytest.skip(f"PTAB Interferences API error during search_decisions POST: {e}")

    def test_search_decisions_with_date_filters(
        self, ptab_interferences_client: PTABInterferencesClient
    ) -> None:
        """Test searching interference decisions with date range filters."""
        try:
            response = ptab_interferences_client.search_decisions(
                decision_date_from_q="2020-01-01",
                decision_date_to_q="2024-12-31",
                limit=2,
            )

            assert response is not None
            assert isinstance(response, PTABInterferenceResponse)
            assert response.count >= 0

            if response.count > 0:
                assert response.patent_interference_data_bag is not None

        except USPTOApiError as e:
            pytest.skip(
                f"PTAB Interferences API error during search_decisions with date filters: {e}"
            )

    def test_search_decisions_by_decision_type(
        self, ptab_interferences_client: PTABInterferencesClient
    ) -> None:
        """Test searching interference decisions by decision type."""
        try:
            response = ptab_interferences_client.search_decisions(
                decision_type_category_q="Final",
                limit=2,
            )

            assert response is not None
            assert isinstance(response, PTABInterferenceResponse)
            assert response.count >= 0

            if response.count > 0:
                assert response.patent_interference_data_bag is not None
                for decision in response.patent_interference_data_bag:
                    # Verify decision type if present
                    if decision.document_data:
                        if decision.document_data.decision_type_category:
                            assert "Final" in decision.document_data.decision_type_category

        except USPTOApiError as e:
            pytest.skip(
                f"PTAB Interferences API error during search by decision type: {e}"
            )

    def test_search_decisions_by_party(
        self, ptab_interferences_client: PTABInterferencesClient
    ) -> None:
        """Test searching interference decisions by party name."""
        try:
            # Search for senior or junior party
            response = ptab_interferences_client.search_decisions(
                senior_party_name_q="Corporation",
                limit=2,
            )

            assert response is not None
            assert isinstance(response, PTABInterferenceResponse)
            assert response.count >= 0

            if response.count > 0:
                assert response.patent_interference_data_bag is not None

        except USPTOApiError as e:
            pytest.skip(
                f"PTAB Interferences API error during search by party: {e}"
            )

    def test_search_decisions_by_patent_number(
        self, ptab_interferences_client: PTABInterferencesClient
    ) -> None:
        """Test searching interference decisions by patent number."""
        try:
            response = ptab_interferences_client.search_decisions(
                senior_party_patent_number_q="US*",
                limit=2,
            )

            assert response is not None
            assert isinstance(response, PTABInterferenceResponse)
            assert response.count >= 0

            if response.count > 0:
                assert response.patent_interference_data_bag is not None

        except USPTOApiError as e:
            pytest.skip(
                f"PTAB Interferences API error during search by patent number: {e}"
            )

    def test_paginate_decisions(
        self, ptab_interferences_client: PTABInterferencesClient
    ) -> None:
        """Test paginating through interference decisions."""
        try:
            # Limit to small number to avoid long test times
            results = list(
                ptab_interferences_client.paginate_decisions(
                    query="interferenceNumber:*",
                    limit=5,
                    max_results=10,
                )
            )

            assert isinstance(results, list)
            if len(results) > 0:
                assert all(isinstance(d, PTABInterferenceDecision) for d in results)
                assert len(results) <= 10  # Should respect max_results

        except USPTOApiError as e:
            pytest.skip(f"PTAB Interferences API error during paginate_decisions: {e}")

    def test_search_with_optional_params(
        self, ptab_interferences_client: PTABInterferencesClient
    ) -> None:
        """Test searching with optional parameters like sort and facets."""
        try:
            response = ptab_interferences_client.search_decisions(
                query="interferenceNumber:*",
                limit=2,
                sort="interferenceNumber desc",
                offset=0,
            )

            assert response is not None
            assert isinstance(response, PTABInterferenceResponse)
            assert response.count >= 0

        except USPTOApiError as e:
            pytest.skip(
                f"PTAB Interferences API error during search with optional params: {e}"
            )

    def test_search_with_style_name(
        self, ptab_interferences_client: PTABInterferencesClient
    ) -> None:
        """Test searching by interference style name."""
        try:
            response = ptab_interferences_client.search_decisions(
                interference_style_name_q="*",
                limit=2,
            )

            assert response is not None
            assert isinstance(response, PTABInterferenceResponse)
            assert response.count >= 0

            if response.count > 0:
                assert response.patent_interference_data_bag is not None

        except USPTOApiError as e:
            pytest.skip(
                f"PTAB Interferences API error during search by style name: {e}"
            )

    def test_invalid_query_handling(
        self, ptab_interferences_client: PTABInterferencesClient
    ) -> None:
        """Test proper error handling with an invalid query."""
        try:
            # Use an obviously malformed query
            response = ptab_interferences_client.search_decisions(
                query="INVALID_FIELD:value", limit=1
            )

            # API may return 0 results instead of error for invalid field
            assert isinstance(response, PTABInterferenceResponse)

        except USPTOApiError as e:
            # This is acceptable - API may return error for invalid queries
            assert e.status_code in [400, 404, 500]
