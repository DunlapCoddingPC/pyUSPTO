"""
Consolidated tests for the pyUSPTO.clients.patent_data.PatentDataClient.

This module combines tests for initialization, core functionality, document handling,
metadata retrieval, status codes, return type validation, and edge cases for the
PatentDataClient.
"""

import os
import re
from datetime import date, datetime, timezone
from typing import Any, Dict, Iterator, List, Optional
from unittest.mock import MagicMock, Mock, mock_open, patch
from urllib.parse import urlparse

import pytest
import requests

from pyUSPTO.clients.patent_data import PatentDataClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.exceptions import USPTOApiBadRequestError, USPTOApiError
from pyUSPTO.models.patent_data import (
    ApplicationContinuityData,
    ApplicationMetaData,
    Assignment,
    AssociatedDocumentsData,
    Attorney,
    ChildContinuity,
    DirectionCategory,
    Document,
    DocumentBag,
    DocumentDownloadFormat,
    DocumentMetaData,
    EventData,
    ForeignPriority,
    Inventor,
    ParentContinuity,
    PatentDataResponse,
    PatentFileWrapper,
    PatentTermAdjustmentData,
    RecordAttorney,
    StatusCode,
    StatusCodeCollection,
    StatusCodeSearchResponse,
)

# --- Fixtures ---

@pytest.fixture
def api_key_fixture() -> str:
    """Provides a test API key."""
    return "test_key"

@pytest.fixture
def patent_data_client(api_key_fixture: str) -> PatentDataClient:
    """Provides a PatentDataClient instance initialized with a test API key."""
    return PatentDataClient(api_key=api_key_fixture)

@pytest.fixture
def mock_application_meta_data() -> ApplicationMetaData:
    """Provides a mock ApplicationMetaData instance."""
    # Create an instance of the Inventor class
    first_inventor = Inventor(inventor_name_text="John Inventor")
    # If you had more complex inventors with addresses, you'd mock Address objects too.

    return ApplicationMetaData(
        invention_title="Test Invention",
        patent_number="10000000",
        filing_date=date(2020, 1, 1),
        grant_date=date(2022, 1, 1),
        first_applicant_name="Test Applicant",
        inventor_bag=[first_inventor],
        cpc_classification_bag=["G06F1/00"],
    )

@pytest.fixture
def mock_assignment() -> Assignment:
    """Provides a mock Assignment instance."""
    return Assignment(reel_number="12345", frame_number="67890")

@pytest.fixture
def mock_record_attorney() -> RecordAttorney:
    """Provides a mock RecordAttorney instance."""
    return RecordAttorney(
        attorney_bag=[
            Attorney(
                first_name="James", last_name="Legal", registration_number="12345"
            )
        ]
    )

@pytest.fixture
def mock_foreign_priority() -> ForeignPriority:
    """Provides a mock ForeignPriority instance."""
    return ForeignPriority(
        ip_office_name="European Patent Office",
        application_number_text="EP12345678",
    )

@pytest.fixture
def mock_parent_continuity() -> ParentContinuity:
    """Provides a mock ParentContinuity instance."""
    return ParentContinuity(parent_application_number_text="11111111")

@pytest.fixture
def mock_child_continuity() -> ChildContinuity:
    """Provides a mock ChildContinuity instance."""
    return ChildContinuity(child_application_number_text="99999999")

@pytest.fixture
def mock_patent_term_adjustment_data() -> PatentTermAdjustmentData:
    """Provides a mock PatentTermAdjustmentData instance."""
    return PatentTermAdjustmentData(adjustment_total_quantity=150.0)

@pytest.fixture
def mock_event_data() -> EventData:
    """Provides a mock EventData instance."""
    dt = date(2022, 1, 1) # Ensure date object for EventData
    return EventData(
        event_code="COMP",
        event_description_text="Application ready for examination",
        event_date=dt,
    )

@pytest.fixture
def mock_pgpub_document_meta_data() -> DocumentMetaData:
    """Provides a mock pgpub DocumentMetaData instance."""
    dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    return DocumentMetaData(
        zip_file_name="pgpub.zip",
        product_identifier="PGPUB",
        file_create_date_time=dt,
    )

@pytest.fixture
def mock_grant_document_meta_data() -> DocumentMetaData:
    """Provides a mock grant DocumentMetaData instance."""
    dt = datetime(2023, 2, 1, 12, 0, 0, tzinfo=timezone.utc)
    return DocumentMetaData(
        zip_file_name="grant.zip",
        product_identifier="GRANT",
        file_create_date_time=dt,
    )

@pytest.fixture
def mock_patent_file_wrapper(
    mock_application_meta_data: ApplicationMetaData,
    mock_assignment: Assignment,
    mock_record_attorney: RecordAttorney,
    mock_foreign_priority: ForeignPriority,
    mock_parent_continuity: ParentContinuity,
    mock_child_continuity: ChildContinuity,
    mock_patent_term_adjustment_data: PatentTermAdjustmentData,
    mock_event_data: EventData,
    mock_pgpub_document_meta_data: DocumentMetaData,
    mock_grant_document_meta_data: DocumentMetaData,
) -> PatentFileWrapper:
    """
    Provides a comprehensive mock PatentFileWrapper instance.
    Application number is set to '12345678'.
    """
    return PatentFileWrapper(
        application_number_text="12345678",
        application_meta_data=mock_application_meta_data,
        assignment_bag=[mock_assignment],
        record_attorney=mock_record_attorney,
        foreign_priority_bag=[mock_foreign_priority],
        parent_continuity_bag=[mock_parent_continuity],
        child_continuity_bag=[mock_child_continuity],
        patent_term_adjustment_data=mock_patent_term_adjustment_data,
        event_data_bag=[mock_event_data],
        pgpub_document_meta_data=mock_pgpub_document_meta_data,
        grant_document_meta_data=mock_grant_document_meta_data,
    )

