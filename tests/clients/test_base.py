"""
Tests for the pyUSPTO.base module.

This module contains tests for the BaseUSPTOClient class.
"""

from typing import Any, cast
from unittest.mock import MagicMock, mock_open, patch

import pytest
import requests
from requests.adapters import HTTPAdapter

import pyUSPTO.models.base as BaseModels
from pyUSPTO.clients.base import BaseUSPTOClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.exceptions import (
    USPTOApiAuthError,
    USPTOApiBadRequestError,
    USPTOApiError,
    USPTOApiNotFoundError,
    USPTOApiPayloadTooLargeError,
    USPTOApiRateLimitError,
    USPTOApiResponseParseError,
    USPTOApiServerError,
    USPTOConnectionError,
    USPTOTimeout,
)


@pytest.fixture
def uspto_config() -> USPTOConfig:
    """Provides a USPTOConfig instance with test API key."""
    mock_session = MagicMock()
    config = USPTOConfig(api_key="test_key")
    config._session = mock_session
    return config


class TestModelsBase:
    """Test classes from models.base."""

    def test_base_model_initialization(self) -> None:
        """Tests BaseModel initialization with raw_data and kwargs."""
        raw_input = {"key1": "value1"}
        kwarg_input = {"attr1": "hello", "attr2": 123}

        # Test with only raw_data
        model1 = BaseModels.BaseModel(raw_data=raw_input)
        assert model1.raw_data == raw_input
        assert not hasattr(
            model1, "key1"
        )  # raw_data keys are not automatically attributes
        assert not hasattr(model1, "attr1")

        # Test with only kwargs
        model2 = BaseModels.BaseModel(**kwarg_input)
        assert model2.raw_data is None
        assert model2.attr1 == "hello"  # type: ignore  # Attribute set by kwarg
        assert model2.attr2 == 123  # type: ignore  # Attribute set by kwarg
        assert not hasattr(model2, "key1")

        # Test with both raw_data and kwargs
        model3 = BaseModels.BaseModel(raw_data=raw_input, **kwarg_input)
        assert model3.raw_data == raw_input
        assert model3.attr1 == "hello"  # type: ignore  # Attribute set by kwarg
        assert model3.attr2 == 123  # type: ignore  # Attribute set by kwarg
        assert not hasattr(
            model3, "key1"
        )  # Ensure raw_data keys don't conflict unless also in kwargs

        # Test with kwargs that might overlap with raw_data keys (kwargs should win for attributes)
        model4 = BaseModels.BaseModel(
            raw_data=raw_input, key1="kwarg_value_for_key1", attr1="another_val"
        )
        assert model4.raw_data == raw_input
        assert (
            model4.key1 == "kwarg_value_for_key1"  # type: ignore
        )  # Attribute set by kwarg
        assert model4.attr1 == "another_val"  # type: ignore

        # Test with no parameters
        model5 = BaseModels.BaseModel()
        assert model5.raw_data is None
        # Check no unexpected attributes were set
        assert len(model5.__dict__) == 1  # Should only have raw_data


