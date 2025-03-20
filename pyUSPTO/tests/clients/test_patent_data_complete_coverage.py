"""
Tests specifically targeting remaining uncovered lines in patent_data.py.

This module focuses on achieving complete test coverage for all lines in the PatentDataClient class.
"""

import os
from unittest.mock import MagicMock, mock_open, patch

import pytest
from requests import Response

from pyUSPTO.clients.patent_data import PatentDataClient
from pyUSPTO.models.patent_data import PatentDataResponse


class TestPatentDataCompleteCoverage:
    """Tests focusing specifically on remaining uncovered lines in PatentDataClient."""

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_patent_by_application_number_patentFileWrapperDataBag_not_found(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test get_patent_by_application_number when application not found in patentFileWrapperDataBag."""
        # Setup mock to return a response with patentFileWrapperDataBag but not containing the requested application
        mock_response = {
            "patentFileWrapperDataBag": [
                {"applicationNumberText": "87654321", "otherData": "test"},
            ]
        }
        mock_make_request.return_value = mock_response

        # Create client
        client = PatentDataClient(api_key="test_key")

        # This should trigger the ValueError when application not found in patentFileWrapperDataBag
        with pytest.raises(
            ValueError,
            match="Patent with application number 12345678 not found in response",
        ):
            client.get_patent_by_application_number(application_number="12345678")

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_patent_by_application_number_unexpected_response_type(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test get_patent_by_application_number with unexpected response type."""
        # Setup mock to return a non-dict, non-PatentFileWrapper response
        mock_make_request.return_value = ["unexpected", "response", "type"]

        # Create client
        client = PatentDataClient(api_key="test_key")

        # This should trigger the TypeError for unexpected response type
        with pytest.raises(TypeError, match="Unexpected response type"):
            client.get_patent_by_application_number(application_number="12345678")

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_application_document_type_error_handling(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test download_application_document with non-Response object."""
        # Setup mock to return something that's not a requests.Response
        mock_make_request.return_value = {"not": "a response object"}

        # Create client
        client = PatentDataClient(api_key="test_key")

        # This should trigger the TypeError for expected Response object
        with pytest.raises(
            TypeError, match="Expected a Response object for streaming download"
        ):
            client.download_application_document(
                application_number="12345678",
                document_id="document123",
                destination="./downloads",
            )

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    @patch("os.path.exists")
    @patch("os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    def test_download_application_document_content_disposition_parsing(
        self, mock_file_open, mock_makedirs, mock_path_exists, mock_make_request
    ) -> None:
        """Test download_application_document with Content-Disposition header."""
        # Setup mock to simulate a Response object
        mock_response = MagicMock(spec=Response)
        mock_response.headers = {
            "Content-Disposition": 'attachment; filename="test_file.pdf"'
        }
        mock_response.iter_content.return_value = [b"test content"]
        mock_make_request.return_value = mock_response

        # Setup os.path.exists to return False so os.makedirs is called
        mock_path_exists.return_value = False

        # Create client
        client = PatentDataClient(api_key="test_key")

        # Call the method
        result = client.download_application_document(
            application_number="12345678",
            document_id="document123",
            destination="./downloads",
        )

        # Verify the path extraction from Content-Disposition header
        assert result == os.path.join("./downloads", "test_file.pdf")
        mock_makedirs.assert_called_once_with("./downloads")
        mock_file_open.assert_called_once_with(file=result, mode="wb")

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    @patch("os.path.exists")
    @patch("os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    def test_download_application_document_no_filename_in_header(
        self, mock_file_open, mock_makedirs, mock_path_exists, mock_make_request
    ) -> None:
        """Test download_application_document with Content-Disposition header but no filename."""
        # Setup mock to simulate a Response object
        mock_response = MagicMock(spec=Response)
        mock_response.headers = {"Content-Disposition": "attachment;"}  # No filename
        mock_response.iter_content.return_value = [b"test content"]
        mock_make_request.return_value = mock_response

        # Setup os.path.exists to return False so os.makedirs is called
        mock_path_exists.return_value = False

        # Create client
        client = PatentDataClient(api_key="test_key")

        # Call the method
        result = client.download_application_document(
            application_number="12345678",
            document_id="document123",
            destination="./downloads",
        )

        # Should use document_id as filename
        assert result == os.path.join("./downloads", "document123")

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    @patch("os.path.exists")
    @patch("os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    def test_download_application_document_no_content_disposition(
        self, mock_file_open, mock_makedirs, mock_path_exists, mock_make_request
    ) -> None:
        """Test download_application_document without Content-Disposition header."""
        # Setup mock to simulate a Response object
        mock_response = MagicMock(spec=Response)
        mock_response.headers = {}  # No Content-Disposition header
        mock_response.iter_content.return_value = [b"test content"]
        mock_make_request.return_value = mock_response

        # Setup os.path.exists to return False so os.makedirs is called
        mock_path_exists.return_value = False

        # Create client
        client = PatentDataClient(api_key="test_key")

        # Call the method
        result = client.download_application_document(
            application_number="12345678",
            document_id="document123",
            destination="./downloads",
        )

        # Should use document_id as filename when no Content-Disposition header
        assert result == os.path.join("./downloads", "document123")

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_search_patents_all_date_filter_combinations(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test search_patents with various date filter combinations."""
        # Setup mock
        mock_response = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response

        # Create client
        client = PatentDataClient(api_key="test_key")

        # Test with filing_date_from only
        client.search_patents(filing_date_from="2020-01-01")
        mock_make_request.assert_called_with(
            method="GET",
            endpoint="applications/search",
            params={
                "q": "applicationMetaData.filingDate:>=2020-01-01",
                "offset": "0",
                "limit": "25",
            },
            response_class=PatentDataResponse,
        )

        # Test with filing_date_to only
        mock_make_request.reset_mock()
        client.search_patents(filing_date_to="2022-01-01")
        mock_make_request.assert_called_with(
            method="GET",
            endpoint="applications/search",
            params={
                "q": "applicationMetaData.filingDate:<=2022-01-01",
                "offset": "0",
                "limit": "25",
            },
            response_class=PatentDataResponse,
        )

        # Test with grant_date_from only
        mock_make_request.reset_mock()
        client.search_patents(grant_date_from="2020-01-01")
        mock_make_request.assert_called_with(
            method="GET",
            endpoint="applications/search",
            params={
                "q": "applicationMetaData.grantDate:>=2020-01-01",
                "offset": "0",
                "limit": "25",
            },
            response_class=PatentDataResponse,
        )

        # Test with grant_date_to only
        mock_make_request.reset_mock()
        client.search_patents(grant_date_to="2022-01-01")
        mock_make_request.assert_called_with(
            method="GET",
            endpoint="applications/search",
            params={
                "q": "applicationMetaData.grantDate:<=2022-01-01",
                "offset": "0",
                "limit": "25",
            },
            response_class=PatentDataResponse,
        )

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_attorney_special_response_types(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test get_application_attorney with special response types to cover uncovered lines."""
        # Create client
        client = PatentDataClient(api_key="test_key")

        # 1. Test with PatentDataResponse object already (no need for assertion)
        mock_response = PatentDataResponse(count=1, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response

        result = client.get_application_attorney(application_number="12345678")
        assert result is mock_response

        # 2. Test with unexpected response type to trigger assertion error
        mock_make_request.return_value = "not a PatentDataResponse"

        with pytest.raises(AssertionError):
            client.get_application_attorney(application_number="12345678")
