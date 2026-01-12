"""base - Base client class for USPTO API clients.

This module provides a base client class with common functionality for all USPTO API clients.
"""

import re
from collections.abc import Generator
from pathlib import Path
from typing import (
    Any,
    Generic,
    Protocol,
    TypeVar,
    runtime_checkable,
)

import requests

from pyUSPTO.config import USPTOConfig
from pyUSPTO.exceptions import (
    APIErrorArgs,
    USPTOApiResponseParseError,
    USPTOConnectionError,
    USPTOTimeout,
    get_api_exception,
)


@runtime_checkable
class FromDictProtocol(Protocol):
    """Protocol for classes that can be created from a dictionary."""

    @classmethod
    def from_dict(cls, data: dict[str, Any], include_raw_data: bool = False) -> Any:
        """Create an object from a dictionary."""
        ...


# Type variable for response classes
T = TypeVar("T", bound=FromDictProtocol)


class BaseUSPTOClient(Generic[T]):
    """Base client class for USPTO API clients."""

    def __init__(
        self,
        base_url: str = "",
        config: USPTOConfig | None = None,
    ):
        """Initialize the BaseUSPTOClient.

        Args:
            base_url: The base URL of the API
            config: USPTOConfig instance containing API key and HTTP settings.
                When multiple clients share the same config object, they automatically
                share an HTTP session for better performance and connection pooling.
                If not provided, creates a default config (requires USPTO_API_KEY
                environment variable).
        """
        # Use provided config or create default from environment
        if config is None:
            self.config = USPTOConfig.from_env()
        else:
            self.config = config

        # Store API key and HTTP config from config
        self._api_key = self.config.api_key
        self.http_config = self.config.http_config

        self.base_url = base_url.rstrip("/")

        # No session creation here - clients use config's session
        # Session is accessed via property: self.session -> self.config.session

    @property
    def session(self) -> requests.Session:
        """Get the HTTP session from config.

        Returns:
            Session: The requests Session configured by this client's config.
        """
        return self.config.session

    def close(self) -> None:
        """Close the client and release resources.

        Note: This method does NOT close the HTTP session, as clients do not
        own sessions. To close the session, call close() on the USPTOConfig
        object that was used to create this client.

        Example:
            config = USPTOConfig(api_key="...")
            client = PatentDataClient(config=config)
            try:
                # Use client
                pass
            finally:
                config.close()  # Close config, not client
        """
        # Nothing to do - client doesn't own any resources
        pass

    def __enter__(self) -> "BaseUSPTOClient[T]":
        """Enter context manager, returning the client instance.

        Returns:
            Self for use in with statements

        Example:
            config = USPTOConfig(api_key="...")
            with PatentDataClient(config=config) as client:
                response = client.search_applications(...)
        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any | None,
    ) -> None:
        """Exit context manager.

        Note: Does not close the session. Use context manager on
        USPTOConfig instead if session cleanup is needed.
        """
        # Nothing to close - client doesn't own session
        pass

    def _parse_json_response(
        self, response: requests.Response, url: str
    ) -> dict[str, Any]:
        """Parse JSON response with proper error handling.

        Args:
            response: The requests Response object to parse
            url: The URL that was requested (for error messages)

        Returns:
            Parsed JSON as a dictionary

        Raises:
            USPTOApiResponseParseError: If the response cannot be parsed as JSON
        """
        try:
            json_data: dict[str, Any] = response.json()
            return json_data
        except (ValueError, requests.exceptions.JSONDecodeError) as json_err:
            # Get content-type header to provide better error context
            content_type = response.headers.get("content-type", "unknown")

            # Truncate response text for error message if it's too long
            response_preview = response.text[:500] if response.text else "(empty)"
            if len(response.text) > 500:
                response_preview += "... (truncated)"

            raise USPTOApiResponseParseError(
                message=f"Failed to parse JSON response from '{url}'",
                status_code=response.status_code,
                api_short_error="JSON Parse Error",
                error_details=(
                    f"Response Content-Type: {content_type}\n"
                    f"Parse error: {str(json_err)}\n"
                    f"Response preview: {response_preview}"
                ),
            ) from json_err

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        stream: bool = False,
        response_class: type[T] | None = None,
        custom_url: str | None = None,
        custom_base_url: str | None = None,
    ) -> dict[str, Any] | T | requests.Response:
        """Make an HTTP request to the USPTO API.

        Note: Only GET and POST methods are supported. Other HTTP methods will
        raise a ValueError.

        Args:
            method: HTTP method (GET or POST only)
            endpoint: API endpoint path (without base URL)
            params: Optional query parameters
            json_data: Optional JSON body for POST requests
            stream: Whether to stream the response
            response_class: Class to use for parsing the response
            custom_url: Optional full custom URL to use (overrides endpoint and base URL)
            custom_base_url: Optional custom base URL to use instead of self.base_url

        Returns:
            Response data in the appropriate format:
            - If stream=True: requests.Response object
            - If response_class is provided: Instance of response_class
            - Otherwise: Dict[str, Any] containing the JSON response

        Raises:
            ValueError: If an unsupported HTTP method is provided
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

            # Parse JSON response with error handling
            json_data = self._parse_json_response(response, url)

            # Parse the response based on the specified class
            if response_class:
                parsed_response: T = response_class.from_dict(
                    json_data, include_raw_data=self.config.include_raw_data
                )
                return parsed_response

            # Return the raw JSON for other requests
            return json_data

        except requests.exceptions.HTTPError as http_err:
            client_operation_message = f"API request to '{url}' failed with HTTPError"  # 'url' is from _make_request scope

            # Include request body for POST debugging
            if method.upper() == "POST" and json_data:
                import json

                client_operation_message += (
                    f"\nRequest body sent:\n{json.dumps(json_data, indent=2)}"
                )

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
        self,
        method_name: str,
        response_container_attr: str,
        post_body: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Generator[Any, None, None]:
        """Paginate through all results of a method, supporting both GET and POST.

        Args:
            method_name: Name of the method to call
            response_container_attr: Attribute name of the container in the response
            post_body: Optional POST body for POST-based pagination. If provided,
                pagination parameters (offset, limit) will be injected into this body.
            **kwargs: Keyword arguments to pass to the method (for GET pagination)

        Yields:
            Items from the response container

        Raises:
            ValueError: If offset is provided in kwargs or post_body (offset is managed
                automatically by pagination)

        Examples:
            # GET pagination
            for app in client.paginate_results(
                "search_applications",
                "patent_file_wrapper_data_bag",
                query="test"
            ):
                print(app)

            # POST pagination with custom limit
            for app in client.paginate_results(
                "search_applications",
                "patent_file_wrapper_data_bag",
                post_body={"q": "test", "limit": 50}
            ):
                print(app)
        """
        # Determine if POST body uses nested pagination structure
        uses_nested_pagination = False
        if post_body is not None:
            uses_nested_pagination = "pagination" in post_body and isinstance(
                post_body["pagination"], dict
            )

        # Validate that offset is not provided by the user
        if post_body is not None:
            if uses_nested_pagination:
                # Check nested pagination object
                if "offset" in post_body["pagination"]:
                    raise ValueError(
                        "Cannot specify 'offset' in post_body['pagination']. "
                        "Pagination manages offset automatically."
                    )
                limit = post_body["pagination"].get("limit", 25)
            else:
                # Check top-level
                if "offset" in post_body:
                    raise ValueError(
                        "Cannot specify 'offset' in post_body. Pagination manages offset automatically."
                    )
                limit = post_body.get("limit", 25)
        else:
            if "offset" in kwargs:
                raise ValueError(
                    "Cannot specify 'offset' in kwargs. Pagination manages offset automatically."
                )
            limit = kwargs.get("limit", 25)

        offset = 0

        while True:
            # Prepare parameters based on request type
            if post_body is not None:
                # POST request: update body with pagination params
                current_body = post_body.copy()

                if uses_nested_pagination:
                    # Update nested pagination object
                    current_body["pagination"] = current_body["pagination"].copy()
                    current_body["pagination"]["offset"] = offset
                    current_body["pagination"]["limit"] = limit
                else:
                    # Update top-level pagination params
                    current_body["offset"] = offset
                    current_body["limit"] = limit

                method = getattr(self, method_name)
                response = method(post_body=current_body, **kwargs)
            else:
                # GET request: update kwargs with pagination params
                kwargs["offset"] = offset
                kwargs["limit"] = limit

                method = getattr(self, method_name)
                response = method(**kwargs)

            # Validate response has required pagination attributes
            if not hasattr(response, "count"):
                raise AttributeError(
                    f"Response from '{method_name}' missing required 'count' attribute for pagination"
                )

            if response.count is None:
                # count=None means no results, stop pagination
                break

            if not response.count:
                # count=0 means no results, stop pagination
                break

            # Validate container attribute exists
            if not hasattr(response, response_container_attr):
                raise AttributeError(
                    f"Response from '{method_name}' missing required '{response_container_attr}' "
                    f"attribute for pagination"
                )

            container = getattr(response, response_container_attr)

            # Validate container is iterable
            if container is None:
                raise ValueError(
                    f"Container '{response_container_attr}' is None in response from '{method_name}'"
                )

            yield from container

            if response.count < limit + offset:
                break

            offset += limit

    @staticmethod
    def _extract_filename_from_content_disposition(
        content_disposition: str | None,
    ) -> str | None:
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
    def _get_extension_from_mime_type(mime_type: str | None) -> str | None:
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
            "application/x-tar": ".tar",
            "application/gzip": ".tar.gz",
            "application/octet-stream": "",
        }

        return mime_to_ext.get(mime_type)

    def _save_response_to_file(
        self,
        response: requests.Response,
        destination: str | None = None,
        file_name: str | None = None,
        overwrite: bool = False,
    ) -> str:
        """Save streaming response to file.

        Args:
            response: Streaming HTTP response
            destination: Directory to save to (default: current directory)
            file_name: Override filename (default: from Content-Disposition)
            overwrite: Overwrite existing file

        Returns:
            Path to saved file

        Raises:
            FileExistsError: If file exists and overwrite is False
        """
        filename: str | None = None

        if file_name:
            filename = file_name
        else:
            content_disp = response.headers.get("Content-Disposition")
            filename = self._extract_filename_from_content_disposition(content_disp)
            if not filename:
                # Try to extract filename from URL
                from urllib.parse import unquote, urlparse

                url_path = urlparse(response.url).path
                url_filename = unquote(url_path.split("/")[-1]) if url_path else None

                if url_filename and "." in url_filename:
                    filename = url_filename
                elif url_filename:
                    filename = url_filename
                    content_type = response.headers.get("Content-Type")
                    ext = self._get_extension_from_mime_type(content_type)
                    if ext:
                        filename += ext
                else:
                    filename = "download"

        if destination:
            dest_path = Path(destination)
            dest_path.mkdir(parents=True, exist_ok=True)
            final_path = dest_path / filename
        else:
            final_path = Path.cwd() / filename

        if final_path.exists() and not overwrite:
            raise FileExistsError(f"File exists: {final_path}. Use overwrite=True")

        with open(final_path, "wb") as f:
            for chunk in response.iter_content(
                chunk_size=self.http_config.download_chunk_size
            ):
                if chunk:
                    f.write(chunk)

        return str(final_path)

    def _extract_archive(
        self,
        archive_path: Path,
        extract_to: Path | None = None,
        remove_archive: bool = False,
    ) -> str:
        """Extract TAR or ZIP archive.

        Args:
            archive_path: Path to archive file
            extract_to: Directory to extract to (default: archive_path.stem)
            remove_archive: Delete archive after extraction

        Returns:
            Path to extracted content (single file: path to file, multiple files: directory path)

        Raises:
            ValueError: If file is not a valid TAR or ZIP archive
        """
        import tarfile
        import zipfile

        if extract_to is None:
            extract_to = archive_path.parent / archive_path.stem

        extract_to.mkdir(parents=True, exist_ok=True)

        extracted_items = []
        if tarfile.is_tarfile(archive_path):
            with tarfile.open(archive_path, "r:*") as tar:
                tar.extractall(path=extract_to)
                extracted_items = [m.name for m in tar.getmembers() if m.isfile()]
        elif zipfile.is_zipfile(archive_path):
            with zipfile.ZipFile(archive_path, "r") as zip_ref:
                zip_ref.extractall(extract_to)
                extracted_items = [n for n in zip_ref.namelist() if not n.endswith("/")]
        else:
            raise ValueError(f"Not a valid TAR/ZIP archive: {archive_path}")

        if remove_archive:
            archive_path.unlink()

        if len(extracted_items) == 1:
            return str(extract_to / extracted_items[0])
        else:
            return str(extract_to)

    def _download_and_extract(
        self,
        url: str,
        destination: str | None = None,
        file_name: str | None = None,
        overwrite: bool = False,
    ) -> str:
        """Download file and auto-extract if it's an archive.

        Args:
            url: URL to download
            destination: Directory to save/extract to
            file_name: Override filename
            overwrite: Overwrite existing files

        Returns:
            Path to extracted content (file or directory)

        Raises:
            TypeError: If response is not a valid Response object
            FileExistsError: If file exists and overwrite is False
            ValueError: If downloaded file is not a valid archive when extraction attempted
        """
        import tarfile
        import zipfile

        downloaded_path = self._download_file(
            url=url, destination=destination, file_name=file_name, overwrite=overwrite
        )

        path_obj = Path(downloaded_path)
        is_archive = (
            path_obj.suffix.lower() in [".tar", ".tgz", ".gz", ".zip"]
            or tarfile.is_tarfile(path_obj)
            or zipfile.is_zipfile(path_obj)
        )

        if is_archive:
            return self._extract_archive(path_obj, remove_archive=True)
        else:
            return downloaded_path

    def _download_file(
        self,
        url: str,
        destination: str | None = None,
        file_name: str | None = None,
        overwrite: bool = False,
    ) -> str:
        """Download file to disk (NO extraction).

        Args:
            url: URL to download
            destination: Directory to save to
            file_name: Override filename
            overwrite: Overwrite existing files

        Returns:
            Path to downloaded file

        Raises:
            TypeError: If response is not a valid Response object
            FileExistsError: If file exists and overwrite is False
        """
        response = self._make_request(
            method="GET",
            endpoint="",
            stream=True,
            custom_url=url,
        )

        if not isinstance(response, requests.Response):
            raise TypeError(f"Expected Response, got {type(response)}")

        return self._save_response_to_file(
            response=response,
            destination=destination,
            file_name=file_name,
            overwrite=overwrite,
        )

    @property
    def api_key(self) -> str:
        """Return a masked representation of the API key for security purposes.

        Returns:
            str: A string of asterisks masking the actual API key.
        """
        return "********"