class TestResponseClass:
    """Test class implementing FromDictProtocol for testing."""

    data: dict[str, Any]

    @classmethod
    def from_dict(
        cls, data: dict[str, Any], include_raw_data: bool = False
    ) -> "TestResponseClass":
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
            config=USPTOConfig(api_key="test_key"), base_url="https://api.test.com"
        )
        assert client._api_key == "test_key"
        assert client.api_key == "********"  # API key is masked
        assert client.base_url == "https://api.test.com"
        assert "X-API-KEY" in client.session.headers
        assert client.session.headers["X-API-KEY"] == "test_key"

        # Test without API key
        client = BaseUSPTOClient(base_url="https://api.test.com")
        assert client._api_key is None
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
        assert cast(HTTPAdapter, http_adapter).max_retries.backoff_factor == 2

    def test_make_request_get(self, mock_session: MagicMock) -> None:
        """Test _make_request method with GET."""
        # Setup
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(base_url="https://api.test.com")
        client.config._session = mock_session

        mock_response = MagicMock()
        mock_response.json.return_value = {"key": "value"}
        mock_session.get.return_value = mock_response

        # Test GET request
        result = client._make_request(
            method="GET", endpoint="test", params={"param": "value"}
        )

        # Verify
        mock_session.get.assert_called_once_with(
            url="https://api.test.com/test",
            params={"param": "value"},
            stream=False,
            timeout=(10.0, 30.0),  # Default HTTPConfig timeout
        )
        assert result == {"key": "value"}

    def test_make_request_post(self, mock_session: MagicMock) -> None:
        """Test _make_request method with POST."""
        # Setup
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(base_url="https://api.test.com")
        client.config._session = mock_session

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
            timeout=(10.0, 30.0),  # Default HTTPConfig timeout
        )
        assert result == {"key": "value"}

    def test_make_request_with_response_class(self, mock_session: MagicMock) -> None:
        """Test _make_request method with response_class."""
        # Setup
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(base_url="https://api.test.com")
        client.config._session = mock_session

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
        client.config._session = mock_session

        mock_response = MagicMock()
        mock_response.json.return_value = {"key": "value"}
        mock_session.get.return_value = mock_response

        # Test with custom_base_url
        result = client._make_request(
            method="GET",
            endpoint="test",
            custom_url="https://custom.api.test.com",
        )

        # Verify
        mock_session.get.assert_called_once_with(
            url="https://custom.api.test.com",
            params=None,
            stream=False,
            timeout=(10.0, 30.0),  # Default HTTPConfig timeout
        )
        assert result == {"key": "value"}

    def test_make_request_with_stream(self, mock_session: MagicMock) -> None:
        """Test _make_request method with stream=True."""
        # Setup
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(base_url="https://api.test.com")
        client.config._session = mock_session

        mock_response = MagicMock()
        mock_session.get.return_value = mock_response

        # Test with stream=True
        result = client._make_request(method="GET", endpoint="test", stream=True)

        # Verify
        mock_session.get.assert_called_once_with(
            url="https://api.test.com/test",
            params=None,
            stream=True,
            timeout=(10.0, 30.0),  # Default HTTPConfig timeout
        )
        assert result == mock_response
        mock_response.json.assert_not_called()

    def test_make_request_invalid_method(self, mock_session: MagicMock) -> None:
        """Test _make_request method with invalid HTTP method."""
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(base_url="https://api.test.com")

        # Test with invalid method
        with pytest.raises(ValueError, match="Unsupported HTTP method: DELETE"):
            client._make_request(method="DELETE", endpoint="test")

        # Test catch-all error case with unknown status code
        mock_response = MagicMock()
        mock_response.status_code = (
            418  # I'm a teapot (unused status in the specific handlers)
        )
        mock_response.json.return_value = {
            "errorDetails": "I'm a teapot",
            "requestIdentifier": "req-418",
        }
        mock_session.get.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )

        with pytest.raises(USPTOApiError) as excinfo:
            client._make_request(method="GET", endpoint="test")
        assert "I'm a teapot" in str(excinfo.value)
        assert excinfo.value.error_details == "I'm a teapot"
        assert excinfo.value.status_code == 418

    def test_make_request_http_errors(self, mock_session: MagicMock) -> None:
        """Test _make_request method with HTTP errors."""
        # Setup
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(base_url="https://api.test.com")
        client.config._session = mock_session

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
        with pytest.raises(expected_exception=USPTOApiAuthError) as excinfo:
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
            "message": "API Payload Too Large",
            "detailedMessage": "Request entity too large.",
            "requestIdentifier": "req-413",
        }
        with pytest.raises(expected_exception=USPTOApiPayloadTooLargeError) as excinfo:
            client._make_request(method="GET", endpoint="test")
            assert "Payload Too Large" in str(excinfo.value)
            assert excinfo.value.error_details == "Request entity too large."
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
            "errorDetails": "Alternative error format",
            "requestIdentifier": "req-500-alt",
        }
        with pytest.raises(USPTOApiServerError) as excinfo:
            client._make_request(method="GET", endpoint="test")
            assert "Alternative error format" in str(object=excinfo.value)
            assert excinfo.value.error_details == "Alternative error format"
            assert excinfo.value.request_identifier == "req-500-alt"

        # Test other HTTP error without JSON response
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = "This is an error less than 500 chars."
        with pytest.raises(USPTOApiServerError) as excinfo:
            client._make_request(method="GET", endpoint="test")
            assert "This is an error less than 500 chars." in str(excinfo.value)
            assert excinfo.value.request_identifier is None

    def test_make_request_post_error_includes_body(
        self, mock_session: MagicMock
    ) -> None:
        """Test that POST request errors include the request body in the error message."""
        # Setup
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(base_url="https://api.test.com")
        client.config._session = mock_session

        # Mock a 400 Bad Request error
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )
        mock_response.json.return_value = {
            "errorDetails": "Invalid request",
            "requestIdentifier": "req-400",
        }
        mock_response.text = '{"errorDetails": "Invalid request"}'

        mock_session.post.return_value = mock_response

        # Make a POST request with a body
        post_body = {"q": "test query", "pagination": {"limit": 100}}

        with pytest.raises(USPTOApiBadRequestError) as excinfo:
            client._make_request(method="POST", endpoint="test", json_data=post_body)

        # Verify the error message includes the POST body
        error_message = str(excinfo.value)
        assert "Request body sent:" in error_message
        assert '"q": "test query"' in error_message
        assert '"pagination"' in error_message

    def test_make_request_connection_error(self, mock_session: MagicMock) -> None:
        """Test _make_request method with connection error."""
        # Setup
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(base_url="https://api.test.com")
        client.config._session = mock_session

        # Test connection error
        mock_session.get.side_effect = requests.exceptions.ConnectionError(
            "Connection refused"
        )

        with pytest.raises(USPTOConnectionError) as excinfo:
            client._make_request(method="GET", endpoint="test")

        # Verify error details
        assert "Failed to connect to" in str(excinfo.value)
        assert "https://api.test.com/test" in str(excinfo.value)
        assert excinfo.value.api_short_error == "Connection Error"

    def test_make_request_timeout_error(self, mock_session: MagicMock) -> None:
        """Test _make_request method with timeout error."""
        # Setup
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(base_url="https://api.test.com")
        client.config._session = mock_session

        # Test timeout error
        mock_session.get.side_effect = requests.exceptions.Timeout("Request timed out")

        with pytest.raises(USPTOTimeout) as excinfo:
            client._make_request(method="GET", endpoint="test")

        # Verify error details
        assert "timed out" in str(excinfo.value)
        assert "https://api.test.com/test" in str(excinfo.value)
        assert excinfo.value.api_short_error == "Timeout"

    def test_make_request_generic_request_exception(
        self, mock_session: MagicMock
    ) -> None:
        """Test _make_request method with generic request exception."""
        # Setup
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(base_url="https://api.test.com")
        client.config._session = mock_session

        # Test generic RequestException (not Timeout or ConnectionError)
        mock_session.get.side_effect = requests.exceptions.RequestException(
            "Some other network issue"
        )

        # Should fall back to generic USPTOApiError
        expected_message_pattern = "API request to 'https://api.test.com/test' failed due to a network or request issue"
        with pytest.raises(USPTOApiError, match=expected_message_pattern):
            client._make_request(method="GET", endpoint="test")

    def test_make_request_json_parse_error(self, mock_session: MagicMock) -> None:
        """Test _make_request method with JSON parsing error."""
        # Setup
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(base_url="https://api.test.com")
        client.config._session = mock_session

        # Mock successful HTTP response but with non-JSON content
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "text/html"}
        mock_response.text = "<html><body>Error page</body></html>"
        mock_response.json.side_effect = ValueError("Expecting value: line 1 column 1")
        mock_response.raise_for_status.return_value = None

        mock_session.get.return_value = mock_response

        # Should raise USPTOApiResponseParseError
        with pytest.raises(USPTOApiResponseParseError) as excinfo:
            client._make_request(method="GET", endpoint="test")

        # Verify error details
        assert "Failed to parse JSON response" in str(excinfo.value)
        assert excinfo.value.status_code == 200
        assert excinfo.value.api_short_error == "JSON Parse Error"
        assert "text/html" in str(excinfo.value.error_details)
        assert "Error page" in str(excinfo.value.error_details)

    def test_make_request_json_parse_error_with_response_class(
        self, mock_session: MagicMock
    ) -> None:
        """Test _make_request with JSON parsing error when using response_class."""
        # Setup
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(base_url="https://api.test.com")
        client.config._session = mock_session

        # Mock successful HTTP response but with invalid JSON
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.text = "Not valid JSON at all"
        mock_response.json.side_effect = requests.exceptions.JSONDecodeError(
            "Invalid JSON", "doc", 0
        )
        mock_response.raise_for_status.return_value = None

        mock_session.get.return_value = mock_response

        # Should raise USPTOApiResponseParseError even with response_class
        with pytest.raises(USPTOApiResponseParseError) as excinfo:
            client._make_request(
                method="GET", endpoint="test", response_class=TestResponseClass
            )

        # Verify error details
        assert "Failed to parse JSON response" in str(excinfo.value)
        assert excinfo.value.status_code == 200
        assert "application/json" in str(excinfo.value.error_details)

    def test_paginate_results(self, mock_session: MagicMock) -> None:
        """Test paginate_results method."""
        # Setup
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(base_url="https://api.test.com")
        client.config._session = mock_session

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
        test_client.config._session = mock_session

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

            # Test early return with count < limit
            # Create a response where count < limit to trigger the early return
            partial_response = MagicMock()
            partial_response.count = 1  # Less than limit=2
            partial_response.items = ["partial-item"]

            class TestPartialClient(BaseUSPTOClient[Any]):
                def test_method(self, **kwargs: Any) -> Any:
                    return partial_response

            # Use our test client for partial results
            test_partial_client = TestPartialClient(base_url="https://api.test.com")
            test_partial_client.config._session = mock_session

            # Test paginate_results with early return
            results = list(
                test_partial_client.paginate_results(
                    method_name="test_method",
                    response_container_attr="items",
                    limit=2,
                )
            )

            # Verify early return works
            assert results == ["partial-item"]

            # Test zero count case (empty response)
            empty_response = MagicMock()
            empty_response.count = 0  # No results
            empty_response.items = []

            class TestEmptyClient(BaseUSPTOClient[Any]):
                def test_method(self, **kwargs: Any) -> Any:
                    return empty_response

            # Use our test client for empty results
            test_empty_client = TestEmptyClient(base_url="https://api.test.com")
            test_empty_client.config._session = mock_session

            # Test paginate_results with empty response
            results = list(
                test_empty_client.paginate_results(
                    method_name="test_method",
                    response_container_attr="items",
                    limit=2,
                )
            )

            # Verify empty results works
            assert results == []

    def test_paginate_results_with_nested_pagination(
        self, mock_session: MagicMock
    ) -> None:
        """Test paginate_results handles nested pagination structure correctly."""
        # Setup client
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(base_url="https://api.test.com")
        client.config._session = mock_session

        # Create mock responses
        # response.count is the TOTAL count across all pages
        # Break condition: response.count < limit + offset
        first_response = MagicMock()
        first_response.count = 3  # Total: 3 items across all pages
        first_response.items = ["item1", "item2"]

        second_response = MagicMock()
        second_response.count = 3  # Total still 3, triggers break: 3 < 2 + 2 is False, but we yield then break
        second_response.items = ["item3"]

        # Track what post_body was actually sent
        received_bodies: list[dict[str, Any]] = []

        def mock_test_method(
            post_body: dict[str, Any] | None = None, **kwargs: Any
        ) -> Any:
            """Mock method that tracks POST body and returns appropriate response."""
            # Record the body we received
            if post_body:
                received_bodies.append(post_body.copy())

            # Return different responses based on offset in nested pagination
            if post_body and "pagination" in post_body:
                offset = post_body["pagination"].get("offset", 0)
                if offset == 0:
                    return first_response
                elif offset == 2:
                    return second_response
            # Should not reach here
            return MagicMock(count=0, items=[])

        # Add the mock method to the client
        client.test_method = mock_test_method  # type: ignore[attr-defined]

        # Test with nested pagination structure (like USPTO API accepts)
        post_body = {
            "q": "applicationMetaData.applicationStatusDate:>2025-06-16",
            "filters": [{"name": "eventDataBag.eventCode", "value": ["CTNF", "CTFR"]}],
            "fields": ["applicationNumberText", "eventDataBag"],
            "pagination": {"limit": 2},  # Nested structure
        }

        results = list(
            client.paginate_results(
                method_name="test_method",
                response_container_attr="items",
                post_body=post_body,
            )
        )

        # Verify results
        assert results == ["item1", "item2", "item3"]

        # Verify that pagination params were added to nested structure, not top-level
        assert len(received_bodies) == 2

        # First request should have offset=0, limit=2 in nested pagination
        first_body = received_bodies[0]
        assert "pagination" in first_body
        assert first_body["pagination"]["offset"] == 0
        assert first_body["pagination"]["limit"] == 2
        # Should NOT have top-level offset/limit
        assert "offset" not in first_body
        assert "limit" not in first_body
        # Original fields should be preserved
        assert (
            first_body["q"] == "applicationMetaData.applicationStatusDate:>2025-06-16"
        )
        assert len(first_body["filters"]) == 1
        assert first_body["fields"] == ["applicationNumberText", "eventDataBag"]

        # Second request should have offset=2, limit=2 in nested pagination
        second_body = received_bodies[1]
        assert "pagination" in second_body
        assert second_body["pagination"]["offset"] == 2
        assert second_body["pagination"]["limit"] == 2
        # Should NOT have top-level offset/limit
        assert "offset" not in second_body
        assert "limit" not in second_body

    def test_paginate_results_with_flat_pagination(
        self, mock_session: MagicMock
    ) -> None:
        """Test paginate_results still works with flat (top-level) pagination structure."""
        # Setup client
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(base_url="https://api.test.com")
        client.config._session = mock_session

        # Create mock responses
        # First page: 2 items, total count shows there's only 1 item total (less than limit)
        first_response = MagicMock()
        first_response.count = 1  # Total count (triggers break since 1 < 2 + 0)
        first_response.items = ["item1"]

        received_bodies: list[dict[str, Any]] = []

        def mock_test_method(
            post_body: dict[str, Any] | None = None, **kwargs: Any
        ) -> Any:
            """Mock method that tracks POST body and returns appropriate response."""
            if post_body:
                received_bodies.append(post_body.copy())
            return first_response

        # Add the mock method to the client
        client.test_method = mock_test_method  # type: ignore[attr-defined]

        # Test with flat (top-level) pagination structure
        post_body = {
            "q": "test query",
            "limit": 2,  # Flat structure
        }

        results = list(
            client.paginate_results(
                method_name="test_method",
                response_container_attr="items",
                post_body=post_body,
            )
        )

        # Verify results
        assert results == ["item1"]

        # Verify that pagination params were added at top-level
        assert len(received_bodies) == 1
        first_body = received_bodies[0]
        assert first_body["offset"] == 0
        assert first_body["limit"] == 2
        # Should NOT have nested pagination
        assert "pagination" not in first_body

    def test_paginate_results_rejects_offset_in_nested_pagination(
        self, mock_session: MagicMock
    ) -> None:
        """Test that offset is rejected when provided in nested pagination."""
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(base_url="https://api.test.com")
        client.config._session = mock_session

        post_body = {
            "q": "test",
            "pagination": {"offset": 10, "limit": 50},  # User provided offset - BAD
        }

        with pytest.raises(
            ValueError,
            match="Cannot specify 'offset' in post_body\\['pagination'\\]",
        ):
            list(
                client.paginate_results(
                    method_name="test_method",
                    response_container_attr="items",
                    post_body=post_body,
                )
            )

    def test_paginate_results_missing_count_attribute(
        self, mock_session: MagicMock
    ) -> None:
        """Test pagination raises AttributeError when response missing count."""
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(base_url="https://api.test.com")
        client.config._session = mock_session

        # Create response without count attribute
        mock_response = MagicMock()
        del mock_response.count  # Remove count attribute

        class TestClient(BaseUSPTOClient[Any]):
            def test_method(self, **kwargs: Any) -> Any:
                return mock_response

        test_client = TestClient(base_url="https://api.test.com")
        test_client.config._session = mock_session

        with pytest.raises(
            AttributeError, match="missing required 'count' attribute for pagination"
        ):
            list(
                test_client.paginate_results(
                    method_name="test_method", response_container_attr="items"
                )
            )

    def test_paginate_results_missing_container_attribute(
        self, mock_session: MagicMock
    ) -> None:
        """Test pagination raises AttributeError when response missing container."""
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(base_url="https://api.test.com")
        client.config._session = mock_session

        # Create response with count but without items
        mock_response = MagicMock()
        mock_response.count = 10
        del mock_response.items  # Remove items attribute

        class TestClient(BaseUSPTOClient[Any]):
            def test_method(self, **kwargs: Any) -> Any:
                return mock_response

        test_client = TestClient(base_url="https://api.test.com")
        test_client.config._session = mock_session

        with pytest.raises(
            AttributeError, match="missing required 'items' attribute for pagination"
        ):
            list(
                test_client.paginate_results(
                    method_name="test_method", response_container_attr="items"
                )
            )

    def test_paginate_results_count_none(self, mock_session: MagicMock) -> None:
        """Test pagination stops gracefully when count is None."""
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(base_url="https://api.test.com")
        client.config._session = mock_session

        mock_response = MagicMock()
        mock_response.count = None

        class TestClient(BaseUSPTOClient[Any]):
            def test_method(self, **kwargs: Any) -> Any:
                return mock_response

        test_client = TestClient(base_url="https://api.test.com")
        test_client.config._session = mock_session

        # Should return empty list without error
        results = list(
            test_client.paginate_results(
                method_name="test_method", response_container_attr="items"
            )
        )
        assert results == []

    def test_paginate_results_container_none(self, mock_session: MagicMock) -> None:
        """Test pagination raises ValueError when container is None."""
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(base_url="https://api.test.com")
        client.config._session = mock_session

        mock_response = MagicMock()
        mock_response.count = 10
        mock_response.items = None  # Container is None

        class TestClient(BaseUSPTOClient[Any]):
            def test_method(self, **kwargs: Any) -> Any:
                return mock_response

        test_client = TestClient(base_url="https://api.test.com")
        test_client.config._session = mock_session

        with pytest.raises(ValueError, match="Container 'items' is None"):
            list(
                test_client.paginate_results(
                    method_name="test_method", response_container_attr="items"
                )
            )

    def test_save_response_to_file(self, mock_session: MagicMock) -> None:
        """Test _save_response_to_file raises FileExistsError."""
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(base_url="https://api.test.com")
        client.config._session = mock_session
        mock_response = MagicMock()
        mock_response.headers = {}
        mock_response.url = "https://api.test.com/file"
        path = "tests/clients/test_file.txt"

        # Pretend Path.exists() returns True
        with patch("pyUSPTO.clients.base.Path.exists", return_value=True):
            with pytest.raises(FileExistsError):
                client._save_response_to_file(mock_response, path, overwrite=False)

    def test_base_client_with_http_config(self) -> None:
        """Test BaseUSPTOClient applies HTTPConfig settings"""
        from pyUSPTO.config import USPTOConfig
        from pyUSPTO.http_config import HTTPConfig

        http_cfg = HTTPConfig(
            max_retries=7,
            backoff_factor=2.5,
            pool_connections=15,
            pool_maxsize=20,
            custom_headers={"User-Agent": "TestApp"},
        )
        config = USPTOConfig(api_key="test", http_config=http_cfg)

        client: BaseUSPTOClient[Any] = BaseUSPTOClient(
            config=config, base_url="https://test.com"
        )

        # Verify HTTP config is stored
        assert client.http_config is http_cfg
        assert client.http_config.max_retries == 7
        assert client.http_config.backoff_factor == 2.5

        # Verify custom headers applied
        assert client.session.headers.get("User-Agent") == "TestApp"

        # Verify retry configuration (check adapter)
        adapter = client.session.get_adapter("https://test.com")
        assert isinstance(adapter, HTTPAdapter)
        assert adapter.max_retries.total == 7  # type: ignore
        assert adapter.max_retries.backoff_factor == 2.5  # type: ignore

    def test_base_client_backward_compatibility(self) -> None:
        """Test client works without HTTPConfig (backward compatibility)"""
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(
            config=USPTOConfig(api_key="test"), base_url="https://test.com"
        )

        # Should create default HTTPConfig automatically
        assert client.http_config is not None
        assert client.http_config.timeout == 30.0
        assert client.http_config.max_retries == 3

    def test_base_client_timeout_applied(self, mock_session: MagicMock) -> None:
        """Test that timeout is passed to requests"""
        from pyUSPTO.config import USPTOConfig
        from pyUSPTO.http_config import HTTPConfig

        http_cfg = HTTPConfig(timeout=45.0, connect_timeout=8.0)
        config = USPTOConfig(api_key="test", http_config=http_cfg)

        client: BaseUSPTOClient[Any] = BaseUSPTOClient(
            config=config, base_url="https://api.test.com"
        )
        client.config._session = mock_session

        mock_session.get.return_value.status_code = 200
        mock_session.get.return_value.json.return_value = {"test": "data"}

        # Make request
        client._make_request(method="GET", endpoint="test")

        # Verify timeout was passed
        mock_session.get.assert_called_once()
        call_kwargs = mock_session.get.call_args[1]
        assert "timeout" in call_kwargs
        assert call_kwargs["timeout"] == (8.0, 45.0)  # (connect, read)

    def test_base_client_with_config_object(self) -> None:
        """Test BaseUSPTOClient accepts USPTOConfig"""
        from pyUSPTO.config import USPTOConfig

        config = USPTOConfig(api_key="config_key")
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(
            config=config, base_url="https://test.com"
        )

        # API key should come from config
        assert client._api_key == "config_key"
        assert client.config is config

    def test_context_manager_enters_and_exits(self, mock_session: MagicMock) -> None:
        """Test that context manager __enter__ and __exit__ work correctly."""
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(base_url="https://api.test.com")
        client.config._session = mock_session

        # Test __enter__ returns self
        with client as ctx_client:
            assert ctx_client is client

        # Verify session not closed by client context manager
        mock_session.close.assert_not_called()

    def test_close_does_not_close_session(self, mock_session: MagicMock) -> None:
        """Test close() does NOT close session."""
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(base_url="https://api.test.com")
        client.config._session = mock_session

        client.close()
        mock_session.close.assert_not_called()

    def test_config_context_manager(self) -> None:
        """Test USPTOConfig context manager."""
        config = USPTOConfig(api_key="test")
        with config as ctx_config:
            assert ctx_config is config
            assert config.session is not None

    def test_config_close_with_session(self, uspto_config: USPTOConfig) -> None:
        """Test USPTOConfig.close() when session exists."""
        config = uspto_config
        assert config._session is not None
        config.close()
        assert config._session is None

    def test_paginate_results_rejects_offset_in_flat_post_body(
        self, mock_session: MagicMock
    ) -> None:
        """Test that offset is rejected when provided in flat POST body."""
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(base_url="https://api.test.com")
        client.config._session = mock_session

        # Flat structure with user-provided offset - should raise
        post_body = {"q": "test", "offset": 10, "limit": 50}

        with pytest.raises(ValueError, match="Cannot specify 'offset' in post_body"):
            list(
                client.paginate_results(
                    method_name="test_method",
                    response_container_attr="items",
                    post_body=post_body,
                )
            )


