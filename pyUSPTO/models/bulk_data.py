"""
models.bulk_data - Data models for USPTO bulk data API

This module provides data models for the USPTO Open Data Portal (ODP) Bulk Data API.
"""

from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterator,
    List,
    Optional,
    TypeVar,
    Union,
)

T = TypeVar("T")


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

    def __len__(self) -> int:
        """Return the number of file data elements."""
        return len(self.file_data_bag)

    def __iter__(self) -> Iterator[FileData]:
        """Iterate over the file data elements."""
        return iter(self.file_data_bag)

    def __getitem__(self, index: int) -> FileData:
        """Get a file data element by index."""
        return self.file_data_bag[index]

    def find(self, predicate: Callable[[FileData], bool]) -> Optional[FileData]:
        """Find a file data element that matches the predicate."""
        for file_data in self.file_data_bag:
            if predicate(file_data):
                return file_data
        return None

    def filter(self, predicate: Callable[[FileData], bool]) -> List[FileData]:
        """Filter file data elements that match the predicate."""
        return [file_data for file_data in self.file_data_bag if predicate(file_data)]

    def sort_by(
        self, key: Callable[[FileData], Any], reverse: bool = False
    ) -> List[FileData]:
        """Sort file data elements by the provided key function."""
        return sorted(self.file_data_bag, key=key, reverse=reverse)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProductFileBag":
        """Create a ProductFileBag object from a dictionary."""
        # Handle the case where the data might be None or empty
        if not data:
            return cls(count=0, file_data_bag=[])

        # The API returns a structure with count and fileDataBag fields
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
        # Handle the productFileBag correctly
        product_file_bag = None
        if "productFileBag" in data and data["productFileBag"]:
            # Pass the entire productFileBag object to ProductFileBag.from_dict
            product_file_bag = ProductFileBag.from_dict(data["productFileBag"])

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
            product_file_bag=product_file_bag,
        )


@dataclass
class BulkDataResponse:
    """
    Top-level response from the bulk data API with pagination capabilities.

    This class implements collection-like behavior and pagination methods to
    easily navigate through multiple pages of results.
    """

    count: int
    bulk_data_product_bag: List[BulkDataProduct]

    # Fields for pagination support (not included in repr)
    _client: Any = field(default=None, repr=False)
    _method_name: Optional[str] = field(default=None, repr=False)
    _params: Optional[Dict[str, Any]] = field(default=None, repr=False)
    _offset: int = field(default=0, repr=False)
    _limit: int = field(default=25, repr=False)

    def __len__(self) -> int:
        """Return the number of products in this response."""
        return len(self.bulk_data_product_bag)

    def __iter__(self) -> Iterator[BulkDataProduct]:
        """Iterate over the products in this response."""
        return iter(self.bulk_data_product_bag)

    def __getitem__(self, index: int) -> BulkDataProduct:
        """Get a product by index."""
        return self.bulk_data_product_bag[index]

    def has_next_page(self) -> bool:
        """Check if there are more results available."""
        if not self._client or not self._method_name:
            return False
        return self.count >= self._limit

    def get_next_page(self) -> "BulkDataResponse":
        """
        Fetch the next page of results.

        Returns:
            A new BulkDataResponse object with the next page of results.

        Raises:
            ValueError: If this response cannot be paginated or no more pages are available.
        """
        if not self._client or not self._method_name or not self._params:
            raise ValueError("This response cannot be paginated")

        if not self.has_next_page():
            raise ValueError("No more pages available")

        # Clone params and update offset
        params = self._params.copy() if self._params else {}
        params["offset"] = self._offset + self._limit

        # Call the same method with updated parameters
        method = getattr(self._client, self._method_name)
        return method(**params)

    def find(
        self, predicate: Callable[[BulkDataProduct], bool]
    ) -> Optional[BulkDataProduct]:
        """Find a product that matches the predicate."""
        for product in self.bulk_data_product_bag:
            if predicate(product):
                return product
        return None

    def filter(
        self, predicate: Callable[[BulkDataProduct], bool]
    ) -> List[BulkDataProduct]:
        """Filter products that match the predicate."""
        return [product for product in self.bulk_data_product_bag if predicate(product)]

    def sort_by(
        self, key: Callable[[BulkDataProduct], Any], reverse: bool = False
    ) -> List[BulkDataProduct]:
        """Sort products by the provided key function."""
        return sorted(self.bulk_data_product_bag, key=key, reverse=reverse)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BulkDataResponse":
        """Create a BulkDataResponse object from a dictionary."""
        return cls(
            count=data.get("count", 0),
            bulk_data_product_bag=[
                BulkDataProduct.from_dict(product)
                for product in data.get("bulkDataProductBag", [])
            ],
        )

    @classmethod
    def from_dict_with_pagination(
        cls,
        data: Dict[str, Any],
        client: Any,
        method_name: str,
        params: Dict[str, Any],
        offset: int,
        limit: int,
    ) -> "BulkDataResponse":
        """
        Create a BulkDataResponse object from a dictionary with pagination context.

        Args:
            data: The raw API response data
            client: The client instance used to make the request
            method_name: The name of the method that made the request
            params: The parameters used in the request
            offset: The offset used in the request
            limit: The limit used in the request

        Returns:
            A BulkDataResponse object with pagination context
        """
        response = cls.from_dict(data)
        response._client = client
        response._method_name = method_name
        response._params = params
        response._offset = offset
        response._limit = limit
        return response

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


