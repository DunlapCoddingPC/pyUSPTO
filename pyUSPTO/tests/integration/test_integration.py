"""
Integration tests for the USPTO API client.

This module contains integration tests that make real API calls to the USPTO API.
These tests are optional and are skipped by default unless the ENABLE_INTEGRATION_TESTS
environment variable is set to 'true'.
"""

import datetime  # For date and datetime assertions
import os
import shutil
from typing import Iterator, List, Optional  # Keep List for type hinting

import pytest

from pyUSPTO.clients import BulkDataClient, PatentDataClient
from pyUSPTO.config import USPTOConfig

# Updated exception imports based on provided files
from pyUSPTO.exceptions import USPTOApiError, USPTOApiNotFoundError
from pyUSPTO.models.bulk_data import BulkDataProduct, BulkDataResponse

# Updated model imports for patent_data based on provided files
from pyUSPTO.models.patent_data import Document  # Added Document as it's used directly
from pyUSPTO.models.patent_data import (
    StatusCode,  # Added StatusCode as it's used directly
)
from pyUSPTO.models.patent_data import (  # DocumentMetaData, # This is a component, not directly asserted on in the same way Document is
    ApplicationContinuityData,
    ApplicationMetaData,
    Assignment,
    AssociatedDocumentsData,
    DocumentBag,
    EventData,
    ForeignPriority,
    PatentDataResponse,
    PatentFileWrapper,
    PatentTermAdjustmentData,
    RecordAttorney,
    StatusCodeCollection,
    StatusCodeSearchResponse,
)

# Skip all tests in this module unless ENABLE_INTEGRATION_TESTS is set to 'true'
pytestmark = pytest.mark.skipif(
    os.environ.get("ENABLE_INTEGRATION_TESTS", "").lower() != "true",
    reason="Integration tests are disabled. Set ENABLE_INTEGRATION_TESTS=true to enable.",
)

# Define a temporary download directory for tests
TEST_DOWNLOAD_DIR = "./temp_test_downloads"


@pytest.fixture(scope="module", autouse=True)
def manage_test_download_dir() -> Iterator[None]:
    """Create and clean up the test download directory."""
    if os.path.exists(TEST_DOWNLOAD_DIR):
        shutil.rmtree(TEST_DOWNLOAD_DIR)
    os.makedirs(TEST_DOWNLOAD_DIR, exist_ok=True)
    yield
    if os.path.exists(TEST_DOWNLOAD_DIR):
        shutil.rmtree(TEST_DOWNLOAD_DIR)


@pytest.fixture
def api_key() -> Optional[str]:
    """
    Get the API key from the environment.

    Returns:
        Optional[str]: The API key or None if not set
    """
    key = os.environ.get("USPTO_API_KEY")
    if not key:
        pytest.skip(
            "USPTO_API_KEY environment variable not set. Skipping integration tests."
        )
    return key


@pytest.fixture
def config(api_key: Optional[str]) -> USPTOConfig:
    """
    Create a USPTOConfig instance for integration tests.

    Args:
        api_key: The API key from the environment

    Returns:
        USPTOConfig: A configuration instance
    """
    return USPTOConfig(api_key=api_key)


@pytest.fixture
def bulk_data_client(config: USPTOConfig) -> BulkDataClient:
    """
    Create a BulkDataClient instance for integration tests.

    Args:
        config: The configuration instance

    Returns:
        BulkDataClient: A client instance
    """
    return BulkDataClient(config=config)


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
        response = patent_data_client.get_patent_applications(
            params={
                "limit": 1,
                "q": 'applicationMetaData.applicationTypeCategory:Utility AND applicationMetaData.applicationStatusDescriptionText:(Pending OR "Patented Case")',
            }
        )
        if response.count > 0 and response.patent_file_wrapper_data_bag:
            app_num = response.patent_file_wrapper_data_bag[0].application_number_text
            if app_num:
                return app_num

        # If we get here, no valid application number was found
        pytest.skip(
            "Could not retrieve a sample application number. Ensure API is reachable and query is valid."
        )

    except USPTOApiError as e:
        pytest.skip(f"Could not fetch sample application number due to API error: {e}")
    except Exception as e:
        pytest.skip(
            f"Could not fetch sample application number due to unexpected error: {e}"
        )