class TestContentDispositionParsing:
    """Tests for Content-Disposition header parsing."""

    def test_extract_filename_simple(self) -> None:
        """Test extracting filename from simple Content-Disposition."""
        filename = BaseUSPTOClient._extract_filename_from_content_disposition(
            'attachment; filename="document.pdf"'
        )
        assert filename == "document.pdf"

    def test_extract_filename_without_quotes(self) -> None:
        """Test extracting filename without quotes."""
        filename = BaseUSPTOClient._extract_filename_from_content_disposition(
            "attachment; filename=document.pdf"
        )
        assert filename == "document.pdf"

    def test_extract_filename_rfc2231(self) -> None:
        """Test extracting filename from RFC 2231 format."""
        filename = BaseUSPTOClient._extract_filename_from_content_disposition(
            "attachment; filename*=UTF-8''my%20document.pdf"
        )
        assert filename == "my document.pdf"

    def test_extract_filename_rfc2231_lowercase(self) -> None:
        """Test extracting filename from RFC 2231 format (lowercase)."""
        filename = BaseUSPTOClient._extract_filename_from_content_disposition(
            "attachment; filename*=utf-8''test%20file.txt"
        )
        assert filename == "test file.txt"

    def test_extract_filename_empty_header(self) -> None:
        """Test extracting filename from empty header."""
        filename = BaseUSPTOClient._extract_filename_from_content_disposition("")
        assert filename is None

    def test_extract_filename_no_filename(self) -> None:
        """Test extracting filename when header has no filename."""
        filename = BaseUSPTOClient._extract_filename_from_content_disposition(
            "attachment"
        )
        assert filename is None

    def test_extract_filename_complex(self) -> None:
        """Test extracting filename from complex header."""
        filename = BaseUSPTOClient._extract_filename_from_content_disposition(
            'attachment; filename="report.pdf"; size=12345'
        )
        assert filename == "report.pdf"


