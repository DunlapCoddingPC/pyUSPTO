"""
Integration tests for the USPTO Patent Data API client.

This module contains integration tests that make real API calls to the USPTO Patent Data API.
These tests are optional and are skipped by default unless the ENABLE_INTEGRATION_TESTS
environment variable is set to 'true'.
"""

import datetime
import os
from typing import Iterator, List, Optional

import pytest

# Import shared fixtures
from tests.integration.conftest import TEST_DOWNLOAD_DIR

from pyUSPTO.clients import PatentDataClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.exceptions import USPTOApiError, USPTOApiNotFoundError
from pyUSPTO.models.patent_data import (
    ApplicationContinuityData,
    ApplicationMetaData,
    Assignment,
    Document,
    DocumentBag,
    EventData,
    ForeignPriority,
    PatentDataResponse,
    PatentFileWrapper,
    PatentTermAdjustmentData,
    PrintedPublication,
    RecordAttorney,
    StatusCode,
    StatusCodeCollection,
    StatusCodeSearchResponse,
)

# Skip all tests in this module unless ENABLE_INTEGRATION_TESTS is set to 'true'
pytestmark = pytest.mark.skipif(
    os.environ.get("ENABLE_INTEGRATION_TESTS", "").lower() != "true",
    reason="Integration tests are disabled. Set ENABLE_INTEGRATION_TESTS=true to enable.",
)


@pytest.fixture(scope="module")
def patent_data_client(config: USPTOConfig) -> PatentDataClient:
    """
    Create a PatentDataClient instance for integration tests.

    Uses module scope to reuse the same client for all tests in the module,
    reducing overhead from creating multiple client instances.

    Args:
        config: The configuration instance

    Returns:
        PatentDataClient: A client instance
    """
    return PatentDataClient(config=config)


@pytest.fixture(scope="module")
def sample_application_number(patent_data_client: PatentDataClient) -> str:
    """Provides a sample application number for tests.

    Uses module scope to execute once per test module and cache the result,
    reducing redundant API calls from 11 to 1.
    """
    try:
        response = patent_data_client.search_applications(
            query='applicationMetaData.applicationTypeLabelName:Utility AND applicationMetaData.applicationStatusDescriptionText:"Patented Case"',
            limit=1,
        )
        if response.count > 0 and response.patent_file_wrapper_data_bag:
            app_num = response.patent_file_wrapper_data_bag[0].application_number_text
            if app_num:
                return app_num

        pytest.fail(
            "Could not retrieve a sample application number. Ensure API is reachable and query is valid."
        )

    except USPTOApiError as e:
        pytest.fail(f"Could not fetch sample application number due to API error: {e}")
    except Exception as e:
        pytest.fail(
            f"Could not fetch sample application number due to unexpected error: {e}"
        )
    return ""


