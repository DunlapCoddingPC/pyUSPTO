"""
Consolidated tests for the pyUSPTO.clients.patent_data.PatentDataClient.

This module combines tests for initialization, core functionality, document handling,
metadata retrieval, status codes, return type validation, and edge cases for the
PatentDataClient.
"""

import csv
import io
import os
import re
from datetime import date, datetime, timezone
from typing import Any, Dict, Iterator, List, Optional
from unittest import mock
from unittest.mock import MagicMock, Mock, mock_open, patch
from urllib.parse import unquote, urlparse

import pytest
import requests

from pyUSPTO.clients.base import BaseUSPTOClient
from pyUSPTO.clients.patent_data import PatentDataClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.exceptions import USPTOApiBadRequestError, USPTOApiError
from pyUSPTO.models.patent_data import (
    ApplicationContinuityData,
    ApplicationMetaData,
    Assignment,
    Attorney,
    ChildContinuity,
    DirectionCategory,
    Document,
    DocumentBag,
    DocumentFormat,
    EventData,
    ForeignPriority,
    Inventor,
    ParentContinuity,
    PatentDataResponse,
    PatentFileWrapper,
    PatentTermAdjustmentData,
    PrintedMetaData,
    PrintedPublication,
    RecordAttorney,
    StatusCode,
    StatusCodeCollection,
    StatusCodeSearchResponse,
    serialize_date,
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
    first_inventor = Inventor(inventor_name_text="John Inventor")
    return ApplicationMetaData(
        invention_title="Test Invention",
        patent_number="10000000",
        filing_date=date(2020, 1, 1),
        grant_date=date(2022, 1, 1),
        application_type_label_name="Utility",
        publication_category_bag=["A1", "B2"],
        application_status_description_text="Patented Case",
        application_status_date=date(2022, 1, 1),
        first_applicant_name="Test Applicant",
        first_inventor_name="John Inventor",
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
            Attorney(first_name="James", last_name="Legal", registration_number="12345")
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
    dt = date(2022, 1, 1)
    return EventData(
        event_code="COMP",
        event_description_text="Application ready for examination",
        event_date=dt,
    )


@pytest.fixture
def mock_pgpub_document_meta_data() -> PrintedMetaData:
    """Provides a mock pgpub DocumentMetaData instance."""
    dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    return PrintedMetaData(
        zip_file_name="pgpub.zip",
        product_identifier="PGPUB",
        file_create_date_time=dt,
    )


@pytest.fixture
def mock_grant_document_meta_data() -> PrintedMetaData:
    """Provides a mock grant DocumentMetaData instance."""
    dt = datetime(2023, 2, 1, 12, 0, 0, tzinfo=timezone.utc)
    return PrintedMetaData(
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
    mock_pgpub_document_meta_data: PrintedMetaData,
    mock_grant_document_meta_data: PrintedMetaData,
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
        client = PatentDataClient(api_key=api_key_fixture, config=config)
        assert client.api_key == api_key_fixture
        assert client.base_url == "https://config.api.test.com"

        custom_url = "https://custom.url.com"
        client_custom_url = PatentDataClient(
            api_key=api_key_fixture, base_url=custom_url, config=config
        )
        assert client_custom_url.base_url == custom_url


class TestPatentApplicationSearch:
    """Tests for patent application search functionalities using the new search_applications method."""

    def test_search_applications_get_direct_query(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_with_data: PatentDataResponse,
    ) -> None:
        """Test search_applications method (GET search path) with direct query."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_with_data

        params_to_send: Dict[str, Any] = {"query": "Test", "limit": 10, "offset": 0}
        expected_api_params: Dict[str, Any] = {"q": "Test", "limit": 10, "offset": 0}

        result = client.search_applications(**params_to_send)

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/patent/applications/search",
            params=expected_api_params,
            response_class=PatentDataResponse,
        )
        assert result is mock_patent_data_response_with_data

    def test_search_applications_get_with_combined_q_convenience_params(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_empty: PatentDataResponse,
    ) -> None:
        """Test search_applications GET path with a combination of _q convenience params."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_empty

        client.search_applications(
            inventor_name_q="Doe", filing_date_from_q="2021-01-01", limit=5
        )

        expected_api_params = {
            "q": "applicationMetaData.inventorBag.inventorNameText:Doe AND applicationMetaData.filingDate:>=2021-01-01",
            "limit": 5,
            "offset": 0,
        }
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/patent/applications/search",
            params=expected_api_params,
            response_class=PatentDataResponse,
        )

    def test_search_applications_post(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_with_data: PatentDataResponse,
    ) -> None:
        """Test search_applications method (POST search path)."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_with_data
        search_body = {
            "q": "Test",
            "filters": [
                {"name": "inventionSubjectMatterCategory", "value": ["MECHANICAL"]}
            ],
            "pagination": {"offset": 0, "limit": 100},
        }

        result = client.search_applications(post_body=search_body)

        mock_make_request.assert_called_once_with(
            method="POST",
            endpoint="api/v1/patent/applications/search",
            json_data=search_body,
            params=None,
            response_class=PatentDataResponse,
        )
        assert result is mock_patent_data_response_with_data

    @pytest.mark.parametrize(
        "search_q_params, expected_q_part",
        [
            ({"application_number_q": "app123"}, "applicationNumberText:app123"),
            ({"patent_number_q": "PN123"}, "applicationMetaData.patentNumber:PN123"),
            (
                {"inventor_name_q": "Doe J"},
                "applicationMetaData.inventorBag.inventorNameText:Doe J",
            ),
            (
                {"applicant_name_q": "Corp Inc"},
                "applicationMetaData.firstApplicantName:Corp Inc",
            ),
            (
                {"assignee_name_q": "Assignee Ltd"},
                "assignmentBag.assigneeBag.assigneeNameText:Assignee Ltd",
            ),
            (
                {"classification_q": "H04L"},
                "applicationMetaData.cpcClassificationBag:H04L",
            ),
            (
                {"earliestPublicationNumber_q": "*12345678*"},
                "applicationMetaData.earliestPublicationNumber:*12345678*",
            ),
            (
                {"pctPublicationNumber_q": "PCTUS202501234567"},
                "applicationMetaData.pctPublicationNumber:PCTUS202501234567",
            ),
            (
                {"filing_date_from_q": "2021-01-01"},
                "applicationMetaData.filingDate:>=2021-01-01",
            ),
            (
                {"filing_date_to_q": "2021-12-31"},
                "applicationMetaData.filingDate:<=2021-12-31",
            ),
            (
                {"filing_date_from_q": "2021-01-01", "filing_date_to_q": "2021-12-31"},
                "applicationMetaData.filingDate:[2021-01-01 TO 2021-12-31]",
            ),
            (
                {"grant_date_from_q": "2022-01-01"},
                "applicationMetaData.grantDate:>=2022-01-01",
            ),
            (
                {"grant_date_to_q": "2022-12-31"},
                "applicationMetaData.grantDate:<=2022-12-31",
            ),
            (
                {"grant_date_from_q": "2022-01-01", "grant_date_to_q": "2022-12-31"},
                "applicationMetaData.grantDate:[2022-01-01 TO 2022-12-31]",
            ),
        ],
    )
    def test_search_applications_get_various_q_convenience_filters(
        self,
        search_q_params: Dict[str, Any],
        expected_q_part: str,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_empty: PatentDataResponse,
    ) -> None:
        """Test search_applications GET path with various individual _q convenience filters."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_empty

        limit = 25
        offset = 0

        effective_limit = search_q_params.pop("limit", limit)
        effective_offset = search_q_params.pop("offset", offset)

        client.search_applications(
            **search_q_params, limit=effective_limit, offset=effective_offset
        )

        expected_call_params = {
            "q": expected_q_part,
            "limit": effective_limit,
            "offset": effective_offset,
        }

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/patent/applications/search",
            params=expected_call_params,
            response_class=PatentDataResponse,
        )

    def test_search_applications_get_multiple_q_convenience_filters(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_empty: PatentDataResponse,
    ) -> None:
        """Test search_applications GET path with multiple _q convenience filters combined."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_empty

        client.search_applications(
            inventor_name_q="John Smith",
            filing_date_from_q="2020-01-01",
            filing_date_to_q="2022-01-01",
            classification_q="G06F",
            limit=20,
            offset=10,
        )

        expected_q = (
            "applicationMetaData.inventorBag.inventorNameText:John Smith AND "
            "applicationMetaData.cpcClassificationBag:G06F AND "
            "applicationMetaData.filingDate:[2020-01-01 TO 2022-01-01]"
        )
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/patent/applications/search",
            params={"q": expected_q, "limit": 20, "offset": 10},
            response_class=PatentDataResponse,
        )

    def test_search_applications_get_empty_query_params_uses_defaults(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_empty: PatentDataResponse,
    ) -> None:
        """Test search_applications GET with no specific query parameters, only default limit/offset."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_empty

        client.search_applications()

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/patent/applications/search",
            params={"offset": 0, "limit": 25},
            response_class=PatentDataResponse,
        )

    def test_search_applications_get_explicitly_null_limit_offset_direct_q(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_empty: PatentDataResponse,
    ) -> None:
        """Test search_applications GET with limit and offset explicitly None, using direct 'query'."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_empty

        client.search_applications(query="test query", limit=None, offset=None)

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/patent/applications/search",
            params={"q": "test query"},
            response_class=PatentDataResponse,
        )

    @pytest.mark.parametrize(
        "api_param_name, api_param_value, expected_param_key",
        [
            ("sort", "applicationMetaData.filingDate asc", "sort"),
            ("facets", "applicationMetaData.applicationTypeCode", "facets"),
            ("fields", "applicationNumberText,inventionTitle", "fields"),
            ("filters", "applicationMetaData.applicationTypeCode UTL", "filters"),
            (
                "range_filters",
                "applicationMetaData.filingDate 2020-01-01:2020-12-31",
                "rangeFilters",
            ),
        ],
    )
    def test_search_applications_get_with_openapi_params(  # New test
        self,
        api_param_name: str,
        api_param_value: str,
        expected_param_key: str,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_empty: PatentDataResponse,
    ) -> None:
        """Test search_applications GET path with various direct OpenAPI parameters."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_empty

        method_kwargs: Dict[str, Any] = {
            api_param_name: api_param_value,
            "limit": 5,
            "offset": 0,
        }
        client.search_applications(**method_kwargs)

        expected_api_params = {
            expected_param_key: api_param_value,
            "limit": 5,
            "offset": 0,
        }
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/patent/applications/search",
            params=expected_api_params,
            response_class=PatentDataResponse,
        )
        # mock_make_request.reset_mock() # Removed as it caused issues with parametrize in some pytest versions

    def test_search_applications_get_with_additional_query_params(  # New test
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_empty: PatentDataResponse,
    ) -> None:
        """Test search_applications GET path with additional_query_params."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_empty

        client.search_applications(
            query="main_query",
            sort="field asc",
            additional_query_params={"custom_param": "custom_value", "another": "one"},
            limit=10,
        )

        expected_api_params = {
            "q": "main_query",
            "sort": "field asc",
            "custom_param": "custom_value",
            "another": "one",
            "limit": 10,
            "offset": 0,
        }
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/patent/applications/search",
            params=expected_api_params,
            response_class=PatentDataResponse,
        )


class TestPatentApplicationDetails:
    """Tests for retrieving details of a single patent application."""

    def test_get_application_by_number_success(
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

        result = client.get_application_by_number(application_number=app_num)

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint=f"api/v1/patent/applications/{app_num}",
            response_class=PatentDataResponse,
        )
        assert result is mock_patent_file_wrapper
        assert result is not None
        assert result.application_number_text == app_num
        assert result.application_meta_data is not None
        assert result.application_meta_data.invention_title == "Test Invention"

    def test_get_application_by_number_empty_bag_returns_none(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_empty: PatentDataResponse,
    ) -> None:
        """Test get_application_by_number returns None if patentFileWrapperDataBag is empty."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_empty
        app_num_to_request = "nonexistent123"

        result = client.get_application_by_number(application_number=app_num_to_request)
        assert result is None


