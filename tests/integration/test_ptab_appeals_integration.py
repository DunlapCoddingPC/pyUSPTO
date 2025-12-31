"""
Integration tests for the USPTO PTAB Appeals API client.

This module contains integration tests that make real API calls to the USPTO PTAB Appeals API.
These tests are optional and are skipped by default unless the ENABLE_INTEGRATION_TESTS
environment variable is set to 'true'.
"""

import os

import pytest

from pyUSPTO.clients import PTABAppealsClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.exceptions import USPTOApiError
from pyUSPTO.models.ptab import AppealMetaData, PTABAppealDecision, PTABAppealResponse

# Import shared fixtures
from tests.integration.conftest import TEST_DOWNLOAD_DIR

# Skip all tests in this module unless ENABLE_INTEGRATION_TESTS is set to 'true'
pytestmark = pytest.mark.skipif(
    os.environ.get("ENABLE_INTEGRATION_TESTS", "").lower() != "true",
    reason="Integration tests are disabled. Set ENABLE_INTEGRATION_TESTS=true to enable.",
)


@pytest.fixture(scope="class")
def ptab_appeals_client(config: USPTOConfig) -> PTABAppealsClient:
    """
    Create a PTABAppealsClient instance for integration tests.

    Args:
        config: The configuration instance

    Returns:
        PTABAppealsClient: A client instance
    """
    return PTABAppealsClient(config=config)


@pytest.fixture(scope="class")
def appeals_with_download_uris(
    ptab_appeals_client: PTABAppealsClient,
) -> PTABAppealResponse:
    """
    Fetch appeals with download URIs once and cache for all download tests.

    This fixture is scoped to the class level to avoid running the same
    search query multiple times across different download tests.

    Args:
        ptab_appeals_client: The client instance

    Returns:
        PTABAppealResponse: Response containing appeals with download URIs
    """
    return ptab_appeals_client.search_decisions(
        query="appealMetaData.applicationTypeCategory:Appeal",
        limit=5,
    )