class TestMimeTypeMapping:
    """Tests for _get_extension_from_mime_type method."""

    def test_mime_type_pdf(self) -> None:
        """Test mapping application/pdf to .pdf extension."""
        ext = BaseUSPTOClient._get_extension_from_mime_type("application/pdf")
        assert ext == ".pdf"

    def test_mime_type_tiff(self) -> None:
        """Test mapping image/tiff to .tif extension."""
        ext = BaseUSPTOClient._get_extension_from_mime_type("image/tiff")
        assert ext == ".tif"

    def test_mime_type_tif_variant(self) -> None:
        """Test mapping image/tif to .tif extension."""
        ext = BaseUSPTOClient._get_extension_from_mime_type("image/tif")
        assert ext == ".tif"

    def test_mime_type_xml_application(self) -> None:
        """Test mapping application/xml to .xml extension."""
        ext = BaseUSPTOClient._get_extension_from_mime_type("application/xml")
        assert ext == ".xml"

    def test_mime_type_xml_text(self) -> None:
        """Test mapping text/xml to .xml extension."""
        ext = BaseUSPTOClient._get_extension_from_mime_type("text/xml")
        assert ext == ".xml"

    def test_mime_type_zip(self) -> None:
        """Test mapping application/zip to .zip extension."""
        ext = BaseUSPTOClient._get_extension_from_mime_type("application/zip")
        assert ext == ".zip"

    def test_mime_type_with_charset(self) -> None:
        """Test MIME type with charset parameter."""
        ext = BaseUSPTOClient._get_extension_from_mime_type(
            "application/pdf; charset=utf-8"
        )
        assert ext == ".pdf"

    def test_mime_type_case_insensitive(self) -> None:
        """Test MIME type mapping is case-insensitive."""
        ext = BaseUSPTOClient._get_extension_from_mime_type("APPLICATION/PDF")
        assert ext == ".pdf"

    def test_mime_type_unmapped(self) -> None:
        """Test unmapped MIME type returns None."""
        ext = BaseUSPTOClient._get_extension_from_mime_type("application/unknown")
        assert ext is None

    def test_mime_type_empty(self) -> None:
        """Test empty MIME type returns None."""
        ext = BaseUSPTOClient._get_extension_from_mime_type("")
        assert ext is None

    def test_mime_type_none(self) -> None:
        """Test None MIME type returns None."""
        ext = BaseUSPTOClient._get_extension_from_mime_type(None)
        assert ext is None


