"""
Integration tests for the USPTO Bulk Data API client.

This module contains integration tests that make real API calls to the USPTO Bulk Data API.
These tests are optional and are skipped by default unless the ENABLE_INTEGRATION_TESTS
environment variable is set to 'true'.
"""

import os
from typing import Iterator, List, Optional

import pytest

from pyUSPTO.clients import BulkDataClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.exceptions import USPTOApiError
from pyUSPTO.models.bulk_data import BulkDataProduct, BulkDataResponse

# Import shared fixtures
from tests.integration.conftest import TEST_DOWNLOAD_DIR

# Skip all tests in this module unless ENABLE_INTEGRATION_TESTS is set to 'true'
pytestmark = pytest.mark.skipif(
    os.environ.get("ENABLE_INTEGRATION_TESTS", "").lower() != "true",
    reason="Integration tests are disabled. Set ENABLE_INTEGRATION_TESTS=true to enable.",
)


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


class TestBulkDataIntegration:
    """Integration tests for the BulkDataClient."""

    def test_get_products(self, bulk_data_client: BulkDataClient) -> None:
        """Test getting products from the API."""
        response = bulk_data_client.get_products()

        assert response is not None
        assert isinstance(response, BulkDataResponse)
        assert response.count > 0
        assert response.bulk_data_product_bag is not None
        assert len(response.bulk_data_product_bag) > 0

        product = response.bulk_data_product_bag[0]
        assert isinstance(product, BulkDataProduct)
        assert product.product_identifier is not None
        assert product.product_title_text is not None

    def test_search_products(self, bulk_data_client: BulkDataClient) -> None:
        """Test searching for products."""
        response = bulk_data_client.search_products(
            query="PAIF", limit=5
        )  # PAIF is a common product type

        assert response is not None
        assert isinstance(response, BulkDataResponse)
        assert response.count > 0
        assert response.bulk_data_product_bag is not None
        assert len(response.bulk_data_product_bag) > 0
        assert len(response.bulk_data_product_bag) <= 5

    def test_get_product_by_id(self, bulk_data_client: BulkDataClient) -> None:
        """Test getting a specific product by ID."""
        response = bulk_data_client.get_products(
            params={
                "limit": 1,
                "q": "productTitleText:Patent Application Information Retrieval*",
            }
        )  # More specific query
        assert response.count > 0
        assert response.bulk_data_product_bag

        product_id = response.bulk_data_product_bag[0].product_identifier
        assert product_id is not None
        product = bulk_data_client.get_product_by_id(product_id, include_files=True)

        assert product is not None
        assert isinstance(product, BulkDataProduct)
        assert product.product_identifier == product_id

        if product.product_file_total_quantity > 0:
            assert product.product_file_bag is not None
            assert product.product_file_bag.count > 0
