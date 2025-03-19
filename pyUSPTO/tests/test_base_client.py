"""
Tests for the base client module.

This module contains tests for the BaseUSPTOClient class and related functionality.
"""

from typing import Any, Dict, Type
from unittest.mock import MagicMock, patch

import pytest
import requests

from pyUSPTO.base import (
    BaseUSPTOClient,
    FromDictProtocol,
    USPTOApiAuthError,
    USPTOApiError,
    USPTOApiNotFoundError,
    USPTOApiRateLimitError,
)


class TestResponseClass:
    """Test class implementing FromDictProtocol for testing."""

    data: Dict[str, Any]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TestResponseClass":
        """Create a TestResponseClass object from a dictionary."""
        instance = cls()
        instance.data = data
        return instance


class TestBaseUSPTOClient:
    """Tests for the BaseUSPTOClient class."""

    def test_init(self) -> None:
        """Test initialization of the BaseUSPTOClient."""
        # Test with API key
        client = BaseUSPTOClient(api_key="test_key", base_url="https://api.test.com")
        assert client.api_key == "test_key"
        assert client.base_url == "https://api.test.com"
        assert "X-API-KEY" in client.session.headers
        assert client.session.headers["X-API-KEY"] == "test_key"

        # Test without API key
        client = BaseUSPTOClient(base_url="https://api.test.com")
        assert client.api_key is None
        assert client.base_url == "https://api.test.com"
        assert "X-API-KEY" not in client.session.headers

        # Test with trailing slash in base_url
        client = BaseUSPTOClient(base_url="https://api.test.com/")
        assert client.base_url == "https://api.test.com"

    def test_retry_configuration(self) -> None:
        """Test that retry configuration is properly set up."""
        # Create a client
        client = BaseUSPTOClient(base_url="https://api.test.com")

        # Check that the session has adapters for both http and https
        assert "http://" in client.session.adapters
        assert "https://" in client.session.adapters

        # Get the retry configuration from the adapters
        http_adapter = client.session.adapters["http://"]
        https_adapter = client.session.adapters["https://"]

        # Verify both adapters have retry configuration
        assert http_adapter.max_retries is not None  # type: ignore
        assert https_adapter.max_retries is not None  # type: ignore

        # Verify retry settings
        # Note: We can't directly check the status_forcelist because it's not exposed
        # in a consistent way across different versions of urllib3/requests
        assert http_adapter.max_retries.total == 3  # type: ignore
        assert http_adapter.max_retries.backoff_factor == 1  # type: ignore

    def test_make_request_get(self, mock_session: MagicMock) -> None:
        """Test _make_request method with GET."""
        # Setup
        client = BaseUSPTOClient(base_url="https://api.test.com")
        client.session = mock_session

        mock_response = MagicMock()
        mock_response.json.return_value = {"key": "value"}
        mock_session.get.return_value = mock_response

        # Test GET request
        result = client._make_request(
            method="GET", endpoint="test", params={"param": "value"}
        )

        # Verify
        mock_session.get.assert_called_once_with(
            url="https://api.test.com/test", params={"param": "value"}, stream=False
        )
        assert result == {"key": "value"}

    def test_make_request_post(self, mock_session: MagicMock) -> None:
        """Test _make_request method with POST."""
        # Setup
        client = BaseUSPTOClient(base_url="https://api.test.com")
        client.session = mock_session

        mock_response = MagicMock()
        mock_response.json.return_value = {"key": "value"}
        mock_session.post.return_value = mock_response

        # Test POST request
        result = client._make_request(
            method="POST",
            endpoint="test",
            params={"param": "value"},
            json_data={"data": "value"},
        )

        # Verify
        mock_session.post.assert_called_once_with(
            url="https://api.test.com/test",
            params={"param": "value"},
            json={"data": "value"},
            stream=False,
        )
        assert result == {"key": "value"}

    def test_make_request_with_response_class(self, mock_session: MagicMock) -> None:
        """Test _make_request method with response_class."""
        # Setup
        client = BaseUSPTOClient(base_url="https://api.test.com")
        client.session = mock_session

        mock_response = MagicMock()
        mock_response.json.return_value = {"key": "value"}
        mock_session.get.return_value = mock_response

        # Test with response_class
        result = client._make_request(
            method="GET",
            endpoint="test",
            response_class=TestResponseClass,
        )

        # Verify
        assert isinstance(result, TestResponseClass)
        assert result.data == {"key": "value"}

    def test_make_request_with_custom_base_url(self, mock_session: MagicMock) -> None:
        """Test _make_request method with custom_base_url."""
        # Setup
        client = BaseUSPTOClient(base_url="https://api.test.com")
        client.session = mock_session

        mock_response = MagicMock()
        mock_response.json.return_value = {"key": "value"}
        mock_session.get.return_value = mock_response

        # Test with custom_base_url
        result = client._make_request(
            method="GET",
            endpoint="test",
            custom_base_url="https://custom.api.test.com",
        )

        # Verify
        mock_session.get.assert_called_once_with(
            url="https://custom.api.test.com/test", params=None, stream=False
        )
        assert result == {"key": "value"}

    def test_make_request_with_stream(self, mock_session: MagicMock) -> None:
        """Test _make_request method with stream=True."""
        # Setup
        client = BaseUSPTOClient(base_url="https://api.test.com")
        client.session = mock_session

        mock_response = MagicMock()
        mock_session.get.return_value = mock_response

        # Test with stream=True
        result = client._make_request(method="GET", endpoint="test", stream=True)

        # Verify
        mock_session.get.assert_called_once_with(
            url="https://api.test.com/test", params=None, stream=True
        )
        assert result == mock_response
        mock_response.json.assert_not_called()

    def test_make_request_invalid_method(self) -> None:
        """Test _make_request method with invalid HTTP method."""
        client = BaseUSPTOClient(base_url="https://api.test.com")

        # Test with invalid method
        with pytest.raises(ValueError, match="Unsupported HTTP method: DELETE"):
            client._make_request(method="DELETE", endpoint="test")

    def test_make_request_http_errors(self, mock_session: MagicMock) -> None:
        """Test _make_request method with HTTP errors."""
        # Setup
        client = BaseUSPTOClient(base_url="https://api.test.com")
        client.session = mock_session

        # Test 401 error
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_session.get.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )

        with pytest.raises(USPTOApiAuthError, match="Authentication failed"):
            client._make_request(method="GET", endpoint="test")

        # Test 403 error
        mock_response.status_code = 403
        with pytest.raises(USPTOApiAuthError, match="Access forbidden"):
            client._make_request(method="GET", endpoint="test")

        # Test 404 error
        mock_response.status_code = 404
        with pytest.raises(USPTOApiNotFoundError, match="Resource not found"):
            client._make_request(method="GET", endpoint="test")

        # Test 429 error
        mock_response.status_code = 429
        with pytest.raises(USPTOApiRateLimitError, match="Rate limit exceeded"):
            client._make_request(method="GET", endpoint="test")

        # Test other HTTP error with JSON response
        mock_response.status_code = 500
        mock_response.json.return_value = {"errorDetails": "Internal server error"}
        with pytest.raises(USPTOApiError, match="API Error 500: Internal server error"):
            client._make_request(method="GET", endpoint="test")

        # Test other HTTP error without JSON response
        mock_response.json.side_effect = ValueError("Invalid JSON")
        with pytest.raises(USPTOApiError, match="API Error 500"):
            client._make_request(method="GET", endpoint="test")

    def test_make_request_request_exception(self, mock_session: MagicMock) -> None:
        """Test _make_request method with request exception."""
        # Setup
        client = BaseUSPTOClient(base_url="https://api.test.com")
        client.session = mock_session

        # Test request exception
        mock_session.get.side_effect = requests.exceptions.ConnectionError(
            "Connection refused"
        )
        with pytest.raises(USPTOApiError, match="Request failed: Connection refused"):
            client._make_request(method="GET", endpoint="test")

    def test_paginate_results(self, mock_session: MagicMock) -> None:
        """Test paginate_results method."""
        # Setup
        client = BaseUSPTOClient(base_url="https://api.test.com")
        client.session = mock_session

        # Create mock responses
        first_response = MagicMock()
        first_response.count = 2
        first_response.items = ["item1", "item2"]

        second_response = MagicMock()
        second_response.count = 1
        second_response.items = ["item3"]

        third_response = MagicMock()
        third_response.count = 0
        third_response.items = []

        # Create a test class with the method we want to paginate
        class TestClient(BaseUSPTOClient):
            def test_method(self, **kwargs):
                # Return different responses based on offset
                offset = kwargs.get("offset", 0)
                if offset == 0:
                    return first_response
                elif offset == 2:
                    return second_response
                else:
                    return third_response

        # Use our test client
        test_client = TestClient(base_url="https://api.test.com")
        test_client.session = mock_session

        # Spy on the test_method to verify calls
        with patch.object(
            test_client, "test_method", wraps=test_client.test_method
        ) as spy_method:
            # Test paginate_results
            results = list(
                test_client.paginate_results(
                    method_name="test_method",
                    response_container_attr="items",
                    param1="value1",
                    limit=2,
                )
            )

            # Verify
            assert results == ["item1", "item2", "item3"]
            assert spy_method.call_count == 2
            spy_method.assert_any_call(param1="value1", offset=0, limit=2)
            spy_method.assert_any_call(param1="value1", offset=2, limit=2)


class TestExceptions:
    """Tests for the exception classes."""

    def test_uspto_api_error(self) -> None:
        """Test USPTOApiError."""
        # Test with status_code
        error = USPTOApiError("Test error", 400)
        assert str(error) == "Test error"
        assert error.status_code == 400

        # Test without status_code
        error = USPTOApiError("Test error")
        assert str(error) == "Test error"
        assert error.status_code is None

    def test_exception_inheritance(self) -> None:
        """Test exception inheritance."""
        # Test USPTOApiAuthError
        error = USPTOApiAuthError("Auth error", 401)
        assert isinstance(error, USPTOApiError)
        assert str(error) == "Auth error"
        assert error.status_code == 401

        # Test USPTOApiRateLimitError
        error = USPTOApiRateLimitError("Rate limit error", 429)
        assert isinstance(error, USPTOApiError)
        assert str(error) == "Rate limit error"
        assert error.status_code == 429

        # Test USPTOApiNotFoundError
        error = USPTOApiNotFoundError("Not found error", 404)
        assert isinstance(error, USPTOApiError)
        assert str(error) == "Not found error"
        assert error.status_code == 404
