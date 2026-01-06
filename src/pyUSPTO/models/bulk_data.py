"""models.bulk_data - Data models for USPTO bulk data API.

This module provides data models for the USPTO Open Data Portal (ODP) Bulk Data API.
"""

import json
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any

from pyUSPTO.models.utils import (
    parse_to_date,
    parse_to_datetime_utc,
    serialize_date,
    serialize_datetime_as_naive,
)


# --- Enums for Categorical Data ---
class FileTypeCategory(Enum):
    """File type categories in bulk data.

    This enum provides type-safe representations of file types commonly
    found in USPTO bulk data products.
    """

    ZIP = "ZIP"
    TAR = "TAR"
    TAR_GZ = "TAR_GZ"
    TGZ = "TGZ"
    XML = "XML"
    JSON = "JSON"
    CSV = "CSV"

    @classmethod
    def _missing_(cls, value: Any) -> "FileTypeCategory | None":
        """Handle case-insensitive lookup and common aliases."""
        if isinstance(value, str):
            val_upper = value.upper().replace(".", "_")
            # Handle tar.gz variations
            if val_upper in ("TAR_GZ", "TARGZ", "TGZ", "TAR.GZ"):
                return cls.TAR_GZ
            # Try exact match
            for member in cls:
                if member.value.upper() == val_upper:
                    return member
        return None


class ProductFrequency(Enum):
    """Product update frequency categories.

    Represents how often a bulk data product is updated.
    """

    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    ANNUALLY = "ANNUALLY"
    AD_HOC = "AD_HOC"

    @classmethod
    def _missing_(cls, value: Any) -> "ProductFrequency | None":
        """Handle case-insensitive lookup."""
        if isinstance(value, str):
            val_upper = value.upper().replace(" ", "_").replace("-", "_")
            for member in cls:
                if member.value.upper() == val_upper:
                    return member
        return None


