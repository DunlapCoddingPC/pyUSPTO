"""clients.bulk_data - Client for USPTO bulk data API.

This module provides a client for interacting with the USPTO Open Data Portal (ODP)
Bulk Data API. It allows you to search for and download bulk data products.
"""

import warnings
from collections.abc import Iterator
from typing import Any

from pyUSPTO.clients.base import BaseUSPTOClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.bulk_data import BulkDataProduct, BulkDataResponse, FileData
from pyUSPTO.warnings import USPTODataMismatchWarning


class BulkDataClient(BaseUSPTOClient[BulkDataResponse]):
    """Client for interacting with the USPTO bulk data API."""

    # Centralized endpoint configuration
    ENDPOINTS = {
        # Products endpoints
        "products_search": "api/v1/datasets/products/search",
        "product_by_id": "api/v1/datasets/products/{product_id}",
        # Download endpoint
        "download_file": "api/v1/datasets/products/files/{productIdentifier}/{fileName}",
    }

    def __init__(
        self,
        config: USPTOConfig | None = None,
        base_url: str | None = None,
    ):
        """Initialize the BulkDataClient.

        Args:
            config: USPTOConfig instance containing API key and settings. If not provided,
                creates config from environment variables (requires USPTO_API_KEY).
            base_url: Optional base URL override for the USPTO Bulk Data API.
                If not provided, uses config.bulk_data_base_url or default.
        """
        # Use provided config or create from environment
        if config is None:
            self.config = USPTOConfig.from_env()
        else:
            self.config = config

        # Determine effective base URL
        effective_base_url = base_url or self.config.bulk_data_base_url

        # Initialize base client
        super().__init__(
            base_url=effective_base_url,
            config=self.config,
        )

    def get_product_by_id(
        self,
        product_id: str,
        file_data_from_date: str | None = None,
        file_data_to_date: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        include_files: bool | None = None,
        latest: bool | None = None,
    ) -> BulkDataProduct:
        """Get a specific bulk data product by ID.

        Args:
            product_id: The product identifier.
            file_data_from_date: Filter files by data from date (YYYY-MM-DD).
            file_data_to_date: Filter files by data to date (YYYY-MM-DD).
            offset: Number of product file records to skip.
            limit: Number of product file records to collect.
            include_files: Whether to include product files in the response.
            latest: Whether to return only the latest product file.

        Returns:
            BulkDataProduct: The requested product.

        Raises:
            ValueError: If product not found in response.

        Examples:
            Get product without files:
            >>> product = client.get_product_by_id("patent-grant-data-text")

            Get product with files:
            >>> product = client.get_product_by_id(
            ...     "patent-grant-data-text",
            ...     include_files=True,
            ...     latest=True
            ... )
        """
        endpoint = self.ENDPOINTS["product_by_id"].format(product_id=product_id)

        params = {}
        if file_data_from_date:
            params["fileDataFromDate"] = file_data_from_date
        if file_data_to_date:
            params["fileDataToDate"] = file_data_to_date
        if offset is not None:
            params["offset"] = str(offset)
        if limit is not None:
            params["limit"] = str(limit)
        if include_files is not None:
            params["includeFiles"] = str(include_files).lower()
        if latest is not None:
            params["latest"] = str(latest).lower()

        # Use response_class for clean parsing
        response = self._make_request(
            method="GET",
            endpoint=endpoint,
            params=params if params else None,
            response_class=BulkDataResponse,
        )
        assert isinstance(response, BulkDataResponse)

        # Extract the product from response
        if response.bulk_data_product_bag:
            product = response.bulk_data_product_bag[0]
            # Validate it's the correct product
            if product.product_identifier != product_id:
                warnings.warn(
                    f"API returned product '{product.product_identifier}' "
                    f"but requested '{product_id}'. This may indicate an API inconsistency.",
                    USPTODataMismatchWarning,
                    stacklevel=2,
                )
            return product
        else:
            raise ValueError(f"Product '{product_id}' not found")

    def download_file(
        self,
        file_data: FileData,
        destination: str | None = None,
        file_name: str | None = None,
        overwrite: bool = False,
        extract: bool = True,
    ) -> str:
        """Download a file from the bulk data API.

        Automatically extracts archives (tar.gz, zip) by default. The download
        uses base class helpers for consistent behavior across all clients.

        Args:
            file_data: FileData object containing download info and product_identifier.
            destination: Directory to save/extract to. Defaults to current directory.
            file_name: Override filename. Defaults to file_data.file_name.
            overwrite: Whether to overwrite existing files. Defaults to False.
            extract: Whether to auto-extract archives. Defaults to True.

        Returns:
            str: Path to downloaded file or extracted directory.

        Raises:
            FileExistsError: If file exists and overwrite=False.

        Examples:
            Download and extract a file:
            >>> product = client.get_product_by_id("product-123", include_files=True)
            >>> file_data = product.product_file_bag.file_data_bag[0]
            >>> path = client.download_file(file_data, destination="./downloads")

            Download without extraction:
            >>> path = client.download_file(file_data, extract=False)
        """
        # Resolve filename
        default_file_name = file_name or file_data.file_name

        # Construct URL from endpoint
        endpoint = self.ENDPOINTS["download_file"].format(
            productIdentifier=file_data.product_identifier,
            fileName=default_file_name,
        )
        download_url = f"{self.base_url}/{endpoint}"

        # Delegate to base class helpers
        if extract:
            return self._download_and_extract(
                url=download_url,
                destination=destination,
                file_name=default_file_name,
                overwrite=overwrite,
            )
        else:
            return self._download_file(
                url=download_url,
                destination=destination,
                file_name=default_file_name,
                overwrite=overwrite,
            )

    def paginate_products(
        self, post_body: dict[str, Any] | None = None, **kwargs: Any
    ) -> Iterator[BulkDataProduct]:
        """Paginate through all products matching the search criteria.

        Supports both GET and POST requests.

        Args:
            post_body: Optional POST body for complex search queries
            **kwargs: Keyword arguments for GET-based pagination

        Yields:
            BulkDataProduct objects
        """
        return self.paginate_results(
            method_name="search_products",
            response_container_attr="bulk_data_product_bag",
            post_body=post_body,
            **kwargs,
        )

    def search_products(
        self,
        query: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        facets: bool | None = None,
        fields: list[str] | None = None,
    ) -> BulkDataResponse:
        """Search for Bulk Data Products.

        Note: The USPTO Bulk Data API only supports full-text search in the query
        parameter. Field-specific queries (e.g., field:value) do not work despite
        being documented in the API swagger specification.

        Args:
            query: Full-text search query string. Field-specific syntax like
                "productIdentifier:value" is not supported by the API.
            offset: Number of product records to skip.
            limit: Number of product records to collect.
            facets: Whether to enable facets in the response.
            fields: List of field names to include in the response.

        Returns:
            BulkDataResponse: Response containing matching products.

        Examples:
            Search with full-text query:
            >>> response = client.search_products(query="Patent", limit=50)
        """
        params = {}

        # Add query parameter
        if query is not None:
            params["q"] = query
        if offset is not None:
            params["offset"] = str(offset)
        if limit is not None:
            params["limit"] = str(limit)
        if facets is not None:
            params["facets"] = str(facets).lower()
        if fields is not None:
            params["fields"] = ",".join(fields)

        result = self._make_request(
            method="GET",
            endpoint=self.ENDPOINTS["products_search"],
            params=params,
            response_class=BulkDataResponse,
        )

        # Since we specified response_class=BulkDataResponse, the result should be a BulkDataResponse
        assert isinstance(result, BulkDataResponse)
        return result
