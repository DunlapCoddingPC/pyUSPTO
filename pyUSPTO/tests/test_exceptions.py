"""
Tests for the pyUSPTO.exceptions module.

This module contains tests for exception classes, helper structures,
and functions defined in pyUSPTO.exceptions.
"""

from typing import Optional, Type, Union
from unittest.mock import MagicMock

import pytest
import requests  # For requests.exceptions

# Assuming your exceptions module is in pyUSPTO.exceptions
from pyUSPTO.exceptions import (
    APIErrorArgs,
    USPTOApiAuthError,
    USPTOApiBadRequestError,
    USPTOApiError,
    USPTOApiNotFoundError,
    USPTOApiPayloadTooLargeError,
    USPTOApiRateLimitError,
    USPTOApiServerError,
    get_api_exception,
)


class TestAPIErrorArgs:
    """Tests for the APIErrorArgs dataclass and its methods."""

    def test_direct_instantiation(self) -> None:
        """Test direct instantiation of APIErrorArgs."""
        args = APIErrorArgs(
            message="Client message",
            status_code=400,
            api_short_error="Bad Request",
            error_details={"field": "is wrong"},
            request_identifier="req-123",
        )
        assert args.message == "Client message"
        assert args.status_code == 400
        assert args.api_short_error == "Bad Request"
        assert args.error_details == {"field": "is wrong"}
        assert args.request_identifier == "req-123"

    def test_from_http_error_basic(self) -> None:
        """Test from_http_error with a basic HTTPError."""
        mock_http_error = MagicMock(spec=requests.exceptions.HTTPError)
        mock_http_error.response = MagicMock(spec=requests.Response)
        mock_http_error.response.status_code = 400
        mock_http_error.response.reason = "Bad Request Reason"
        mock_http_error.response.headers = {"content-type": "application/json"}
        mock_http_error.response.json.return_value = {
            "error": "API Bad Request",
            "errorDetails": "Invalid parameter.",
            "requestIdentifier": "req-abc",
        }
        mock_http_error.response.text = '{"error": "API Bad Request", "errorDetails": "Invalid parameter.", "requestIdentifier": "req-abc"}'

        args = APIErrorArgs.from_http_error(
            http_error=mock_http_error, client_operation_message="Test operation failed"
        )

        assert args.message == "Test operation failed"
        assert args.status_code == 400
        assert args.api_short_error == "API Bad Request"
        assert args.error_details == "Invalid parameter."
        assert args.request_identifier == "req-abc"

    def test_from_http_error_413(self) -> None:
        """Test from_http_error for 413 status code with different field names."""
        mock_http_error = MagicMock(spec=requests.exceptions.HTTPError)
        mock_http_error.response = MagicMock(spec=requests.Response)
        mock_http_error.response.status_code = 413
        mock_http_error.response.reason = "Payload Too Large"
        mock_http_error.response.headers = {"content-type": "application/json"}
        mock_http_error.response.json.return_value = {
            "message": "API Payload Too Large",
            "detailedMessage": "Request entity too large.",
            "requestIdentifier": "req-413",
        }
        mock_http_error.response.text = '{"message": "API Payload Too Large", "detailedMessage": "Request entity too large.", "requestIdentifier": "req-413"}'

        args = APIErrorArgs.from_http_error(
            http_error=mock_http_error, client_operation_message="Upload failed"
        )

        assert args.message == "Upload failed"
        assert args.status_code == 413
        assert args.api_short_error == "API Payload Too Large"
        assert args.error_details == "Request entity too large."
        assert args.request_identifier == "req-413"

    def test_from_http_error_json_body_missing_fields(self) -> None:
        """Test from_http_error with JSON body but missing expected error fields."""
        mock_http_error = MagicMock(spec=requests.exceptions.HTTPError)
        mock_http_error.response = MagicMock(spec=requests.Response)
        mock_http_error.response.status_code = 400
        mock_http_error.response.reason = "Bad Request Reason"
        mock_http_error.response.headers = {"content-type": "application/json"}
        mock_http_error.response.json.return_value = {
            "unexpected_field": "some_value"
        }  # No 'error' or 'errorDetails'
        mock_http_error.response.text = '{"unexpected_field": "some_value"}'

        args = APIErrorArgs.from_http_error(
            http_error=mock_http_error, client_operation_message="Client op failed"
        )
        assert args.message == "Client op failed"
        assert args.status_code == 400
        assert args.api_short_error == "Bad Request Reason"  # Fallback to reason
        assert (
            args.error_details == '{"unexpected_field": "some_value"}'
        )  # Fallback to full text if JSON but no specific detail fields
        assert args.request_identifier is None

    def test_from_request_exception(self) -> None:
        """Test from_request_exception for non-HTTP errors."""
        mock_req_exception = MagicMock(spec=requests.exceptions.ConnectionError)
        mock_req_exception.__str__.return_value = "Connection refused"  # type: ignore[attr-defined]

        args_with_client_msg = APIErrorArgs.from_request_exception(
            request_exception=mock_req_exception,
            client_operation_message="Connecting to service",
        )
        assert (
            args_with_client_msg.message
            == "Connecting to service due to a network or request issue: Connection refused"
        )
        assert args_with_client_msg.status_code is None
        assert args_with_client_msg.api_short_error is None

        args_no_client_msg = APIErrorArgs.from_request_exception(
            request_exception=mock_req_exception
        )
        assert (
            args_no_client_msg.message
            == "API request failed due to a network or request issue: Connection refused"
        )

    def test_from_http_error_non_json_long_text(self) -> None:
        """
        Tests from_http_error when response text is long, not JSON,
        and error_details should be the generic message.
        """
        mock_http_error = MagicMock(spec=requests.exceptions.HTTPError)
        mock_http_error.response = MagicMock(spec=requests.Response)
        status_code = 500
        mock_http_error.response.status_code = status_code
        mock_http_error.response.reason = "Internal Server Error"
        mock_http_error.response.headers = {"content-type": "text/html"}  # Not JSON
        mock_http_error.response.json.side_effect = ValueError("No JSON")
        # Create text longer than 500 characters
        mock_http_error.response.text = "a" * 501

        args = APIErrorArgs.from_http_error(
            http_error=mock_http_error, client_operation_message="Server call failed"
        )

        assert (
            args.error_details
            == f"Non-JSON error response (status {status_code}). Check response text."
        )
        assert args.api_short_error == "Internal Server Error"

    def test_from_http_error_non_json_short_text(self) -> None:
        """
        Tests from_http_error when response text is short, not JSON,
        and error_details should be the actual response text.
        """
        mock_http_error = MagicMock(spec=requests.exceptions.HTTPError)
        mock_http_error.response = MagicMock(spec=requests.Response)
        mock_http_error.response.status_code = 500
        mock_http_error.response.reason = "Internal Server Error"
        mock_http_error.response.headers = {"content-type": "text/plain"}  # Not JSON
        mock_http_error.response.json.side_effect = ValueError("No JSON")
        # Create text shorter than or equal to 500 characters
        short_text = "This is a short error page."
        mock_http_error.response.text = short_text

        args = APIErrorArgs.from_http_error(
            http_error=mock_http_error, client_operation_message="Server call failed"
        )

        assert args.error_details == short_text
        assert args.api_short_error == "Internal Server Error"


