"""
Tests for the pyUSPTO.exceptions module.

This module contains tests for exception classes defined in pyUSPTO.exceptions.
"""

import pytest

from pyUSPTO.exceptions import (
    USPTOApiAuthError,
    USPTOApiBadRequestError,
    USPTOApiError,
    USPTOApiNotFoundError,
    USPTOApiPayloadTooLargeError,
    USPTOApiRateLimitError,
    USPTOApiServerError,
)


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
