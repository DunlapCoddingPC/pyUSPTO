"""
base - Base client class for USPTO API clients

This module provides a base client class with common functionality for all USPTO API clients.
"""

import re
from pathlib import Path
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

from pyUSPTO.config import USPTOConfig
from pyUSPTO.exceptions import (
    APIErrorArgs,
    USPTOApiError,
    USPTOConnectionError,
    USPTOTimeout,
    get_api_exception,
)
from pyUSPTO.http_config import HTTPConfig


@runtime_checkable
class FromDictProtocol(Protocol):
    """Protocol for classes that can be created from a dictionary."""

    @classmethod
    def from_dict(cls, data: Dict[str, Any], include_raw_data: bool = False) -> Any:
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
        config: Optional[USPTOConfig] = None,
    ):
        """Initialize the BaseUSPTOClient.

        Args:
            api_key: API key for authentication
            base_url: The base URL of the API
            config: Optional USPTOConfig instance
        """
        # Handle config if provided
        if config:
            self.config = config
            self._api_key = api_key or config.api_key
        else:
            # Backward compatibility: create minimal config
            self.config = USPTOConfig(api_key=api_key)
            self._api_key = api_key

        self.base_url = base_url.rstrip("/")

        # Extract HTTP config for session creation
        self.http_config = self.config.http_config

        # Create session with HTTP config settings
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create configured HTTP session from HTTPConfig settings.

        Returns:
            Configured requests.Session instance
        """
        session = requests.Session()

        # Set API key and default headers
        if self._api_key:
            session.headers.update(
                {"X-API-KEY": self._api_key, "content-type": "application/json"}
            )

        # Apply custom headers from HTTP config
        if self.http_config.custom_headers:
            session.headers.update(self.http_config.custom_headers)

        # Configure retry strategy from HTTP config
        retry_strategy = Retry(
            total=self.http_config.max_retries,
            backoff_factor=self.http_config.backoff_factor,
            status_forcelist=self.http_config.retry_status_codes,
        )

        # Create adapter with retry and connection pool settings
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=self.http_config.pool_connections,
            pool_maxsize=self.http_config.pool_maxsize,
        )

        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        stream: bool = False,
        response_class: Optional[Type[T]] = None,
        custom_url: Optional[str] = None,
        custom_base_url: Optional[str] = None,
    ) -> Dict[str, Any] | T | requests.Response:
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
        url: str = ""
        if custom_url:
            url = custom_url
        else:
            base = custom_base_url if custom_base_url else self.base_url
            url = f"{base}/{endpoint.lstrip('/')}"

        # Get timeout from HTTP config
        timeout = self.http_config.get_timeout_tuple()

        try:
            if method.upper() == "GET":
                response = self.session.get(
                    url=url, params=params, stream=stream, timeout=timeout
                )
            elif method.upper() == "POST":
                response = self.session.post(
                    url=url,
                    params=params,
                    json=json_data,
                    stream=stream,
                    timeout=timeout,
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()

            # Return the raw response for streaming requests
            if stream:
                return response

            # Parse the response based on the specified class
            if response_class:
                parsed_response: T = response_class.from_dict(
                    response.json(), include_raw_data=self.config.include_raw_data
                )
                return parsed_response

            # Return the raw JSON for other requests
            json_response: Dict[str, Any] = response.json()
            return json_response

        except requests.exceptions.HTTPError as http_err:
            client_operation_message = f"API request to '{url}' failed with HTTPError"  # 'url' is from _make_request scope

            # Create APIErrorArgs directly from the HTTPError
            current_error_args = APIErrorArgs.from_http_error(
                http_error=http_err, client_operation_message=client_operation_message
            )

            api_exception_to_raise = get_api_exception(error_args=current_error_args)
            raise api_exception_to_raise from http_err

        except requests.exceptions.Timeout as timeout_err:
            # Specific handling for timeout errors
            raise USPTOTimeout(
                message=f"Request to '{url}' timed out",
                api_short_error="Timeout",
                error_details=str(timeout_err),
            ) from timeout_err

        except requests.exceptions.ConnectionError as conn_err:
            # Specific handling for connection errors (DNS, refused connection, etc.)
            raise USPTOConnectionError(
                message=f"Failed to connect to '{url}'",
                api_short_error="Connection Error",
                error_details=str(conn_err),
            ) from conn_err

        except (
            requests.exceptions.RequestException
        ) as req_err:  # Catches other non-HTTP errors from requests
            client_operation_message = (
                f"API request to '{url}' failed"  # 'url' is from _make_request scope
            )

            # Create APIErrorArgs from the generic RequestException
            current_error_args = APIErrorArgs.from_request_exception(
                request_exception=req_err,
                client_operation_message=client_operation_message,  # or pass None if you prefer default message
            )

            api_exception_to_raise = get_api_exception(
                current_error_args
            )  # Will default to USPTOApiError
            raise api_exception_to_raise from req_err

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

    @staticmethod
    def _extract_filename_from_content_disposition(
        content_disposition: Optional[str],
    ) -> Optional[str]:
        """Extract filename from Content-Disposition header.

        Supports both RFC 2231 (filename*) and simple filename formats.

        Args:
            content_disposition: The Content-Disposition header value.

        Returns:
            Optional[str]: The extracted filename, or None if not found.

        Examples:
            >>> _extract_filename_from_content_disposition('attachment; filename="document.pdf"')
            'document.pdf'
            >>> _extract_filename_from_content_disposition("attachment; filename*=UTF-8''file%20name.pdf")
            'file name.pdf'
        """
        if not content_disposition:
            return None

        # Try RFC 2231 format first (filename*=UTF-8''filename)
        rfc2231_match = re.search(
            r"filename\*=(?:UTF-8|utf-8)?''([^;\s]+)", content_disposition
        )
        if rfc2231_match:
            from urllib.parse import unquote

            return unquote(rfc2231_match.group(1))

        # Try standard filename="..." or filename=...
        filename_match = re.search(
            r'filename=(?:"([^"]+)"|([^;\s]+))', content_disposition
        )
        if filename_match:
            return filename_match.group(1) or filename_match.group(2)

        return None

    @staticmethod
    def _get_extension_from_mime_type(mime_type: Optional[str]) -> Optional[str]:
        """Map MIME type to file extension.

        Maps common USPTO file formats to their appropriate extensions.

        Args:
            mime_type: The MIME type from Content-Type header (e.g., "application/pdf").

        Returns:
            Optional[str]: File extension including dot (e.g., ".pdf"), or None if unmapped.

        Examples:
            >>> _get_extension_from_mime_type("application/pdf")
            '.pdf'
            >>> _get_extension_from_mime_type("image/tiff")
            '.tif'
            >>> _get_extension_from_mime_type("unknown/type")
            None
        """
        if not mime_type:
            return None

        # Normalize MIME type (remove charset and other parameters)
        mime_type = mime_type.split(";")[0].strip().lower()

        # Map of common USPTO file MIME types to extensions
        mime_to_ext = {
            "application/pdf": ".pdf",
            "image/tiff": ".tif",
            "image/tif": ".tif",
            "application/xml": ".xml",
            "text/xml": ".xml",
            "application/zip": ".zip",
        }

        return mime_to_ext.get(mime_type)

    def _save_response_to_file(
        self, response: requests.Response, file_path: str, overwrite: bool = False
    ) -> str:
        """Save a streaming response to a file on disk.

        If file_path is a directory, attempts to extract filename from
        Content-Disposition header and save in that directory.

        If file_path has no extension and Content-Disposition doesn't provide
        a filename, attempts to determine extension from Content-Type header.

        Args:
            response: Streaming response object from requests
            file_path: Local path where file should be saved. Can be a file path
                or a directory (in which case filename from Content-Disposition is used).
            overwrite: Whether to overwrite existing files. Default False

        Returns:
            str: Path to the saved file

        Raises:
            FileExistsError: If file exists and overwrite=False
            ValueError: If file_path is a directory but no filename can be determined
        """
        from pathlib import Path

        path = Path(file_path)

        # If path is a directory, try to extract filename from Content-Disposition
        if path.is_dir():
            content_disp = response.headers.get("Content-Disposition")
            filename = self._extract_filename_from_content_disposition(content_disp)
            if not filename:
                raise ValueError(
                    f"file_path is a directory ({file_path}) but Content-Disposition "
                    "header does not contain a filename. Please provide a full file path."
                )
            path = path / filename
        # If path has no extension, try to determine it from Content-Type
        elif not path.suffix:
            # Only attempt if Content-Disposition doesn't already provide filename
            content_disp = response.headers.get("Content-Disposition")
            if not self._extract_filename_from_content_disposition(content_disp):
                # Try to get extension from Content-Type header
                content_type = response.headers.get("Content-Type")
                extension = self._get_extension_from_mime_type(content_type)
                if extension:
                    path = path.with_suffix(extension)

        # Check for existing file
        if path.exists() and not overwrite:
            raise FileExistsError(
                f"File already exists: {path}. Set overwrite=True to replace."
            )

        # Save to disk with streaming
        with open(file=str(path), mode="wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # Filter out keep-alive chunks
                    f.write(chunk)
        return str(path)

    def _download_file(self, url: str, file_path: str, overwrite: bool = False) -> str:
        """Download a file directly to disk.

        Args:
            url: URL to download from
            file_path: Local path where file should be saved
            overwrite: Whether to overwrite existing files. Default False

        Returns:
            str: Path to the downloaded file

        Raises:
            HTTPError: If download request fails
            FileExistsError: If file exists and overwrite=False
        """
        # Always stream for file downloads (internal implementation detail)
        response = self._make_request(
            method="GET",
            endpoint="",  # Not used when custom_url is provided
            stream=True,
            custom_url=url,
        )

        if not isinstance(response, requests.Response):
            raise TypeError(
                f"Expected requests.Response for streaming download, got {type(response)}"
            )

        return self._save_response_to_file(
            response=response, file_path=file_path, overwrite=overwrite
        )

    @property
    def api_key(self) -> str:
        return "********"
