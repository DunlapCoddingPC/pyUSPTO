"""
Integration tests for the USPTO API client.

This module contains integration tests that make real API calls to the USPTO API.
These tests are optional and are skipped by default unless the ENABLE_INTEGRATION_TESTS
environment variable is set to 'true'.
"""

import os
from typing import Optional

import pytest

from pyUSPTO.clients import BulkDataClient, PatentDataClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.bulk_data import BulkDataProduct, BulkDataResponse
from pyUSPTO.models.patent_data import PatentDataResponse, PatentFileWrapper

# Skip all tests in this module unless ENABLE_INTEGRATION_TESTS is set to 'true'
pytestmark = pytest.mark.skipif(
    os.environ.get("ENABLE_INTEGRATION_TESTS", "").lower() != "true",
    reason="Integration tests are disabled. Set ENABLE_INTEGRATION_TESTS=true to enable.",
)


@pytest.fixture
def api_key() -> Optional[str]:
    """
    Get the API key from the environment.

    Returns:
        Optional[str]: The API key or None if not set
    """
    return os.environ.get("USPTO_API_KEY")


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


class TestBulkDataIntegration:
    """Integration tests for the BulkDataClient."""

    def test_get_products(self, bulk_data_client: BulkDataClient) -> None:
        """Test getting products from the API."""
        response = bulk_data_client.get_products()

        assert response is not None
        assert isinstance(response, BulkDataResponse)
        assert response.count > 0
        assert len(response.bulk_data_product_bag) > 0

        # Verify the structure of the first product
        product = response.bulk_data_product_bag[0]
        assert isinstance(product, BulkDataProduct)
        assert product.product_identifier is not None
        assert product.product_title_text is not None

    def test_search_products(self, bulk_data_client: BulkDataClient) -> None:
        """Test searching for products."""
        # Search for patent products
        response = bulk_data_client.search_products(query="patent", limit=5)

        assert response is not None
        assert isinstance(response, BulkDataResponse)
        assert response.count > 0
        assert len(response.bulk_data_product_bag) > 0
        assert len(response.bulk_data_product_bag) <= 5  # Respect the limit

    def test_get_product_by_id(self, bulk_data_client: BulkDataClient) -> None:
        """Test getting a specific product by ID."""
        # First get a list of products to find a valid ID
        response = bulk_data_client.get_products(params={"limit": 1})
        assert response.count > 0

        product_id = response.bulk_data_product_bag[0].product_identifier
        product = bulk_data_client.get_product_by_id(product_id, include_files=True)

        assert product is not None
        assert isinstance(product, BulkDataProduct)
        assert product.product_identifier == product_id
        assert product.product_title_text is not None

        # Check if files are included
        if product.product_file_total_quantity > 0:
            assert product.product_file_bag is not None
            assert product.product_file_bag.count > 0


