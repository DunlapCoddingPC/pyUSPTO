"""
Tests for edge cases in the bulk_data client module.

This module contains tests for error handling and edge cases in the BulkDataClient.
"""

from unittest.mock import MagicMock, patch

import pytest
import requests

from pyUSPTO.clients.bulk_data import BulkDataClient
from pyUSPTO.models.bulk_data import BulkDataProduct, BulkDataResponse, FileData


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
        with patch.object(client, "_make_request", return_value=mock_response), patch(
            "os.path.exists", return_value=False
        ), patch("os.makedirs") as mock_makedirs, patch("builtins.open", MagicMock()):

            # Call download_file
            client.download_file(file_data=file_data, destination="/tmp")

            # Verify makedirs was called
            mock_makedirs.assert_called_once_with("/tmp")
