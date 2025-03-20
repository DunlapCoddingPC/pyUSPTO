"""
Tests for the core functionality of the patent_data client module.

This module contains tests for initialization and basic search/retrieval methods
of the PatentDataClient class.
"""

from unittest.mock import MagicMock, patch

import pytest

from pyUSPTO.clients.patent_data import PatentDataClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.patent_data import PatentDataResponse, PatentFileWrapper


class TestPatentDataClientInit:
    """Tests for the initialization of the PatentDataClient."""

    def test_init_with_api_key(self) -> None:
        """Test initialization with API key."""
        client = PatentDataClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.base_url == "https://api.uspto.gov/api/v1/patent"

    def test_init_with_custom_base_url(self) -> None:
        """Test initialization with custom base URL."""
        client = PatentDataClient(
            api_key="test_key", base_url="https://custom.api.test.com"
        )
        assert client.api_key == "test_key"
        assert client.base_url == "https://custom.api.test.com"

    def test_init_with_config(self) -> None:
        """Test initialization with config object."""
        config = USPTOConfig(
            api_key="config_key",
            patent_data_base_url="https://config.api.test.com",
        )
        client = PatentDataClient(config=config)
        assert client.api_key == "config_key"
        assert client.base_url == "https://config.api.test.com"
        assert client.config is config

    def test_init_with_api_key_and_config(self) -> None:
        """Test initialization with both API key and config (API key should take precedence)."""
        config = USPTOConfig(
            api_key="config_key",
            patent_data_base_url="https://config.api.test.com",
        )
        client = PatentDataClient(api_key="direct_key", config=config)
        assert client.api_key == "direct_key"
        assert client.base_url == "https://config.api.test.com"


