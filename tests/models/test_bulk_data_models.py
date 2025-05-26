"""
Tests for the bulk_data models.

This module contains consolidated tests for all classes in pyUSPTO.models.bulk_data.
"""

from typing import Any, Dict

from pyUSPTO.models.bulk_data import BulkDataProduct, BulkDataResponse


class TestBulkDataModelFromDict:
    """Tests for creating model objects from dictionaries."""

    def test_bulk_data_response_from_empty_dict(self) -> None:
        """Test from_dict method with empty data for BulkDataResponse."""
        # Test BulkDataResponse
        bulk_response = BulkDataResponse.from_dict({})
        assert bulk_response.count == 0
        assert bulk_response.bulk_data_product_bag == []

    def test_bulk_data_product_from_empty_dict(self) -> None:
        """Test from_dict method with empty data for BulkDataProduct."""
        # Test BulkDataProduct
        product = BulkDataProduct.from_dict({})
        assert product.product_identifier == ""
        assert product.product_description_text == ""
        assert product.product_title_text == ""
        assert product.product_frequency_text == ""
        assert product.product_label_array_text == []
        assert product.product_dataset_array_text == []
        assert product.product_dataset_category_array_text == []
        assert product.product_from_date == ""
        assert product.product_to_date == ""
        assert product.product_total_file_size == 0
        assert product.product_file_total_quantity == 0
        assert product.last_modified_date_time == ""
        assert product.mime_type_identifier_array_text == []
        assert product.product_file_bag is not None
        assert product.product_file_bag.count == 0
        assert product.product_file_bag.file_data_bag == []


class TestBulkDataModelToDict:
    """Tests for converting model objects to dictionaries."""

    def test_bulk_data_response_to_dict(self, bulk_data_sample: Dict[str, Any]) -> None:
        """Test BulkDataResponse.to_dict method."""
        # Create a BulkDataResponse from the sample data
        response = BulkDataResponse.from_dict(bulk_data_sample)

        # Convert it back to a dictionary
        result = response.to_dict()

        # Verify the structure of the result
        assert isinstance(result, dict)
        assert "count" in result
        assert result["count"] == response.count
        assert "bulkDataProductBag" in result
        assert isinstance(result["bulkDataProductBag"], list)
        assert len(result["bulkDataProductBag"]) == len(response.bulk_data_product_bag)

        # Check the first product in the bag
        product_dict = result["bulkDataProductBag"][0]
        assert "productIdentifier" in product_dict
        assert (
            product_dict["productIdentifier"]
            == response.bulk_data_product_bag[0].product_identifier
        )
        assert "productTitleText" in product_dict
        assert (
            product_dict["productTitleText"]
            == response.bulk_data_product_bag[0].product_title_text
        )
        assert "productDescriptionText" in product_dict
        assert (
            product_dict["productDescriptionText"]
            == response.bulk_data_product_bag[0].product_description_text
        )

    def test_bulk_data_response_to_dict_empty(self) -> None:
        """Test to_dict method with empty data for BulkDataResponse."""
        # Test BulkDataResponse
        bulk_response = BulkDataResponse(count=0, bulk_data_product_bag=[])
        result = bulk_response.to_dict()
        assert result["count"] == 0
        assert result["bulkDataProductBag"] == []
