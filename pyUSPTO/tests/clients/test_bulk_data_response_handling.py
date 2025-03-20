"""
Tests for response handling in bulk_data.py.

This module contains tests for different API response formats and edge cases
in the BulkDataClient's response handling.
"""

from unittest.mock import MagicMock, patch

import pytest

from pyUSPTO.clients.bulk_data import BulkDataClient
from pyUSPTO.models.bulk_data import BulkDataProduct


class TestBulkDataResponseHandling:
    """Tests for response format handling in the BulkDataClient class."""

    def test_get_product_by_id_with_dict_response_containing_product_bag(self) -> None:
        """Test get_product_by_id when response is a dict with bulkDataProductBag."""
        # Setup
        client = BulkDataClient(api_key="test_key")

        # Create a dictionary response with a bulkDataProductBag containing the product we want
        dict_response = {
            "bulkDataProductBag": [
                {
                    "productIdentifier": "OTHER_PRODUCT",
                    "productTitleText": "Some Other Product",
                },
                {
                    "productIdentifier": "TARGET_PRODUCT",
                    "productTitleText": "Target Product",
                    "productDescriptionText": "This is the product we want",
                    "productFrequencyText": "Daily",
                    "productLabelArrayText": ["Test"],
                    "productDatasetArrayText": ["Test Dataset"],
                    "productDatasetCategoryArrayText": ["Test Category"],
                    "productFromDate": "2023-01-01",
                    "productToDate": "2023-12-31",
                    "productTotalFileSize": 1024,
                    "productFileTotalQuantity": 1,
                    "lastModifiedDateTime": "2023-12-31T23:59:59",
                    "mimeTypeIdentifierArrayText": ["application/zip"],
                },
            ]
        }

        # Mock _make_request to return our dictionary
        with patch.object(client, "_make_request", return_value=dict_response):
            # Call the method to test the missing branch
            result = client.get_product_by_id(product_id="TARGET_PRODUCT")

            # Verify
            assert isinstance(result, BulkDataProduct)
            assert result.product_identifier == "TARGET_PRODUCT"
            assert result.product_title_text == "Target Product"
            assert result.product_description_text == "This is the product we want"

    def test_get_product_by_id_with_dict_response_product_not_found(self) -> None:
        """Test get_product_by_id when product is not found in bulkDataProductBag."""
        # Setup
        client = BulkDataClient(api_key="test_key")

        # Create a dictionary response with a bulkDataProductBag NOT containing the product we want
        dict_response = {
            "bulkDataProductBag": [
                {
                    "productIdentifier": "PRODUCT_1",
                    "productTitleText": "Product 1",
                },
                {
                    "productIdentifier": "PRODUCT_2",
                    "productTitleText": "Product 2",
                },
            ]
        }

        # Mock _make_request to return our dictionary
        with patch.object(client, "_make_request", return_value=dict_response):
            # Call the method to test the error case
            with pytest.raises(
                ValueError, match="Product with ID NON_EXISTENT not found in response"
            ):
                client.get_product_by_id(product_id="NON_EXISTENT")

    def test_get_product_by_id_with_non_dict_json_response(self) -> None:
        """Test get_product_by_id when response.json() returns a non-dict value."""
        # Setup
        client = BulkDataClient(api_key="test_key")

        # Create a mock response object whose json() method returns a list instead of a dict
        mock_response = MagicMock()
        mock_response.json.return_value = ["not", "a", "dict"]

        # Patch _make_request to return our mock response
        with patch.object(client, "_make_request", return_value=mock_response):
            # Should raise TypeError
            with pytest.raises(TypeError, match=r"Expected dict, got <class 'list'>"):
                client.get_product_by_id(product_id="TEST")
