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
    PrintedMetaData,
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


@pytest.fixture
def patent_data_client(config: USPTOConfig) -> PatentDataClient:
    """
    Create a PatentDataClient instance for integration tests.

    Args:
        config: The configuration instance

    Returns:
        PatentDataClient: A client instance
    """
    return PatentDataClient(config=config)


@pytest.fixture
def sample_application_number(patent_data_client: PatentDataClient) -> str:
    """Provides a sample application number for tests."""
    try:
        # Updated to use search_applications (GET path)
        response = patent_data_client.search_applications(
            query='applicationMetaData.applicationTypeCategory:Utility AND applicationMetaData.applicationStatusDescriptionText:(Pending OR "Patented Case")',
            limit=1,
        )
        if response.count > 0 and response.patent_file_wrapper_data_bag:
            app_num = response.patent_file_wrapper_data_bag[0].application_number_text
            if app_num:
                return app_num

        pytest.skip(
            "Could not retrieve a sample application number. Ensure API is reachable and query is valid."
        )

    except USPTOApiError as e:
        pytest.skip(f"Could not fetch sample application number due to API error: {e}")
    except Exception as e:
        pytest.skip(
            f"Could not fetch sample application number due to unexpected error: {e}"
        )
    return ""


class TestPatentDataIntegration:
    """Integration tests for the PatentDataClient."""

    KNOWN_APP_NUM_WITH_DOCS = "18045436"

    def test_search_applications_get(  # Renamed test
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test getting patent applications from the API using GET path of search_applications."""
        # Updated to use search_applications
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
    ) -> None:  # Renamed test
        """Test searching for patents using convenience _q parameters of search_applications."""
        # Updated to use search_applications with _q parameter
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
            assert response.patent_file_wrapper_data_bag == []

    def test_get_application_by_number(  # Renamed test
        self, patent_data_client: PatentDataClient, sample_application_number: str
    ) -> None:
        """Test getting a specific patent by application number."""
        # Updated to use get_application_by_number
        patent_wrapper = patent_data_client.get_application_by_number(
            sample_application_number
        )

        assert patent_wrapper is not None
        assert isinstance(patent_wrapper, PatentFileWrapper)
        assert patent_wrapper.application_number_text == sample_application_number
        assert patent_wrapper.application_meta_data is not None
        assert isinstance(patent_wrapper.application_meta_data, ApplicationMetaData)
        assert patent_wrapper.application_meta_data.invention_title is not None

    def test_get_status_codes(  # Renamed test
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test getting patent status codes."""
        # Updated to use get_status_codes
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
                pytest.skip(
                    f"No metadata available for application {sample_application_number}"
                )

            assert isinstance(metadata, ApplicationMetaData)
            assert metadata.invention_title is not None
            assert metadata.filing_date is not None
            assert isinstance(metadata.filing_date, datetime.date)
        except USPTOApiNotFoundError:
            pytest.skip(
                f"Metadata not found (404) for application {sample_application_number}"
            )
        except USPTOApiError as e:
            pytest.skip(
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
                pytest.skip(f"No adjustment data for {sample_application_number}")

            assert isinstance(adjustment_data, PatentTermAdjustmentData)
            assert adjustment_data.adjustment_total_quantity is not None
        except USPTOApiNotFoundError:
            pytest.skip(
                f"Adjustment data not found (404) for application {sample_application_number}"
            )
        except USPTOApiError as e:
            pytest.skip(
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
                pytest.skip(
                    f"No assignment data (returned None) for {sample_application_number}"
                )

            assert isinstance(assignments, list)
            if not assignments:
                pytest.skip(
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
            pytest.skip(
                f"Assignment data not found (404) for application {sample_application_number}"
            )
        except USPTOApiError as e:
            pytest.skip(
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
                pytest.skip(f"No attorney data for {sample_application_number}")

            assert isinstance(attorney_data, RecordAttorney)
            has_attorney_info = False
            if attorney_data.attorney_bag:
                assert isinstance(
                    attorney_data.attorney_bag[0].first_name, str
                ) or isinstance(attorney_data.attorney_bag[0].last_name, str)
                has_attorney_info = True
            if attorney_data.customer_number_correspondence_data:
                assert (
                    attorney_data.customer_number_correspondence_data[
                        0
                    ].patron_identifier
                    is not None
                )
                has_attorney_info = True

            if not has_attorney_info:
                pytest.skip(
                    f"Attorney data present but bags are empty for {sample_application_number}"
                )

        except USPTOApiNotFoundError:
            pytest.skip(
                f"Attorney data not found (404) for application {sample_application_number}"
            )
        except USPTOApiError as e:
            pytest.skip(
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
                pytest.skip(f"No continuity data for {sample_application_number}")

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
            pytest.skip(
                f"Continuity data not found (404) for application {sample_application_number}"
            )
        except USPTOApiError as e:
            pytest.skip(
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
                pytest.skip(
                    f"No foreign priority data (returned None) for {sample_application_number}"
                )

            assert isinstance(priorities, list)
            if not priorities:
                pytest.skip(
                    f"Foreign priority data list is empty for {sample_application_number}"
                )

            assert isinstance(priorities[0], ForeignPriority)
            assert priorities[0].ip_office_name is not None
            assert priorities[0].filing_date is not None
            assert isinstance(priorities[0].filing_date, datetime.date)

        except USPTOApiNotFoundError:
            pytest.skip(
                f"Foreign priority data not found (404) for application {sample_application_number}"
            )
        except USPTOApiError as e:
            pytest.skip(
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
                pytest.skip(
                    f"No transaction data (returned None) for {sample_application_number}"
                )

            assert isinstance(transactions, list)
            if not transactions:
                pytest.skip(
                    f"Transaction data list is empty for {sample_application_number}"
                )

            assert isinstance(transactions[0], EventData)
            assert transactions[0].event_code is not None
            assert transactions[0].event_date is not None
            assert isinstance(transactions[0].event_date, datetime.date)
        except USPTOApiNotFoundError:
            pytest.skip(
                f"Transaction data not found (404) for application {sample_application_number}"
            )
        except USPTOApiError as e:
            pytest.skip(
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
                pytest.skip(
                    f"No document bag returned for {self.KNOWN_APP_NUM_WITH_DOCS}"
                )

            assert isinstance(documents_bag, DocumentBag)
            assert documents_bag.documents is not None
            if not documents_bag.documents:
                pytest.skip(f"Document bag is empty for {self.KNOWN_APP_NUM_WITH_DOCS}")

            first_doc = documents_bag.documents[0]
            assert isinstance(first_doc, Document)
            assert first_doc.document_identifier is not None
            assert first_doc.document_code is not None
            assert first_doc.official_date is not None
            assert isinstance(first_doc.official_date, datetime.datetime)

        except USPTOApiNotFoundError:
            pytest.skip(f"Documents not found (404) for {self.KNOWN_APP_NUM_WITH_DOCS}")
        except USPTOApiError as e:
            pytest.skip(
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
                pytest.skip(
                    f"No associated documents data for {sample_application_number}"
                )

            assert isinstance(assoc_docs_data, PrintedMetaData)
            assert (
                assoc_docs_data.pgpub_document_meta_data is not None
                or assoc_docs_data.grant_document_meta_data is not None
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
            pytest.skip(
                f"Associated documents data not found (404) for application {sample_application_number}"
            )
        except USPTOApiError as e:
            pytest.skip(
                f"Associated documents data not available or API error for {sample_application_number}: {e}"
            )

    def test_download_application_document(
        self, patent_data_client: PatentDataClient
    ) -> None:  # Renamed test
        """Test downloading a document file."""
        try:
            documents_bag = patent_data_client.get_application_documents(
                self.KNOWN_APP_NUM_WITH_DOCS
            )
            if documents_bag is None or not documents_bag.documents:
                pytest.skip(
                    f"No documents found for {self.KNOWN_APP_NUM_WITH_DOCS} to test download."
                )

            doc_to_download = None
            for doc in documents_bag.documents:
                if doc.document_formats:
                    doc_to_download = doc
                    break

            if doc_to_download is None or doc_to_download.document_identifier is None:
                pytest.skip(
                    f"No downloadable document found for {self.KNOWN_APP_NUM_WITH_DOCS}"
                )

            assert isinstance(doc_to_download.document_identifier, str)

            file_path = patent_data_client.download_document(
                document_format=doc_to_download.document_formats[0],
                file_path=TEST_DOWNLOAD_DIR,
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

    def test_search_applications_post(  # Renamed test
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test searching patent applications using POST method with search_applications."""
        search_request_body = {  # Renamed from search_request to search_request_body for clarity
            "q": "applicationMetaData.applicationTypeCategory:Utility AND applicationMetaData.inventionTitle:(computer OR software)",
            "pagination": {"offset": 0, "limit": 2},
        }
        try:
            # Updated to use search_applications with post_body
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
                assert response.patent_file_wrapper_data_bag == []
        except USPTOApiError as e:
            pytest.skip(f"POST search failed: {e}")

    def test_get_search_results_get(  # Renamed test
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test getting search results (as JSON structure) using GET path of get_search_results."""
        # format is now handled internally by get_search_results for GET
        try:
            # Updated to use get_search_results
            response = patent_data_client.get_search_results(
                query=f"applicationNumberText:{self.KNOWN_APP_NUM_WITH_DOCS}",
                limit=1,  # Pass as keyword argument
            )
            assert response is not None
            assert isinstance(response, PatentDataResponse)
            if response.count > 0 and response.patent_file_wrapper_data_bag:
                assert (
                    response.patent_file_wrapper_data_bag[0].application_number_text
                    == self.KNOWN_APP_NUM_WITH_DOCS
                )
            elif response.count == 0:
                assert response.patent_file_wrapper_data_bag == []
            else:
                pytest.fail(
                    f"Unexpected response structure for get_search_results GET: count={response.count} but bag is {response.patent_file_wrapper_data_bag}"
                )
        except USPTOApiError as e:
            pytest.skip(f"get_search_results GET test failed: {e}")

    def test_get_search_results_post(  # Renamed test
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test getting search results (as JSON structure) using POST path of get_search_results."""
        # format should be part of the post_body for POST requests to this endpoint
        post_body_request = {  # Renamed for clarity
            "q": f"applicationNumberText:{self.KNOWN_APP_NUM_WITH_DOCS}",
            "pagination": {"offset": 0, "limit": 1},
            "format": "json",  # Explicitly set format for POST body
        }
        try:
            # Updated to use get_search_results with post_body
            response = patent_data_client.get_search_results(
                post_body=post_body_request
            )
            assert response is not None
            assert isinstance(response, PatentDataResponse)

            if response.count > 0 and response.patent_file_wrapper_data_bag:
                assert (
                    response.patent_file_wrapper_data_bag[0].application_number_text
                    == self.KNOWN_APP_NUM_WITH_DOCS
                )
            elif response.count == 0:
                assert response.patent_file_wrapper_data_bag == []
            else:
                pytest.fail(
                    f"Unexpected response structure for get_search_results POST: count={response.count} but bag is {response.patent_file_wrapper_data_bag}"
                )
        except USPTOApiError as e:
            pytest.skip(f"get_search_results POST test failed: {e}")

    def test_search_status_codes_post(  # Renamed test
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test searching status codes using POST method with search_status_codes."""
        search_request = {
            "q": "applicationStatusDescriptionText:(abandoned OR expired OR pending)",
            "pagination": {"offset": 0, "limit": 5},
        }
        try:
            # Updated to use search_status_codes
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
                assert len(response.status_code_bag) == 0

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
        except USPTOApiNotFoundError as e:
            assert e.status_code == 404, f"Expected 404 error, got {e.status_code}"
        except USPTOApiError as e:
            pytest.fail(
                f"Expected USPTOApiNotFoundError for invalid app number, but got different USPTOApiError: {e}"
            )
        except Exception as e:
            pytest.fail(f"Unexpected exception for invalid app number: {e}")