@pytest.fixture
def mock_patent_file_wrapper_minimal() -> PatentFileWrapper:
    """Provides a minimal mock PatentFileWrapper instance with only applicationNumberText."""
    return PatentFileWrapper(application_number_text="12345678")


@pytest.fixture
def mock_patent_data_response_with_data(
    mock_patent_file_wrapper: PatentFileWrapper,
) -> PatentDataResponse:
    """
    Provides a mock PatentDataResponse instance containing one mock_patent_file_wrapper.
    """
    return PatentDataResponse(
        count=1, patent_file_wrapper_data_bag=[mock_patent_file_wrapper]
    )

@pytest.fixture
def mock_patent_data_response_empty() -> PatentDataResponse:
    """Provides an empty mock PatentDataResponse instance."""
    return PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])


@pytest.fixture
def client_with_mocked_request(
    patent_data_client: PatentDataClient,
) -> Iterator[tuple[PatentDataClient, MagicMock]]:
    """
    Provides a PatentDataClient instance with its _make_request method mocked.
    Returns a tuple (client, mock_make_request).
    """
    with patch.object(
        patent_data_client, "_make_request", autospec=True
    ) as mock_make_request:
        yield patent_data_client, mock_make_request

@pytest.fixture
def mock_requests_response() -> MagicMock:
    """Provides a mock requests.Response object for download tests."""
    response = MagicMock(spec=requests.Response)
    response.headers = {}
    response.iter_content.return_value = [b"test content"]
    return response




# --- Test Classes ---

class TestPatentDataClientInit:
    """Tests for the initialization of the PatentDataClient."""

    def test_init_with_api_key(self, api_key_fixture: str) -> None:
        """Test initialization with API key."""
        client = PatentDataClient(api_key=api_key_fixture)
        assert client.api_key == api_key_fixture
        assert client.base_url == "https://api.uspto.gov"

    def test_init_with_custom_base_url(self, api_key_fixture: str) -> None:
        """Test initialization with custom base URL."""
        custom_url = "https://custom.api.test.com"
        client = PatentDataClient(api_key=api_key_fixture, base_url=custom_url)
        assert client.api_key == api_key_fixture
        assert client.base_url == custom_url

    def test_init_with_config(self) -> None:
        """Test initialization with config object."""
        config_key = "config_key"
        config_url = "https://config.api.test.com"
        config = USPTOConfig(api_key=config_key, patent_data_base_url=config_url)
        client = PatentDataClient(config=config)
        assert client.api_key == config_key
        assert client.base_url == config_url
        assert client.config is config

    def test_init_with_api_key_and_config(self, api_key_fixture: str) -> None:
        """Test initialization with both API key and config."""
        config = USPTOConfig(
            api_key="config_key", patent_data_base_url="https://config.api.test.com"
        )
        # API key from param takes precedence for api_key
        client = PatentDataClient(api_key=api_key_fixture, config=config)
        assert client.api_key == api_key_fixture
        # base_url from param takes precedence if provided, otherwise from config
        assert client.base_url == "https://config.api.test.com"

        custom_url = "https://custom.url.com"
        client_custom_url = PatentDataClient(
            api_key=api_key_fixture, base_url=custom_url, config=config
        )
        assert client_custom_url.base_url == custom_url


