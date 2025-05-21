"""
Tests for the status code methods of the patent_data client module.

This module contains tests for the status code-related functionality
of the PatentDataClient class.
"""

from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

from pyUSPTO.clients.patent_data import PatentDataClient
from pyUSPTO.models.patent_data import (
    StatusCode,
    StatusCodeCollection,
    StatusCodeSearchResponse,
)


class TestPatentStatusCodes:
    """Tests for patent status code methods."""

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_patent_status_codes(self, mock_make_request: MagicMock) -> None:
        """Test get_patent_status_codes method."""
        mock_response = {
            "count": 2,
            "statusCodeBag": [
                {
                    "applicationStatusCode": 100,
                    "applicationStatusDescriptionText": "Status 100 Description",
                },
                {
                    "applicationStatusCode": 200,
                    "applicationStatusDescriptionText": "Status 200 Description",
                },
            ],
            "requestIdentifier": "test-req-id",
        }
        mock_make_request.return_value = mock_response

        client = PatentDataClient(api_key="test_key")
        result = client.get_patent_status_codes()

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/patent/status-codes",
            params=None,
        )
        assert isinstance(result, StatusCodeSearchResponse)
        assert result.count == 2
        assert result.request_identifier == "test-req-id"
        assert isinstance(result.status_code_bag, StatusCodeCollection)
        assert len(result.status_code_bag) == 2
        codes = list(result.status_code_bag)
        assert codes[0].code == 100
        assert codes[0].description == "Status 100 Description"

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_search_patent_status_codes_post(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test search_patent_status_codes_post method."""
        mock_response = {
            "count": 2,
            "statusCodeBag": [
                {
                    "applicationStatusCode": 150,
                    "applicationStatusDescriptionText": "Status 150 Description",
                },
                {
                    "applicationStatusCode": 250,
                    "applicationStatusDescriptionText": "Status 250 Description",
                },
            ],
            "requestIdentifier": "test-req-id-post",
        }
        mock_make_request.return_value = mock_response

        client = PatentDataClient(api_key="test_key")
        search_request = {"q": "Description", "limit": 10}
        result = client.search_patent_status_codes_post(search_request=search_request)

        mock_make_request.assert_called_once_with(
            method="POST",
            endpoint="api/v1/patent/status-codes",
            json_data=search_request,
        )
        assert isinstance(result, StatusCodeSearchResponse)
        assert result.count == 2
        assert result.request_identifier == "test-req-id-post"
        assert isinstance(result.status_code_bag, StatusCodeCollection)
        assert len(result.status_code_bag) == 2
        codes = list(result.status_code_bag)
        assert codes[0].code == 150


class TestStatusCodeModel:
    """Tests for the StatusCode and StatusCodeCollection models."""

    def test_status_code_initialization(self) -> None:
        status = StatusCode(code=100, description="Active Application")
        assert status.code == 100
        assert status.description == "Active Application"
        assert str(status) == "100: Active Application"

    def test_status_code_from_dict(self) -> None:
        data = {
            "applicationStatusCode": 150,
            "applicationStatusDescriptionText": "Pending Application",
        }
        status = StatusCode.from_dict(data)
        assert status.code == 150
        assert status.description == "Pending Application"

    def test_status_code_collection_initialization(self) -> None:
        status_codes = [
            StatusCode(code=100, description="Active Application"),
            StatusCode(code=150, description="Pending Application"),
            StatusCode(code=200, description="Approved Application"),
        ]
        collection = StatusCodeCollection(status_codes=status_codes)
        assert len(collection) == 3
        assert list(collection) == status_codes
        assert str(collection) == "StatusCodeCollection with 3 status codes"
        # Updated based on likely __repr__ from model patent_data_py_v3
        # The error "StatusCodeCollection(3 status codes: 100, 150, 200)"
        assert repr(collection) == "StatusCodeCollection(3 status codes: 100, 150, 200)"

    def test_status_code_collection_empty(self) -> None:
        collection = StatusCodeCollection(status_codes=[])
        assert len(collection) == 0
        assert list(collection) == []
        # Updated based on likely __repr__ from model patent_data_py_v3
        assert repr(collection) == "StatusCodeCollection(empty)"

    def test_status_code_collection_with_dict_input_for_search_response(self) -> None:
        data = {
            "count": 2,
            "statusCodeBag": [
                {
                    "applicationStatusCode": 100,
                    "applicationStatusDescriptionText": "Status 100",
                },
                {
                    "applicationStatusCode": 200,
                    "applicationStatusDescriptionText": "Status 200",
                },
            ],
            "requestIdentifier": "some-id",
        }
        response_obj = StatusCodeSearchResponse.from_dict(data)
        assert isinstance(response_obj, StatusCodeSearchResponse)
        assert response_obj.count == 2
        assert isinstance(response_obj.status_code_bag, StatusCodeCollection)
        assert len(response_obj.status_code_bag) == 2

    def test_find_by_code(self) -> None:
        status_codes = [
            StatusCode(code=100, description="Active"),
            StatusCode(code=150, description="Pending"),
        ]
        collection = StatusCodeCollection(status_codes=status_codes)
        assert collection.find_by_code(150).description == "Pending"  # type: ignore
        assert collection.find_by_code(999) is None

    def test_search_by_description(self) -> None:
        status_codes = [
            StatusCode(code=100, description="Active"),
            StatusCode(code=150, description="Pending"),
        ]
        collection = StatusCodeCollection(status_codes=status_codes)
        assert len(collection.search_by_description("Pend")) == 1
