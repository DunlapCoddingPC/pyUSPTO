"""
Tests for the patent_data processing methods.

This module contains tests for document download and specific data processing methods.
"""

import os
from unittest.mock import MagicMock, mock_open, patch

import pytest
import requests

from pyUSPTO.clients.patent_data import PatentDataClient
from pyUSPTO.models.patent_data import PatentDataResponse, PatentFileWrapper


class TestPatentDataProcessing:
    """Tests for document download and processing methods of the PatentDataClient class."""

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

        # Test with no Content-Disposition header
        mock_response.headers = {}
        mock_make_request.return_value = mock_response

        with patch("builtins.open", mock_open_func), patch(
            "os.path.exists", return_value=False
        ), patch("os.makedirs") as mock_makedirs:
            # Create client and call method
            client = PatentDataClient(api_key="test_key")
            result = client.download_application_document(
                application_number="12345678", document_id="DOC123", destination="/tmp"
            )

            # Verify directory creation
            mock_makedirs.assert_called_once_with("/tmp")

            # Verify fallback to document_id for filename
            assert result == os.path.join("/tmp", "DOC123")

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_patent_applications(self, mock_make_request: MagicMock) -> None:
        """Test download_patent_applications method."""
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
        params = {
            "q": "Test",
            "limit": "25",
        }
        result = client.download_patent_applications(params=params, format="json")

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/search/download",
            params={"q": "Test", "limit": "25", "format": "json"},
            response_class=PatentDataResponse,
        )

        # Verify result
        assert isinstance(result, PatentDataResponse)
        assert result.count == 1

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

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_adjustment(self, mock_make_request: MagicMock) -> None:
        """Test get_application_adjustment method."""
        # Setup mock
        mock_response_obj = PatentDataResponse(count=1, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        result = client.get_application_adjustment(application_number="12345678")

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/12345678/adjustment",
            response_class=PatentDataResponse,
        )

        # Verify result
        assert isinstance(result, PatentDataResponse)
        assert result.count == 1

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_assignment(self, mock_make_request: MagicMock) -> None:
        """Test get_application_assignment method."""
        # Setup mock
        mock_response_obj = PatentDataResponse(count=1, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        result = client.get_application_assignment(application_number="12345678")

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/12345678/assignment",
            response_class=PatentDataResponse,
        )

        # Verify result
        assert isinstance(result, PatentDataResponse)
        assert result.count == 1

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_attorney(self, mock_make_request: MagicMock) -> None:
        """Test get_application_attorney method."""
        # Setup mock
        mock_response_obj = PatentDataResponse(count=1, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        result = client.get_application_attorney(application_number="12345678")

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/12345678/attorney",
            response_class=PatentDataResponse,
        )

        # Verify result
        assert isinstance(result, PatentDataResponse)
        assert result.count == 1

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_continuity(self, mock_make_request: MagicMock) -> None:
        """Test get_application_continuity method."""
        # Setup mock
        mock_response_obj = PatentDataResponse(count=1, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        result = client.get_application_continuity(application_number="12345678")

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/12345678/continuity",
            response_class=PatentDataResponse,
        )

        # Verify result
        assert isinstance(result, PatentDataResponse)
        assert result.count == 1

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_foreign_priority(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test get_application_foreign_priority method."""
        # Setup mock
        mock_response_obj = PatentDataResponse(count=1, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        result = client.get_application_foreign_priority(application_number="12345678")

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/12345678/foreign-priority",
            response_class=PatentDataResponse,
        )

        # Verify result
        assert isinstance(result, PatentDataResponse)
        assert result.count == 1

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_transactions(self, mock_make_request: MagicMock) -> None:
        """Test get_application_transactions method."""
        # Setup mock
        mock_response_obj = PatentDataResponse(count=1, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        result = client.get_application_transactions(application_number="12345678")

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/12345678/transactions",
            response_class=PatentDataResponse,
        )

        # Verify result
        assert isinstance(result, PatentDataResponse)
        assert result.count == 1

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
