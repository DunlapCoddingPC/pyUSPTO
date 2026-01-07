"""
Tests for the bulk_data module.

This module contains tests for the BulkDataClient class, including core functionality,
model handling, edge cases, and response handling.
"""

import os
from datetime import date
from typing import Any
from unittest.mock import MagicMock, mock_open, patch

import pytest
import requests

from pyUSPTO.clients import BulkDataClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.bulk_data import (
    BulkDataProduct,
    BulkDataResponse,
    FileData,
    ProductFileBag,
)


class TestBulkDataModels:
    """Tests for the bulk data model classes."""

    def test_file_data_from_dict(self) -> None:
        """Test FileData.from_dict method."""
        data = {
            "fileName": "test.zip",
            "fileSize": 1024,
            "fileDataFromDate": "2023-01-01",
            "fileDataToDate": "2023-12-31",
            "fileTypeText": "ZIP",
            "fileReleaseDate": "2024-01-01",
            "fileDownloadURI": "https://example.com/test.zip",
            "fileDate": "2023-12-31",
            "fileLastModifiedDateTime": "2023-12-31T23:59:59",
        }

        file_data = FileData.from_dict(data, product_identifier="PRODUCT1")

        assert file_data.file_name == "test.zip"
        assert file_data.file_size == 1024
        assert file_data.product_identifier == "PRODUCT1"
        assert file_data.file_data_from_date == date(2023, 1, 1)
        assert file_data.file_data_to_date == date(2023, 12, 31)
        assert file_data.file_type_text == "ZIP"
        assert file_data.file_release_date == date(2024, 1, 1)
        assert file_data.file_download_uri == "https://example.com/test.zip"
        assert file_data.file_date == date(2023, 12, 31)
        assert file_data.file_last_modified_date_time is not None  # Datetime object, not string

    def test_product_file_bag_from_dict(self) -> None:
        """Test ProductFileBag.from_dict method."""
        data = {
            "count": 2,
            "fileDataBag": [
                {
                    "fileName": "test1.zip",
                    "fileSize": 512,
                    "fileDataFromDate": "2023-01-01",
                    "fileDataToDate": "2023-06-30",
                    "fileTypeText": "ZIP",
                    "fileReleaseDate": "2023-07-01",
                },
                {
                    "fileName": "test2.zip",
                    "fileSize": 512,
                    "fileDataFromDate": "2023-07-01",
                    "fileDataToDate": "2023-12-31",
                    "fileTypeText": "ZIP",
                    "fileReleaseDate": "2024-01-01",
                },
            ],
        }

        product_file_bag = ProductFileBag.from_dict(data, product_identifier="PRODUCT1")

        assert product_file_bag.count == 2
        assert len(product_file_bag.file_data_bag) == 2
        assert product_file_bag.file_data_bag[0].file_name == "test1.zip"
        assert product_file_bag.file_data_bag[1].file_name == "test2.zip"
        assert product_file_bag.file_data_bag[0].product_identifier == "PRODUCT1"
        assert product_file_bag.file_data_bag[1].product_identifier == "PRODUCT1"

    def test_bulk_data_product_from_dict(self) -> None:
        """Test BulkDataProduct.from_dict method."""
        data = {
            "productIdentifier": "PRODUCT1",
            "productDescriptionText": "Test Product",
            "productTitleText": "Test Product Title",
            "productFrequencyText": "Weekly",
            "daysOfWeekText": "Monday",
            "productLabelArrayText": ["Patent", "Test"],
            "productDatasetArrayText": ["Patents"],
            "productDatasetCategoryArrayText": ["Patent"],
            "productFromDate": "2023-01-01",
            "productToDate": "2023-12-31",
            "productTotalFileSize": 1024,
            "productFileTotalQuantity": 2,
            "lastModifiedDateTime": "2023-12-31T23:59:59",
            "mimeTypeIdentifierArrayText": ["application/zip"],
            "productFileBag": {
                "count": 2,
                "fileDataBag": [
                    {
                        "fileName": "test1.zip",
                        "fileSize": 512,
                        "fileDataFromDate": "2023-01-01",
                        "fileDataToDate": "2023-06-30",
                        "fileTypeText": "ZIP",
                        "fileReleaseDate": "2023-07-01",
                    },
                    {
                        "fileName": "test2.zip",
                        "fileSize": 512,
                        "fileDataFromDate": "2023-07-01",
                        "fileDataToDate": "2023-12-31",
                        "fileTypeText": "ZIP",
                        "fileReleaseDate": "2024-01-01",
                    },
                ],
            },
        }

        product = BulkDataProduct.from_dict(data)

        assert product.product_identifier == "PRODUCT1"
        assert product.product_description_text == "Test Product"
        assert product.product_title_text == "Test Product Title"
        assert product.product_frequency_text == "Weekly"
        assert product.days_of_week_text == "Monday"
        assert product.product_label_array_text == ["Patent", "Test"]
        assert product.product_dataset_array_text == ["Patents"]
        assert product.product_dataset_category_array_text == ["Patent"]
        assert product.product_from_date == date(2023, 1, 1)
        assert product.product_to_date == date(2023, 12, 31)
        assert product.product_total_file_size == 1024
        assert product.product_file_total_quantity == 2
        assert product.last_modified_date_time is not None  # Datetime object, not string
        assert product.mime_type_identifier_array_text == ["application/zip"]
        assert product.product_file_bag is not None
        assert product.product_file_bag.count == 2
        assert len(product.product_file_bag.file_data_bag) == 2

    def test_bulk_data_response_from_dict(self) -> None:
        """Test BulkDataResponse.from_dict method."""
        data = {
            "count": 2,
            "bulkDataProductBag": [
                {
                    "productIdentifier": "PRODUCT1",
                    "productDescriptionText": "Test Product 1",
                    "productTitleText": "Test Product 1 Title",
                    "productFrequencyText": "Weekly",
                    "productLabelArrayText": ["Patent", "Test"],
                    "productDatasetArrayText": ["Patents"],
                    "productDatasetCategoryArrayText": ["Patent"],
                    "productFromDate": "2023-01-01",
                    "productToDate": "2023-12-31",
                    "productTotalFileSize": 1024,
                    "productFileTotalQuantity": 2,
                    "lastModifiedDateTime": "2023-12-31T23:59:59",
                    "mimeTypeIdentifierArrayText": ["application/zip"],
                    "productFileBag": {
                        "count": 1,
                        "fileDataBag": [
                            {
                                "fileName": "test1.zip",
                                "fileSize": 512,
                                "fileDataFromDate": "2023-01-01",
                                "fileDataToDate": "2023-06-30",
                                "fileTypeText": "ZIP",
                                "fileReleaseDate": "2023-07-01",
                            }
                        ],
                    },
                },
                {
                    "productIdentifier": "PRODUCT2",
                    "productDescriptionText": "Test Product 2",
                    "productTitleText": "Test Product 2 Title",
                    "productFrequencyText": "Monthly",
                    "productLabelArrayText": ["Trademark", "Test"],
                    "productDatasetArrayText": ["Trademarks"],
                    "productDatasetCategoryArrayText": ["Trademark"],
                    "productFromDate": "2023-01-01",
                    "productToDate": "2023-12-31",
                    "productTotalFileSize": 2048,
                    "productFileTotalQuantity": 1,
                    "lastModifiedDateTime": "2023-12-31T23:59:59",
                    "mimeTypeIdentifierArrayText": ["application/zip"],
                },
            ],
        }

        response = BulkDataResponse.from_dict(data)

        assert response.count == 2
        assert len(response.bulk_data_product_bag) == 2
        assert response.bulk_data_product_bag[0].product_identifier == "PRODUCT1"
        assert response.bulk_data_product_bag[1].product_identifier == "PRODUCT2"
        assert response.bulk_data_product_bag[0].product_file_bag is not None
        assert response.bulk_data_product_bag[0].product_file_bag.count == 1
        assert len(response.bulk_data_product_bag[0].product_file_bag.file_data_bag) == 1
        assert response.bulk_data_product_bag[1].product_file_bag is None