class TestPatentDataIntegration:
    """Integration tests for the PatentDataClient."""

    KNOWN_APP_NUM_WITH_DOCS = "18045436"

    def test_search_applications_get(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test getting patent applications from the API using GET path of search_applications."""
        response = patent_data_client.search_applications(
            query="applicationMetaData.applicationTypeLabelName:Utility", limit=2
        )

        assert response is not None
        assert isinstance(response, PatentDataResponse)
        assert response.count > 0
        assert response.patent_file_wrapper_data_bag is not None
        assert len(response.patent_file_wrapper_data_bag) > 0
        assert len(response.patent_file_wrapper_data_bag) <= 2

        patent_wrapper = response.patent_file_wrapper_data_bag[0]
        assert isinstance(patent_wrapper, PatentFileWrapper)
        assert patent_wrapper.application_number_text is not None
        assert patent_wrapper.application_meta_data is not None
        assert isinstance(patent_wrapper.application_meta_data, ApplicationMetaData)

    def test_search_applications_with_convenience_q_param(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test searching for patents using convenience _q parameters of search_applications."""
        response = patent_data_client.search_applications(
            assignee_name_q="International Business Machines", limit=2
        )

        assert response is not None
        assert isinstance(response, PatentDataResponse)
        if response.count > 0:
            assert response.patent_file_wrapper_data_bag is not None
            assert len(response.patent_file_wrapper_data_bag) > 0
            assert len(response.patent_file_wrapper_data_bag) <= 2
            assert isinstance(
                response.patent_file_wrapper_data_bag[0], PatentFileWrapper
            )
        else:
            pytest.fail(
                f'No PatentDate returned for: `assignee_name_q="International Business Machines"`'
            )

    def test_get_application_by_number(
        self,
        patent_data_client: PatentDataClient,
    ) -> None:
        """Test getting a specific patent by application number."""
        patent_wrapper = patent_data_client.get_application_by_number(
            self.KNOWN_APP_NUM_WITH_DOCS
        )

        assert patent_wrapper is not None
        assert isinstance(patent_wrapper, PatentFileWrapper)
        assert patent_wrapper.application_number_text == self.KNOWN_APP_NUM_WITH_DOCS
        assert patent_wrapper.application_meta_data is not None
        assert isinstance(patent_wrapper.application_meta_data, ApplicationMetaData)
        assert patent_wrapper.application_meta_data.invention_title is not None

    def test_to_dict_matches_raw_api_response(self, api_key: Optional[str]) -> None:
        """Test that to_dict() output matches the original API response stored in raw_data.

        This test compares the to_dict() serialization with the original API response
        to ensure that the model correctly reconstructs the API format.
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
        client_with_raw = PatentDataClient(config=config_with_raw)

        # Use search_applications to get a PatentDataResponse (which has raw_data)
        response = client_with_raw.search_applications(
            application_number_q=self.KNOWN_APP_NUM_WITH_DOCS, limit=1
        )

        assert response is not None
        assert isinstance(response, PatentDataResponse)
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
        expected_missing_fields: set[str] = set()

        # Remove expected metadata fields from raw API for comparison
        raw_api_dict_filtered = {
            k: v for k, v in raw_api_dict.items() if k not in expected_missing_fields
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
                                    compare_dicts(item1, item2, f"{current_path}[{i}]")
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
            diff_report = "\n".join(differences[:20])  # Limit to first 20 differences
            if len(differences) > 20:
                diff_report += f"\n... and {len(differences) - 20} more differences"
            pytest.fail(
                f"to_dict() output does not match raw API response. Differences found:\n{diff_report}"
            )

    def test_round_trip_data_integrity(
        self, patent_data_client: PatentDataClient, sample_application_number: str
    ) -> None:
        """Test that parsing and serialization preserves data (round-trip test)."""
        # Get application from API
        original = patent_data_client.get_application_by_number(
            sample_application_number
        )

        assert original is not None

        # Convert to dict
        data_dict = original.to_dict()

        # Parse back from dict
        reconstructed = PatentFileWrapper.from_dict(data_dict)

        # Verify key fields match
        assert reconstructed.application_number_text == original.application_number_text

        if original.application_meta_data:
            assert reconstructed.application_meta_data is not None
            assert (
                reconstructed.application_meta_data.invention_title
                == original.application_meta_data.invention_title
            )
            assert (
                reconstructed.application_meta_data.filing_date
                == original.application_meta_data.filing_date
            )

    def test_get_status_codes(self, patent_data_client: PatentDataClient) -> None:
        """Test getting patent status codes."""
        status_codes_response = patent_data_client.get_status_codes()

        assert status_codes_response is not None
        assert isinstance(status_codes_response, StatusCodeSearchResponse)
        assert status_codes_response.status_code_bag is not None
        assert isinstance(status_codes_response.status_code_bag, StatusCodeCollection)
        assert len(status_codes_response.status_code_bag) > 0

        first_status_code = status_codes_response.status_code_bag[0]
        assert isinstance(first_status_code, StatusCode)
        assert first_status_code.code is not None
        assert first_status_code.description is not None

    def test_get_application_metadata(
        self, patent_data_client: PatentDataClient, sample_application_number: str
    ) -> None:
        """Test getting metadata for a patent application."""
        try:
            metadata = patent_data_client.get_application_metadata(
                sample_application_number
            )
            if metadata is None:
                pytest.fail(
                    f"No metadata available for application {sample_application_number}"
                )

            assert isinstance(metadata, ApplicationMetaData)
            assert metadata.invention_title is not None
            assert metadata.filing_date is not None
            assert isinstance(metadata.filing_date, datetime.date)
        except USPTOApiNotFoundError:
            pytest.fail(
                f"Metadata not found (404) for application {sample_application_number}"
            )
        except USPTOApiError as e:
            pytest.fail(
                f"API call for metadata failed for {sample_application_number}: {e}"
            )

    def test_get_application_adjustment(
        self, patent_data_client: PatentDataClient, sample_application_number: str
    ) -> None:
        """Test getting patent term adjustment data."""
        try:
            adjustment_data = patent_data_client.get_application_adjustment(
                sample_application_number
            )
            if adjustment_data is None:
                pytest.fail(f"No adjustment data for {sample_application_number}")

            assert isinstance(adjustment_data, PatentTermAdjustmentData)
            assert adjustment_data.adjustment_total_quantity is not None
        except USPTOApiNotFoundError:
            pytest.fail(
                f"Adjustment data not found (404) for application {sample_application_number}"
            )
        except USPTOApiError as e:
            pytest.fail(
                f"Adjustment data not available or API error for {sample_application_number}: {e}"
            )

    def test_get_application_assignment(
        self, patent_data_client: PatentDataClient, sample_application_number: str
    ) -> None:
        """Test getting assignment data."""
        try:
            assignments = patent_data_client.get_application_assignment(
                sample_application_number
            )
            if assignments is None:
                pytest.fail(
                    f"No assignment data (returned None) for {sample_application_number}"
                )

            assert isinstance(assignments, list)
            if not assignments:
                pytest.fail(
                    f"Assignment data list is empty for {sample_application_number}"
                )

            assert isinstance(assignments[0], Assignment)
            assert (
                assignments[0].reel_number is not None
                or assignments[0].frame_number is not None
            )
            if assignments[0].assignee_bag:
                assert assignments[0].assignee_bag[0].assignee_name_text is not None

        except USPTOApiNotFoundError:
            pytest.fail(
                f"Assignment data not found (404) for application {sample_application_number}"
            )
        except USPTOApiError as e:
            pytest.fail(
                f"Assignment data not available or API error for {sample_application_number}: {e}"
            )

    def test_get_application_attorney(
        self, patent_data_client: PatentDataClient, sample_application_number: str
    ) -> None:
        """Test getting attorney/agent data."""
        try:
            attorney_data = patent_data_client.get_application_attorney(
                sample_application_number
            )
            if attorney_data is None:
                pytest.fail(f"No attorney data for {sample_application_number}")

            assert isinstance(attorney_data, RecordAttorney)
            has_attorney_info = False
            if attorney_data.attorney_bag:
                assert isinstance(
                    attorney_data.attorney_bag[0].first_name, str
                ) or isinstance(attorney_data.attorney_bag[0].last_name, str)
                has_attorney_info = True
            if attorney_data.customer_number_correspondence_data:
                assert (
                    attorney_data.customer_number_correspondence_data.patron_identifier
                    is not None
                )
                has_attorney_info = True

            if not has_attorney_info:
                pytest.fail(
                    f"Attorney data present but bags are empty for {sample_application_number}"
                )

        except USPTOApiNotFoundError:
            pytest.fail(
                f"Attorney data not found (404) for application {sample_application_number}"
            )
        except USPTOApiError as e:
            pytest.fail(
                f"Attorney data not available or API error for {sample_application_number}: {e}"
            )

    def test_get_application_continuity(
        self, patent_data_client: PatentDataClient, sample_application_number: str
    ) -> None:
        """Test getting continuity data."""
        try:
            continuity_data = patent_data_client.get_application_continuity(
                sample_application_number
            )
            if continuity_data is None:
                pytest.fail(f"No continuity data for {sample_application_number}")

            assert isinstance(continuity_data, ApplicationContinuityData)
            assert continuity_data.parent_continuity_bag is not None
            assert continuity_data.child_continuity_bag is not None
            if continuity_data.parent_continuity_bag:
                assert (
                    continuity_data.parent_continuity_bag[
                        0
                    ].parent_application_number_text
                    is not None
                )
        except USPTOApiNotFoundError:
            pytest.fail(
                f"Continuity data not found (404) for application {sample_application_number}"
            )
        except USPTOApiError as e:
            pytest.fail(
                f"Continuity data not available or API error for {sample_application_number}: {e}"
            )

    def test_get_application_foreign_priority(
        self, patent_data_client: PatentDataClient, sample_application_number: str
    ) -> None:
        """Test getting foreign priority data."""
        try:
            priorities = patent_data_client.get_application_foreign_priority(
                sample_application_number
            )
            if priorities is None:
                pytest.fail(
                    f"No foreign priority data (returned None) for {sample_application_number}"
                )

            assert isinstance(priorities, list)
            if not priorities:
                pytest.fail(
                    f"Foreign priority data list is empty for {sample_application_number}"
                )

            assert isinstance(priorities[0], ForeignPriority)
            assert priorities[0].ip_office_name is not None
            assert priorities[0].filing_date is not None
            assert isinstance(priorities[0].filing_date, datetime.date)

        except USPTOApiNotFoundError:
            pytest.fail(
                f"Foreign priority data not found (404) for application {sample_application_number}"
            )
        except USPTOApiError as e:
            pytest.fail(
                f"Foreign priority data not available or API error for {sample_application_number}: {e}"
            )

    def test_get_application_transactions(
        self, patent_data_client: PatentDataClient, sample_application_number: str
    ) -> None:
        """Test getting transaction history data."""
        try:
            transactions = patent_data_client.get_application_transactions(
                sample_application_number
            )
            if transactions is None:
                pytest.fail(
                    f"No transaction data (returned None) for {sample_application_number}"
                )

            assert isinstance(transactions, list)
            if not transactions:
                pytest.fail(
                    f"Transaction data list is empty for {sample_application_number}"
                )

            assert isinstance(transactions[0], EventData)
            assert transactions[0].event_code is not None
            assert transactions[0].event_date is not None
            assert isinstance(transactions[0].event_date, datetime.date)
        except USPTOApiNotFoundError:
            pytest.fail(
                f"Transaction data not found (404) for application {sample_application_number}"
            )
        except USPTOApiError as e:
            pytest.fail(
                f"Transaction data not available or API error for {sample_application_number}: {e}"
            )

    def test_get_application_documents(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test getting document listings."""
        try:
            documents_bag = patent_data_client.get_application_documents(
                self.KNOWN_APP_NUM_WITH_DOCS
            )
            if documents_bag is None:
                pytest.fail(
                    f"No document bag returned for {self.KNOWN_APP_NUM_WITH_DOCS}"
                )

            assert isinstance(documents_bag, DocumentBag)
            assert documents_bag.documents is not None
            if not documents_bag.documents:
                pytest.fail(f"Document bag is empty for {self.KNOWN_APP_NUM_WITH_DOCS}")

            first_doc = documents_bag.documents[0]
            assert isinstance(first_doc, Document)
            assert first_doc.document_identifier is not None
            assert first_doc.document_code is not None
            assert first_doc.official_date is not None
            assert isinstance(first_doc.official_date, datetime.datetime)

        except USPTOApiNotFoundError:
            pytest.fail(f"Documents not found (404) for {self.KNOWN_APP_NUM_WITH_DOCS}")
        except USPTOApiError as e:
            pytest.fail(
                f"Document endpoint failed for {self.KNOWN_APP_NUM_WITH_DOCS}: {e}"
            )

    def test_get_application_associated_documents(
        self, patent_data_client: PatentDataClient, sample_application_number: str
    ) -> None:
        """Test getting associated documents metadata."""
        try:
            assoc_docs_data = patent_data_client.get_application_associated_documents(
                sample_application_number
            )
            if assoc_docs_data is None:
                pytest.fail(
                    f"No associated documents data for {sample_application_number}"
                )

            assert isinstance(assoc_docs_data, PrintedPublication)

            if (
                assoc_docs_data.pgpub_document_meta_data is None
                and assoc_docs_data.grant_document_meta_data is None
            ):
                pytest.fail(
                    f"No pgpub or grant document metadata for {sample_application_number}"
                )
            if assoc_docs_data.pgpub_document_meta_data:
                assert (
                    assoc_docs_data.pgpub_document_meta_data.file_location_uri
                    is not None
                )
            if assoc_docs_data.grant_document_meta_data:
                assert (
                    assoc_docs_data.grant_document_meta_data.file_location_uri
                    is not None
                )
        except USPTOApiNotFoundError:
            pytest.fail(
                f"Associated documents data not found (404) for application {sample_application_number}"
            )
        except USPTOApiError as e:
            pytest.fail(
                f"Associated documents data not available or API error for {sample_application_number}: {e}"
            )

    def test_download_application_document(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test downloading a document file."""
        try:
            documents_bag = patent_data_client.get_application_documents(
                self.KNOWN_APP_NUM_WITH_DOCS
            )
            if documents_bag is None or not documents_bag.documents:
                pytest.fail(
                    f"No documents found for {self.KNOWN_APP_NUM_WITH_DOCS} to test download."
                )

            doc_to_download = None
            for doc in documents_bag.documents:
                if doc.document_formats:
                    doc_to_download = doc
                    break

            if doc_to_download is None or doc_to_download.document_identifier is None:
                pytest.fail(
                    f"No downloadable document found for {self.KNOWN_APP_NUM_WITH_DOCS}"
                )

            assert isinstance(doc_to_download.document_identifier, str)

            file_path = patent_data_client.download_document(
                document_format=doc_to_download.document_formats[0],
                destination_path=TEST_DOWNLOAD_DIR,
            )

            assert file_path is not None
            assert os.path.exists(file_path)
            assert os.path.getsize(file_path) > 0
        except USPTOApiNotFoundError:
            pytest.skip(
                f"Document or application not found (404) for download: {self.KNOWN_APP_NUM_WITH_DOCS}"
            )
        except USPTOApiError as e:
            pytest.skip(
                f"Document download failed for {self.KNOWN_APP_NUM_WITH_DOCS}: {e}"
            )
        except IndexError:
            pytest.skip(
                f"No documents available in bag for {self.KNOWN_APP_NUM_WITH_DOCS} to test download."
            )

    def test_search_applications_post(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test searching patent applications using POST method with search_applications."""
        search_request_body = {
            "q": "applicationMetaData.applicationTypeLabelName:Utility AND applicationMetaData.inventionTitle:(computer OR software)",
            "pagination": {"offset": 0, "limit": 2},
        }
        try:
            response = patent_data_client.search_applications(
                post_body=search_request_body
            )
            assert response is not None
            assert isinstance(response, PatentDataResponse)
            assert response.count >= 0
            if response.count > 0:
                assert response.patent_file_wrapper_data_bag is not None
                assert len(response.patent_file_wrapper_data_bag) > 0
                assert len(response.patent_file_wrapper_data_bag) <= 2
                assert isinstance(
                    response.patent_file_wrapper_data_bag[0], PatentFileWrapper
                )
            else:
                pytest.fail(f"No PatentDate returned for: {search_request_body}")
        except USPTOApiError as e:
            pytest.fail(f"POST search failed: {e}")

    def test_get_search_results_get(self, patent_data_client: PatentDataClient) -> None:
        """Test getting search results (as JSON structure) using GET path of get_search_results."""
        try:
            response = patent_data_client.get_search_results(
                query=f"applicationNumberText:{self.KNOWN_APP_NUM_WITH_DOCS}",
                limit=1,
            )
            assert response is not None
            assert isinstance(response, List)
            if len(response) > 0:
                assert response[0].application_type_label_name == "Utility"
            elif len(response) == 0:
                pytest.fail(
                    f"No applicationMetaData returned for {self.KNOWN_APP_NUM_WITH_DOCS}"
                )
            else:
                pytest.fail(
                    f"Unexpected response structure for get_search_results GET: app no={self.KNOWN_APP_NUM_WITH_DOCS}"
                )
        except USPTOApiError as e:
            pytest.fail(f"get_search_results GET test failed: {e}")

    def test_get_search_results_post(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test getting search results using POST path of get_search_results."""
        post_body_request = {
            "q": f"applicationNumberText:{self.KNOWN_APP_NUM_WITH_DOCS}",
            "pagination": {"offset": 0, "limit": 1},
        }
        try:
            response = patent_data_client.get_search_results(
                post_body=post_body_request
            )
            assert response is not None
            assert isinstance(response, List)

            if len(response) > 0:
                assert response[0].application_type_label_name == "Utility"
            elif response.count == 0:
                pytest.fail(
                    f"No PatentData returned for US App No.: {self.KNOWN_APP_NUM_WITH_DOCS} with: {post_body_request}"
                )
        except USPTOApiError as e:
            pytest.skip(f"get_search_results POST test failed: {e}")

    def test_search_status_codes_post(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test searching status codes using POST method with search_status_codes."""
        search_request = {
            "q": "applicationStatusDescriptionText:(abandoned OR expired OR pending)",
            "pagination": {"offset": 0, "limit": 5},
        }
        try:
            response = patent_data_client.search_status_codes(search_request)
            assert response is not None
            assert isinstance(response, StatusCodeSearchResponse)
            assert response.status_code_bag is not None
            assert isinstance(response.status_code_bag, StatusCodeCollection)

            if response.count > 0:
                assert len(response.status_code_bag) > 0
                assert len(response.status_code_bag) <= 5
                assert isinstance(response.status_code_bag[0], StatusCode)
                assert response.status_code_bag[0].code is not None
            else:
                pytest.fail(
                    f"No PatentDate returned for abandoned OR expired OR pending applications."
                )

        except USPTOApiError as e:
            pytest.skip(f"Status codes POST search failed: {e}")

    def test_invalid_application_number_handling(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test proper error handling with an invalid application number."""
        invalid_app_num = "INVALID123XYZ"

        try:
            metadata = patent_data_client.get_application_metadata(invalid_app_num)
            assert (
                metadata is None
            ), "Expected None for invalid application number if client handles 404 by returning None"
        except ValueError as e:
            # Client validates application number format before API call
            assert "Invalid application number format" in str(e)
        except USPTOApiNotFoundError as e:
            assert e.status_code == 404, f"Expected 404 error, got {e.status_code}"
        except USPTOApiError as e:
            pytest.fail(
                f"Expected USPTOApiNotFoundError for invalid app number, but got different USPTOApiError: {e}"
            )
        except Exception as e:
            pytest.fail(f"Unexpected exception for invalid app number: {e}")
