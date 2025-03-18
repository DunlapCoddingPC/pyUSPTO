"""
Tests for the bulk_data module.

This module contains tests for the BulkDataClient class, including core functionality,
model handling, edge cases, and response handling.
"""

import os
from typing import Any, Dict
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


class TestBulkDataClientInit:
    """Tests for the initialization of the BulkDataClient class."""

    def test_init_with_api_key(self) -> None:
        """Test initialization with direct API key."""
        client = BulkDataClient(api_key="test_key")
        assert client.api_key == "test_key"
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
        assert client.api_key == "config_key"
        assert client.base_url == "https://config.api.test.com"
        assert client.config is config

    def test_init_with_api_key_and_config(self) -> None:
        """Test initialization with both API key and config."""
        config = USPTOConfig(
            api_key="config_key",
            bulk_data_base_url="https://config.api.test.com",
        )
        client = BulkDataClient(api_key="direct_key", config=config)
        assert client.api_key == "direct_key"
        assert client.base_url == "https://config.api.test.com"


class TestBulkDataClientCore:
    """Tests for the core functionality of the BulkDataClient class."""

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
                "offset": "0",
                "limit": "10",
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
        mock_response = MagicMock(spec=requests.Response)
        mock_response.iter_content.return_value = [b"chunk1", b"chunk2"]

        # Patch the _make_request method to return our mock response
        mock_make_request = MagicMock(return_value=mock_response)
        with patch.object(mock_bulk_data_client, "_make_request", mock_make_request):
            # Mock os.path.exists and os.makedirs
            with (
                patch("os.path.exists", return_value=False),
                patch("os.makedirs") as mock_makedirs,
                patch("builtins.open", mock_open()) as mock_file,
            ):
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

    def test_download_file_with_relative_url(
        self, mock_bulk_data_client: BulkDataClient
    ) -> None:
        """Test download_file method with relative URL."""
        # Setup
        file_data = FileData(
            file_name="test.zip",
            file_size=1024,
            file_data_from_date="2023-01-01",
            file_data_to_date="2023-12-31",
            file_type_text="ZIP",
            file_release_date="2024-01-01",
            file_download_uri="downloads/test.zip",
        )
        destination = "./downloads"

        # Mock response for streaming
        mock_response = MagicMock(spec=requests.Response)
        mock_response.iter_content.return_value = [b"chunk1", b"chunk2"]

        # Patch the _make_request method for the relative URL test
        mock_make_request = MagicMock(return_value=mock_response)
        with patch.object(mock_bulk_data_client, "_make_request", mock_make_request):
            with (
                patch("os.path.exists", return_value=True),
                patch("builtins.open", mock_open()) as mock_file,
            ):
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

    def test_search_products(
        self, mock_bulk_data_client: BulkDataClient, bulk_data_sample: Dict[str, Any]
    ) -> None:
        """Test search_products method with all parameters."""
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
                "offset": "0",
                "limit": "10",
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