class TestBulkDataClientInit:
    """Tests for the initialization of the BulkDataClient class."""

    def test_init_with_api_key(self) -> None:
        """Test initialization with direct API key."""
        client = BulkDataClient(api_key="test_key")
        assert client._api_key == "test_key"
        assert client.base_url == "https://api.uspto.gov"
        assert client.config is not None
        assert client.config.api_key == "test_key"

    def test_init_with_custom_base_url(self) -> None:
        """Test initialization with custom base URL."""
        client = BulkDataClient(
            api_key="test_key", base_url="https://custom.api.test.com"
        )
        assert client.base_url == "https://custom.api.test.com"

    def test_init_with_config(self) -> None:
        """Test initialization with config object."""
        config = USPTOConfig(
            api_key="config_key",
            bulk_data_base_url="https://config.api.test.com",
        )
        client = BulkDataClient(config=config)
        assert client._api_key == "config_key"
        assert client.base_url == "https://config.api.test.com"
        assert client.config is config

    def test_init_with_api_key_and_config(self) -> None:
        """Test initialization with both API key and config."""
        config = USPTOConfig(
            api_key="config_key",
            bulk_data_base_url="https://config.api.test.com",
        )
        client = BulkDataClient(api_key="direct_key", config=config)
        assert client._api_key == "direct_key"
        assert client.base_url == "https://config.api.test.com"


