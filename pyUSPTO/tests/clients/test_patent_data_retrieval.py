"""
Tests for the patent_data retrieval methods.

This module contains tests for the retrieval methods of the PatentDataClient class.
"""

import os
from unittest.mock import MagicMock, patch

import pytest
import requests

from pyUSPTO.clients.patent_data import PatentDataClient
from pyUSPTO.models.patent_data import PatentDataResponse, PatentFileWrapper


class TestPatentDataRetrieval:
    """Tests for the retrieval methods of the PatentDataClient class."""

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
    def test_get_patent_applications(self, mock_make_request: MagicMock) -> None:
        """Test get_patent_applications method."""
        # Setup mock response object
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
        mock_make_request.return_value = mock_response_obj

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        params = {
            "q": "Test",
            "limit": "25",
            "offset": "0",
        }
        result = client.get_patent_applications(params=params)

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/search",
            params=params,
            response_class=PatentDataResponse,
        )

        # Verify result
        assert isinstance(result, PatentDataResponse)
        assert result.count == 2
        assert len(result.patent_file_wrapper_data_bag) == 2
        assert (
            result.patent_file_wrapper_data_bag[0].application_number_text == "12345678"
        )

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_search_patents(self, mock_make_request: MagicMock) -> None:
        """Test search_patents method."""
        # Setup mock response object
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

        # Verify result
        assert isinstance(result, PatentDataResponse)
        assert result.count == 2
        assert len(result.patent_file_wrapper_data_bag) == 2

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_search_patents_with_multiple_filters(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test search_patents method with multiple filters."""
        # Setup mock response object
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

        # Verify result
        assert isinstance(result, PatentDataResponse)
        assert result.count == 1
        assert len(result.patent_file_wrapper_data_bag) == 1

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_metadata(self, mock_make_request: MagicMock) -> None:
        """Test get_application_metadata method."""
        # Setup mock with a response object
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
    def test_get_patent_by_application_number_with_patentFileWrapperDataBag(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test get_patent_by_application_number with patentFileWrapperDataBag in response."""
        # Setup mock to return a response with patentFileWrapperDataBag - this will hit line 199
        mock_response = {
            "patentFileWrapperDataBag": [
                {
                    "applicationNumberText": "12345678",
                    "applicationMetaData": {"inventionTitle": "Test Invention"},
                }
            ]
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
    def test_get_patent_by_application_number_with_PatentFileWrapper_response(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test get_patent_by_application_number with PatentFileWrapper response."""
        # Setup mock to return a PatentFileWrapper object directly - this will hit line 207
        mock_response = PatentFileWrapper(
            application_number_text="12345678",
            application_meta_data=MagicMock(invention_title="Test Invention"),
        )
        mock_make_request.return_value = mock_response

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        result = client.get_patent_by_application_number(application_number="12345678")

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/12345678",
        )

        # Verify result is the same object
        assert result is mock_response
        assert isinstance(result, PatentFileWrapper)
        assert result.application_number_text == "12345678"

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_application_document_non_response_object(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test download_application_document with a non-Response object."""

        # Create a non-Response object that will trigger the TypeError in line 457
        class NotAResponse:
            """A class that is not a Response object"""

            def __init__(self):
                self.headers = {"Content-Type": "application/json"}

        # Return an object that is definitely not a requests.Response
        mock_make_request.return_value = NotAResponse()

        # Create client
        client = PatentDataClient(api_key="test_key")

        # Call should raise TypeError at line 457
        with pytest.raises(
            TypeError, match="Expected a Response object for streaming download"
        ):
            client.download_application_document(
                application_number="12345678", document_id="DOC123", destination="/tmp"
            )
