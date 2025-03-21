"""
Tests for the metadata and status-related methods of the patent_data client module.

This module contains tests for metadata retrieval, status code handling, and other
auxiliary data methods in the PatentDataClient class.
"""

from unittest.mock import MagicMock, patch

from pyUSPTO.clients.patent_data import PatentDataClient
from pyUSPTO.models.patent_data import PatentDataResponse


class TestApplicationMetadata:
    """Tests for application metadata methods."""

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_metadata(self, mock_make_request: MagicMock) -> None:
        """Test get_application_metadata method."""
        # Setup mock with a response object
        mock_response_obj = PatentDataResponse(
            count=1,
            patent_file_wrapper_data_bag=[
                MagicMock(
                    application_number_text="12345678",
                    application_meta_data=MagicMock(invention_title="Test Invention"),
                ),
            ],
        )
        mock_make_request.return_value = mock_response_obj

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        result = client.get_application_metadata(application_number="12345678")

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/12345678/meta-data",
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


# Status code handling tests have been moved to test_patent_data_client_status_codes.py
