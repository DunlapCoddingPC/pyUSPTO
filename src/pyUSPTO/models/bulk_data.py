"""
models.bulk_data - Data models for USPTO bulk data API

This module provides data models for the USPTO Open Data Portal (ODP) Bulk Data API.
"""

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class FileData:
    """Represents a file in the bulk data API."""

    file_name: str
    file_size: int
    file_data_from_date: str
    file_data_to_date: str
    file_type_text: str
    file_release_date: str
    file_download_uri: Optional[str] = None
    file_date: Optional[str] = None
    file_last_modified_date_time: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FileData":
        """Create a FileData object from a dictionary."""
        return cls(
            file_name=data.get("fileName", ""),
            file_size=data.get("fileSize", 0),
            file_data_from_date=data.get("fileDataFromDate", ""),
            file_data_to_date=data.get("fileDataToDate", ""),
            file_type_text=data.get("fileTypeText", ""),
            file_release_date=data.get("fileReleaseDate", ""),
            file_download_uri=data.get("fileDownloadURI"),
            file_date=data.get("fileDate"),
            file_last_modified_date_time=data.get("fileLastModifiedDateTime"),
        )


@dataclass
class ProductFileBag:
    """Container for file data elements."""

    count: int
    file_data_bag: List[FileData]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProductFileBag":
        """Create a ProductFileBag object from a dictionary."""
        return cls(
            count=data.get("count", 0),
            file_data_bag=[
                FileData.from_dict(file_data)
                for file_data in data.get("fileDataBag", [])
            ],
        )


@dataclass
class BulkDataProduct:
    """Represents a product in the bulk data API."""

    product_identifier: str
    product_description_text: str
    product_title_text: str
    product_frequency_text: str
    product_label_array_text: List[str]
    product_dataset_array_text: List[str]
    product_dataset_category_array_text: List[str]
    product_from_date: str
    product_to_date: str
    product_total_file_size: int
    product_file_total_quantity: int
    last_modified_date_time: str
    mime_type_identifier_array_text: List[str]
    product_file_bag: Optional[ProductFileBag] = None
    days_of_week_text: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BulkDataProduct":
        """Create a BulkDataProduct object from a dictionary."""
        return cls(
            product_identifier=data.get("productIdentifier", ""),
            product_description_text=data.get("productDescriptionText", ""),
            product_title_text=data.get("productTitleText", ""),
            product_frequency_text=data.get("productFrequencyText", ""),
            days_of_week_text=data.get("daysOfWeekText"),
            product_label_array_text=data.get("productLabelArrayText", []),
            product_dataset_array_text=data.get("productDatasetArrayText", []),
            product_dataset_category_array_text=data.get(
                "productDatasetCategoryArrayText", []
            ),
            product_from_date=data.get("productFromDate", ""),
            product_to_date=data.get("productToDate", ""),
            product_total_file_size=data.get("productTotalFileSize", 0),
            product_file_total_quantity=data.get("productFileTotalQuantity", 0),
            last_modified_date_time=data.get("lastModifiedDateTime", ""),
            mime_type_identifier_array_text=data.get("mimeTypeIdentifierArrayText", []),
            product_file_bag=ProductFileBag.from_dict(data.get("productFileBag", {})),
        )


@dataclass
class BulkDataResponse:
    """Top-level response from the bulk data API.

    Attributes:
        count: The number of bulk data products in the response.
        bulk_data_product_bag: List of bulk data products.
        raw_data: Optional raw JSON data from the API response (for debugging).
    """

    count: int
    bulk_data_product_bag: List[BulkDataProduct]
    raw_data: Optional[str] = field(default=None, compare=False, repr=False)

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], include_raw_data: bool = False
    ) -> "BulkDataResponse":
        """Create a BulkDataResponse object from a dictionary.

        Args:
            data: Dictionary containing API response data.
            include_raw_data: If True, store the raw JSON for debugging.

        Returns:
            BulkDataResponse: An instance of BulkDataResponse.
        """
        return cls(
            count=data.get("count", 0),
            bulk_data_product_bag=[
                BulkDataProduct.from_dict(product)
                for product in data.get("bulkDataProductBag", [])
            ],
            raw_data=json.dumps(data) if include_raw_data else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert the BulkDataResponse object to a dictionary."""
        return {
            "count": self.count,
            "bulkDataProductBag": [
                {
                    "productIdentifier": product.product_identifier,
                    "productTitleText": product.product_title_text,
                    "productDescriptionText": product.product_description_text,
                    # Add other fields as needed
                }
                for product in self.bulk_data_product_bag
            ],
        }