class TestPatentApplicationPagination:
    """Tests for patent application result pagination."""

    def test_paginate_applications(self, patent_data_client: PatentDataClient) -> None:
        """Test paginate_applications method correctly calls paginate_results."""
        with patch.object(
            patent_data_client, "paginate_results", autospec=True
        ) as mock_paginate_results:
            patent1 = PatentFileWrapper(application_number_text="123")
            patent2 = PatentFileWrapper(application_number_text="456")
            mock_paginate_results.return_value = iter([patent1, patent2])

            results = list(
                patent_data_client.paginate_applications(query="Test", limit=20)
            )

            mock_paginate_results.assert_called_once_with(
                method_name="search_applications",
                response_container_attr="patent_file_wrapper_data_bag",
                query="Test",
                limit=20,
            )
            assert len(results) == 2
            assert results[0] is patent1
            assert results[1] is patent2

    def test_paginate_applications_raises_value_error_for_post_body(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test paginate_applications raises ValueError if post_body is provided."""
        with pytest.raises(
            ValueError,
            match="paginate_applications uses GET requests and does not support 'post_body'",
        ):
            list(patent_data_client.paginate_applications(post_body={"q": "test"}))


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
                    "downloadOptionBag": [
                        {"mimeTypeIdentifier": "PDF", "downloadURI": "/doc1.pdf"}
                    ],
                }
            ]
        }
        mock_make_request.return_value = mock_response_dict
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
        assert isinstance(result, PrintedPublication)
        assert (
            result.pgpub_document_meta_data
            is mock_patent_file_wrapper.pgpub_document_meta_data
        )
        assert (
            result.grant_document_meta_data
            is mock_patent_file_wrapper.grant_document_meta_data
        )


class TestPatentDocumentDownload:
    """Tests for downloading individual patent documents."""

    @pytest.fixture
    def sample_document_format(self) -> DocumentFormat:
        """Sample DocumentFormat object for testing."""
        return DocumentFormat(
            mime_type_identifier="PDF",
            download_url="https://api.uspto.gov/api/v1/patent/application/documents/16123123/LDXBTPQ7XBLUEX3.pdf",
            page_total_quantity=2,
        )

    @pytest.fixture
    def client_with_mocked_download(self) -> tuple[PatentDataClient, MagicMock]:
        """Client with mocked _download_file method."""
        client = PatentDataClient()
        mock_download_file = MagicMock()
        client._download_file = mock_download_file
        return client, mock_download_file

    @patch("pathlib.Path.is_dir")
    @patch("pathlib.Path.exists")
    def test_download_document_basic(
        self,
        mock_exists: MagicMock,
        mock_is_dir: MagicMock,
        client_with_mocked_download: tuple[PatentDataClient, MagicMock],
        sample_document_format: DocumentFormat,
    ) -> None:
        """Test basic document download with DocumentFormat object."""
        client, mock_download_file = client_with_mocked_download
        mock_exists.return_value = False
        mock_is_dir.return_value = True

        expected_path = "/tmp/downloads/LDXBTPQ7XBLUEX3.pdf"
        mock_download_file.return_value = (
            expected_path  # Ensure the mock returns the expected path
        )

        result_path = client.download_document(
            document_format=sample_document_format, destination_path="/tmp/downloads/"
        )

        mock_download_file.assert_called_once_with(
            url=sample_document_format.download_url, file_path=expected_path
        )
        assert result_path == expected_path

    @patch("pathlib.Path.is_dir")
    @patch("pathlib.Path.exists")
    def test_download_document_custom_filename(
        self,
        mock_exists: MagicMock,
        mock_is_dir: MagicMock,
        client_with_mocked_download: tuple[PatentDataClient, MagicMock],
        sample_document_format: DocumentFormat,
    ) -> None:
        """Test document download with custom filename."""
        client, mock_download_file = client_with_mocked_download
        mock_exists.return_value = False
        mock_is_dir.return_value = True

        custom_filename = "my_patent_doc.pdf"
        expected_path = "/tmp/downloads/my_patent_doc.pdf"
        mock_download_file.return_value = expected_path

        result_path = client.download_document(
            document_format=sample_document_format,
            file_name=custom_filename,
            destination_path="/tmp/downloads",
        )

        mock_download_file.assert_called_once_with(
            url=sample_document_format.download_url, file_path=expected_path
        )
        assert result_path == expected_path

    @patch("pathlib.Path.is_dir")
    @patch("pathlib.Path.exists")
    def test_download_document_fallback_filename(
        self,
        mock_exists: MagicMock,
        mock_is_dir: MagicMock,
        client_with_mocked_download: tuple[PatentDataClient, MagicMock],
    ) -> None:
        """Test document download with mime type fallback for filename."""
        client, mock_download_file = client_with_mocked_download
        mock_exists.return_value = False
        mock_is_dir.return_value = True

        document_format = DocumentFormat(
            mime_type_identifier="PDF",
            download_url="https://api.uspto.gov/documents/someidentifier",  # No extension in URL
            page_total_quantity=2,
        )

        expected_path = "/tmp/downloads/document.pdf"  # Falls back to mime type
        mock_download_file.return_value = expected_path
        result_path = client.download_document(
            document_format=document_format, destination_path="/tmp/downloads"
        )

        mock_download_file.assert_called_once_with(
            url=document_format.download_url, file_path=expected_path
        )

        assert result_path == expected_path

    @patch("pathlib.Path.is_dir")
    @patch("pathlib.Path.exists")
    def test_download_document_file_exists_no_overwrite(
        self,
        mock_exists: MagicMock,
        mock_is_dir: MagicMock,
        client_with_mocked_download: tuple[PatentDataClient, MagicMock],
        sample_document_format: DocumentFormat,
    ) -> None:
        """Test document download raises FileExistsError when file exists and overwrite=False."""
        client, mock_download_file = client_with_mocked_download
        mock_exists.return_value = True  # Simulate file exists
        mock_is_dir.return_value = True

        with pytest.raises(
            FileExistsError, match="File already exists.*Use overwrite=True"
        ):
            client.download_document(
                document_format=sample_document_format,
                destination_path="/tmp/downloads/",
            )

        mock_download_file.assert_not_called()

    @patch("pathlib.Path.is_dir")
    @patch("pathlib.Path.exists")
    def test_download_document_overwrite_existing(
        self,
        mock_exists: MagicMock,
        mock_is_dir: MagicMock,
        client_with_mocked_download: tuple[PatentDataClient, MagicMock],
        sample_document_format: DocumentFormat,
    ) -> None:
        """Test document download overwrites existing file when overwrite=True."""
        client, mock_download_file = client_with_mocked_download
        mock_exists.return_value = True  # Simulate file exists, but overwrite is True
        mock_is_dir.return_value = True

        expected_path = "/tmp/downloads/LDXBTPQ7XBLUEX3.pdf"
        mock_download_file.return_value = expected_path

        result_path = client.download_document(
            document_format=sample_document_format,
            destination_path="/tmp/downloads",
            overwrite=True,
        )

        expected_path = "/tmp/downloads/LDXBTPQ7XBLUEX3.pdf"
        mock_download_file.assert_called_once_with(
            url=sample_document_format.download_url, file_path=expected_path
        )
        assert result_path == expected_path

    def test_download_document_missing_url(
        self,
        client_with_mocked_download: tuple[PatentDataClient, MagicMock],
    ) -> None:
        """Test download_document raises ValueError when DocumentFormat has no download URL."""
        client, mock_download_file = client_with_mocked_download

        document_format = DocumentFormat(
            mime_type_identifier="PDF",
            download_url=None,  # Missing URL
            page_total_quantity=2,
        )

        with pytest.raises(ValueError, match="DocumentFormat must have a download_url"):
            client.download_document(document_format=document_format)

        mock_download_file.assert_not_called()

    @patch("pathlib.Path.exists")
    def test_download_document_no_file_path(
        self,
        mock_exists: MagicMock,
        client_with_mocked_download: tuple[PatentDataClient, MagicMock],
        sample_document_format: DocumentFormat,
    ) -> None:
        """Test document download with no file_path provided (uses current directory)."""
        client, mock_download_file = client_with_mocked_download
        mock_exists.return_value = False

        expected_path = "LDXBTPQ7XBLUEX3.pdf"  # Just the filename, no directory
        mock_download_file.return_value = expected_path

        # Don't provide file_path - this hits the else branch
        result_path = client.download_document(document_format=sample_document_format)

        mock_download_file.assert_called_once_with(
            url=sample_document_format.download_url, file_path=expected_path
        )
        assert result_path == expected_path


class TestDownloadFile:
    """Tests for the _download_file method in BaseUSPTOClient."""

    @patch("builtins.open", new_callable=mock_open)
    @patch.object(BaseUSPTOClient, "_make_request")
    def test_download_file_success(
        self,
        mock_make_request: MagicMock,
        mock_file_open: MagicMock,
        patent_data_client: PatentDataClient,
    ) -> None:
        """Test successful file download."""
        # Setup mock response
        mock_response = MagicMock(spec=requests.Response)
        mock_response.iter_content.return_value = [b"chunk1", b"chunk2", b""]
        mock_make_request.return_value = mock_response

        url = "https://example.com/file.pdf"
        file_path = "/tmp/test_file.pdf"

        result = patent_data_client._download_file(url, file_path)

        # Verify _make_request called correctly
        mock_make_request.assert_called_once_with(
            method="GET", endpoint="", stream=True, custom_url=url
        )

        # Verify file operations
        mock_file_open.assert_called_once_with(file=file_path, mode="wb")
        mock_file_open().write.assert_has_calls(
            [mock.call(b"chunk1"), mock.call(b"chunk2")]
        )

        assert result == file_path

    @patch.object(BaseUSPTOClient, "_make_request")
    def test_download_file_wrong_response_type(
        self,
        mock_make_request: MagicMock,
        patent_data_client: PatentDataClient,
    ) -> None:
        """Test _download_file raises TypeError when _make_request returns wrong type."""
        # Return a dict instead of Response
        mock_make_request.return_value = {"not": "a response"}

        url = "https://example.com/file.pdf"
        file_path = "/tmp/test_file.pdf"

        with pytest.raises(
            TypeError, match="Expected requests.Response for streaming download"
        ):
            patent_data_client._download_file(url, file_path)

    @patch("builtins.open", new_callable=mock_open)
    @patch.object(BaseUSPTOClient, "_make_request")
    def test_download_file_filters_empty_chunks(
        self,
        mock_make_request: MagicMock,
        mock_file_open: MagicMock,
        patent_data_client: PatentDataClient,
    ) -> None:
        """Test that empty chunks are filtered out."""
        mock_response = MagicMock(spec=requests.Response)
        mock_response.iter_content.return_value = [b"data", b"", None, b"more"]
        mock_make_request.return_value = mock_response

        result = patent_data_client._download_file("https://test.com", "/tmp/file")

        # Should only write non-empty chunks
        mock_file_open().write.assert_has_calls(
            [mock.call(b"data"), mock.call(b"more")]
        )
        assert mock_file_open().write.call_count == 2


class TestGetIFW:
    """Tests for the get_IFW convenience method."""

    def test_get_ifw_by_application_number(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_file_wrapper: PatentFileWrapper,
    ) -> None:
        """Test get_IFW with application_number calls get_application_by_number."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = PatentDataResponse(
            count=1, patent_file_wrapper_data_bag=[mock_patent_file_wrapper]
        )

        app_num = "12345678"
        result = client.get_IFW_metadata(application_number=app_num)

        # Should call get_application_by_number
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint=f"api/v1/patent/applications/{app_num}",
            response_class=PatentDataResponse,
        )
        assert result is mock_patent_file_wrapper

    def test_get_ifw_by_patent_number(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_file_wrapper: PatentFileWrapper,
    ) -> None:
        """Test get_IFW with patent_number calls search_applications."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = PatentDataResponse(
            count=1, patent_file_wrapper_data_bag=[mock_patent_file_wrapper]
        )

        patent_num = "10000000"
        result = client.get_IFW_metadata(patent_number=patent_num)

        # Should call search_applications with patent_number_q
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/patent/applications/search",
            params={
                "q": f"applicationMetaData.patentNumber:{patent_num}",
                "limit": 1,
                "offset": 0,
            },
            response_class=PatentDataResponse,
        )
        assert result is mock_patent_file_wrapper

    def test_get_ifw_by_publication_number(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_file_wrapper: PatentFileWrapper,
    ) -> None:
        """Test get_IFW with publication_number calls search_applications."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = PatentDataResponse(
            count=1, patent_file_wrapper_data_bag=[mock_patent_file_wrapper]
        )

        pub_num = "US20240123456A1"
        result = client.get_IFW_metadata(publication_number=pub_num)

        # Should call search_applications with earliestPublicationNumber_q
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/patent/applications/search",
            params={
                "q": f"applicationMetaData.earliestPublicationNumber:{pub_num}",
                "limit": 1,
                "offset": 0,
            },
            response_class=PatentDataResponse,
        )
        assert result is mock_patent_file_wrapper

    def test_get_ifw_by_pct_app_number(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_file_wrapper: PatentFileWrapper,
    ) -> None:
        """Test get_IFW with PCT_app_number calls get_application_by_number."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = PatentDataResponse(
            count=1, patent_file_wrapper_data_bag=[mock_patent_file_wrapper]
        )

        pct_app = "PCT/US2024/012345"
        result = client.get_IFW_metadata(PCT_app_number=pct_app)

        # Should call get_application_by_number
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint=f"api/v1/patent/applications/{pct_app}",
            response_class=PatentDataResponse,
        )
        assert result is mock_patent_file_wrapper

    def test_get_ifw_by_pct_pub_number(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_file_wrapper: PatentFileWrapper,
    ) -> None:
        """Test get_IFW with PCT_pub_number calls search_applications."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = PatentDataResponse(
            count=1, patent_file_wrapper_data_bag=[mock_patent_file_wrapper]
        )

        pct_pub = "WO2024012345A1"
        result = client.get_IFW_metadata(PCT_pub_number=pct_pub)

        # Should call search_applications with pctPublicationNumber_q
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/patent/applications/search",
            params={
                "q": f"applicationMetaData.pctPublicationNumber:{pct_pub}",
                "limit": 1,
                "offset": 0,
            },
            response_class=PatentDataResponse,
        )
        assert result is mock_patent_file_wrapper

    def test_get_ifw_no_parameters_returns_none(
        self, patent_data_client: PatentDataClient
    ) -> None:
        """Test get_IFW with no parameters returns None."""
        result = patent_data_client.get_IFW_metadata()
        assert result is None

    def test_get_ifw_empty_search_results_returns_none(
        self, client_with_mocked_request: tuple[PatentDataClient, MagicMock]
    ) -> None:
        """Test get_IFW returns None when search returns empty results."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = PatentDataResponse(
            count=0, patent_file_wrapper_data_bag=[]
        )

        result = client.get_IFW_metadata(patent_number="nonexistent")
        assert result is None

    def test_get_ifw_prioritizes_first_parameter(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_file_wrapper: PatentFileWrapper,
    ) -> None:
        """Test get_IFW uses application_number when multiple parameters provided."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = PatentDataResponse(
            count=1, patent_file_wrapper_data_bag=[mock_patent_file_wrapper]
        )

        app_num = "12345678"
        # Provide multiple parameters - should use application_number
        result = client.get_IFW_metadata(
            application_number=app_num,
            patent_number="10000000",
            publication_number="US20240123456A1",
        )

        # Should only call get_application_by_number, not search
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint=f"api/v1/patent/applications/{app_num}",
            response_class=PatentDataResponse,
        )
        assert result is mock_patent_file_wrapper


