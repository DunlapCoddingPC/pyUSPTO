"""
exceptions - Exception classes for USPTO API clients

This module provides exception classes for USPTO API errors that correspond to
the various response types from the USPTO API.
"""

from typing import Optional


class USPTOApiError(Exception):
    """Base exception for USPTO API errors.

    This is the parent class for all USPTO API-specific exceptions. It includes
    information about the status code, error details, and request identifier
    from the API response.
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        error_details: Optional[str] = None,
        request_identifier: Optional[str] = None,
    ):
        self.status_code = status_code
        self.error_details = error_details
        self.request_identifier = request_identifier
        super().__init__(message)


class USPTOApiBadRequestError(USPTOApiError):
    """Bad Request error (HTTP 400).

    Raised when the API returns a 400 status code, indicating that the request
    was invalid. This can happen due to invalid parameters, incorrect query syntax,
    or other client-side errors in the request format.
    """

    pass


class USPTOApiAuthError(USPTOApiError):
    """Authentication/Authorization error (HTTP 403).

    Raised when the API returns a 403 status code, indicating an issue with
    authentication. This typically happens when the API key is missing,
    invalid, or doesn't have permission to access the requested resource.
    """

    pass


class USPTOApiRateLimitError(USPTOApiError):
    """Rate limit exceeded error.

    Raised when the API rate limits have been exceeded. The USPTO API enforces
    rate limits to prevent excessive usage. Details about these limits can be
    found at https://data.uspto.gov/apis/api-rate-limits.
    """

    pass


class USPTOApiNotFoundError(USPTOApiError):
    """Resource not found error (HTTP 404).

    Raised when the API returns a 404 status code, indicating that the
    requested resource does not exist. This can happen when searching for
    a specific patent application that doesn't exist, or when using an
    invalid endpoint.
    """

    pass


class USPTOApiPayloadTooLargeError(USPTOApiError):
    """Payload Too Large error (HTTP 413).

    Raised when the API returns a 413 status code, indicating that the response
    payload exceeds the allowed limit (typically 6MB). In this case, the client
    should refine their search criteria or reduce the requested data size.
    """

    pass


class USPTOApiServerError(USPTOApiError):
    """Internal Server Error (HTTP 500).

    Raised when the API returns a 500 status code, indicating that an error
    occurred on the server side. These errors are not related to the client's
    request and typically require contacting the USPTO Help Desk for resolution.
    """

    pass
