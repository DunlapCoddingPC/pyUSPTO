"""Tests for the clients in pyUSPTO.clients.petition_decisions.

This module contains comprehensive tests for PetitionDecisionsClient
initialization, search functionality, retrieval, pagination, and document
downloads, and for FinalPetitionDecisionsClient and the fixed-filter hook
that restricts it to final decisions.
"""

from collections.abc import Iterator
from typing import Any
from unittest.mock import MagicMock, Mock, call, patch

import pytest
import requests

import pyUSPTO
import pyUSPTO.clients
from pyUSPTO.clients.petition_decisions import (
    FinalPetitionDecisionsClient,
    PetitionDecisionsClient,
)
from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.petition_decisions import (
    DocumentDownloadOption,
    PetitionDecision,
    PetitionDecisionDownloadResponse,
    PetitionDecisionResponse,
)
from pyUSPTO.warnings import USPTODataMismatchWarning


# --- Fixtures ---
@pytest.fixture
def api_key_fixture() -> str:
    """Provides a test API key."""
    return "test_key"


@pytest.fixture
def uspto_config(api_key_fixture: str) -> USPTOConfig:
    """Provides a USPTOConfig instance with test API key."""
    return USPTOConfig(api_key=api_key_fixture)


@pytest.fixture
def petition_client(
    uspto_config: USPTOConfig,
) -> Iterator[PetitionDecisionsClient]:
    """Provides a PetitionDecisionsClient instance."""
    client = PetitionDecisionsClient(config=uspto_config)
    with patch.object(client, "_download_and_extract") as mock_download:
        mock_download.return_value = "/tmp/document.pdf"
        yield client


@pytest.fixture
def mock_petition_decision() -> PetitionDecision:
    """Provides a mock PetitionDecision instance."""
    return PetitionDecision(
        petition_decision_record_identifier="9f1a4a2b-eee1-58ec-a3aa-167c4075aed4",
        application_number_text="17765301",
        decided_petition_type_code="C",
        decided_petition_type_code_description_text="DENIED",
        first_applicant_name="Test Applicant",
        technology_center="1700",
        inventor_bag=["John Doe"],
    )


@pytest.fixture
def mock_petition_response_with_data(
    mock_petition_decision: PetitionDecision,
) -> PetitionDecisionResponse:
    """Provides a mock PetitionDecisionResponse with data."""
    return PetitionDecisionResponse(
        count=1,
        request_identifier="test-request-id",
        petition_decision_data_bag=[mock_petition_decision],
    )


@pytest.fixture
def mock_petition_response_empty() -> PetitionDecisionResponse:
    """Provides an empty mock PetitionDecisionResponse."""
    return PetitionDecisionResponse(count=0, petition_decision_data_bag=[])


@pytest.fixture
def client_with_mocked_request(
    petition_client: PetitionDecisionsClient,
) -> Iterator[tuple[PetitionDecisionsClient, MagicMock]]:
    """Provides a client with mocked _get_model method."""
    with patch.object(petition_client, "_get_model", autospec=True) as mock_get_model:
        yield petition_client, mock_get_model


@pytest.fixture
def mock_download_option() -> DocumentDownloadOption:
    """Provides a mock DocumentDownloadOption."""
    return DocumentDownloadOption(
        mime_type_identifier="PDF",
        download_url="https://api.test.uspto.gov/api/v1/download/test.pdf",
        page_total_quantity=10,
    )


@pytest.fixture
def final_petition_client(uspto_config: USPTOConfig) -> FinalPetitionDecisionsClient:
    """Provides a FinalPetitionDecisionsClient instance."""
    return FinalPetitionDecisionsClient(config=uspto_config)


@pytest.fixture
def final_client_with_mocked_request(
    final_petition_client: FinalPetitionDecisionsClient,
) -> Iterator[tuple[FinalPetitionDecisionsClient, MagicMock]]:
    """Provides a FinalPetitionDecisionsClient with mocked _get_model method."""
    with patch.object(
        final_petition_client, "_get_model", autospec=True
    ) as mock_get_model:
        yield final_petition_client, mock_get_model


@pytest.fixture
def mock_final_petition_decision() -> PetitionDecision:
    """Provides a final PetitionDecision (finalPetitionDecisionIndicator true)."""
    return PetitionDecision(
        petition_decision_record_identifier="1a552446-1d2b-570a-9bb6-b4fef39b0a91",
        application_number_text="17765301",
        final_petition_decision_indicator=True,
    )


@pytest.fixture
def mock_final_decision_pages() -> list[PetitionDecisionResponse]:
    """Provides two pages of final decisions (3 total) for pagination with limit=2."""
    return [
        PetitionDecisionResponse(
            count=3,
            petition_decision_data_bag=[
                PetitionDecision(
                    petition_decision_record_identifier="Final-Record-01",
                    final_petition_decision_indicator=True,
                ),
                PetitionDecision(
                    petition_decision_record_identifier="Final-Record-02",
                    final_petition_decision_indicator=True,
                ),
            ],
        ),
        PetitionDecisionResponse(
            count=3,
            petition_decision_data_bag=[
                PetitionDecision(
                    petition_decision_record_identifier="Final-Record-03",
                    final_petition_decision_indicator=True,
                ),
            ],
        ),
    ]


# --- Test Classes ---


class TestPetitionDecisionsClientInit:
    """Tests for initialization of PetitionDecisionsClient."""

    def test_init_with_api_key(
        self, petition_client: PetitionDecisionsClient, uspto_config: USPTOConfig
    ) -> None:
        """Test initialization with API key."""
        client = petition_client
        assert client._api_key == uspto_config.api_key
        assert client.base_url == "https://api.uspto.gov"

    def test_init_with_custom_base_url(self, uspto_config: USPTOConfig) -> None:
        """Test initialization with custom base URL."""
        custom_url = "https://custom.api.test.com"
        client = PetitionDecisionsClient(config=uspto_config, base_url=custom_url)
        assert client.base_url == custom_url

    def test_init_with_config(self) -> None:
        """Test initialization with config object."""
        config_key = "config_key"
        config_url = "https://config.api.test.com"
        config = USPTOConfig(api_key=config_key, petition_decisions_base_url=config_url)
        client = PetitionDecisionsClient(config=config)
        assert client._api_key == config_key
        assert client.base_url == config_url
        assert client.config is config

    def test_init_without_config(self, monkeypatch: Any) -> None:
        """Test initialization without config uses environment."""
        monkeypatch.setenv("USPTO_API_KEY", "env_key")
        client = PetitionDecisionsClient()
        assert client.config.api_key == "env_key"