class TestDownloadArchive:
    """Tests for downloading archive files."""

    @pytest.fixture
    def sample_printed_metadata(self) -> PrintedMetaData:
        """Sample PrintedMetaData object for testing."""
        return PrintedMetaData(
            xml_file_name="patent_12345.xml",
            product_identifier="PTGRXML",
            file_location_uri="https://bulkdata.uspto.gov/data/patent/grant/redbook/fulltext/2024/patent_12345.xml",
        )

    @pytest.fixture
    def client_with_mocked_download(self) -> tuple[PatentDataClient, MagicMock]:
        """Client with mocked _download_file method."""
        client = PatentDataClient()
        mock_download_file = MagicMock()
        client._download_file = mock_download_file
        return client, mock_download_file

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.mkdir")
    def test_download_archive_basic(
        self,
        mock_mkdir: MagicMock,
        mock_exists: MagicMock,
        client_with_mocked_download: tuple[PatentDataClient, MagicMock],
        sample_printed_metadata: PrintedMetaData,
    ) -> None:
        """Test basic archive download."""
        client, mock_download_file = client_with_mocked_download
        mock_exists.return_value = False

        expected_path = "/printedmeta/patent_12345.xml"
        mock_download_file.return_value = expected_path

        result = client.download_archive(
            printed_metadata=sample_printed_metadata, destination_path="/printedmeta"
        )

        mock_download_file.assert_called_once_with(
            url=sample_printed_metadata.file_location_uri, file_path=expected_path
        )
        assert result == expected_path

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.mkdir")
    def test_download_archive_custom_filename(
        self,
        mock_mkdir: MagicMock,
        mock_exists: MagicMock,
        client_with_mocked_download: tuple[PatentDataClient, MagicMock],
        sample_printed_metadata: PrintedMetaData,
    ) -> None:
        """Test archive download with custom filename."""
        client, mock_download_file = client_with_mocked_download
        mock_exists.return_value = False

        custom_name = "my_patent.xml"
        expected_path = "/printedmeta/my_patent.xml"
        mock_download_file.return_value = expected_path

        result = client.download_archive(
            printed_metadata=sample_printed_metadata,
            file_name=custom_name,
            destination_path="/printedmeta",
        )

        mock_download_file.assert_called_once_with(
            url=sample_printed_metadata.file_location_uri, file_path=expected_path
        )
        assert result == expected_path

    @patch("pathlib.Path.exists")
    def test_download_archive_no_destination_path(
        self,
        mock_exists: MagicMock,
        client_with_mocked_download: tuple[PatentDataClient, MagicMock],
        sample_printed_metadata: PrintedMetaData,
    ) -> None:
        """Test archive download with no destination path (current directory)."""
        client, mock_download_file = client_with_mocked_download
        mock_exists.return_value = False

        expected_path = "patent_12345.xml"
        mock_download_file.return_value = expected_path

        result = client.download_archive(printed_metadata=sample_printed_metadata)

        mock_download_file.assert_called_once_with(
            url=sample_printed_metadata.file_location_uri, file_path=expected_path
        )
        assert result == expected_path

    def test_download_archive_missing_url(
        self, client_with_mocked_download: tuple[PatentDataClient, MagicMock]
    ) -> None:
        """Test download_archive raises ValueError when no download URL."""
        client, mock_download_file = client_with_mocked_download

        metadata_no_url = PrintedMetaData(
            xml_file_name="test.xml", file_location_uri=None
        )

        with pytest.raises(
            ValueError, match="ArchiveMetaData must have a file_location_uri"
        ):
            client.download_archive(printed_metadata=metadata_no_url)

        mock_download_file.assert_not_called()

    @patch("pathlib.Path.exists")
    def test_download_archive_file_exists_no_overwrite(
        self,
        mock_exists: MagicMock,
        client_with_mocked_download: tuple[PatentDataClient, MagicMock],
        sample_printed_metadata: PrintedMetaData,
    ) -> None:
        """Test download_archive raises FileExistsError when file exists."""
        client, mock_download_file = client_with_mocked_download
        mock_exists.return_value = True

        with pytest.raises(
            FileExistsError, match="File already exists.*Use overwrite=True"
        ):
            client.download_archive(printed_metadata=sample_printed_metadata)

        mock_download_file.assert_not_called()

    @patch("pathlib.Path.exists")
    def test_download_archive_overwrite_existing(
        self,
        mock_exists: MagicMock,
        client_with_mocked_download: tuple[PatentDataClient, MagicMock],
        sample_printed_metadata: PrintedMetaData,
    ) -> None:
        """Test download_archive overwrites when overwrite=True."""
        client, mock_download_file = client_with_mocked_download
        mock_exists.return_value = True

        expected_path = "patent_12345.xml"
        mock_download_file.return_value = expected_path

        result = client.download_archive(
            printed_metadata=sample_printed_metadata, overwrite=True
        )

        mock_download_file.assert_called_once()
        assert result == expected_path

    @patch("pathlib.Path.exists")
    def test_download_archive_fallback_filename_from_url(
        self,
        mock_exists: MagicMock,
        client_with_mocked_download: tuple[PatentDataClient, MagicMock],
    ) -> None:
        """Test filename fallback when xml_file_name is None."""
        client, mock_download_file = client_with_mocked_download
        mock_exists.return_value = False

        metadata = PrintedMetaData(
            xml_file_name=None,
            file_location_uri="https://example.com/data/file123.xml",
            product_identifier="PTGRXML",
        )

        expected_path = "file123.xml"
        mock_download_file.return_value = expected_path

        result = client.download_archive(printed_metadata=metadata)

        mock_download_file.assert_called_once_with(
            url=metadata.file_location_uri, file_path=expected_path
        )
        assert result == expected_path

    @patch("pathlib.Path.exists")
    def test_download_archive_last_resort_filename(
        self,
        mock_exists: MagicMock,
        client_with_mocked_download: tuple[PatentDataClient, MagicMock],
    ) -> None:
        """Test last resort filename when no xml_file_name and URL has no extension."""
        client, mock_download_file = client_with_mocked_download
        mock_exists.return_value = False

        metadata = PrintedMetaData(
            xml_file_name=None,
            file_location_uri="https://example.com/data/someidentifier",
            product_identifier="PTGRXML",
        )

        expected_path = "PTGRXML.xml"
        mock_download_file.return_value = expected_path

        result = client.download_archive(printed_metadata=metadata)

        mock_download_file.assert_called_once_with(
            url=metadata.file_location_uri, file_path=expected_path
        )
        assert result == expected_path


