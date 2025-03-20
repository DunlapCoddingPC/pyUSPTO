"""
Tests for the patent_data status code retrieval methods.

This module focuses specifically on testing the status code retrieval methods
to improve coverage and ensure proper functionality.
"""

from unittest.mock import MagicMock, patch

import pytest
import requests

from pyUSPTO.clients.patent_data import PatentDataClient


class TestPatentDataStatusCodes:
    """Tests for the status code retrieval methods of the PatentDataClient class."""

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

        # Test with search query
        result = client.get_patent_status_codes(params={"q": "awaiting"})
        mock_make_request.assert_called_with(
            method="GET",
            endpoint="status-codes",
            params={"q": "awaiting"},
        )
        assert result == mock_response

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
    def test_get_patent_status_codes_response_handling(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test get_patent_status_codes with various response formats."""
        # Create client
        client = PatentDataClient(api_key="test_key")

        # Test with empty dict response
        mock_make_request.return_value = {}
        result = client.get_patent_status_codes()
        assert result == {}

        # Test with minimal response
        mock_make_request.return_value = {"count": 0}
        result = client.get_patent_status_codes()
        assert result == {"count": 0}

        # Test with statusCodeBag but no count
        mock_make_request.return_value = {"statusCodeBag": []}
        result = client.get_patent_status_codes()
        assert result == {"statusCodeBag": []}

        # Test with unusual but valid structure
        mock_make_request.return_value = {
            "statusCodeBag": [],
            "additionalInfo": "test",
            "pagination": {"total": 0},
        }
        result = client.get_patent_status_codes()
        assert result["additionalInfo"] == "test"
        assert result["pagination"]["total"] == 0

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

        # Test with basic search request
        search_request = {
            "q": "awaiting",
            "limit": "10",
            "offset": "0",
        }
        result = client.search_patent_status_codes_post(search_request=search_request)
        mock_make_request.assert_called_with(
            method="POST",
            endpoint="status-codes",
            json_data=search_request,
        )
        assert result == mock_response

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
    def test_search_patent_status_codes_post_error_handling(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test search_patent_status_codes_post error handling."""
        # Create client
        client = PatentDataClient(api_key="test_key")

        # Test with response that has unexpected format but is still a dict
        mock_make_request.return_value = {"error": "Invalid request"}
        result = client.search_patent_status_codes_post({"q": "test"})
        assert result == {"error": "Invalid request"}

        # Test with nested dict response
        mock_make_request.return_value = {
            "response": {"data": {"statusCodeBag": [], "count": 0}}
        }
        result = client.search_patent_status_codes_post({"q": "test"})
        assert result["response"]["data"]["count"] == 0

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

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_patent_status_codes_response_types(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test get_patent_status_codes with different response types to ensure correct handling."""
        # Create client
        client = PatentDataClient(api_key="test_key")

        # Test with empty dict
        mock_make_request.return_value = {}
        result = client.get_patent_status_codes()
        assert isinstance(result, dict)
        assert len(result) == 0

        # Test with dict with only statusCodeBag
        mock_make_request.return_value = {"statusCodeBag": []}
        result = client.get_patent_status_codes()
        assert isinstance(result, dict)
        assert "statusCodeBag" in result
        assert len(result["statusCodeBag"]) == 0

        # Test with dict with only count
        mock_make_request.return_value = {"count": 0}
        result = client.get_patent_status_codes()
        assert isinstance(result, dict)
        assert "count" in result
        assert result["count"] == 0

        # Test with custom dict
        mock_make_request.return_value = {"custom_key": "value"}
        result = client.get_patent_status_codes()
        assert isinstance(result, dict)
        assert result["custom_key"] == "value"
