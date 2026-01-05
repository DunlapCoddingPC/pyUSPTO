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
        "download_file": "api/v1/datasets/products/files/{file_download_uri}",
    }

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        config: USPTOConfig | None = None,
    ):
        """Initialize the BulkDataClient.

        Args:
            api_key: Optional API key for authentication
            base_url: The base URL of the API, defaults to config.bulk_data_base_url or "https://api.uspto.gov/api/v1/datasets"
            config: Optional USPTOConfig instance
        """
        # Use config if provided, otherwise create default config
        self.config = config or USPTOConfig(api_key=api_key)

        # Use provided API key or get from config
        api_key = api_key or self.config.api_key

        # Use provided base_url or get from config
        base_url = base_url or self.config.bulk_data_base_url

        super().__init__(api_key=api_key, base_url=base_url, config=self.config)

    def get_products(self, params: dict[str, Any] | None = None) -> BulkDataResponse:
        """Get a list of bulk data products.

        This method is deprecated. Use search_products instead.

        Args:
            params: Optional query parameters

        Returns:
            BulkDataResponse object containing the API response
        """
        result = self._make_request(
            method="GET",
            endpoint=self.ENDPOINTS["products_search"],
            params=params,
            response_class=BulkDataResponse,
        )
        # Since we specified response_class=BulkDataResponse, the result should be a BulkDataResponse
        assert isinstance(result, BulkDataResponse)
        return result

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
            file_data: FileData object containing download URI and metadata.
            destination: Directory to save/extract to. Defaults to current directory.
            file_name: Override filename. Defaults to file_data.file_name.
            overwrite: Whether to overwrite existing files. Defaults to False.
            extract: Whether to auto-extract archives. Defaults to True.

        Returns:
            str: Path to downloaded file or extracted directory.

        Raises:
            ValueError: If file_data has no download URI.
            FileExistsError: If file exists and overwrite=False.

        Examples:
            Download and extract a file:
            >>> product = client.get_product_by_id("product-123", include_files=True)
            >>> file_data = product.product_file_bag.file_data_bag[0]
            >>> path = client.download_file(file_data, destination="./downloads")

            Download without extraction:
            >>> path = client.download_file(file_data, extract=False)
        """
        if not file_data.file_download_uri:
            raise ValueError("FileData has no download URI")

        # Use file_name from file_data if not provided
        default_file_name = file_name or file_data.file_name

        # Use base class helpers based on extract flag
        if extract:
            return self._download_and_extract(
                url=file_data.file_download_uri,
                destination=destination,
                file_name=default_file_name,
                overwrite=overwrite,
            )
        else:
            return self._download_file(
                url=file_data.file_download_uri,
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
        product_title: str | None = None,
        product_description: str | None = None,
        product_short_name: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        categories: list[str] | None = None,
        labels: list[str] | None = None,
        datasets: list[str] | None = None,
        file_types: list[str] | None = None,
        offset: int | None = None,
        limit: int | None = None,
        include_files: bool | None = None,
        latest: bool | None = None,
        facets: bool | None = None,
        # Convenience query parameters
        product_id_q: str | None = None,
        product_title_q: str | None = None,
        product_description_q: str | None = None,
        dataset_q: str | None = None,
        category_q: str | None = None,
        label_q: str | None = None,
        file_type_q: str | None = None,
        from_date_q: str | None = None,
        to_date_q: str | None = None,
        additional_query_params: dict[str, Any] | None = None,
    ) -> BulkDataResponse:
        """Search for products with various filters.

        This method supports both direct parameter filters and convenience query
        parameters that are automatically combined into a query string.

        Args:
            query: Direct query string in USPTO search syntax.
            product_title: Filter by product title (direct parameter).
            product_description: Filter by product description (direct parameter).
            product_short_name: Filter by product identifier (direct parameter).
            from_date: Filter products with data from this date (YYYY-MM-DD).
            to_date: Filter products with data until this date (YYYY-MM-DD).
            categories: Filter by dataset categories.
            labels: Filter by product labels.
            datasets: Filter by datasets.
            file_types: Filter by file types.
            offset: Number of product records to skip.
            limit: Number of product records to collect.
            include_files: Whether to include product files in the response.
            latest: Whether to return only the latest product file for each product.
            facets: Whether to enable facets in the response.
            product_id_q: Filter by product identifier (query syntax).
            product_title_q: Filter by product title (query syntax).
            product_description_q: Filter by description (query syntax).
            dataset_q: Filter by dataset name (query syntax).
            category_q: Filter by category (query syntax).
            label_q: Filter by label (query syntax).
            file_type_q: Filter by file type (query syntax).
            from_date_q: Filter products from date (YYYY-MM-DD, query syntax).
            to_date_q: Filter products to date (YYYY-MM-DD, query syntax).
            additional_query_params: Additional custom query parameters.

        Returns:
            BulkDataResponse: Response containing matching products.

        Examples:
            Search with direct query:
            >>> response = client.search_products(query="productTitle:Patent")

            Search with convenience parameters:
            >>> response = client.search_products(
            ...     dataset_q="Patents",
            ...     from_date_q="2023-01-01",
            ...     limit=50
            ... )

            Search with direct parameters:
            >>> response = client.search_products(
            ...     product_title="Patent Grant",
            ...     categories=["Patents"],
            ...     include_files=True
            ... )
        """
        params = {}
        final_q = query

        # Build query from convenience parameters
        if final_q is None:
            q_parts = []
            if product_id_q:
                q_parts.append(f"productIdentifier:{product_id_q}")
            if product_title_q:
                q_parts.append(f"productTitleText:{product_title_q}")
            if product_description_q:
                q_parts.append(f"productDescriptionText:{product_description_q}")
            if dataset_q:
                q_parts.append(f"productDatasetArrayText:{dataset_q}")
            if category_q:
                q_parts.append(f"productDatasetCategoryArrayText:{category_q}")
            if label_q:
                q_parts.append(f"productLabelArrayText:{label_q}")
            if file_type_q:
                q_parts.append(f"mimeTypeIdentifierArrayText:{file_type_q}")

            # Handle date range
            if from_date_q and to_date_q:
                q_parts.append(f"productFromDate:[{from_date_q} TO {to_date_q}]")
            elif from_date_q:
                q_parts.append(f"productFromDate:>={from_date_q}")
            elif to_date_q:
                q_parts.append(f"productToDate:<={to_date_q}")

            if q_parts:
                final_q = " AND ".join(q_parts)

        # Add query parameter
        if final_q is not None:
            params["q"] = final_q

        # Add direct filter parameters
        if product_title:
            params["productTitle"] = product_title
        if product_description:
            params["productDescription"] = product_description
        if product_short_name:
            params["productShortName"] = product_short_name
        if from_date:
            params["fromDate"] = from_date
        if to_date:
            params["toDate"] = to_date
        if categories:
            params["categories"] = ",".join(categories)
        if labels:
            params["labels"] = ",".join(labels)
        if datasets:
            params["datasets"] = ",".join(datasets)
        if file_types:
            params["fileTypes"] = ",".join(file_types)
        if offset is not None:
            params["offset"] = str(offset)
        if limit is not None:
            params["limit"] = str(limit)
        if include_files is not None:
            params["includeFiles"] = str(include_files).lower()
        if latest is not None:
            params["latest"] = str(latest).lower()
        if facets is not None:
            params["facets"] = str(facets).lower()

        # Add additional custom parameters
        if additional_query_params:
            params.update(additional_query_params)

        result = self._make_request(
            method="GET",
            endpoint=self.ENDPOINTS["products_search"],
            params=params,
            response_class=BulkDataResponse,
        )

        # Since we specified response_class=BulkDataResponse, the result should be a BulkDataResponse
        assert isinstance(result, BulkDataResponse)
        return result
