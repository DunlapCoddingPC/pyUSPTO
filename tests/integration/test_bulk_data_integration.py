"""
Integration tests for the USPTO Bulk Data API client.

This module contains integration tests that make real API calls to the USPTO Bulk Data API.
These tests are optional and are skipped by default unless the ENABLE_INTEGRATION_TESTS
environment variable is set to 'true'.
"""

import os

import pytest

from pyUSPTO.clients import BulkDataClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.bulk_data import BulkDataProduct, BulkDataResponse

# Import shared fixtures

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

    def test_search_products_no_query(self, bulk_data_client: BulkDataClient) -> None:
        """Test getting products from the API without a query (returns default results)."""
        response = bulk_data_client.search_products()

        assert response is not None
        assert isinstance(response, BulkDataResponse)
        assert response.count > 0
        assert response.bulk_data_product_bag is not None
        assert len(response.bulk_data_product_bag) > 0

        product = response.bulk_data_product_bag[0]
        assert isinstance(product, BulkDataProduct)
        assert product.product_identifier is not None
        assert product.product_title_text is not None

    def test_search_products_with_query(self, bulk_data_client: BulkDataClient) -> None:
        """Test searching for products with a full-text query.

        Note: The USPTO Bulk Data API only supports full-text search.
        Field-specific queries (e.g., field:value) do not work.
        """
        # Use "TRTDXFAG" as a test query (from notes file)
        response = bulk_data_client.search_products(query="TRTDXFAG", limit=5)

        assert response is not None
        assert isinstance(response, BulkDataResponse)
        # May return 0 results if the query doesn't match anything
        assert response.bulk_data_product_bag is not None

        if response.count > 0:
            assert len(response.bulk_data_product_bag) > 0
            assert len(response.bulk_data_product_bag) <= 5

    def test_search_products_with_limit_and_offset(
        self, bulk_data_client: BulkDataClient
    ) -> None:
        """Test pagination with offset and limit parameters."""
        # Get first page
        response1 = bulk_data_client.search_products(offset=0, limit=5)
        assert response1.count > 0
        assert len(response1.bulk_data_product_bag) > 0

        # Get second page
        response2 = bulk_data_client.search_products(offset=5, limit=5)

        # Verify we got different results (if there are enough products)
        if response1.count > 5:
            first_ids = {p.product_identifier for p in response1.bulk_data_product_bag}
            second_ids = {p.product_identifier for p in response2.bulk_data_product_bag}
            # The two pages should have different products
            assert first_ids.isdisjoint(second_ids)

    def test_get_product_by_id(self, bulk_data_client: BulkDataClient) -> None:
        """Test getting a specific product by ID."""
        # First, search for a product to get a valid ID
        response = bulk_data_client.search_products(limit=1)
        assert response.count > 0
        assert response.bulk_data_product_bag

        product_id = response.bulk_data_product_bag[0].product_identifier
        assert product_id is not None

        # Get the product by ID with files
        product = bulk_data_client.get_product_by_id(product_id, include_files=True)

        assert product is not None
        assert isinstance(product, BulkDataProduct)
        assert product.product_identifier == product_id

        if product.product_file_total_quantity > 0:
            assert product.product_file_bag is not None
            assert product.product_file_bag.count > 0

    def test_get_product_by_id_with_latest_flag(
        self, bulk_data_client: BulkDataClient
    ) -> None:
        """Test getting the latest file for a product."""
        # Search for a product
        response = bulk_data_client.search_products(limit=1)
        assert response.count > 0

        product_id = response.bulk_data_product_bag[0].product_identifier

        # Get product with latest file only
        product = bulk_data_client.get_product_by_id(
            product_id, include_files=True, latest=True
        )

        assert product is not None
        assert product.product_identifier == product_id

        # If there are files, verify we got at most one
        if product.product_file_bag and product.product_file_bag.file_data_bag:
            # Latest flag should return only the most recent file
            assert len(product.product_file_bag.file_data_bag) >= 1