class TestPatentApplicationSearch:
    """Tests for patent application search functionalities."""

    def test_get_patent_applications(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_with_data: PatentDataResponse,
    ) -> None:
        """Test get_patent_applications method (GET search)."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_with_data
        params = {"q": "Test", "limit": 10, "offset": 0}

        result = client.get_patent_applications(params=params)

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/patent/applications/search",
            params=params,
            response_class=PatentDataResponse,
        )
        assert result is mock_patent_data_response_with_data

    def test_search_patent_applications_post(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_with_data: PatentDataResponse,
    ) -> None:
        """Test search_patent_applications_post method (POST search)."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_with_data
        search_request = {
            "q": "Test",
            "filters": [{"field": "inventionSubjectMatterCategory", "value": "MECHANICAL"}],
            "pagination": {"offset": 0, "limit": 100},
        }

        result = client.search_patent_applications_post(search_request=search_request)

        mock_make_request.assert_called_once_with(
            method="POST",
            endpoint="api/v1/patent/applications/search",
            json_data=search_request,
            response_class=PatentDataResponse,
        )
        assert result is mock_patent_data_response_with_data

    def test_search_patents_basic_filter(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_with_data: PatentDataResponse,
    ) -> None:
        """Test search_patents with a basic patent number filter."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_with_data
        patent_num = "10000000"

        client.search_patents(patent_number=patent_num, limit=10, offset=0)

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/patent/applications/search",
            params={
                "q": f"applicationMetaData.patentNumber:{patent_num}",
                "limit": 10,
                "offset": 0,
            },
            response_class=PatentDataResponse,
        )

    @pytest.mark.parametrize(
        "search_params, expected_q_part",
        [
            ({"application_number": "app123"}, "applicationNumberText:app123"),
            ({"inventor_name": "Doe J"}, "applicationMetaData.inventorBag.inventorNameText:Doe J"),
            ({"applicant_name": "Corp Inc"}, "applicationMetaData.firstApplicantName:Corp Inc"),
            ({"assignee_name": "Assignee Ltd"}, "assignmentBag.assigneeBag.assigneeNameText:Assignee Ltd"),
            ({"classification": "H04L"}, "applicationMetaData.cpcClassificationBag:H04L"),
            ({"filing_date_from": "2021-01-01"}, "applicationMetaData.filingDate:>=2021-01-01"),
            ({"filing_date_to": "2021-12-31"}, "applicationMetaData.filingDate:<=2021-12-31"),
            (
                {"filing_date_from": "2021-01-01", "filing_date_to": "2021-12-31"},
                "applicationMetaData.filingDate:[2021-01-01 TO 2021-12-31]",
            ),
            ({"grant_date_from": "2022-01-01"}, "applicationMetaData.grantDate:>=2022-01-01"),
            ({"grant_date_to": "2022-12-31"}, "applicationMetaData.grantDate:<=2022-12-31"),
            (
                {"grant_date_from": "2022-01-01", "grant_date_to": "2022-12-31"},
                "applicationMetaData.grantDate:[2022-01-01 TO 2022-12-31]",
            ),
        ],
    )
    def test_search_patents_various_filters(
        self,
        search_params: Dict[str, Any],
        expected_q_part: str,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_empty: PatentDataResponse,
    ) -> None:
        """Test search_patents with various individual filters."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_empty
        
        # Default limit and offset
        limit = 25 
        offset = 0
        final_params = {"limit": limit, "offset": offset, **search_params}


        client.search_patents(**final_params) # type: ignore

        expected_call_params = {"q": expected_q_part, "limit": limit, "offset": offset}
        
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/patent/applications/search",
            params=expected_call_params,
            response_class=PatentDataResponse,
        )
    
    def test_search_patents_multiple_filters(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_empty: PatentDataResponse,
    ) -> None:
        """Test search_patents with multiple filters combined."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_empty

        client.search_patents(
            inventor_name="John Smith",
            filing_date_from="2020-01-01",
            filing_date_to="2022-01-01",
            query="Test Invention",
            limit=20,
            offset=10,
        )
        # Order of q_parts matters for exact string match if not using a set for comparison
        # The client implementation specific order: app_num, patent_num, inventor, applicant, assignee, classification, filing_date, grant_date, query
        expected_q = (
            "applicationMetaData.inventorBag.inventorNameText:John Smith AND "
            "applicationMetaData.filingDate:[2020-01-01 TO 2022-01-01] AND "
            "Test Invention"
        )
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/patent/applications/search",
            params={"q": expected_q, "limit": 20, "offset": 10},
            response_class=PatentDataResponse,
        )

    def test_search_patents_with_empty_query_params(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_empty: PatentDataResponse,
    ) -> None:
        """Test search_patents with no specific query parameters, only default limit/offset."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_empty

        client.search_patents() # Uses default limit=25, offset=0

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/patent/applications/search",
            params={"limit": 25, "offset": 0}, # q is None, so not included
            response_class=PatentDataResponse,
        )

    def test_search_patents_explicitly_null_limit_offset(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_empty: PatentDataResponse,
    ) -> None:
        """Test search_patents with limit and offset explicitly set to None."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_empty

        client.search_patents(query="test query", limit=None, offset=None)

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/patent/applications/search",
            params={"q": "test query"}, # Only q should be present
            response_class=PatentDataResponse,
        )


class TestPatentApplicationDetails:
    """Tests for retrieving details of a single patent application."""

    def test_get_patent_application_details_success(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_with_data: PatentDataResponse,
        mock_patent_file_wrapper: PatentFileWrapper,
    ) -> None:
        """Test successful retrieval of patent application details."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_with_data
        app_num = mock_patent_file_wrapper.application_number_text
        assert app_num is not None

        result = client.get_patent_application_details(application_number=app_num)

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint=f"api/v1/patent/applications/{app_num}",
            response_class=PatentDataResponse,
        )
        assert result is mock_patent_file_wrapper # Client extracts this
        assert result is not None

        assert result.application_number_text == app_num
        assert result.application_meta_data.invention_title == "Test Invention" # type: ignore

    def test_get_patent_application_details_empty_bag_returns_none(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_empty: PatentDataResponse,
    ) -> None:
        """Test get_patent_application_details returns None if patentFileWrapperDataBag is empty."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_empty
        app_num_to_request = "nonexistent123"

        result = client.get_patent_application_details(application_number=app_num_to_request)
        assert result is None


class TestPatentApplicationPagination:
    """Tests for patent application result pagination."""

    def test_paginate_patents(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test paginate_patents method correctly calls paginate_results."""
        with patch.object(patent_data_client, "paginate_results", autospec=True) as mock_paginate_results:
            patent1 = PatentFileWrapper(application_number_text="123")
            patent2 = PatentFileWrapper(application_number_text="456")
            mock_paginate_results.return_value = iter([patent1, patent2])

            results = list(patent_data_client.paginate_patents(query="Test", limit=20))

            mock_paginate_results.assert_called_once_with(
                method_name="get_patent_applications",
                response_container_attr="patent_file_wrapper_data_bag",
                query="Test",
                limit=20,
            )
            assert len(results) == 2
            assert results[0] is patent1
            assert results[1] is patent2


