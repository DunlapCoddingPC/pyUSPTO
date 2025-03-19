"""
Tests for edge cases and error handling.

This module contains tests for edge cases and error handling in the USPTO API clients.
"""

from typing import Any, Dict, Optional
from unittest.mock import MagicMock, patch

import pytest
import requests

from pyUSPTO.base import (
    BaseUSPTOClient,
    USPTOApiAuthError,
    USPTOApiError,
    USPTOApiNotFoundError,
    USPTOApiRateLimitError,
)
from pyUSPTO.clients import BulkDataClient, PatentDataClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.bulk_data import (
    BulkDataProduct,
    BulkDataResponse,
    FileData,
    ProductFileBag,
)
from pyUSPTO.models.patent_data import (
    PatentDataResponse,
    PatentFileWrapper,
)


class TestConfigEdgeCases:
    """Tests for edge cases in the USPTOConfig class."""

    def test_config_with_empty_api_key(self) -> None:
        """Test creating a config with an empty API key."""
        # Empty string API key
        config = USPTOConfig(api_key="")
        assert config.api_key == ""

        # None API key should fall back to environment variable
        with patch.dict("os.environ", {"USPTO_API_KEY": "env_key"}, clear=True):
            config = USPTOConfig(api_key=None)
            assert config.api_key == "env_key"

        # No API key and no environment variable
        with patch.dict("os.environ", {}, clear=True):
            config = USPTOConfig()
            assert config.api_key is None

    def test_from_env_with_missing_variables(self) -> None:
        """Test from_env method with missing environment variables."""
        # No environment variables
        with patch.dict("os.environ", {}, clear=True):
            config = USPTOConfig.from_env()
            assert config.api_key is None
            assert config.bulk_data_base_url == "https://api.uspto.gov/api/v1/datasets"
            assert config.patent_data_base_url == "https://api.uspto.gov/api/v1/patent"

        # Only API key
        with patch.dict("os.environ", {"USPTO_API_KEY": "env_key"}, clear=True):
            config = USPTOConfig.from_env()
            assert config.api_key == "env_key"
            assert config.bulk_data_base_url == "https://api.uspto.gov/api/v1/datasets"
            assert config.patent_data_base_url == "https://api.uspto.gov/api/v1/patent"

        # Custom URLs
        with patch.dict(
            "os.environ",
            {
                "USPTO_API_KEY": "env_key",
                "USPTO_BULK_DATA_BASE_URL": "https://custom.bulk.url",
                "USPTO_PATENT_DATA_BASE_URL": "https://custom.patent.url",
            },
            clear=True,
        ):
            config = USPTOConfig.from_env()
            assert config.api_key == "env_key"
            assert config.bulk_data_base_url == "https://custom.bulk.url"
            assert config.patent_data_base_url == "https://custom.patent.url"


class TestBaseClientEdgeCases:
    """Tests for edge cases in the BaseUSPTOClient class."""

    def test_make_request_with_empty_response(self, mock_session: MagicMock) -> None:
        """Test _make_request method with empty response."""
        # Setup
        client = BaseUSPTOClient(base_url="https://api.test.com")
        client.session = mock_session

        # Empty JSON response
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_session.get.return_value = mock_response

        # Test with empty response
        result = client._make_request(method="GET", endpoint="test")
        assert result == {}

        # None response (should not happen in practice, but test anyway)
        mock_response.json.return_value = None
        result = client._make_request(method="GET", endpoint="test")
        assert result is None

    def test_make_request_with_invalid_json(self, mock_session: MagicMock) -> None:
        """Test _make_request method with invalid JSON response."""
        # Setup
        client = BaseUSPTOClient(base_url="https://api.test.com")
        client.session = mock_session

        # Mock response that raises ValueError on json()
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_session.get.return_value = mock_response

        # This should raise an exception since we can't parse the response
        with pytest.raises(ValueError, match="Invalid JSON"):
            client._make_request(method="GET", endpoint="test")

    def test_paginate_results_with_empty_response(self) -> None:
        """Test paginate_results method with empty response."""

        # Create a test class with a method that returns empty responses
        class TestClient(BaseUSPTOClient):
            def test_method(self, **kwargs):
                # Return an empty response
                response = MagicMock()
                response.count = 0
                response.items = []
                return response

        # Use our test client
        test_client = TestClient(base_url="https://api.test.com")

        # Test paginate_results with empty response
        results = list(
            test_client.paginate_results(
                method_name="test_method",
                response_container_attr="items",
                param1="value1",
                limit=10,
            )
        )

        # Verify
        assert results == []


