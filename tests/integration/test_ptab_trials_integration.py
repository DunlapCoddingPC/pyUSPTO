"""
Integration tests for the USPTO PTAB Trials API client.

This module contains integration tests that make real API calls to the USPTO PTAB Trials API.
These tests are optional and are skipped by default unless the ENABLE_INTEGRATION_TESTS
environment variable is set to 'true'.
"""

import os
from typing import Iterator, Optional

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

    def test_search_proceedings_get(self, ptab_trials_client: PTABTrialsClient) -> None:
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

    def test_search_documents_get(self, ptab_trials_client: PTABTrialsClient) -> None:
        """Test searching PTAB trial documents using GET method."""
        try:
            response = ptab_trials_client.search_documents(
                query="documentData.documentTypeDescriptionText:Exhibit",
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
                document_type_name_q="Exhibit",
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

    def test_search_documents_post(self, ptab_trials_client: PTABTrialsClient) -> None:
        """Test searching PTAB trial documents using POST method."""
        post_body = {
            "q": "trialMetaData.trialTypeCode:IPR",
            "pagination": {"offset": 0, "limit": 1},
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

    def test_search_decisions_get(self, ptab_trials_client: PTABTrialsClient) -> None:
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
                limit=1,
            )

            assert response is not None
            assert isinstance(response, PTABTrialDocumentResponse)
            assert response.count >= 0

            if response.count > 0:
                assert response.patent_trial_document_data_bag is not None
                for document in response.patent_trial_document_data_bag:
                    if document.trial_type_code:
                        assert document.trial_type_code == "IPR"

        except USPTOApiError as e:
            pytest.skip(
                f"PTAB Trials API error during search_decisions with convenience params: {e}"
            )

    def test_search_decisions_post(self, ptab_trials_client: PTABTrialsClient) -> None:
        """Test searching PTAB trial decisions using POST method."""
        post_body = {
            "q": "trialMetaData.trialTypeCode:IPR",
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

    def test_paginate_proceedings(self, ptab_trials_client: PTABTrialsClient) -> None:
        """Test paginating through trial proceedings."""
        try:
            # Limit to small number to avoid long test times
            max_results = 10
            results = []
            for proceeding in ptab_trials_client.paginate_proceedings(
                query="trialMetaData.trialTypeCode:IPR",
                limit=5,
            ):
                results.append(proceeding)
                if len(results) >= max_results:
                    break

            assert isinstance(results, list)
            if len(results) > 0:
                assert all(isinstance(p, PTABTrialProceeding) for p in results)
                assert len(results) <= max_results

        except USPTOApiError as e:
            pytest.skip(f"PTAB Trials API error during paginate_proceedings: {e}")

    def test_to_dict_matches_raw_api_response_proceedings(
        self, api_key: Optional[str]
    ) -> None:
        """Test that to_dict() output matches the original API response for trial proceedings.

        This test compares the to_dict() serialization with the original API response
        to ensure that the model correctly reconstructs the API format.
        """
        # Create a config with include_raw_data=True to preserve original API data
        config_with_raw = USPTOConfig(api_key=api_key, include_raw_data=True)
        client_with_raw = PTABTrialsClient(config=config_with_raw)

        try:
            # Search for trial proceedings
            response = client_with_raw.search_proceedings(
                query="trialMetaData.trialTypeCode:IPR",
                limit=1,
            )

            if response is None or response.count == 0:
                pytest.skip("No trial proceedings found for raw API comparison test")

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

                    if type(val1) != type(val2):
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

    def test_to_dict_matches_raw_api_response_documents(
        self, api_key: Optional[str]
    ) -> None:
        """Test that to_dict() output matches the original API response for trial documents.

        This test compares the to_dict() serialization with the original API response
        to ensure that the model correctly reconstructs the API format.
        """
        # Create a config with include_raw_data=True to preserve original API data
        config_with_raw = USPTOConfig(api_key=api_key, include_raw_data=True)
        client_with_raw = PTABTrialsClient(config=config_with_raw)

        try:
            # Search for trial documents
            response = client_with_raw.search_documents(
                query="trialMetaData.trialTypeCode:IPR",
                limit=1,
            )

            if response is None or response.count == 0:
                pytest.fail("No trial documents found for raw API comparison test")

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

                    if type(val1) != type(val2):
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

    def test_to_dict_matches_raw_api_response_trials(
        self, api_key: Optional[str]
    ) -> None:
        """Test that to_dict() output matches the original API response for trial decisions."""
        config_with_raw = USPTOConfig(api_key=api_key, include_raw_data=True)
        client_with_raw = PTABTrialsClient(config=config_with_raw)

        try:
            response = client_with_raw.search_decisions(
                query="trialMetaData.trialTypeCode:IPR",
                limit=1,
            )

            if response is None or response.count == 0:
                pytest.fail("No trial decisions found for raw API comparison test")

            assert response.raw_data is not None
            assert isinstance(response.raw_data, dict)

            raw_api_dict = response.raw_data
            to_dict_output = response.to_dict()

            def compare_dicts(dict1, dict2, path=""):
                differences = []
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

                for key in keys1 & keys2:
                    val1 = dict1[key]
                    val2 = dict2[key]
                    current_path = f"{path}.{key}" if path else key

                    if type(val1) != type(val2):
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

            differences = compare_dicts(to_dict_output, raw_api_dict)

            if differences:
                diff_report = "\n".join(differences[:20])
                if len(differences) > 20:
                    diff_report += f"\n... and {len(differences) - 20} more differences"
                pytest.fail(
                    f"to_dict() output does not match raw API response. Differences found:\n{diff_report}"
                )

        except USPTOApiError as e:
            pytest.skip(f"Raw API comparison test failed with API error: {e}")

    def test_invalid_query_handling(self, ptab_trials_client: PTABTrialsClient) -> None:
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