class TestPatentApplicationDocumentListing:
    """Tests for listing documents associated with a patent application."""

    def test_get_application_documents(
        self, client_with_mocked_request: tuple[PatentDataClient, MagicMock]
    ) -> None:
        """Test retrieval of application documents."""
        client, mock_make_request = client_with_mocked_request
        app_num = "appDoc123"
        mock_response_dict = {
            "documentBag": [
                {
                    "documentIdentifier": "DOC1",
                    "documentCode": "IDS",
                    "officialDate": "2023-01-01T00:00:00Z",
                    "downloadOptionBag": [{"mimeTypeIdentifier": "PDF", "downloadURI": "/doc1.pdf"}],
                }
            ]
        }
        mock_make_request.return_value = mock_response_dict # This endpoint returns dict directly

        result = client.get_application_documents(application_number=app_num)

        mock_make_request.assert_called_once_with(
            method="GET", endpoint=f"api/v1/patent/applications/{app_num}/documents"
        )
        assert isinstance(result, DocumentBag)
        assert len(result.documents) == 1
        assert result.documents[0].document_identifier == "DOC1"


class TestPatentApplicationAssociatedDocuments:
    """Tests for retrieving associated documents metadata."""

    def test_get_application_associated_documents(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_with_data: PatentDataResponse,
        mock_patent_file_wrapper: PatentFileWrapper,
    ) -> None:
        """Test retrieval of associated documents metadata."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_with_data
        app_num = mock_patent_file_wrapper.application_number_text
        assert app_num is not None

        result = client.get_application_associated_documents(application_number=app_num)

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint=f"api/v1/patent/applications/{app_num}/associated-documents",
            response_class=PatentDataResponse,
        )
        assert isinstance(result, AssociatedDocumentsData)
        assert result.pgpub_document_meta_data is mock_patent_file_wrapper.pgpub_document_meta_data
        assert result.grant_document_meta_data is mock_patent_file_wrapper.grant_document_meta_data


class TestPatentDocumentDownload:
    """Tests for downloading individual patent documents."""

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.makedirs")
    @patch("os.path.exists")
    def test_download_document_file_with_content_disposition(
        self,
        mock_exists: MagicMock,
        mock_makedirs: MagicMock,
        mock_file_open: MagicMock,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_requests_response: MagicMock,
    ) -> None:
        """Test document download with Content-Disposition header."""
        client, mock_make_request = client_with_mocked_request
        mock_exists.return_value = False # Ensure makedirs is called
        
        filename_from_header = "test_document.pdf"
        mock_requests_response.headers = {"Content-Disposition": f'filename="{filename_from_header}"'}
        mock_make_request.return_value = mock_requests_response

        app_num = "appDL123"
        doc_id = "orig_doc_id.zip" # Original ID, filename comes from header
        dest_dir = "/tmp/downloads"
        
        expected_path = os.path.join(dest_dir, filename_from_header)

        result_path = client.download_document_file(
            application_number=app_num, document_id=doc_id, destination_dir=dest_dir
        )

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint=f"api/v1/download/applications/{app_num}/{doc_id}",
            stream=True,
        )
        mock_makedirs.assert_called_once_with(dest_dir, exist_ok=True)
        mock_file_open.assert_called_once_with(file=expected_path, mode="wb")
        mock_file_open().write.assert_called_with(b"test content")
        assert result_path == expected_path

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.makedirs")
    @patch("os.path.exists")
    def test_download_document_file_no_content_disposition(
        self,
        mock_exists: MagicMock,
        mock_makedirs: MagicMock,
        mock_file_open: MagicMock,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_requests_response: MagicMock, # headers will be empty by default
    ) -> None:
        """Test document download when Content-Disposition is missing, uses document_id as filename."""
        client, mock_make_request = client_with_mocked_request
        mock_exists.return_value = True # makedirs might not be called if dir exists
        mock_make_request.return_value = mock_requests_response

        app_num = "appDL456"
        doc_id = "document_as_filename.pdf"
        dest_dir = "./test_downloads"
        expected_path = os.path.join(dest_dir, doc_id)

        result_path = client.download_document_file(
            application_number=app_num, document_id=doc_id, destination_dir=dest_dir
        )
        
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint=f"api/v1/download/applications/{app_num}/{doc_id}",
            stream=True,
        )
        mock_file_open.assert_called_once_with(file=expected_path, mode="wb")
        assert result_path == expected_path
        
    def test_download_document_file_missing_params(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock], # Use mocked client
        mock_requests_response: MagicMock # For the mocked network call
    ) -> None:

        """Test download_document_file raises TypeError for missing or invalid parameters."""
        client, mock_make_request = client_with_mocked_request
        
        # Scenario 1: destination_dir is None (causes TypeError inside os.path functions)
        # Mock _make_request to return a valid response to allow execution to reach os.path
        mock_make_request.return_value = mock_requests_response
        with pytest.raises(TypeError):
            client.download_document_file(
                application_number="123",
                document_id="doc.pdf",
                destination_dir=None # type: ignore
            )
        mock_make_request.reset_mock() # Reset for next calls if needed

        # Scenario 2: Missing required arguments (causes TypeError from method signature)
        with pytest.raises(TypeError):
            client.download_document_file(application_number="123", document_id="doc.pdf") # type: ignore

        with pytest.raises(TypeError):
            client.download_document_file(application_number="123", destination_dir="/tmp") # type: ignore
            
        with pytest.raises(TypeError):
            client.download_document_file(document_id="doc.pdf", destination_dir="/tmp") # type: ignore

class TestPatentApplicationBulkDownload:
    """Tests for bulk downloading of patent application search results."""

    @pytest.mark.parametrize("format_type", ["json", "csv", "xml"])
    def test_download_patent_applications_get(
        self,
        format_type: str,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_empty: PatentDataResponse,
    ) -> None:
        """Test GET bulk download with various formats."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_empty
        params = {"q": "bulk test", "format": format_type} # format in params overrides format_type arg

        result = client.download_patent_applications_get(params=params) # format_type arg will be overridden

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/patent/applications/search/download",
            params=params, # The format from params is used
            response_class=PatentDataResponse,
        )
        assert result is mock_patent_data_response_empty

    def test_download_patent_applications_get_default_format(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_empty: PatentDataResponse,
    ) -> None:
        """Test GET bulk download uses default format 'json' if not specified."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_empty
        
        client.download_patent_applications_get(params={"q": "test"}) # No format in params or arg

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/patent/applications/search/download",
            params={"q": "test", "format": "json"}, # Default format added
            response_class=PatentDataResponse,
        )

    def test_download_patent_applications_post(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_with_data: PatentDataResponse,
    ) -> None:
        """Test POST bulk download."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_with_data
        download_request = {"q": "Test POST", "format": "xml", "fields": ["patentNumber"]}

        result = client.download_patent_applications_post(download_request=download_request)

        mock_make_request.assert_called_once_with(
            method="POST",
            endpoint="api/v1/patent/applications/search/download",
            json_data=download_request,
            response_class=PatentDataResponse,
        )
        assert result is mock_patent_data_response_with_data

    def test_download_patent_applications_get_default_params_when_none(
            self,
            client_with_mocked_request: tuple[PatentDataClient, MagicMock],
            mock_patent_data_response_empty: PatentDataResponse,
        ) -> None:
            """Test GET bulk download correctly initializes params if None and uses default format."""
            client, mock_make_request = client_with_mocked_request
            mock_make_request.return_value = mock_patent_data_response_empty
            
            # Call download_patent_applications_get without the 'params' argument
            # so it defaults to None internally.
            result = client.download_patent_applications_get() 

            # Verify that params was initialized to {} and then 'format': 'json' was added.
            mock_make_request.assert_called_once_with(
                method="GET",
                endpoint="api/v1/patent/applications/search/download",
                params={"format": "json"}, 
                response_class=PatentDataResponse,
            )
            assert result is mock_patent_data_response_empty


