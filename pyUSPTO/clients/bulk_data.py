"""
clients.bulk_data - Client for USPTO bulk data API

This module provides a client for interacting with the USPTO Open Data Portal (ODP)
Bulk Data API. It allows you to search for and download bulk data products.
"""

import os
import re
import time
from typing import Any, Dict, Iterator, List, Optional, Union
from urllib.parse import urlparse

from pyUSPTO.base import BaseUSPTOClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.bulk_data import (
    BulkDataProduct,
    BulkDataResponse,
    DatasetField,
    DatasetFieldCollection,
    DatasetInfo,
    FileData,
)


class BulkDataClient(BaseUSPTOClient[BulkDataResponse]):
    """Client for interacting with the USPTO bulk data API."""

    # Centralized endpoint configuration
    ENDPOINTS = {
        # Products endpoints
        "products_search": "products/search",
        "product_by_id": "products/{product_id}",
        # Dataset endpoints
        "dataset_info": "datasets/{dataset_id}",
        "dataset_fields": "datasets/{dataset_id}/fields",
        # Download endpoint
        "download_product_file": "products/files/{product_id}/{file_name}",
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
        # Extract pagination parameters if present
        offset = int(params.get("offset", 0)) if params else 0
        limit = int(params.get("limit", 25)) if params else 25

        # Get the raw API response data
        result = self._make_request(
            method="GET",
            endpoint=self.ENDPOINTS["products_search"],
            params=params,
        )

        if isinstance(result, dict):
            # Create a response with pagination context
            response = BulkDataResponse.from_dict_with_pagination(
                data=result,
                client=self,
                method_name="get_products",
                params=params.copy() if params else {},
                offset=offset,
                limit=limit,
            )
            return response
        else:
            # If we didn't get a dict, create a regular response without pagination context
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

    def download_product_file(
        self, product_id: str, file_name: str, destination: str
    ) -> str:
        """
        Download a file from a specific product.

        Args:
            product_id: The product identifier
            file_name: The name of the file to download
            destination: Directory where the file should be saved

        Returns:
            Path to the downloaded file
        """
        import os
        import re
        from typing import cast

        import requests

        # Format the endpoint
        endpoint = self.ENDPOINTS["download_product_file"].format(
            product_id=product_id, file_name=file_name
        )

        # Make the request using the base client method with stream=True
        # This ensures we get a requests.Response object
        response = cast(
            requests.Response,
            self._make_request(method="GET", endpoint=endpoint, stream=True),
        )

        # Parse the redirect URL from the response text
        redirect_match = re.search(
            r'redirect URL to download:\s*(https?://[^\s"]+)', response.text
        )

        if not redirect_match:
            raise ValueError(
                f"Could not find redirect URL in response: {response.text[:100]}..."
            )

        # Extract the redirect URL
        redirect_url = redirect_match.group(1)

        # Follow the redirect to download the file
        file_response = requests.get(redirect_url, stream=True)

        # Create destination directory if it doesn't exist
        if not os.path.exists(destination):
            os.makedirs(destination)

        # Save the file
        file_path = os.path.join(destination, file_name)
        with open(file_path, "wb") as f:
            for chunk in file_response.iter_content(chunk_size=8192):
                if chunk:
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

    def get_dataset_info(self, dataset_id: str) -> DatasetInfo:
        """
        Get information about a specific dataset.

        Args:
            dataset_id: The dataset identifier

        Returns:
            DatasetInfo object containing dataset information
        """
        endpoint = self.ENDPOINTS["dataset_info"].format(dataset_id=dataset_id)

        result = self._make_request(
            method="GET",
            endpoint=endpoint,
        )

        if isinstance(result, dict):
            dataset_info = DatasetInfo.from_dict(result)
            # Attach client for lazy loading
            dataset_info._client = self
            return dataset_info
        else:
            raise TypeError(f"Expected dict, got {type(result)}")

    def get_dataset_fields(self, dataset_id: str) -> DatasetFieldCollection:
        """
        Get fields for a specific dataset.

        Args:
            dataset_id: The dataset identifier

        Returns:
            DatasetFieldCollection object containing field information
        """
        endpoint = self.ENDPOINTS["dataset_fields"].format(dataset_id=dataset_id)

        result = self._make_request(
            method="GET",
            endpoint=endpoint,
        )

        if isinstance(result, dict):
            fields = DatasetFieldCollection.from_dict(result)
            # Attach client for future reference
            fields._client = self
            return fields
        else:
            raise TypeError(f"Expected dict, got {type(result)}")

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
            BulkDataResponse object containing matching products with pagination support
        """
        # Set default pagination values
        offset_value = 0 if offset is None else offset
        limit_value = 25 if limit is None else limit

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

        # Get the raw API response data
        result = self._make_request(
            method="GET",
            endpoint=self.ENDPOINTS["products_search"],
            params=params,
        )

        if isinstance(result, dict):
            # Create method parameters for pagination
            method_params = {
                "query": query,
                "product_title": product_title,
                "product_description": product_description,
                "product_short_name": product_short_name,
                "from_date": from_date,
                "to_date": to_date,
                "categories": categories,
                "labels": labels,
                "datasets": datasets,
                "file_types": file_types,
                "include_files": include_files,
                "latest": latest,
                "facets": facets,
            }

            # Add pagination parameters if provided
            if offset is not None:
                method_params["offset"] = offset
            if limit is not None:
                method_params["limit"] = limit

            # Create response with pagination context
            response = BulkDataResponse.from_dict_with_pagination(
                data=result,
                client=self,
                method_name="search_products",
                params=method_params,
                offset=offset_value,
                limit=limit_value,
            )
            return response
        elif isinstance(result, BulkDataResponse):
            # If we already have a BulkDataResponse, add pagination context
            result._client = self
            result._method_name = "search_products"
            result._params = {
                "query": query,
                "product_title": product_title,
                "product_description": product_description,
                "product_short_name": product_short_name,
                "from_date": from_date,
                "to_date": to_date,
                "categories": categories,
                "labels": labels,
                "datasets": datasets,
                "file_types": file_types,
                "include_files": include_files,
                "latest": latest,
                "facets": facets,
            }
            if offset is not None:
                result._params["offset"] = offset
            if limit is not None:
                result._params["limit"] = limit
            result._offset = offset_value
            result._limit = limit_value
            return result
        else:
            raise TypeError(f"Expected dict or BulkDataResponse, got {type(result)}")
