"""
Tests for the status code methods of the patent_data client module.

This module contains tests for the status code-related functionality
of the PatentDataClient class.
"""

from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

from pyUSPTO.clients.patent_data import PatentDataClient
from pyUSPTO.models.patent_data import StatusCode, StatusCodeCollection


class TestPatentStatusCodes:
    """Tests for patent status code methods."""

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_patent_status_codes(self, mock_make_request: MagicMock) -> None:
        """Test get_patent_status_codes method."""
        # Setup mock
        mock_response = {
            "statusCodes": [
                {"code": 100, "description": "Status 100 Description"},
                {"code": 200, "description": "Status 200 Description"},
            ]
        }
        mock_make_request.return_value = mock_response

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        result = client.get_patent_status_codes()

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="status-codes",
            params=None,
        )

        # Verify result is a StatusCodeCollection
        assert isinstance(result, StatusCodeCollection)
        assert len(result) == 2

        # Check individual status codes
        codes = list(result)
        assert codes[0].code == 100
        assert codes[0].description == "Status 100 Description"
        assert codes[1].code == 200
        assert codes[1].description == "Status 200 Description"

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_search_patent_status_codes_post(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test search_patent_status_codes_post method."""
        # Setup mock
        mock_response = {
            "statusCodes": [
                {"code": 150, "description": "Status 150 Description"},
                {"code": 250, "description": "Status 250 Description"},
            ]
        }
        mock_make_request.return_value = mock_response

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        search_request = {"q": "Description", "limit": 10}
        result = client.search_patent_status_codes_post(search_request=search_request)

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="POST",
            endpoint="status-codes",
            json_data=search_request,
        )

        # Verify result
        assert isinstance(result, StatusCodeCollection)
        assert len(result) == 2


class TestStatusCodeModel:
    """Tests for the StatusCode and StatusCodeCollection models."""

    def test_status_code_initialization(self) -> None:
        """Test StatusCode initialization and string representation."""
        status = StatusCode(code=100, description="Active Application")

        assert status.code == 100
        assert status.description == "Active Application"
        assert str(status) == "100: Active Application"

    def test_status_code_from_dict(self) -> None:
        """Test StatusCode.from_dict method."""
        data = {"code": 150, "description": "Pending Application"}
        status = StatusCode.from_dict(data)

        assert status.code == 150
        assert status.description == "Pending Application"

    def test_status_code_collection_initialization(self) -> None:
        """Test StatusCodeCollection initialization and properties."""
        status_codes = [
            StatusCode(code=100, description="Active Application"),
            StatusCode(code=150, description="Pending Application"),
            StatusCode(code=200, description="Approved Application"),
        ]
        collection = StatusCodeCollection(status_codes=status_codes)

        assert len(collection) == 3
        assert list(collection) == status_codes
        assert str(collection) == "StatusCodeCollection with 3 status codes"
        assert repr(collection) == "StatusCodeCollection(3 status codes: 100, 150, 200)"

    def test_status_code_collection_empty(self) -> None:
        """Test empty StatusCodeCollection."""
        collection = StatusCodeCollection(status_codes=[])

        assert len(collection) == 0
        assert list(collection) == []
        assert repr(collection) == "StatusCodeCollection(empty)"

    def test_status_code_collection_from_dict(self) -> None:
        """Test StatusCodeCollection.from_dict method."""
        # Test with camelCase format: "statusCodes"
        data = {
            "statusCodes": [
                {"code": 100, "description": "Status 100"},
                {"code": 200, "description": "Status 200"},
            ]
        }
        collection = StatusCodeCollection.from_dict(data)

        assert len(collection) == 2
        codes = list(collection)
        assert codes[0].code == 100
        assert codes[1].description == "Status 200"

        # Test with kebab-case format: "status-codes"
        data = {
            "status-codes": [
                {"code": 150, "description": "Status 150"},
                {"code": 250, "description": "Status 250"},
            ]
        }
        collection = StatusCodeCollection.from_dict(data)

        assert len(collection) == 2
        codes = list(collection)
        assert codes[0].code == 150
        assert codes[1].description == "Status 250"

    def test_status_code_collection_from_list(self) -> None:
        """Test StatusCodeCollection.from_dict with list input."""
        data: List[Dict[str, Any]] = [
            {"code": 100, "description": "Status 100"},
            {"code": 200, "description": "Status 200"},
        ]
        collection = StatusCodeCollection.from_dict(data)

        assert len(collection) == 2
        codes = list(collection)
        assert codes[0].code == 100
        assert codes[1].description == "Status 200"

    def test_find_by_code(self) -> None:
        """Test find_by_code method."""
        status_codes = [
            StatusCode(code=100, description="Active Application"),
            StatusCode(code=150, description="Pending Application"),
            StatusCode(code=200, description="Approved Application"),
        ]
        collection = StatusCodeCollection(status_codes=status_codes)

        # Find existing code
        result = collection.find_by_code(150)
        assert result is not None
        assert result.code == 150
        assert result.description == "Pending Application"

        # Try to find non-existing code
        result = collection.find_by_code(999)
        assert result is None

    def test_search_by_description(self) -> None:
        """Test search_by_description method."""
        status_codes = [
            StatusCode(code=100, description="Active Application"),
            StatusCode(code=150, description="Pending Application"),
            StatusCode(code=200, description="Approved Application"),
        ]
        collection = StatusCodeCollection(status_codes=status_codes)

        # Search for existing text in description
        results = collection.search_by_description("pending")
        assert len(results) == 1
        assert list(results)[0].code == 150

        # Search for text matching multiple descriptions
        results = collection.search_by_description("Application")
        assert len(results) == 3

        # Search for non-matching text
        results = collection.search_by_description("NonExistent")
        assert len(results) == 0
