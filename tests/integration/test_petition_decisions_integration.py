"""
Integration tests for the USPTO Final Petition Decisions API client.

This module contains integration tests that make real API calls to the USPTO Final Petition Decisions API.
These tests are optional and are skipped by default unless the ENABLE_INTEGRATION_TESTS
environment variable is set to 'true'.
"""

import os
from typing import Iterator, List, Optional

import pytest

# Import shared fixtures
from tests.integration.conftest import TEST_DOWNLOAD_DIR

from pyUSPTO.clients import FinalPetitionDecisionsClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.exceptions import USPTOApiError, USPTOApiNotFoundError
from pyUSPTO.models.petition_decisions import (
    DecisionTypeCode,
    DocumentDirectionCategory,
    DocumentDownloadOption,
    PetitionDecision,
    PetitionDecisionDocument,
    PetitionDecisionDownloadResponse,
    PetitionDecisionResponse,
)

# Skip all tests in this module unless ENABLE_INTEGRATION_TESTS is set to 'true'
pytestmark = pytest.mark.skipif(
    os.environ.get("ENABLE_INTEGRATION_TESTS", "").lower() != "true",
    reason="Integration tests are disabled. Set ENABLE_INTEGRATION_TESTS=true to enable.",
)


@pytest.fixture
def petition_decisions_client(config: USPTOConfig) -> FinalPetitionDecisionsClient:
    """
    Create a FinalPetitionDecisionsClient instance for integration tests.

    Args:
        config: The configuration instance

    Returns:
        FinalPetitionDecisionsClient: A client instance
    """
    return FinalPetitionDecisionsClient(config=config)


@pytest.fixture
def sample_petition_decision_id(
    petition_decisions_client: FinalPetitionDecisionsClient,
) -> str:
    """Provides a sample petition decision record ID for tests."""
    try:
        # Search for a recent decision
        response = petition_decisions_client.search_decisions(limit=1)
        if response.count > 0 and response.petition_decision_data_bag:
            decision_id = response.petition_decision_data_bag[
                0
            ].petition_decision_record_identifier
            if decision_id:
                return decision_id

        pytest.skip(
            "Could not retrieve a sample petition decision ID. Ensure API is reachable."
        )

    except USPTOApiError as e:
        pytest.skip(f"Could not fetch sample petition decision ID due to API error: {e}")
    except Exception as e:
        pytest.skip(
            f"Could not fetch sample petition decision ID due to unexpected error: {e}"
        )
    return ""