@dataclass
class DatasetField:
    """Represents a field in a dataset."""

    name: str
    description: str
    data_type: str
    is_searchable: bool = False
    is_sortable: bool = False
    is_facetable: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DatasetField":
        """Create a DatasetField object from a dictionary."""
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            data_type=data.get("dataType", ""),
            is_searchable=data.get("isSearchable", False),
            is_sortable=data.get("isSortable", False),
            is_facetable=data.get("isFacetable", False),
        )


@dataclass
class DatasetFieldCollection:
    """Collection of dataset fields with helper methods."""

    fields: List[DatasetField]
    _client: Any = field(default=None, repr=False)

    def __len__(self) -> int:
        """Return the number of fields."""
        return len(self.fields)

    def __iter__(self) -> Iterator[DatasetField]:
        """Iterate over the fields."""
        return iter(self.fields)

    def __getitem__(self, index: int) -> DatasetField:
        """Get a field by index."""
        return self.fields[index]

    def find(self, predicate: Callable[[DatasetField], bool]) -> Optional[DatasetField]:
        """Find a field that matches the predicate."""
        for field in self.fields:
            if predicate(field):
                return field
        return None

    def get_by_name(self, name: str) -> Optional[DatasetField]:
        """Get a field by name."""
        return self.find(lambda field: field.name == name)

    def filter(self, predicate: Callable[[DatasetField], bool]) -> List[DatasetField]:
        """Filter fields that match the predicate."""
        return [field for field in self.fields if predicate(field)]

    def get_searchable_fields(self) -> List[DatasetField]:
        """Get all searchable fields."""
        return self.filter(lambda field: field.is_searchable)

    def get_sortable_fields(self) -> List[DatasetField]:
        """Get all sortable fields."""
        return self.filter(lambda field: field.is_sortable)

    def get_facetable_fields(self) -> List[DatasetField]:
        """Get all facetable fields."""
        return self.filter(lambda field: field.is_facetable)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DatasetFieldCollection":
        """Create a DatasetFieldCollection object from a dictionary."""
        return cls(
            fields=[
                DatasetField.from_dict(field_data)
                for field_data in data.get("fields", [])
            ]
        )


@dataclass
class DatasetInfo:
    """Represents dataset information."""

    name: str
    title: str
    description: str
    last_updated: Optional[str] = None
    record_count: Optional[int] = None
    field_count: Optional[int] = None
    dataset_fields: Optional[DatasetFieldCollection] = None
    _client: Any = field(default=None, repr=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DatasetInfo":
        """Create a DatasetInfo object from a dictionary."""
        return cls(
            name=data.get("name", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            last_updated=data.get("lastUpdated"),
            record_count=data.get("recordCount"),
            field_count=data.get("fieldCount"),
            dataset_fields=(
                DatasetFieldCollection.from_dict(data) if "fields" in data else None
            ),
        )

    def get_fields(self) -> Optional[DatasetFieldCollection]:
        """
        Get the fields for this dataset.

        If fields are already loaded, returns them directly.
        Otherwise, attempts to load them using the client if available.

        Returns:
            DatasetFieldCollection if available, None otherwise.
        """
        if self.dataset_fields:
            return self.dataset_fields

        if not self._client:
            return None

        # This assumes a method get_dataset_fields exists on the client
        if hasattr(self._client, "get_dataset_fields"):
            try:
                self.dataset_fields = self._client.get_dataset_fields(self.name)
                return self.dataset_fields
            except Exception:
                return None

        return None