class TestBulkDataClientCore:
    """Tests for the core functionality of the BulkDataClient class."""

    def test_search_products_basic(
        self, mock_bulk_data_client: BulkDataClient, bulk_data_sample: dict[str, Any]
    ) -> None:
        """Test search_products method with basic query."""
        # Setup
        mock_response = MagicMock()
        mock_response.json.return_value = bulk_data_sample

        # Create a dedicated mock session
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response

        # Replace the client's session with our mock
        mock_bulk_data_client.session = mock_session

        # Test search_products with basic query
        response = mock_bulk_data_client.search_products(query="Patent")

        # Verify
        mock_session.get.assert_called_once_with(
            url=f"{mock_bulk_data_client.base_url}/api/v1/datasets/products/search",
            params={"q": "Patent"},
            stream=False,
            timeout=(10.0, 30.0),
        )
        assert isinstance(response, BulkDataResponse)
        assert response.count == 2
        assert len(response.bulk_data_product_bag) == 2

    def test_get_product_by_id(
        self, mock_bulk_data_client: BulkDataClient, bulk_data_sample: dict[str, Any]
    ) -> None:
        """Test get_product_by_id method."""
        # Setup
        product_id = "PRODUCT1"
        mock_response = MagicMock()
        # API returns a BulkDataResponse wrapper
        mock_response.json.return_value = bulk_data_sample

        # Create a dedicated mock session
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response

        # Replace the client's session with our mock
        mock_bulk_data_client.session = mock_session

        # Test get_product_by_id
        product = mock_bulk_data_client.get_product_by_id(
            product_id=product_id,
            file_data_from_date="2023-01-01",
            file_data_to_date="2023-12-31",
            offset=0,
            limit=10,
            include_files=True,
            latest=True,
        )

        # Verify
        mock_session.get.assert_called_once_with(
            url=f"{mock_bulk_data_client.base_url}/api/v1/datasets/products/{product_id}",
            params={
                "fileDataFromDate": "2023-01-01",
                "fileDataToDate": "2023-12-31",
                "offset": "0",
                "limit": "10",
                "includeFiles": "true",
                "latest": "true",
            },
            stream=False,
            timeout=(10.0, 30.0),
        )
        assert isinstance(product, BulkDataProduct)
        assert product.product_identifier == "PRODUCT1"

    def test_download_file(self, mock_bulk_data_client: BulkDataClient) -> None:
        """Test download_file method."""
        # Setup
        file_data = FileData(
            file_name="test.tar.gz",
            file_size=1024,
            product_identifier="PRODUCT1",
            file_data_from_date=date(2023, 1, 1),
            file_data_to_date=date(2023, 12, 31),
            file_type_text="TAR",
            file_release_date=date(2024, 1, 1),
        )
        destination = "./downloads"

        # Mock the _download_and_extract method
        with patch.object(
            mock_bulk_data_client, "_download_and_extract", return_value="./downloads/extracted"
        ) as mock_download:
            # Test download_file with extraction (default)
            file_path = mock_bulk_data_client.download_file(
                file_data=file_data, destination=destination
            )

            # Verify
            expected_url = f"{mock_bulk_data_client.base_url}/api/v1/datasets/products/files/PRODUCT1/test.tar.gz"
            mock_download.assert_called_once_with(
                url=expected_url,
                destination=destination,
                file_name="test.tar.gz",
                overwrite=False,
            )
            assert file_path == "./downloads/extracted"

    def test_download_file_without_extraction(
        self, mock_bulk_data_client: BulkDataClient
    ) -> None:
        """Test download_file method without extraction."""
        # Setup
        file_data = FileData(
            file_name="test.zip",
            file_size=1024,
            product_identifier="PRODUCT1",
            file_data_from_date=date(2023, 1, 1),
            file_data_to_date=date(2023, 12, 31),
            file_type_text="ZIP",
            file_release_date=date(2024, 1, 1),
        )
        destination = "./downloads"

        # Mock the _download_file method
        with patch.object(
            mock_bulk_data_client, "_download_file", return_value="./downloads/test.zip"
        ) as mock_download:
            file_path = mock_bulk_data_client.download_file(
                file_data=file_data, destination=destination, extract=False
            )

            # Verify
            expected_url = f"{mock_bulk_data_client.base_url}/api/v1/datasets/products/files/PRODUCT1/test.zip"
            mock_download.assert_called_once_with(
                url=expected_url,
                destination=destination,
                file_name="test.zip",
                overwrite=False,
            )
            assert file_path == "./downloads/test.zip"

    def test_search_products_all_params(
        self, mock_bulk_data_client: BulkDataClient, bulk_data_sample: dict[str, Any]
    ) -> None:
        """Test search_products method with all available parameters."""
        # Setup
        mock_response = MagicMock()
        mock_response.json.return_value = bulk_data_sample

        # Create a dedicated mock session
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response

        # Replace the client's session with our mock
        mock_bulk_data_client.session = mock_session

        # Test search_products with all available parameters
        response = mock_bulk_data_client.search_products(
            query="Patent",
            offset=0,
            limit=10,
            facets=True,
            fields=["productIdentifier", "productTitleText"],
        )

        # Verify
        mock_session.get.assert_called_once_with(
            url=f"{mock_bulk_data_client.base_url}/api/v1/datasets/products/search",
            params={
                "q": "Patent",
                "offset": "0",
                "limit": "10",
                "facets": "true",
                "fields": "productIdentifier,productTitleText",
            },
            stream=False,
            timeout=(10.0, 30.0),
        )
        assert isinstance(response, BulkDataResponse)
        assert response.count == 2

    def test_paginate_products(self, mock_bulk_data_client: BulkDataClient) -> None:
        """Test paginate_products method."""
        # This is just a wrapper around paginate_results, so we'll test that it calls
        # paginate_results with the correct parameters

        # Create a dedicated mock for paginate_results
        mock_paginate_results = MagicMock()
        mock_paginate_results.return_value = iter([])

        with patch.object(
            mock_bulk_data_client, "paginate_results", mock_paginate_results
        ):
            result = mock_bulk_data_client.paginate_products(param="value")
            list(result)  # Consume the iterator

            # Verify
            mock_paginate_results.assert_called_once_with(
                method_name="search_products",
                response_container_attr="bulk_data_product_bag",
                post_body=None,
                param="value",
            )