@dataclass(frozen=True)
class FileData:
    """Represent a file in the bulk data API.

    Attributes:
        file_name: The name of the file.
        file_size: Size of the file in bytes.
        product_identifier: The identifier of the product this file belongs to.
        file_data_from_date: Start date of data covered in the file.
        file_data_to_date: End date of data covered in the file.
        file_type_text: Description of the file type.
        file_release_date: Date when the file was released.
        file_download_uri: URL for downloading the file.
        file_date: Additional file date information.
        file_last_modified_date_time: Last modification timestamp.
        raw_data: Optional raw JSON data from the API response (for debugging).
    """

    file_name: str
    file_size: int
    product_identifier: str
    file_data_from_date: date | None
    file_data_to_date: date | None
    file_type_text: str
    file_release_date: date | None
    file_download_uri: str | None = None
    file_date: date | None = None
    file_last_modified_date_time: datetime | None = None
    raw_data: str | None = field(default=None, compare=False, repr=False)

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        product_identifier: str,
        include_raw_data: bool = False,
    ) -> "FileData":
        """Create a FileData object from a dictionary.

        Args:
            data: Dictionary containing file data from API response.
            product_identifier: The identifier of the product this file belongs to.
            include_raw_data: If True, store the raw JSON for debugging.

        Returns:
            FileData: An instance of FileData.
        """
        return cls(
            file_name=data.get("fileName", ""),
            file_size=data.get("fileSize", 0),
            product_identifier=product_identifier,
            file_data_from_date=parse_to_date(data.get("fileDataFromDate")),
            file_data_to_date=parse_to_date(data.get("fileDataToDate")),
            file_type_text=data.get("fileTypeText", ""),
            file_release_date=parse_to_date(data.get("fileReleaseDate")),
            file_download_uri=data.get("fileDownloadURI"),
            file_date=parse_to_date(data.get("fileDate")),
            file_last_modified_date_time=parse_to_datetime_utc(
                data.get("fileLastModifiedDateTime")
            ),
            raw_data=json.dumps(data) if include_raw_data else None,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the FileData object to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation with camelCase keys.
        """
        d = {
            "fileName": self.file_name,
            "fileSize": self.file_size,
            "fileDataFromDate": serialize_date(self.file_data_from_date),
            "fileDataToDate": serialize_date(self.file_data_to_date),
            "fileTypeText": self.file_type_text,
            "fileReleaseDate": serialize_date(self.file_release_date),
            "fileDownloadURI": self.file_download_uri,
            "fileDate": serialize_date(self.file_date),
            "fileLastModifiedDateTime": (
                serialize_datetime_as_naive(self.file_last_modified_date_time)
                if self.file_last_modified_date_time
                else None
            ),
        }
        return {k: v for k, v in d.items() if v is not None}


@dataclass(frozen=True)
class ProductFileBag:
    """Container for file data elements.

    Attributes:
        count: The number of files in the bag.
        file_data_bag: List of FileData objects.
        raw_data: Optional raw JSON data from the API response (for debugging).
    """

    count: int
    file_data_bag: list[FileData] = field(default_factory=list)
    raw_data: str | None = field(default=None, compare=False, repr=False)

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        product_identifier: str,
        include_raw_data: bool = False,
    ) -> "ProductFileBag":
        """Create a ProductFileBag object from a dictionary.

        Args:
            data: Dictionary containing product file bag data.
            product_identifier: The identifier of the product this bag belongs to.
            include_raw_data: If True, store the raw JSON for debugging.

        Returns:
            ProductFileBag: An instance of ProductFileBag.
        """
        # Defensive parsing for file_data_bag
        file_data_bag_raw = data.get("fileDataBag", [])
        file_data_bag = (
            [
                FileData.from_dict(
                    file_data,
                    product_identifier=product_identifier,
                    include_raw_data=include_raw_data,
                )
                for file_data in file_data_bag_raw
                if isinstance(file_data, dict)
            ]
            if isinstance(file_data_bag_raw, list)
            else []
        )

        return cls(
            count=data.get("count", 0),
            file_data_bag=file_data_bag,
            raw_data=json.dumps(data) if include_raw_data else None,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the ProductFileBag object to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation with camelCase keys.
        """
        d = {
            "count": self.count,
            "fileDataBag": [f.to_dict() for f in self.file_data_bag],
        }
        return {
            k: v
            for k, v in d.items()
            if v is not None and (not isinstance(v, list) or v)
        }


@dataclass(frozen=True)
class BulkDataProduct:
    """Represent a product in the bulk data API.

    Attributes:
        product_identifier: Unique identifier for the product.
        product_description_text: Description of the product.
        product_title_text: Title of the product.
        product_frequency_text: Update frequency description.
        product_label_array_text: Labels associated with the product.
        product_dataset_array_text: Datasets included in the product.
        product_dataset_category_array_text: Categories of datasets.
        product_from_date: Start date of data in the product.
        product_to_date: End date of data in the product.
        product_total_file_size: Total size of all files in bytes.
        product_file_total_quantity: Number of files in the product.
        last_modified_date_time: Last modification timestamp.
        mime_type_identifier_array_text: MIME types of files in the product.
        product_file_bag: Container with file data.
        days_of_week_text: Days of the week for updates (if applicable).
        raw_data: Optional raw JSON data from the API response (for debugging).
    """

    product_identifier: str
    product_description_text: str
    product_title_text: str
    product_frequency_text: str
    product_label_array_text: list[str] = field(default_factory=list)
    product_dataset_array_text: list[str] = field(default_factory=list)
    product_dataset_category_array_text: list[str] = field(default_factory=list)
    product_from_date: date | None = None
    product_to_date: date | None = None
    product_total_file_size: int = 0
    product_file_total_quantity: int = 0
    last_modified_date_time: datetime | None = None
    mime_type_identifier_array_text: list[str] = field(default_factory=list)
    product_file_bag: ProductFileBag | None = None
    days_of_week_text: str | None = None
    raw_data: str | None = field(default=None, compare=False, repr=False)

    @classmethod
    def from_dict(
        cls, data: dict[str, Any], include_raw_data: bool = False
    ) -> "BulkDataProduct":
        """Create a BulkDataProduct object from a dictionary.

        Args:
            data: Dictionary containing product data from API response.
            include_raw_data: If True, store the raw JSON for debugging.

        Returns:
            BulkDataProduct: An instance of BulkDataProduct.
        """
        # Defensive parsing for list fields
        product_label_array = data.get("productLabelArrayText", [])
        if not isinstance(product_label_array, list):
            product_label_array = []

        product_dataset_array = data.get("productDatasetArrayText", [])
        if not isinstance(product_dataset_array, list):
            product_dataset_array = []

        product_dataset_category_array = data.get("productDatasetCategoryArrayText", [])
        if not isinstance(product_dataset_category_array, list):
            product_dataset_category_array = []

        mime_type_array = data.get("mimeTypeIdentifierArrayText", [])
        if not isinstance(mime_type_array, list):
            mime_type_array = []

        # Parse product file bag #TODO: this does not seem to be available in search responses.
        product_file_bag_data = data.get("productFileBag")
        product_file_bag = (
            ProductFileBag.from_dict(
                product_file_bag_data,
                product_identifier=data.get("productIdentifier", ""),
                include_raw_data=include_raw_data,
            )
            if product_file_bag_data and isinstance(product_file_bag_data, dict)
            else None
        )

        return cls(
            product_identifier=data.get("productIdentifier", ""),
            product_description_text=data.get("productDescriptionText", ""),
            product_title_text=data.get("productTitleText", ""),
            product_frequency_text=data.get("productFrequencyText", ""),
            days_of_week_text=data.get("daysOfWeekText"),
            product_label_array_text=product_label_array,
            product_dataset_array_text=product_dataset_array,
            product_dataset_category_array_text=product_dataset_category_array,
            product_from_date=parse_to_date(data.get("productFromDate")),
            product_to_date=parse_to_date(data.get("productToDate")),
            product_total_file_size=data.get("productTotalFileSize", 0),
            product_file_total_quantity=data.get("productFileTotalQuantity", 0),
            last_modified_date_time=parse_to_datetime_utc(
                data.get("lastModifiedDateTime")
            ),
            mime_type_identifier_array_text=mime_type_array,
            product_file_bag=product_file_bag,
            raw_data=json.dumps(data) if include_raw_data else None,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the BulkDataProduct object to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation with camelCase keys.
        """
        d = {
            "productIdentifier": self.product_identifier,
            "productDescriptionText": self.product_description_text,
            "productTitleText": self.product_title_text,
            "productFrequencyText": self.product_frequency_text,
            "daysOfWeekText": self.days_of_week_text,
            "productLabelArrayText": self.product_label_array_text,
            "productDatasetArrayText": self.product_dataset_array_text,
            "productDatasetCategoryArrayText": self.product_dataset_category_array_text,
            "productFromDate": serialize_date(self.product_from_date),
            "productToDate": serialize_date(self.product_to_date),
            "productTotalFileSize": self.product_total_file_size,
            "productFileTotalQuantity": self.product_file_total_quantity,
            "lastModifiedDateTime": (
                serialize_datetime_as_naive(self.last_modified_date_time)
                if self.last_modified_date_time
                else None
            ),
            "mimeTypeIdentifierArrayText": self.mime_type_identifier_array_text,
            "productFileBag": (
                self.product_file_bag.to_dict() if self.product_file_bag else None
            ),
        }
        return {
            k: v
            for k, v in d.items()
            if v is not None and (not isinstance(v, list) or v)
        }


@dataclass(frozen=True)
class BulkDataResponse:
    """Top-level response from the bulk data API.

    Attributes:
        count: The number of bulk data products in the response.
        bulk_data_product_bag: List of bulk data products.
        raw_data: Optional raw JSON data from the API response (for debugging).
    """

    count: int
    bulk_data_product_bag: list[BulkDataProduct] = field(default_factory=list)
    raw_data: str | None = field(default=None, compare=False, repr=False)

    @classmethod
    def from_dict(
        cls, data: dict[str, Any], include_raw_data: bool = False
    ) -> "BulkDataResponse":
        """Create a BulkDataResponse object from a dictionary.

        Args:
            data: Dictionary containing API response data.
            include_raw_data: If True, store the raw JSON for debugging and
                propagate to nested models.

        Returns:
            BulkDataResponse: An instance of BulkDataResponse.
        """
        # Defensive parsing for bulk_data_product_bag
        products_data = data.get("bulkDataProductBag", [])
        products = (
            [
                BulkDataProduct.from_dict(product, include_raw_data=include_raw_data)
                for product in products_data
                if isinstance(product, dict)
            ]
            if isinstance(products_data, list)
            else []
        )

        return cls(
            count=data.get("count", 0),
            bulk_data_product_bag=products,
            raw_data=json.dumps(data) if include_raw_data else None,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the BulkDataResponse object to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation with camelCase keys.
        """
        d = {
            "count": self.count,
            "bulkDataProductBag": [
                product.to_dict() for product in self.bulk_data_product_bag
            ],
        }
        return {
            k: v
            for k, v in d.items()
            if v is not None and (not isinstance(v, list) or v)
        }
