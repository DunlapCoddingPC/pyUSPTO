"""
Integration tests for the USPTO PTAB Interferences API client.

This module contains integration tests that make real API calls to the USPTO PTAB Interferences API.
These tests are optional and are skipped by default unless the ENABLE_INTEGRATION_TESTS
environment variable is set to 'true'.
"""

import os

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
            pytest.skip(
                f"PTAB Interferences API error during search_decisions GET: {e}"
            )

    def test_search_decisions_with_convenience_params(
        self, ptab_interferences_client: PTABInterferencesClient
    ) -> None:
        """Test searching interference decisions with convenience parameters."""
        try:
            response = ptab_interferences_client.search_decisions(
                interference_outcome_category_q="Final Decision",
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
                                "Final Decision"
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
            pytest.skip(
                f"PTAB Interferences API error during search_decisions POST: {e}"
            )

    def test_search_decisions_with_date_filters(
        self, ptab_interferences_client: PTABInterferencesClient
    ) -> None:
        """Test searching interference decisions with date range filters."""
        try:
            # Use date range that matches actual interference data
            response = ptab_interferences_client.search_decisions(
                decision_date_from_q="2000-01-01",
                decision_date_to_q="2010-12-31",
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
                decision_type_category_q="Decision",
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
                            assert (
                                "Decision"
                                in decision.document_data.decision_type_category
                            )

        except USPTOApiError as e:
            pytest.skip(
                f"PTAB Interferences API error during search by decision type: {e}"
            )

    def test_search_decisions_by_party(
        self, ptab_interferences_client: PTABInterferencesClient
    ) -> None:
        """Test searching interference decisions by party name."""
        try:
            # Search for senior or junior party with wildcard to ensure results
            response = ptab_interferences_client.search_decisions(
                senior_party_name_q="PATRICE",
                limit=2,
            )

            assert response is not None
            assert isinstance(response, PTABInterferenceResponse)
            assert response.count >= 0

            if response.count > 0:
                assert response.patent_interference_data_bag is not None

        except USPTOApiError as e:
            pytest.fail(f"PTAB Interferences API error during search by party: {e}")

    def test_search_decisions_by_patent_number(
        self, ptab_interferences_client: PTABInterferencesClient
    ) -> None:
        """Test searching interference decisions by patent number or application number."""
        try:
            # Use application number which is more common than patent number
            response = ptab_interferences_client.search_decisions(
                query="seniorPartyData.applicationNumberText:10618977",
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
            max_results = 10
            results = []
            for decision in ptab_interferences_client.paginate_decisions(
                query="interferenceNumber:*",
                limit=5,
            ):
                results.append(decision)
                if len(results) >= max_results:
                    break

            assert isinstance(results, list)
            if len(results) > 0:
                assert all(isinstance(d, PTABInterferenceDecision) for d in results)
                assert len(results) <= max_results

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
                query="interferenceMetaData.interferenceStyleName:*",
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

    def test_to_dict_matches_raw_api_response(self, api_key: str | None) -> None:
        """Test that to_dict() output matches the original API response stored in raw_data.

        This test compares the to_dict() serialization with the original API response
        to ensure that the model correctly reconstructs the API format.
        """
        # Create a config with include_raw_data=True to preserve original API data
        config_with_raw = USPTOConfig(api_key=api_key, include_raw_data=True)
        client_with_raw = PTABInterferencesClient(config=config_with_raw)

        try:
            # Search for any interference decision
            response = client_with_raw.search_decisions(
                query="interferenceNumber:*",
                limit=1,
            )

            if response is None or response.count == 0:
                pytest.skip(
                    "No interference decisions found for raw API comparison test"
                )

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
            pytest.skip(f"Raw API comparison test failed with API error: {e}")

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
