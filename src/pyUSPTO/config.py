"""config - Configuration management for USPTO API clients.

This module provides configuration management for USPTO API clients,
including API keys, base URLs, and HTTP transport settings.
"""

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import requests

from pyUSPTO.http_config import HTTPConfig


class USPTOConfig:
    """Configuration for USPTO API clients.

    Manages API-level configuration (keys, URLs) and optionally
    accepts HTTP transport configuration via HTTPConfig.
    """

    def __init__(
        self,
        api_key: str | None = None,
        bulk_data_base_url: str = "https://api.uspto.gov",
        patent_data_base_url: str = "https://api.uspto.gov",
        petition_decisions_base_url: str = "https://api.uspto.gov",
        ptab_base_url: str = "https://api.uspto.gov",
        http_config: HTTPConfig | None = None,
        include_raw_data: bool = False,
    ):
        """Initialize the USPTOConfig.

        Args:
            api_key: API key for authentication, defaults to USPTO_API_KEY environment variable
            bulk_data_base_url: Base URL for the Bulk Data API
            patent_data_base_url: Base URL for the Patent Data API
            petition_decisions_base_url: Base URL for the Final Petition Decisions API
            ptab_base_url: Base URL for the PTAB (Patent Trial and Appeal Board) API
            http_config: Optional HTTPConfig for request handling (uses defaults if None)
            include_raw_data: If True, store raw JSON in response objects for debugging (default: False)
        """
        # Use environment variable only if api_key is None, not if it's an empty string
        self.api_key = (
            api_key if api_key is not None else os.environ.get("USPTO_API_KEY")
        )
        self.bulk_data_base_url = bulk_data_base_url
        self.patent_data_base_url = patent_data_base_url
        self.petition_decisions_base_url = petition_decisions_base_url
        self.ptab_base_url = ptab_base_url

        # Use provided HTTPConfig or create default
        self.http_config = http_config if http_config is not None else HTTPConfig()

        # Control whether to include raw JSON data in response objects
        self.include_raw_data = include_raw_data

        # Session for all clients using this config (created lazily)
        self._session: requests.Session | None = None

    @classmethod
    def from_env(cls) -> "USPTOConfig":
        """Create a USPTOConfig from environment variables.

        Returns:
            USPTOConfig instance with values from environment
        """
        return cls(
            api_key=os.environ.get("USPTO_API_KEY"),
            bulk_data_base_url=os.environ.get(
                "USPTO_BULK_DATA_BASE_URL", "https://api.uspto.gov"
            ),
            patent_data_base_url=os.environ.get(
                "USPTO_PATENT_DATA_BASE_URL", "https://api.uspto.gov"
            ),
            petition_decisions_base_url=os.environ.get(
                "USPTO_PETITION_DECISIONS_BASE_URL", "https://api.uspto.gov"
            ),
            ptab_base_url=os.environ.get(
                "USPTO_PTAB_BASE_URL", "https://api.uspto.gov"
            ),
            # Also read HTTP config from environment
            http_config=HTTPConfig.from_env(),
        )

    @property
    def session(self) -> "requests.Session":
        """Get the HTTP session for this config, creating it if needed.

        The session is created lazily on first access and reused for all
        subsequent requests. All clients sharing this config will use the
        same session for connection pooling.

        Returns:
            Session: The requests Session object with configured adapters.
        """
        if self._session is None:
            self._session = self._create_session()
        return self._session

    def _create_session(self) -> "requests.Session":
        """Create and configure a new requests Session.

        Returns:
            Session: Configured session with retry logic and connection pooling.
        """
        from requests import Session
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry

        session = Session()

        # Set API key header
        if self.api_key:
            session.headers["X-API-KEY"] = self.api_key

        # Apply custom headers from HTTP config
        if self.http_config.custom_headers:
            session.headers.update(self.http_config.custom_headers)

        # Configure retry strategy
        retry_strategy = Retry(
            total=self.http_config.max_retries,
            backoff_factor=self.http_config.backoff_factor,
            status_forcelist=self.http_config.retry_status_codes,
        )

        # Configure connection pooling
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=self.http_config.pool_connections,
            pool_maxsize=self.http_config.pool_maxsize,
        )

        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def close(self) -> None:
        """Close the HTTP session and release resources.

        This should be called when you're done using this config and all
        clients created from it. After calling close(), the session will
        be recreated if accessed again.

        Example:
            config = USPTOConfig(api_key="...")
            client = PatentDataClient(config=config)
            try:
                # Use client
                pass
            finally:
                config.close()
        """
        if self._session is not None:
            self._session.close()
            self._session = None

    def __enter__(self) -> "USPTOConfig":
        """Enter context manager."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        """Exit context manager, closing the session."""
        self.close()
