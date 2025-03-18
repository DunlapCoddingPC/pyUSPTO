"""
Integration tests for the USPTO API client.

This module contains integration tests that make real API calls to the USPTO API.
These tests are optional and are skipped by default unless the ENABLE_INTEGRATION_TESTS
environment variable is set to 'true'.
"""

import os
import pytest
from typing import Dict, Any, List, Optional

from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.bulk_data import BulkDataResponse, BulkDataProduct
from pyUSPTO.clients import BulkDataClient, PatentDataClient
from pyUSPTO.models.patent_data import (
    PatentDataResponse,
    PatentFileWrapper,
)


# Skip all tests in this module unless ENABLE_INTEGRATION_TESTS is set to 'true'
pytestmark = pytest.mark.skipif(
    os.environ.get("ENABLE_INTEGRATION_TESTS", "").lower() != "true",
    reason="Integration tests are disabled. Set ENABLE_INTEGRATION_TESTS=true to enable.",
)


@pytest.fixture
def api_key() -> Optional[str]:
    """
    Get the API key from the environment.

    Returns:
        Optional[str]: The API key or None if not set
    """
    return os.environ.get("USPTO_API_KEY")


@pytest.fixture
def config(api_key: Optional[str]) -> USPTOConfig:
    """
    Create a USPTOConfig instance for integration tests.

    Args:
        api_key: The API key from the environment

    Returns:
        USPTOConfig: A configuration instance
    """
    return USPTOConfig(api_key=api_key)


@pytest.fixture
def bulk_data_client(config: USPTOConfig) -> BulkDataClient:
    """
    Create a BulkDataClient instance for integration tests.

    Args:
        config: The configuration instance

    Returns:
        BulkDataClient: A client instance
    """
    return BulkDataClient(config=config)


@pytest.fixture
def patent_data_client(config: USPTOConfig) -> PatentDataClient:
    """
    Create a PatentDataClient instance for integration tests.

    Args:
        config: The configuration instance

    Returns:
        PatentDataClient: A client instance
    """
    return PatentDataClient(config=config)


class TestBulkDataIntegration:
    """Integration tests for the BulkDataClient."""

    def test_get_products(self, bulk_data_client: BulkDataClient) -> None:
        """Test getting products from the API."""
        response = bulk_data_client.get_products()

        assert response is not None
        assert isinstance(response, BulkDataResponse)
        assert response.count > 0
        assert len(response.bulk_data_product_bag) > 0

        # Verify the structure of the first product
        product = response.bulk_data_product_bag[0]
        assert isinstance(product, BulkDataProduct)
        assert product.product_identifier is not None
        assert product.product_title_text is not None

    def test_search_products(self, bulk_data_client: BulkDataClient) -> None:
        """Test searching for products."""
        # Search for patent products
        response = bulk_data_client.search_products(query="patent", limit=5)

        assert response is not None
        assert isinstance(response, BulkDataResponse)
        assert response.count > 0
        assert len(response.bulk_data_product_bag) > 0
        assert len(response.bulk_data_product_bag) <= 5  # Respect the limit

    def test_get_product_by_id(self, bulk_data_client: BulkDataClient) -> None:
        """Test getting a specific product by ID."""
        # First get a list of products to find a valid ID
        response = bulk_data_client.get_products(params={"limit": 1})
        assert response.count > 0

        product_id = response.bulk_data_product_bag[0].product_identifier
        product = bulk_data_client.get_product_by_id(product_id, include_files=True)

        assert product is not None
        assert isinstance(product, BulkDataProduct)
        assert product.product_identifier == product_id
        assert product.product_title_text is not None

        # Check if files are included
        if product.product_file_total_quantity > 0:
            assert product.product_file_bag is not None
            assert product.product_file_bag.count > 0


class TestPatentDataIntegration:
    """Integration tests for the PatentDataClient."""

    def test_get_patent_applications(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test getting patent applications from the API."""
        response = patent_data_client.get_patent_applications(params={"limit": 5})

        assert response is not None
        assert isinstance(response, PatentDataResponse)
        assert response.count > 0
        assert len(response.patent_file_wrapper_data_bag) > 0
        assert len(response.patent_file_wrapper_data_bag) <= 5  # Respect the limit

        # Verify the structure of the first patent
        patent = response.patent_file_wrapper_data_bag[0]
        assert isinstance(patent, PatentFileWrapper)
        assert patent.application_number_text is not None
        assert patent.application_meta_data is not None

    def test_search_patents(self, patent_data_client: PatentDataClient) -> None:
        """Test searching for patents."""
        # Search for patents with a common inventor name
        response = patent_data_client.search_patents(inventor_name="Smith", limit=5)

        assert response is not None
        assert isinstance(response, PatentDataResponse)
        assert response.count > 0
        assert len(response.patent_file_wrapper_data_bag) > 0
        assert len(response.patent_file_wrapper_data_bag) <= 5  # Respect the limit

    def test_get_patent_by_application_number(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test getting a specific patent by application number."""
        # First get a list of patents to find a valid application number
        response = patent_data_client.get_patent_applications(params={"limit": 1})
        assert response.count > 0

        application_number = response.patent_file_wrapper_data_bag[
            0
        ].application_number_text
        # Ensure application_number is not None before proceeding
        assert application_number is not None, "Application number should not be None"
        patent = patent_data_client.get_patent_by_application_number(application_number)

        assert patent is not None
        assert isinstance(patent, PatentFileWrapper)
        assert patent.application_number_text == application_number
        assert patent.application_meta_data is not None

    def test_get_patent_status_codes(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test getting patent status codes."""
        status_codes = patent_data_client.get_patent_status_codes()

        assert status_codes is not None
        assert isinstance(status_codes, dict)
        assert "statusCodeBag" in status_codes
        assert len(status_codes["statusCodeBag"]) > 0