class TestPatentApplicationDataRetrieval:
    """Tests for  data retrieval of patent application search results using get_search_results."""

    def test_get_search_results_get_direct_query(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_empty: PatentDataResponse,
    ) -> None:
        """Test GET path of get_search_results with direct query, always requests JSON."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_empty

        method_params: Dict[str, Any] = {"query": "bulk test"}
        expected_api_params = {
            "q": "bulk test",
            "format": "json",
            "offset": 0,
            "limit": 25,
        }

        result = client.get_search_results(**method_params)

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/patent/applications/search/download",
            params=expected_api_params,
            response_class=PatentDataResponse,
        )
        assert result is mock_patent_data_response_empty

    def test_get_search_results_get_with_combined_q_convenience_params(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_empty: PatentDataResponse,
    ) -> None:
        """Test get_search_results GET path with a combination of _q convenience params."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_empty

        client.get_search_results(
            inventor_name_q="Doe", filing_date_from_q="2021-01-01", limit=5
        )

        expected_api_params = {
            "q": "applicationMetaData.inventorBag.inventorNameText:Doe AND applicationMetaData.filingDate:>=2021-01-01",
            "limit": 5,
            "offset": 0,
            "format": "json",
        }
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/patent/applications/search/download",
            params=expected_api_params,
            response_class=PatentDataResponse,
        )

    @pytest.mark.parametrize(
        "search_q_params, expected_q_part",
        [
            ({"application_number_q": "app123"}, "applicationNumberText:app123"),
            ({"patent_number_q": "PN123"}, "applicationMetaData.patentNumber:PN123"),
            (
                {"inventor_name_q": "Doe J"},
                "applicationMetaData.inventorBag.inventorNameText:Doe J",
            ),
            (
                {"applicant_name_q": "Corp Inc"},
                "applicationMetaData.firstApplicantName:Corp Inc",
            ),
            (
                {"assignee_name_q": "Assignee Ltd"},
                "assignmentBag.assigneeBag.assigneeNameText:Assignee Ltd",
            ),
            (
                {"classification_q": "H04L"},
                "applicationMetaData.cpcClassificationBag:H04L",
            ),
            (
                {"filing_date_from_q": "2021-01-01"},
                "applicationMetaData.filingDate:>=2021-01-01",
            ),
            (
                {"filing_date_to_q": "2021-12-31"},
                "applicationMetaData.filingDate:<=2021-12-31",
            ),
            (
                {"filing_date_from_q": "2021-01-01", "filing_date_to_q": "2021-12-31"},
                "applicationMetaData.filingDate:[2021-01-01 TO 2021-12-31]",
            ),
            (
                {"grant_date_from_q": "2022-01-01"},
                "applicationMetaData.grantDate:>=2022-01-01",
            ),
            (
                {"grant_date_to_q": "2022-12-31"},
                "applicationMetaData.grantDate:<=2022-12-31",
            ),
            (
                {"grant_date_from_q": "2022-01-01", "grant_date_to_q": "2022-12-31"},
                "applicationMetaData.grantDate:[2022-01-01 TO 2022-12-31]",
            ),
        ],
    )
    def test_get_search_results_get_various_q_convenience_filters(
        self,
        search_q_params: Dict[str, Any],
        expected_q_part: str,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_empty: PatentDataResponse,
    ) -> None:
        """Test get_search_results GET path with various individual _q convenience filters."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_empty

        limit = 15
        offset = 5

        effective_limit = search_q_params.pop("limit", limit)
        effective_offset = search_q_params.pop("offset", offset)

        client.get_search_results(
            **search_q_params, limit=effective_limit, offset=effective_offset
        )

        expected_call_params = {
            "q": expected_q_part,
            "limit": effective_limit,
            "offset": effective_offset,
            "format": "json",
        }

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/patent/applications/search/download",
            params=expected_call_params,
            response_class=PatentDataResponse,
        )
        # mock_make_request.reset_mock() # Removed to avoid issues with parametrize if tests are run in certain ways

    @pytest.mark.parametrize(
        "method_param_name, param_value, expected_api_key",
        [
            ("sort", "applicationMetaData.filingDate desc", "sort"),
            ("fields_param", "applicationNumberText,inventionTitle", "fields"),
            ("filters_param", "applicationMetaData.applicationTypeCode DES", "filters"),
            (
                "range_filters_param",
                "applicationMetaData.filingDate 2021-01-01:2021-12-31",
                "rangeFilters",
            ),
        ],
    )
    def test_get_search_results_get_with_openapi_params(  # New test
        self,
        method_param_name: str,
        param_value: str,
        expected_api_key: str,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_empty: PatentDataResponse,
    ) -> None:
        """Test get_search_results GET path with various direct OpenAPI parameters."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_empty

        method_kwargs: Dict[str, Any] = {
            method_param_name: param_value,
            "limit": 7,
            "offset": 1,
        }
        client.get_search_results(**method_kwargs)

        expected_api_params = {
            expected_api_key: param_value,
            "limit": 7,
            "offset": 1,
            "format": "json",
        }
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/patent/applications/search/download",
            params=expected_api_params,
            response_class=PatentDataResponse,
        )
        # mock_make_request.reset_mock() # Parametrized tests should not reset mock if one instance per test function

    def test_get_search_results_get_with_additional_query_params(  # New test
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_empty: PatentDataResponse,
    ) -> None:
        """Test get_search_results GET path with additional_query_params."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_empty

        client.get_search_results(
            query="main_download_query",
            fields_param="applicationNumberText",
            additional_query_params={
                "custom_dl_param": "dl_value",
                "another_dl": "val",
            },
            limit=3,
        )

        expected_api_params = {
            "q": "main_download_query",
            "fields": "applicationNumberText",
            "custom_dl_param": "dl_value",
            "another_dl": "val",
            "limit": 3,
            "offset": 0,
            "format": "json",
        }
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/patent/applications/search/download",
            params=expected_api_params,
            response_class=PatentDataResponse,
        )

    def test_get_search_results_post(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_with_data: PatentDataResponse,
    ) -> None:
        """Test POST path of get_search_results."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_with_data

        post_body_request = {"q": "Test POST", "fields": ["patentNumber"]}

        expected_post_body_sent_to_api = {
            "q": "Test POST",
            "fields": ["patentNumber"],
            "format": "json",
        }

        result = client.get_search_results(post_body=post_body_request)

        mock_make_request.assert_called_once_with(
            method="POST",
            endpoint="api/v1/patent/applications/search/download",
            json_data=expected_post_body_sent_to_api,
            params=None,
            response_class=PatentDataResponse,
        )
        assert result is mock_patent_data_response_with_data


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
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint=f"api/v1/patent/applications/{app_num}/meta-data",
            response_class=PatentDataResponse,
        )
        assert result is mock_patent_file_wrapper.application_meta_data

    def test_get_application_adjustment(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_data_response_with_data: PatentDataResponse,
        mock_patent_file_wrapper: PatentFileWrapper,
    ) -> None:
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_with_data
        app_num = mock_patent_file_wrapper.application_number_text
        assert app_num is not None
        result = client.get_application_adjustment(application_number=app_num)
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint=f"api/v1/patent/applications/{app_num}/adjustment",
            response_class=PatentDataResponse,
        )
        assert result is mock_patent_file_wrapper.patent_term_adjustment_data


