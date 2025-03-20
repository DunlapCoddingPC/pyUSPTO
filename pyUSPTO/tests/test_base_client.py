"""
Tests for the base client module.

This module contains tests for the BaseUSPTOClient class and related functionality.
"""

from typing import Any, Dict, cast
from unittest.mock import MagicMock, patch

import pytest
import requests
from requests.adapters import HTTPAdapter

from pyUSPTO.base import BaseUSPTOClient
from pyUSPTO.exceptions import (
    USPTOApiAuthError,
    USPTOApiBadRequestError,
    USPTOApiError,
    USPTOApiNotFoundError,
    USPTOApiPayloadTooLargeError,
    USPTOApiRateLimitError,
    USPTOApiServerError,
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
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(
            api_key="test_key", base_url="https://api.test.com"
        )
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
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(base_url="https://api.test.com")

        # Check that the session has adapters for both http and https
        assert "http://" in client.session.adapters
        assert "https://" in client.session.adapters

        # Get the retry configuration from the adapters
        http_adapter = client.session.adapters["http://"]
        https_adapter = client.session.adapters["https://"]

        # Verify both adapters have retry configuration
        assert cast(HTTPAdapter, http_adapter).max_retries is not None
        assert cast(HTTPAdapter, https_adapter).max_retries is not None

        # Verify retry settings
        # Note: We can't directly check the status_forcelist because it's not exposed
        # in a consistent way across different versions of urllib3/requests
        assert cast(HTTPAdapter, http_adapter).max_retries.total == 3
        assert cast(HTTPAdapter, http_adapter).max_retries.backoff_factor == 1

    def test_make_request_get(self, mock_session: MagicMock) -> None:
        """Test _make_request method with GET."""
        # Setup
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(base_url="https://api.test.com")
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
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(base_url="https://api.test.com")
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
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(base_url="https://api.test.com")
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
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(base_url="https://api.test.com")
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
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(base_url="https://api.test.com")
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
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(base_url="https://api.test.com")

        # Test with invalid method
        with pytest.raises(ValueError, match="Unsupported HTTP method: DELETE"):
            client._make_request(method="DELETE", endpoint="test")

    def test_make_request_http_errors(self, mock_session: MagicMock) -> None:
        """Test _make_request method with HTTP errors."""
        # Setup
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(base_url="https://api.test.com")
        client.session = mock_session

        # Test 400 error (Bad Request)
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "errorDetails": "Invalid request parameters",
            "requestIdentifier": "req-400",
        }
        mock_session.get.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )

        with pytest.raises(USPTOApiBadRequestError) as excinfo:
            client._make_request(method="GET", endpoint="test")
        assert "Invalid request parameters" in str(excinfo.value)
        assert excinfo.value.error_details == "Invalid request parameters"
        assert excinfo.value.request_identifier == "req-400"

        # Test 401 error (Auth Error)
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "errorDetails": "Authentication failed",
            "requestIdentifier": "req-401",
        }
        with pytest.raises(USPTOApiAuthError) as excinfo:
            client._make_request(method="GET", endpoint="test")
        assert "Authentication failed" in str(excinfo.value)
        assert excinfo.value.error_details == "Authentication failed"
        assert excinfo.value.request_identifier == "req-401"

        # Test 403 error (Auth Error)
        mock_response.status_code = 403
        mock_response.json.return_value = {
            "errorDetails": "Access forbidden",
            "requestIdentifier": "req-403",
        }
        with pytest.raises(USPTOApiAuthError) as excinfo:
            client._make_request(method="GET", endpoint="test")
        assert "Access forbidden" in str(excinfo.value)
        assert excinfo.value.error_details == "Access forbidden"
        assert excinfo.value.request_identifier == "req-403"

        # Test 404 error (Not Found)
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "errorDetails": "Resource not found",
            "requestIdentifier": "req-404",
        }
        with pytest.raises(USPTOApiNotFoundError) as excinfo:
            client._make_request(method="GET", endpoint="test")
        assert "Resource not found" in str(excinfo.value)
        assert excinfo.value.error_details == "Resource not found"
        assert excinfo.value.request_identifier == "req-404"

        # Test 413 error (Payload Too Large)
        mock_response.status_code = 413
        mock_response.json.return_value = {
            "errorDetails": "Payload too large",
            "requestIdentifier": "req-413",
        }
        with pytest.raises(USPTOApiPayloadTooLargeError) as excinfo:
            client._make_request(method="GET", endpoint="test")
        assert "Payload too large" in str(excinfo.value)
        assert excinfo.value.error_details == "Payload too large"
        assert excinfo.value.request_identifier == "req-413"

        # Test 429 error (Rate Limit)
        mock_response.status_code = 429
        mock_response.json.return_value = {
            "errorDetails": "Rate limit exceeded",
            "requestIdentifier": "req-429",
        }
        with pytest.raises(USPTOApiRateLimitError) as excinfo:
            client._make_request(method="GET", endpoint="test")
        assert "Rate limit exceeded" in str(excinfo.value)
        assert excinfo.value.error_details == "Rate limit exceeded"
        assert excinfo.value.request_identifier == "req-429"

        # Test 500 error (Server Error)
        mock_response.status_code = 500
        mock_response.json.return_value = {
            "errorDetails": "Internal server error",
            "requestIdentifier": "req-500",
        }
        with pytest.raises(USPTOApiServerError) as excinfo:
            client._make_request(method="GET", endpoint="test")
        assert "Internal server error" in str(excinfo.value)
        assert excinfo.value.error_details == "Internal server error"
        assert excinfo.value.request_identifier == "req-500"

        # Test detailedError field instead of errorDetails
        mock_response.status_code = 500
        mock_response.json.return_value = {
            "detailedError": "Alternative error format",
            "requestIdentifier": "req-500-alt",
        }
        with pytest.raises(USPTOApiServerError) as excinfo:
            client._make_request(method="GET", endpoint="test")
        assert "Alternative error format" in str(excinfo.value)
        assert excinfo.value.error_details == "Alternative error format"
        assert excinfo.value.request_identifier == "req-500-alt"

        # Test other HTTP error without JSON response
        mock_response.json.side_effect = ValueError("Invalid JSON")
        with pytest.raises(USPTOApiServerError) as excinfo:
            client._make_request(method="GET", endpoint="test")
        assert "API Error 500" in str(excinfo.value)
        assert excinfo.value.error_details is None
        assert excinfo.value.request_identifier is None

    def test_make_request_request_exception(self, mock_session: MagicMock) -> None:
        """Test _make_request method with request exception."""
        # Setup
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(base_url="https://api.test.com")
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
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(base_url="https://api.test.com")
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
        class TestClient(BaseUSPTOClient[Any]):
            def test_method(self, **kwargs: Any) -> Any:
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
        # Test with status_code only
        error = USPTOApiError("Test error", 400)
        assert str(error) == "Test error"
        assert error.status_code == 400
        assert error.error_details is None
        assert error.request_identifier is None

        # Test with all parameters
        error = USPTOApiError("Test error", 400, "Detailed error message", "req-123")
        assert str(error) == "Test error"
        assert error.status_code == 400
        assert error.error_details == "Detailed error message"
        assert error.request_identifier == "req-123"

        # Test without status_code
        error = USPTOApiError("Test error")
        assert str(error) == "Test error"
        assert error.status_code is None
        assert error.error_details is None
        assert error.request_identifier is None

    def test_exception_inheritance(self) -> None:
        """Test exception inheritance."""
        # Test USPTOApiBadRequestError
        bad_request_error = USPTOApiBadRequestError(
            "Bad request", 400, "Invalid parameters", "req-400"
        )
        assert isinstance(bad_request_error, USPTOApiError)
        assert str(bad_request_error) == "Bad request"
        assert bad_request_error.status_code == 400
        assert bad_request_error.error_details == "Invalid parameters"
        assert bad_request_error.request_identifier == "req-400"

        # Test USPTOApiAuthError
        auth_error = USPTOApiAuthError("Auth error", 401, "Invalid API key", "req-401")
        assert isinstance(auth_error, USPTOApiError)
        assert str(auth_error) == "Auth error"
        assert auth_error.status_code == 401
        assert auth_error.error_details == "Invalid API key"
        assert auth_error.request_identifier == "req-401"

        # Test USPTOApiRateLimitError
        rate_limit_error = USPTOApiRateLimitError(
            "Rate limit error", 429, "Too many requests", "req-429"
        )
        assert isinstance(rate_limit_error, USPTOApiError)
        assert str(rate_limit_error) == "Rate limit error"
        assert rate_limit_error.status_code == 429
        assert rate_limit_error.error_details == "Too many requests"
        assert rate_limit_error.request_identifier == "req-429"

        # Test USPTOApiNotFoundError
        not_found_error = USPTOApiNotFoundError(
            "Not found error", 404, "Resource does not exist", "req-404"
        )
        assert isinstance(not_found_error, USPTOApiError)
        assert str(not_found_error) == "Not found error"
        assert not_found_error.status_code == 404
        assert not_found_error.error_details == "Resource does not exist"
        assert not_found_error.request_identifier == "req-404"

        # Test USPTOApiPayloadTooLargeError
        payload_too_large_error = USPTOApiPayloadTooLargeError(
            "Payload too large", 413, "Exceeds 6MB limit", "req-413"
        )
        assert isinstance(payload_too_large_error, USPTOApiError)
        assert str(payload_too_large_error) == "Payload too large"
        assert payload_too_large_error.status_code == 413
        assert payload_too_large_error.error_details == "Exceeds 6MB limit"
        assert payload_too_large_error.request_identifier == "req-413"

        # Test USPTOApiServerError
        server_error = USPTOApiServerError(
            "Server error", 500, "Internal error", "req-500"
        )
        assert isinstance(server_error, USPTOApiError)
        assert str(server_error) == "Server error"
        assert server_error.status_code == 500
        assert server_error.error_details == "Internal error"
        assert server_error.request_identifier == "req-500"
