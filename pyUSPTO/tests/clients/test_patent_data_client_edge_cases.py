"""
Tests for edge cases and error handling in the patent_data client module.

This module focuses on testing error handling, unexpected response types,
and unusual input/output combinations for the PatentDataClient class.
"""

from unittest.mock import MagicMock, patch

import pytest
import requests

from pyUSPTO.clients.patent_data import PatentDataClient
from pyUSPTO.models.patent_data import PatentDataResponse


class TestPatentDataEdgeCases:
    """Tests for error handling and edge cases in the PatentDataClient class."""

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
    def test_download_document_non_response_object(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test download_document with a non-Response object."""
        # Return an object that is definitely not a requests.Response
        mock_make_request.return_value = {"not": "a response object"}

        # Create client
        client = PatentDataClient(api_key="test_key")

        # Call should raise TypeError
        with pytest.raises(
            TypeError, match="Expected a Response object for streaming download"
        ):
            client.download_document(
                destination="/tmp", download_url="https://example.com/test.pdf"
            )

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_patent_applications_invalid_params(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test download_patent_applications with invalid parameters."""
        # Setup mock to raise an exception for invalid params
        mock_make_request.side_effect = ValueError("Invalid parameters")

        # Create client and call method with invalid params
        client = PatentDataClient(api_key="test_key")
        with pytest.raises(ValueError) as exc_info:
            client.download_patent_applications(params={"invalid_param": "value"})

        # Verify the exception message
        assert str(exc_info.value) == "Invalid parameters"

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/search/download",
            params={"invalid_param": "value", "format": "json"},
            response_class=PatentDataResponse,
        )


class TestResponseTypeHandling:
    """Tests for handling different response types and type assertions."""

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
    def test_get_application_attorney_special_response_types(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test get_application_attorney with special response types."""
        # Create client
        client = PatentDataClient(api_key="test_key")

        # 1. Test with PatentDataResponse object already
        mock_response = PatentDataResponse(count=1, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response

        result = client.get_application_attorney(application_number="12345678")
        assert result is mock_response

        # 2. Test with unexpected response type
        mock_make_request.return_value = "not a PatentDataResponse"

        with pytest.raises(AssertionError):
            client.get_application_attorney(application_number="12345678")