class TestPatentStatusCodesEndpoints:
    """Tests for interacting with patent status code endpoints."""

    def test_get_status_codes(
        self, client_with_mocked_request: tuple[PatentDataClient, MagicMock]
    ) -> None:
        """Test get_status_codes method."""
        client, mock_make_request = client_with_mocked_request
        mock_api_response = {
            "count": 1,
            "statusCodeBag": [
                {
                    "applicationStatusCode": 100,
                    "applicationStatusDescriptionText": "Active",
                }
            ],
        }
        mock_make_request.return_value = mock_api_response
        result = client.get_status_codes(params={"limit": 1})

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/patent/status-codes",
            params={"limit": 1},
        )
        assert isinstance(result, StatusCodeSearchResponse)
        assert result.count == 1
        assert result.status_code_bag[0].code == 100

    def test_search_status_codes(
        self, client_with_mocked_request: tuple[PatentDataClient, MagicMock]
    ) -> None:
        """Test search_status_codes method."""
        client, mock_make_request = client_with_mocked_request
        mock_api_response = {
            "count": 1,
            "statusCodeBag": [
                {
                    "applicationStatusCode": 150,
                    "applicationStatusDescriptionText": "Pending",
                }
            ],
        }
        mock_make_request.return_value = mock_api_response
        search_request = {"q": "Pending"}

        result = client.search_status_codes(search_request=search_request)

        mock_make_request.assert_called_once_with(
            method="POST",
            endpoint="api/v1/patent/status-codes",
            json_data=search_request,
        )
        assert isinstance(result, StatusCodeSearchResponse)
        assert result.status_code_bag[0].description == "Pending"