class TestFinalPetitionDecisionsIntegration:
    """Integration tests for the FinalPetitionDecisionsClient."""

    def test_search_decisions_basic(
        self, petition_decisions_client: FinalPetitionDecisionsClient
    ) -> None:
        """Test basic search for petition decisions."""
        response = petition_decisions_client.search_decisions(limit=5)

        assert response is not None
        assert isinstance(response, PetitionDecisionResponse)
        assert response.count is not None
        assert response.count >= 0

        if response.count > 0:
            assert response.petition_decision_data_bag is not None
            assert len(response.petition_decision_data_bag) > 0
            assert len(response.petition_decision_data_bag) <= 5

            decision = response.petition_decision_data_bag[0]
            assert isinstance(decision, PetitionDecision)
            assert decision.petition_decision_record_identifier is not None

    def test_search_decisions_with_query(
        self, petition_decisions_client: FinalPetitionDecisionsClient
    ) -> None:
        """Test searching with a custom query."""
        try:
            response = petition_decisions_client.search_decisions(
                query="applicantName:*", limit=3
            )

            assert response is not None
            assert isinstance(response, PetitionDecisionResponse)
            assert response.count >= 0

            if response.count > 0:
                assert response.petition_decision_data_bag is not None
                assert len(response.petition_decision_data_bag) <= 3
        except USPTOApiNotFoundError:
            # 404 may be returned if no records match the query
            pytest.skip("No records found matching query criteria")

    def test_search_decisions_with_application_number(
        self, petition_decisions_client: FinalPetitionDecisionsClient
    ) -> None:
        """Test searching using convenience application_number_q parameter."""
        # First get any decision with an application number
        response = petition_decisions_client.search_decisions(limit=10)
        if response.count == 0:
            pytest.skip("No decisions available to test application number search")

        # Find a decision with an application number
        app_num = None
        for decision in response.petition_decision_data_bag:
            if decision.application_number_text:
                app_num = decision.application_number_text
                break

        if not app_num:
            pytest.skip("No decisions with application numbers found")

        # Search for that specific application number
        response = petition_decisions_client.search_decisions(
            application_number_q=app_num, limit=5
        )

        assert response is not None
        assert response.count > 0
        if response.petition_decision_data_bag:
            # At least one should match
            found = any(
                d.application_number_text == app_num
                for d in response.petition_decision_data_bag
            )
            assert found, f"Expected to find application number {app_num} in results"

    def test_search_decisions_with_patent_number(
        self, petition_decisions_client: FinalPetitionDecisionsClient
    ) -> None:
        """Test searching using convenience patent_number_q parameter."""
        # First get any decision with a patent number
        response = petition_decisions_client.search_decisions(limit=20)
        if response.count == 0:
            pytest.skip("No decisions available to test patent number search")

        # Find a decision with a patent number
        patent_num = None
        for decision in response.petition_decision_data_bag:
            if decision.patent_number:
                patent_num = decision.patent_number
                break

        if not patent_num:
            pytest.skip("No decisions with patent numbers found in first 20 results")

        # Search for that specific patent number
        response = petition_decisions_client.search_decisions(
            patent_number_q=patent_num, limit=5
        )

        assert response is not None
        if response.count > 0 and response.petition_decision_data_bag:
            # At least one should match
            found = any(
                d.patent_number == patent_num
                for d in response.petition_decision_data_bag
            )
            assert (
                found
            ), f"Expected to find patent number {patent_num} in results but count is {response.count}"

    def test_search_decisions_with_technology_center(
        self, petition_decisions_client: FinalPetitionDecisionsClient
    ) -> None:
        """Test searching using convenience technology_center_q parameter."""
        # Technology centers are typically 2600, 2800, etc.
        response = petition_decisions_client.search_decisions(
            technology_center_q="2600", limit=5
        )

        assert response is not None
        assert isinstance(response, PetitionDecisionResponse)
        # May or may not have results depending on data availability
        assert response.count >= 0

    def test_search_decisions_with_date_range(
        self, petition_decisions_client: FinalPetitionDecisionsClient
    ) -> None:
        """Test searching using date range parameters."""
        # Search for decisions from 2020-01-01 onwards
        response = petition_decisions_client.search_decisions(
            decision_date_from_q="2020-01-01", limit=5
        )

        assert response is not None
        assert isinstance(response, PetitionDecisionResponse)
        assert response.count >= 0

        if response.count > 0:
            assert response.petition_decision_data_bag is not None
            assert len(response.petition_decision_data_bag) <= 5

    def test_get_decision_by_id(
        self,
        petition_decisions_client: FinalPetitionDecisionsClient,
        sample_petition_decision_id: str,
    ) -> None:
        """Test getting a specific decision by ID."""
        decision = petition_decisions_client.get_decision_by_id(
            sample_petition_decision_id
        )

        assert decision is not None
        assert isinstance(decision, PetitionDecision)
        assert decision.petition_decision_record_identifier == sample_petition_decision_id
        assert decision.decision_type_code is not None

    def test_get_decision_by_invalid_id(
        self, petition_decisions_client: FinalPetitionDecisionsClient
    ) -> None:
        """Test proper error handling with an invalid decision ID."""
        invalid_id = "INVALID_ID_12345"

        try:
            decision = petition_decisions_client.get_decision_by_id(invalid_id)
            # If no exception, the API might return None or an empty response
            assert decision is None or isinstance(decision, PetitionDecision)
        except USPTOApiNotFoundError as e:
            assert e.status_code == 404, f"Expected 404 error, got {e.status_code}"
        except USPTOApiError:
            # Other API errors are acceptable (e.g., 400 Bad Request)
            pass

    def test_download_decisions_json(
        self, petition_decisions_client: FinalPetitionDecisionsClient
    ) -> None:
        """Test downloading petition decisions in JSON format."""
        try:
            response = petition_decisions_client.download_decisions(
                format="json", decision_date_from_q="2023-01-01", limit=2
            )

            assert response is not None
            assert isinstance(response, PetitionDecisionDownloadResponse)
            # PetitionDecisionDownloadResponse doesn't have count attribute
            assert response.petition_decision_data is not None
            assert isinstance(response.petition_decision_data, list)

            if len(response.petition_decision_data) > 0:
                assert len(response.petition_decision_data) <= 2
                assert isinstance(
                    response.petition_decision_data[0], PetitionDecision
                )
        except USPTOApiError as e:
            pytest.skip(f"Download endpoint failed: {e}")

    def test_download_decisions_csv(
        self, petition_decisions_client: FinalPetitionDecisionsClient
    ) -> None:
        """Test downloading petition decisions in CSV format to file."""
        try:
            file_path = petition_decisions_client.download_decisions(
                format="csv",
                decision_date_from_q="2023-01-01",
                limit=2,
                destination_path=TEST_DOWNLOAD_DIR,
            )

            # Should return a file path
            assert file_path is not None
            assert isinstance(file_path, str)
            assert os.path.exists(file_path)
            assert os.path.getsize(file_path) > 0

            # Check it's a CSV file
            assert file_path.endswith(".csv")

            # Read first line to verify CSV format
            with open(file_path, "r", encoding="utf-8") as f:
                first_line = f.readline()
                # CSV should have headers with commas
                assert len(first_line) > 0
                assert "," in first_line

        except USPTOApiError as e:
            pytest.skip(f"CSV download endpoint failed: {e}")

    def test_paginate_decisions(
        self, petition_decisions_client: FinalPetitionDecisionsClient
    ) -> None:
        """Test pagination through petition decisions."""
        page_size = 5
        max_pages = 2  # Only test 2 pages to keep test fast

        pages_retrieved = 0
        total_decisions = 0

        try:
            for response in petition_decisions_client.paginate_decisions(
                limit=page_size, query="applicantName:*"
            ):
                assert isinstance(response, PetitionDecisionResponse)
                assert len(response.petition_decision_data_bag) <= page_size

                total_decisions += len(response.petition_decision_data_bag)
                pages_retrieved += 1

                if pages_retrieved >= max_pages:
                    break

            assert pages_retrieved > 0, "Should have retrieved at least one page"
            assert total_decisions > 0, "Should have retrieved at least one decision"

        except USPTOApiError as e:
            pytest.skip(f"Pagination test failed: {e}")

    def test_decision_with_documents(
        self, petition_decisions_client: FinalPetitionDecisionsClient
    ) -> None:
        """Test retrieving a decision that has associated documents."""
        # Search for decisions and find one with documents
        response = petition_decisions_client.search_decisions(limit=20)

        if response.count == 0:
            pytest.skip("No decisions available to test document retrieval")

        # Find a decision with documents
        decision_with_docs = None
        for decision in response.petition_decision_data_bag:
            if decision.document_bag and len(decision.document_bag) > 0:
                decision_with_docs = decision
                break

        if not decision_with_docs:
            pytest.skip("No decisions with documents found in first 20 results")

        # Verify document structure
        assert decision_with_docs.document_bag is not None
        assert len(decision_with_docs.document_bag) > 0

        doc = decision_with_docs.document_bag[0]
        assert isinstance(doc, PetitionDecisionDocument)
        assert doc.document_identifier is not None

    def test_download_petition_document(
        self, petition_decisions_client: FinalPetitionDecisionsClient
    ) -> None:
        """Test downloading a petition decision document."""
        # Search for decisions with downloadable documents
        response = petition_decisions_client.search_decisions(limit=20)

        if response.count == 0:
            pytest.skip("No decisions available to test document download")

        # Find a document with download options
        download_option = None
        for decision in response.petition_decision_data_bag:
            if decision.document_bag:
                for doc in decision.document_bag:
                    if doc.download_option_bag and len(doc.download_option_bag) > 0:
                        download_option = doc.download_option_bag[0]
                        break
            if download_option:
                break

        if not download_option or not download_option.download_url:
            pytest.skip("No downloadable documents found in first 20 results")

        try:
            file_path = petition_decisions_client.download_petition_document(
                download_option, file_path=TEST_DOWNLOAD_DIR
            )

            assert file_path is not None
            assert os.path.exists(file_path)
            assert os.path.getsize(file_path) > 0

        except USPTOApiError as e:
            pytest.skip(f"Document download failed: {e}")
        except Exception as e:
            pytest.skip(f"Document download failed with unexpected error: {e}")

    def test_search_decisions_with_multiple_params(
        self, petition_decisions_client: FinalPetitionDecisionsClient
    ) -> None:
        """Test searching with multiple convenience parameters."""
        response = petition_decisions_client.search_decisions(
            decision_date_from_q="2020-01-01",
            decision_date_to_q="2024-12-31",
            limit=10,
        )

        assert response is not None
        assert isinstance(response, PetitionDecisionResponse)
        assert response.count >= 0

        if response.count > 0:
            assert len(response.petition_decision_data_bag) <= 10

    def test_search_decisions_response_fields(
        self, petition_decisions_client: FinalPetitionDecisionsClient
    ) -> None:
        """Test that response includes expected fields."""
        response = petition_decisions_client.search_decisions(limit=5)

        assert response is not None
        assert response.count is not None
        assert response.request_identifier is not None

        if response.count > 0:
            decision = response.petition_decision_data_bag[0]

            # Check for key fields (some may be None depending on the decision)
            assert hasattr(decision, "petition_decision_record_identifier")
            assert hasattr(decision, "application_number_text")
            assert hasattr(decision, "decision_type_code")
            assert hasattr(decision, "decision_date")
            assert hasattr(decision, "document_bag")
            assert hasattr(decision, "inventor_bag")
            assert hasattr(decision, "rule_bag")
            assert hasattr(decision, "statute_bag")

    def test_decision_type_code_enum(
        self, petition_decisions_client: FinalPetitionDecisionsClient
    ) -> None:
        """Test that decision type codes are properly parsed into enums."""
        response = petition_decisions_client.search_decisions(limit=10)

        if response.count == 0:
            pytest.skip("No decisions available to test decision type codes")

        # Find a decision with a decision_type_code
        for decision in response.petition_decision_data_bag:
            if decision.decision_type_code:
                # Should be a valid DecisionTypeCode enum or string
                assert isinstance(decision.decision_type_code, (DecisionTypeCode, str))
                break
        else:
            pytest.skip("No decisions with decision_type_code found")

    def test_document_direction_category_enum(
        self, petition_decisions_client: FinalPetitionDecisionsClient
    ) -> None:
        """Test that document direction categories are properly parsed into enums."""
        response = petition_decisions_client.search_decisions(limit=20)

        if response.count == 0:
            pytest.skip("No decisions available to test document direction categories")

        # Find a document with a direction category
        found = False
        for decision in response.petition_decision_data_bag:
            if decision.document_bag:
                for doc in decision.document_bag:
                    if doc.document_direction_category:
                        # Should be a valid DocumentDirectionCategory enum or string
                        assert isinstance(
                            doc.document_direction_category,
                            (DocumentDirectionCategory, str),
                        )
                        found = True
                        break
            if found:
                break

        if not found:
            pytest.skip("No documents with direction_category found")