class TestBulkDataClientEdgeCases:
    """Tests for edge cases in the BulkDataClient class."""

    def test_get_product_by_id_not_found(self) -> None:
        """Test get_product_by_id when product is not in response."""
        # Setup
        client = BulkDataClient(api_key="test_key")

        # Mock _make_request to return an empty BulkDataResponse
        empty_response = BulkDataResponse(count=0, bulk_data_product_bag=[])
        with patch.object(client, "_make_request", return_value=empty_response):
            # Test with product not found
            with pytest.raises(ValueError, match="Product 'TEST' not found"):
                client.get_product_by_id(product_id="TEST")

    def test_get_product_by_id_wrong_product_returned(self) -> None:
        """Test get_product_by_id when API returns wrong product."""
        # Setup
        client = BulkDataClient(api_key="test_key")

        # Create response with different product ID
        wrong_product = BulkDataProduct(
            product_identifier="WRONG_ID",
            product_title_text="Wrong Product",
            product_description_text="Wrong Description",
            product_frequency_text="Daily",
        )
        response = BulkDataResponse(count=1, bulk_data_product_bag=[wrong_product])

        with patch.object(client, "_make_request", return_value=response):
            # Should still return the product but issue a warning
            with pytest.warns(match="API returned product 'WRONG_ID' but requested 'TEST'"):
                product = client.get_product_by_id(product_id="TEST")
                assert product.product_identifier == "WRONG_ID"

    def test_download_file_with_custom_filename(
        self, mock_bulk_data_client: BulkDataClient
    ) -> None:
        """Test download_file with custom filename override."""
        # Setup
        file_data = FileData(
            file_name="original.zip",
            file_size=1024,
            product_identifier="PRODUCT1",
            file_data_from_date=date(2023, 1, 1),
            file_data_to_date=date(2023, 12, 31),
            file_type_text="ZIP",
            file_release_date=date(2024, 1, 1),
        )
        destination = "./downloads"

        # Mock the _download_file method
        with patch.object(
            mock_bulk_data_client, "_download_file", return_value="./downloads/custom.zip"
        ) as mock_download:
            file_path = mock_bulk_data_client.download_file(
                file_data=file_data,
                destination=destination,
                file_name="custom.zip",
                extract=False,
            )

            # Verify custom filename is used
            expected_url = f"{mock_bulk_data_client.base_url}/api/v1/datasets/products/files/PRODUCT1/custom.zip"
            mock_download.assert_called_once_with(
                url=expected_url,
                destination=destination,
                file_name="custom.zip",
                overwrite=False,
            )
            assert file_path == "./downloads/custom.zip"

    def test_download_file_with_overwrite(
        self, mock_bulk_data_client: BulkDataClient
    ) -> None:
        """Test download_file with overwrite flag."""
        # Setup
        file_data = FileData(
            file_name="test.zip",
            file_size=1024,
            product_identifier="PRODUCT1",
            file_data_from_date=date(2023, 1, 1),
            file_data_to_date=date(2023, 12, 31),
            file_type_text="ZIP",
            file_release_date=date(2024, 1, 1),
        )

        # Mock the _download_and_extract method
        with patch.object(
            mock_bulk_data_client, "_download_and_extract", return_value="./test.zip"
        ) as mock_download:
            mock_bulk_data_client.download_file(file_data=file_data, overwrite=True)

            # Verify overwrite is passed through
            assert mock_download.call_args[1]["overwrite"] is True


