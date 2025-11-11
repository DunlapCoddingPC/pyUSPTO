"""Tests for HTTPConfig"""
import os

import pytest

from pyUSPTO.http_config import HTTPConfig


class TestHTTPConfig:
    """Tests for HTTPConfig dataclass"""

    def test_default_values(self):
        """Test default HTTPConfig values"""
        config = HTTPConfig()
        assert config.timeout == 30.0
        assert config.connect_timeout == 10.0
        assert config.max_retries == 3
        assert config.backoff_factor == 1.0
        assert config.retry_status_codes == [429, 500, 502, 503, 504]
        assert config.pool_connections == 10
        assert config.pool_maxsize == 10
        assert config.custom_headers is None

    def test_custom_values(self):
        """Test HTTPConfig with custom values"""
        config = HTTPConfig(
            timeout=60.0,
            connect_timeout=15.0,
            max_retries=5,
            backoff_factor=2.0,
            retry_status_codes=[500, 503],
            pool_connections=20,
            pool_maxsize=30,
            custom_headers={"User-Agent": "TestApp/1.0"}
        )
        assert config.timeout == 60.0
        assert config.connect_timeout == 15.0
        assert config.max_retries == 5
        assert config.backoff_factor == 2.0
        assert config.retry_status_codes == [500, 503]
        assert config.pool_connections == 20
        assert config.pool_maxsize == 30
        assert config.custom_headers == {"User-Agent": "TestApp/1.0"}

    def test_from_env(self, monkeypatch):
        """Test HTTPConfig.from_env()"""
        monkeypatch.setenv("USPTO_REQUEST_TIMEOUT", "45.0")
        monkeypatch.setenv("USPTO_CONNECT_TIMEOUT", "8.0")
        monkeypatch.setenv("USPTO_MAX_RETRIES", "7")
        monkeypatch.setenv("USPTO_BACKOFF_FACTOR", "1.5")
        monkeypatch.setenv("USPTO_POOL_CONNECTIONS", "15")
        monkeypatch.setenv("USPTO_POOL_MAXSIZE", "25")

        config = HTTPConfig.from_env()
        assert config.timeout == 45.0
        assert config.connect_timeout == 8.0
        assert config.max_retries == 7
        assert config.backoff_factor == 1.5
        assert config.pool_connections == 15
        assert config.pool_maxsize == 25

    def test_from_env_with_defaults(self):
        """Test HTTPConfig.from_env() uses defaults when env vars not set"""
        # Clear any existing env vars
        for key in ["USPTO_REQUEST_TIMEOUT", "USPTO_CONNECT_TIMEOUT", "USPTO_MAX_RETRIES",
                    "USPTO_BACKOFF_FACTOR", "USPTO_POOL_CONNECTIONS", "USPTO_POOL_MAXSIZE"]:
            os.environ.pop(key, None)

        config = HTTPConfig.from_env()
        assert config.timeout == 30.0
        assert config.connect_timeout == 10.0
        assert config.max_retries == 3
        assert config.backoff_factor == 1.0
        assert config.pool_connections == 10
        assert config.pool_maxsize == 10

    def test_get_timeout_tuple(self):
        """Test timeout tuple generation"""
        config = HTTPConfig(connect_timeout=5.0, timeout=15.0)
        timeout_tuple = config.get_timeout_tuple()
        assert timeout_tuple == (5.0, 15.0)

    def test_get_timeout_tuple_with_none(self):
        """Test timeout tuple with None values"""
        config = HTTPConfig(connect_timeout=None, timeout=None)
        timeout_tuple = config.get_timeout_tuple()
        assert timeout_tuple == (None, None)

    def test_custom_headers_none_by_default(self):
        """Test custom_headers is None by default"""
        config = HTTPConfig()
        assert config.custom_headers is None

    def test_custom_headers_can_be_set(self):
        """Test custom_headers can be set"""
        headers = {
            "User-Agent": "MyApp/2.0",
            "X-Custom-Header": "custom-value"
        }
        config = HTTPConfig(custom_headers=headers)
        assert config.custom_headers == headers

    def test_retry_status_codes_default(self):
        """Test retry_status_codes has correct default"""
        config = HTTPConfig()
        assert 429 in config.retry_status_codes  # Rate limit
        assert 500 in config.retry_status_codes  # Internal server error
        assert 502 in config.retry_status_codes  # Bad gateway
        assert 503 in config.retry_status_codes  # Service unavailable
        assert 504 in config.retry_status_codes  # Gateway timeout
