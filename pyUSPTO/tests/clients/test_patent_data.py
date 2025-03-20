"""
Tests for the patent_data client module.

This module contains tests for the PatentDataClient class.
"""

import os
from unittest.mock import MagicMock, patch

import pytest
import requests

from pyUSPTO.clients.patent_data import PatentDataClient
from pyUSPTO.models.patent_data import PatentDataResponse, PatentFileWrapper


class TestPatentDataClient:
    """Tests for the PatentDataClient class."""

    def test_init(self) -> None:
        """Test initialization of the PatentDataClient."""
        # Test with API key
        client = PatentDataClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.base_url == "https://api.uspto.gov/api/v1/patent"

        # Test with custom base URL
        client = PatentDataClient(
            api_key="test_key", base_url="https://custom.api.test.com"
        )
        assert client.api_key == "test_key"
        assert client.base_url == "https://custom.api.test.com"

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_patent_by_application_number(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test get_patent_by_application_number method."""
        # Setup mock
        mock_response = {
            "applicationNumberText": "12345678",
            "applicationMetaData": {"inventionTitle": "Test Invention"},
        }
        mock_make_request.return_value = mock_response

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        result = client.get_patent_by_application_number(application_number="12345678")

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/12345678",
        )

        # Verify result was parsed correctly
        assert isinstance(result, PatentFileWrapper)
        assert result.application_number_text == "12345678"
        assert result.application_meta_data is not None
        assert result.application_meta_data.invention_title == "Test Invention"

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_search_patents(self, mock_make_request: MagicMock) -> None:
        """Test search_patents method."""
        # Setup mock
        mock_response = {
            "patentFileWrapperDataBag": [
                {
                    "applicationNumberText": "12345678",
                    "applicationMetaData": {"patentNumber": "10000000"},
                },
                {
                    "applicationNumberText": "87654321",
                    "applicationMetaData": {"patentNumber": "20000000"},
                },
            ],
            "count": 2,
        }
        mock_make_request.return_value = mock_response

        # Mock the return value as a PatentDataResponse
        mock_response_obj = PatentDataResponse(
            count=2,
            patent_file_wrapper_data_bag=[
                PatentFileWrapper(
                    application_number_text="12345678",
                    application_meta_data=MagicMock(patent_number="10000000"),
                ),
                PatentFileWrapper(
                    application_number_text="87654321",
                    application_meta_data=MagicMock(patent_number="20000000"),
                ),
            ],
        )
        mock_response_obj.count = 2
        mock_response_obj.patent_file_wrapper_data_bag = [
            PatentFileWrapper(
                application_number_text="12345678",
                application_meta_data=MagicMock(patent_number="10000000"),
            ),
            PatentFileWrapper(
                application_number_text="87654321",
                application_meta_data=MagicMock(patent_number="20000000"),
            ),
        ]
        mock_make_request.return_value = mock_response_obj

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        result = client.search_patents(patent_number="10000000", limit=25, offset=0)

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/search",
            params={
                "q": "applicationMetaData.patentNumber:10000000",
                "limit": "25",
                "offset": "0",
            },
            response_class=PatentDataResponse,
        )

        # No need to assert isinstance since we're mocking the response directly
        assert result.count == 2
        assert len(result.patent_file_wrapper_data_bag) == 2
        assert (
            result.patent_file_wrapper_data_bag[0].application_number_text == "12345678"
        )
        # Verify application_meta_data is not None before checking patent_number
        assert result.patent_file_wrapper_data_bag[0].application_meta_data is not None
        assert (
            result.patent_file_wrapper_data_bag[0].application_meta_data.patent_number
            == "10000000"
        )

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_search_patents_with_multiple_filters(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test search_patents method with multiple filters."""
        # Setup mock
        mock_response = {
            "patentFileWrapperDataBag": [
                {
                    "applicationNumberText": "12345678",
                    "applicationMetaData": {"inventionTitle": "Test Invention"},
                }
            ],
            "count": 1,
        }
        mock_make_request.return_value = mock_response

        # Mock the return value as a PatentDataResponse
        mock_response_obj = PatentDataResponse(
            count=1,
            patent_file_wrapper_data_bag=[
                PatentFileWrapper(
                    application_number_text="12345678",
                    application_meta_data=MagicMock(invention_title="Test Invention"),
                ),
            ],
        )
        mock_response_obj.count = 1
        mock_response_obj.patent_file_wrapper_data_bag = [
            PatentFileWrapper(
                application_number_text="12345678",
                application_meta_data=MagicMock(invention_title="Test Invention"),
            )
        ]
        mock_make_request.return_value = mock_response_obj

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        result = client.search_patents(
            query="Test Invention",
            inventor_name="John Smith",
            filing_date_from="2020-01-01",
            filing_date_to="2022-01-01",
            limit=20,
            offset=10,
        )

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/search",
            params={
                "q": "applicationMetaData.inventorBag.inventorNameText:John Smith AND Test Invention AND applicationMetaData.filingDate:[2020-01-01 TO 2022-01-01]",
                "limit": "20",
                "offset": "10",
            },
            response_class=PatentDataResponse,
        )

        # No need to assert isinstance since we're mocking the response directly
        assert result.count == 1
        assert len(result.patent_file_wrapper_data_bag) == 1
        assert (
            result.patent_file_wrapper_data_bag[0].application_number_text == "12345678"
        )
        # Verify application_meta_data is not None before checking invention_title
        assert result.patent_file_wrapper_data_bag[0].application_meta_data is not None
        assert (
            result.patent_file_wrapper_data_bag[0].application_meta_data.invention_title
            == "Test Invention"
        )

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_search_patent_applications_post(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test search_patent_applications_post method."""
        # Setup mock with a properly typed response object
        mock_response_obj = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        result = client.search_patent_applications_post(
            search_request={
                "q": "Test",
                "filters": [
                    {"field": "inventionSubjectMatterCategory", "value": "MECHANICAL"}
                ],
                "fields": ["patentNumber", "inventionTitle"],
                "pagination": {"offset": 0, "limit": 100},
                "sort": [{"field": "filingDate", "order": "desc"}],
            }
        )

        # Verify result is a PatentDataResponse
        assert isinstance(result, PatentDataResponse)

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="POST",
            endpoint="applications/search",
            json_data={
                "q": "Test",
                "filters": [
                    {"field": "inventionSubjectMatterCategory", "value": "MECHANICAL"}
                ],
                "fields": ["patentNumber", "inventionTitle"],
                "pagination": {"offset": 0, "limit": 100},
                "sort": [{"field": "filingDate", "order": "desc"}],
            },
            response_class=PatentDataResponse,
        )

    @patch("pyUSPTO.clients.patent_data.PatentDataClient.paginate_results")
    def test_paginate_patents(self, mock_paginate: MagicMock) -> None:
        """Test paginate_patents method."""
        # Setup mock
        patent1 = PatentFileWrapper(application_number_text="12345678")
        patent2 = PatentFileWrapper(application_number_text="87654321")
        mock_paginate.return_value = iter([patent1, patent2])

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        results = list(client.paginate_patents(query="Test", limit=20))

        # Verify paginate_results was called correctly
        mock_paginate.assert_called_once_with(
            method_name="get_patent_applications",
            response_container_attr="patent_file_wrapper_data_bag",
            query="Test",
            limit=20,
        )

        # Verify results were processed correctly
        assert len(results) == 2
        assert results[0].application_number_text == "12345678"
        assert results[1].application_number_text == "87654321"

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_metadata(self, mock_make_request: MagicMock) -> None:
        """Test get_application_metadata method."""
        # Setup mock with a MagicMock that can handle any attribute
        mock_response_obj = MagicMock(spec=PatentDataResponse)
        mock_response_obj.count = 0
        mock_response_obj.patent_file_wrapper_data_bag = []
        # The mock can now handle any attribute access
        mock_make_request.return_value = mock_response_obj

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        result = client.get_application_metadata(application_number="12345678")

        # Since we're mocking, just verify that the result is the mock we returned
        assert result is mock_response_obj

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/12345678/meta-data",
            response_class=PatentDataResponse,
        )

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_application_document(self, mock_make_request: MagicMock) -> None:
        """Test download_application_document method."""
        # Setup mock for the response
        mock_response = MagicMock(spec=requests.Response)
        mock_response.headers = {"Content-Disposition": 'filename="test_document.pdf"'}
        mock_response.iter_content.return_value = [b"test content"]
        mock_make_request.return_value = mock_response

        # Mock open function
        mock_open = MagicMock()
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        with patch("builtins.open", mock_open), patch(
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

    # New Test Cases for download_patent_applications

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
            endpoint=client.ENDPOINTS["applications_search_download"],
            params={"invalid_param": "value", "format": "json"},
            response_class=PatentDataResponse,
        )

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
            endpoint=client.ENDPOINTS["applications_search_download"],
            params={"q": "test", "format": "csv"},
            response_class=PatentDataResponse,
        )

        # Verify the result type
        assert isinstance(result, PatentDataResponse)

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_patent_applications_correct_assignment_endpoint(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test download_patent_applications with correct assignment endpoint."""
        # Setup mock response
        mock_response_obj = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        # Create client and call method with format passed as a separate argument
        client = PatentDataClient(api_key="test_key")
        result = client.download_patent_applications(params={"q": "test"}, format="csv")

        # Verify request was made correctly with format added to params
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint=client.ENDPOINTS["applications_search_download"],
            params={"q": "test", "format": "csv"},
            response_class=PatentDataResponse,
        )

        # Verify the result type
        assert isinstance(result, PatentDataResponse)
