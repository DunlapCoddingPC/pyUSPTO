"""
Tests for edge cases and specific uncovered lines in patent_data.py.

This module focuses on testing specific edge cases and lines that were previously uncovered.
"""

from unittest.mock import MagicMock, patch

import pytest
import requests

from pyUSPTO.clients.patent_data import PatentDataClient
from pyUSPTO.models.patent_data import PatentDataResponse, PatentFileWrapper


class TestPatentDataEdgeCases:
    """Tests focusing on edge cases and previously uncovered lines in PatentDataClient."""

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_adjustment_assert_type(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test get_application_adjustment with a non-PatentDataResponse return type."""
        # Setup mock to return a dict instead of PatentDataResponse to trigger assertion
        mock_make_request.return_value = {"data": "test"}

        # Create client
        client = PatentDataClient(api_key="test_key")

        # Expect assertion error when not returning PatentDataResponse
        with pytest.raises(AssertionError):
            client.get_application_adjustment(application_number="12345678")

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_attorney_edge_case(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test get_application_attorney with edge case response."""
        # Return different types of response to trigger different code paths
        mock_response = {"custom_key": "value"}
        mock_make_request.return_value = mock_response

        # Create client
        client = PatentDataClient(api_key="test_key")

        # Expect assertion error
        with pytest.raises(AssertionError):
            client.get_application_attorney(application_number="12345678")

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_search_patents_with_empty_query(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test search_patents with empty query parameters."""
        # Setup mock response
        mock_response_obj = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        # Create client and call method with no search parameters
        client = PatentDataClient(api_key="test_key")
        result = client.search_patents()

        # Verify request was made with empty q parameter
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/search",
            params={"offset": "0", "limit": "25"},
            response_class=PatentDataResponse,
        )

        # Verify result
        assert isinstance(result, PatentDataResponse)
        assert result.count == 0

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_patent_status_codes_edge_cases(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test edge cases for get_patent_status_codes method."""
        # Test with different response types to cover assertion branches
        # 1. Test with non-dict response
        mock_make_request.return_value = "not a dict"

        client = PatentDataClient(api_key="test_key")

        # Should raise TypeError for non-dict response
        with pytest.raises(AssertionError):
            client.get_patent_status_codes()

        # 2. Test with empty dict response
        mock_make_request.return_value = {}

        # Should not raise error even with empty dict
        result = client.get_patent_status_codes()
        assert result == {}

        # 3. Test with minimal dict
        mock_make_request.return_value = {"count": 0}

        result = client.get_patent_status_codes()
        assert result == {"count": 0}

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_search_patent_status_codes_post_edge_cases(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test edge cases for search_patent_status_codes_post method."""
        # Test with different response types
        # 1. Test with non-dict response
        mock_make_request.return_value = "not a dict"

        client = PatentDataClient(api_key="test_key")

        # Should raise TypeError for non-dict response
        with pytest.raises(AssertionError):
            client.search_patent_status_codes_post({"q": "test"})

        # 2. Test with different dict structures
        mock_make_request.return_value = {"statusCodeBag": []}

        result = client.search_patent_status_codes_post({"q": "test"})
        assert result == {"statusCodeBag": []}