class TestStatusCodeModels:
    """Tests for StatusCode, StatusCodeCollection, and StatusCodeSearchResponse models."""

    def test_status_code_model(self) -> None:
        status = StatusCode(code=100, description="Active Application")
        assert status.code == 100
        assert status.description == "Active Application"
        assert str(status) == "100: Active Application"

    def test_status_code_from_dict(self) -> None:
        data = {
            "applicationStatusCode": 150,
            "applicationStatusDescriptionText": "Abandoned",
        }
        status = StatusCode.from_dict(data)
        assert status.code == 150
        assert status.description == "Abandoned"

    def test_status_code_collection_model(self) -> None:
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
        collection = StatusCodeCollection(status_codes=[])
        assert len(collection) == 0
        assert repr(collection) == "StatusCodeCollection(empty)"

    def test_status_code_search_response_from_dict(self) -> None:
        data = {
            "count": 1,
            "statusCodeBag": [
                {
                    "applicationStatusCode": 100,
                    "applicationStatusDescriptionText": "Test",
                }
            ],
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
        client_with_mocked_request: tuple[
            PatentDataClient, MagicMock
        ],  # Use the existing fixture
        mock_patent_data_response_with_data: PatentDataResponse,
    ) -> PatentDataClient:
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_patent_data_response_with_data
        return client

    def test_get_application_metadata_type(
        self,
        client_for_return_type_tests: PatentDataClient,
        mock_patent_file_wrapper: PatentFileWrapper,
    ) -> None:
        result = client_for_return_type_tests.get_application_metadata("12345678")
        assert result is mock_patent_file_wrapper.application_meta_data

    def test_get_application_associated_documents_type(
        self,
        client_for_return_type_tests: PatentDataClient,
        mock_patent_file_wrapper: PatentFileWrapper,
    ) -> None:
        result = client_for_return_type_tests.get_application_associated_documents(
            "12345678"
        )
        assert isinstance(result, PrintedPublication)
        assert (
            result.pgpub_document_meta_data
            is mock_patent_file_wrapper.pgpub_document_meta_data
        )


