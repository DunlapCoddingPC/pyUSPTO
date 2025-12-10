"""
Integration tests for the USPTO Final Petition Decisions API client.

This module contains integration tests that make real API calls to the USPTO Final Petition Decisions API.
These tests are optional and are skipped by default unless the ENABLE_INTEGRATION_TESTS
environment variable is set to 'true'.
"""

import os

import pytest

from pyUSPTO.clients import FinalPetitionDecisionsClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.exceptions import USPTOApiError, USPTOApiNotFoundError
from pyUSPTO.models.petition_decisions import (
    DecisionTypeCode,
    DocumentDirectionCategory,
    PetitionDecision,
    PetitionDecisionDocument,
    PetitionDecisionDownloadResponse,
    PetitionDecisionResponse,
)

# Import shared fixtures
from tests.integration.conftest import TEST_DOWNLOAD_DIR

# Skip all tests in this module unless ENABLE_INTEGRATION_TESTS is set to 'true'
pytestmark = pytest.mark.skipif(
    os.environ.get("ENABLE_INTEGRATION_TESTS", "").lower() != "true",
    reason="Integration tests are disabled. Set ENABLE_INTEGRATION_TESTS=true to enable.",
)


@pytest.fixture(scope="module")
def petition_decisions_client(config: USPTOConfig) -> FinalPetitionDecisionsClient:
    """
    Create a FinalPetitionDecisionsClient instance for integration tests.

    Uses module scope to reuse the same client for all tests in the module,
    reducing overhead from creating multiple client instances.

    Args:
        config: The configuration instance

    Returns:
        FinalPetitionDecisionsClient: A client instance
    """
    return FinalPetitionDecisionsClient(config=config)


@pytest.fixture(scope="module")
def sample_petition_decision(
    petition_decisions_client: FinalPetitionDecisionsClient,
) -> PetitionDecision:
    """Provides a sample petition decision for tests.

    Uses module scope to execute once per test module and cache the result,
    reducing redundant API calls from multiple tests.
    """
    try:
        # Search for a recent decision
        response = petition_decisions_client.search_decisions(limit=1)
        if (
            response.count is not None
            and response.count > 0
            and response.petition_decision_data_bag
        ):
            return response.petition_decision_data_bag[0]

        pytest.skip(
            "Could not retrieve a sample petition decision. Ensure API is reachable."
        )

    except USPTOApiError as e:
        pytest.skip(f"Could not fetch sample petition decision due to API error: {e}")
    except Exception as e:
        pytest.skip(
            f"Could not fetch sample petition decision due to unexpected error: {e}"
        )
    # This return is unreachable but satisfies type checker
    return PetitionDecision()


@pytest.fixture(scope="module")
def sample_petition_decision_id(sample_petition_decision: PetitionDecision) -> str:
    """Provides a sample petition decision record ID for tests.

    Derives from sample_petition_decision to avoid redundant API calls.
    """
    if sample_petition_decision.petition_decision_record_identifier:
        return sample_petition_decision.petition_decision_record_identifier
    pytest.skip("Sample petition decision does not have a record identifier")
    return ""


