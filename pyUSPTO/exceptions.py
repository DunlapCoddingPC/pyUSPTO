"""
exceptions - Exception classes for USPTO API clients

This module provides exception classes for USPTO API errors that correspond to
the various response types from the USPTO API. It also includes helper
structures and functions for creating these exceptions.
"""

from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Optional, Type, Union

# To avoid circular imports if requests is type-hinted directly,
# use TYPE_CHECKING guard or a string literal for the type hint.
if TYPE_CHECKING:
    import requests  # requests.exceptions.HTTPError


# --- Exception Classes (largely unchanged) ---
class USPTOApiError(Exception):
    """Base exception for USPTO API errors.
    This is the parent class for all USPTO API-specific exceptions. It includes
    information about the status code, API's short error message, detailed error
    information, and request identifier from the API response.
    """

    DEFAULT_UNKNOWN_MESSAGE = "UNK USPTO API ERROR"

    def __init__(
        self,
        message: str,  # Primary client-facing message for the exception context
        status_code: Optional[int] = None,
        api_short_error: Optional[
            str
        ] = None,  # From API 'error' or 'message' (for 413) field
        error_details: Optional[
            Union[str, dict]
        ] = None,  # From API 'errorDetails' or 'detailedMessage' field
        request_identifier: Optional[str] = None,
    ):
        """
        Initializes the USPTOApiError.
        Args:
            message: The primary message for the exception (often client-generated context).
            status_code: The HTTP status code from the API response (e.g., 400, 403).
            api_short_error: The short error description from the API (e.g., "Bad Request", "Forbidden").
            error_details: The detailed error message or structure from the API.
            request_identifier: The request identifier from the API response, if available.
        """
        effective_message = message if message else self.DEFAULT_UNKNOWN_MESSAGE
        super().__init__(effective_message)
        self.status_code = status_code
        self.api_short_error = api_short_error
        self.error_details = error_details
        self.request_identifier = request_identifier

    @property
    def message(self) -> str:
        """
        Provides direct access to the primary exception message.
        This refers to the first argument passed to the exception,
        which is conventionally the main human-readable message.
        """
        return str(object=self.args[0])

    def __str__(self) -> str:
        """Provides a more informative string representation of the error."""
        parts = [super().__str__()]

        if self.status_code:
            parts.append(f"HTTP Status: {self.status_code}")

        if self.api_short_error:
            parts.append(f"API Error: {self.api_short_error}")

        if self.error_details:
            details_str = str(self.error_details)
            parts.append(f"Details: {details_str}")

        if self.request_identifier:
            parts.append(f"Request ID: {self.request_identifier}")

        if len(parts) > 1:
            return " - ".join(filter(None, parts))
        else:
            return parts[0]


class USPTOApiBadRequestError(USPTOApiError):
    """Bad Request error (HTTP 400)."""

    pass


class USPTOApiAuthError(USPTOApiError):
    """Authentication/Authorization error (HTTP 401/403)."""

    pass


class USPTOApiRateLimitError(USPTOApiError):
    """Rate limit exceeded error (HTTP 429)."""

    pass


class USPTOApiNotFoundError(USPTOApiError):
    """Resource not found error (HTTP 404)."""

    pass


class USPTOApiPayloadTooLargeError(USPTOApiError):
    """Payload Too Large error (HTTP 413)."""

    pass


class USPTOApiServerError(USPTOApiError):
    """Internal Server Error (HTTP 500 series)."""

    pass


# --- Helper Structures and Functions ---


@dataclass
class APIErrorArgs:
    """Data structure to hold arguments for API exception constructors."""

    message: str
    status_code: Optional[int] = None
    api_short_error: Optional[str] = None
    error_details: Optional[Union[str, dict]] = None
    request_identifier: Optional[str] = None

    @classmethod
    def from_http_error(
        cls,
        http_error: "requests.exceptions.HTTPError",  # String literal for type hint
        client_operation_message: str,
    ) -> "APIErrorArgs":
        """
        Creates an APIErrorArgs instance by parsing a requests.exceptions.HTTPError.

        Args:
            http_error: The HTTPError object from the requests library.
            client_operation_message: A message describing the client operation that failed.

        Returns:
            An instance of APIErrorArgs populated with details from the HTTPError.
        """
        status_code = http_error.response.status_code

        api_short_error_from_response = None
        error_details_from_response = None
        request_identifier_from_response = None

        try:
            error_data = http_error.response.json()
            if status_code == 413:
                api_short_error_from_response = error_data.get("message")
                error_details_from_response = error_data.get("detailedMessage")
            else:
                api_short_error_from_response = error_data.get("error")
                error_details_from_response = error_data.get("errorDetails")
            request_identifier_from_response = error_data.get("requestIdentifier")
        except ValueError:  # If response.json() fails (e.g., not JSON)
            pass  # Values remain None

        # Fallback for api_short_error if not found in JSON response
        if not api_short_error_from_response and http_error.response.reason:
            api_short_error_from_response = http_error.response.reason

        # Fallback for error_details if not found in JSON and response text is available
        if not error_details_from_response and http_error.response.text:
            # Avoid setting very long HTML pages as error_details if JSON parsing failed
            if (
                "content-type" in http_error.response.headers
                and "application/json"
                not in http_error.response.headers.get("content-type", "").lower()
            ):
                if len(http_error.response.text) > 500:  # Heuristic for "too long"
                    error_details_from_response = f"Non-JSON error response (status {status_code}). Check response text."
                else:
                    error_details_from_response = http_error.response.text
            elif (
                http_error.response.text
            ):  # If it might have been JSON but parsing failed
                error_details_from_response = http_error.response.text

        return cls(
            message=client_operation_message,
            status_code=status_code,
            api_short_error=api_short_error_from_response,
            error_details=error_details_from_response,
            request_identifier=request_identifier_from_response,
        )

    @classmethod
    def from_request_exception(
        cls,
        request_exception: "requests.exceptions.RequestException",  # String for type hint
        client_operation_message: Optional[str] = None,
    ) -> "APIErrorArgs":
        """
        Creates an APIErrorArgs instance from a generic requests.exceptions.RequestException
        (e.g., ConnectionError, Timeout) that is not an HTTPError.
        """
        message_prefix = client_operation_message or "API request failed"
        return cls(
            message=f"{message_prefix} due to a network or request issue: {str(request_exception)}"
            # status_code, api_short_error, etc., will be None
        )


def get_api_exception(error_args: APIErrorArgs) -> USPTOApiError:
    """
    Determines and instantiates the appropriate USPTOApiError subclass
    based on the status code in error_args.

    Args:
        error_args: An instance of APIErrorArgs containing all necessary
                    information to construct the exception.

    Returns:
        An instance of a USPTOApiError subclass.
    """
    status_code = error_args.status_code
    exception_class: Type[USPTOApiError]

    match status_code:
        case 400:
            exception_class = USPTOApiBadRequestError
        case 401 | 403:
            exception_class = USPTOApiAuthError
        case 404:
            exception_class = USPTOApiNotFoundError
        case 413:
            exception_class = USPTOApiPayloadTooLargeError
        case 429:
            exception_class = USPTOApiRateLimitError
        case _ if status_code is not None and status_code >= 500:
            exception_class = USPTOApiServerError
        case (
            _
        ):  # Default for other errors or if status_code is None (e.g. network error)
            exception_class = USPTOApiError

    return exception_class(**asdict(error_args))
