"""
Integration tests for the USPTO PTAB Appeals API client.

This module contains integration tests that make real API calls to the USPTO PTAB Appeals API.
These tests are optional and are skipped by default unless the ENABLE_INTEGRATION_TESTS
environment variable is set to 'true'.
"""

import os
from typing import Iterator

import pytest

from pyUSPTO.clients import PTABAppealsClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.exceptions import USPTOApiError
from pyUSPTO.models.ptab import PTABAppealDecision, PTABAppealResponse

# Skip all tests in this module unless ENABLE_INTEGRATION_TESTS is set to 'true'
pytestmark = pytest.mark.skipif(
    os.environ.get("ENABLE_INTEGRATION_TESTS", "").lower() != "true",
    reason="Integration tests are disabled. Set ENABLE_INTEGRATION_TESTS=true to enable.",
)


@pytest.fixture
def ptab_appeals_client(config: USPTOConfig) -> PTABAppealsClient:
    """
    Create a PTABAppealsClient instance for integration tests.

    Args:
        config: The configuration instance

    Returns:
        PTABAppealsClient: A client instance
    """
    return PTABAppealsClient(config=config)


class TestPTABAppealsIntegration:
    """Integration tests for the PTABAppealsClient."""

    def test_search_decisions_get(
        self, ptab_appeals_client: PTABAppealsClient
    ) -> None:
        """Test searching PTAB appeal decisions using GET method."""
        try:
            response = ptab_appeals_client.search_decisions(
                query="appealMetaData.applicationTypeCategory:Utility",
                limit=2,
            )

            assert response is not None
            assert isinstance(response, PTABAppealResponse)
            assert response.count >= 0

            if response.count > 0:
                assert response.patent_appeal_data_bag is not None
                assert len(response.patent_appeal_data_bag) > 0
                assert len(response.patent_appeal_data_bag) <= 2

                decision = response.patent_appeal_data_bag[0]
                assert isinstance(decision, PTABAppealDecision)
                assert decision.appeal_number is not None

        except USPTOApiError as e:
            pytest.skip(f"PTAB Appeals API error during search_decisions GET: {e}")

    def test_search_decisions_with_convenience_params(
        self, ptab_appeals_client: PTABAppealsClient
    ) -> None:
        """Test searching appeal decisions with convenience parameters."""
        try:
            response = ptab_appeals_client.search_decisions(
                application_type_category_q="Utility",
                limit=2,
            )

            assert response is not None
            assert isinstance(response, PTABAppealResponse)
            assert response.count >= 0

            if response.count > 0:
                assert response.patent_appeal_data_bag is not None
                for decision in response.patent_appeal_data_bag:
                    assert isinstance(decision, PTABAppealDecision)
                    # Verify application type if metadata present
                    if decision.appeal_meta_data:
                        if decision.appeal_meta_data.application_type_category:
                            assert (
                                decision.appeal_meta_data.application_type_category
                                == "Utility"
                            )

        except USPTOApiError as e:
            pytest.skip(
                f"PTAB Appeals API error during search_decisions with convenience params: {e}"
            )

    def test_search_decisions_post(
        self, ptab_appeals_client: PTABAppealsClient
    ) -> None:
        """Test searching PTAB appeal decisions using POST method."""
        post_body = {
            "q": "appealMetaData.applicationTypeCategory:Utility",
            "pagination": {"offset": 0, "limit": 2},
        }

        try:
            response = ptab_appeals_client.search_decisions(post_body=post_body)

            assert response is not None
            assert isinstance(response, PTABAppealResponse)
            assert response.count >= 0

            if response.count > 0:
                assert response.patent_appeal_data_bag is not None
                assert len(response.patent_appeal_data_bag) <= 2

        except USPTOApiError as e:
            pytest.skip(f"PTAB Appeals API error during search_decisions POST: {e}")

    def test_search_decisions_with_date_filters(
        self, ptab_appeals_client: PTABAppealsClient
    ) -> None:
        """Test searching appeal decisions with date range filters."""
        try:
            response = ptab_appeals_client.search_decisions(
                decision_date_from_q="2023-01-01",
                decision_date_to_q="2024-12-31",
                limit=2,
            )

            assert response is not None
            assert isinstance(response, PTABAppealResponse)
            assert response.count >= 0

            if response.count > 0:
                assert response.patent_appeal_data_bag is not None

        except USPTOApiError as e:
            pytest.skip(
                f"PTAB Appeals API error during search_decisions with date filters: {e}"
            )

    def test_search_decisions_by_decision_type(
        self, ptab_appeals_client: PTABAppealsClient
    ) -> None:
        """Test searching appeal decisions by decision type."""
        try:
            response = ptab_appeals_client.search_decisions(
                decision_type_category_q="Affirmed",
                limit=2,
            )

            assert response is not None
            assert isinstance(response, PTABAppealResponse)
            assert response.count >= 0

            if response.count > 0:
                assert response.patent_appeal_data_bag is not None
                for decision in response.patent_appeal_data_bag:
                    # Verify decision type if present
                    if decision.decision_data:
                        if decision.decision_data.decision_type_category:
                            assert "Affirmed" in decision.decision_data.decision_type_category

        except USPTOApiError as e:
            pytest.skip(
                f"PTAB Appeals API error during search by decision type: {e}"
            )

    def test_search_decisions_by_appellant(
        self, ptab_appeals_client: PTABAppealsClient
    ) -> None:
        """Test searching appeal decisions by appellant name."""
        try:
            # Use a common corporation name
            response = ptab_appeals_client.search_decisions(
                appellant_name_q="Corporation",
                limit=2,
            )

            assert response is not None
            assert isinstance(response, PTABAppealResponse)
            assert response.count >= 0

            if response.count > 0:
                assert response.patent_appeal_data_bag is not None

        except USPTOApiError as e:
            pytest.skip(
                f"PTAB Appeals API error during search by appellant: {e}"
            )

    def test_paginate_decisions(
        self, ptab_appeals_client: PTABAppealsClient
    ) -> None:
        """Test paginating through appeal decisions."""
        try:
            # Limit to small number to avoid long test times
            results = list(
                ptab_appeals_client.paginate_decisions(
                    query="appealMetaData.applicationTypeCategory:Utility",
                    limit=5,
                    max_results=10,
                )
            )

            assert isinstance(results, list)
            if len(results) > 0:
                assert all(isinstance(d, PTABAppealDecision) for d in results)
                assert len(results) <= 10  # Should respect max_results

        except USPTOApiError as e:
            pytest.skip(f"PTAB Appeals API error during paginate_decisions: {e}")

    def test_search_with_optional_params(
        self, ptab_appeals_client: PTABAppealsClient
    ) -> None:
        """Test searching with optional parameters like sort and facets."""
        try:
            response = ptab_appeals_client.search_decisions(
                query="appealMetaData.applicationTypeCategory:Utility",
                limit=2,
                sort="appealNumber desc",
                offset=0,
            )

            assert response is not None
            assert isinstance(response, PTABAppealResponse)
            assert response.count >= 0

        except USPTOApiError as e:
            pytest.skip(
                f"PTAB Appeals API error during search with optional params: {e}"
            )

    def test_invalid_query_handling(
        self, ptab_appeals_client: PTABAppealsClient
    ) -> None:
        """Test proper error handling with an invalid query."""
        try:
            # Use an obviously malformed query
            response = ptab_appeals_client.search_decisions(
                query="INVALID_FIELD:value", limit=1
            )

            # API may return 0 results instead of error for invalid field
            assert isinstance(response, PTABAppealResponse)

        except USPTOApiError as e:
            # This is acceptable - API may return error for invalid queries
            assert e.status_code in [400, 404, 500]
