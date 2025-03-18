"""
clients.bulk_data - Client for USPTO bulk data API

This module provides a client for interacting with the USPTO Open Data Portal (ODP)
Bulk Data API. It allows you to search for and download bulk data products.
"""

import os
from typing import Any, Dict, Iterator, List, Optional
from urllib.parse import urlparse

from pyUSPTO.clients.base import BaseUSPTOClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.bulk_data import BulkDataProduct, BulkDataResponse, FileData


class BulkDataClient(BaseUSPTOClient[BulkDataResponse]):
    """Client for interacting with the USPTO bulk data API."""

    # Centralized endpoint configuration
    ENDPOINTS = {
        # Products endpoints
        "products_search": "products/search",
        "product_by_id": "products/{product_id}",
        # Download endpoint
        "download_file": "{file_download_uri}",
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        config: Optional[USPTOConfig] = None,
    ):
        """
        Initialize the BulkDataClient.

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

        super().__init__(api_key=api_key, base_url=base_url)

    def get_products(self, params: Optional[Dict[str, Any]] = None) -> BulkDataResponse:
        """
        Get a list of bulk data products.

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
        file_data_from_date: Optional[str] = None,
        file_data_to_date: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        include_files: Optional[bool] = None,
        latest: Optional[bool] = None,
    ) -> BulkDataProduct:
        """
        Get a specific bulk data product by ID.

        Args:
            product_id: The product identifier
            file_data_from_date: Filter files by data from date (YYYY-MM-DD)
            file_data_to_date: Filter files by data to date (YYYY-MM-DD)
            offset: Number of product file records to skip
            limit: Number of product file records to collect
            include_files: Whether to include product files in the response
            latest: Whether to return only the latest product file

        Returns:
            BulkDataProduct object containing the product data
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

        result = self._make_request(method="GET", endpoint=endpoint, params=params)

        # Process result based on its type
        if isinstance(result, BulkDataResponse):
            # If it's a BulkDataResponse, extract the matching product
            for product in result.bulk_data_product_bag:
                if product.product_identifier == product_id:
                    return product
            raise ValueError(f"Product with ID {product_id} not found in response")

        # If we get here, result is not a BulkDataResponse
        if isinstance(result, dict):
            data = result
        else:
            data = result.json()

        # Handling different response formats
        if isinstance(data, dict) and "bulkDataProductBag" in data:
            for product_data in data["bulkDataProductBag"]:
                if (
                    isinstance(product_data, dict)
                    and product_data.get("productIdentifier") == product_id
                ):
                    return BulkDataProduct.from_dict(product_data)
            raise ValueError(f"Product with ID {product_id} not found in response")
        else:
            if isinstance(data, dict):
                return BulkDataProduct.from_dict(data)
            else:
                raise TypeError(f"Expected dict, got {type(data)}")

    def download_file(self, file_data: FileData, destination: str) -> str:
        """
        Download a file from the API.

        Args:
            file_data: FileData object containing file information
            destination: Directory where the file should be saved

        Returns:
            Path to the downloaded file
        """
        if not file_data.file_download_uri:
            raise ValueError("No download URI available for this file")

        # For absolute URLs, split into base and path
        if file_data.file_download_uri.startswith("http"):
            # Parse the URL to extract components
            parsed_url = urlparse(file_data.file_download_uri)

            # Use the scheme and netloc as the base URL
            custom_base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

            # Use the path as the endpoint (remove leading slash)
            endpoint = parsed_url.path.lstrip("/")

            result = self._make_request(
                method="GET",
                endpoint=endpoint,
                stream=True,
                custom_base_url=custom_base_url,
            )
        else:
            # For relative URLs, use the endpoint directly
            result = self._make_request(
                method="GET",
                endpoint=file_data.file_download_uri,
                stream=True,
            )

        # Ensure we have a Response object with iter_content
        import requests

        if not isinstance(result, requests.Response):
            raise TypeError("Expected a Response object for streaming download")

        if not os.path.exists(destination):
            os.makedirs(destination)

        file_path = os.path.join(destination, file_data.file_name)

        with open(file_path, "wb") as f:
            for chunk in result.iter_content(chunk_size=8192):
                f.write(chunk)

        return file_path

    def paginate_products(self, **kwargs: Any) -> Iterator[BulkDataProduct]:
        """
        Paginate through all products matching the search criteria.

        Args:
            **kwargs: Keyword arguments to pass to search_products

        Yields:
            BulkDataProduct objects
        """
        return self.paginate_results(
            method_name="search_products",
            response_container_attr="bulk_data_product_bag",
            **kwargs,
        )

    def search_products(
        self,
        query: Optional[str] = None,
        product_title: Optional[str] = None,
        product_description: Optional[str] = None,
        product_short_name: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        categories: Optional[List[str]] = None,
        labels: Optional[List[str]] = None,
        datasets: Optional[List[str]] = None,
        file_types: Optional[List[str]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        include_files: Optional[bool] = None,
        latest: Optional[bool] = None,
        facets: Optional[bool] = None,
    ) -> BulkDataResponse:
        """
        Search for products with various filters.

        Args:
            query: Search text
            product_title: Filter by product title
            product_description: Filter by product description
            product_short_name: Filter by product identifier (short name)
            from_date: Filter products with data from this date (YYYY-MM-DD)
            to_date: Filter products with data until this date (YYYY-MM-DD)
            categories: Filter by dataset categories
            labels: Filter by product labels
            datasets: Filter by datasets
            file_types: Filter by file types
            offset: Number of product records to skip
            limit: Number of product records to collect
            include_files: Whether to include product files in the response
            latest: Whether to return only the latest product file for each product
            facets: Whether to enable facets in the response

        Returns:
            BulkDataResponse object containing matching products
        """
        params = {}
        if query:
            params["q"] = query
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

        result = self._make_request(
            method="GET",
            endpoint=self.ENDPOINTS["products_search"],
            params=params,
            response_class=BulkDataResponse,
        )

        # Since we specified response_class=BulkDataResponse, the result should be a BulkDataResponse
        assert isinstance(result, BulkDataResponse)
        return result
