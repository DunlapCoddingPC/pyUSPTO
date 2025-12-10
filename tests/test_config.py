"""Tests for USPTOConfig"""

from pyUSPTO.config import USPTOConfig
from pyUSPTO.http_config import HTTPConfig


class TestUSPTOConfig:
    """Tests for USPTOConfig class"""

    def test_default_values(self):
        """Test default USPTOConfig values"""
        config = USPTOConfig(api_key="test_key")
        assert config.api_key == "test_key"
        assert config.bulk_data_base_url == "https://api.uspto.gov"
        assert config.patent_data_base_url == "https://api.uspto.gov"
        assert config.petition_decisions_base_url == "https://api.uspto.gov"
        assert config.http_config is not None
        assert isinstance(config.http_config, HTTPConfig)

    def test_config_with_http_config(self):
        """Test USPTOConfig accepts HTTPConfig"""
        http_cfg = HTTPConfig(timeout=60.0, max_retries=5)
        config = USPTOConfig(api_key="test", http_config=http_cfg)

        assert config.http_config.timeout == 60.0
        assert config.http_config.max_retries == 5

    def test_config_default_http_config(self):
        """Test USPTOConfig creates default HTTPConfig"""
        config = USPTOConfig(api_key="test")
        assert config.http_config is not None
        assert config.http_config.timeout == 30.0
        assert config.http_config.max_retries == 3

    def test_config_from_env_includes_http_config(self, monkeypatch):
        """Test USPTOConfig.from_env() creates HTTPConfig from env"""
        monkeypatch.setenv("USPTO_API_KEY", "test_key")
        monkeypatch.setenv("USPTO_REQUEST_TIMEOUT", "45.0")
        monkeypatch.setenv("USPTO_MAX_RETRIES", "7")

        config = USPTOConfig.from_env()
        assert config.api_key == "test_key"
        assert config.http_config.timeout == 45.0
        assert config.http_config.max_retries == 7

    def test_config_api_key_from_env(self, monkeypatch):
        """Test USPTOConfig reads API key from environment"""
        monkeypatch.setenv("USPTO_API_KEY", "env_api_key")
        config = USPTOConfig()
        assert config.api_key == "env_api_key"

    def test_config_api_key_explicit_overrides_env(self, monkeypatch):
        """Test explicit API key overrides environment"""
        monkeypatch.setenv("USPTO_API_KEY", "env_api_key")
        config = USPTOConfig(api_key="explicit_key")
        assert config.api_key == "explicit_key"

    def test_config_custom_base_urls(self):
        """Test USPTOConfig with custom base URLs"""
        config = USPTOConfig(
            api_key="test",
            bulk_data_base_url="https://bulk.example.com",
            patent_data_base_url="https://patent.example.com",
            petition_decisions_base_url="https://petition.example.com",
        )
        assert config.bulk_data_base_url == "https://bulk.example.com"
        assert config.patent_data_base_url == "https://patent.example.com"
        assert config.petition_decisions_base_url == "https://petition.example.com"

    def test_config_from_env_custom_urls(self, monkeypatch):
        """Test USPTOConfig.from_env() reads custom URLs"""
        monkeypatch.setenv("USPTO_API_KEY", "test_key")
        monkeypatch.setenv("USPTO_BULK_DATA_BASE_URL", "https://bulk.example.com")
        monkeypatch.setenv("USPTO_PATENT_DATA_BASE_URL", "https://patent.example.com")
        monkeypatch.setenv(
            "USPTO_PETITION_DECISIONS_BASE_URL", "https://petition.example.com"
        )

        config = USPTOConfig.from_env()
        assert config.bulk_data_base_url == "https://bulk.example.com"
        assert config.patent_data_base_url == "https://patent.example.com"
        assert config.petition_decisions_base_url == "https://petition.example.com"

    def test_http_config_sharing(self):
        """Test HTTPConfig can be shared across multiple USPTOConfig instances"""
        shared_http_config = HTTPConfig(timeout=90.0, max_retries=10)

        config1 = USPTOConfig(api_key="key1", http_config=shared_http_config)
        config2 = USPTOConfig(api_key="key2", http_config=shared_http_config)

        # Both configs should reference the same HTTPConfig instance
        assert config1.http_config is config2.http_config
        assert config1.http_config.timeout == 90.0
        assert config2.http_config.timeout == 90.0