class TestApplicationSpecificDataRetrieval:
    """Tests for retrieving specific metadata facets of a patent application."""

    def test_get_application_metadata(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_with_data: PatentDataResponse,
        mock_patent_file_wrapper: PatentFileWrapper,
    ) -> None:
        """Test get_application_metadata returns ApplicationMetaData."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_with_data
        app_num = mock_patent_file_wrapper.application_number_text
        
        assert app_num is not None

        result = client.get_application_metadata(application_number=app_num)
        assert result is mock_patent_file_wrapper.application_meta_data

    def test_get_application_adjustment(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_with_data: PatentDataResponse,
        mock_patent_file_wrapper: PatentFileWrapper,
    ) -> None:
        """Test get_application_adjustment returns PatentTermAdjustmentData."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_with_data
        app_num = mock_patent_file_wrapper.application_number_text
        assert app_num is not None

        result = client.get_application_adjustment(application_number=app_num)
        assert result is mock_patent_file_wrapper.patent_term_adjustment_data

    def test_get_application_assignment(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_with_data: PatentDataResponse,
        mock_patent_file_wrapper: PatentFileWrapper,
    ) -> None:
        """Test get_application_assignment returns List[Assignment]."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_with_data
        app_num = mock_patent_file_wrapper.application_number_text
        assert app_num is not None

        result = client.get_application_assignment(application_number=app_num)
        assert result is mock_patent_file_wrapper.assignment_bag

    def test_get_application_attorney(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_with_data: PatentDataResponse,
        mock_patent_file_wrapper: PatentFileWrapper,
    ) -> None:
        """Test get_application_attorney returns RecordAttorney."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_with_data
        app_num = mock_patent_file_wrapper.application_number_text
        assert app_num is not None

        result = client.get_application_attorney(application_number=app_num)
        assert result is mock_patent_file_wrapper.record_attorney

    def test_get_application_continuity(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_with_data: PatentDataResponse,
        mock_patent_file_wrapper: PatentFileWrapper,
    ) -> None:
        """Test get_application_continuity returns ApplicationContinuityData."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_with_data
        app_num = mock_patent_file_wrapper.application_number_text
        assert app_num is not None

        result = client.get_application_continuity(application_number=app_num)
        assert isinstance(result, ApplicationContinuityData)
        assert result.parent_continuity_bag is mock_patent_file_wrapper.parent_continuity_bag
        assert result.child_continuity_bag is mock_patent_file_wrapper.child_continuity_bag

    def test_get_application_foreign_priority(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_with_data: PatentDataResponse,
        mock_patent_file_wrapper: PatentFileWrapper,
    ) -> None:
        """Test get_application_foreign_priority returns List[ForeignPriority]."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_with_data
        app_num = mock_patent_file_wrapper.application_number_text
        assert app_num is not None

        result = client.get_application_foreign_priority(application_number=app_num)
        assert result is mock_patent_file_wrapper.foreign_priority_bag

    def test_get_application_transactions(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_with_data: PatentDataResponse,
        mock_patent_file_wrapper: PatentFileWrapper,
    ) -> None:
        """Test get_application_transactions returns List[EventData]."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_with_data
        app_num = mock_patent_file_wrapper.application_number_text
        assert app_num is not None

        result = client.get_application_transactions(application_number=app_num)
        assert result is mock_patent_file_wrapper.event_data_bag


class TestPatentStatusCodesEndpoints:
    """Tests for interacting with patent status code endpoints."""

    def test_get_patent_status_codes(
        self, client_with_mocked_request: tuple[PatentDataClient, MagicMock]
    ) -> None:
        """Test get_patent_status_codes method."""
        client, mock_make_request = client_with_mocked_request
        mock_api_response = {
            "count": 1, "statusCodeBag": [{"applicationStatusCode": 100, "applicationStatusDescriptionText": "Active"}]
        }
        mock_make_request.return_value = mock_api_response # Returns dict for this endpoint

        result = client.get_patent_status_codes(params={"limit":1})

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/patent/status-codes",
            params={"limit":1},
        )
        assert isinstance(result, StatusCodeSearchResponse)
        assert result.count == 1
        assert result.status_code_bag[0].code == 100 # type: ignore

    def test_search_patent_status_codes_post(
        self, client_with_mocked_request: tuple[PatentDataClient, MagicMock]
    ) -> None:
        """Test search_patent_status_codes_post method."""
        client, mock_make_request = client_with_mocked_request
        mock_api_response = {
            "count": 1, "statusCodeBag": [{"applicationStatusCode": 150, "applicationStatusDescriptionText": "Pending"}]
        }
        mock_make_request.return_value = mock_api_response # Returns dict
        search_request = {"q": "Pending"}

        result = client.search_patent_status_codes_post(search_request=search_request)

        mock_make_request.assert_called_once_with(
            method="POST",
            endpoint="api/v1/patent/status-codes",
            json_data=search_request,
        )
        assert isinstance(result, StatusCodeSearchResponse)
        assert result.status_code_bag[0].description == "Pending" # type: ignore


class TestStatusCodeModels:
    """Tests for StatusCode, StatusCodeCollection, and StatusCodeSearchResponse models."""

    def test_status_code_model(self) -> None:
        """Test StatusCode model initialization and string representation."""
        status = StatusCode(code=100, description="Active Application")
        assert status.code == 100
        assert status.description == "Active Application"
        assert str(status) == "100: Active Application"

    def test_status_code_from_dict(self) -> None:
        """Test StatusCode.from_dict functionality."""
        data = {"applicationStatusCode": 150, "applicationStatusDescriptionText": "Abandoned"}
        status = StatusCode.from_dict(data)
        assert status.code == 150
        assert status.description == "Abandoned"

    def test_status_code_collection_model(self) -> None:
        """Test StatusCodeCollection model functionality."""
        s1 = StatusCode(code=100, description="A")
        s2 = StatusCode(code=200, description="B")
        collection = StatusCodeCollection(status_codes=[s1, s2])
        assert len(collection) == 2
        assert list(collection) == [s1, s2]
        assert repr(collection) == "StatusCodeCollection(2 status codes: 100, 200)"
        assert collection.find_by_code(200) is s2
        assert collection.find_by_code(999) is None
        assert len(collection.search_by_description("A")) == 1

    def test_status_code_collection_empty(self) -> None:
        """Test empty StatusCodeCollection."""
        collection = StatusCodeCollection(status_codes=[])
        assert len(collection) == 0
        assert repr(collection) == "StatusCodeCollection(empty)"

    def test_status_code_search_response_from_dict(self) -> None:
        """Test StatusCodeSearchResponse.from_dict functionality."""
        data = {
            "count": 1,
            "statusCodeBag": [{"applicationStatusCode": 100, "applicationStatusDescriptionText": "Test"}],
            "requestIdentifier": "req-123",
        }
        response_obj = StatusCodeSearchResponse.from_dict(data)
        assert response_obj.count == 1
        assert response_obj.request_identifier == "req-123"
        assert isinstance(response_obj.status_code_bag, StatusCodeCollection)
        assert len(response_obj.status_code_bag) == 1


class TestSpecificDataReturnTypes:
    """Tests for verifying specific model return types from client methods."""

    @pytest.fixture
    def client_for_return_type_tests(
        self,
        patent_data_client: PatentDataClient,
        mock_patent_data_response_with_data: PatentDataResponse
    ) -> PatentDataClient:
        """Provides a client with _make_request patched to return a full mock response."""
        patent_data_client._make_request = MagicMock(return_value=mock_patent_data_response_with_data) # type: ignore
        return patent_data_client

    def test_get_application_metadata_type(
        self, client_for_return_type_tests: PatentDataClient, mock_patent_file_wrapper: PatentFileWrapper
    ) -> None:
        """Ensure get_application_metadata returns ApplicationMetaData."""
        result = client_for_return_type_tests.get_application_metadata("123")
        assert result is mock_patent_file_wrapper.application_meta_data

    # Similar tests for other methods:
    # get_application_adjustment -> PatentTermAdjustmentData
    # get_application_assignment -> List[Assignment]
    # get_application_attorney -> RecordAttorney
    # get_application_continuity -> ApplicationContinuityData
    # get_application_foreign_priority -> List[ForeignPriority]
    # get_application_transactions -> List[EventData]
    # get_application_associated_documents -> AssociatedDocumentsData

    def test_get_application_associated_documents_type(
        self, client_for_return_type_tests: PatentDataClient, mock_patent_file_wrapper: PatentFileWrapper
    ) -> None:
        """Ensure get_application_associated_documents returns AssociatedDocumentsData."""
        result = client_for_return_type_tests.get_application_associated_documents("123")
        assert isinstance(result, AssociatedDocumentsData)
        assert result.pgpub_document_meta_data is mock_patent_file_wrapper.pgpub_document_meta_data


class TestReturnTypesEdgeCases:
    """Tests edge cases for methods with specific model return types."""

    @pytest.fixture
    def client_with_empty_response_for_return_types(
        self,
        patent_data_client: PatentDataClient,
        mock_patent_data_response_empty: PatentDataResponse
    ) -> PatentDataClient:
        """Client whose _make_request returns an empty PatentDataResponse."""
        patent_data_client._make_request = MagicMock(return_value=mock_patent_data_response_empty) # type: ignore
        return patent_data_client

    @pytest.fixture
    def client_with_minimal_wrapper_for_return_types(
        self,
        patent_data_client: PatentDataClient,
        mock_patent_file_wrapper_minimal: PatentFileWrapper
    ) -> PatentDataClient:
        """Client whose _make_request returns a response with a minimal wrapper (only app number)."""
        response = PatentDataResponse(count=1, patent_file_wrapper_data_bag=[mock_patent_file_wrapper_minimal])
        patent_data_client._make_request = MagicMock(return_value=response) # type: ignore
        return patent_data_client

    def test_specific_getters_return_none_on_empty_response(
        self, client_with_empty_response_for_return_types: PatentDataClient
    ) -> None:
        """Test specific getters return None or empty list when API response has no wrapper."""
        client = client_with_empty_response_for_return_types
        app_num = "any_app_num"
        assert client.get_application_metadata(app_num) is None
        assert client.get_application_adjustment(app_num) is None
        assert client.get_application_assignment(app_num) is None # Or [] depending on impl. Client returns wrapper.assignment_bag
        assert client.get_application_attorney(app_num) is None
        assert client.get_application_continuity(app_num) is None
        assert client.get_application_foreign_priority(app_num) is None # Or []
        assert client.get_application_transactions(app_num) is None # Or []
        assert client.get_application_associated_documents(app_num) is None

    def test_specific_getters_handle_missing_fields_in_wrapper(
        self, client_with_minimal_wrapper_for_return_types: PatentDataClient
    ) -> None:
        """Test specific getters return None or empty list when wrapper exists but fields are missing."""
        client = client_with_minimal_wrapper_for_return_types
        app_num = "12345678" # Matches minimal wrapper
        assert client.get_application_metadata(app_num) is None
        assert client.get_application_adjustment(app_num) is None
        assert client.get_application_assignment(app_num) == [] # Default empty list from Pydantic model
        assert client.get_application_attorney(app_num) is None
        
        continuity_result = client.get_application_continuity(app_num)
        assert isinstance(continuity_result, ApplicationContinuityData) # Object is created
        assert continuity_result.parent_continuity_bag == []
        assert continuity_result.child_continuity_bag == []

        assert client.get_application_foreign_priority(app_num) == []
        assert client.get_application_transactions(app_num) == []

        assoc_docs_result = client.get_application_associated_documents(app_num)
        assert isinstance(assoc_docs_result, AssociatedDocumentsData)
        assert assoc_docs_result.pgpub_document_meta_data is None


class TestGeneralEdgeCasesAndErrors:
    """Tests for general robustness, error handling, and unexpected API responses."""

    def test_get_patent_application_details_app_num_mismatch_in_bag(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_file_wrapper: PatentFileWrapper, # This wrapper has app_num "12345678"
    ) -> None:
        """Test get_patent_application_details when requested app_num differs from the one in the returned bag."""
        client, mock_make_request = client_with_mocked_request
        requested_app_num = "DIFFERENT_APP_NUM_999"
        
        # API returns a wrapper for "12345678"
        response_with_original_wrapper = PatentDataResponse(count=1, patent_file_wrapper_data_bag=[mock_patent_file_wrapper])
        mock_make_request.return_value = response_with_original_wrapper

        # Client._get_wrapper_from_response logs a warning but returns the first wrapper.
        with patch("builtins.print") as mock_print: # To check for warning
            result = client.get_patent_application_details(application_number=requested_app_num)
        
        assert result is mock_patent_file_wrapper # Returns the wrapper it found
        assert result is not None
        assert result.application_number_text == "12345678" # Not the requested one
        mock_print.assert_any_call(
            "Warning: Fetched wrapper application number '12345678' "
            f"does not match requested '{requested_app_num}'."
        )

    def test_get_patent_application_details_unexpected_response_type(
        self, client_with_mocked_request: tuple[PatentDataClient, MagicMock]
    ) -> None:
        """Test get_patent_application_details if _make_request returns an unexpected type (not PatentDataResponse)."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = ["not", "a", "PatentDataResponse"]

        with pytest.raises(AssertionError): # Client asserts isinstance(response_data, PatentDataResponse)
            client.get_patent_application_details(application_number="123")

    def test_download_document_file_non_requests_response(
        self, client_with_mocked_request: tuple[PatentDataClient, MagicMock]
    ) -> None:
        """Test download_document_file if _make_request returns non-requests.Response for streaming."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = {"not_a_response_object": True}

        with pytest.raises(TypeError, match="Expected a requests.Response object"):
            client.download_document_file("app", "doc", "/tmp")
            
    def test_api_error_handling(
        self, client_with_mocked_request: tuple[PatentDataClient, MagicMock]
    ) -> None:
        """Test that API errors from _make_request are propagated."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.side_effect = USPTOApiBadRequestError("Mocked API Bad Request")

        with pytest.raises(USPTOApiBadRequestError, match="Mocked API Bad Request"):
            client.get_patent_applications(params={"q": "test"})

    def test_search_patent_applications_post_assertion_error(
        self, client_with_mocked_request: tuple[PatentDataClient, MagicMock]
    ) -> None:
        """Test assertion in search_patent_applications_post if response is not PatentDataResponse."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = {"not_a_patent_data_response": True}

        with pytest.raises(AssertionError):
            client.search_patent_applications_post(search_request={"q": "test"})


class TestInternalHelpersEdgeCases:
    """Tests for edge cases in internal helper methods like _get_wrapper_from_response."""

    def test_get_wrapper_from_response_empty_bag(
        self, patent_data_client: PatentDataClient, mock_patent_data_response_empty: PatentDataResponse
    ) -> None:
        """Test _get_wrapper_from_response returns None if bag is empty."""
        result = patent_data_client._get_wrapper_from_response(mock_patent_data_response_empty)
        assert result is None

    def test_get_wrapper_from_response_item_is_dict(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test _get_wrapper_from_response handles dict item in bag by calling from_dict."""
        app_num = "dict_app_num"
        mock_dict_item = {"applicationNumberText": app_num, "applicationMetaData": {"inventionTitle": "From Dict"}}
        response_with_dict = PatentDataResponse(count=1, patent_file_wrapper_data_bag=[mock_dict_item]) # type: ignore

        with patch("pyUSPTO.models.patent_data.PatentFileWrapper.from_dict") as mock_from_dict:
            mock_pfw_instance = PatentFileWrapper(application_number_text=app_num)
            mock_from_dict.return_value = mock_pfw_instance
            
            result = patent_data_client._get_wrapper_from_response(response_with_dict)
        
        mock_from_dict.assert_called_once_with(mock_dict_item)
        assert result is mock_pfw_instance

    def test_get_wrapper_from_response_item_is_invalid_type(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test _get_wrapper_from_response returns None if bag item is not a PFW or dict."""
        response_with_invalid_item = PatentDataResponse(count=1, patent_file_wrapper_data_bag=["just_a_string"]) # type: ignore
        
        result = patent_data_client._get_wrapper_from_response(response_with_invalid_item)
        assert result is None


class TestDocumentModels:
    """Tests for Document, DocumentBag, and DocumentDownloadFormat models."""

    def test_document_model(self) -> None:
        """Test Document model initialization and string representation."""
        dt = datetime(2023, 1, 1, 10, 30, 0, tzinfo=timezone.utc)
        doc = Document(
            document_identifier="DOC123",
            official_date=dt,
            document_code="IDS",
            document_code_description_text="Info Disclosure",
            direction_category=DirectionCategory.INCOMING,
        )
        assert doc.document_identifier == "DOC123"
        assert "2023-01-01" in str(doc) # Model's __str__ formats date
        assert "IDS" in str(doc)

    def test_document_download_format_model(self) -> None:
        """Test DocumentDownloadFormat model."""
        fmt = DocumentDownloadFormat(
            mime_type_identifier="PDF",
            download_url="http://example.com/doc.pdf",
            page_total_quantity=10,
        )
        assert fmt.mime_type_identifier == "PDF"
        assert "PDF format" in str(fmt)
        assert "10 pages" in str(fmt)

    def test_document_bag_model(self) -> None:
        """Test DocumentBag model iteration and length."""
        doc1 = Document(document_identifier="D1", official_date=datetime.now(timezone.utc), document_code="C1")
        doc2 = Document(document_identifier="D2", official_date=datetime.now(timezone.utc), document_code="C2")
        bag = DocumentBag(documents=[doc1, doc2])
        assert len(bag) == 2
        assert list(bag) == [doc1, doc2]
        docs_from_iter = [d for d in bag]
        assert docs_from_iter == [doc1, doc2]

