"""
config - Configuration management for USPTO API clients

This module provides configuration management for USPTO API clients,
including API keys, base URLs, and HTTP transport settings.
"""

import os
from typing import Optional

from pyUSPTO.http_config import HTTPConfig


class USPTOConfig:
    """Configuration for USPTO API clients.

    Manages API-level configuration (keys, URLs) and optionally
    accepts HTTP transport configuration via HTTPConfig.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        bulk_data_base_url: str = "https://api.uspto.gov",
        patent_data_base_url: str = "https://api.uspto.gov",
        petition_decisions_base_url: str = "https://api.uspto.gov",
        http_config: Optional[HTTPConfig] = None,
    ):
        """Initialize the USPTOConfig.

        Args:
            api_key: API key for authentication, defaults to USPTO_API_KEY environment variable
            bulk_data_base_url: Base URL for the Bulk Data API
            patent_data_base_url: Base URL for the Patent Data API
            petition_decisions_base_url: Base URL for the Final Petition Decisions API
            http_config: Optional HTTPConfig for request handling (uses defaults if None)
        """
        # Use environment variable only if api_key is None, not if it's an empty string
        self.api_key = (
            api_key if api_key is not None else os.environ.get("USPTO_API_KEY")
        )
        self.bulk_data_base_url = bulk_data_base_url
        self.patent_data_base_url = patent_data_base_url
        self.petition_decisions_base_url = petition_decisions_base_url

        # Use provided HTTPConfig or create default
        self.http_config = http_config if http_config is not None else HTTPConfig()

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
            # Also read HTTP config from environment
            http_config=HTTPConfig.from_env(),
        )
