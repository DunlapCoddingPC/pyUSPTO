"""
Tests for the bulk_data module.

This module contains tests for the BulkDataClient class and related functionality.
"""

import os
from typing import Any, Dict
from unittest.mock import MagicMock, mock_open, patch

import pytest

from pyUSPTO.base import USPTOApiError
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

        file_data = FileData.from_dict(data)

        assert file_data.file_name == "test.zip"
        assert file_data.file_size == 1024
        assert file_data.file_data_from_date == "2023-01-01"
        assert file_data.file_data_to_date == "2023-12-31"
        assert file_data.file_type_text == "ZIP"
        assert file_data.file_release_date == "2024-01-01"
        assert file_data.file_download_uri == "https://example.com/test.zip"
        assert file_data.file_date == "2023-12-31"
        assert file_data.file_last_modified_date_time == "2023-12-31T23:59:59"

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

        product_file_bag = ProductFileBag.from_dict(data)

        assert product_file_bag.count == 2
        assert len(product_file_bag.file_data_bag) == 2
        assert product_file_bag.file_data_bag[0].file_name == "test1.zip"
        assert product_file_bag.file_data_bag[1].file_name == "test2.zip"

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
        assert product.product_from_date == "2023-01-01"
        assert product.product_to_date == "2023-12-31"
        assert product.product_total_file_size == 1024
        assert product.product_file_total_quantity == 2
        assert product.last_modified_date_time == "2023-12-31T23:59:59"
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
        assert response.bulk_data_product_bag[1].product_file_bag is not None
        assert response.bulk_data_product_bag[1].product_file_bag.count == 0


