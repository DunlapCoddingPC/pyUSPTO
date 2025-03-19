"""
Test fixtures for USPTO API client tests.

This module provides pytest fixtures for testing the USPTO API clients.
"""

from typing import Any, Dict, Generator
from unittest.mock import MagicMock, patch

import pytest

from pyUSPTO.clients import BulkDataClient, PatentDataClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.patent_data import (
    PatentDataResponse,
    PatentFileWrapper,
)


@pytest.fixture
def uspto_config() -> USPTOConfig:
    """
    Create a test USPTOConfig instance.

    Returns:
        USPTOConfig: A test configuration with a dummy API key
    """
    return USPTOConfig(
        api_key="test_api_key",
        bulk_data_base_url="https://api.uspto.gov/api/v1/datasets",
        patent_data_base_url="https://api.uspto.gov/api/v1/patent",
    )


@pytest.fixture
def mock_response() -> MagicMock:
    """
    Create a mock requests.Response object.

    Returns:
        MagicMock: A mock response object
    """
    mock = MagicMock()
    mock.raise_for_status.return_value = None
    return mock


@pytest.fixture
def mock_session() -> Generator[MagicMock, None, None]:
    """
    Create a mock requests.Session object and patch the Session class.

    Yields:
        MagicMock: A mock session object
    """
    with patch("requests.Session") as mock_session_class:
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        yield mock_session


@pytest.fixture
def bulk_data_sample() -> Dict[str, Any]:
    """
    Provide a sample bulk data API response.

    Returns:
        Dict[str, Any]: A sample bulk data API response
    """
    return {
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
                    "count": 2,
                    "fileDataBag": [
                        {
                            "fileName": "test1.zip",
                            "fileSize": 512,
                            "fileDataFromDate": "2023-01-01",
                            "fileDataToDate": "2023-06-30",
                            "fileTypeText": "ZIP",
                            "fileReleaseDate": "2023-07-01",
                            "fileDownloadURI": "https://example.com/test1.zip",
                        },
                        {
                            "fileName": "test2.zip",
                            "fileSize": 512,
                            "fileDataFromDate": "2023-07-01",
                            "fileDataToDate": "2023-12-31",
                            "fileTypeText": "ZIP",
                            "fileReleaseDate": "2024-01-01",
                            "fileDownloadURI": "https://example.com/test2.zip",
                        },
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
                "productFileBag": {
                    "count": 1,
                    "fileDataBag": [
                        {
                            "fileName": "test3.zip",
                            "fileSize": 2048,
                            "fileDataFromDate": "2023-01-01",
                            "fileDataToDate": "2023-12-31",
                            "fileTypeText": "ZIP",
                            "fileReleaseDate": "2024-01-01",
                            "fileDownloadURI": "https://example.com/test3.zip",
                        }
                    ],
                },
            },
        ],
    }


@pytest.fixture
def patent_data_sample() -> Dict[str, Any]:
    """
    Provide a sample patent data API response.

    Returns:
        Dict[str, Any]: A sample patent data API response
    """
    return {
        "count": 2,
        "patentFileWrapperDataBag": [
            {
                "applicationNumberText": "12345678",
                "applicationMetaData": {
                    "inventionTitle": "Test Invention 1",
                    "filingDate": "2023-01-01",
                    "applicationStatusCode": 150,
                    "applicationStatusDescriptionText": "Patented Case",
                    "patentNumber": "10000001",
                    "grantDate": "2023-06-01",
                    "firstInventorName": "John Smith",
                    "firstApplicantName": "Test Company Inc.",
                    "inventorBag": [
                        {
                            "firstName": "John",
                            "lastName": "Smith",
                            "inventorNameText": "John Smith",
                            "correspondenceAddressBag": [
                                {
                                    "cityName": "San Francisco",
                                    "geographicRegionCode": "CA",
                                    "countryCode": "US",
                                }
                            ],
                        }
                    ],
                    "applicantBag": [
                        {
                            "applicantNameText": "Test Company Inc.",
                            "correspondenceAddressBag": [
                                {
                                    "cityName": "San Francisco",
                                    "geographicRegionCode": "CA",
                                    "countryCode": "US",
                                }
                            ],
                        }
                    ],
                },
            },
            {
                "applicationNumberText": "87654321",
                "applicationMetaData": {
                    "inventionTitle": "Test Invention 2",
                    "filingDate": "2023-02-01",
                    "applicationStatusCode": 30,
                    "applicationStatusDescriptionText": "Docketed New Case - Ready for Examination",
                    "firstInventorName": "Jane Doe",
                    "firstApplicantName": "Test Company Inc.",
                    "inventorBag": [
                        {
                            "firstName": "Jane",
                            "lastName": "Doe",
                            "inventorNameText": "Jane Doe",
                            "correspondenceAddressBag": [
                                {
                                    "cityName": "New York",
                                    "geographicRegionCode": "NY",
                                    "countryCode": "US",
                                }
                            ],
                        }
                    ],
                    "applicantBag": [
                        {
                            "applicantNameText": "Test Company Inc.",
                            "correspondenceAddressBag": [
                                {
                                    "cityName": "San Francisco",
                                    "geographicRegionCode": "CA",
                                    "countryCode": "US",
                                }
                            ],
                        }
                    ],
                },
            },
        ],
    }


@pytest.fixture
def mock_bulk_data_client(
    mock_session: MagicMock, uspto_config: USPTOConfig
) -> BulkDataClient:
    """
    Create a BulkDataClient with a mocked session.

    Args:
        mock_session: A mock session object
        uspto_config: A test configuration

    Returns:
        BulkDataClient: A client with a mocked session
    """
    client = BulkDataClient(config=uspto_config)
    client.session = mock_session
    return client


@pytest.fixture
def mock_patent_data_client(
    mock_session: MagicMock, uspto_config: USPTOConfig
) -> PatentDataClient:
    """
    Create a PatentDataClient with a mocked session.

    Args:
        mock_session: A mock session object
        uspto_config: A test configuration

    Returns:
        PatentDataClient: A client with a mocked session
    """
    client = PatentDataClient(config=uspto_config)
    client.session = mock_session
    return client
