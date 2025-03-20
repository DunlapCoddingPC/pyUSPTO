"""
Tests for the patent_data client module initialization and basic operations.

This module contains tests for the PatentDataClient class core functionality.
"""

import os
from unittest.mock import MagicMock, patch

import pytest
import requests

from pyUSPTO.clients.patent_data import PatentDataClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.patent_data import PatentDataResponse, PatentFileWrapper


class TestPatentDataClient:
    """Tests for the PatentDataClient class initialization and basic operations."""

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

        # Test with config
        config = USPTOConfig(
            api_key="config_key",
            patent_data_base_url="https://config.api.test.com",
        )
        client = PatentDataClient(config=config)
        assert client.api_key == "config_key"
        assert client.base_url == "https://config.api.test.com"
        assert client.config is config

        # Test with both API key and config (API key should take precedence)
        client = PatentDataClient(api_key="direct_key", config=config)
        assert client.api_key == "direct_key"
        assert client.base_url == "https://config.api.test.com"

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
