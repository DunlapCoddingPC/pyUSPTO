"""
Integration tests for the USPTO Petition Decisions API clients.

This module contains integration tests that make real API calls to the USPTO Petition Decisions API.
These tests are optional and are skipped by default unless the ENABLE_INTEGRATION_TESTS
environment variable is set to 'true'.
"""

import os
from collections.abc import Iterable
from datetime import date

import pytest

from pyUSPTO.clients import FinalPetitionDecisionsClient, PetitionDecisionsClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.exceptions import USPTOApiError, USPTOApiNotFoundError
from pyUSPTO.models.petition_decisions import (
    DecisionTypeCode,
    PetitionDecision,
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
def petition_decisions_client(config: USPTOConfig) -> PetitionDecisionsClient:
    """
    Create a PetitionDecisionsClient instance for integration tests.

    Uses module scope to reuse the same client for all tests in the module,
    reducing overhead from creating multiple client instances.

    Args:
        config: The configuration instance

    Returns:
        PetitionDecisionsClient: A client instance
    """
    return PetitionDecisionsClient(config=config)


@pytest.fixture(scope="module")
def final_petition_decisions_client(
    config: USPTOConfig,
) -> FinalPetitionDecisionsClient:
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
    petition_decisions_client: PetitionDecisionsClient,
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

        pytest.fail(
            "Could not retrieve a sample petition decision. Ensure API is reachable."
        )

    except USPTOApiError as e:
        pytest.fail(f"Could not fetch sample petition decision due to API error: {e}")
    except Exception as e:
        pytest.fail(
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
    pytest.fail("Sample petition decision does not have a record identifier")
    return ""


class TestPetitionDecisionsIntegration:
    """Integration tests for the PetitionDecisionsClient."""

    # Known decision ID for consistent testing (update with a stable ID from the API)
    KNOWN_DECISION_ID = None  # TODO: Add a known stable decision ID when available

    def test_search_decisions_basic(
        self, petition_decisions_client: PetitionDecisionsClient
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
        self, petition_decisions_client: PetitionDecisionsClient
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
            pytest.fail("No records found matching query criteria")
        except USPTOApiError as e:
            pytest.fail(f"Query search failed: {e}")

    def test_search_decisions_with_application_number(
        self,
        petition_decisions_client: PetitionDecisionsClient,
        sample_petition_decision: PetitionDecision,
    ) -> None:
        """Test searching using convenience application_number_q parameter."""
        # Use the application number from the sample decision
        if not sample_petition_decision.application_number_text:
            pytest.fail(
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
                assert found, (
                    f"Expected to find application number {app_num} in results"
                )
        except USPTOApiError as e:
            pytest.fail(f"Application number search failed: {e}")

    def test_search_decisions_with_patent_number(
        self, petition_decisions_client: PetitionDecisionsClient
    ) -> None:
        """Test searching using convenience patent_number_q parameter."""
        response = petition_decisions_client.search_decisions(
            patent_number_q="12311325", limit=5
        )

        assert response.count == 1
        assert [
            (
                d.petition_decision_record_identifier,
                d.application_number_text,
                d.patent_number,
            )
            for d in response.petition_decision_data_bag
        ] == [("1a552446-1d2b-570a-9bb6-b4fef39b0a91", "17765301", "12311325")]

    def test_search_decisions_with_technology_center(
        self, petition_decisions_client: PetitionDecisionsClient
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
        self, petition_decisions_client: PetitionDecisionsClient
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
        petition_decisions_client: PetitionDecisionsClient,
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
            assert decision.decided_petition_type_code in {"A", "B", "C", "D"}
        except USPTOApiNotFoundError:
            pytest.fail(
                f"Decision not found (404) for ID {sample_petition_decision_id}"
            )
        except USPTOApiError as e:
            pytest.fail(f"Failed to get decision by ID: {e}")

    def test_round_trip_data_integrity(
        self,
        petition_decisions_client: PetitionDecisionsClient,
        sample_petition_decision_id: str,
    ) -> None:
        """Test that parsing and serialization preserves data (round-trip test)."""
        try:
            # Get decision from API
            original = petition_decisions_client.get_decision_by_id(
                sample_petition_decision_id
            )

            if original is None:
                pytest.fail(
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
            assert (
                reconstructed.decided_petition_type_code
                == original.decided_petition_type_code
            )
            assert (
                reconstructed.last_modified_date_time
                == original.last_modified_date_time
            )

            if original.decision_date:
                assert reconstructed.decision_date == original.decision_date

            if original.application_number_text:
                assert (
                    reconstructed.application_number_text
                    == original.application_number_text
                )

        except USPTOApiNotFoundError:
            pytest.fail(
                f"Decision not found (404) for round-trip test: {sample_petition_decision_id}"
            )
        except USPTOApiError as e:
            pytest.fail(f"Round-trip test failed due to API error: {e}")

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
        # pytest.fail(
        #     "Test disabled pending USPTO API fix for datetime format. See issue #17"
        # )

        # Create a config with include_raw_data=True to preserve original API JSON
        config_with_raw = USPTOConfig(api_key=api_key, include_raw_data=True)
        client_with_raw = PetitionDecisionsClient(config=config_with_raw)

        try:
            # Get decision with raw data
            response = client_with_raw.search_decisions(
                query=f"petitionDecisionRecordIdentifier:{sample_petition_decision_id}",
                limit=1,
            )

            if response is None or response.count == 0:
                pytest.fail(
                    f"No decision found for raw API comparison: {sample_petition_decision_id}"
                )

            assert response.raw_data is not None, (
                "raw_data should be populated when include_raw_data=True"
            )

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
            pytest.fail(
                f"Decision not found (404) for raw API comparison: {sample_petition_decision_id}"
            )
        except USPTOApiError as e:
            pytest.fail(f"Raw API comparison failed due to API error: {e}")

    def test_get_decision_by_invalid_id(
        self, petition_decisions_client: PetitionDecisionsClient
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
        self, petition_decisions_client: PetitionDecisionsClient
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
            pytest.fail(f"Download endpoint failed: {e}")

    def test_download_decisions_csv(
        self, petition_decisions_client: PetitionDecisionsClient
    ) -> None:
        """Test downloading petition decisions in CSV format to file."""
        try:
            file_path = petition_decisions_client.download_decisions(
                format="csv",
                decision_date_from_q="2023-01-01",
                limit=2,
                destination=TEST_DOWNLOAD_DIR,
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
            pytest.fail(f"CSV download endpoint failed: {e}")

    def test_paginate_decisions(
        self, petition_decisions_client: PetitionDecisionsClient
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
            pytest.fail(f"Pagination test failed: {e}")

    def test_paginate_decisions_get_yields_each_decision_once(
        self, petition_decisions_client: PetitionDecisionsClient
    ) -> None:
        """Test GET pagination returns every decision exactly once."""
        query = "decisionDate:2024-03-05"
        # USPTO adds and removes decisions over time, so compare against the
        # API's own total rather than a fixed number
        total = petition_decisions_client.search_decisions(query=query, limit=1).count

        ids = [
            d.petition_decision_record_identifier
            for d in petition_decisions_client.paginate_decisions(
                query=query,
                limit=50,
                fields="petitionDecisionRecordIdentifier",
            )
        ]

        assert len(ids) == total
        assert len(set(ids)) == total

    def test_paginate_decisions_yields_nothing_for_no_match(
        self, petition_decisions_client: PetitionDecisionsClient
    ) -> None:
        """Test pagination over a search with no matches yields nothing."""
        decisions = list(
            petition_decisions_client.paginate_decisions(
                query="applicationNumberText:00000001"
            )
        )

        assert decisions == []

    def test_paginate_decisions_post_yields_each_decision_once(
        self, petition_decisions_client: PetitionDecisionsClient
    ) -> None:
        """Test POST pagination returns every decision exactly once."""
        query = "decisionDate:2024-03-05"
        # USPTO adds and removes decisions over time, so compare against the
        # API's own total rather than a fixed number
        total = petition_decisions_client.search_decisions(query=query, limit=1).count

        ids = [
            d.petition_decision_record_identifier
            for d in petition_decisions_client.paginate_decisions(
                post_body={
                    "q": query,
                    "fields": ["petitionDecisionRecordIdentifier"],
                }
            )
        ]

        assert len(ids) == total
        assert len(set(ids)) == total

    def test_decision_with_documents_and_download(
        self, petition_decisions_client: PetitionDecisionsClient
    ) -> None:
        """Test a lookup by ID returns the decision's documents and the PDF downloads."""
        decision_id = "1a552446-1d2b-570a-9bb6-b4fef39b0a91"
        decision = petition_decisions_client.get_decision_by_id(decision_id)

        assert isinstance(decision, PetitionDecision)
        assert decision.petition_decision_record_identifier == decision_id
        assert decision.application_number_text == "17765301"
        assert [
            (doc.document_identifier, doc.document_code)
            for doc in decision.document_bag
        ] == [("M6ATX5A7WFYBX90", "PPH.DECISION")]
        options = decision.document_bag[0].download_option_bag
        assert [opt.mime_type_identifier for opt in options] == [
            "PDF",
            "PNG",
            "XML",
            "MS_WORD",
        ]
        assert options[0].page_total_quantity == 3

        file_path = petition_decisions_client.download_petition_document(
            options[0], destination=TEST_DOWNLOAD_DIR, overwrite=True
        )

        assert os.path.basename(file_path) == "M6ATX5A7WFYBX90.pdf"
        with open(file_path, "rb") as f:
            pdf = f.read()
        # USPTO renders the PDF on each request, so its bytes and size vary with
        # the time; check that it is the right document and that it is complete
        assert pdf[:8] == b"%PDF-1.2"
        assert b"/Title (DocumentId M6ATX5A7WFYBX90)" in pdf
        assert pdf.endswith(b"%%EOF\r\n")

    def test_search_decisions_with_multiple_params(
        self, petition_decisions_client: PetitionDecisionsClient
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

    def test_decided_petition_type_code(
        self, petition_decisions_client: PetitionDecisionsClient
    ) -> None:
        """Test that the decided type fields parse and map to DecisionTypeCode."""
        response = petition_decisions_client.search_decisions(
            application_number_q="17765301", limit=1
        )

        assert response.count == 1
        decision = response.petition_decision_data_bag[0]
        assert decision.decided_petition_type_code == "C"
        assert decision.decided_petition_type_code_description_text == "DENIED"
        assert (
            DecisionTypeCode(decision.decided_petition_type_code)
            is DecisionTypeCode.DENIED
        )
        assert decision.final_petition_decision_indicator is True
        assert decision.decision_mail_date == date(2025, 1, 23)

    def test_search_by_decided_petition_type_code(
        self, petition_decisions_client: PetitionDecisionsClient
    ) -> None:
        """Test that decided_petition_type_code_q filters on decidedPetitionTypeCode."""
        response = petition_decisions_client.search_decisions(
            decided_petition_type_code_q="B", limit=5
        )

        assert len(response.petition_decision_data_bag) == 5
        for decision in response.petition_decision_data_bag:
            assert decision.decided_petition_type_code == "B"
            assert (
                decision.decided_petition_type_code_description_text
                == "GRANTED-IN-PART"
            )


def _sorted_record_ids(decisions: Iterable[PetitionDecision]) -> list[str]:
    """Return the record identifiers of the given decisions, sorted."""
    return sorted(d.petition_decision_record_identifier for d in decisions)


class TestFinalPetitionDecisionsClientIntegration:
    """Integration tests for the FinalPetitionDecisionsClient.

    Application 16591555 has four petition decisions, exactly one of them final.
    Tests that also query PetitionDecisionsClient use it as the control, which
    sees all four.
    """

    APPLICATION_NUMBER = "16591555"
    FINAL_DECISION_ID = "f2137ac1-0bde-5b84-8299-6faf96a5fb9f"
    ALL_DECISION_IDS = sorted(
        [
            FINAL_DECISION_ID,
            "ea57f096-cea9-53a2-9a5d-6bbb9aca0260",
            "5f1f2752-9680-5fd6-aada-0d9b198540d3",
            "0332e5e1-f6f7-5efa-a478-405e3d479e29",
        ]
    )
    # Non-final decision on application 16947346.
    NON_FINAL_DECISION_ID = "0b9ea48d-43c9-5197-8bf1-126d965816a7"
    # Final decision on application 17765301.
    OTHER_FINAL_DECISION_ID = "1a552446-1d2b-570a-9bb6-b4fef39b0a91"

    def test_search_decisions_returns_only_final(
        self,
        petition_decisions_client: PetitionDecisionsClient,
        final_petition_decisions_client: FinalPetitionDecisionsClient,
    ) -> None:
        """Test that a GET search returns only the application's final decision."""
        all_response = petition_decisions_client.search_decisions(
            application_number_q=self.APPLICATION_NUMBER
        )
        assert all_response.count == 4
        assert (
            _sorted_record_ids(all_response.petition_decision_data_bag)
            == self.ALL_DECISION_IDS
        )

        final_response = final_petition_decisions_client.search_decisions(
            application_number_q=self.APPLICATION_NUMBER
        )
        assert final_response.count == 1
        assert _sorted_record_ids(final_response.petition_decision_data_bag) == [
            self.FINAL_DECISION_ID
        ]

    def test_search_decisions_post_returns_only_final(
        self,
        petition_decisions_client: PetitionDecisionsClient,
        final_petition_decisions_client: FinalPetitionDecisionsClient,
    ) -> None:
        """Test that a POST search returns only the application's final decision."""
        post_body = {"q": f"applicationNumberText:{self.APPLICATION_NUMBER}"}

        all_response = petition_decisions_client.search_decisions(post_body=post_body)
        assert all_response.count == 4
        assert (
            _sorted_record_ids(all_response.petition_decision_data_bag)
            == self.ALL_DECISION_IDS
        )

        final_response = final_petition_decisions_client.search_decisions(
            post_body=post_body
        )
        assert final_response.count == 1
        assert _sorted_record_ids(final_response.petition_decision_data_bag) == [
            self.FINAL_DECISION_ID
        ]

    def test_get_decision_by_id_returns_none_for_non_final(
        self,
        petition_decisions_client: PetitionDecisionsClient,
        final_petition_decisions_client: FinalPetitionDecisionsClient,
    ) -> None:
        """Test that the final client returns None for a non-final decision."""
        decision = petition_decisions_client.get_decision_by_id(
            self.NON_FINAL_DECISION_ID
        )
        assert isinstance(decision, PetitionDecision)
        assert (
            decision.petition_decision_record_identifier == self.NON_FINAL_DECISION_ID
        )
        assert decision.application_number_text == "16947346"
        assert decision.final_petition_decision_indicator is False

        assert (
            final_petition_decisions_client.get_decision_by_id(
                self.NON_FINAL_DECISION_ID
            )
            is None
        )

    def test_get_decision_by_id_returns_final_decision(
        self, final_petition_decisions_client: FinalPetitionDecisionsClient
    ) -> None:
        """Test that the final client returns a final decision looked up by ID."""
        decision = final_petition_decisions_client.get_decision_by_id(
            self.OTHER_FINAL_DECISION_ID
        )
        assert isinstance(decision, PetitionDecision)
        assert (
            decision.petition_decision_record_identifier == self.OTHER_FINAL_DECISION_ID
        )
        assert decision.application_number_text == "17765301"
        assert decision.final_petition_decision_indicator is True

    def test_download_decisions_json_returns_only_final(
        self,
        petition_decisions_client: PetitionDecisionsClient,
        final_petition_decisions_client: FinalPetitionDecisionsClient,
    ) -> None:
        """Test that a JSON download contains only the application's final decision."""
        all_download = petition_decisions_client.download_decisions(
            format="json", application_number_q=self.APPLICATION_NUMBER
        )
        assert isinstance(all_download, PetitionDecisionDownloadResponse)
        assert (
            _sorted_record_ids(all_download.petition_decision_data)
            == self.ALL_DECISION_IDS
        )

        final_download = final_petition_decisions_client.download_decisions(
            format="json", application_number_q=self.APPLICATION_NUMBER
        )
        assert isinstance(final_download, PetitionDecisionDownloadResponse)
        assert _sorted_record_ids(final_download.petition_decision_data) == [
            self.FINAL_DECISION_ID
        ]

    def test_paginate_decisions_yields_all_decisions(
        self, petition_decisions_client: PetitionDecisionsClient
    ) -> None:
        """Test that the base client pages through all four decisions."""
        decisions = petition_decisions_client.paginate_decisions(
            application_number_q=self.APPLICATION_NUMBER, limit=2
        )
        assert _sorted_record_ids(decisions) == self.ALL_DECISION_IDS

    def test_paginate_decisions_yields_only_final(
        self, final_petition_decisions_client: FinalPetitionDecisionsClient
    ) -> None:
        """Test that the final client pages through only the final decision."""
        decisions = final_petition_decisions_client.paginate_decisions(
            application_number_q=self.APPLICATION_NUMBER, limit=2
        )
        assert _sorted_record_ids(decisions) == [self.FINAL_DECISION_ID]
