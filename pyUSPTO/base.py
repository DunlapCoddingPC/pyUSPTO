"""
base - Base client class for USPTO API clients

This module provides a base client class with common functionality for all USPTO API clients.
"""

from typing import (
    Any,
    Dict,
    Generator,
    Generic,
    Optional,
    Protocol,
    Type,
    TypeVar,
    Union,
    runtime_checkable,
)
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from pyUSPTO.exceptions import (
    USPTOApiAuthError,
    USPTOApiError,
    USPTOApiNotFoundError,
    USPTOApiRateLimitError,
    USPTOApiBadRequestError,
    USPTOApiPayloadTooLargeError,
    USPTOApiServerError,
)


@runtime_checkable
class FromDictProtocol(Protocol):
    """Protocol for classes that can be created from a dictionary."""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Any:
        """Create an object from a dictionary."""
        ...


# Type variable for response classes
T = TypeVar("T", bound=FromDictProtocol)


class BaseUSPTOClient(Generic[T]):
    """Base client class for USPTO API clients."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "",
    ):
        """
        Initialize the BaseUSPTOClient.

        Args:
            api_key: API key for authentication
            base_url: The base URL of the API
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()

        if api_key:
            self.session.headers.update(
                {"X-API-KEY": api_key, "content-type": "application/json"}
            )

        # Configure retries
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        stream: bool = False,
        response_class: Optional[Type[T]] = None,
        custom_base_url: Optional[str] = None,
    ) -> Union[Dict[str, Any], T, requests.Response]:
        """
        Make an HTTP request to the USPTO API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path (without base URL)
            params: Optional query parameters
            json_data: Optional JSON body for POST requests
            stream: Whether to stream the response
            response_class: Class to use for parsing the response
            custom_base_url: Optional custom base URL to use instead of self.base_url

        Returns:
            Response data in the appropriate format:
            - If stream=True: requests.Response object
            - If response_class is provided: Instance of response_class
            - Otherwise: Dict[str, Any] containing the JSON response
        """
        base = custom_base_url if custom_base_url else self.base_url
        url = f"{base}/{endpoint.lstrip('/')}"

        try:
            if method.upper() == "GET":
                response = self.session.get(url=url, params=params, stream=stream)
            elif method.upper() == "POST":
                response = self.session.post(
                    url=url, params=params, json=json_data, stream=stream
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()

            # Return the raw response for streaming requests
            if stream:
                return response

            # Parse the response based on the specified class
            if response_class:
                parsed_response: T = response_class.from_dict(response.json())
                return parsed_response

            # Return the raw JSON for other requests
            json_response: Dict[str, Any] = response.json()
            return json_response

        except requests.exceptions.HTTPError as e:
            # Map HTTP errors to custom exceptions
            status_code = e.response.status_code

            # Attempt to parse the error response for additional details
            error_details = None
            request_identifier = None

            try:
                error_data = e.response.json()
                error_details = error_data.get("errorDetails") or error_data.get(
                    "detailedError"
                )
                request_identifier = error_data.get("requestIdentifier")
            except (ValueError, KeyError):
                # If we can't parse the error response, proceed with basic info
                pass

            # Create the appropriate error message
            error_message = f"API Error {status_code}"
            if error_details:
                error_message = f"{error_message}: {error_details}"

            # Map specific status codes to appropriate exception classes
            if status_code == 400:
                raise USPTOApiBadRequestError(
                    error_message, status_code, error_details, request_identifier
                ) from e
            elif status_code in (401, 403):
                raise USPTOApiAuthError(
                    error_message, status_code, error_details, request_identifier
                ) from e
            elif status_code == 404:
                raise USPTOApiNotFoundError(
                    error_message, status_code, error_details, request_identifier
                ) from e
            elif status_code == 413:
                raise USPTOApiPayloadTooLargeError(
                    error_message, status_code, error_details, request_identifier
                ) from e
            elif status_code == 429:
                raise USPTOApiRateLimitError(
                    error_message, status_code, error_details, request_identifier
                ) from e
            elif status_code >= 500:
                raise USPTOApiServerError(
                    error_message, status_code, error_details, request_identifier
                ) from e
            else:
                # For any other status codes, use the base USPTOApiError
                raise USPTOApiError(
                    error_message, status_code, error_details, request_identifier
                ) from e
        except requests.exceptions.RequestException as e:
            # Re-raise other request exceptions as USPTOApiError
            raise USPTOApiError(f"Request failed: {str(e)}") from e

    def paginate_results(
        self, method_name: str, response_container_attr: str, **kwargs: Any
    ) -> Generator[Any, None, None]:
        """
        Paginate through all results of a method.

        Args:
            method_name: Name of the method to call
            response_container_attr: Attribute name of the container in the response
            **kwargs: Keyword arguments to pass to the method

        Yields:
            Items from the response container
        """
        offset = kwargs.get("offset", 0)
        limit = kwargs.get("limit", 25)

        while True:
            kwargs["offset"] = offset
            kwargs["limit"] = limit

            method = getattr(self, method_name)
            response = method(**kwargs)

            if not response.count:
                break

            container = getattr(response, response_container_attr)
            for item in container:
                yield item

            if response.count < limit:
                break

            offset += limit