class TestFinalPetitionDecisionsIntegration:
    """Integration tests for the FinalPetitionDecisionsClient."""

    # Known decision ID for consistent testing (update with a stable ID from the API)
    KNOWN_DECISION_ID = None  # TODO: Add a known stable decision ID when available

    def test_search_decisions_basic(
        self, petition_decisions_client: FinalPetitionDecisionsClient
    ) -> None:
        """Test basic search for petition decisions."""
        response = petition_decisions_client.search_decisions(limit=5)

        assert response is not None
        assert isinstance(response, PetitionDecisionResponse)
        assert response.count is not None
        assert response.count >= 0

        if response.count is not None and response.count > 0:
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
                query="firstApplicantName:*", limit=3
            )

            assert response is not None
            assert isinstance(response, PetitionDecisionResponse)
            assert response.count is not None and response.count >= 0

            if response.count is not None and response.count > 0:
                assert response.petition_decision_data_bag is not None
                assert len(response.petition_decision_data_bag) <= 3
        except USPTOApiNotFoundError:
            # 404 may be returned if no records match the query
            pytest.skip("No records found matching query criteria")
        except USPTOApiError as e:
            pytest.skip(f"Query search failed: {e}")

    def test_search_decisions_with_application_number(
        self,
        petition_decisions_client: FinalPetitionDecisionsClient,
        sample_petition_decision: PetitionDecision,
    ) -> None:
        """Test searching using convenience application_number_q parameter."""
        # Use the application number from the sample decision
        if not sample_petition_decision.application_number_text:
            pytest.skip(
                "Sample decision does not have an application number to test with"
            )

        app_num = sample_petition_decision.application_number_text

        try:
            # Search for that specific application number
            response = petition_decisions_client.search_decisions(
                application_number_q=app_num, limit=5
            )

            assert response is not None
            assert response.count is not None and response.count > 0
            if response.petition_decision_data_bag:
                # At least one should match
                found = any(
                    d.application_number_text == app_num
                    for d in response.petition_decision_data_bag
                )
                assert (
                    found
                ), f"Expected to find application number {app_num} in results"
        except USPTOApiError as e:
            pytest.skip(f"Application number search failed: {e}")

    def test_search_decisions_with_patent_number(
        self,
        petition_decisions_client: FinalPetitionDecisionsClient,
        sample_petition_decision: PetitionDecision,
    ) -> None:
        """Test searching using convenience patent_number_q parameter."""
        try:
            # Try to use patent number from sample decision first
            patent_num = sample_petition_decision.patent_number

            # If sample doesn't have a patent number, search for one
            if not patent_num:
                response = petition_decisions_client.search_decisions(limit=20)
                if response.count == 0:
                    pytest.skip("No decisions available to test patent number search")

                # Find a decision with a patent number
                for decision in response.petition_decision_data_bag:
                    if decision.patent_number:
                        patent_num = decision.patent_number
                        break

                if not patent_num:
                    pytest.skip(
                        "No decisions with patent numbers found in first 20 results"
                    )

            # Search for that specific patent number
            response = petition_decisions_client.search_decisions(
                patent_number_q=patent_num, limit=5
            )

            assert response is not None
            if (
                response.count is not None
                and response.count > 0
                and response.petition_decision_data_bag
            ):
                # At least one should match
                found = any(
                    d.patent_number == patent_num
                    for d in response.petition_decision_data_bag
                )
                assert (
                    found
                ), f"Expected to find patent number {patent_num} in results but count is {response.count}"
        except USPTOApiError as e:
            pytest.skip(f"Patent number search failed: {e}")

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
        assert response.count is not None and response.count >= 0

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
        assert response.count is not None and response.count >= 0

        if response.count is not None and response.count > 0:
            assert response.petition_decision_data_bag is not None
            assert len(response.petition_decision_data_bag) <= 5

    def test_get_decision_by_id(
        self,
        petition_decisions_client: FinalPetitionDecisionsClient,
        sample_petition_decision_id: str,
    ) -> None:
        """Test getting a specific decision by ID."""
        try:
            decision = petition_decisions_client.get_decision_by_id(
                sample_petition_decision_id
            )

            assert decision is not None
            assert isinstance(decision, PetitionDecision)
            assert (
                decision.petition_decision_record_identifier
                == sample_petition_decision_id
            )
            assert decision.decision_type_code is not None
        except USPTOApiNotFoundError:
            pytest.skip(
                f"Decision not found (404) for ID {sample_petition_decision_id}"
            )
        except USPTOApiError as e:
            pytest.skip(f"Failed to get decision by ID: {e}")

    def test_round_trip_data_integrity(
        self,
        petition_decisions_client: FinalPetitionDecisionsClient,
        sample_petition_decision_id: str,
    ) -> None:
        """Test that parsing and serialization preserves data (round-trip test)."""
        try:
            # Get decision from API
            original = petition_decisions_client.get_decision_by_id(
                sample_petition_decision_id
            )

            if original is None:
                pytest.skip(
                    f"No decision data returned for {sample_petition_decision_id}"
                )

            # Convert to dict
            data_dict = original.to_dict()

            # Parse back from dict
            reconstructed = PetitionDecision.from_dict(data_dict)

            # Verify key fields match
            assert (
                reconstructed.petition_decision_record_identifier
                == original.petition_decision_record_identifier
            )
            assert reconstructed.decision_type_code == original.decision_type_code

            if original.decision_date:
                assert reconstructed.decision_date == original.decision_date

            if original.application_number_text:
                assert (
                    reconstructed.application_number_text
                    == original.application_number_text
                )

        except USPTOApiNotFoundError:
            pytest.skip(
                f"Decision not found (404) for round-trip test: {sample_petition_decision_id}"
            )
        except USPTOApiError as e:
            pytest.skip(f"Round-trip test failed due to API error: {e}")

    def test_to_dict_matches_raw_api_response(
        self, api_key: str | None, sample_petition_decision_id: str
    ) -> None:
        """Test that to_dict() output matches the original API response stored in raw_data.

        This test compares the to_dict() serialization with the original API response
        to ensure that the model correctly reconstructs the API format. Some differences
        are expected (e.g., requestIdentifier field is not part of the model).
        """
        # TEMPORARILY DISABLED: See GitHub issue #17
        # API returns naive datetime strings (e.g., '2025-12-03T07:21:12') without timezone
        # indicators, but we serialize with UTC 'Z' suffix (e.g., '2025-12-03T12:21:12Z').
        # Waiting for USPTO ODP to adopt UTC standard for datetime fields.
        # pytest.skip(
        #     "Test disabled pending USPTO API fix for datetime format. See issue #17"
        # )

        # Create a config with include_raw_data=True to preserve original API JSON
        config_with_raw = USPTOConfig(api_key=api_key, include_raw_data=True)
        client_with_raw = FinalPetitionDecisionsClient(config=config_with_raw)

        try:
            # Get decision with raw data
            response = client_with_raw.search_decisions(
                query=f"petitionDecisionRecordIdentifier:{sample_petition_decision_id}",
                limit=1,
            )

            if response is None or response.count == 0:
                pytest.skip(
                    f"No decision found for raw API comparison: {sample_petition_decision_id}"
                )

            assert (
                response.raw_data is not None
            ), "raw_data should be populated when include_raw_data=True"

            # Parse the raw API response JSON
            import json

            raw_api_dict = json.loads(response.raw_data)

            # Convert the model back to dict
            to_dict_output = response.to_dict()

            # Fields that are expected to be in raw API but not in model serialization
            # (these are API metadata, not domain data)
            # expected_missing_fields = {"requestIdentifier"}
            expected_missing_fields = {}

            # Remove expected metadata fields from raw API for comparison
            raw_api_dict_filtered = {
                k: v
                for k, v in raw_api_dict.items()
                if k not in expected_missing_fields
            }

            # Deep comparison of the two dictionaries
            def compare_dicts(dict1, dict2, path=""):
                """Recursively compare two dictionaries and report differences."""
                differences = []

                # Check keys present in dict1 but not dict2
                keys1 = set(dict1.keys())
                keys2 = set(dict2.keys())

                missing_in_dict2 = keys1 - keys2
                if missing_in_dict2:
                    differences.append(
                        f"Keys in to_dict but not in raw API at {path}: {missing_in_dict2}"
                    )

                missing_in_dict1 = keys2 - keys1
                if missing_in_dict1:
                    differences.append(
                        f"Keys in raw API but not in to_dict at {path}: {missing_in_dict1}"
                    )

                # Compare values for common keys
                for key in keys1 & keys2:
                    val1 = dict1[key]
                    val2 = dict2[key]
                    current_path = f"{path}.{key}" if path else key

                    if type(val1) is not type(val2):
                        differences.append(
                            f"Type mismatch at {current_path}: {type(val1).__name__} vs {type(val2).__name__}"
                        )
                    elif isinstance(val1, dict):
                        differences.extend(compare_dicts(val1, val2, current_path))
                    elif isinstance(val1, list):
                        if len(val1) != len(val2):
                            differences.append(
                                f"List length mismatch at {current_path}: {len(val1)} vs {len(val2)}"
                            )
                        else:
                            for i, (item1, item2) in enumerate(zip(val1, val2)):
                                if isinstance(item1, dict) and isinstance(item2, dict):
                                    differences.extend(
                                        compare_dicts(
                                            item1, item2, f"{current_path}[{i}]"
                                        )
                                    )
                                elif item1 != item2:
                                    differences.append(
                                        f"Value mismatch at {current_path}[{i}]: {item1!r} vs {item2!r}"
                                    )
                    elif val1 != val2:
                        differences.append(
                            f"Value mismatch at {current_path}: {val1!r} vs {val2!r}"
                        )

                return differences

            # Perform the comparison
            differences = compare_dicts(to_dict_output, raw_api_dict_filtered)

            # If there are differences, print them and fail
            if differences:
                diff_report = "\n".join(
                    differences[:20]
                )  # Limit to first 20 differences
                if len(differences) > 20:
                    diff_report += f"\n... and {len(differences) - 20} more differences"
                pytest.fail(
                    f"to_dict() output does not match raw API response. Differences found:\n{diff_report}"
                )

        except USPTOApiNotFoundError:
            pytest.skip(
                f"Decision not found (404) for raw API comparison: {sample_petition_decision_id}"
            )
        except USPTOApiError as e:
            pytest.skip(f"Raw API comparison failed due to API error: {e}")

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
                assert isinstance(response.petition_decision_data[0], PetitionDecision)
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
            with open(file_path, encoding="utf-8") as f:
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
        max_decisions = 10  # Only test first 10 decisions to keep test fast

        total_decisions = 0

        try:
            for decision in petition_decisions_client.paginate_decisions(
                limit=page_size, query="firstApplicantName:*"
            ):
                assert isinstance(decision, PetitionDecision)
                assert decision.petition_decision_record_identifier is not None

                total_decisions += 1

                if total_decisions >= max_decisions:
                    break

            assert total_decisions > 0, "Should have retrieved at least one decision"

        except USPTOApiError as e:
            pytest.skip(f"Pagination test failed: {e}")

    def test_decision_with_documents_and_download(
        self,
        petition_decisions_client: FinalPetitionDecisionsClient,
        sample_petition_decision_id: str,
    ) -> None:
        """Test retrieving a decision with documents and downloading them."""
        try:
            # Get decision with documents
            response = petition_decisions_client.get_decision_by_id(
                petition_decision_record_identifier=sample_petition_decision_id,
                include_documents=True,
            )

            assert response is not None
            assert isinstance(response, PetitionDecision)

            if response and response.document_bag and len(response.document_bag) > 0:
                doc = response.document_bag[0]
                assert isinstance(doc, PetitionDecisionDocument)
                assert doc.document_identifier is not None

                # If document has download options, test downloading
                if doc.download_option_bag and len(doc.download_option_bag) > 0:
                    download_option = doc.download_option_bag[0]
                    if download_option.download_url:
                        file_path = (
                            petition_decisions_client.download_petition_document(
                                download_option, destination_path=TEST_DOWNLOAD_DIR
                            )
                        )

                        assert file_path is not None
                        assert os.path.exists(file_path)
                        assert os.path.getsize(file_path) > 0
            else:
                pytest.fail("No decisions with documents found")

        except USPTOApiError as e:
            pytest.fail(f"Document retrieval test failed with API error: {e}")

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
        assert response.count is not None and response.count >= 0

        if response.count is not None and response.count > 0:
            assert len(response.petition_decision_data_bag) <= 10

    def test_decision_type_code_enum(
        self, petition_decisions_client: FinalPetitionDecisionsClient
    ) -> None:
        """Test that decision type codes are properly parsed into enums."""
        try:
            response = petition_decisions_client.search_decisions(limit=10)

            if response.count == 0:
                pytest.fail("No decisions available to test decision type codes")

            # Find a decision with a decision_type_code
            found = False
            for decision in response.petition_decision_data_bag:
                if decision.decision_type_code:
                    # Should be a valid DecisionTypeCode enum or string
                    assert isinstance(
                        decision.decision_type_code, (DecisionTypeCode, str)
                    )
                    found = True
                    break

            if not found:
                pytest.fail("No decisions with decision_type_code found in 10 results")

        except USPTOApiError as e:
            pytest.fail(f"Decision type code test failed with API error: {e}")

    def test_document_direction_category_enum(
        self,
        petition_decisions_client: FinalPetitionDecisionsClient,
        sample_petition_decision_id: str,
    ) -> None:
        """Test that document direction categories are properly parsed into enums."""
        try:
            # Get decision with documents - same pattern as test_decision_with_documents_and_download
            response = petition_decisions_client.get_decision_by_id(
                petition_decision_record_identifier=sample_petition_decision_id,
                include_documents=True,
            )

            assert response is not None
            assert isinstance(response, PetitionDecision)

            # Find a document with a direction category
            found = False
            if response and response.document_bag and len(response.document_bag) > 0:
                for doc in response.document_bag:
                    if doc.direction_category:
                        # Should be a valid DocumentDirectionCategory enum or string
                        assert isinstance(
                            doc.direction_category,
                            (DocumentDirectionCategory, str),
                        )
                        found = True
                        break
            else:
                pytest.fail(
                    f"No documents found to test in decision: {sample_petition_decision_id}"
                )
            if not found:
                pytest.fail(
                    f"No documents with direction categories found to test in decision: {sample_petition_decision_id}"
                )

        except USPTOApiError as e:
            pytest.fail(f"Document direction category test failed with API error: {e}")
