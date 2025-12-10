"""
Common fixtures for integration tests.

This module contains fixtures that are shared between different integration test modules.
"""

import os
import shutil
from collections.abc import Iterator

import pytest

from pyUSPTO.config import USPTOConfig

# Skip all tests in this directory unless ENABLE_INTEGRATION_TESTS is set to 'true'
pytestmark = pytest.mark.skipif(
    os.environ.get("ENABLE_INTEGRATION_TESTS", "").lower() != "true",
    reason="Integration tests are disabled. Set ENABLE_INTEGRATION_TESTS=true to enable.",
)

# Define a temporary download directory for tests
TEST_DOWNLOAD_DIR = "./temp_test_downloads"


@pytest.fixture(scope="module", autouse=True)
def manage_test_download_dir() -> Iterator[None]:
    """Create and clean up the test download directory."""
    if os.path.exists(TEST_DOWNLOAD_DIR):
        shutil.rmtree(TEST_DOWNLOAD_DIR)
    os.makedirs(TEST_DOWNLOAD_DIR, exist_ok=True)
    yield
    if os.path.exists(TEST_DOWNLOAD_DIR):
        shutil.rmtree(TEST_DOWNLOAD_DIR)


@pytest.fixture(scope="module")
def api_key() -> str | None:
    """
    Get the API key from the environment.

    Uses module scope to cache the API key for all tests in the module.

    Returns:
        Optional[str]: The API key or None if not set
    """
    key = os.environ.get("USPTO_API_KEY")
    if not key:
        pytest.skip(
            "USPTO_API_KEY environment variable not set. Skipping integration tests."
        )
    return key


@pytest.fixture(scope="module")
def config(api_key: str | None) -> USPTOConfig:
    """
    Create a USPTOConfig instance for integration tests.

    Uses module scope to reuse the same config for all tests in the module.

    Args:
        api_key: The API key from the environment

    Returns:
        USPTOConfig: A configuration instance
    """
    return USPTOConfig(api_key=api_key)