class TestReturnTypesEdgeCases:
    """Tests edge cases for methods with specific model return types."""

    @pytest.fixture
    def client_with_minimal_wrapper_for_return_types(
        self,
        client_with_mocked_request: tuple[
            PatentDataClient, MagicMock
        ],  # Use the existing patching fixture
        mock_patent_file_wrapper_minimal: PatentFileWrapper,
    ) -> PatentDataClient:
        """Client whose _make_request returns a response with a minimal wrapper (only app number)."""
        client, mock_make_request = client_with_mocked_request
        response = PatentDataResponse(
            count=1, patent_file_wrapper_data_bag=[mock_patent_file_wrapper_minimal]
        )
        mock_make_request.return_value = response
        return client

    def test_specific_getters_handle_missing_fields_in_wrapper(
        self, client_with_minimal_wrapper_for_return_types: PatentDataClient
    ) -> None:
        client = client_with_minimal_wrapper_for_return_types
        app_num = "12345678"
        assert client.get_application_metadata(app_num) is None
        assert client.get_application_adjustment(app_num) is None
        assert client.get_application_assignment(app_num) == []
        assert client.get_application_attorney(app_num) is None

        continuity_result = client.get_application_continuity(app_num)
        assert isinstance(continuity_result, ApplicationContinuityData)
        assert continuity_result.parent_continuity_bag == []
        assert continuity_result.child_continuity_bag == []

        assert client.get_application_foreign_priority(app_num) == []
        assert client.get_application_transactions(app_num) == []

        assoc_docs_result = client.get_application_associated_documents(app_num)
        assert isinstance(assoc_docs_result, PrintedPublication)
        assert assoc_docs_result.pgpub_document_meta_data is None


class TestGeneralEdgeCasesAndErrors:
    """Tests for general robustness, error handling, and unexpected API responses."""

    def test_get_application_by_number_app_num_mismatch_in_bag(
        self,
        client_with_mocked_request: tuple[PatentDataClient, MagicMock],
        mock_patent_file_wrapper: PatentFileWrapper,
    ) -> None:
        client, mock_make_request = client_with_mocked_request
        requested_app_num = "DIFFERENT_APP_NUM_999"
        response_with_original_wrapper = PatentDataResponse(
            count=1, patent_file_wrapper_data_bag=[mock_patent_file_wrapper]
        )
        mock_make_request.return_value = response_with_original_wrapper

        with patch("builtins.print") as mock_print:
            result = client.get_application_by_number(
                application_number=requested_app_num
            )

        assert result is mock_patent_file_wrapper
        assert result is not None
        assert result.application_number_text == "12345678"
        mock_print.assert_any_call(
            "Warning: Fetched wrapper application number '12345678' "
            f"does not match requested '{requested_app_num}'."
        )

    def test_get_application_by_number_unexpected_response_type(
        self, client_with_mocked_request: tuple[PatentDataClient, MagicMock]
    ) -> None:
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = ["not", "a", "PatentDataResponse"]

        with pytest.raises(AssertionError):
            client.get_application_by_number(application_number="123")

    def test_api_error_handling(
        self, client_with_mocked_request: tuple[PatentDataClient, MagicMock]
    ) -> None:
        client, mock_make_request = client_with_mocked_request
        mock_make_request.side_effect = USPTOApiBadRequestError(
            "Mocked API Bad Request"
        )

        with pytest.raises(USPTOApiBadRequestError, match="Mocked API Bad Request"):
            client.search_applications(query="test")

    def test_search_applications_post_assertion_error(
        self, client_with_mocked_request: tuple[PatentDataClient, MagicMock]
    ) -> None:
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = {"not_a_patent_data_response": True}

        with pytest.raises(AssertionError):
            client.search_applications(post_body={"q": "test"})


class TestInternalHelpersEdgeCases:
    """Tests for edge cases in internal helper methods like _get_wrapper_from_response."""

    def test_get_wrapper_from_response_empty_bag(
        self,
        patent_data_client: PatentDataClient,
        mock_patent_data_response_empty: PatentDataResponse,
    ) -> None:
        result = patent_data_client._get_wrapper_from_response(
            mock_patent_data_response_empty
        )
        assert result is None


class TestDocumentModels:
    """Tests for Document, DocumentBag, and DocumentDownloadFormat models."""

    def test_document_model(self) -> None:
        dt = datetime(2023, 1, 1, 10, 30, 0, tzinfo=timezone.utc)
        doc = Document(
            application_number_text="12345678",
            document_identifier="DOC123",
            official_date=dt,
            document_code="IDS",
            document_code_description_text="Info Disclosure",
            direction_category=DirectionCategory.INCOMING,
        )
        assert doc.document_identifier == "DOC123"
        assert "2023-01-01" in str(doc)
        assert "IDS" in str(doc)

    def test_document_download_format_model(self) -> None:
        fmt = DocumentFormat(
            mime_type_identifier="PDF",
            download_url="http://example.com/doc.pdf",
            page_total_quantity=10,
        )
        assert fmt.mime_type_identifier == "PDF"
        assert "PDF format" in str(fmt)
        assert "10 pages" in str(fmt)

    def test_document_bag_model(self) -> None:
        doc1 = Document(
            document_identifier="D1",
            official_date=datetime.now(timezone.utc),
            document_code="C1",
        )
        doc2 = Document(
            document_identifier="D2",
            official_date=datetime.now(timezone.utc),
            document_code="C2",
        )
        bag = DocumentBag(documents=[doc1, doc2])
        assert len(bag) == 2
        assert list(bag) == [doc1, doc2]
        docs_from_iter = [d for d in bag]
        assert docs_from_iter == [doc1, doc2]