class TestPetitionDecisionsClientSearch:
    """Tests for search_decisions method."""

    def test_search_get_direct_query(
        self,
        client_with_mocked_request: tuple[PetitionDecisionsClient, MagicMock],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test search with direct query string."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_petition_response_with_data

        result = client.search_decisions(query="Test", limit=10, offset=0)

        mock_get_model.assert_called_once_with(
            method="GET",
            endpoint="api/v1/petition/decisions/search",
            params={"q": "Test", "limit": 10, "offset": 0},
            response_class=PetitionDecisionResponse,
        )
        assert result is mock_petition_response_with_data

    def test_search_with_application_number(
        self,
        client_with_mocked_request: tuple[PetitionDecisionsClient, MagicMock],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test search with application number convenience parameter."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_petition_response_with_data

        result = client.search_decisions(application_number_q="17765301", limit=25)

        expected_params = {
            "q": "applicationNumberText:17765301",
            "limit": 25,
            "offset": 0,
        }
        mock_get_model.assert_called_once_with(
            method="GET",
            endpoint="api/v1/petition/decisions/search",
            params=expected_params,
            response_class=PetitionDecisionResponse,
        )
        assert result is mock_petition_response_with_data

    def test_search_with_date_range(
        self,
        client_with_mocked_request: tuple[PetitionDecisionsClient, MagicMock],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test search with date range."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_petition_response_with_data

        client.search_decisions(
            decision_date_from_q="2022-01-01",
            decision_date_to_q="2022-12-31",
            limit=25,
        )

        expected_params = {
            "q": "decisionDate:[2022-01-01 TO 2022-12-31]",
            "limit": 25,
            "offset": 0,
        }
        mock_get_model.assert_called_once_with(
            method="GET",
            endpoint="api/v1/petition/decisions/search",
            params=expected_params,
            response_class=PetitionDecisionResponse,
        )

    def test_search_with_multiple_params(
        self,
        client_with_mocked_request: tuple[PetitionDecisionsClient, MagicMock],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test search combining multiple parameters."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_petition_response_with_data

        client.search_decisions(
            applicant_name_q="Test Corp",
            technology_center_q="1700",
            decided_petition_type_code_q="C",
            limit=50,
        )

        # Check that the query contains all three conditions joined with AND
        call_args = mock_get_model.call_args
        params = call_args[1]["params"]
        assert "q" in params
        query = params["q"]
        assert 'firstApplicantName:"Test Corp"' in query
        assert "technologyCenter:1700" in query
        assert "decidedPetitionTypeCode:C" in query
        assert " AND " in query
        assert params["limit"] == 50

    def test_search_post_request(
        self,
        client_with_mocked_request: tuple[PetitionDecisionsClient, MagicMock],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test search with POST body."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_petition_response_with_data

        post_body = {"q": "technologyCenter:1700", "limit": 100}
        client.search_decisions(post_body=post_body)

        mock_get_model.assert_called_once_with(
            method="POST",
            endpoint="api/v1/petition/decisions/search",
            json_data=post_body,
            params=None,
            response_class=PetitionDecisionResponse,
        )

    def test_search_with_patent_number(
        self,
        client_with_mocked_request: tuple[PetitionDecisionsClient, MagicMock],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test search with patent_number_q parameter."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_petition_response_with_data

        client.search_decisions(patent_number_q="10123456")

        call_args = mock_get_model.call_args
        params = call_args[1]["params"]
        assert "patentNumber:10123456" in params["q"]

    def test_search_with_inventor_name(
        self,
        client_with_mocked_request: tuple[PetitionDecisionsClient, MagicMock],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test search with inventor_name_q parameter."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_petition_response_with_data

        client.search_decisions(inventor_name_q="John Doe")

        call_args = mock_get_model.call_args
        params = call_args[1]["params"]
        assert 'inventorBag:"John Doe"' in params["q"]

    def test_search_with_invention_title(
        self,
        client_with_mocked_request: tuple[PetitionDecisionsClient, MagicMock],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test search with invention_title_q parameter."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_petition_response_with_data

        client.search_decisions(invention_title_q="Test Invention")

        call_args = mock_get_model.call_args
        params = call_args[1]["params"]
        assert 'inventionTitle:"Test Invention"' in params["q"]

    def test_search_with_final_deciding_office_name(
        self,
        client_with_mocked_request: tuple[PetitionDecisionsClient, MagicMock],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test search with final_deciding_office_name_q parameter."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_petition_response_with_data

        client.search_decisions(final_deciding_office_name_q="TC Director")

        call_args = mock_get_model.call_args
        params = call_args[1]["params"]
        assert 'finalDecidingOfficeName:"TC Director"' in params["q"]

    def test_search_with_decision_date_from_only(
        self,
        client_with_mocked_request: tuple[PetitionDecisionsClient, MagicMock],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test search with only decision_date_from_q parameter."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_petition_response_with_data

        client.search_decisions(decision_date_from_q="2023-01-01")

        call_args = mock_get_model.call_args
        params = call_args[1]["params"]
        assert "decisionDate:>=2023-01-01" in params["q"]

    def test_search_with_decision_date_to_only(
        self,
        client_with_mocked_request: tuple[PetitionDecisionsClient, MagicMock],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test search with only decision_date_to_q parameter."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_petition_response_with_data

        client.search_decisions(decision_date_to_q="2023-12-31")

        call_args = mock_get_model.call_args
        params = call_args[1]["params"]
        assert "decisionDate:<=2023-12-31" in params["q"]

    def test_search_with_petition_mail_date_from_only(
        self,
        client_with_mocked_request: tuple[PetitionDecisionsClient, MagicMock],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test search with only petition_mail_date_from_q parameter."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_petition_response_with_data

        client.search_decisions(petition_mail_date_from_q="2023-01-01")

        call_args = mock_get_model.call_args
        params = call_args[1]["params"]
        assert "petitionMailDate:>=2023-01-01" in params["q"]

    def test_search_with_petition_mail_date_to_only(
        self,
        client_with_mocked_request: tuple[PetitionDecisionsClient, MagicMock],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test search with only petition_mail_date_to_q parameter."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_petition_response_with_data

        client.search_decisions(petition_mail_date_to_q="2023-12-31")

        call_args = mock_get_model.call_args
        params = call_args[1]["params"]
        assert "petitionMailDate:<=2023-12-31" in params["q"]

    def test_search_with_petition_mail_date_range(
        self,
        client_with_mocked_request: tuple[PetitionDecisionsClient, MagicMock],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test search with petition mail date range."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_petition_response_with_data

        client.search_decisions(
            petition_mail_date_from_q="2023-01-01",
            petition_mail_date_to_q="2023-12-31",
        )

        call_args = mock_get_model.call_args
        params = call_args[1]["params"]
        assert "petitionMailDate:[2023-01-01 TO 2023-12-31]" in params["q"]

    def test_search_with_optional_params(
        self,
        client_with_mocked_request: tuple[PetitionDecisionsClient, MagicMock],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test search with optional sort, facets, fields, filters, and range_filters."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_petition_response_with_data

        client.search_decisions(
            query="test",
            sort="decisionDate desc",
            facets="technologyCenter",
            fields="applicationNumberText,patentNumber",
            filters="decidedPetitionTypeCode A",
            range_filters="decisionDate:[2020 TO 2024]",
        )

        call_args = mock_get_model.call_args
        params = call_args[1]["params"]
        assert params["sort"] == "decisionDate desc"
        assert params["facets"] == "technologyCenter"
        assert params["fields"] == "applicationNumberText,patentNumber"
        assert params["filters"] == "decidedPetitionTypeCode A"
        assert params["rangeFilters"] == "decisionDate:[2020 TO 2024]"

    def test_search_with_additional_query_params(
        self,
        client_with_mocked_request: tuple[PetitionDecisionsClient, MagicMock],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test search with additional_query_params."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_petition_response_with_data

        client.search_decisions(
            query="test", additional_query_params={"customParam": "customValue"}
        )

        call_args = mock_get_model.call_args
        params = call_args[1]["params"]
        assert params["customParam"] == "customValue"


class TestPetitionDecisionsClientGetById:
    """Tests for get_decision_by_id method."""

    def test_get_decision_by_id(
        self,
        client_with_mocked_request: tuple[PetitionDecisionsClient, MagicMock],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test retrieving decision by ID."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_petition_response_with_data

        record_id = "9f1a4a2b-eee1-58ec-a3aa-167c4075aed4"
        result = client.get_decision_by_id(record_id)

        mock_get_model.assert_called_once_with(
            method="GET",
            endpoint=f"api/v1/petition/decisions/{record_id}",
            params=None,
            response_class=PetitionDecisionResponse,
        )
        assert result is not None
        assert result.petition_decision_record_identifier == record_id

    def test_get_decision_by_id_not_found(
        self,
        client_with_mocked_request: tuple[PetitionDecisionsClient, MagicMock],
        mock_petition_response_empty: PetitionDecisionResponse,
    ) -> None:
        """Test retrieving non-existent decision returns None."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_petition_response_empty

        result = client.get_decision_by_id("nonexistent-id")
        assert result is None


class TestPetitionDecisionsClientDownload:
    """Tests for download_decisions method."""

    def test_download_json(
        self,
        client_with_mocked_request: tuple[PetitionDecisionsClient, MagicMock],
    ) -> None:
        """Test downloading decisions in JSON format."""
        client, mock_get_model = client_with_mocked_request

        mock_response = PetitionDecisionDownloadResponse(
            petition_decision_data=[
                PetitionDecision(
                    application_number_text="12345678",
                    petition_decision_record_identifier="test-id",
                )
            ]
        )
        mock_get_model.return_value = mock_response

        result = client.download_decisions(format="json", applicant_name_q="Test Corp")

        assert isinstance(result, PetitionDecisionDownloadResponse)
        assert len(result.petition_decision_data) == 1

        mock_get_model.assert_called_once_with(
            method="GET",
            endpoint="api/v1/petition/decisions/search/download",
            response_class=PetitionDecisionDownloadResponse,
            params={
                "format": "json",
                "q": 'firstApplicantName:"Test Corp"',
            },
        )

    def test_download_csv(
        self,
        petition_client: PetitionDecisionsClient,
    ) -> None:
        """Test downloading decisions in CSV format as streaming response."""
        mock_response = MagicMock(spec=requests.Response)
        mock_response.iter_content.return_value = [b"csv,data"]

        with patch.object(
            petition_client, "_stream_request", return_value=mock_response
        ) as mock_stream_request:
            result = petition_client.download_decisions(format="csv")

            assert isinstance(result, requests.Response)
            mock_stream_request.assert_called_once()

    def test_download_csv_to_file(
        self,
        petition_client: PetitionDecisionsClient,
        tmp_path,
    ) -> None:
        """Test downloading decisions in CSV format and saving to file."""
        # Mock both _stream_request and _save_response_to_file
        mock_response = Mock(spec=requests.Response)
        expected_path = str(tmp_path / "petition_decisions.csv")

        with (
            patch.object(
                petition_client, "_stream_request", return_value=mock_response
            ) as mock_stream_request,
            patch.object(
                petition_client, "_save_response_to_file", return_value=expected_path
            ) as mock_save,
        ):
            result = petition_client.download_decisions(
                format="csv",
                decision_date_from_q="2023-01-01",
                decision_date_to_q="2023-12-31",
                destination=str(tmp_path),
            )

            assert result == expected_path
            mock_stream_request.assert_called_once()
            mock_save.assert_called_once()

            # Verify _save_response_to_file was called with correct arguments
            save_call_args = mock_save.call_args
            assert save_call_args[1]["response"] == mock_response
            assert save_call_args[1]["destination"] == str(tmp_path)

    def test_download_with_patent_number(
        self,
        client_with_mocked_request: tuple[PetitionDecisionsClient, MagicMock],
    ) -> None:
        """Test download with patent_number_q parameter."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = PetitionDecisionDownloadResponse(
            petition_decision_data=[]
        )

        client.download_decisions(format="json", patent_number_q="10123456")

        call_args = mock_get_model.call_args
        params = call_args[1]["params"]
        assert "patentNumber:10123456" in params["q"]

    def test_download_with_application_number(
        self,
        client_with_mocked_request: tuple[PetitionDecisionsClient, MagicMock],
    ) -> None:
        """Test download with application_number_q parameter."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = PetitionDecisionDownloadResponse(
            petition_decision_data=[]
        )

        client.download_decisions(format="json", application_number_q="17765301")

        call_args = mock_get_model.call_args
        params = call_args[1]["params"]
        assert "applicationNumberText:17765301" in params["q"]

    def test_download_with_inventor_name(
        self,
        client_with_mocked_request: tuple[PetitionDecisionsClient, MagicMock],
    ) -> None:
        """Test download with inventor_name_q parameter."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = PetitionDecisionDownloadResponse(
            petition_decision_data=[]
        )

        client.download_decisions(format="json", inventor_name_q="Jane Doe")

        call_args = mock_get_model.call_args
        params = call_args[1]["params"]
        assert 'inventorBag:"Jane Doe"' in params["q"]

    def test_download_with_decision_date_from_only(
        self,
        client_with_mocked_request: tuple[PetitionDecisionsClient, MagicMock],
    ) -> None:
        """Test download with only decision_date_from_q parameter."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = PetitionDecisionDownloadResponse(
            petition_decision_data=[]
        )

        client.download_decisions(format="json", decision_date_from_q="2023-01-01")

        call_args = mock_get_model.call_args
        params = call_args[1]["params"]
        assert "decisionDate:>=2023-01-01" in params["q"]

    def test_download_with_decision_date_to_only(
        self,
        client_with_mocked_request: tuple[PetitionDecisionsClient, MagicMock],
    ) -> None:
        """Test download with only decision_date_to_q parameter."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = PetitionDecisionDownloadResponse(
            petition_decision_data=[]
        )

        client.download_decisions(format="json", decision_date_to_q="2023-12-31")

        call_args = mock_get_model.call_args
        params = call_args[1]["params"]
        assert "decisionDate:<=2023-12-31" in params["q"]

    def test_download_with_optional_params(
        self,
        client_with_mocked_request: tuple[PetitionDecisionsClient, MagicMock],
    ) -> None:
        """Test download with optional sort, fields, filters, and range_filters."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = PetitionDecisionDownloadResponse(
            petition_decision_data=[]
        )

        client.download_decisions(
            format="json",
            query="test",
            sort="decisionDate desc",
            fields="applicationNumberText",
            filters="decidedPetitionTypeCode A",
            range_filters="decisionDate:[2020 TO 2024]",
        )

        call_args = mock_get_model.call_args
        params = call_args[1]["params"]
        assert params["sort"] == "decisionDate desc"
        assert params["fields"] == "applicationNumberText"
        assert params["filters"] == "decidedPetitionTypeCode A"
        assert params["rangeFilters"] == "decisionDate:[2020 TO 2024]"

    def test_download_with_offset_and_limit(
        self,
        client_with_mocked_request: tuple[PetitionDecisionsClient, MagicMock],
    ) -> None:
        """Test download with offset and limit parameters."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = PetitionDecisionDownloadResponse(
            petition_decision_data=[]
        )

        client.download_decisions(format="json", offset=50, limit=100)

        call_args = mock_get_model.call_args
        params = call_args[1]["params"]
        assert params["offset"] == 50
        assert params["limit"] == 100

    def test_download_with_additional_query_params(
        self,
        client_with_mocked_request: tuple[PetitionDecisionsClient, MagicMock],
    ) -> None:
        """Test download with additional_query_params."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = PetitionDecisionDownloadResponse(
            petition_decision_data=[]
        )

        client.download_decisions(
            format="json", additional_query_params={"customParam": "customValue"}
        )

        call_args = mock_get_model.call_args
        params = call_args[1]["params"]
        assert params["customParam"] == "customValue"


class TestPetitionDecisionsClientPagination:
    """Tests for paginate_decisions method."""

    def test_paginate_decisions(self, petition_client: PetitionDecisionsClient) -> None:
        """Test pagination through decisions."""
        # Mock multiple pages of results (count is the total across all pages)
        page1 = PetitionDecisionResponse(
            count=3,
            petition_decision_data_bag=[
                PetitionDecision(
                    application_number_text="111",
                    petition_decision_record_identifier="Test-Record-01",
                ),
                PetitionDecision(
                    application_number_text="222",
                    petition_decision_record_identifier="Test-Record-01",
                ),
            ],
        )
        page2 = PetitionDecisionResponse(
            count=3,
            petition_decision_data_bag=[
                PetitionDecision(
                    application_number_text="333",
                    petition_decision_record_identifier="Test-Record-01",
                ),
            ],
        )

        with patch.object(petition_client, "search_decisions") as mock_search:
            mock_search.side_effect = [page1, page2]

            results = list(
                petition_client.paginate_decisions(technology_center_q="1700", limit=2)
            )

            assert len(results) == 3
            assert results[0].application_number_text == "111"
            assert results[1].application_number_text == "222"
            assert results[2].application_number_text == "333"

    def test_paginate_decisions_rejects_offset_in_kwargs(
        self, petition_client: PetitionDecisionsClient
    ) -> None:
        """Test that pagination raises error with offset in kwargs."""
        with pytest.raises(ValueError, match="Cannot specify 'offset'"):
            list(petition_client.paginate_decisions(query="test", offset=10))

    def test_paginate_get_sorts_by_record_id_without_caller_sort(
        self,
        client_with_mocked_request: tuple[PetitionDecisionsClient, MagicMock],
        mock_final_decision_pages: list[PetitionDecisionResponse],
    ) -> None:
        """Test GET pagination sorts by the unique record ID when no sort is given."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.side_effect = mock_final_decision_pages

        list(client.paginate_decisions(query="decisionDate:2024-03-05", limit=2))

        assert [c.kwargs["params"]["sort"] for c in mock_get_model.call_args_list] == [
            ["petitionDecisionRecordIdentifier asc"],
            ["petitionDecisionRecordIdentifier asc"],
        ]

    @pytest.mark.parametrize(
        ("caller_sort", "expected_sort"),
        [
            (
                "decisionDate desc",
                ["decisionDate desc", "petitionDecisionRecordIdentifier asc"],
            ),
            (
                ["decisionDate desc", "applicationNumberText asc"],
                [
                    "decisionDate desc",
                    "applicationNumberText asc",
                    "petitionDecisionRecordIdentifier asc",
                ],
            ),
        ],
    )
    def test_paginate_get_appends_record_id_to_caller_sort(
        self,
        client_with_mocked_request: tuple[PetitionDecisionsClient, MagicMock],
        mock_final_decision_pages: list[PetitionDecisionResponse],
        caller_sort: str | list[str],
        expected_sort: list[str],
    ) -> None:
        """Test GET pagination appends the record ID tiebreaker to the caller's sort."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.side_effect = mock_final_decision_pages
        caller_sort_before = (
            list(caller_sort) if isinstance(caller_sort, list) else caller_sort
        )

        list(client.paginate_decisions(query="q", sort=caller_sort, limit=2))

        assert [c.kwargs["params"]["sort"] for c in mock_get_model.call_args_list] == [
            expected_sort,
            expected_sort,
        ]
        assert caller_sort == caller_sort_before

    def test_paginate_get_keeps_caller_record_id_sort(
        self,
        client_with_mocked_request: tuple[PetitionDecisionsClient, MagicMock],
        mock_final_decision_pages: list[PetitionDecisionResponse],
    ) -> None:
        """Test a caller sort already on the record ID gets no duplicate key."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.side_effect = mock_final_decision_pages

        list(
            client.paginate_decisions(
                query="q", sort="petitionDecisionRecordIdentifier desc", limit=2
            )
        )

        assert [c.kwargs["params"]["sort"] for c in mock_get_model.call_args_list] == [
            ["petitionDecisionRecordIdentifier desc"],
            ["petitionDecisionRecordIdentifier desc"],
        ]

    def test_paginate_post_appends_record_id_sort(
        self,
        client_with_mocked_request: tuple[PetitionDecisionsClient, MagicMock],
        mock_final_decision_pages: list[PetitionDecisionResponse],
    ) -> None:
        """Test POST pagination appends the tiebreaker without changing the caller's body."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.side_effect = mock_final_decision_pages
        caller_sort = [{"field": "decisionDate", "order": "desc"}]
        post_body: dict[str, Any] = {
            "q": "q",
            "sort": caller_sort,
            "pagination": {"limit": 2},
        }

        list(client.paginate_decisions(post_body=post_body))

        expected_sort = [
            {"field": "decisionDate", "order": "desc"},
            {"field": "petitionDecisionRecordIdentifier", "order": "asc"},
        ]
        assert [
            c.kwargs["json_data"]["sort"] for c in mock_get_model.call_args_list
        ] == [expected_sort, expected_sort]
        assert post_body == {
            "q": "q",
            "sort": [{"field": "decisionDate", "order": "desc"}],
            "pagination": {"limit": 2},
        }
        assert post_body["sort"] is caller_sort

    def test_paginate_post_keeps_caller_record_id_sort(
        self,
        client_with_mocked_request: tuple[PetitionDecisionsClient, MagicMock],
        mock_final_decision_pages: list[PetitionDecisionResponse],
    ) -> None:
        """Test a POST sort already on the record ID gets no duplicate key."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.side_effect = mock_final_decision_pages
        post_body: dict[str, Any] = {
            "q": "q",
            "sort": [{"field": "petitionDecisionRecordIdentifier", "order": "desc"}],
            "pagination": {"limit": 2},
        }

        list(client.paginate_decisions(post_body=post_body))

        expected_sort = [{"field": "petitionDecisionRecordIdentifier", "order": "desc"}]
        assert [
            c.kwargs["json_data"]["sort"] for c in mock_get_model.call_args_list
        ] == [expected_sort, expected_sort]
        assert post_body == {
            "q": "q",
            "sort": [{"field": "petitionDecisionRecordIdentifier", "order": "desc"}],
            "pagination": {"limit": 2},
        }

    def test_search_decisions_sends_sort_list(
        self,
        client_with_mocked_request: tuple[PetitionDecisionsClient, MagicMock],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test a sort list is passed through for requests to repeat the sort param."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_petition_response_with_data

        client.search_decisions(
            query="q",
            sort=["decisionDate desc", "petitionDecisionRecordIdentifier asc"],
        )

        assert mock_get_model.call_args.kwargs["params"]["sort"] == [
            "decisionDate desc",
            "petitionDecisionRecordIdentifier asc",
        ]


class TestPetitionDecisionsClientDocumentDownload:
    """Tests for download_petition_document method."""

    def test_download_document_success(
        self,
        petition_client: PetitionDecisionsClient,
        mock_download_option: DocumentDownloadOption,
    ) -> None:
        """Test successful document download."""
        with patch.object(petition_client, "_download_and_extract") as mock_download:
            mock_download.return_value = "/path/to/test.pdf"

            result = petition_client.download_petition_document(
                mock_download_option, destination="/tmp"
            )

            assert result == "/path/to/test.pdf"
            mock_download.assert_called_once()
            call_args = mock_download.call_args
            # Verify destination and file_name
            assert call_args[1]["destination"] == "/tmp"
            assert call_args[1]["file_name"] is None

    def test_download_document_no_url(
        self, petition_client: PetitionDecisionsClient
    ) -> None:
        """Test download fails without URL."""
        option = DocumentDownloadOption(mime_type_identifier="PDF", download_url=None)

        with pytest.raises(ValueError, match="has no download_url"):
            petition_client.download_petition_document(option)

    def test_download_document_file_exists(
        self,
        petition_client: PetitionDecisionsClient,
        mock_download_option: DocumentDownloadOption,
        tmp_path: Any,
    ) -> None:
        """Test download fails if file exists and overwrite=False."""
        # Create an existing file
        existing_file = tmp_path / "document.pdf"
        existing_file.write_text("existing content")

        # Mock _download_and_extract to raise FileExistsError
        with patch.object(petition_client, "_download_and_extract") as mock_dl:
            mock_dl.side_effect = FileExistsError(
                f"File exists: {existing_file}. Use overwrite=True"
            )

            with pytest.raises(FileExistsError, match="File exists"):
                petition_client.download_petition_document(
                    mock_download_option,
                    file_name="document.pdf",
                    destination=str(tmp_path),
                    overwrite=False,
                )

    def test_download_document_url_without_extension(
        self, petition_client: PetitionDecisionsClient
    ) -> None:
        """Test download with URL that has no file extension generates filename from MIME type."""
        option = DocumentDownloadOption(
            mime_type_identifier="PDF",
            download_url="https://api.test.uspto.gov/api/v1/download/ABCD1234",
            page_total_quantity=5,
        )

        with patch.object(petition_client, "_download_and_extract") as mock_download:
            mock_download.return_value = "/tmp/document.pdf"

            petition_client.download_petition_document(option, destination="/tmp")

            call_args = mock_download.call_args
            # Verify destination
            assert call_args[1]["destination"] == "/tmp"
            assert call_args[1]["file_name"] is None

    def test_download_document_url_without_extension_no_mime(
        self, petition_client: PetitionDecisionsClient
    ) -> None:
        """Test download with URL without extension and no MIME type defaults to pdf."""
        option = DocumentDownloadOption(
            mime_type_identifier=None,
            download_url="https://api.test.uspto.gov/api/v1/download/XYZ9999",
            page_total_quantity=3,
        )

        with patch.object(petition_client, "_download_and_extract") as mock_download:
            mock_download.return_value = "/tmp/document.pdf"

            petition_client.download_petition_document(option, destination="/tmp")

            call_args = mock_download.call_args
            # Verify destination
            assert call_args[1]["destination"] == "/tmp"
            assert call_args[1]["file_name"] is None

    def test_download_document_no_destination(
        self, petition_client: PetitionDecisionsClient
    ) -> None:
        """Test download without destination saves to current directory."""
        option = DocumentDownloadOption(
            mime_type_identifier="PDF",
            download_url="https://api.test.uspto.gov/api/v1/download/test.pdf",
            page_total_quantity=10,
        )

        with patch.object(petition_client, "_download_and_extract") as mock_download:
            mock_download.return_value = "test.pdf"

            petition_client.download_petition_document(option)

            call_args = mock_download.call_args
            # Verify no destination specified
            assert call_args[1]["destination"] is None
            assert call_args[1]["file_name"] is None


class TestPetitionDecisionsClientHelpers:
    """Tests for helper methods."""

    def test_get_decision_from_response(
        self,
        petition_client: PetitionDecisionsClient,
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test _get_decision_from_response helper."""
        result = petition_client._get_decision_from_response(
            mock_petition_response_with_data,
            petition_decision_record_identifier_for_validation="9f1a4a2b-eee1-58ec-a3aa-167c4075aed4",
        )
        assert result is not None
        assert result.application_number_text == "17765301"

    def test_get_decision_from_empty_response(
        self,
        petition_client: PetitionDecisionsClient,
        mock_petition_response_empty: PetitionDecisionResponse,
    ) -> None:
        """Test _get_decision_from_response with empty response."""
        result = petition_client._get_decision_from_response(
            mock_petition_response_empty
        )
        assert result is None

    def test_get_decision_from_response_id_mismatch(
        self,
        petition_client: PetitionDecisionsClient,
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test _get_decision_from_response with mismatched ID raises a warning.

        When the API returns a different decision identifier than requested,
        a USPTODataMismatchWarning should be issued to alert the user of
        the data inconsistency.
        """
        with pytest.warns(
            USPTODataMismatchWarning,
            match="API returned decision identifier .* but requested 'different-id-12345'",
        ):
            result = petition_client._get_decision_from_response(
                mock_petition_response_with_data,
                petition_decision_record_identifier_for_validation="different-id-12345",
            )
        assert result is not None


class TestFinalPetitionDecisionsClient:
    """Tests for FinalPetitionDecisionsClient and the fixed-filter hook."""

    def test_init_with_config(
        self,
        final_petition_client: FinalPetitionDecisionsClient,
        uspto_config: USPTOConfig,
    ) -> None:
        """Test initialization uses the given config and petition decisions URL."""
        client = final_petition_client
        assert client.config is uspto_config
        assert client.base_url == "https://api.uspto.gov"

    def test_search_get_without_criteria_adds_final_filter(
        self,
        final_client_with_mocked_request: tuple[
            FinalPetitionDecisionsClient, MagicMock
        ],
        mock_petition_response_empty: PetitionDecisionResponse,
    ) -> None:
        """Test a bare GET search sends only the final filter beyond the defaults."""
        client, mock_get_model = final_client_with_mocked_request
        mock_get_model.return_value = mock_petition_response_empty

        result = client.search_decisions()

        mock_get_model.assert_called_once_with(
            method="GET",
            endpoint="api/v1/petition/decisions/search",
            params={
                "offset": 0,
                "limit": 25,
                "filters": ["finalPetitionDecisionIndicator true"],
            },
            response_class=PetitionDecisionResponse,
        )
        assert result is mock_petition_response_empty

    def test_search_get_convenience_params_with_caller_filter(
        self,
        final_client_with_mocked_request: tuple[
            FinalPetitionDecisionsClient, MagicMock
        ],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test the final filter follows the caller's filter and q is unchanged."""
        client, mock_get_model = final_client_with_mocked_request
        mock_get_model.return_value = mock_petition_response_with_data

        client.search_decisions(
            application_number_q="17765301",
            decision_date_from_q="2020-01-01",
            filters="technologyCenter 1700",
            limit=10,
        )

        mock_get_model.assert_called_once_with(
            method="GET",
            endpoint="api/v1/petition/decisions/search",
            params={
                "q": "applicationNumberText:17765301 AND decisionDate:>=2020-01-01",
                "offset": 0,
                "limit": 10,
                "filters": [
                    "technologyCenter 1700",
                    "finalPetitionDecisionIndicator true",
                ],
            },
            response_class=PetitionDecisionResponse,
        )

    def test_search_get_direct_query_passes_through(
        self,
        final_client_with_mocked_request: tuple[
            FinalPetitionDecisionsClient, MagicMock
        ],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test a direct query is sent untouched with the final filter appended."""
        client, mock_get_model = final_client_with_mocked_request
        mock_get_model.return_value = mock_petition_response_with_data

        client.search_decisions(
            query="applicationNumberText:17765301 AND decidedPetitionTypeCode:C",
            limit=10,
            offset=0,
        )

        mock_get_model.assert_called_once_with(
            method="GET",
            endpoint="api/v1/petition/decisions/search",
            params={
                "q": "applicationNumberText:17765301 AND decidedPetitionTypeCode:C",
                "offset": 0,
                "limit": 10,
                "filters": ["finalPetitionDecisionIndicator true"],
            },
            response_class=PetitionDecisionResponse,
        )

    def test_search_additional_query_params_filters_list_is_extended(
        self,
        final_client_with_mocked_request: tuple[
            FinalPetitionDecisionsClient, MagicMock
        ],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test a filters list from additional_query_params is extended, not replaced."""
        client, mock_get_model = final_client_with_mocked_request
        mock_get_model.return_value = mock_petition_response_with_data
        caller_filters = ["technologyCenter 1700", "decidedPetitionTypeCode C"]

        client.search_decisions(
            query="applicationNumberText:17765301",
            additional_query_params={"filters": caller_filters},
        )

        mock_get_model.assert_called_once_with(
            method="GET",
            endpoint="api/v1/petition/decisions/search",
            params={
                "q": "applicationNumberText:17765301",
                "offset": 0,
                "limit": 25,
                "filters": [
                    "technologyCenter 1700",
                    "decidedPetitionTypeCode C",
                    "finalPetitionDecisionIndicator true",
                ],
            },
            response_class=PetitionDecisionResponse,
        )
        assert caller_filters == ["technologyCenter 1700", "decidedPetitionTypeCode C"]

    def test_search_get_sends_filters_as_repeated_query_params(
        self, final_petition_client: FinalPetitionDecisionsClient
    ) -> None:
        """Test the caller's filter and the final filter go out as repeated params."""
        mock_response = MagicMock(spec=requests.Response)
        mock_response.json.return_value = {"count": 0, "petitionDecisionDataBag": []}

        with patch.object(
            final_petition_client.session, "get", autospec=True
        ) as mock_session_get:
            mock_session_get.return_value = mock_response
            final_petition_client.search_decisions(
                query="applicationNumberText:17765301",
                filters="technologyCenter 1700",
            )

        mock_session_get.assert_called_once()
        sent = mock_session_get.call_args.kwargs
        prepared = requests.Request("GET", sent["url"], params=sent["params"]).prepare()
        assert prepared.url == (
            "https://api.uspto.gov/api/v1/petition/decisions/search"
            "?q=applicationNumberText%3A17765301&offset=0&limit=25"
            "&filters=technologyCenter+1700"
            "&filters=finalPetitionDecisionIndicator+true"
        )

    def test_search_post_without_filters_adds_final_filter_entry(
        self,
        final_client_with_mocked_request: tuple[
            FinalPetitionDecisionsClient, MagicMock
        ],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test a POST body without filters is sent with the final filter entry."""
        client, mock_get_model = final_client_with_mocked_request
        mock_get_model.return_value = mock_petition_response_with_data
        post_body: dict[str, Any] = {"q": "applicationNumberText:17765301"}

        client.search_decisions(post_body=post_body)

        mock_get_model.assert_called_once_with(
            method="POST",
            endpoint="api/v1/petition/decisions/search",
            json_data={
                "q": "applicationNumberText:17765301",
                "filters": [
                    {"name": "finalPetitionDecisionIndicator", "value": ["true"]}
                ],
            },
            params=None,
            response_class=PetitionDecisionResponse,
        )
        assert post_body == {"q": "applicationNumberText:17765301"}

    def test_search_post_with_none_filters_adds_final_filter_entry(
        self,
        final_client_with_mocked_request: tuple[
            FinalPetitionDecisionsClient, MagicMock
        ],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test a POST body with filters=None gets only the final filter entry."""
        client, mock_get_model = final_client_with_mocked_request
        mock_get_model.return_value = mock_petition_response_with_data
        post_body: dict[str, Any] = {
            "q": "applicationNumberText:17765301",
            "filters": None,
        }

        client.search_decisions(post_body=post_body)

        mock_get_model.assert_called_once_with(
            method="POST",
            endpoint="api/v1/petition/decisions/search",
            json_data={
                "q": "applicationNumberText:17765301",
                "filters": [
                    {"name": "finalPetitionDecisionIndicator", "value": ["true"]}
                ],
            },
            params=None,
            response_class=PetitionDecisionResponse,
        )
        assert post_body == {"q": "applicationNumberText:17765301", "filters": None}

    def test_search_post_with_filters_appends_final_filter_entry(
        self,
        final_client_with_mocked_request: tuple[
            FinalPetitionDecisionsClient, MagicMock
        ],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test the final filter entry follows the caller's, without mutating them."""
        client, mock_get_model = final_client_with_mocked_request
        mock_get_model.return_value = mock_petition_response_with_data
        caller_filters = [{"name": "technologyCenter", "value": ["1700"]}]
        post_body: dict[str, Any] = {
            "q": "decidedPetitionTypeCode:C",
            "filters": caller_filters,
        }

        client.search_decisions(post_body=post_body)

        mock_get_model.assert_called_once_with(
            method="POST",
            endpoint="api/v1/petition/decisions/search",
            json_data={
                "q": "decidedPetitionTypeCode:C",
                "filters": [
                    {"name": "technologyCenter", "value": ["1700"]},
                    {"name": "finalPetitionDecisionIndicator", "value": ["true"]},
                ],
            },
            params=None,
            response_class=PetitionDecisionResponse,
        )
        assert post_body["filters"] is caller_filters
        assert caller_filters == [{"name": "technologyCenter", "value": ["1700"]}]

    def test_search_post_leaves_query_params_unchanged(
        self,
        final_client_with_mocked_request: tuple[
            FinalPetitionDecisionsClient, MagicMock
        ],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test POST puts the final filter in the body, not the query params."""
        client, mock_get_model = final_client_with_mocked_request
        mock_get_model.return_value = mock_petition_response_with_data

        client.search_decisions(
            post_body={"q": "applicationNumberText:17765301"},
            additional_query_params={"customParam": "customValue"},
        )

        mock_get_model.assert_called_once_with(
            method="POST",
            endpoint="api/v1/petition/decisions/search",
            json_data={
                "q": "applicationNumberText:17765301",
                "filters": [
                    {"name": "finalPetitionDecisionIndicator", "value": ["true"]}
                ],
            },
            params={"customParam": "customValue"},
            response_class=PetitionDecisionResponse,
        )

    def test_download_json_adds_final_filter(
        self,
        final_client_with_mocked_request: tuple[
            FinalPetitionDecisionsClient, MagicMock
        ],
    ) -> None:
        """Test a JSON download sends the caller's filter plus the final filter."""
        client, mock_get_model = final_client_with_mocked_request
        download_response = PetitionDecisionDownloadResponse(petition_decision_data=[])
        mock_get_model.return_value = download_response

        result = client.download_decisions(
            format="json",
            application_number_q="17765301",
            filters="technologyCenter 1700",
        )

        mock_get_model.assert_called_once_with(
            method="GET",
            endpoint="api/v1/petition/decisions/search/download",
            response_class=PetitionDecisionDownloadResponse,
            params={
                "format": "json",
                "q": "applicationNumberText:17765301",
                "filters": [
                    "technologyCenter 1700",
                    "finalPetitionDecisionIndicator true",
                ],
            },
        )
        assert result is download_response

    def test_download_csv_adds_final_filter(
        self, final_petition_client: FinalPetitionDecisionsClient
    ) -> None:
        """Test a CSV download streams with the final filter in its params."""
        mock_response = MagicMock(spec=requests.Response)

        with patch.object(
            final_petition_client, "_stream_request", autospec=True
        ) as mock_stream_request:
            mock_stream_request.return_value = mock_response
            result = final_petition_client.download_decisions(
                format="csv", decision_date_from_q="2023-01-01"
            )

        mock_stream_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/petition/decisions/search/download",
            params={
                "format": "csv",
                "q": "decisionDate:>=2023-01-01",
                "filters": ["finalPetitionDecisionIndicator true"],
            },
        )
        assert result is mock_response

    def test_paginate_get_adds_final_filter_once_per_page(
        self,
        final_client_with_mocked_request: tuple[
            FinalPetitionDecisionsClient, MagicMock
        ],
        mock_final_decision_pages: list[PetitionDecisionResponse],
    ) -> None:
        """Test every GET page carries the final filter exactly once."""
        client, mock_get_model = final_client_with_mocked_request
        mock_get_model.side_effect = mock_final_decision_pages

        results = list(client.paginate_decisions(technology_center_q="1700", limit=2))

        assert [r.petition_decision_record_identifier for r in results] == [
            "Final-Record-01",
            "Final-Record-02",
            "Final-Record-03",
        ]
        assert mock_get_model.call_args_list == [
            call(
                method="GET",
                endpoint="api/v1/petition/decisions/search",
                response_class=PetitionDecisionResponse,
                params={
                    "q": "technologyCenter:1700",
                    "sort": ["petitionDecisionRecordIdentifier asc"],
                    "offset": offset,
                    "limit": 2,
                    "filters": ["finalPetitionDecisionIndicator true"],
                },
            )
            for offset in (0, 2)
        ]

    def test_paginate_get_does_not_stack_filters_on_reused_caller_list(
        self,
        final_client_with_mocked_request: tuple[
            FinalPetitionDecisionsClient, MagicMock
        ],
        mock_final_decision_pages: list[PetitionDecisionResponse],
    ) -> None:
        """Test a caller filters list reused for every page is never extended."""
        client, mock_get_model = final_client_with_mocked_request
        mock_get_model.side_effect = mock_final_decision_pages
        caller_filters = ["technologyCenter 1700"]

        results = list(
            client.paginate_decisions(
                query="decidedPetitionTypeCode:C",
                limit=2,
                additional_query_params={"filters": caller_filters},
            )
        )

        assert len(results) == 3
        assert mock_get_model.call_args_list == [
            call(
                method="GET",
                endpoint="api/v1/petition/decisions/search",
                response_class=PetitionDecisionResponse,
                params={
                    "q": "decidedPetitionTypeCode:C",
                    "sort": ["petitionDecisionRecordIdentifier asc"],
                    "offset": offset,
                    "limit": 2,
                    "filters": [
                        "technologyCenter 1700",
                        "finalPetitionDecisionIndicator true",
                    ],
                },
            )
            for offset in (0, 2)
        ]
        assert caller_filters == ["technologyCenter 1700"]

    def test_paginate_post_adds_final_filter_once_per_page(
        self,
        final_client_with_mocked_request: tuple[
            FinalPetitionDecisionsClient, MagicMock
        ],
        mock_final_decision_pages: list[PetitionDecisionResponse],
    ) -> None:
        """Test every POST page body carries the final filter exactly once."""
        client, mock_get_model = final_client_with_mocked_request
        mock_get_model.side_effect = mock_final_decision_pages
        caller_filters = [{"name": "technologyCenter", "value": ["1700"]}]
        post_body: dict[str, Any] = {
            "q": "decidedPetitionTypeCode:C",
            "pagination": {"limit": 2},
            "filters": caller_filters,
        }

        results = list(client.paginate_decisions(post_body=post_body))

        assert [r.petition_decision_record_identifier for r in results] == [
            "Final-Record-01",
            "Final-Record-02",
            "Final-Record-03",
        ]
        assert mock_get_model.call_args_list == [
            call(
                method="POST",
                endpoint="api/v1/petition/decisions/search",
                response_class=PetitionDecisionResponse,
                json_data={
                    "q": "decidedPetitionTypeCode:C",
                    "pagination": {"limit": 2, "offset": offset},
                    "sort": [
                        {"field": "petitionDecisionRecordIdentifier", "order": "asc"}
                    ],
                    "filters": [
                        {"name": "technologyCenter", "value": ["1700"]},
                        {"name": "finalPetitionDecisionIndicator", "value": ["true"]},
                    ],
                },
                params=None,
            )
            for offset in (0, 2)
        ]
        assert post_body == {
            "q": "decidedPetitionTypeCode:C",
            "pagination": {"limit": 2},
            "filters": [{"name": "technologyCenter", "value": ["1700"]}],
        }
        assert post_body["filters"] is caller_filters

    def test_get_decision_by_id_returns_final_decision(
        self,
        final_client_with_mocked_request: tuple[
            FinalPetitionDecisionsClient, MagicMock
        ],
        mock_final_petition_decision: PetitionDecision,
    ) -> None:
        """Test a final decision looked up by ID is returned."""
        client, mock_get_model = final_client_with_mocked_request
        mock_get_model.return_value = PetitionDecisionResponse(
            count=1, petition_decision_data_bag=[mock_final_petition_decision]
        )
        record_id = "1a552446-1d2b-570a-9bb6-b4fef39b0a91"

        result = client.get_decision_by_id(record_id)

        mock_get_model.assert_called_once_with(
            method="GET",
            endpoint=f"api/v1/petition/decisions/{record_id}",
            params=None,
            response_class=PetitionDecisionResponse,
        )
        assert result is mock_final_petition_decision

    @pytest.mark.parametrize(
        "indicator", [False, None], ids=["indicator_false", "indicator_none"]
    )
    def test_get_decision_by_id_returns_none_for_non_final_decision(
        self,
        final_client_with_mocked_request: tuple[
            FinalPetitionDecisionsClient, MagicMock
        ],
        indicator: bool | None,
    ) -> None:
        """Test a decision whose final indicator is not True is not returned."""
        client, mock_get_model = final_client_with_mocked_request
        record_id = "0b9ea48d-43c9-5197-8bf1-126d965816a7"
        mock_get_model.return_value = PetitionDecisionResponse(
            count=1,
            petition_decision_data_bag=[
                PetitionDecision(
                    petition_decision_record_identifier=record_id,
                    final_petition_decision_indicator=indicator,
                )
            ],
        )

        result = client.get_decision_by_id(record_id)

        mock_get_model.assert_called_once_with(
            method="GET",
            endpoint=f"api/v1/petition/decisions/{record_id}",
            params=None,
            response_class=PetitionDecisionResponse,
        )
        assert result is None

    def test_get_decision_by_id_not_found(
        self,
        final_client_with_mocked_request: tuple[
            FinalPetitionDecisionsClient, MagicMock
        ],
        mock_petition_response_empty: PetitionDecisionResponse,
    ) -> None:
        """Test an empty response returns None."""
        client, mock_get_model = final_client_with_mocked_request
        mock_get_model.return_value = mock_petition_response_empty

        result = client.get_decision_by_id("nonexistent-id")

        mock_get_model.assert_called_once_with(
            method="GET",
            endpoint="api/v1/petition/decisions/nonexistent-id",
            params=None,
            response_class=PetitionDecisionResponse,
        )
        assert result is None


class TestPetitionDecisionsClientWithoutFixedFilters:
    """Tests that the base PetitionDecisionsClient adds no fixed filters."""

    def test_search_get_without_filters_sends_no_filters(
        self,
        client_with_mocked_request: tuple[PetitionDecisionsClient, MagicMock],
        mock_petition_response_empty: PetitionDecisionResponse,
    ) -> None:
        """Test a bare GET search sends no filters param."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_petition_response_empty

        client.search_decisions()

        mock_get_model.assert_called_once_with(
            method="GET",
            endpoint="api/v1/petition/decisions/search",
            params={"offset": 0, "limit": 25},
            response_class=PetitionDecisionResponse,
        )

    def test_search_post_without_filters_sends_body_unchanged(
        self,
        client_with_mocked_request: tuple[PetitionDecisionsClient, MagicMock],
        mock_petition_response_empty: PetitionDecisionResponse,
    ) -> None:
        """Test a POST body without filters is sent as given."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_petition_response_empty
        post_body: dict[str, Any] = {"q": "applicationNumberText:17765301"}

        client.search_decisions(post_body=post_body)

        mock_get_model.assert_called_once_with(
            method="POST",
            endpoint="api/v1/petition/decisions/search",
            json_data={"q": "applicationNumberText:17765301"},
            params=None,
            response_class=PetitionDecisionResponse,
        )
        assert post_body == {"q": "applicationNumberText:17765301"}

    def test_download_without_filters_sends_no_filters(
        self,
        client_with_mocked_request: tuple[PetitionDecisionsClient, MagicMock],
    ) -> None:
        """Test a JSON download sends no filters param."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = PetitionDecisionDownloadResponse(
            petition_decision_data=[]
        )

        client.download_decisions(format="json")

        mock_get_model.assert_called_once_with(
            method="GET",
            endpoint="api/v1/petition/decisions/search/download",
            response_class=PetitionDecisionDownloadResponse,
            params={"format": "json"},
        )


class TestPetitionDecisionsClientExports:
    """Tests for the public exports of the petition decision clients."""

    def test_exported_from_pyuspto(self) -> None:
        """Test both clients are exported from the top-level package."""
        assert pyUSPTO.PetitionDecisionsClient is PetitionDecisionsClient
        assert pyUSPTO.FinalPetitionDecisionsClient is FinalPetitionDecisionsClient
        assert "PetitionDecisionsClient" in pyUSPTO.__all__
        assert "FinalPetitionDecisionsClient" in pyUSPTO.__all__

    def test_exported_from_pyuspto_clients(self) -> None:
        """Test both clients are exported from pyUSPTO.clients."""
        assert pyUSPTO.clients.PetitionDecisionsClient is PetitionDecisionsClient
        assert (
            pyUSPTO.clients.FinalPetitionDecisionsClient is FinalPetitionDecisionsClient
        )
        assert "PetitionDecisionsClient" in pyUSPTO.clients.__all__
        assert "FinalPetitionDecisionsClient" in pyUSPTO.clients.__all__

    def test_final_client_is_petition_decisions_client_subclass(self) -> None:
        """Test FinalPetitionDecisionsClient subclasses PetitionDecisionsClient."""
        assert issubclass(FinalPetitionDecisionsClient, PetitionDecisionsClient)