class TestSaveResponseToFile:
    """Tests for _save_response_to_file method."""

    @patch("builtins.open", new_callable=mock_open)
    def test_save_to_directory_with_content_disposition(
        self, mock_file_open: MagicMock, tmp_path: Any
    ) -> None:
        """Test saving to directory extracts filename from Content-Disposition."""

        # Create a test client
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(
            config=USPTOConfig(api_key="test"), base_url="https://test.com"
        )

        # Mock response with Content-Disposition header
        mock_response = MagicMock()
        mock_response.headers = {
            "Content-Disposition": 'attachment; filename="test_doc.pdf"'
        }
        mock_response.iter_content.return_value = [b"data1", b"data2"]

        # Save to directory (using tmp_path from pytest fixture)
        result = client._save_response_to_file(mock_response, str(tmp_path))

        # Verify the file was saved with extracted filename
        expected_path = tmp_path / "test_doc.pdf"
        mock_file_open.assert_called_once_with(expected_path, "wb")
        assert result == str(expected_path)

    @patch("builtins.open", new_callable=mock_open)
    def test_save_without_extension_uses_content_type_pdf(
        self, mock_file_open: MagicMock, tmp_path: Any
    ) -> None:
        """Test saving file without extension adds extension from Content-Type (PDF)."""
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(
            config=USPTOConfig(api_key="test"), base_url="https://test.com"
        )

        # Mock response with Content-Type but no Content-Disposition
        mock_response = MagicMock()
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.iter_content.return_value = [b"pdf data"]
        mock_response.url = "https://test.com/document"

        # Save to file without extension
        result = client._save_response_to_file(mock_response, destination=tmp_path)

        # Verify extension was added
        expected_path = tmp_path / "document.pdf"
        mock_file_open.assert_called_once_with(expected_path, "wb")
        assert result == str(expected_path)

    @patch("builtins.open", new_callable=mock_open)
    def test_save_url_without_extension_uses_content_type_tiff(
        self, mock_file_open: MagicMock, tmp_path: Any
    ) -> None:
        """Test filename from URL without extension gets extension from Content-Type (TIFF)."""
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(
            config=USPTOConfig(api_key="test"), base_url="https://test.com"
        )

        # Mock response with TIFF Content-Type, filename extracted from URL
        mock_response = MagicMock()
        mock_response.headers = {"Content-Type": "image/tiff"}
        mock_response.iter_content.return_value = [b"tiff data"]
        mock_response.url = "https://test.com/image"

        # Save to directory, filename from URL
        result = client._save_response_to_file(mock_response, destination=str(tmp_path))

        # Verify .tif extension was added
        expected_path = tmp_path / "image.tif"
        mock_file_open.assert_called_once_with(expected_path, "wb")
        assert result == str(expected_path)

    @patch("builtins.open", new_callable=mock_open)
    def test_save_url_with_existing_extension_ignores_content_type(
        self, mock_file_open: MagicMock, tmp_path: Any
    ) -> None:
        """Test filename from URL with extension ignores Content-Type."""
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(
            config=USPTOConfig(api_key="test"), base_url="https://test.com"
        )

        # Mock response with Content-Type
        mock_response = MagicMock()
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.iter_content.return_value = [b"data"]
        mock_response.url = "https://test.com/document.txt"

        # Save to directory, filename from URL with extension
        result = client._save_response_to_file(
            response=mock_response, destination=str(tmp_path)
        )

        # Verify original extension was kept
        expected_path = tmp_path / "document.txt"
        mock_file_open.assert_called_once_with(expected_path, "wb")
        assert result == str(expected_path)

    @patch("builtins.open", new_callable=mock_open)
    def test_save_url_without_extension_unmapped_mime_type(
        self, mock_file_open: MagicMock, tmp_path: Any
    ) -> None:
        """Test filename from URL with unmapped MIME type saves without extension."""
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(
            config=USPTOConfig(api_key="test"), base_url="https://test.com"
        )

        # Mock response with unmapped Content-Type
        mock_response = MagicMock()
        mock_response.headers = {"Content-Type": "application/unknown"}
        mock_response.iter_content.return_value = [b"data"]
        mock_response.url = "https://test.com/document"

        # Save to directory, filename from URL without extension, no mapped MIME type
        result = client._save_response_to_file(mock_response, destination=str(tmp_path))

        # Verify no extension was added
        expected_path = tmp_path / "document"
        mock_file_open.assert_called_once_with(expected_path, "wb")
        assert result == str(expected_path)

    @patch("builtins.open", new_callable=mock_open)
    def test_save_url_without_extension_no_content_type(
        self, mock_file_open: MagicMock, tmp_path: Any
    ) -> None:
        """Test filename from URL without Content-Type header saves without extension."""
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(
            config=USPTOConfig(api_key="test"), base_url="https://test.com"
        )

        # Mock response without Content-Type header
        mock_response = MagicMock()
        mock_response.headers = {}
        mock_response.iter_content.return_value = [b"data"]
        mock_response.url = "https://test.com/document"

        # Save to directory, filename from URL without extension, no Content-Type
        result = client._save_response_to_file(mock_response, destination=str(tmp_path))

        # Verify no extension was added
        expected_path = tmp_path / "document"
        mock_file_open.assert_called_once_with(expected_path, "wb")
        assert result == str(expected_path)

    @patch("builtins.open", new_callable=mock_open)
    def test_save_content_disposition_takes_precedence_over_content_type(
        self, mock_file_open: MagicMock, tmp_path: Any
    ) -> None:
        """Test Content-Disposition filename takes precedence over Content-Type extension."""
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(
            config=USPTOConfig(api_key="test"), base_url="https://test.com"
        )

        # Mock response with both Content-Disposition and Content-Type
        mock_response = MagicMock()
        mock_response.headers = {
            "Content-Disposition": 'attachment; filename="report.xml"',
            "Content-Type": "application/pdf",  # Different type
        }
        mock_response.iter_content.return_value = [b"data"]
        mock_response.url = "https://test.com/document"

        # Save to directory (will use Content-Disposition)
        result = client._save_response_to_file(mock_response, str(tmp_path))

        # Verify Content-Disposition filename was used (not Content-Type)
        expected_path = tmp_path / "report.xml"
        mock_file_open.assert_called_once_with(expected_path, "wb")
        assert result == str(expected_path)

    @patch("builtins.open", new_callable=mock_open)
    def test_save_fallback_to_download_filename(
        self, mock_file_open: MagicMock, tmp_path: Any
    ) -> None:
        """Test fallback to 'download' filename when no filename can be determined."""
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(
            config=USPTOConfig(api_key="test"), base_url="https://test.com"
        )

        # Mock response with no Content-Disposition, no URL path, no extension
        mock_response = MagicMock()
        mock_response.headers = {}
        mock_response.iter_content.return_value = [b"data"]
        mock_response.url = "https://test.com/"

        # Save to directory with no filename info
        result = client._save_response_to_file(mock_response, destination=str(tmp_path))

        # Verify fallback to "download"
        expected_path = tmp_path / "download"
        mock_file_open.assert_called_once_with(expected_path, "wb")
        assert result == str(expected_path)

    @patch("builtins.open", new_callable=mock_open)
    def test_save_to_current_directory_when_no_destination(
        self, mock_file_open: MagicMock
    ) -> None:
        """Test saving to current working directory when destination is None."""
        from pathlib import Path

        client: BaseUSPTOClient[Any] = BaseUSPTOClient(
            config=USPTOConfig(api_key="test"), base_url="https://test.com"
        )

        # Mock response
        mock_response = MagicMock()
        mock_response.headers = {
            "Content-Disposition": 'attachment; filename="test.pdf"'
        }
        mock_response.iter_content.return_value = [b"data"]

        # Save with no destination (should use cwd)
        with patch("pyUSPTO.clients.base.Path.cwd") as mock_cwd:
            mock_cwd.return_value = Path("/fake/cwd")
            result = client._save_response_to_file(mock_response, destination=None)

            # Verify saved to current directory
            expected_path = Path("/fake/cwd") / "test.pdf"
            mock_file_open.assert_called_once_with(expected_path, "wb")
            assert result == str(expected_path)


