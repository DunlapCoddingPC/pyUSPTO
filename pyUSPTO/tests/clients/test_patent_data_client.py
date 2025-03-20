"""
Tests for the patent_data client module.

This module contains tests for the PatentDataClient class, including initialization,
core functionality, data retrieval, processing, error handling, and edge cases.
"""

import os
from unittest.mock import MagicMock, mock_open, patch

import pytest
import requests

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


class TestPatentDataRetrieval:
    """Tests for the patent data retrieval methods."""

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

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_search_patents(self, mock_make_request: MagicMock) -> None:
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
    def test_search_patents_all_date_filter_combinations(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test search_patents with various date filter combinations."""
        # Setup mock
        mock_response = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response

        # Create client
        client = PatentDataClient(api_key="test_key")

        # Test with filing_date_from only
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
    def test_search_patents_grant_date_range_filter(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test search_patents with grant date range filter."""
        mock_response = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response

        client = PatentDataClient(api_key="test_key")
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

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_search_patents_applicant_name_filter(self, mock_make_request):
        """Test search_patents with applicant_name filter."""
        mock_response = MagicMock(spec=PatentDataResponse)
        mock_make_request.return_value = mock_response

        client = PatentDataClient(api_key="test_key")
        applicant_name = "Test Applicant"

        client.search_patents(applicant_name=applicant_name)

        called_args = mock_make_request.call_args
        called_params = called_args[1]["params"]

        assert "q" in called_params
        assert (
            f"applicationMetaData.firstApplicantName:{applicant_name}"
            in called_params["q"]
        )

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_search_patents_assignee_name_filter(self, mock_make_request):
        """Test search_patents with assignee_name filter."""
        mock_response = MagicMock(spec=PatentDataResponse)
        mock_make_request.return_value = mock_response

        client = PatentDataClient(api_key="test_key")
        assignee_name = "Test Assignee"

        client.search_patents(assignee_name=assignee_name)

        called_args = mock_make_request.call_args
        called_params = called_args[1]["params"]

        assert "q" in called_params
        assert (
            f"assignmentBag.assigneeBag.assigneeNameText:{assignee_name}"
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
    def test_get_application_metadata(self, mock_make_request: MagicMock) -> None:
        """Test get_application_metadata method."""
        # Setup mock with a response object
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
        result = client.get_application_metadata(application_number="12345678")

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/12345678/meta-data",
            response_class=PatentDataResponse,
        )

        # Verify result
        assert isinstance(result, PatentDataResponse)
        assert result.count == 1


class TestPatentDataDocumentHandling:
    """Tests for patent document handling methods."""

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_application_document(self, mock_make_request: MagicMock) -> None:
        """Test download_application_document method."""
        # Setup mock for the response
        mock_response = MagicMock(spec=requests.Response)
        mock_response.headers = {"Content-Disposition": 'filename="test_document.pdf"'}
        mock_response.iter_content.return_value = [b"test content"]
        mock_make_request.return_value = mock_response

        # Mock open function
        mock_open_func = mock_open()
        mock_file = MagicMock()
        mock_open_func.return_value.__enter__.return_value = mock_file

        with patch("builtins.open", mock_open_func), patch(
            "os.path.exists", return_value=True
        ):
            # Create client and call method
            client = PatentDataClient(api_key="test_key")
            result = client.download_application_document(
                application_number="12345678", document_id="DOC123", destination="/tmp"
            )

            # Verify request was made correctly with correct base URL handling
            mock_make_request.assert_called_once_with(
                method="GET",
                endpoint="download/applications/12345678/DOC123",
                stream=True,
                custom_base_url=client.base_url.split("/patent")[0],
            )

            # Verify file was written correctly
            mock_file.write.assert_called_with(b"test content")
            # Use os.path.join for cross-platform paths
            assert result == os.path.join("/tmp", "test_document.pdf")

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_application_document_content_disposition_parsing(
        self, mock_make_request
    ) -> None:
        """Test download_application_document with Content-Disposition header parsing."""
        # Setup mock to simulate a Response object
        mock_response = MagicMock(spec=requests.Response)
        mock_response.headers = {
            "Content-Disposition": 'attachment; filename="test_file.pdf"'
        }
        mock_response.iter_content.return_value = [b"test content"]
        mock_make_request.return_value = mock_response

        # Setup os.path.exists to return False so os.makedirs is called
        with patch("os.path.exists", return_value=False), patch(
            "os.makedirs"
        ) as mock_makedirs, patch("builtins.open", mock_open()) as mock_file:
            # Create client
            client = PatentDataClient(api_key="test_key")

            # Call the method
            result = client.download_application_document(
                application_number="12345678",
                document_id="document123",
                destination="./downloads",
            )

            # Verify the path extraction from Content-Disposition header
            assert result == os.path.join("./downloads", "test_file.pdf")
            mock_makedirs.assert_called_once_with("./downloads")
            mock_file.assert_called_once_with(file=result, mode="wb")

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_application_document_no_filename_in_header(
        self, mock_make_request
    ) -> None:
        """Test download_application_document with Content-Disposition header but no filename."""
        # Setup mock to simulate a Response object
        mock_response = MagicMock(spec=requests.Response)
        mock_response.headers = {"Content-Disposition": "attachment;"}  # No filename
        mock_response.iter_content.return_value = [b"test content"]
        mock_make_request.return_value = mock_response

        # Setup os.path.exists to return False so os.makedirs is called
        with patch("os.path.exists", return_value=False), patch(
            "os.makedirs"
        ) as mock_makedirs, patch("builtins.open", mock_open()) as mock_file:
            # Create client
            client = PatentDataClient(api_key="test_key")

            # Call the method
            result = client.download_application_document(
                application_number="12345678",
                document_id="document123",
                destination="./downloads",
            )

            # Should use document_id as filename
            assert result == os.path.join("./downloads", "document123")

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_application_document_no_content_disposition(
        self, mock_make_request
    ) -> None:
        """Test download_application_document without Content-Disposition header."""
        # Setup mock to simulate a Response object
        mock_response = MagicMock(spec=requests.Response)
        mock_response.headers = {}  # No Content-Disposition header
        mock_response.iter_content.return_value = [b"test content"]
        mock_make_request.return_value = mock_response

        # Setup os.path.exists to return False so os.makedirs is called
        with patch("os.path.exists", return_value=False), patch(
            "os.makedirs"
        ) as mock_makedirs, patch("builtins.open", mock_open()) as mock_file:
            # Create client
            client = PatentDataClient(api_key="test_key")

            # Call the method
            result = client.download_application_document(
                application_number="12345678",
                document_id="document123",
                destination="./downloads",
            )

            # Should use document_id as filename when no Content-Disposition header
            assert result == os.path.join("./downloads", "document123")

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_application_document_non_response_object(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test download_application_document with a non-Response object."""
        # Return an object that is definitely not a requests.Response
        mock_make_request.return_value = {"not": "a response object"}

        # Create client
        client = PatentDataClient(api_key="test_key")

        # Call should raise TypeError
        with pytest.raises(
            TypeError, match="Expected a Response object for streaming download"
        ):
            client.download_application_document(
                application_number="12345678", document_id="DOC123", destination="/tmp"
            )

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_documents(self, mock_make_request: MagicMock) -> None:
        """Test get_application_documents method."""
        # Setup mock
        mock_response_obj = PatentDataResponse(count=1, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        result = client.get_application_documents(application_number="12345678")

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/12345678/documents",
            response_class=PatentDataResponse,
        )

        # Verify result
        assert isinstance(result, PatentDataResponse)
        assert result.count == 1

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_associated_documents(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test get_application_associated_documents method."""
        # Setup mock
        mock_response_obj = PatentDataResponse(count=1, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        result = client.get_application_associated_documents(
            application_number="12345678"
        )

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/12345678/associated-documents",
            response_class=PatentDataResponse,
        )

        # Verify result
        assert isinstance(result, PatentDataResponse)
        assert result.count == 1


class TestPatentApplicationMethods:
    """Tests for patent application data methods."""

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_patent_applications_default_params(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test download_patent_applications with default parameters."""
        # Setup mock response
        mock_response_obj = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        # Create client and call method without params
        client = PatentDataClient(api_key="test_key")
        result = client.download_patent_applications()

        # Verify request was made correctly with default format
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/search/download",
            params={"format": "json"},
            response_class=PatentDataResponse,
        )

        # Verify the result type
        assert isinstance(result, PatentDataResponse)

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_patent_applications_missing_format(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test download_patent_applications when format is missing in params."""
        # Setup mock response
        mock_response_obj = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        # Create client and call method with params missing 'format'
        client = PatentDataClient(api_key="test_key")
        result = client.download_patent_applications(params={"q": "test"})

        # Verify request was made correctly with default format added
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/search/download",
            params={"q": "test", "format": "json"},
            response_class=PatentDataResponse,
        )

        # Verify the result type
        assert isinstance(result, PatentDataResponse)

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_patent_applications_custom_format(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test download_patent_applications with custom format."""
        # Setup mock response
        mock_response_obj = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        # Create client and call method with custom format
        client = PatentDataClient(api_key="test_key")
        result = client.download_patent_applications(format="csv")

        # Verify request was made correctly with custom format
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/search/download",
            params={"format": "csv"},
            response_class=PatentDataResponse,
        )

        # Verify the result type
        assert isinstance(result, PatentDataResponse)

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_patent_applications_format_argument(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test download_patent_applications with format passed as a separate argument."""
        # Setup mock response
        mock_response_obj = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        # Create client and call method with format passed as a separate argument
        client = PatentDataClient(api_key="test_key")
        result = client.download_patent_applications(params={"q": "test"}, format="csv")

        # Verify request was made correctly with format added to params
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/search/download",
            params={"q": "test", "format": "csv"},
            response_class=PatentDataResponse,
        )

        # Verify the result type
        assert isinstance(result, PatentDataResponse)

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_patent_applications_post(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test download_patent_applications_post method."""
        # Setup mock
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
        download_request = {
            "q": "Test",
            "format": "csv",
            "fields": ["patentNumber", "inventionTitle"],
        }
        result = client.download_patent_applications_post(
            download_request=download_request
        )

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="POST",
            endpoint="applications/search/download",
            json_data=download_request,
            response_class=PatentDataResponse,
        )

        # Verify result
        assert isinstance(result, PatentDataResponse)
        assert result.count == 1


class TestPatentApplicationDetailsDataMethods:
    """Tests for specific patent application data retrieval methods."""

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_adjustment(self, mock_make_request: MagicMock) -> None:
        """Test get_application_adjustment method."""
        # Setup mock
        mock_response_obj = PatentDataResponse(count=1, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        result = client.get_application_adjustment(application_number="12345678")

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/12345678/adjustment",
            response_class=PatentDataResponse,
        )

        # Verify result
        assert isinstance(result, PatentDataResponse)
        assert result.count == 1

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_assignment(self, mock_make_request: MagicMock) -> None:
        """Test get_application_assignment method."""
        # Setup mock
        mock_response_obj = PatentDataResponse(count=1, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        result = client.get_application_assignment(application_number="12345678")

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/12345678/assignment",
            response_class=PatentDataResponse,
        )

        # Verify result
        assert isinstance(result, PatentDataResponse)
        assert result.count == 1

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_attorney(self, mock_make_request: MagicMock) -> None:
        """Test get_application_attorney method."""
        # Setup mock
        mock_response_obj = PatentDataResponse(count=1, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        result = client.get_application_attorney(application_number="12345678")

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/12345678/attorney",
            response_class=PatentDataResponse,
        )

        # Verify result
        assert isinstance(result, PatentDataResponse)
        assert result.count == 1

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_attorney_special_response_types(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test get_application_attorney with special response types."""
        # Create client
        client = PatentDataClient(api_key="test_key")

        # Test with PatentDataResponse object already
        mock_response = PatentDataResponse(count=1, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response

        result = client.get_application_attorney(application_number="12345678")
        assert result is mock_response

        # Test with unexpected response type
        mock_make_request.return_value = "not a PatentDataResponse"

        with pytest.raises(AssertionError):
            client.get_application_attorney(application_number="12345678")

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_continuity(self, mock_make_request: MagicMock) -> None:
        """Test get_application_continuity method."""
        # Setup mock
        mock_response_obj = PatentDataResponse(count=1, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        result = client.get_application_continuity(application_number="12345678")

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/12345678/continuity",
            response_class=PatentDataResponse,
        )

        # Verify result
        assert isinstance(result, PatentDataResponse)
        assert result.count == 1

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_foreign_priority(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test get_application_foreign_priority method."""
        # Setup mock
        mock_response_obj = PatentDataResponse(count=1, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        result = client.get_application_foreign_priority(application_number="12345678")

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/12345678/foreign-priority",
            response_class=PatentDataResponse,
        )

        # Verify result
        assert isinstance(result, PatentDataResponse)
        assert result.count == 1

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_transactions(self, mock_make_request: MagicMock) -> None:
        """Test get_application_transactions method."""
        # Setup mock
        mock_response_obj = PatentDataResponse(count=1, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        result = client.get_application_transactions(application_number="12345678")

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/12345678/transactions",
            response_class=PatentDataResponse,
        )

        # Verify result
        assert isinstance(result, PatentDataResponse)
        assert result.count == 1


class TestPatentStatusCodeMethods:
    """Tests for patent status code methods."""

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_patent_status_codes(self, mock_make_request: MagicMock) -> None:
        """Test get_patent_status_codes method."""
        # Setup mock
        mock_response = {
            "statusCodeBag": [
                {
                    "statusCode": "150",
                    "statusText": "Awaiting Assignment",
                },
                {
                    "statusCode": "250",
                    "statusText": "Assigned to Examiner",
                },
            ],
            "count": 2,
        }
        mock_make_request.return_value = mock_response

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        result = client.get_patent_status_codes(params={"q": "awaiting"})

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="status-codes",
            params={"q": "awaiting"},
        )

        # Verify result
        assert isinstance(result, dict)
        assert result == mock_response
        assert result["count"] == 2
        assert len(result["statusCodeBag"]) == 2

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_patent_status_codes_with_params(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test get_patent_status_codes method with different parameter combinations."""
        # Setup mock
        mock_response = {
            "statusCodeBag": [
                {
                    "statusCode": "150",
                    "statusText": "Awaiting Assignment",
                    "statusCategory": "Examination",
                    "statusDate": "2020-01-01",
                },
                {
                    "statusCode": "250",
                    "statusText": "Assigned to Examiner",
                    "statusCategory": "Examination",
                    "statusDate": "2020-02-01",
                },
            ],
            "count": 2,
        }
        mock_make_request.return_value = mock_response

        # Create client
        client = PatentDataClient(api_key="test_key")

        # Test with offset and limit
        mock_make_request.reset_mock()
        result = client.get_patent_status_codes(params={"offset": "10", "limit": "5"})
        mock_make_request.assert_called_with(
            method="GET",
            endpoint="status-codes",
            params={"offset": "10", "limit": "5"},
        )
        assert result == mock_response

        # Test with combination of parameters
        mock_make_request.reset_mock()
        result = client.get_patent_status_codes(
            params={"q": "examination", "offset": "0", "limit": "10"}
        )
        mock_make_request.assert_called_with(
            method="GET",
            endpoint="status-codes",
            params={"q": "examination", "offset": "0", "limit": "10"},
        )
        assert result == mock_response

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_search_patent_status_codes_post(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test search_patent_status_codes_post method."""
        # Setup mock
        mock_response = {
            "statusCodeBag": [
                {
                    "statusCode": "150",
                    "statusText": "Awaiting Assignment",
                },
            ],
            "count": 1,
        }
        mock_make_request.return_value = mock_response

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        search_request = {
            "q": "awaiting",
            "limit": 10,
            "offset": 0,
        }
        result = client.search_patent_status_codes_post(search_request=search_request)

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="POST",
            endpoint="status-codes",
            json_data=search_request,
        )

        # Verify result
        assert isinstance(result, dict)
        assert result == mock_response
        assert result["count"] == 1

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_search_patent_status_codes_post_with_various_payloads(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test search_patent_status_codes_post with different payload structures."""
        # Setup mock
        mock_response = {
            "statusCodeBag": [
                {
                    "statusCode": "150",
                    "statusText": "Awaiting Assignment",
                }
            ],
            "count": 1,
        }
        mock_make_request.return_value = mock_response

        # Create client
        client = PatentDataClient(api_key="test_key")

        # Test with more complex search request
        mock_make_request.reset_mock()
        search_request = {
            "filters": [{"field": "statusCategory", "value": "Examination"}],
            "pagination": {"offset": "0", "limit": "25"},
            "sort": [{"field": "statusDate", "order": "desc"}],
        }
        result = client.search_patent_status_codes_post(search_request=search_request)
        mock_make_request.assert_called_with(
            method="POST",
            endpoint="status-codes",
            json_data=search_request,
        )
        assert result == mock_response


class TestPatentDataEdgeCases:
    """Tests for edge cases in the PatentDataClient class."""

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_patent_by_application_number_patentFileWrapperDataBag_not_found(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test get_patent_by_application_number when application not found in patentFileWrapperDataBag."""
        # Setup mock to return a response with patentFileWrapperDataBag but not containing the requested application
        mock_response = {
            "patentFileWrapperDataBag": [
                {"applicationNumberText": "87654321", "otherData": "test"},
            ]
        }
        mock_make_request.return_value = mock_response

        # Create client
        client = PatentDataClient(api_key="test_key")

        # This should trigger the ValueError when application not found in patentFileWrapperDataBag
        with pytest.raises(
            ValueError,
            match="Patent with application number 12345678 not found in response",
        ):
            client.get_patent_by_application_number(application_number="12345678")

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_patent_by_application_number_unexpected_response_type(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test get_patent_by_application_number with unexpected response type."""
        # Setup mock to return a non-dict, non-PatentFileWrapper response
        mock_make_request.return_value = ["unexpected", "response", "type"]

        # Create client
        client = PatentDataClient(api_key="test_key")

        # This should trigger the TypeError for unexpected response type
        with pytest.raises(TypeError, match="Unexpected response type"):
            client.get_patent_by_application_number(application_number="12345678")

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_patent_status_codes_edge_cases(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test edge cases for get_patent_status_codes method."""
        # Test with different response types to cover assertion branches
        # 1. Test with non-dict response
        mock_make_request.return_value = "not a dict"

        client = PatentDataClient(api_key="test_key")

        # Should raise TypeError for non-dict response
        with pytest.raises(AssertionError):
            client.get_patent_status_codes()

        # 2. Test with empty dict response
        mock_make_request.return_value = {}

        # Should not raise error even with empty dict
        result = client.get_patent_status_codes()
        assert result == {}

        # 3. Test with minimal dict
        mock_make_request.return_value = {"count": 0}

        result = client.get_patent_status_codes()
        assert result == {"count": 0}

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_adjustment_assert_type(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test get_application_adjustment with a non-PatentDataResponse return type."""
        # Setup mock to return a dict instead of PatentDataResponse to trigger assertion
        mock_make_request.return_value = {"data": "test"}

        # Create client
        client = PatentDataClient(api_key="test_key")

        # Expect assertion error when not returning PatentDataResponse
        with pytest.raises(AssertionError):
            client.get_application_adjustment(application_number="12345678")