class TestBulkDataClientEdgeCases:
    """Tests for edge cases in the BulkDataClient class."""

    def test_get_product_by_id_with_invalid_response(self) -> None:
        """Test get_product_by_id with an invalid response type."""
        # Setup
        client = BulkDataClient(api_key="test_key")

        # Mock _make_request directly to return something that's not a dict or BulkDataResponse
        with patch.object(
            client, "_make_request", return_value="not a dict or BulkDataResponse"
        ):
            # Test with an invalid response
            with pytest.raises(
                AttributeError, match="'str' object has no attribute 'json'"
            ):
                client.get_product_by_id(product_id="TEST")

    def test_download_file_with_invalid_response(self) -> None:
        """Test download_file with an invalid response type."""
        # Setup
        client = BulkDataClient(api_key="test_key")
        file_data = FileData(
            file_name="test.zip",
            file_size=1024,
            file_data_from_date="2023-01-01",
            file_data_to_date="2023-12-31",
            file_type_text="ZIP",
            file_release_date="2024-01-01",
            file_download_uri="https://example.com/test.zip",
        )

        # Mock _make_request to return something that's not a Response object
        with patch.object(client, "_make_request", return_value="not a Response"):
            # Test with invalid response type
            with pytest.raises(
                TypeError, match="Expected a Response object for streaming download"
            ):
                client.download_file(file_data=file_data, destination="/tmp")

    def test_get_product_by_id_with_bulk_data_response_result(self) -> None:
        """Test get_product_by_id when _make_request returns a BulkDataResponse directly."""
        # Setup
        client = BulkDataClient(api_key="test_key")

        # Create a BulkDataResponse object
        product = BulkDataProduct(
            product_identifier="TEST",
            product_title_text="Test Product",
            product_description_text="Test Description",
            product_frequency_text="Weekly",
            product_label_array_text=["Patent", "Test"],
            product_dataset_array_text=["Patents"],
            product_dataset_category_array_text=["Patent"],
            product_from_date="2023-01-01",
            product_to_date="2023-12-31",
            product_total_file_size=1024,
            product_file_total_quantity=2,
            last_modified_date_time="2023-12-31T23:59:59",
            mime_type_identifier_array_text=["application/zip"],
        )
        response = BulkDataResponse(
            count=1,
            bulk_data_product_bag=[product],
        )

        # Mock _make_request to return a BulkDataResponse
        with patch.object(client, "_make_request", return_value=response):
            # Test with BulkDataResponse result
            result = client.get_product_by_id(product_id="TEST")

            # Verify
            assert isinstance(result, BulkDataProduct)
            assert result.product_identifier == "TEST"
            assert result.product_title_text == "Test Product"

    def test_get_product_by_id_no_matching_product(self) -> None:
        """Test get_product_by_id with a BulkDataResponse that doesn't contain the requested product."""
        # Setup
        client = BulkDataClient(api_key="test_key")

        # Create a BulkDataResponse object with a different product ID
        product = BulkDataProduct(
            product_identifier="OTHER",
            product_title_text="Other Product",
            product_description_text="Other Description",
            product_frequency_text="Monthly",
            product_label_array_text=["Patent", "Other"],
            product_dataset_array_text=["Patents"],
            product_dataset_category_array_text=["Patent"],
            product_from_date="2023-01-01",
            product_to_date="2023-12-31",
            product_total_file_size=2048,
            product_file_total_quantity=1,
            last_modified_date_time="2023-12-31T23:59:59",
            mime_type_identifier_array_text=["application/zip"],
        )
        response = BulkDataResponse(
            count=1,
            bulk_data_product_bag=[product],
        )

        # Mock _make_request to return a BulkDataResponse
        with patch.object(client, "_make_request", return_value=response):
            # Test with product not found
            with pytest.raises(
                ValueError, match="Product with ID TEST not found in response"
            ):
                client.get_product_by_id(product_id="TEST")

    def test_download_file_creates_directory(self) -> None:
        """Test that download_file creates the destination directory if it doesn't exist."""
        # Setup
        client = BulkDataClient(api_key="test_key")
        file_data = FileData(
            file_name="test.zip",
            file_size=1024,
            file_data_from_date="2023-01-01",
            file_data_to_date="2023-12-31",
            file_type_text="ZIP",
            file_release_date="2024-01-01",
            file_download_uri="relative/path/to/test.zip",
        )

        # Mock Response object
        mock_response = MagicMock(spec=requests.Response)
        mock_response.iter_content.return_value = [b"test content"]

        # Patch the necessary methods
        with (
            patch.object(client, "_make_request", return_value=mock_response),
            patch("os.path.exists", return_value=False),
            patch("os.makedirs") as mock_makedirs,
            patch("builtins.open", MagicMock()),
        ):

            # Call download_file
            client.download_file(file_data=file_data, destination="/tmp")

            # Verify makedirs was called
            mock_makedirs.assert_called_once_with("/tmp")

    def test_download_file_with_no_uri(
        self, mock_bulk_data_client: BulkDataClient
    ) -> None:
        """Test download_file with no download URI."""
        # Setup
        file_data = FileData(
            file_name="test.zip",
            file_size=1024,
            file_data_from_date="2023-01-01",
            file_data_to_date="2023-12-31",
            file_type_text="ZIP",
            file_release_date="2024-01-01",
            file_download_uri=None,
        )
        destination = "./downloads"

        # Test download_file with no download URI
        with pytest.raises(ValueError, match="No download URI available for this file"):
            mock_bulk_data_client.download_file(
                file_data=file_data, destination=destination
            )


