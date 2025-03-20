"""
Tests for the document-related methods of the patent_data client module.

This module contains tests for document downloading and handling methods
of the PatentDataClient class.
"""

import os
from unittest.mock import MagicMock, mock_open, patch

import pytest
import requests

from pyUSPTO.clients.patent_data import PatentDataClient
from pyUSPTO.models.patent_data import PatentDataResponse, PatentFileWrapper


class TestDocumentHandling:
    """Tests for document handling methods of the PatentDataClient."""

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_application_document(self, mock_make_request: MagicMock) -> None:
        """Test download_application_document method."""
        # Setup mock for the response
        mock_response = MagicMock(spec=requests.Response)
        mock_response.headers = {"Content-Disposition": 'filename="test_document.pdf"'}
        mock_response.iter_content.return_value = [b"test content"]
        mock_make_request.return_value = mock_response

        # Mock open function
        mock_open_func = mock_open()
        mock_file = MagicMock()
        mock_open_func.return_value.__enter__.return_value = mock_file

        with patch("builtins.open", mock_open_func), patch(
            "os.path.exists", return_value=True
        ):
            # Create client and call method
            client = PatentDataClient(api_key="test_key")
            result = client.download_application_document(
                application_number="12345678", document_id="DOC123", destination="/tmp"
            )

            # Verify request was made correctly with correct base URL handling
            mock_make_request.assert_called_once_with(
                method="GET",
                endpoint="download/applications/12345678/DOC123",
                stream=True,
                custom_base_url=client.base_url.split("/patent")[0],
            )

            # Verify file was written correctly
            mock_file.write.assert_called_with(b"test content")
            # Use os.path.join for cross-platform paths
            assert result == os.path.join("/tmp", "test_document.pdf")

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_application_document_content_disposition_parsing(
        self, mock_make_request
    ) -> None:
        """Test download_application_document with Content-Disposition header parsing."""
        # Setup mock to simulate a Response object
        mock_response = MagicMock(spec=requests.Response)
        mock_response.headers = {
            "Content-Disposition": 'attachment; filename="test_file.pdf"'
        }
        mock_response.iter_content.return_value = [b"test content"]
        mock_make_request.return_value = mock_response

        # Setup os.path.exists to return False so os.makedirs is called
        with patch("os.path.exists", return_value=False), patch(
            "os.makedirs"
        ) as mock_makedirs, patch("builtins.open", mock_open()) as mock_file:
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
            mock_file.assert_called_once_with(file=result, mode="wb")

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_application_document_no_filename_in_header(
        self, mock_make_request
    ) -> None:
        """Test download_application_document with Content-Disposition header but no filename."""
        # Setup mock to simulate a Response object
        mock_response = MagicMock(spec=requests.Response)
        mock_response.headers = {"Content-Disposition": "attachment;"}  # No filename
        mock_response.iter_content.return_value = [b"test content"]
        mock_make_request.return_value = mock_response

        # Setup os.path.exists to return False so os.makedirs is called
        with patch("os.path.exists", return_value=False), patch(
            "os.makedirs"
        ) as mock_makedirs, patch("builtins.open", mock_open()) as mock_file:
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
    def test_download_application_document_no_content_disposition(
        self, mock_make_request
    ) -> None:
        """Test download_application_document without Content-Disposition header."""
        # Setup mock to simulate a Response object
        mock_response = MagicMock(spec=requests.Response)
        mock_response.headers = {}  # No Content-Disposition header
        mock_response.iter_content.return_value = [b"test content"]
        mock_make_request.return_value = mock_response

        # Setup os.path.exists to return False so os.makedirs is called
        with patch("os.path.exists", return_value=False), patch(
            "os.makedirs"
        ) as mock_makedirs, patch("builtins.open", mock_open()) as mock_file:
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
    def test_get_application_documents(self, mock_make_request: MagicMock) -> None:
        """Test get_application_documents method."""
        # Setup mock
        mock_response_obj = PatentDataResponse(count=1, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        result = client.get_application_documents(application_number="12345678")

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/12345678/documents",
            response_class=PatentDataResponse,
        )

        # Verify result
        assert isinstance(result, PatentDataResponse)
        assert result.count == 1

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_associated_documents(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test get_application_associated_documents method."""
        # Setup mock
        mock_response_obj = PatentDataResponse(count=1, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        result = client.get_application_associated_documents(
            application_number="12345678"
        )

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/12345678/associated-documents",
            response_class=PatentDataResponse,
        )

        # Verify result
        assert isinstance(result, PatentDataResponse)
        assert result.count == 1


class TestPatentApplicationDownloads:
    """Tests for patent application download methods."""

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_patent_applications_default_params(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test download_patent_applications with default parameters."""
        # Setup mock response
        mock_response_obj = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        # Create client and call method without params
        client = PatentDataClient(api_key="test_key")
        result = client.download_patent_applications()

        # Verify request was made correctly with default format
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/search/download",
            params={"format": "json"},
            response_class=PatentDataResponse,
        )

        # Verify the result type
        assert isinstance(result, PatentDataResponse)

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_patent_applications_missing_format(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test download_patent_applications when format is missing in params."""
        # Setup mock response
        mock_response_obj = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        # Create client and call method with params missing 'format'
        client = PatentDataClient(api_key="test_key")
        result = client.download_patent_applications(params={"q": "test"})

        # Verify request was made correctly with default format added
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/search/download",
            params={"q": "test", "format": "json"},
            response_class=PatentDataResponse,
        )

        # Verify the result type
        assert isinstance(result, PatentDataResponse)

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_patent_applications_custom_format(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test download_patent_applications with custom format."""
        # Setup mock response
        mock_response_obj = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        # Create client and call method with custom format
        client = PatentDataClient(api_key="test_key")
        result = client.download_patent_applications(format="csv")

        # Verify request was made correctly with custom format
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/search/download",
            params={"format": "csv"},
            response_class=PatentDataResponse,
        )

        # Verify the result type
        assert isinstance(result, PatentDataResponse)

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_patent_applications_format_argument(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test download_patent_applications with format passed as a separate argument."""
        # Setup mock response
        mock_response_obj = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        # Create client and call method with format passed as a separate argument
        client = PatentDataClient(api_key="test_key")
        result = client.download_patent_applications(params={"q": "test"}, format="csv")

        # Verify request was made correctly with format added to params
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/search/download",
            params={"q": "test", "format": "csv"},
            response_class=PatentDataResponse,
        )

        # Verify the result type
        assert isinstance(result, PatentDataResponse)

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_patent_applications_post(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test download_patent_applications_post method."""
        # Setup mock
        mock_response_obj = PatentDataResponse(
            count=1,
            patent_file_wrapper_data_bag=[
                PatentFileWrapper(
                    application_number_text="12345678",
                    application_meta_data=MagicMock(invention_title="Test Invention"),
                ),
            ],
        )
        mock_make_request.return_value = mock_response_obj

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        download_request = {
            "q": "Test",
            "format": "csv",
            "fields": ["patentNumber", "inventionTitle"],
        }
        result = client.download_patent_applications_post(
            download_request=download_request
        )

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="POST",
            endpoint="applications/search/download",
            json_data=download_request,
            response_class=PatentDataResponse,
        )

        # Verify result
        assert isinstance(result, PatentDataResponse)
        assert result.count == 1