class TestBasicRetrieval:
    """Tests for basic patent data retrieval methods."""

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_patent_by_application_number(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test get_patent_by_application_number method."""
        # Setup mock
        mock_response = {
            "applicationNumberText": "12345678",
            "applicationMetaData": {"inventionTitle": "Test Invention"},
        }
        mock_make_request.return_value = mock_response

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        result = client.get_patent_by_application_number(application_number="12345678")

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/12345678",
        )

        # Verify result was parsed correctly
        assert isinstance(result, PatentFileWrapper)
        assert result.application_number_text == "12345678"
        assert result.application_meta_data is not None
        assert result.application_meta_data.invention_title == "Test Invention"

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_patent_by_application_number_with_patentFileWrapperDataBag(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test get_patent_by_application_number with patentFileWrapperDataBag in response."""
        # Setup mock to return a response with patentFileWrapperDataBag
        mock_response = {
            "patentFileWrapperDataBag": [
                {
                    "applicationNumberText": "12345678",
                    "applicationMetaData": {"inventionTitle": "Test Invention"},
                }
            ]
        }
        mock_make_request.return_value = mock_response

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        result = client.get_patent_by_application_number(application_number="12345678")

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/12345678",
        )

        # Verify result was parsed correctly
        assert isinstance(result, PatentFileWrapper)
        assert result.application_number_text == "12345678"
        assert result.application_meta_data is not None
        assert result.application_meta_data.invention_title == "Test Invention"

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_patent_by_application_number_with_PatentFileWrapper_response(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test get_patent_by_application_number with PatentFileWrapper response."""
        # Setup mock to return a PatentFileWrapper object directly
        mock_response = PatentFileWrapper(
            application_number_text="12345678",
            application_meta_data=MagicMock(invention_title="Test Invention"),
        )
        mock_make_request.return_value = mock_response

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        result = client.get_patent_by_application_number(application_number="12345678")

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/12345678",
        )

        # Verify result is the same object
        assert result is mock_response
        assert isinstance(result, PatentFileWrapper)
        assert result.application_number_text == "12345678"

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_patent_applications(self, mock_make_request: MagicMock) -> None:
        """Test get_patent_applications method."""
        # Setup mock response object
        mock_response_obj = PatentDataResponse(
            count=2,
            patent_file_wrapper_data_bag=[
                PatentFileWrapper(
                    application_number_text="12345678",
                    application_meta_data=MagicMock(patent_number="10000000"),
                ),
                PatentFileWrapper(
                    application_number_text="87654321",
                    application_meta_data=MagicMock(patent_number="20000000"),
                ),
            ],
        )
        mock_make_request.return_value = mock_response_obj

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        params = {
            "q": "Test",
            "limit": "25",
            "offset": "0",
        }
        result = client.get_patent_applications(params=params)

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/search",
            params=params,
            response_class=PatentDataResponse,
        )

        # Verify result
        assert isinstance(result, PatentDataResponse)
        assert result.count == 2
        assert len(result.patent_file_wrapper_data_bag) == 2
        assert (
            result.patent_file_wrapper_data_bag[0].application_number_text == "12345678"
        )


class TestSearchFilters:
    """Tests for search filters in the PatentDataClient."""

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_search_patents_basic(self, mock_make_request: MagicMock) -> None:
        """Test search_patents method with patent number filter."""
        # Setup mock response object
        mock_response_obj = PatentDataResponse(
            count=2,
            patent_file_wrapper_data_bag=[
                PatentFileWrapper(
                    application_number_text="12345678",
                    application_meta_data=MagicMock(patent_number="10000000"),
                ),
                PatentFileWrapper(
                    application_number_text="87654321",
                    application_meta_data=MagicMock(patent_number="20000000"),
                ),
            ],
        )
        mock_make_request.return_value = mock_response_obj

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        result = client.search_patents(patent_number="10000000", limit=25, offset=0)

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/search",
            params={
                "q": "applicationMetaData.patentNumber:10000000",
                "limit": "25",
                "offset": "0",
            },
            response_class=PatentDataResponse,
        )

        # Verify result
        assert isinstance(result, PatentDataResponse)
        assert result.count == 2
        assert len(result.patent_file_wrapper_data_bag) == 2

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_search_patents_with_multiple_filters(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test search_patents method with multiple filters."""
        # Setup mock response object
        mock_response_obj = PatentDataResponse(
            count=1,
            patent_file_wrapper_data_bag=[
                PatentFileWrapper(
                    application_number_text="12345678",
                    application_meta_data=MagicMock(invention_title="Test Invention"),
                ),
            ],
        )
        mock_make_request.return_value = mock_response_obj

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        result = client.search_patents(
            query="Test Invention",
            inventor_name="John Smith",
            filing_date_from="2020-01-01",
            filing_date_to="2022-01-01",
            limit=20,
            offset=10,
        )

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/search",
            params={
                "q": "applicationMetaData.inventorBag.inventorNameText:John Smith AND Test Invention AND applicationMetaData.filingDate:[2020-01-01 TO 2022-01-01]",
                "limit": "20",
                "offset": "10",
            },
            response_class=PatentDataResponse,
        )

        # Verify result
        assert isinstance(result, PatentDataResponse)
        assert result.count == 1
        assert len(result.patent_file_wrapper_data_bag) == 1

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_search_patents_filing_date_filters(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test search_patents with filing date filters."""
        # Setup mock
        mock_response = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response

        # Create client
        client = PatentDataClient(api_key="test_key")

        # Test with filing_date_from and filing_date_to together
        client.search_patents(
            filing_date_from="2020-01-01", filing_date_to="2022-01-01"
        )
        mock_make_request.assert_called_with(
            method="GET",
            endpoint="applications/search",
            params={
                "q": "applicationMetaData.filingDate:[2020-01-01 TO 2022-01-01]",
                "offset": "0",
                "limit": "25",
            },
            response_class=PatentDataResponse,
        )

        # Test with filing_date_from only
        mock_make_request.reset_mock()
        client.search_patents(filing_date_from="2020-01-01")
        mock_make_request.assert_called_with(
            method="GET",
            endpoint="applications/search",
            params={
                "q": "applicationMetaData.filingDate:>=2020-01-01",
                "offset": "0",
                "limit": "25",
            },
            response_class=PatentDataResponse,
        )

        # Test with filing_date_to only
        mock_make_request.reset_mock()
        client.search_patents(filing_date_to="2022-01-01")
        mock_make_request.assert_called_with(
            method="GET",
            endpoint="applications/search",
            params={
                "q": "applicationMetaData.filingDate:<=2022-01-01",
                "offset": "0",
                "limit": "25",
            },
            response_class=PatentDataResponse,
        )

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_search_patents_grant_date_filters(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test search_patents with grant date filters."""
        mock_response = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response

        client = PatentDataClient(api_key="test_key")

        # Test with grant_date_from and grant_date_to together
        grant_date_from = "2020-01-01"
        grant_date_to = "2020-12-31"
        client.search_patents(
            grant_date_from=grant_date_from, grant_date_to=grant_date_to
        )
        mock_make_request.assert_called_with(
            method="GET",
            endpoint="applications/search",
            params={
                "q": f"applicationMetaData.grantDate:[{grant_date_from} TO {grant_date_to}]",
                "offset": "0",
                "limit": "25",
            },
            response_class=PatentDataResponse,
        )

        # Test with grant_date_from only
        mock_make_request.reset_mock()
        client.search_patents(grant_date_from="2020-01-01")
        mock_make_request.assert_called_with(
            method="GET",
            endpoint="applications/search",
            params={
                "q": "applicationMetaData.grantDate:>=2020-01-01",
                "offset": "0",
                "limit": "25",
            },
            response_class=PatentDataResponse,
        )

        # Test with grant_date_to only
        mock_make_request.reset_mock()
        client.search_patents(grant_date_to="2022-01-01")
        mock_make_request.assert_called_with(
            method="GET",
            endpoint="applications/search",
            params={
                "q": "applicationMetaData.grantDate:<=2022-01-01",
                "offset": "0",
                "limit": "25",
            },
            response_class=PatentDataResponse,
        )

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_search_patents_name_filters(self, mock_make_request):
        """Test search_patents with name-related filters."""
        mock_response = MagicMock(spec=PatentDataResponse)
        mock_make_request.return_value = mock_response

        client = PatentDataClient(api_key="test_key")

        # Test applicant_name
        applicant_name = "Test Applicant"
        client.search_patents(applicant_name=applicant_name)
        called_args = mock_make_request.call_args
        called_params = called_args[1]["params"]
        assert "q" in called_params
        assert (
            f"applicationMetaData.firstApplicantName:{applicant_name}"
            in called_params["q"]
        )

        # Test assignee_name
        mock_make_request.reset_mock()
        assignee_name = "Test Assignee"
        client.search_patents(assignee_name=assignee_name)
        called_args = mock_make_request.call_args
        called_params = called_args[1]["params"]
        assert "q" in called_params
        assert (
            f"assignmentBag.assigneeBag.assigneeNameText:{assignee_name}"
            in called_params["q"]
        )

        # Test inventor_name
        mock_make_request.reset_mock()
        inventor_name = "John Inventor"
        client.search_patents(inventor_name=inventor_name)
        called_args = mock_make_request.call_args
        called_params = called_args[1]["params"]
        assert "q" in called_params
        assert (
            f"applicationMetaData.inventorBag.inventorNameText:{inventor_name}"
            in called_params["q"]
        )

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_search_patents_classification_filter(self, mock_make_request):
        """Test search_patents with classification filter."""
        mock_response = MagicMock(spec=PatentDataResponse)
        mock_make_request.return_value = mock_response

        client = PatentDataClient(api_key="test_key")
        classification = "G06F"

        client.search_patents(classification=classification)

        called_args = mock_make_request.call_args
        called_params = called_args[1]["params"]

        assert "q" in called_params
        assert (
            f"applicationMetaData.cpcClassificationBag:{classification}"
            in called_params["q"]
        )

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_search_patents_application_number_filter(self, mock_make_request):
        """Test search_patents with application number filter."""
        mock_response = MagicMock(spec=PatentDataResponse)
        mock_make_request.return_value = mock_response

        client = PatentDataClient(api_key="test_key")
        application_number = "12345678"

        client.search_patents(application_number=application_number)

        called_args = mock_make_request.call_args
        called_params = called_args[1]["params"]

        assert "q" in called_params
        assert f"applicationNumberText:{application_number}" in called_params["q"]


class TestPaginationAndAdvancedSearch:
    """Tests for pagination and advanced search methods."""

    @patch("pyUSPTO.clients.patent_data.PatentDataClient.paginate_results")
    def test_paginate_patents(self, mock_paginate: MagicMock) -> None:
        """Test paginate_patents method."""
        # Setup mock
        patent1 = PatentFileWrapper(application_number_text="12345678")
        patent2 = PatentFileWrapper(application_number_text="87654321")
        mock_paginate.return_value = iter([patent1, patent2])

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        results = list(client.paginate_patents(query="Test", limit=20))

        # Verify paginate_results was called correctly
        mock_paginate.assert_called_once_with(
            method_name="get_patent_applications",
            response_container_attr="patent_file_wrapper_data_bag",
            query="Test",
            limit=20,
        )

        # Verify results were processed correctly
        assert len(results) == 2
        assert results[0].application_number_text == "12345678"
        assert results[1].application_number_text == "87654321"

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_search_patent_applications_post(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test search_patent_applications_post method."""
        # Setup mock with a properly typed response object
        mock_response_obj = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        result = client.search_patent_applications_post(
            search_request={
                "q": "Test",
                "filters": [
                    {"field": "inventionSubjectMatterCategory", "value": "MECHANICAL"}
                ],
                "fields": ["patentNumber", "inventionTitle"],
                "pagination": {"offset": 0, "limit": 100},
                "sort": [{"field": "filingDate", "order": "desc"}],
            }
        )

        # Verify result is a PatentDataResponse
        assert isinstance(result, PatentDataResponse)

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="POST",
            endpoint="applications/search",
            json_data={
                "q": "Test",
                "filters": [
                    {"field": "inventionSubjectMatterCategory", "value": "MECHANICAL"}
                ],
                "fields": ["patentNumber", "inventionTitle"],
                "pagination": {"offset": 0, "limit": 100},
                "sort": [{"field": "filingDate", "order": "desc"}],
            },
            response_class=PatentDataResponse,
        )

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_search_patents_with_empty_query(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test search_patents with empty query parameters."""
        # Setup mock response
        mock_response_obj = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        # Create client and call method with no search parameters
        client = PatentDataClient(api_key="test_key")
        result = client.search_patents()

        # Verify request was made with empty q parameter
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/search",
            params={"offset": "0", "limit": "25"},
            response_class=PatentDataResponse,
        )

        # Verify result
        assert isinstance(result, PatentDataResponse)
        assert result.count == 0

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_search_patents_explicitly_null_limit_offset(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test search_patents with explicitly null limit and offset."""
        # Setup mock response
        mock_response_obj = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        # Create client
        client = PatentDataClient(api_key="test_key")

        # Call with explicitly None limit and offset
        client.search_patents(query="test query", limit=None, offset=None)

        # Verify the right query was built and sent WITHOUT limit and offset params
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/search",
            params={"q": "test query"},
            response_class=PatentDataResponse,
        )
