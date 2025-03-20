"""
Tests for the metadata and status-related methods of the patent_data client module.

This module contains tests for metadata retrieval, status code handling, and other
auxiliary data methods in the PatentDataClient class.
"""

from unittest.mock import MagicMock, patch

import pytest

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


class TestStatusCodeHandling:
    """Tests for status code handling methods."""

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_patent_status_codes(self, mock_make_request: MagicMock) -> None:
        """Test get_patent_status_codes method."""
        # Setup mock
        mock_response = {
            "statusCodeBag": [
                {
                    "statusCode": "150",
                    "statusText": "Awaiting Assignment",
                },
                {
                    "statusCode": "250",
                    "statusText": "Assigned to Examiner",
                },
            ],
            "count": 2,
        }
        mock_make_request.return_value = mock_response

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        result = client.get_patent_status_codes(params={"q": "awaiting"})

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="status-codes",
            params={"q": "awaiting"},
        )

        # Verify result
        assert isinstance(result, dict)
        assert result == mock_response
        assert result["count"] == 2
        assert len(result["statusCodeBag"]) == 2

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_patent_status_codes_with_params(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test get_patent_status_codes method with different parameter combinations."""
        # Setup mock
        mock_response = {
            "statusCodeBag": [
                {
                    "statusCode": "150",
                    "statusText": "Awaiting Assignment",
                    "statusCategory": "Examination",
                    "statusDate": "2020-01-01",
                },
                {
                    "statusCode": "250",
                    "statusText": "Assigned to Examiner",
                    "statusCategory": "Examination",
                    "statusDate": "2020-02-01",
                },
            ],
            "count": 2,
        }
        mock_make_request.return_value = mock_response

        # Create client
        client = PatentDataClient(api_key="test_key")

        # Test with offset and limit
        mock_make_request.reset_mock()
        result = client.get_patent_status_codes(params={"offset": "10", "limit": "5"})
        mock_make_request.assert_called_with(
            method="GET",
            endpoint="status-codes",
            params={"offset": "10", "limit": "5"},
        )
        assert result == mock_response

        # Test with combination of parameters
        mock_make_request.reset_mock()
        result = client.get_patent_status_codes(
            params={"q": "examination", "offset": "0", "limit": "10"}
        )
        mock_make_request.assert_called_with(
            method="GET",
            endpoint="status-codes",
            params={"q": "examination", "offset": "0", "limit": "10"},
        )
        assert result == mock_response

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_search_patent_status_codes_post(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test search_patent_status_codes_post method."""
        # Setup mock
        mock_response = {
            "statusCodeBag": [
                {
                    "statusCode": "150",
                    "statusText": "Awaiting Assignment",
                },
            ],
            "count": 1,
        }
        mock_make_request.return_value = mock_response

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        search_request = {
            "q": "awaiting",
            "limit": 10,
            "offset": 0,
        }
        result = client.search_patent_status_codes_post(search_request=search_request)

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="POST",
            endpoint="status-codes",
            json_data=search_request,
        )

        # Verify result
        assert isinstance(result, dict)
        assert result == mock_response
        assert result["count"] == 1

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_search_patent_status_codes_post_with_various_payloads(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test search_patent_status_codes_post with different payload structures."""
        # Setup mock
        mock_response = {
            "statusCodeBag": [
                {
                    "statusCode": "150",
                    "statusText": "Awaiting Assignment",
                }
            ],
            "count": 1,
        }
        mock_make_request.return_value = mock_response

        # Create client
        client = PatentDataClient(api_key="test_key")

        # Test with more complex search request
        mock_make_request.reset_mock()
        search_request = {
            "filters": [{"field": "statusCategory", "value": "Examination"}],
            "pagination": {"offset": "0", "limit": "25"},
            "sort": [{"field": "statusDate", "order": "desc"}],
        }
        result = client.search_patent_status_codes_post(search_request=search_request)
        mock_make_request.assert_called_with(
            method="POST",
            endpoint="status-codes",
            json_data=search_request,
        )
        assert result == mock_response

        # Test with empty search request
        mock_make_request.reset_mock()
        search_request = {}
        result = client.search_patent_status_codes_post(search_request=search_request)
        mock_make_request.assert_called_with(
            method="POST",
            endpoint="status-codes",
            json_data=search_request,
        )
        assert result == mock_response

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_patent_status_codes_with_none_params(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test get_patent_status_codes with None params."""
        # Setup mock
        mock_response = {"statusCodeBag": [], "count": 0}
        mock_make_request.return_value = mock_response

        # Create client
        client = PatentDataClient(api_key="test_key")

        # Test with None params (should not cause errors)
        result = client.get_patent_status_codes(params=None)
        mock_make_request.assert_called_with(
            method="GET",
            endpoint="status-codes",
            params=None,
        )
        assert result == mock_response
