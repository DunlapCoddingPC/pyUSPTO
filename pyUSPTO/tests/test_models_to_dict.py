"""
Tests for the to_dict methods in model classes.

This module contains tests for the to_dict methods in the model classes.
"""

from typing import Any, Dict

import pytest

from pyUSPTO.models.bulk_data import (
    BulkDataProduct,
    BulkDataResponse,
    FileData,
    ProductFileBag,
)
from pyUSPTO.models.patent_data import (
    ApplicationMetaData,
    PatentDataResponse,
    PatentFileWrapper,
)


class TestBulkDataModelsToDictMethods:
    """Tests for the to_dict methods in bulk data model classes."""

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


class TestPatentDataModelsToDictMethods:
    """Tests for the to_dict methods in patent data model classes."""

    def test_patent_data_response_to_dict(
        self, patent_data_sample: Dict[str, Any]
    ) -> None:
        """Test PatentDataResponse.to_dict method."""
        # Create a PatentDataResponse from the sample data
        response = PatentDataResponse.from_dict(patent_data_sample)

        # Convert it back to a dictionary
        result = response.to_dict()

        # Verify the structure of the result
        assert isinstance(result, dict)
        assert "count" in result
        assert result["count"] == response.count
        assert "patentFileWrapperDataBag" in result
        assert isinstance(result["patentFileWrapperDataBag"], list)
        assert len(result["patentFileWrapperDataBag"]) == len(
            response.patent_file_wrapper_data_bag
        )

        # Check the first patent in the bag
        patent_dict = result["patentFileWrapperDataBag"][0]
        assert "applicationNumberText" in patent_dict
        assert (
            patent_dict["applicationNumberText"]
            == response.patent_file_wrapper_data_bag[0].application_number_text
        )

        # Verify documentBag is present (even if empty)
        assert "documentBag" in result
        assert isinstance(result["documentBag"], list)
