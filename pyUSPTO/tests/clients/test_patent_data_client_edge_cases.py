"""
Tests for edge cases and error handling in the patent_data client module.

This module focuses on testing error handling, unexpected response types,
and unusual input/output combinations for the PatentDataClient class.
"""

from unittest.mock import MagicMock, patch

import pytest
import requests

from pyUSPTO.clients.patent_data import PatentDataClient
from pyUSPTO.exceptions import USPTOApiBadRequestError

# Import necessary models for constructing mock responses
from pyUSPTO.models.patent_data import (
    ApplicationMetaData,
    PatentDataResponse,
    PatentFileWrapper,
    RecordAttorney,
)


class TestPatentDataEdgeCases:
    """Tests for error handling and edge cases in the PatentDataClient class."""

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_patent_application_details_app_not_in_bag(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test get_patent_application_details when requested app_num is not the one in the returned bag."""
        app_num_requested = "12345678"
        app_num_in_bag = "87654321"

        mock_wrapper_data = {
            "applicationNumberText": app_num_in_bag,
            "applicationMetaData": {"inventionTitle": "Other Invention"},
        }
        mock_pfw_instance = PatentFileWrapper.from_dict(mock_wrapper_data)
        mock_response_obj = PatentDataResponse(
            count=1, patent_file_wrapper_data_bag=[mock_pfw_instance]
        )
        mock_make_request.return_value = mock_response_obj

        client = PatentDataClient(api_key="test_key")
        result = client.get_patent_application_details(
            application_number=app_num_requested
        )

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint=client.ENDPOINTS["application_by_number"].format(
                application_number=app_num_requested
            ),
            response_class=PatentDataResponse,
        )
        # Based on current client logic (client_patent_data_py_v2):
        # it logs a warning and returns the first wrapper if present,
        # even if application_number_text doesn't match the requested number.
        assert isinstance(result, PatentFileWrapper)
        assert result.application_number_text == app_num_in_bag

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_patent_application_details_empty_bag_returns_none(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test get_patent_application_details returns None if patentFileWrapperDataBag is empty."""
        app_num_to_request = "12345678"
        mock_response_obj = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        client = PatentDataClient(api_key="test_key")
        result = client.get_patent_application_details(
            application_number=app_num_to_request
        )
        assert result is None

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_patent_application_details_unexpected_response_type_from_make_request(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test get_patent_application_details if _make_request returns an unexpected type."""
        mock_make_request.return_value = ["unexpected", "response", "type"]

        client = PatentDataClient(api_key="test_key")

        # The client has: assert isinstance(response_data, PatentDataResponse), f"..."
        # This will raise an AssertionError.
        with pytest.raises(AssertionError) as excinfo:
            client.get_patent_application_details(application_number="12345678")

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_document_file_non_requests_response_object(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test download_document_file with a non-requests.Response object from _make_request."""
        mock_make_request.return_value = {"not": "a requests.Response object"}

        client = PatentDataClient(api_key="test_key")

        with pytest.raises(
            TypeError,
            match="Expected a requests.Response object for streaming download, got <class 'dict'>",
        ):
            client.download_document_file(
                application_number="12345678",
                document_id="DOC123.pdf",
                destination_dir="/tmp",
            )

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_patent_applications_get_invalid_params_raises_api_error(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test download_patent_applications_get raises specific API error for invalid params."""
        mock_make_request.side_effect = USPTOApiBadRequestError(
            "Invalid API parameters from mock"
        )

        client = PatentDataClient(api_key="test_key")
        with pytest.raises(
            USPTOApiBadRequestError, match="Invalid API parameters from mock"
        ):
            client.download_patent_applications_get(params={"invalid_param": "value"})

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/patent/applications/search/download",
            params={"invalid_param": "value", "format": "json"},
            response_class=PatentDataResponse,
        )

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_search_patent_applications_post_assertion(self, mock_make_request):
        """Test assertion in search_patent_applications_post when response is not a PatentDataResponse."""
        # Set up the mock to return something that's not a PatentDataResponse object
        mock_make_request.return_value = {"not": "a_patent_data_response"}

        client = PatentDataClient(api_key="test_key")

        # Call the method with a simple search request to trigger the assertion
        with pytest.raises(AssertionError):
            client.search_patent_applications_post(search_request={"q": "test"})

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_search_patent_applications_post_success(self, mock_make_request):
        """Test successful execution path of search_patent_applications_post."""
        # Create a mock PatentDataResponse object
        mock_response = MagicMock(spec=PatentDataResponse)
        mock_make_request.return_value = mock_response

        client = PatentDataClient(api_key="test_key")

        # Call the method with a simple search request
        result = client.search_patent_applications_post(search_request={"q": "test"})

        # Verify we got the expected result
        assert result is mock_response
        mock_make_request.assert_called_once_with(
            method="POST",
            endpoint=client.ENDPOINTS["applications_search"],
            json_data={"q": "test"},
            response_class=PatentDataResponse,
        )


class TestResponseTypeHandling:
    """Tests for handling different response types and type assertions, focusing on specific getters."""

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_adjustment_returns_none_on_empty_wrapper(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test get_application_adjustment returns None if wrapper is empty or not found."""
        mock_response_empty_bag = PatentDataResponse(
            count=0, patent_file_wrapper_data_bag=[]
        )
        mock_make_request.return_value = mock_response_empty_bag

        client = PatentDataClient(api_key="test_key")
        result = client.get_application_adjustment(application_number="12345678")
        assert result is None

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_attorney_returns_specific_type(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test get_application_attorney returns RecordAttorney correctly."""
        app_num = "12345678"
        mock_attorney_data = RecordAttorney()
        mock_wrapper = PatentFileWrapper(
            application_number_text=app_num, record_attorney=mock_attorney_data
        )
        mock_response_from_api = PatentDataResponse(
            count=1, patent_file_wrapper_data_bag=[mock_wrapper]
        )
        mock_make_request.return_value = mock_response_from_api

        client = PatentDataClient(api_key="test_key")
        result = client.get_application_attorney(application_number=app_num)

        assert isinstance(result, RecordAttorney)
        assert result is mock_attorney_data

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_attorney_returns_none_if_no_data(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test get_application_attorney returns None if no attorney data in wrapper."""
        app_num = "12345678"
        mock_wrapper_no_attorney = PatentFileWrapper(
            application_number_text=app_num, record_attorney=None
        )
        mock_response_from_api = PatentDataResponse(
            count=1, patent_file_wrapper_data_bag=[mock_wrapper_no_attorney]
        )
        mock_make_request.return_value = mock_response_from_api

        client = PatentDataClient(api_key="test_key")
        result = client.get_application_attorney(application_number=app_num)
        assert result is None


class TestPatentDataClientGetWrapper:
    """Tests for the _get_wrapper_from_response method of PatentDataClient."""

    def test_get_wrapper_non_patentfilewrapper_dict(self):
        """Test _get_wrapper_from_response when the wrapper is a dict instead of PatentFileWrapper."""
        client = PatentDataClient(api_key="test_key")

        # Create a dict for the wrapper bag
        mock_dict = {"applicationNumberText": "12345678"}

        # Create mock response with the dict in the bag
        mock_response = MagicMock(spec=PatentDataResponse)
        mock_response.patent_file_wrapper_data_bag = [mock_dict]

        # Create a mock wrapper to return from the patched method
        mock_wrapper = MagicMock(spec=PatentFileWrapper)
        mock_wrapper.application_number_text = "12345678"

        # Use the correct import path based on your actual code structure
        with patch(
            "pyUSPTO.models.patent_data.PatentFileWrapper.from_dict",
            return_value=mock_wrapper,
        ):
            result = client._get_wrapper_from_response(mock_response)

        assert result is mock_wrapper

    def test_get_wrapper_non_patentfilewrapper_other(self):
        """Test _get_wrapper_from_response when the wrapper is neither PatentFileWrapper nor dict."""
        client = PatentDataClient(api_key="test_key")

        # Create a mock response with a non-dict, non-PatentFileWrapper in the bag
        mock_response = PatentDataResponse(count=1, patent_file_wrapper_data_bag=["not_a_wrapper"])  # type: ignore

        result = client._get_wrapper_from_response(mock_response, "12345678")

        # Verify the result is None
        assert result is None