class TestBulkDataResponseHandling:
    """Tests for response format handling in the BulkDataClient class."""

    def test_get_product_by_id_with_dict_response_containing_product_bag(self) -> None:
        """Test get_product_by_id when response is a dict with bulkDataProductBag."""
        # Setup
        client = BulkDataClient(api_key="test_key")

        # Create a dictionary response with a bulkDataProductBag containing the product we want
        dict_response = {
            "bulkDataProductBag": [
                {
                    "productIdentifier": "OTHER_PRODUCT",
                    "productTitleText": "Some Other Product",
                },
                {
                    "productIdentifier": "TARGET_PRODUCT",
                    "productTitleText": "Target Product",
                    "productDescriptionText": "This is the product we want",
                    "productFrequencyText": "Daily",
                    "productLabelArrayText": ["Test"],
                    "productDatasetArrayText": ["Test Dataset"],
                    "productDatasetCategoryArrayText": ["Test Category"],
                    "productFromDate": "2023-01-01",
                    "productToDate": "2023-12-31",
                    "productTotalFileSize": 1024,
                    "productFileTotalQuantity": 1,
                    "lastModifiedDateTime": "2023-12-31T23:59:59",
                    "mimeTypeIdentifierArrayText": ["application/zip"],
                },
            ]
        }

        # Mock _make_request to return our dictionary
        with patch.object(client, "_make_request", return_value=dict_response):
            # Call the method to test the missing branch
            result = client.get_product_by_id(product_id="TARGET_PRODUCT")

            # Verify
            assert isinstance(result, BulkDataProduct)
            assert result.product_identifier == "TARGET_PRODUCT"
            assert result.product_title_text == "Target Product"
            assert result.product_description_text == "This is the product we want"

    def test_get_product_by_id_with_dict_response_product_not_found(self) -> None:
        """Test get_product_by_id when product is not found in bulkDataProductBag."""
        # Setup
        client = BulkDataClient(api_key="test_key")

        # Create a dictionary response with a bulkDataProductBag NOT containing the product we want
        dict_response = {
            "bulkDataProductBag": [
                {
                    "productIdentifier": "PRODUCT_1",
                    "productTitleText": "Product 1",
                },
                {
                    "productIdentifier": "PRODUCT_2",
                    "productTitleText": "Product 2",
                },
            ]
        }

        # Mock _make_request to return our dictionary
        with patch.object(client, "_make_request", return_value=dict_response):
            # Call the method to test the error case
            with pytest.raises(
                ValueError, match="Product with ID NON_EXISTENT not found in response"
            ):
                client.get_product_by_id(product_id="NON_EXISTENT")

    def test_get_product_by_id_with_non_dict_json_response(self) -> None:
        """Test get_product_by_id when response.json() returns a non-dict value."""
        # Setup
        client = BulkDataClient(api_key="test_key")

        # Create a mock response object whose json() method returns a list instead of a dict
        mock_response = MagicMock()
        mock_response.json.return_value = ["not", "a", "dict"]

        # Patch _make_request to return our mock response
        with patch.object(client, "_make_request", return_value=mock_response):
            # Should raise TypeError
            with pytest.raises(TypeError, match=r"Expected dict, got <class 'list'>"):
                client.get_product_by_id(product_id="TEST")