class TestBulkDataIntegration:
    """Integration tests for the BulkDataClient."""

    def test_get_products(self, bulk_data_client: BulkDataClient) -> None:
        """Test getting products from the API."""
        response = bulk_data_client.get_products()

        assert response is not None
        assert isinstance(response, BulkDataResponse)
        assert response.count > 0
        assert response.bulk_data_product_bag is not None
        assert len(response.bulk_data_product_bag) > 0

        product = response.bulk_data_product_bag[0]
        assert isinstance(product, BulkDataProduct)
        assert product.product_identifier is not None
        assert product.product_title_text is not None

    def test_search_products(self, bulk_data_client: BulkDataClient) -> None:
        """Test searching for products."""
        response = bulk_data_client.search_products(
            query="PAIF", limit=5
        )  # PAIF is a common product type

        assert response is not None
        assert isinstance(response, BulkDataResponse)
        assert response.count > 0
        assert response.bulk_data_product_bag is not None
        assert len(response.bulk_data_product_bag) > 0
        assert len(response.bulk_data_product_bag) <= 5

    def test_get_product_by_id(self, bulk_data_client: BulkDataClient) -> None:
        """Test getting a specific product by ID."""
        response = bulk_data_client.get_products(
            params={
                "limit": 1,
                "q": "productTitleText:Patent Application Information Retrieval*",
            }
        )  # More specific query
        assert response.count > 0
        assert response.bulk_data_product_bag

        product_id = response.bulk_data_product_bag[0].product_identifier
        assert product_id is not None
        product = bulk_data_client.get_product_by_id(product_id, include_files=True)

        assert product is not None
        assert isinstance(product, BulkDataProduct)
        assert product.product_identifier == product_id

        if product.product_file_total_quantity > 0:
            assert product.product_file_bag is not None
            assert product.product_file_bag.count > 0


