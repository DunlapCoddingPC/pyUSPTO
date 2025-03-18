"""
Tests for edge cases in the USPTOConfig class.

This module contains tests for edge cases and error handling in USPTOConfig.
"""

from unittest.mock import patch

from pyUSPTO.config import USPTOConfig


def test_config_with_empty_api_key() -> None:
    """Test creating a config with an empty API key."""
    # Empty string API key
    config = USPTOConfig(api_key="")
    assert config.api_key == ""

    # None API key should fall back to environment variable
    with patch.dict("os.environ", {"USPTO_API_KEY": "env_key"}, clear=True):
        config = USPTOConfig(api_key=None)
        assert config.api_key == "env_key"

    # No API key and no environment variable
    with patch.dict("os.environ", {}, clear=True):
        config = USPTOConfig()
        assert config.api_key is None


def test_from_env_with_missing_variables() -> None:
    """Test from_env method with missing environment variables."""
    # No environment variables
    with patch.dict("os.environ", {}, clear=True):
        config = USPTOConfig.from_env()
        assert config.api_key is None
        assert config.bulk_data_base_url == "https://api.uspto.gov"
        assert config.patent_data_base_url == "https://api.uspto.gov"

    # Only API key
    with patch.dict("os.environ", {"USPTO_API_KEY": "env_key"}, clear=True):
        config = USPTOConfig.from_env()
        assert config.api_key == "env_key"
        assert config.bulk_data_base_url == "https://api.uspto.gov"
        assert config.patent_data_base_url == "https://api.uspto.gov"

    # Custom URLs
    with patch.dict(
        "os.environ",
        {
            "USPTO_API_KEY": "env_key",
            "USPTO_BULK_DATA_BASE_URL": "https://custom.bulk.url",
            "USPTO_PATENT_DATA_BASE_URL": "https://custom.patent.url",
        },
        clear=True,
    ):
        config = USPTOConfig.from_env()
        assert config.api_key == "env_key"
        assert config.bulk_data_base_url == "https://custom.bulk.url"
        assert config.patent_data_base_url == "https://custom.patent.url"