class TestExtractArchive:
    """Tests for _extract_archive method."""

    def test_extract_tar_file(self, tmp_path: Any) -> None:
        """Test extracting a TAR file."""
        import tarfile

        client: BaseUSPTOClient[Any] = BaseUSPTOClient(
            config=USPTOConfig(api_key="test"), base_url="https://test.com"
        )

        # Create a test TAR file
        tar_path = tmp_path / "test.tar"
        extract_to = tmp_path / "extracted"

        with tarfile.open(tar_path, "w") as tar:
            # Create a temp file to add to tar
            temp_file = tmp_path / "test_file.txt"
            temp_file.write_text("test content")
            tar.add(temp_file, arcname="test_file.txt")

        # Extract the archive
        result = client._extract_archive(tar_path, extract_to=extract_to)

        # Verify extraction
        assert (extract_to / "test_file.txt").exists()
        assert result == str(
            extract_to / "test_file.txt"
        )  # Single file returns file path

    def test_extract_tar_gz_file(self, tmp_path: Any) -> None:
        """Test extracting a TAR.GZ file."""
        import tarfile

        client: BaseUSPTOClient[Any] = BaseUSPTOClient(
            config=USPTOConfig(api_key="test"), base_url="https://test.com"
        )

        # Create a test TAR.GZ file
        tar_path = tmp_path / "test.tar.gz"
        extract_to = tmp_path / "extracted"

        with tarfile.open(tar_path, "w:gz") as tar:
            temp_file = tmp_path / "test_file.txt"
            temp_file.write_text("test content")
            tar.add(temp_file, arcname="test_file.txt")

        # Extract the archive
        result = client._extract_archive(tar_path, extract_to=extract_to)

        # Verify extraction
        assert (extract_to / "test_file.txt").exists()
        assert result == str(extract_to / "test_file.txt")

    def test_extract_zip_file(self, tmp_path: Any) -> None:
        """Test extracting a ZIP file."""
        import zipfile

        client: BaseUSPTOClient[Any] = BaseUSPTOClient(
            config=USPTOConfig(api_key="test"), base_url="https://test.com"
        )

        # Create a test ZIP file
        zip_path = tmp_path / "test.zip"
        extract_to = tmp_path / "extracted"

        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("test_file.txt", "test content")

        # Extract the archive
        result = client._extract_archive(zip_path, extract_to=extract_to)

        # Verify extraction
        assert (extract_to / "test_file.txt").exists()
        assert result == str(extract_to / "test_file.txt")

    def test_extract_multiple_files_returns_directory(self, tmp_path: Any) -> None:
        """Test extracting archive with multiple files returns directory path."""
        import tarfile

        client: BaseUSPTOClient[Any] = BaseUSPTOClient(
            config=USPTOConfig(api_key="test"), base_url="https://test.com"
        )

        # Create archive with multiple files
        tar_path = tmp_path / "test.tar"
        extract_to = tmp_path / "extracted"

        with tarfile.open(tar_path, "w") as tar:
            file1 = tmp_path / "file1.txt"
            file2 = tmp_path / "file2.txt"
            file1.write_text("content1")
            file2.write_text("content2")
            tar.add(file1, arcname="file1.txt")
            tar.add(file2, arcname="file2.txt")

        # Extract the archive
        result = client._extract_archive(tar_path, extract_to=extract_to)

        # Verify multiple files returns directory
        assert result == str(extract_to)
        assert (extract_to / "file1.txt").exists()
        assert (extract_to / "file2.txt").exists()

    def test_extract_with_remove_archive(self, tmp_path: Any) -> None:
        """Test extracting archive with remove_archive=True deletes the archive."""
        import tarfile

        client: BaseUSPTOClient[Any] = BaseUSPTOClient(
            config=USPTOConfig(api_key="test"), base_url="https://test.com"
        )

        # Create a test archive
        tar_path = tmp_path / "test.tar"
        with tarfile.open(tar_path, "w") as tar:
            temp_file = tmp_path / "test_file.txt"
            temp_file.write_text("test content")
            tar.add(temp_file, arcname="test_file.txt")

        # Verify archive exists before extraction
        assert tar_path.exists()

        # Extract with remove_archive=True
        client._extract_archive(tar_path, remove_archive=True)

        # Verify archive was deleted
        assert not tar_path.exists()

    def test_extract_invalid_archive_raises_error(self, tmp_path: Any) -> None:
        """Test extracting invalid archive raises ValueError."""
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(
            config=USPTOConfig(api_key="test"), base_url="https://test.com"
        )

        # Create a non-archive file
        invalid_file = tmp_path / "not_an_archive.txt"
        invalid_file.write_text("not an archive")

        # Try to extract - should raise ValueError
        with pytest.raises(ValueError, match="Not a valid TAR/ZIP archive"):
            client._extract_archive(invalid_file)

    def test_extract_default_extract_to_path(self, tmp_path: Any) -> None:
        """Test extracting with default extract_to uses archive stem."""
        import tarfile

        client: BaseUSPTOClient[Any] = BaseUSPTOClient(
            config=USPTOConfig(api_key="test"), base_url="https://test.com"
        )

        # Create archive
        tar_path = tmp_path / "myarchive.tar"
        with tarfile.open(tar_path, "w") as tar:
            temp_file = tmp_path / "test.txt"
            temp_file.write_text("content")
            tar.add(temp_file, arcname="test.txt")

        # Extract without specifying extract_to
        result = client._extract_archive(tar_path)

        # Should extract to archive_path.parent / archive_path.stem
        expected_dir = tmp_path / "myarchive"
        assert expected_dir.exists()
        assert (expected_dir / "test.txt").exists()
        assert result == str(expected_dir / "test.txt")

    def test_tar_path_traversal_blocked(self, tmp_path: Any) -> None:
        """Test that tar archives with ../ paths are rejected."""
        import io
        import tarfile

        client: BaseUSPTOClient[Any] = BaseUSPTOClient(
            config=USPTOConfig(api_key="test"), base_url="https://test.com"
        )

        archive_path = tmp_path / "malicious.tar"
        with tarfile.open(archive_path, "w") as tar:
            info = tarfile.TarInfo(name="../../etc/passwd")
            info.size = 10
            tar.addfile(info, io.BytesIO(b"malicious!"))

        extract_to = tmp_path / "safe_dir"
        extract_to.mkdir()

        with pytest.raises(ValueError, match="unsafe path"):
            client._extract_archive(archive_path, extract_to=extract_to)

    def test_zip_path_traversal_blocked(self, tmp_path: Any) -> None:
        """Test that zip archives with ../ paths are rejected."""
        import zipfile

        client: BaseUSPTOClient[Any] = BaseUSPTOClient(
            config=USPTOConfig(api_key="test"), base_url="https://test.com"
        )

        archive_path = tmp_path / "malicious.zip"
        with zipfile.ZipFile(archive_path, "w") as zip_ref:
            zip_ref.writestr("../../etc/passwd", "malicious!")

        extract_to = tmp_path / "safe_dir"
        extract_to.mkdir()

        with pytest.raises(ValueError, match="unsafe path"):
            client._extract_archive(archive_path, extract_to=extract_to)

    def test_max_size_enforcement(self, tmp_path: Any) -> None:
        """Test that max_size parameter prevents extracting large archives."""
        import tarfile

        client: BaseUSPTOClient[Any] = BaseUSPTOClient(
            config=USPTOConfig(api_key="test"), base_url="https://test.com"
        )

        # Create archive with known size
        archive_path = tmp_path / "large.tar"
        with tarfile.open(archive_path, "w") as tar:
            temp_file = tmp_path / "large_file.txt"
            temp_file.write_text("x" * 1000)  # 1000 bytes
            tar.add(temp_file, arcname="large_file.txt")

        extract_to = tmp_path / "extracted"

        # Should fail with max_size=500
        with pytest.raises(ValueError, match="exceeds maximum allowed"):
            client._extract_archive(archive_path, extract_to=extract_to, max_size=500)

        # Should succeed with max_size=2000
        result = client._extract_archive(
            archive_path, extract_to=extract_to, max_size=2000
        )
        assert (extract_to / "large_file.txt").exists()

    def test_max_size_enforcement_zip(self, tmp_path: Any) -> None:
        """Test that max_size parameter prevents extracting large zip archives."""
        import zipfile

        client: BaseUSPTOClient[Any] = BaseUSPTOClient(
            config=USPTOConfig(api_key="test"), base_url="https://test.com"
        )

        archive_path = tmp_path / "large.zip"
        with zipfile.ZipFile(archive_path, "w") as zip_ref:
            zip_ref.writestr("large_file.txt", "x" * 1000)

        extract_to = tmp_path / "extracted"

        # Should fail with max_size=500
        with pytest.raises(ValueError, match="exceeds maximum allowed"):
            client._extract_archive(archive_path, extract_to=extract_to, max_size=500)

    def test_tar_with_directories(self, tmp_path: Any) -> None:
        """Test that tar archives with directories extract correctly."""
        import tarfile

        client: BaseUSPTOClient[Any] = BaseUSPTOClient(
            config=USPTOConfig(api_key="test"), base_url="https://test.com"
        )

        archive_path = tmp_path / "with_dirs.tar"
        with tarfile.open(archive_path, "w") as tar:
            # Add a directory and a file
            temp_dir = tmp_path / "testdir"
            temp_dir.mkdir()
            temp_file = temp_dir / "file.txt"
            temp_file.write_text("content")
            tar.add(temp_dir, arcname="testdir")

        extract_to = tmp_path / "extracted"
        result = client._extract_archive(archive_path, extract_to=extract_to)

        # Directory entries are skipped, but files are extracted
        assert (extract_to / "testdir" / "file.txt").exists()

    def test_zip_with_directories(self, tmp_path: Any) -> None:
        """Test that zip archives with directories extract correctly."""
        import zipfile

        client: BaseUSPTOClient[Any] = BaseUSPTOClient(
            config=USPTOConfig(api_key="test"), base_url="https://test.com"
        )

        archive_path = tmp_path / "with_dirs.zip"
        with zipfile.ZipFile(archive_path, "w") as zip_ref:
            # Add directory entry and file
            zip_ref.writestr("testdir/", "")
            zip_ref.writestr("testdir/file.txt", "content")

        extract_to = tmp_path / "extracted"
        result = client._extract_archive(archive_path, extract_to=extract_to)

        # Directory entries are skipped, but files are extracted
        assert (extract_to / "testdir" / "file.txt").exists()


