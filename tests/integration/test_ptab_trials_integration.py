"""
Integration tests for the USPTO PTAB Trials API client.

This module contains integration tests that make real API calls to the USPTO PTAB Trials API.
These tests are optional and are skipped by default unless the ENABLE_INTEGRATION_TESTS
environment variable is set to 'true'.
"""

import os
from typing import Iterator

import pytest

from pyUSPTO.clients import PTABTrialsClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.exceptions import USPTOApiError
from pyUSPTO.models.ptab import (
    PTABTrialDocumentResponse,
    PTABTrialProceeding,
    PTABTrialProceedingResponse,
)

# Skip all tests in this module unless ENABLE_INTEGRATION_TESTS is set to 'true'
pytestmark = pytest.mark.skipif(
    os.environ.get("ENABLE_INTEGRATION_TESTS", "").lower() != "true",
    reason="Integration tests are disabled. Set ENABLE_INTEGRATION_TESTS=true to enable.",
)


@pytest.fixture
def ptab_trials_client(config: USPTOConfig) -> PTABTrialsClient:
    """
    Create a PTABTrialsClient instance for integration tests.

    Args:
        config: The configuration instance

    Returns:
        PTABTrialsClient: A client instance
    """
    return PTABTrialsClient(config=config)


class TestPTABTrialsIntegration:
    """Integration tests for the PTABTrialsClient."""

    def test_search_proceedings_get(
        self, ptab_trials_client: PTABTrialsClient
    ) -> None:
        """Test searching PTAB trial proceedings using GET method."""
        try:
            response = ptab_trials_client.search_proceedings(
                query="trialMetaData.trialStatusCategory:Instituted",
                limit=2,
            )

            assert response is not None
            assert isinstance(response, PTABTrialProceedingResponse)
            assert response.count >= 0

            if response.count > 0:
                assert response.patent_trial_proceeding_data_bag is not None
                assert len(response.patent_trial_proceeding_data_bag) > 0
                assert len(response.patent_trial_proceeding_data_bag) <= 2

                proceeding = response.patent_trial_proceeding_data_bag[0]
                assert isinstance(proceeding, PTABTrialProceeding)
                assert proceeding.trial_number is not None

        except USPTOApiError as e:
            pytest.skip(f"PTAB Trials API error during search_proceedings GET: {e}")

    def test_search_proceedings_with_convenience_params(
        self, ptab_trials_client: PTABTrialsClient
    ) -> None:
        """Test searching proceedings with convenience parameters."""
        try:
            response = ptab_trials_client.search_proceedings(
                trial_type_code_q="IPR",
                trial_status_category_q="Instituted",
                limit=2,
            )

            assert response is not None
            assert isinstance(response, PTABTrialProceedingResponse)
            assert response.count >= 0

            if response.count > 0:
                assert response.patent_trial_proceeding_data_bag is not None
                for proceeding in response.patent_trial_proceeding_data_bag:
                    assert isinstance(proceeding, PTABTrialProceeding)
                    if proceeding.trial_meta_data:
                        # Verify trial type if present
                        if proceeding.trial_meta_data.trial_type_code:
                            assert proceeding.trial_meta_data.trial_type_code == "IPR"

        except USPTOApiError as e:
            pytest.skip(
                f"PTAB Trials API error during search_proceedings with convenience params: {e}"
            )

    def test_search_proceedings_post(
        self, ptab_trials_client: PTABTrialsClient
    ) -> None:
        """Test searching PTAB trial proceedings using POST method."""
        post_body = {
            "q": "trialMetaData.trialTypeCode:IPR",
            "pagination": {"offset": 0, "limit": 2},
        }

        try:
            response = ptab_trials_client.search_proceedings(post_body=post_body)

            assert response is not None
            assert isinstance(response, PTABTrialProceedingResponse)
            assert response.count >= 0

            if response.count > 0:
                assert response.patent_trial_proceeding_data_bag is not None
                assert len(response.patent_trial_proceeding_data_bag) <= 2

        except USPTOApiError as e:
            pytest.skip(f"PTAB Trials API error during search_proceedings POST: {e}")

    def test_search_documents_get(
        self, ptab_trials_client: PTABTrialsClient
    ) -> None:
        """Test searching PTAB trial documents using GET method."""
        try:
            response = ptab_trials_client.search_documents(
                query="documentData.documentCategory:Paper",
                limit=2,
            )

            assert response is not None
            assert isinstance(response, PTABTrialDocumentResponse)
            assert response.count >= 0

            if response.count > 0:
                assert response.patent_trial_document_data_bag is not None
                assert len(response.patent_trial_document_data_bag) > 0
                assert len(response.patent_trial_document_data_bag) <= 2

                document = response.patent_trial_document_data_bag[0]
                assert document.trial_number is not None

        except USPTOApiError as e:
            pytest.skip(f"PTAB Trials API error during search_documents GET: {e}")

    def test_search_documents_with_convenience_params(
        self, ptab_trials_client: PTABTrialsClient
    ) -> None:
        """Test searching documents with convenience parameters."""
        try:
            response = ptab_trials_client.search_documents(
                document_category_q="Paper",
                limit=2,
            )

            assert response is not None
            assert isinstance(response, PTABTrialDocumentResponse)
            assert response.count >= 0

            if response.count > 0:
                assert response.patent_trial_document_data_bag is not None

        except USPTOApiError as e:
            pytest.skip(
                f"PTAB Trials API error during search_documents with convenience params: {e}"
            )

    def test_search_documents_post(
        self, ptab_trials_client: PTABTrialsClient
    ) -> None:
        """Test searching PTAB trial documents using POST method."""
        post_body = {
            "q": "trialTypeCode:IPR",
            "pagination": {"offset": 0, "limit": 2},
        }

        try:
            response = ptab_trials_client.search_documents(post_body=post_body)

            assert response is not None
            assert isinstance(response, PTABTrialDocumentResponse)
            assert response.count >= 0

            if response.count > 0:
                assert response.patent_trial_document_data_bag is not None
                assert len(response.patent_trial_document_data_bag) <= 2

        except USPTOApiError as e:
            pytest.skip(f"PTAB Trials API error during search_documents POST: {e}")

    def test_search_decisions_get(
        self, ptab_trials_client: PTABTrialsClient
    ) -> None:
        """Test searching PTAB trial decisions using GET method."""
        try:
            response = ptab_trials_client.search_decisions(
                query="decisionData.decisionTypeCategory:Final Written Decision",
                limit=2,
            )

            assert response is not None
            assert isinstance(response, PTABTrialDocumentResponse)
            assert response.count >= 0

            if response.count > 0:
                assert response.patent_trial_document_data_bag is not None
                assert len(response.patent_trial_document_data_bag) > 0
                assert len(response.patent_trial_document_data_bag) <= 2

                decision = response.patent_trial_document_data_bag[0]
                assert decision.trial_number is not None

        except USPTOApiError as e:
            pytest.skip(f"PTAB Trials API error during search_decisions GET: {e}")

    def test_search_decisions_with_convenience_params(
        self, ptab_trials_client: PTABTrialsClient
    ) -> None:
        """Test searching decisions with convenience parameters."""
        try:
            response = ptab_trials_client.search_decisions(
                trial_type_code_q="IPR",
                limit=2,
            )

            assert response is not None
            assert isinstance(response, PTABTrialDocumentResponse)
            assert response.count >= 0

            if response.count > 0:
                assert response.patent_trial_document_data_bag is not None
                for decision in response.patent_trial_document_data_bag:
                    if decision.trial_type_code:
                        assert decision.trial_type_code == "IPR"

        except USPTOApiError as e:
            pytest.skip(
                f"PTAB Trials API error during search_decisions with convenience params: {e}"
            )

    def test_search_decisions_post(
        self, ptab_trials_client: PTABTrialsClient
    ) -> None:
        """Test searching PTAB trial decisions using POST method."""
        post_body = {
            "q": "trialTypeCode:IPR",
            "pagination": {"offset": 0, "limit": 2},
        }

        try:
            response = ptab_trials_client.search_decisions(post_body=post_body)

            assert response is not None
            assert isinstance(response, PTABTrialDocumentResponse)
            assert response.count >= 0

            if response.count > 0:
                assert response.patent_trial_document_data_bag is not None
                assert len(response.patent_trial_document_data_bag) <= 2

        except USPTOApiError as e:
            pytest.skip(f"PTAB Trials API error during search_decisions POST: {e}")

    def test_paginate_proceedings(
        self, ptab_trials_client: PTABTrialsClient
    ) -> None:
        """Test paginating through trial proceedings."""
        try:
            # Limit to small number to avoid long test times
            results = list(
                ptab_trials_client.paginate_proceedings(
                    query="trialMetaData.trialTypeCode:IPR",
                    limit=5,
                    max_results=10,
                )
            )

            assert isinstance(results, list)
            if len(results) > 0:
                assert all(isinstance(p, PTABTrialProceeding) for p in results)
                assert len(results) <= 10  # Should respect max_results

        except USPTOApiError as e:
            pytest.skip(f"PTAB Trials API error during paginate_proceedings: {e}")

    def test_invalid_query_handling(
        self, ptab_trials_client: PTABTrialsClient
    ) -> None:
        """Test proper error handling with an invalid query."""
        try:
            # Use an obviously malformed query
            response = ptab_trials_client.search_proceedings(
                query="INVALID_FIELD:value", limit=1
            )

            # API may return 0 results instead of error for invalid field
            assert isinstance(response, PTABTrialProceedingResponse)

        except USPTOApiError as e:
            # This is acceptable - API may return error for invalid queries
            assert e.status_code in [400, 404, 500]