# New Test Class for CSV Export functionality from PatentDataResponse
class TestPatentDataResponseCSVExport:
    """Tests for the to_csv method of the PatentDataResponse model."""

    def test_to_csv_with_data(
        self,
        mock_patent_data_response_with_data: PatentDataResponse,
        mock_patent_file_wrapper: PatentFileWrapper,
        mock_application_meta_data: ApplicationMetaData,
    ) -> None:
        """Tests to_csv with a PatentDataResponse containing data."""
        response = mock_patent_data_response_with_data
        csv_string = response.to_csv()

        assert isinstance(csv_string, str)

        reader = csv.reader(io.StringIO(csv_string))
        header_row = next(reader)
        expected_headers = [
            "inventionTitle",
            "applicationNumberText",
            "filingDate",
            "applicationTypeLabelName",
            "publicationCategoryBag",
            "applicationStatusDescriptionText",
            "applicationStatusDate",
            "firstInventorName",
        ]
        assert header_row == expected_headers

        data_rows = list(reader)
        assert len(data_rows) == 1

        meta = mock_application_meta_data
        wrapper = mock_patent_file_wrapper

        expected_row_data = [
            meta.invention_title or "",
            wrapper.application_number_text or "",
            serialize_date(meta.filing_date) or "",
            meta.application_type_label_name or "",
            (
                "|".join(meta.publication_category_bag)
                if meta.publication_category_bag
                else ""
            ),
            meta.application_status_description_text or "",
            serialize_date(meta.application_status_date) or "",
            meta.first_inventor_name or "",
        ]
        assert data_rows[0] == expected_row_data

    def test_to_csv_empty_response(
        self, mock_patent_data_response_empty: PatentDataResponse
    ) -> None:
        """Tests to_csv with an empty PatentDataResponse."""
        response = mock_patent_data_response_empty
        csv_string = response.to_csv()

        reader = csv.reader(io.StringIO(csv_string))
        header_row = next(reader)
        expected_headers = [
            "inventionTitle",
            "applicationNumberText",
            "filingDate",
            "applicationTypeLabelName",
            "publicationCategoryBag",
            "applicationStatusDescriptionText",
            "applicationStatusDate",
            "firstInventorName",
        ]
        assert header_row == expected_headers
        with pytest.raises(StopIteration):
            next(reader)

    def test_to_csv_wrapper_missing_metadata(self) -> None:
        """Tests to_csv when a PatentFileWrapper is missing application_meta_data."""
        wrapper_no_meta = PatentFileWrapper(application_number_text="12345XYZ")
        response = PatentDataResponse(
            count=1, patent_file_wrapper_data_bag=[wrapper_no_meta]
        )
        csv_string = response.to_csv()

        reader = csv.reader(io.StringIO(csv_string))
        header_row = next(reader)
        expected_headers = [
            "inventionTitle",
            "applicationNumberText",
            "filingDate",
            "applicationTypeLabelName",
            "publicationCategoryBag",
            "applicationStatusDescriptionText",
            "applicationStatusDate",
            "firstInventorName",
        ]
        assert header_row == expected_headers

        with pytest.raises(StopIteration):
            next(reader)

        meta = ApplicationMetaData(invention_title="Test Title")
        wrapper_with_meta = PatentFileWrapper(
            application_number_text="456", application_meta_data=meta
        )
        response_mixed = PatentDataResponse(
            count=2, patent_file_wrapper_data_bag=[wrapper_no_meta, wrapper_with_meta]
        )
        csv_string_mixed = response_mixed.to_csv()
        reader_mixed = csv.reader(io.StringIO(csv_string_mixed))
        next(reader_mixed)
        data_rows_mixed = list(reader_mixed)
        assert len(data_rows_mixed) == 1
        assert data_rows_mixed[0][0] == "Test Title"
        assert data_rows_mixed[0][1] == "456"

    def test_to_csv_with_multiple_wrappers(
        self, mock_application_meta_data: ApplicationMetaData
    ) -> None:
        """Tests to_csv with multiple PatentFileWrappers."""
        wrapper1_meta = mock_application_meta_data
        wrapper1 = PatentFileWrapper(
            application_number_text="APP001", application_meta_data=wrapper1_meta
        )

        meta2_dict = mock_application_meta_data.to_dict()
        if meta2_dict:
            meta2_dict["inventionTitle"] = "Another Test Invention"
            meta2_dict["filingDate"] = "2021-02-02"
            meta2_dict["firstInventorName"] = "Jane Inventor"
            # Ensure other fields needed for CSV are present if they were None in original mock_app_meta
            meta2_dict.setdefault("applicationTypeLabelName", "Design")
            meta2_dict.setdefault("publicationCategoryBag", ["S1"])
            meta2_dict.setdefault("applicationStatusDescriptionText", "Allowed")
            meta2_dict.setdefault("applicationStatusDate", "2023-10-10")

            wrapper2_meta = ApplicationMetaData.from_dict(meta2_dict)
            wrapper2 = PatentFileWrapper(
                application_number_text="APP002", application_meta_data=wrapper2_meta
            )
            response = PatentDataResponse(
                count=2, patent_file_wrapper_data_bag=[wrapper1, wrapper2]
            )
        else:
            wrapper2_meta = ApplicationMetaData(
                invention_title="Fallback Title",
                first_inventor_name="Fallback Inventor",
                filing_date=date(2021, 2, 2),
                application_type_label_name="Utility",
                publication_category_bag=["A1"],
                application_status_description_text="Status",
                application_status_date=date(2021, 2, 3),
            )
            wrapper2 = PatentFileWrapper(
                application_number_text="APP002", application_meta_data=wrapper2_meta
            )
            response = PatentDataResponse(
                count=1, patent_file_wrapper_data_bag=[wrapper1]
            )  # fallback to 1 if dict was None

        csv_string = response.to_csv()
        reader = csv.reader(io.StringIO(csv_string))
        header_row = next(reader)
        data_rows = list(reader)

        assert len(data_rows) == response.count

        assert data_rows[0][0] == wrapper1_meta.invention_title
        assert data_rows[0][1] == "APP001"
        assert data_rows[0][2] == serialize_date(wrapper1_meta.filing_date)
        assert data_rows[0][7] == wrapper1_meta.first_inventor_name

        if response.count > 1:
            assert data_rows[1][0] == wrapper2_meta.invention_title
            assert data_rows[1][1] == "APP002"
            assert data_rows[1][2] == serialize_date(wrapper2_meta.filing_date)
            assert data_rows[1][7] == wrapper2_meta.first_inventor_name