class TestPTABAppealsIntegration:
    """Integration tests for the PTABAppealsClient."""

    def test_search_decisions_get(self, ptab_appeals_client: PTABAppealsClient) -> None:
        """Test searching PTAB appeal decisions using GET method."""
        try:
            response = ptab_appeals_client.search_decisions(
                query="appealMetaData.applicationTypeCategory:Appeal",
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
            else:
                pytest.fail("There should always be a response to this query.")

        except USPTOApiError as e:
            pytest.fail(f"PTAB Appeals API error during search_decisions GET: {e}")

    def test_search_decisions_with_convenience_params(
        self, ptab_appeals_client: PTABAppealsClient
    ) -> None:
        """Test searching appeal decisions with application number."""
        try:
            # Use direct query since applicationNumberText is nested under appellantData
            response = ptab_appeals_client.search_decisions(
                query="appellantData.applicationNumberText:12608694",
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
                        assert isinstance(decision.appeal_meta_data, AppealMetaData)

        except USPTOApiError as e:
            pytest.fail(
                f"PTAB Appeals API error during search_decisions with convenience params: {e}"
            )

    def test_search_decisions_post(
        self, ptab_appeals_client: PTABAppealsClient
    ) -> None:
        """Test searching PTAB appeal decisions using POST method."""
        post_body = {
            "q": "appealMetaData.applicationTypeCategory:Appeal",
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
            pytest.fail(f"PTAB Appeals API error during search_decisions POST: {e}")

    def test_search_decisions_with_date_filters(
        self, ptab_appeals_client: PTABAppealsClient
    ) -> None:
        """Test searching appeal decisions with date range filters."""
        try:
            # Use direct query with correct field name (decisionIssueDate, not decisionDate)
            response = ptab_appeals_client.search_decisions(
                query="decisionData.decisionIssueDate:[2014-01-01 TO 2020-12-31]",
                limit=2,
            )

            assert response is not None
            assert isinstance(response, PTABAppealResponse)
            assert response.count >= 0

            if response.count > 0:
                assert response.patent_appeal_data_bag is not None

        except USPTOApiError as e:
            pytest.fail(
                f"PTAB Appeals API error during search_decisions with date filters: {e}"
            )

    def test_search_decisions_by_decision_type(
        self, ptab_appeals_client: PTABAppealsClient
    ) -> None:
        """Test searching appeal decisions by decision type."""
        try:
            # Use direct query since decisionTypeCategory is nested under decisionData
            response = ptab_appeals_client.search_decisions(
                query="decisionData.decisionTypeCategory:Decision",
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
                            assert (
                                "Decision"
                                in decision.decision_data.decision_type_category
                            )

        except USPTOApiError as e:
            pytest.fail(f"PTAB Appeals API error during search by decision type: {e}")

    def test_search_decisions_by_appellant(
        self, ptab_appeals_client: PTABAppealsClient
    ) -> None:
        """Test searching appeal decisions by inventor name."""
        try:
            # Search by inventor name (realPartyInInterestName contains inventor info)
            response = ptab_appeals_client.search_decisions(
                query="appellantData.inventorName:*",
                limit=2,
            )

            assert response is not None
            assert isinstance(response, PTABAppealResponse)
            assert response.count >= 0

            if response.count > 0:
                assert response.patent_appeal_data_bag is not None

        except USPTOApiError as e:
            pytest.fail(f"PTAB Appeals API error during search by appellant: {e}")

    def test_paginate_decisions(self, ptab_appeals_client: PTABAppealsClient) -> None:
        """Test paginating through appeal decisions."""
        page_size = 5
        max_decisions = 10  # Only test first 10 decisions to keep test fast

        total_decisions = 0

        try:
            for decision in ptab_appeals_client.paginate_decisions(
                query="appealMetaData.applicationTypeCategory:Appeal",
                limit=page_size,
            ):
                assert isinstance(decision, PTABAppealDecision)
                assert decision.appeal_number is not None

                total_decisions += 1

                if total_decisions >= max_decisions:
                    break

            assert total_decisions > 0, "Should have retrieved at least one decision"

        except USPTOApiError as e:
            pytest.fail(f"Pagination test failed with API error: {e}")

    def test_search_with_optional_params(
        self, ptab_appeals_client: PTABAppealsClient
    ) -> None:
        """Test searching with optional parameters like sort and facets."""
        try:
            response = ptab_appeals_client.search_decisions(
                query="appealMetaData.applicationTypeCategory:Appeal",
                limit=2,
                sort="appealNumber desc",
                offset=0,
            )

            assert response is not None
            assert isinstance(response, PTABAppealResponse)
            assert response.count >= 0

        except USPTOApiError as e:
            pytest.fail(
                f"PTAB Appeals API error during search with optional params: {e}"
            )

    def test_to_dict_matches_raw_api_response(self, api_key: str | None) -> None:
        """Test that to_dict() output matches the original API response stored in raw_data.

        This test compares the to_dict() serialization with the original API response
        to ensure that the model correctly reconstructs the API format.
        """
        # Create a config with include_raw_data=True to preserve original API data
        config_with_raw = USPTOConfig(api_key=api_key, include_raw_data=True)
        client_with_raw = PTABAppealsClient(config=config_with_raw)

        try:
            # Search for a known appeal number
            response = client_with_raw.search_decisions(
                query="appealNumber:2015000194",
                limit=1,
            )

            if response is None or response.count == 0:
                pytest.fail("No decision found for raw API comparison test")

            assert (
                response.raw_data is not None
            ), "raw_data should be populated when include_raw_data=True"

            # PTAB models store raw_data as dict (not JSON string like other models)
            assert isinstance(
                response.raw_data, dict
            ), "raw_data should be a dictionary"

            # Get the raw API response dict
            raw_api_dict = response.raw_data

            # Convert the model back to dict
            to_dict_output = response.to_dict()

            # Deep comparison function
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
            differences = compare_dicts(to_dict_output, raw_api_dict)

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

        except USPTOApiError as e:
            pytest.fail(f"Raw API comparison test failed with API error: {e}")

    def test_download_appeal_archive(
        self,
        ptab_appeals_client: PTABAppealsClient,
        appeals_with_download_uris: PTABAppealResponse,
    ) -> None:
        """Test downloading appeal archive file without extraction."""
        try:
            if (
                not appeals_with_download_uris
                or not appeals_with_download_uris.patent_appeal_data_bag
            ):
                pytest.skip("No appeal decisions found for archive download test")

            # Try multiple appeals until one downloads successfully
            last_error = None
            for decision in appeals_with_download_uris.patent_appeal_data_bag:
                if (
                    not decision.appeal_meta_data
                    or not decision.appeal_meta_data.file_download_uri
                ):
                    continue

                try:
                    file_path = ptab_appeals_client.download_appeal_archive(
                        decision.appeal_meta_data,
                        destination=TEST_DOWNLOAD_DIR,
                        overwrite=True,
                    )

                    # If we get here, download succeeded
                    assert file_path is not None
                    assert os.path.exists(file_path)
                    assert os.path.getsize(file_path) > 0
                    assert file_path.endswith((".zip", ".tar", ".tar.gz", ".tgz"))
                    return  # Test passed!

                except USPTOApiError as e:
                    # Save error and try next appeal
                    last_error = e
                    continue

            # If we tried all appeals and none worked, fail with the last error
            if last_error:
                pytest.fail(f"All appeal archives failed to download. Last error: {last_error}")
            else:
                pytest.skip("No appeal with valid file_download_uri found")

        except USPTOApiError as e:
            pytest.fail(f"PTAB Appeals API error during search: {e}")

    def test_download_appeal_documents(
        self,
        ptab_appeals_client: PTABAppealsClient,
        appeals_with_download_uris: PTABAppealResponse,
    ) -> None:
        """Test downloading and extracting appeal documents."""
        try:
            if (
                not appeals_with_download_uris
                or not appeals_with_download_uris.patent_appeal_data_bag
            ):
                pytest.skip("No appeal decisions found for documents download test")

            # Try multiple appeals until one downloads successfully
            last_error = None
            for decision in appeals_with_download_uris.patent_appeal_data_bag:
                if (
                    not decision.appeal_meta_data
                    or not decision.appeal_meta_data.file_download_uri
                ):
                    continue

                try:
                    extracted_path = ptab_appeals_client.download_appeal_documents(
                        decision.appeal_meta_data,
                        destination=TEST_DOWNLOAD_DIR,
                        overwrite=True,
                    )

                    # If we get here, download and extraction succeeded
                    assert extracted_path is not None
                    assert os.path.exists(extracted_path)
                    return  # Test passed!

                except USPTOApiError as e:
                    # Save error and try next appeal
                    last_error = e
                    continue

            # If we tried all appeals and none worked, fail with the last error
            if last_error:
                pytest.fail(f"All appeal documents failed to download. Last error: {last_error}")
            else:
                pytest.skip("No appeal with valid file_download_uri found")

        except USPTOApiError as e:
            pytest.fail(f"PTAB Appeals API error during search: {e}")

    def test_download_appeal_document(
        self, ptab_appeals_client: PTABAppealsClient
    ) -> None:
        """Test downloading individual appeal document."""
        try:
            response = ptab_appeals_client.search_decisions(
                query="appealMetaData.applicationTypeCategory:Appeal",
                limit=1,
            )

            if not response or not response.patent_appeal_data_bag:
                pytest.skip("No appeal decisions found for document download test")

            decision = response.patent_appeal_data_bag[0]
            if (
                not decision.document_data
                or not decision.document_data.file_download_uri
            ):
                pytest.skip("No file_download_uri available for test")

            file_path = ptab_appeals_client.download_appeal_document(
                decision.document_data,
                destination=TEST_DOWNLOAD_DIR,
                overwrite=True,
            )

            assert file_path is not None
            assert os.path.exists(file_path)
            assert os.path.getsize(file_path) > 0

        except USPTOApiError as e:
            pytest.fail(f"PTAB Appeals API error during document download: {e}")

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
