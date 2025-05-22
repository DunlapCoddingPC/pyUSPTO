"""
config - Configuration management for USPTO API clients

This module provides configuration management for USPTO API clients.
"""

import os
from typing import Optional


class USPTOConfig:
    """Configuration for USPTO API clients."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        bulk_data_base_url: str = "https://api.uspto.gov",
        patent_data_base_url: str = "https://api.uspto.gov",
    ):
        """
        Initialize the USPTOConfig.

        Args:
            api_key: API key for authentication, defaults to USPTO_API_KEY environment variable
            bulk_data_base_url: Base URL for the Bulk Data API
            patent_data_base_url: Base URL for the Patent Data API
        """
        # Use environment variable only if api_key is None, not if it's an empty string
        self.api_key = (
            api_key if api_key is not None else os.environ.get("USPTO_API_KEY")
        )
        self.bulk_data_base_url = bulk_data_base_url
        self.patent_data_base_url = patent_data_base_url

    @classmethod
    def from_env(cls) -> "USPTOConfig":
        """
        Create a USPTOConfig from environment variables.

        Returns:
            USPTOConfig instance
        """
        return cls(
            api_key=os.environ.get("USPTO_API_KEY"),
            bulk_data_base_url=os.environ.get(
                "USPTO_BULK_DATA_BASE_URL", "https://api.uspto.gov"
            ),
            patent_data_base_url=os.environ.get(
                "USPTO_PATENT_DATA_BASE_URL", "https://api.uspto.gov"
            ),
        )