class TestBulkDataResponseHandling:
    """Tests for response format handling in the BulkDataClient class."""

    def test_search_products_with_query_and_limit(
        self, mock_bulk_data_client: BulkDataClient, bulk_data_sample: dict[str, Any]
    ) -> None:
        """Test search_products with query and limit parameters."""
        # Setup
        mock_response = MagicMock()
        mock_response.json.return_value = bulk_data_sample

        # Create a dedicated mock session
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response

        # Replace the client's session with our mock
        mock_bulk_data_client.session = mock_session

        # Test search_products with query and limit
        response = mock_bulk_data_client.search_products(
            query="Patent",
            limit=10,
        )

        # Verify the parameters were passed correctly
        call_args = mock_session.get.call_args
        assert "params" in call_args[1]
        params = call_args[1]["params"]
        assert params["q"] == "Patent"
        assert params["limit"] == "10"
        assert isinstance(response, BulkDataResponse)

    def test_search_products_with_offset_and_facets(
        self, mock_bulk_data_client: BulkDataClient, bulk_data_sample: dict[str, Any]
    ) -> None:
        """Test search_products with offset and facets parameters."""
        # Setup
        mock_response = MagicMock()
        mock_response.json.return_value = bulk_data_sample

        # Create a dedicated mock session
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response

        # Replace the client's session with our mock
        mock_bulk_data_client.session = mock_session

        # Test search_products with offset and facets
        response = mock_bulk_data_client.search_products(
            query="Patent",
            offset=25,
            facets=True,
        )

        # Verify the parameters were passed correctly
        call_args = mock_session.get.call_args
        params = call_args[1]["params"]
        assert params["q"] == "Patent"
        assert params["offset"] == "25"
        assert params["facets"] == "true"
        assert isinstance(response, BulkDataResponse)

    def test_search_products_with_fields(
        self, mock_bulk_data_client: BulkDataClient, bulk_data_sample: dict[str, Any]
    ) -> None:
        """Test search_products with fields parameter."""
        # Setup
        mock_response = MagicMock()
        mock_response.json.return_value = bulk_data_sample
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response
        mock_bulk_data_client.session = mock_session

        # Test search_products with fields
        response = mock_bulk_data_client.search_products(
            query="Patent",
            fields=["productIdentifier", "productTitleText"],
        )

        # Verify the fields parameter was joined correctly
        call_args = mock_session.get.call_args
        params = call_args[1]["params"]
        assert params["q"] == "Patent"
        assert params["fields"] == "productIdentifier,productTitleText"
        assert isinstance(response, BulkDataResponse)
