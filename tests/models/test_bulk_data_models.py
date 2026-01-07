"""
Tests for the bulk_data models.

This module contains consolidated tests for all classes in pyUSPTO.models.bulk_data.
"""

from typing import Any

from pyUSPTO.models.bulk_data import (
    BulkDataProduct,
    BulkDataResponse,
    FileTypeCategory,
    ProductFrequency,
)


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
        assert product.product_from_date is None  # Now returns None (date object), not empty string
        assert product.product_to_date is None  # Now returns None (date object), not empty string
        assert product.product_total_file_size == 0
        assert product.product_file_total_quantity == 0
        assert product.last_modified_date_time is None  # Now returns None (datetime object), not empty string
        assert product.mime_type_identifier_array_text == []
        assert product.product_file_bag is None  # Now defaults to None with empty dict


class TestBulkDataModelToDict:
    """Tests for converting model objects to dictionaries."""

    def test_bulk_data_response_to_dict(self, bulk_data_sample: dict[str, Any]) -> None:
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
        # bulkDataProductBag is filtered out when empty (by design)
        assert "bulkDataProductBag" not in result


class TestBulkDataEnums:
    """Tests for enums in bulk_data models."""

    def test_file_type_category_missing_method(self) -> None:
        """Test FileTypeCategory._missing_ method for case-insensitive lookup."""
        # Test case-insensitive lookup
        assert FileTypeCategory("zip") == FileTypeCategory.ZIP
        assert FileTypeCategory("tar") == FileTypeCategory.TAR

        # Test tar.gz variations (all map to TAR_GZ)
        assert FileTypeCategory("tar.gz") == FileTypeCategory.TAR_GZ
        assert FileTypeCategory("TAR_GZ") == FileTypeCategory.TAR_GZ
        assert FileTypeCategory("TARGZ") == FileTypeCategory.TAR_GZ
        assert FileTypeCategory("tgz") == FileTypeCategory.TAR_GZ  # tgz also maps to TAR_GZ

        # Test TGZ as exact match
        assert FileTypeCategory("TGZ") == FileTypeCategory.TGZ

        # Test return None for unknown values
        assert FileTypeCategory._missing_("unknown") is None
        assert FileTypeCategory._missing_(123) is None  # Non-string value

    def test_product_frequency_missing_method(self) -> None:
        """Test ProductFrequency._missing_ method for case-insensitive lookup."""
        # Test case-insensitive lookup
        assert ProductFrequency("daily") == ProductFrequency.DAILY
        assert ProductFrequency("WEEKLY") == ProductFrequency.WEEKLY

        # Test with spaces and hyphens
        assert ProductFrequency("ad hoc") == ProductFrequency.AD_HOC
        assert ProductFrequency("ad-hoc") == ProductFrequency.AD_HOC

        # Test return None for unknown values
        assert ProductFrequency._missing_("unknown") is None
        assert ProductFrequency._missing_(456) is None  # Non-string value


class TestBulkDataDefensiveParsing:
    """Tests for defensive parsing in bulk_data models."""

    def test_bulk_data_product_from_dict_with_non_list_arrays(self) -> None:
        """Test BulkDataProduct.from_dict with non-list array fields."""
        # Test with string instead of list for array fields
        data = {
            "productIdentifier": "TEST",
            "productDescriptionText": "Test",
            "productTitleText": "Test Title",
            "productFrequencyText": "Daily",
            "productLabelArrayText": "not a list",  # Should become []
            "productDatasetArrayText": "also not a list",  # Should become []
            "productDatasetCategoryArrayText": 123,  # Should become []
            "mimeTypeIdentifierArrayText": None,  # Should become []
        }

        product = BulkDataProduct.from_dict(data)

        # All array fields should be empty lists due to defensive parsing
        assert product.product_label_array_text == []
        assert product.product_dataset_array_text == []
        assert product.product_dataset_category_array_text == []
        assert product.mime_type_identifier_array_text == []