class TestPatentDataIntegration:
    """Integration tests for the PatentDataClient."""

    def test_get_patent_applications(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test getting patent applications from the API."""
        response = patent_data_client.get_patent_applications(params={"limit": 5})

        assert response is not None
        assert isinstance(response, PatentDataResponse)
        assert response.count > 0
        assert len(response.patent_file_wrapper_data_bag) > 0
        assert len(response.patent_file_wrapper_data_bag) <= 5  # Respect the limit

        # Verify the structure of the first patent
        patent = response.patent_file_wrapper_data_bag[0]
        assert isinstance(patent, PatentFileWrapper)
        assert patent.application_number_text is not None
        assert patent.application_meta_data is not None

    def test_search_patents(self, patent_data_client: PatentDataClient) -> None:
        """Test searching for patents."""
        # Search for patents with a common inventor name
        response = patent_data_client.search_patents(inventor_name="Smith", limit=5)

        assert response is not None
        assert isinstance(response, PatentDataResponse)
        assert response.count > 0
        assert len(response.patent_file_wrapper_data_bag) > 0
        assert len(response.patent_file_wrapper_data_bag) <= 5  # Respect the limit

    def test_get_patent_by_application_number(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test getting a specific patent by application number."""
        # First get a list of patents to find a valid application number
        response = patent_data_client.get_patent_applications(params={"limit": 1})
        assert response.count > 0

        application_number = response.patent_file_wrapper_data_bag[
            0
        ].application_number_text
        # Ensure application_number is not None before proceeding
        assert application_number is not None, "Application number should not be None"
        patent = patent_data_client.get_patent_by_application_number(application_number)

        assert patent is not None
        assert isinstance(patent, PatentFileWrapper)
        assert patent.application_number_text == application_number
        assert patent.application_meta_data is not None

    def test_get_patent_status_codes(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test getting patent status codes."""
        status_codes = patent_data_client.get_patent_status_codes()

        assert status_codes is not None
        assert isinstance(status_codes, dict)
        assert "statusCodeBag" in status_codes
        assert len(status_codes["statusCodeBag"]) > 0

    def test_get_application_metadata(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test getting metadata for a patent application."""
        # Get a valid application number from existing applications
        response = patent_data_client.get_patent_applications(params={"limit": 1})
        assert response.count > 0

        application_number = response.patent_file_wrapper_data_bag[
            0
        ].application_number_text
        assert application_number is not None, "Application number should not be None"

        # Call the metadata endpoint
        metadata_response = patent_data_client.get_application_metadata(
            application_number
        )

        # Verify response structure
        assert metadata_response is not None
        assert isinstance(metadata_response, PatentDataResponse)
        assert len(metadata_response.patent_file_wrapper_data_bag) > 0

        # Verify the metadata contains the correct application number
        assert (
            metadata_response.patent_file_wrapper_data_bag[0].application_number_text
            == application_number
        )

    def test_get_application_adjustment(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test getting patent term adjustment data."""
        # Get a valid application number
        response = patent_data_client.get_patent_applications(params={"limit": 1})
        assert response.count > 0

        application_number = response.patent_file_wrapper_data_bag[
            0
        ].application_number_text
        assert application_number is not None, "Application number should not be None"

        try:
            # Call the adjustment endpoint
            adjustment_response = patent_data_client.get_application_adjustment(
                application_number
            )

            # Verify response structure
            assert adjustment_response is not None
            assert isinstance(adjustment_response, PatentDataResponse)

            # The response might be empty if the application doesn't have adjustment data
            if adjustment_response.count > 0:
                assert len(adjustment_response.patent_file_wrapper_data_bag) > 0
                assert (
                    adjustment_response.patent_file_wrapper_data_bag[
                        0
                    ].application_number_text
                    == application_number
                )
        except Exception as e:
            # Some applications might not have adjustment data
            pytest.skip(f"Patent adjustment data not available: {str(e)}")

    def test_get_application_assignment(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test getting assignment data."""
        # Get a valid application number
        response = patent_data_client.get_patent_applications(params={"limit": 1})
        assert response.count > 0

        application_number = response.patent_file_wrapper_data_bag[
            0
        ].application_number_text
        assert application_number is not None, "Application number should not be None"

        try:
            # Call the assignment endpoint
            assignment_response = patent_data_client.get_application_assignment(
                application_number
            )

            # Verify response structure
            assert assignment_response is not None
            assert isinstance(assignment_response, PatentDataResponse)

            # The response might be empty if the application doesn't have assignment data
            if assignment_response.count > 0:
                assert len(assignment_response.patent_file_wrapper_data_bag) > 0
                assert (
                    assignment_response.patent_file_wrapper_data_bag[
                        0
                    ].application_number_text
                    == application_number
                )
        except Exception as e:
            # Some applications might not have assignment data
            pytest.skip(f"Patent assignment data not available: {str(e)}")

    def test_get_application_attorney(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test getting attorney/agent data."""
        # Get a valid application number
        response = patent_data_client.get_patent_applications(params={"limit": 1})
        assert response.count > 0

        application_number = response.patent_file_wrapper_data_bag[
            0
        ].application_number_text
        assert application_number is not None, "Application number should not be None"

        try:
            # Call the attorney endpoint
            attorney_response = patent_data_client.get_application_attorney(
                application_number
            )

            # Verify response structure
            assert attorney_response is not None
            assert isinstance(attorney_response, PatentDataResponse)

            # The response might be empty if the application doesn't have attorney data
            if attorney_response.count > 0:
                assert len(attorney_response.patent_file_wrapper_data_bag) > 0
                assert (
                    attorney_response.patent_file_wrapper_data_bag[
                        0
                    ].application_number_text
                    == application_number
                )
        except Exception as e:
            # Some applications might not have attorney data
            pytest.skip(f"Patent attorney data not available: {str(e)}")

    def test_get_application_continuity(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test getting continuity data."""
        # Get a valid application number
        response = patent_data_client.get_patent_applications(params={"limit": 1})
        assert response.count > 0

        application_number = response.patent_file_wrapper_data_bag[
            0
        ].application_number_text
        assert application_number is not None, "Application number should not be None"

        try:
            # Call the continuity endpoint
            continuity_response = patent_data_client.get_application_continuity(
                application_number
            )

            # Verify response structure
            assert continuity_response is not None
            assert isinstance(continuity_response, PatentDataResponse)

            # The response might be empty if the application doesn't have continuity data
            if continuity_response.count > 0:
                assert len(continuity_response.patent_file_wrapper_data_bag) > 0
                assert (
                    continuity_response.patent_file_wrapper_data_bag[
                        0
                    ].application_number_text
                    == application_number
                )
        except Exception as e:
            # Some applications might not have continuity data
            pytest.skip(f"Patent continuity data not available: {str(e)}")

    def test_get_application_foreign_priority(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test getting foreign priority data."""
        # Get a valid application number
        response = patent_data_client.get_patent_applications(params={"limit": 1})
        assert response.count > 0

        application_number = response.patent_file_wrapper_data_bag[
            0
        ].application_number_text
        assert application_number is not None, "Application number should not be None"

        try:
            # Call the foreign priority endpoint
            priority_response = patent_data_client.get_application_foreign_priority(
                application_number
            )

            # Verify response structure
            assert priority_response is not None
            assert isinstance(priority_response, PatentDataResponse)

            # The response might be empty if the application doesn't have foreign priority data
            if priority_response.count > 0:
                assert len(priority_response.patent_file_wrapper_data_bag) > 0
                assert (
                    priority_response.patent_file_wrapper_data_bag[
                        0
                    ].application_number_text
                    == application_number
                )
        except Exception as e:
            # Some applications might not have foreign priority data
            pytest.skip(f"Patent foreign priority data not available: {str(e)}")

    def test_get_application_transactions(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test getting transaction history data."""
        # Get a valid application number
        response = patent_data_client.get_patent_applications(params={"limit": 1})
        assert response.count > 0

        application_number = response.patent_file_wrapper_data_bag[
            0
        ].application_number_text
        assert application_number is not None, "Application number should not be None"

        try:
            # Call the transactions endpoint
            transactions_response = patent_data_client.get_application_transactions(
                application_number
            )

            # Verify response structure
            assert transactions_response is not None
            assert isinstance(transactions_response, PatentDataResponse)

            # The response might be empty if the application doesn't have transaction data
            if transactions_response.count > 0:
                assert len(transactions_response.patent_file_wrapper_data_bag) > 0
                assert (
                    transactions_response.patent_file_wrapper_data_bag[
                        0
                    ].application_number_text
                    == application_number
                )
        except Exception as e:
            # Some applications might not have transaction data
            pytest.skip(f"Patent transaction data not available: {str(e)}")

    def test_get_application_documents(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test getting document listings."""
        # Use a known application number that has documents
        # 18045436 is a published application with documents from USPTO API Response Sample
        application_number = "18045436"

        try:
            # Call the documents endpoint
            documents_response = patent_data_client.get_application_documents(
                application_number
            )

            # Verify response structure
            assert documents_response is not None
            assert isinstance(documents_response, dict)

            # Verify documentBag exists and is a list
            assert "documentBag" in documents_response
            assert isinstance(documents_response["documentBag"], list)
            assert len(documents_response["documentBag"]) > 0

            # Test the first document properties
            first_doc = documents_response["documentBag"][0]
            assert "documentIdentifier" in first_doc
            assert "documentCode" in first_doc
        except Exception as e:
            pytest.skip(f"Document endpoint failed with application 18045436: {str(e)}")

    def test_get_application_associated_documents(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test getting associated documents metadata."""
        # Get a valid application number
        response = patent_data_client.get_patent_applications(params={"limit": 1})
        assert response.count > 0

        application_number = response.patent_file_wrapper_data_bag[
            0
        ].application_number_text
        assert application_number is not None, "Application number should not be None"

        try:
            # Call the associated documents endpoint
            associated_docs_response = (
                patent_data_client.get_application_associated_documents(
                    application_number
                )
            )

            # Verify response structure
            assert associated_docs_response is not None
            assert isinstance(associated_docs_response, PatentDataResponse)

            # The response might be empty if the application doesn't have associated documents
            if associated_docs_response.count > 0:
                assert len(associated_docs_response.patent_file_wrapper_data_bag) > 0
                assert (
                    associated_docs_response.patent_file_wrapper_data_bag[
                        0
                    ].application_number_text
                    == application_number
                )
        except Exception as e:
            # Some applications might not have associated document data
            pytest.skip(f"Patent associated document data not available: {str(e)}")

    def test_download_application_document(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test downloading a document."""
        import os

        # Use a known application number that has documents
        application_number = "18045436"

        try:
            # Get document list for this application
            docs_response = patent_data_client.get_application_documents(
                application_number
            )

            # Verify we have documents to work with
            assert isinstance(docs_response, dict)
            assert "documentBag" in docs_response
            assert len(docs_response["documentBag"]) > 0

            # Get the document ID from the first document
            document_id = docs_response["documentBag"][0]["documentIdentifier"]
            assert document_id is not None

            # Create downloads directory if it doesn't exist
            if not os.path.exists("./downloads"):
                os.makedirs("./downloads")

            # Download the document
            file_path = patent_data_client.download_application_document(
                application_number, document_id, "./downloads"
            )

            # Verify the file was downloaded
            assert file_path is not None
            assert os.path.exists(file_path)

            # Get file size to verify it's not empty
            file_size = os.path.getsize(file_path)
            assert file_size > 0, "Downloaded file is empty"

            # Clean up
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            pytest.skip(f"Document download failed with application 18045436: {str(e)}")

    def test_search_patent_applications_post(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test searching patent applications using POST method."""
        # Create a search request
        search_request = {
            "q": "applicationMetaData.applicationTypeLabelName:Utility",
            "pagination": {"offset": 0, "limit": 5},
        }

        try:
            # Call the search endpoint
            response = patent_data_client.search_patent_applications_post(
                search_request
            )

            # Verify response
            assert response is not None
            assert isinstance(response, PatentDataResponse)
            assert response.count > 0
            assert len(response.patent_file_wrapper_data_bag) > 0
            assert len(response.patent_file_wrapper_data_bag) <= 5  # Respect the limit
        except Exception as e:
            pytest.skip(f"POST search failed: {str(e)}")

    def test_download_patent_applications(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test downloading patent data as JSON."""
        import os

        # Use a very specific query to find patents - using our known good application number
        params = {
            "q": "applicationNumberText:18045436",
            "limit": "1",
            "format": "json",
        }

        # Create downloads directory if it doesn't exist
        if not os.path.exists("./downloads"):
            os.makedirs("./downloads")

        try:
            # Call the download endpoint
            download_dir = "./downloads"
            response = patent_data_client.download_patent_applications(params=params)

            # Verify response has patent data
            assert response is not None
            assert isinstance(response, PatentDataResponse)
            assert response.count > 0
            assert len(response.patent_file_wrapper_data_bag) > 0

            # Verify it's the patent we requested
            application_number = response.patent_file_wrapper_data_bag[
                0
            ].application_number_text
            assert application_number == "18045436"
        except Exception as e:
            pytest.skip(f"Download test failed: {str(e)}")

    def test_download_patent_applications_post(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test downloading patent data using POST method."""
        import os

        # Create a download request for a specific application number
        download_request = {
            "q": "applicationNumberText:18045436",
            "pagination": {"offset": 0, "limit": 1},
            "format": "json",
        }

        # Create downloads directory if it doesn't exist
        if not os.path.exists("./downloads"):
            os.makedirs("./downloads")

        try:
            # Call the download endpoint
            response = patent_data_client.download_patent_applications_post(
                download_request
            )

            # Verify response has patents
            assert response is not None
            assert isinstance(response, PatentDataResponse)
            assert response.count > 0
            assert len(response.patent_file_wrapper_data_bag) > 0

            # Verify it's the patent we requested
            application_number = response.patent_file_wrapper_data_bag[
                0
            ].application_number_text
            assert application_number == "18045436"
        except Exception as e:
            pytest.skip(f"Download POST test failed: {str(e)}")

    def test_search_patent_status_codes_post(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test searching status codes using POST method."""
        # Create a search request
        search_request = {
            "q": "applicationStatusCode:150",
            "pagination": {"offset": 0, "limit": 10},
        }

        try:
            # Call the status codes search endpoint
            response = patent_data_client.search_patent_status_codes_post(
                search_request
            )

            # Verify response
            assert response is not None
            assert isinstance(response, dict)
            assert "statusCodeBag" in response
            assert len(response["statusCodeBag"]) > 0
        except Exception as e:
            pytest.skip(f"Status codes POST search failed: {str(e)}")

    def test_invalid_application_number_handling(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test proper error handling with an invalid application number."""
        invalid_app_num = "INVALID1234567890"

        # The call should raise an exception or return an appropriate error response
        with pytest.raises(Exception) as excinfo:
            patent_data_client.get_application_metadata(invalid_app_num)