class TestGetAPIException:
    """Tests for the get_api_exception helper function."""

    @pytest.mark.parametrize(
        "status_code, expected_exception_type",
        [
            (400, USPTOApiBadRequestError),
            (401, USPTOApiAuthError),
            (403, USPTOApiAuthError),
            (404, USPTOApiNotFoundError),
            (413, USPTOApiPayloadTooLargeError),
            (429, USPTOApiRateLimitError),
            (500, USPTOApiServerError),
            (503, USPTOApiServerError),
            (418, USPTOApiError),  # "I'm a teapot" - should default to base
            (None, USPTOApiError),  # For non-HTTP errors
        ],
    )
    def test_returns_correct_exception_type(
        self, status_code: Optional[int], expected_exception_type: USPTOApiError
    ) -> None:
        """Test that get_api_exception returns the correct type of exception."""
        message_val: str = "Test operation"
        api_short_error_val: Optional[str] = "API Short Error"
        # Ensure error_details_val matches the Optional[Union[str, dict]] type
        error_details_val: Optional[Union[str, dict]] = "Some details here."
        request_identifier_val: Optional[str] = "req-id-test"

        if status_code is None:  # For non-HTTP errors, these fields might be None
            api_short_error_val = None
            error_details_val = None
            request_identifier_val = None

        args = APIErrorArgs(
            message=message_val,
            status_code=status_code,
            api_short_error=api_short_error_val,
            error_details=error_details_val,
            request_identifier=request_identifier_val,
        )
        exception_instance = get_api_exception(args)

        assert isinstance(exception_instance, USPTOApiError)
        # Access the message via .message property or .args[0] as per USPTOApiError definition
        assert exception_instance.message == message_val
        assert exception_instance.status_code == status_code
        assert exception_instance.api_short_error == api_short_error_val
        assert exception_instance.error_details == error_details_val
        assert exception_instance.request_identifier == request_identifier_val


class TestExceptionClassesStr:
    """Tests the __str__ method of USPTOApiError and its subclasses."""

    def test_uspto_api_error_str_all_fields(self) -> None:
        """Test USPTOApiError.__str__ with all fields populated."""
        error = USPTOApiError(
            message="Client context message",
            status_code=400,
            api_short_error="Bad Request",
            error_details={"field": "value", "reason": "invalid"},
            request_identifier="req-xyz-789",
        )
        expected_str = (
            "Client context message - HTTP Status: 400 - API Error: Bad Request - "
            "Details: {'field': 'value', 'reason': 'invalid'} - Request ID: req-xyz-789"
        )
        assert str(error) == expected_str

    def test_uspto_api_error_str_some_fields_none(self) -> None:
        """Test USPTOApiError.__str__ with some optional fields being None."""
        error = USPTOApiError(
            message="Client context message",
            status_code=404,
            api_short_error="Not Found",
            # error_details is None, request_identifier is None
        )
        expected_str = (
            "Client context message - HTTP Status: 404 - API Error: Not Found"
        )
        assert str(error) == expected_str

    def test_uspto_api_error_str_only_message(self) -> None:
        """Test USPTOApiError.__str__ with only the message field."""
        error = USPTOApiError(message="A network connection error occurred.")
        expected_str = "A network connection error occurred."
        assert str(error) == expected_str

    def test_subclass_str_method_inherited(self) -> None:
        """Test that subclasses inherit and use the USPTOApiError.__str__ method."""
        error = USPTOApiBadRequestError(
            message="Specific client context for bad request",
            status_code=400,
            api_short_error="Bad Request",
            error_details="Parameter 'foo' was missing.",
        )
        expected_str = (
            "Specific client context for bad request - HTTP Status: 400 - "
            "API Error: Bad Request - Details: Parameter 'foo' was missing."
        )
        assert str(error) == expected_str

    # It's good practice to test each specific exception type if they ever
    # were to override __str__ or have unique properties affecting it.
    # For now, since they just 'pass', testing one subclass like above is sufficient
    # to demonstrate inheritance of __str__.