class TestDownloadAndExtract:
    """Tests for _download_and_extract method."""

    def test_download_and_extract_tar_file(self, tmp_path: Any) -> None:
        """Test downloading and extracting a TAR file."""
        import tarfile

        client: BaseUSPTOClient[Any] = BaseUSPTOClient(
            config=USPTOConfig(api_key="test"), base_url="https://test.com"
        )

        # Create a real TAR file to simulate download
        tar_path = tmp_path / "download.tar"
        with tarfile.open(tar_path, "w") as tar:
            temp_file = tmp_path / "document.txt"
            temp_file.write_text("content")
            tar.add(temp_file, arcname="document.txt")

        # Mock _download_file to return the tar path
        with patch.object(client, "_download_file", return_value=str(tar_path)):
            result = client._download_and_extract(
                url="https://test.com/archive.tar", destination=str(tmp_path)
            )

        # Verify it extracted (returns path to extracted content, not archive)
        assert "download" in result or "document.txt" in result
        # Verify archive was removed
        assert not tar_path.exists()

    def test_download_and_extract_zip_file(self, tmp_path: Any) -> None:
        """Test downloading and extracting a ZIP file."""
        import zipfile

        client: BaseUSPTOClient[Any] = BaseUSPTOClient(
            config=USPTOConfig(api_key="test"), base_url="https://test.com"
        )

        # Create a real ZIP file
        zip_path = tmp_path / "download.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("document.txt", "content")

        # Mock _download_file to return the zip path
        with patch.object(client, "_download_file", return_value=str(zip_path)):
            result = client._download_and_extract(
                url="https://test.com/archive.zip", destination=str(tmp_path)
            )

        # Verify extraction occurred
        assert "download" in result or "document.txt" in result
        # Verify archive was removed
        assert not zip_path.exists()

    def test_download_non_archive_returns_file_path(self, tmp_path: Any) -> None:
        """Test downloading non-archive file returns downloaded file path."""
        client: BaseUSPTOClient[Any] = BaseUSPTOClient(
            config=USPTOConfig(api_key="test"), base_url="https://test.com"
        )

        # Create a non-archive file
        file_path = tmp_path / "document.txt"
        file_path.write_text("content")

        # Mock _download_file to return the file path
        with patch.object(client, "_download_file", return_value=str(file_path)):
            result = client._download_and_extract(
                url="https://test.com/document.txt", destination=str(tmp_path)
            )

        # Should return the file path without extraction
        assert result == str(file_path)
        # File should still exist (not removed)
        assert file_path.exists()