class TestBulkDataClient:
    """Tests for the BulkDataClient class."""

    def test_init(self) -> None:
        """Test initialization of the BulkDataClient."""
        # Test with direct API key
        client = BulkDataClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.base_url == "https://api.uspto.gov/api/v1/datasets"
        assert client.config is not None
        assert client.config.api_key == "test_key"

        # Test with custom base_url
        client = BulkDataClient(
            api_key="test_key", base_url="https://custom.api.test.com"
        )
        assert client.base_url == "https://custom.api.test.com"

        # Test with config
        config = USPTOConfig(
            api_key="config_key",
            bulk_data_base_url="https://config.api.test.com",
        )
        client = BulkDataClient(config=config)
        assert client.api_key == "config_key"
        assert client.base_url == "https://config.api.test.com"
        assert client.config is config

        # Test with both API key and config (API key should take precedence)
        client = BulkDataClient(api_key="direct_key", config=config)
        assert client.api_key == "direct_key"
        assert client.base_url == "https://config.api.test.com"

    def test_get_products(
        self, mock_bulk_data_client: BulkDataClient, bulk_data_sample: Dict[str, Any]
    ) -> None:
        """Test get_products method."""
        # Setup
        mock_response = MagicMock()
        mock_response.json.return_value = bulk_data_sample

        # Create a dedicated mock session
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response

        # Replace the client's session with our mock
        mock_bulk_data_client.session = mock_session

        # Test get_products
        response = mock_bulk_data_client.get_products(params={"param": "value"})

        # Verify
        mock_session.get.assert_called_once_with(
            url=f"{mock_bulk_data_client.base_url}/products/search",
            params={"param": "value"},
            stream=False,
        )
        assert isinstance(response, BulkDataResponse)
        assert response.count == 2
        assert len(response.bulk_data_product_bag) == 2

    def test_get_product_by_id(
        self, mock_bulk_data_client: BulkDataClient, bulk_data_sample: Dict[str, Any]
    ) -> None:
        """Test get_product_by_id method."""
        # Setup
        product_id = "PRODUCT1"
        mock_response = MagicMock()
        # Test with direct product response
        product_data = bulk_data_sample["bulkDataProductBag"][0]
        mock_response.json.return_value = product_data

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
            url=f"{mock_bulk_data_client.base_url}/products/{product_id}",
            params={
                "fileDataFromDate": "2023-01-01",
                "fileDataToDate": "2023-12-31",
                "offset": 0,
                "limit": 10,
                "includeFiles": "true",
                "latest": "true",
            },
            stream=False,
        )
        assert isinstance(product, BulkDataProduct)
        assert product.product_identifier == "PRODUCT1"

        # Reset mock for next test
        mock_session.reset_mock()

        # Test with bulkDataProductBag response
        mock_response.json.return_value = bulk_data_sample
        product = mock_bulk_data_client.get_product_by_id(product_id=product_id)
        assert isinstance(product, BulkDataProduct)
        assert product.product_identifier == "PRODUCT1"

        # Test with product not found in bulkDataProductBag
        with pytest.raises(
            ValueError, match=f"Product with ID UNKNOWN not found in response"
        ):
            mock_bulk_data_client.get_product_by_id(product_id="UNKNOWN")

    def test_download_file(self, mock_bulk_data_client: BulkDataClient) -> None:
        """Test download_file method."""
        # Setup
        file_data = FileData(
            file_name="test.zip",
            file_size=1024,
            file_data_from_date="2023-01-01",
            file_data_to_date="2023-12-31",
            file_type_text="ZIP",
            file_release_date="2024-01-01",
            file_download_uri="https://example.com/test.zip",
        )
        destination = "./downloads"

        # Mock response for streaming
        import requests

        mock_response = MagicMock(spec=requests.Response)
        mock_response.iter_content.return_value = [b"chunk1", b"chunk2"]

        # Patch the _make_request method to return our mock response
        mock_make_request = MagicMock(return_value=mock_response)
        with patch.object(mock_bulk_data_client, "_make_request", mock_make_request):
            # Mock os.path.exists and os.makedirs
            with patch("os.path.exists", return_value=False), patch(
                "os.makedirs"
            ) as mock_makedirs, patch("builtins.open", mock_open()) as mock_file:
                # Test download_file with absolute URL
                file_path = mock_bulk_data_client.download_file(
                    file_data=file_data, destination=destination
                )

                # Verify
                mock_makedirs.assert_called_once_with(destination)
                mock_bulk_data_client._make_request.assert_called_once_with(  # type: ignore
                    method="GET",
                    endpoint="test.zip",
                    stream=True,
                    custom_base_url="https://example.com",
                )
                mock_file.assert_called_once_with(
                    os.path.join(destination, "test.zip"), "wb"
                )
                mock_file().write.assert_any_call(b"chunk1")
                mock_file().write.assert_any_call(b"chunk2")
                assert file_path == os.path.join(destination, "test.zip")

        # Test download_file with relative URL
        file_data.file_download_uri = "downloads/test.zip"

        # Patch the _make_request method again for the relative URL test
        mock_make_request = MagicMock(return_value=mock_response)
        with patch.object(mock_bulk_data_client, "_make_request", mock_make_request):
            with patch("os.path.exists", return_value=True), patch(
                "builtins.open", mock_open()
            ) as mock_file:
                file_path = mock_bulk_data_client.download_file(
                    file_data=file_data, destination=destination
                )

                # Verify
                mock_bulk_data_client._make_request.assert_called_once_with(  # type: ignore
                    method="GET",
                    endpoint="downloads/test.zip",
                    stream=True,
                )
                assert file_path == os.path.join(destination, "test.zip")

        # Test download_file with no download URI
        file_data.file_download_uri = None
        with pytest.raises(ValueError, match="No download URI available for this file"):
            mock_bulk_data_client.download_file(
                file_data=file_data, destination=destination
            )

    def test_search_products(
        self, mock_bulk_data_client: BulkDataClient, bulk_data_sample: Dict[str, Any]
    ) -> None:
        """Test search_products method."""
        # Setup
        mock_response = MagicMock()
        mock_response.json.return_value = bulk_data_sample

        # Create a dedicated mock session
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response

        # Replace the client's session with our mock
        mock_bulk_data_client.session = mock_session

        # Test search_products with all parameters
        response = mock_bulk_data_client.search_products(
            query="test",
            product_title="Test Product",
            product_description="Test Description",
            product_short_name="TEST",
            from_date="2023-01-01",
            to_date="2023-12-31",
            categories=["Patent"],
            labels=["Test"],
            datasets=["Patents"],
            file_types=["ZIP"],
            offset=0,
            limit=10,
            include_files=True,
            latest=True,
            facets=True,
        )

        # Verify
        mock_session.get.assert_called_once_with(
            url=f"{mock_bulk_data_client.base_url}/products/search",
            params={
                "q": "test",
                "productTitle": "Test Product",
                "productDescription": "Test Description",
                "productShortName": "TEST",
                "fromDate": "2023-01-01",
                "toDate": "2023-12-31",
                "categories": "Patent",
                "labels": "Test",
                "datasets": "Patents",
                "fileTypes": "ZIP",
                "offset": 0,
                "limit": 10,
                "includeFiles": "true",
                "latest": "true",
                "facets": "true",
            },
            stream=False,
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
                param="value",
            )