class TestBulkDataClientEdgeCases:
    """Tests for edge cases in the BulkDataClient class."""

    def test_get_product_by_id_not_found(
        self, mock_bulk_data_client: BulkDataClient
    ) -> None:
        """Test get_product_by_id method with a non-existent product ID."""
        # Setup
        mock_response = MagicMock()
        mock_response.json.return_value = {"count": 0, "bulkDataProductBag": []}
        mock_bulk_data_client.session.get.return_value = mock_response

        # Test with non-existent product ID
        with pytest.raises(
            ValueError, match="Product with ID NONEXISTENT not found in response"
        ):
            mock_bulk_data_client.get_product_by_id(product_id="NONEXISTENT")

    def test_download_file_with_no_uri(
        self, mock_bulk_data_client: BulkDataClient
    ) -> None:
        """Test download_file method with a file that has no download URI."""
        # Setup
        file_data = FileData(
            file_name="test.zip",
            file_size=1024,
            file_data_from_date="2023-01-01",
            file_data_to_date="2023-12-31",
            file_type_text="ZIP",
            file_release_date="2024-01-01",
            file_download_uri=None,  # No download URI
        )
        destination = "./downloads"

        # Test with no download URI
        with pytest.raises(ValueError, match="No download URI available for this file"):
            mock_bulk_data_client.download_file(
                file_data=file_data, destination=destination
            )

    def test_download_file_with_invalid_response(
        self, mock_bulk_data_client: BulkDataClient
    ) -> None:
        """Test download_file method with an invalid response type."""
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

        # Mock _make_request to return a dict instead of a Response object
        with patch.object(
            mock_bulk_data_client, "_make_request", return_value={"key": "value"}
        ):
            # This should raise an exception since we need a Response object
            with pytest.raises(
                TypeError, match="Expected a Response object for streaming download"
            ):
                mock_bulk_data_client.download_file(
                    file_data=file_data, destination=destination
                )


class TestPatentDataClientEdgeCases:
    """Tests for edge cases in the PatentDataClient class."""

    def test_get_patent_by_application_number_not_found(
        self, mock_patent_data_client: PatentDataClient
    ) -> None:
        """Test get_patent_by_application_number method with a non-existent application number."""
        # Setup
        mock_response = MagicMock()
        mock_response.json.return_value = {"count": 0, "patentFileWrapperDataBag": []}
        mock_patent_data_client.session.get.return_value = mock_response

        # Test with non-existent application number
        with pytest.raises(
            ValueError,
            match="Patent with application number NONEXISTENT not found in response",
        ):
            mock_patent_data_client.get_patent_by_application_number(
                application_number="NONEXISTENT"
            )

    def test_download_application_document_with_invalid_response(
        self, mock_patent_data_client: PatentDataClient
    ) -> None:
        """Test download_application_document method with an invalid response type."""
        # Setup
        application_number = "12345678"
        document_id = "document123"
        destination = "./downloads"

        # Mock _make_request to return a dict instead of a Response object
        with patch.object(
            mock_patent_data_client, "_make_request", return_value={"key": "value"}
        ):
            # This should raise an exception since we need a Response object
            with pytest.raises(
                TypeError, match="Expected a Response object for streaming download"
            ):
                mock_patent_data_client.download_application_document(
                    application_number=application_number,
                    document_id=document_id,
                    destination=destination,
                )


class TestModelEdgeCases:
    """Tests for edge cases in the model classes."""

    def test_from_dict_with_empty_data(self) -> None:
        """Test from_dict methods with empty data."""
        # Test BulkDataResponse
        response = BulkDataResponse.from_dict({})
        assert response.count == 0
        assert response.bulk_data_product_bag == []

        # Test PatentDataResponse
        response = PatentDataResponse.from_dict({})
        assert response.count == 0
        assert response.patent_file_wrapper_data_bag == []

        # Test BulkDataProduct
        product = BulkDataProduct.from_dict({})
        assert product.product_identifier == ""
        assert product.product_description_text == ""
        assert product.product_title_text == ""
        assert product.product_frequency_text == ""
        assert product.product_label_array_text == []
        assert product.product_dataset_array_text == []
        assert product.product_dataset_category_array_text == []
        assert product.product_from_date == ""
        assert product.product_to_date == ""
        assert product.product_total_file_size == 0
        assert product.product_file_total_quantity == 0
        assert product.last_modified_date_time == ""
        assert product.mime_type_identifier_array_text == []
        assert product.product_file_bag is not None
        assert product.product_file_bag.count == 0
        assert product.product_file_bag.file_data_bag == []

        # Test PatentFileWrapper
        wrapper = PatentFileWrapper.from_dict({})
        assert wrapper.application_number_text is None
        assert wrapper.application_meta_data is None
        assert wrapper.correspondence_address_bag == []
        assert wrapper.assignment_bag == []
        assert wrapper.record_attorney is None
        assert wrapper.foreign_priority_bag == []
        assert wrapper.parent_continuity_bag == []
        assert wrapper.child_continuity_bag == []
        assert wrapper.patent_term_adjustment_data is None
        assert wrapper.event_data_bag == []
        assert wrapper.pgpub_document_meta_data is None
        assert wrapper.grant_document_meta_data is None
        assert wrapper.last_ingestion_date_time is None

    def test_to_dict_with_empty_data(self) -> None:
        """Test to_dict methods with empty data."""
        # Test BulkDataResponse
        response = BulkDataResponse(count=0, bulk_data_product_bag=[])
        result = response.to_dict()
        assert result["count"] == 0
        assert result["bulkDataProductBag"] == []

        # Test PatentDataResponse
        response = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
        result = response.to_dict()
        assert result["count"] == 0
        assert result["patentFileWrapperDataBag"] == []
        assert result["documentBag"] == []