class TestPatentDataIntegration:
    """Integration tests for the PatentDataClient."""

    KNOWN_APP_NUM_WITH_DOCS = (
        "18045436"  # From USPTO API sample, likely has various data
    )

    def test_get_patent_applications(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test getting patent applications from the API."""
        response = patent_data_client.get_patent_applications(
            params={
                "limit": 2,
                "q": "applicationMetaData.applicationTypeCategory:Utility",
            }
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

    def test_search_patents(self, patent_data_client: PatentDataClient) -> None:
        """Test searching for patents."""
        # Using a common assignee name known to yield results
        response = patent_data_client.search_patents(
            assignee_name="International Business Machines", limit=2
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
            # If count is 0, the bag should be empty
            assert response.patent_file_wrapper_data_bag == []

    def test_get_patent_application_details(
        self, patent_data_client: PatentDataClient, sample_application_number: str
    ) -> None:
        """Test getting a specific patent by application number."""
        patent_wrapper = patent_data_client.get_patent_application_details(
            sample_application_number
        )

        assert patent_wrapper is not None
        assert isinstance(patent_wrapper, PatentFileWrapper)
        assert patent_wrapper.application_number_text == sample_application_number
        assert patent_wrapper.application_meta_data is not None
        assert isinstance(patent_wrapper.application_meta_data, ApplicationMetaData)
        assert patent_wrapper.application_meta_data.invention_title is not None

    def test_get_patent_status_codes(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test getting patent status codes."""
        status_codes_response = patent_data_client.get_patent_status_codes()

        assert status_codes_response is not None
        assert isinstance(status_codes_response, StatusCodeSearchResponse)
        assert status_codes_response.status_code_bag is not None
        assert isinstance(status_codes_response.status_code_bag, StatusCodeCollection)
        assert (
            len(status_codes_response.status_code_bag) > 0
        )  # Expecting some status codes

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
            if metadata is None:  # Client method returns Optional
                pytest.skip(
                    f"No metadata available for application {sample_application_number}"
                )

            assert isinstance(metadata, ApplicationMetaData)
            assert metadata.invention_title is not None  # Check a key field
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
            # Check a key field, can be 0 so `is not None` is appropriate
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
            if not assignments:  # Empty list is valid if no assignments
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
                f"Assignment data not found (404) for {sample_application_number}"
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
            # RecordAttorney can have empty bags. Check if customer_number_correspondence_data or attorney_bag has content.
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
                f"Attorney data not found (404) for {sample_application_number}"
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
            # Continuity data can have empty parent/child bags, which is valid.
            assert continuity_data.parent_continuity_bag is not None
            assert continuity_data.child_continuity_bag is not None
            # If there's parent data, check a field
            if continuity_data.parent_continuity_bag:
                assert (
                    continuity_data.parent_continuity_bag[
                        0
                    ].parent_application_number_text
                    is not None
                )
        except USPTOApiNotFoundError:
            pytest.skip(
                f"Continuity data not found (404) for {sample_application_number}"
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
            if not priorities:  # Empty list is valid
                pytest.skip(
                    f"Foreign priority data list is empty for {sample_application_number}"
                )

            assert isinstance(priorities[0], ForeignPriority)
            assert priorities[0].ip_office_name is not None
            assert priorities[0].filing_date is not None
            assert isinstance(priorities[0].filing_date, datetime.date)

        except USPTOApiNotFoundError:
            pytest.skip(
                f"Foreign priority data not found (404) for {sample_application_number}"
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
            if not transactions:  # Empty list is valid
                pytest.skip(
                    f"Transaction data list is empty for {sample_application_number}"
                )

            assert isinstance(transactions[0], EventData)
            assert transactions[0].event_code is not None
            assert transactions[0].event_date is not None
            assert isinstance(transactions[0].event_date, datetime.date)
        except USPTOApiNotFoundError:
            pytest.skip(
                f"Transaction data not found (404) for {sample_application_number}"
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
                )  # type: ignore[unreachable]

            assert isinstance(documents_bag, DocumentBag)
            assert documents_bag.documents is not None  # documents is a tuple
            if not documents_bag.documents:
                pytest.skip(f"Document bag is empty for {self.KNOWN_APP_NUM_WITH_DOCS}")

            first_doc = documents_bag.documents[0]
            assert isinstance(first_doc, Document)  # Changed from DocumentMetaData
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

            assert isinstance(assoc_docs_data, AssociatedDocumentsData)
            # Check if at least one of the metadata fields is present
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
                f"Associated documents data not found (404) for {sample_application_number}"
            )
        except USPTOApiError as e:
            pytest.skip(
                f"Associated documents data not available or API error for {sample_application_number}: {e}"
            )

    def test_download_document_file(self, patent_data_client: PatentDataClient) -> None:
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
            # Find a document that has download formats
            for doc in documents_bag.documents:
                if doc.download_formats:
                    doc_to_download = doc
                    break

            if doc_to_download is None or doc_to_download.document_identifier is None:
                pytest.skip(
                    f"No downloadable document found for {self.KNOWN_APP_NUM_WITH_DOCS}"
                )

            assert doc_to_download.document_identifier is str
            file_path = patent_data_client.download_document_file(
                application_number=self.KNOWN_APP_NUM_WITH_DOCS,
                document_id=doc_to_download.document_identifier,
                destination_dir=TEST_DOWNLOAD_DIR,
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
        except (
            IndexError
        ):  # Should be caught by earlier checks if documents_bag.documents is empty
            pytest.skip(
                f"No documents available in bag for {self.KNOWN_APP_NUM_WITH_DOCS} to test download."
            )

    def test_search_patent_applications_post(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test searching patent applications using POST method."""
        search_request = {
            "q": "applicationMetaData.applicationTypeCategory:Utility AND applicationMetaData.inventionTitle:(computer OR software)",
            "pagination": {"offset": 0, "limit": 2},
        }
        try:
            response = patent_data_client.search_patent_applications_post(
                search_request
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
        except USPTOApiError as e:  # General API error
            pytest.skip(f"POST search failed: {e}")

    def test_download_patent_applications_get(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test downloading patent data (as structure) using GET."""
        params = {
            "q": f"applicationNumberText:{self.KNOWN_APP_NUM_WITH_DOCS}",
            "limit": "1",
            "format": "json",
        }
        try:
            response = patent_data_client.download_patent_applications_get(
                params=params
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
            else:  # Should not happen if count is > 0
                pytest.fail(
                    f"Unexpected response structure for download GET: count={response.count} but bag is {response.patent_file_wrapper_data_bag}"
                )
        except USPTOApiError as e:
            pytest.skip(f"Download GET test failed: {e}")

    def test_download_patent_applications_post(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test downloading patent data (as structure) using POST."""
        download_request = {
            "q": f"applicationNumberText:{self.KNOWN_APP_NUM_WITH_DOCS}",
            "pagination": {"offset": 0, "limit": 1},
            "format": "json",
        }
        try:
            response = patent_data_client.download_patent_applications_post(
                download_request
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
                    f"Unexpected response structure for download POST: count={response.count} but bag is {response.patent_file_wrapper_data_bag}"
                )
        except USPTOApiError as e:
            pytest.skip(f"Download POST test failed: {e}")

    def test_search_patent_status_codes_post(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test searching status codes using POST method."""
        search_request = {
            "q": "applicationStatusCodeDescriptionText:(abandoned OR expired OR pending)",
            "pagination": {"offset": 0, "limit": 5},
        }
        try:
            response = patent_data_client.search_patent_status_codes_post(
                search_request
            )
            assert response is not None
            assert isinstance(response, StatusCodeSearchResponse)
            assert response.status_code_bag is not None
            assert isinstance(response.status_code_bag, StatusCodeCollection)

            # The API's 'count' field in this response is the total matching, not page size.
            # So, len(response.status_code_bag) should be <= limit and <= response.count
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
            # This method returns Optional[ApplicationMetaData]
            # For an invalid number, the API should ideally 404, leading to USPTOApiNotFoundError
            # or the client might return None if it handles the error internally that way.
            metadata = patent_data_client.get_application_metadata(invalid_app_num)
            # If the client returns None on 404 instead of raising, this would be the path.
            assert (
                metadata is None
            ), "Expected None for invalid application number if client handles 404 by returning None"
        except USPTOApiNotFoundError as e:
            # This is the expected path if the client raises on 404.
            assert e.status_code == 404, f"Expected 404 error, got {e.status_code}"
        except USPTOApiError as e:  # Catch other API errors
            pytest.fail(
                f"Expected USPTOApiNotFoundError for invalid app number, but got different USPTOApiError: {e}"
            )
        except Exception as e:  # Catch any other unexpected errors
            pytest.fail(f"Unexpected exception for invalid app number: {e}")
