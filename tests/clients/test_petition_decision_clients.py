"""
Tests for the pyUSPTO.clients.petition_decisions.FinalPetitionDecisionsClient.

This module contains comprehensive tests for initialization, search functionality,
retrieval, pagination, and document downloads.
"""

from typing import Any, Dict, Iterator
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests

from pyUSPTO.clients.petition_decisions import FinalPetitionDecisionsClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.petition_decisions import (
    DocumentDownloadOption,
    PetitionDecision,
    PetitionDecisionDownloadResponse,
    PetitionDecisionResponse,
)


# --- Fixtures ---


@pytest.fixture
def api_key_fixture() -> str:
    """Provides a test API key."""
    return "test_key"


@pytest.fixture
def petition_client(api_key_fixture: str) -> FinalPetitionDecisionsClient:
    """Provides a FinalPetitionDecisionsClient instance."""
    return FinalPetitionDecisionsClient(api_key=api_key_fixture)


@pytest.fixture
def mock_petition_decision() -> PetitionDecision:
    """Provides a mock PetitionDecision instance."""
    return PetitionDecision(
        petition_decision_record_identifier="9f1a4a2b-eee1-58ec-a3aa-167c4075aed4",
        application_number_text="17765301",
        decision_type_code="C",
        decision_type_code_description_text="DENIED",
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
    petition_client: FinalPetitionDecisionsClient,
) -> Iterator[tuple[FinalPetitionDecisionsClient, MagicMock]]:
    """Provides a client with mocked _make_request method."""
    with patch.object(
        petition_client, "_make_request", autospec=True
    ) as mock_make_request:
        yield petition_client, mock_make_request


@pytest.fixture
def mock_download_option() -> DocumentDownloadOption:
    """Provides a mock DocumentDownloadOption."""
    return DocumentDownloadOption(
        mime_type_identifier="PDF",
        download_url="https://api.test.uspto.gov/api/v1/download/test.pdf",
        page_total_quantity=10,
    )


# --- Test Classes ---


class TestFinalPetitionDecisionsClientInit:
    """Tests for initialization of FinalPetitionDecisionsClient."""

    def test_init_with_api_key(self, api_key_fixture: str) -> None:
        """Test initialization with API key."""
        client = FinalPetitionDecisionsClient(api_key=api_key_fixture)
        assert client.api_key == api_key_fixture
        assert client.base_url == "https://api.uspto.gov"

    def test_init_with_custom_base_url(self, api_key_fixture: str) -> None:
        """Test initialization with custom base URL."""
        custom_url = "https://custom.api.test.com"
        client = FinalPetitionDecisionsClient(
            api_key=api_key_fixture, base_url=custom_url
        )
        assert client.api_key == api_key_fixture
        assert client.base_url == custom_url

    def test_init_with_config(self) -> None:
        """Test initialization with config object."""
        config_key = "config_key"
        config_url = "https://config.api.test.com"
        config = USPTOConfig(api_key=config_key, petition_decisions_base_url=config_url)
        client = FinalPetitionDecisionsClient(config=config)
        assert client.api_key == config_key
        assert client.base_url == config_url
        assert client.config is config

    def test_init_with_api_key_and_config(self, api_key_fixture: str) -> None:
        """Test initialization with both API key and config."""
        config = USPTOConfig(
            api_key="config_key",
            petition_decisions_base_url="https://config.api.test.com",
        )
        client = FinalPetitionDecisionsClient(api_key=api_key_fixture, config=config)
        # API key parameter takes precedence
        assert client.api_key == api_key_fixture
        # But base_url comes from config
        assert client.base_url == "https://config.api.test.com"

    def test_init_base_url_precedence(self, api_key_fixture: str) -> None:
        """Test that explicit base_url takes precedence over config."""
        config = USPTOConfig(
            api_key="config_key",
            petition_decisions_base_url="https://config.api.test.com",
        )
        custom_url = "https://custom.url.com"
        client = FinalPetitionDecisionsClient(
            api_key=api_key_fixture, base_url=custom_url, config=config
        )
        assert client.base_url == custom_url


class TestFinalPetitionDecisionsClientSearch:
    """Tests for search_decisions method."""

    def test_search_get_direct_query(
        self,
        client_with_mocked_request: tuple[FinalPetitionDecisionsClient, MagicMock],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test search with direct query string."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_petition_response_with_data

        result = client.search_decisions(query="Test", limit=10, offset=0)

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/petition/decisions/search",
            params={"q": "Test", "limit": 10, "offset": 0},
            response_class=PetitionDecisionResponse,
        )
        assert result is mock_petition_response_with_data

    def test_search_with_application_number(
        self,
        client_with_mocked_request: tuple[FinalPetitionDecisionsClient, MagicMock],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test search with application number convenience parameter."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_petition_response_with_data

        result = client.search_decisions(application_number_q="17765301", limit=25)

        expected_params = {
            "q": "applicationNumberText:17765301",
            "limit": 25,
            "offset": 0,
        }
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/petition/decisions/search",
            params=expected_params,
            response_class=PetitionDecisionResponse,
        )
        assert result is mock_petition_response_with_data

    def test_search_with_date_range(
        self,
        client_with_mocked_request: tuple[FinalPetitionDecisionsClient, MagicMock],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test search with date range."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_petition_response_with_data

        result = client.search_decisions(
            decision_date_from_q="2022-01-01",
            decision_date_to_q="2022-12-31",
            limit=25,
        )

        expected_params = {
            "q": "decisionDate:[2022-01-01 TO 2022-12-31]",
            "limit": 25,
            "offset": 0,
        }
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/petition/decisions/search",
            params=expected_params,
            response_class=PetitionDecisionResponse,
        )

    def test_search_with_multiple_params(
        self,
        client_with_mocked_request: tuple[FinalPetitionDecisionsClient, MagicMock],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test search combining multiple parameters."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_petition_response_with_data

        result = client.search_decisions(
            applicant_name_q="Test Corp",
            technology_center_q="1700",
            decision_type_code_q="C",
            limit=50,
        )

        # Check that the query contains all three conditions joined with AND
        call_args = mock_make_request.call_args
        params = call_args[1]["params"]
        assert "q" in params
        query = params["q"]
        assert "firstApplicantName:Test Corp" in query
        assert "technologyCenter:1700" in query
        assert "decisionTypeCode:C" in query
        assert " AND " in query
        assert params["limit"] == 50

    def test_search_post_request(
        self,
        client_with_mocked_request: tuple[FinalPetitionDecisionsClient, MagicMock],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test search with POST body."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_petition_response_with_data

        post_body = {"q": "technologyCenter:1700", "limit": 100}
        result = client.search_decisions(post_body=post_body)

        mock_make_request.assert_called_once_with(
            method="POST",
            endpoint="api/v1/petition/decisions/search",
            json_data=post_body,
            params=None,
            response_class=PetitionDecisionResponse,
        )

    def test_search_with_patent_number(
        self,
        client_with_mocked_request: tuple[FinalPetitionDecisionsClient, MagicMock],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test search with patent_number_q parameter."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_petition_response_with_data

        client.search_decisions(patent_number_q="10123456")

        call_args = mock_make_request.call_args
        params = call_args[1]["params"]
        assert "patentNumber:10123456" in params["q"]

    def test_search_with_inventor_name(
        self,
        client_with_mocked_request: tuple[FinalPetitionDecisionsClient, MagicMock],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test search with inventor_name_q parameter."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_petition_response_with_data

        client.search_decisions(inventor_name_q="John Doe")

        call_args = mock_make_request.call_args
        params = call_args[1]["params"]
        assert "inventorBag:John Doe" in params["q"]

    def test_search_with_invention_title(
        self,
        client_with_mocked_request: tuple[FinalPetitionDecisionsClient, MagicMock],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test search with invention_title_q parameter."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_petition_response_with_data

        client.search_decisions(invention_title_q="Test Invention")

        call_args = mock_make_request.call_args
        params = call_args[1]["params"]
        assert "inventionTitle:Test Invention" in params["q"]

    def test_search_with_final_deciding_office_name(
        self,
        client_with_mocked_request: tuple[FinalPetitionDecisionsClient, MagicMock],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test search with final_deciding_office_name_q parameter."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_petition_response_with_data

        client.search_decisions(final_deciding_office_name_q="TC Director")

        call_args = mock_make_request.call_args
        params = call_args[1]["params"]
        assert "finalDecidingOfficeName:TC Director" in params["q"]

    def test_search_with_decision_date_from_only(
        self,
        client_with_mocked_request: tuple[FinalPetitionDecisionsClient, MagicMock],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test search with only decision_date_from_q parameter."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_petition_response_with_data

        client.search_decisions(decision_date_from_q="2023-01-01")

        call_args = mock_make_request.call_args
        params = call_args[1]["params"]
        assert "decisionDate:>=2023-01-01" in params["q"]

    def test_search_with_decision_date_to_only(
        self,
        client_with_mocked_request: tuple[FinalPetitionDecisionsClient, MagicMock],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test search with only decision_date_to_q parameter."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_petition_response_with_data

        client.search_decisions(decision_date_to_q="2023-12-31")

        call_args = mock_make_request.call_args
        params = call_args[1]["params"]
        assert "decisionDate:<=2023-12-31" in params["q"]

    def test_search_with_petition_mail_date_from_only(
        self,
        client_with_mocked_request: tuple[FinalPetitionDecisionsClient, MagicMock],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test search with only petition_mail_date_from_q parameter."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_petition_response_with_data

        client.search_decisions(petition_mail_date_from_q="2023-01-01")

        call_args = mock_make_request.call_args
        params = call_args[1]["params"]
        assert "petitionMailDate:>=2023-01-01" in params["q"]

    def test_search_with_petition_mail_date_to_only(
        self,
        client_with_mocked_request: tuple[FinalPetitionDecisionsClient, MagicMock],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test search with only petition_mail_date_to_q parameter."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_petition_response_with_data

        client.search_decisions(petition_mail_date_to_q="2023-12-31")

        call_args = mock_make_request.call_args
        params = call_args[1]["params"]
        assert "petitionMailDate:<=2023-12-31" in params["q"]

    def test_search_with_petition_mail_date_range(
        self,
        client_with_mocked_request: tuple[FinalPetitionDecisionsClient, MagicMock],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test search with petition mail date range."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_petition_response_with_data

        client.search_decisions(
            petition_mail_date_from_q="2023-01-01",
            petition_mail_date_to_q="2023-12-31",
        )

        call_args = mock_make_request.call_args
        params = call_args[1]["params"]
        assert "petitionMailDate:[2023-01-01 TO 2023-12-31]" in params["q"]

    def test_search_with_optional_params(
        self,
        client_with_mocked_request: tuple[FinalPetitionDecisionsClient, MagicMock],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test search with optional sort, facets, fields, filters, and range_filters."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_petition_response_with_data

        client.search_decisions(
            query="test",
            sort="decisionDate desc",
            facets="technologyCenter",
            fields="applicationNumberText,patentNumber",
            filters="decisionTypeCode:GRANT",
            range_filters="decisionDate:[2020 TO 2024]",
        )

        call_args = mock_make_request.call_args
        params = call_args[1]["params"]
        assert params["sort"] == "decisionDate desc"
        assert params["facets"] == "technologyCenter"
        assert params["fields"] == "applicationNumberText,patentNumber"
        assert params["filters"] == "decisionTypeCode:GRANT"
        assert params["rangeFilters"] == "decisionDate:[2020 TO 2024]"

    def test_search_with_additional_query_params(
        self,
        client_with_mocked_request: tuple[FinalPetitionDecisionsClient, MagicMock],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test search with additional_query_params."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_petition_response_with_data

        client.search_decisions(
            query="test", additional_query_params={"customParam": "customValue"}
        )

        call_args = mock_make_request.call_args
        params = call_args[1]["params"]
        assert params["customParam"] == "customValue"


class TestFinalPetitionDecisionsClientGetById:
    """Tests for get_decision_by_id method."""

    def test_get_decision_by_id(
        self,
        client_with_mocked_request: tuple[FinalPetitionDecisionsClient, MagicMock],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test retrieving decision by ID."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_petition_response_with_data

        record_id = "9f1a4a2b-eee1-58ec-a3aa-167c4075aed4"
        result = client.get_decision_by_id(record_id)

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint=f"api/v1/petition/decisions/{record_id}",
            params=None,
            response_class=PetitionDecisionResponse,
        )
        assert result is not None
        assert result.petition_decision_record_identifier == record_id

    def test_get_decision_by_id_with_documents(
        self,
        client_with_mocked_request: tuple[FinalPetitionDecisionsClient, MagicMock],
        mock_petition_response_with_data: PetitionDecisionResponse,
    ) -> None:
        """Test retrieving decision by ID with includeDocuments parameter."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_petition_response_with_data

        record_id = "9f1a4a2b-eee1-58ec-a3aa-167c4075aed4"
        result = client.get_decision_by_id(record_id, include_documents=True)

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint=f"api/v1/petition/decisions/{record_id}",
            params={"includeDocuments": "true"},
            response_class=PetitionDecisionResponse,
        )
        assert result is not None

    def test_get_decision_by_id_not_found(
        self,
        client_with_mocked_request: tuple[FinalPetitionDecisionsClient, MagicMock],
        mock_petition_response_empty: PetitionDecisionResponse,
    ) -> None:
        """Test retrieving non-existent decision returns None."""
        client, mock_make_request = client_with_mocked_request
        mock_make_request.return_value = mock_petition_response_empty

        result = client.get_decision_by_id("nonexistent-id")
        assert result is None


class TestFinalPetitionDecisionsClientDownload:
    """Tests for download_decisions method."""

    def test_download_json(
        self,
        client_with_mocked_request: tuple[FinalPetitionDecisionsClient, MagicMock],
    ) -> None:
        """Test downloading decisions in JSON format."""
        client, mock_make_request = client_with_mocked_request

        mock_dict = {"petitionDecisionData": [{"applicationNumberText": "12345678"}]}
        mock_make_request.return_value = mock_dict

        result = client.download_decisions(format="json", applicant_name_q="Test Corp")

        assert isinstance(result, PetitionDecisionDownloadResponse)
        assert len(result.petition_decision_data) == 1

        call_args = mock_make_request.call_args
        params = call_args[1]["params"]
        assert params["format"] == "json"
        assert "firstApplicantName:Test Corp" in params.get("q", "")

    def test_download_csv(
        self,
        client_with_mocked_request: tuple[FinalPetitionDecisionsClient, MagicMock],
    ) -> None:
        """Test downloading decisions in CSV format as streaming response."""
        client, mock_make_request = client_with_mocked_request

        mock_response = MagicMock(spec=requests.Response)
        mock_response.iter_content.return_value = [b"csv,data"]
        mock_make_request.return_value = mock_response

        result = client.download_decisions(format="csv")

        assert isinstance(result, requests.Response)
        mock_make_request.assert_called_once()
        call_args = mock_make_request.call_args
        assert call_args[1]["stream"] is True

    def test_download_csv_to_file(
        self,
        petition_client: FinalPetitionDecisionsClient,
        tmp_path,
    ) -> None:
        """Test downloading decisions in CSV format and saving to file."""
        # Mock both _make_request and _save_response_to_file
        mock_response = Mock(spec=requests.Response)
        expected_path = str(tmp_path / "petition_decisions.csv")

        with (
            patch.object(
                petition_client, "_make_request", return_value=mock_response
            ) as mock_make_request,
            patch.object(
                petition_client, "_save_response_to_file", return_value=expected_path
            ) as mock_save,
        ):
            result = petition_client.download_decisions(
                format="csv",
                decision_date_from_q="2023-01-01",
                decision_date_to_q="2023-12-31",
                destination_path=str(tmp_path),
            )

            assert result == expected_path
            mock_make_request.assert_called_once()
            mock_save.assert_called_once()

            # Verify _save_response_to_file was called with correct arguments
            save_call_args = mock_save.call_args
            assert save_call_args[1]["response"] == mock_response
            assert save_call_args[1]["file_path"] == expected_path

    def test_download_with_patent_number(
        self,
        client_with_mocked_request: tuple[FinalPetitionDecisionsClient, MagicMock],
    ) -> None:
        """Test download with patent_number_q parameter."""
        client, mock_make_request = client_with_mocked_request
        mock_dict = {"petitionDecisionData": []}
        mock_make_request.return_value = mock_dict

        client.download_decisions(format="json", patent_number_q="10123456")

        call_args = mock_make_request.call_args
        params = call_args[1]["params"]
        assert "patentNumber:10123456" in params["q"]

    def test_download_with_application_number(
        self,
        client_with_mocked_request: tuple[FinalPetitionDecisionsClient, MagicMock],
    ) -> None:
        """Test download with application_number_q parameter."""
        client, mock_make_request = client_with_mocked_request
        mock_dict = {"petitionDecisionData": []}
        mock_make_request.return_value = mock_dict

        client.download_decisions(format="json", application_number_q="17765301")

        call_args = mock_make_request.call_args
        params = call_args[1]["params"]
        assert "applicationNumberText:17765301" in params["q"]

    def test_download_with_inventor_name(
        self,
        client_with_mocked_request: tuple[FinalPetitionDecisionsClient, MagicMock],
    ) -> None:
        """Test download with inventor_name_q parameter."""
        client, mock_make_request = client_with_mocked_request
        mock_dict = {"petitionDecisionData": []}
        mock_make_request.return_value = mock_dict

        client.download_decisions(format="json", inventor_name_q="Jane Doe")

        call_args = mock_make_request.call_args
        params = call_args[1]["params"]
        assert "inventorBag:Jane Doe" in params["q"]

    def test_download_with_decision_date_from_only(
        self,
        client_with_mocked_request: tuple[FinalPetitionDecisionsClient, MagicMock],
    ) -> None:
        """Test download with only decision_date_from_q parameter."""
        client, mock_make_request = client_with_mocked_request
        mock_dict = {"petitionDecisionData": []}
        mock_make_request.return_value = mock_dict

        client.download_decisions(format="json", decision_date_from_q="2023-01-01")

        call_args = mock_make_request.call_args
        params = call_args[1]["params"]
        assert "decisionDate:>=2023-01-01" in params["q"]

    def test_download_with_decision_date_to_only(
        self,
        client_with_mocked_request: tuple[FinalPetitionDecisionsClient, MagicMock],
    ) -> None:
        """Test download with only decision_date_to_q parameter."""
        client, mock_make_request = client_with_mocked_request
        mock_dict = {"petitionDecisionData": []}
        mock_make_request.return_value = mock_dict

        client.download_decisions(format="json", decision_date_to_q="2023-12-31")

        call_args = mock_make_request.call_args
        params = call_args[1]["params"]
        assert "decisionDate:<=2023-12-31" in params["q"]

    def test_download_with_optional_params(
        self,
        client_with_mocked_request: tuple[FinalPetitionDecisionsClient, MagicMock],
    ) -> None:
        """Test download with optional sort, fields, filters, and range_filters."""
        client, mock_make_request = client_with_mocked_request
        mock_dict = {"petitionDecisionData": []}
        mock_make_request.return_value = mock_dict

        client.download_decisions(
            format="json",
            query="test",
            sort="decisionDate desc",
            fields="applicationNumberText",
            filters="decisionTypeCode:GRANT",
            range_filters="decisionDate:[2020 TO 2024]",
        )

        call_args = mock_make_request.call_args
        params = call_args[1]["params"]
        assert params["sort"] == "decisionDate desc"
        assert params["fields"] == "applicationNumberText"
        assert params["filters"] == "decisionTypeCode:GRANT"
        assert params["rangeFilters"] == "decisionDate:[2020 TO 2024]"

    def test_download_with_offset_and_limit(
        self,
        client_with_mocked_request: tuple[FinalPetitionDecisionsClient, MagicMock],
    ) -> None:
        """Test download with offset and limit parameters."""
        client, mock_make_request = client_with_mocked_request
        mock_dict = {"petitionDecisionData": []}
        mock_make_request.return_value = mock_dict

        client.download_decisions(format="json", offset=50, limit=100)

        call_args = mock_make_request.call_args
        params = call_args[1]["params"]
        assert params["offset"] == 50
        assert params["limit"] == 100

    def test_download_with_additional_query_params(
        self,
        client_with_mocked_request: tuple[FinalPetitionDecisionsClient, MagicMock],
    ) -> None:
        """Test download with additional_query_params."""
        client, mock_make_request = client_with_mocked_request
        mock_dict = {"petitionDecisionData": []}
        mock_make_request.return_value = mock_dict

        client.download_decisions(
            format="json", additional_query_params={"customParam": "customValue"}
        )

        call_args = mock_make_request.call_args
        params = call_args[1]["params"]
        assert params["customParam"] == "customValue"


class TestFinalPetitionDecisionsClientPagination:
    """Tests for paginate_decisions method."""

    def test_paginate_decisions(
        self, petition_client: FinalPetitionDecisionsClient
    ) -> None:
        """Test pagination through decisions."""
        # Mock multiple pages of results
        page1 = PetitionDecisionResponse(
            count=2,
            petition_decision_data_bag=[
                PetitionDecision(application_number_text="111"),
                PetitionDecision(application_number_text="222"),
            ],
        )
        page2 = PetitionDecisionResponse(
            count=1,
            petition_decision_data_bag=[
                PetitionDecision(application_number_text="333"),
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

    def test_paginate_decisions_rejects_post_body(
        self, petition_client: FinalPetitionDecisionsClient
    ) -> None:
        """Test that pagination raises error with post_body."""
        with pytest.raises(ValueError, match="does not support 'post_body'"):
            list(petition_client.paginate_decisions(post_body={"q": "test"}))


class TestFinalPetitionDecisionsClientDocumentDownload:
    """Tests for download_petition_document method."""

    def test_download_document_success(
        self,
        petition_client: FinalPetitionDecisionsClient,
        mock_download_option: DocumentDownloadOption,
    ) -> None:
        """Test successful document download."""
        with patch.object(petition_client, "_download_file") as mock_download:
            mock_download.return_value = "/path/to/test.pdf"

            result = petition_client.download_petition_document(
                mock_download_option, destination_path="/tmp"
            )

            assert result == "/path/to/test.pdf"
            mock_download.assert_called_once()
            call_args = mock_download.call_args
            # The filename is extracted from the URL which ends in "test.pdf"
            assert "test.pdf" in call_args[1]["file_path"]

    def test_download_document_no_url(
        self, petition_client: FinalPetitionDecisionsClient
    ) -> None:
        """Test download fails without URL."""
        option = DocumentDownloadOption(mime_type_identifier="PDF", download_url=None)

        with pytest.raises(ValueError, match="must have a download_url"):
            petition_client.download_petition_document(option)

    def test_download_document_file_exists(
        self,
        petition_client: FinalPetitionDecisionsClient,
        mock_download_option: DocumentDownloadOption,
        tmp_path: Any,
    ) -> None:
        """Test download fails if file exists and overwrite=False."""
        # Create an existing file
        existing_file = tmp_path / "document.pdf"
        existing_file.write_text("existing content")

        with pytest.raises(FileExistsError, match="File already exists"):
            petition_client.download_petition_document(
                mock_download_option,
                file_name="document.pdf",
                destination_path=str(tmp_path),
                overwrite=False,
            )

    def test_download_document_url_without_extension(
        self, petition_client: FinalPetitionDecisionsClient
    ) -> None:
        """Test download with URL that has no file extension generates filename from MIME type."""
        option = DocumentDownloadOption(
            mime_type_identifier="PDF",
            download_url="https://api.test.uspto.gov/api/v1/download/ABCD1234",
            page_total_quantity=5,
        )

        with patch.object(petition_client, "_download_file") as mock_download:
            mock_download.return_value = "/tmp/document.pdf"

            petition_client.download_petition_document(option, destination_path="/tmp")

            call_args = mock_download.call_args
            file_path = call_args[1]["file_path"]
            # Should generate filename with extension from MIME type
            assert "document.pdf" in file_path

    def test_download_document_url_without_extension_no_mime(
        self, petition_client: FinalPetitionDecisionsClient
    ) -> None:
        """Test download with URL without extension and no MIME type defaults to pdf."""
        option = DocumentDownloadOption(
            mime_type_identifier=None,
            download_url="https://api.test.uspto.gov/api/v1/download/XYZ9999",
            page_total_quantity=3,
        )

        with patch.object(petition_client, "_download_file") as mock_download:
            mock_download.return_value = "/tmp/document.pdf"

            petition_client.download_petition_document(option, destination_path="/tmp")

            call_args = mock_download.call_args
            file_path = call_args[1]["file_path"]
            # Should default to .pdf extension
            assert "document.pdf" in file_path

    def test_download_document_no_destination_path(
        self, petition_client: FinalPetitionDecisionsClient
    ) -> None:
        """Test download without destination_path saves to current directory."""
        option = DocumentDownloadOption(
            mime_type_identifier="PDF",
            download_url="https://api.test.uspto.gov/api/v1/download/test.pdf",
            page_total_quantity=10,
        )

        with patch.object(petition_client, "_download_file") as mock_download:
            mock_download.return_value = "test.pdf"

            result = petition_client.download_petition_document(option)

            call_args = mock_download.call_args
            file_path = call_args[1]["file_path"]
            # Should be just the filename without a directory path
            assert file_path == "test.pdf"


class TestFinalPetitionDecisionsClientHelpers:
    """Tests for helper methods."""

    def test_get_decision_from_response(
        self,
        petition_client: FinalPetitionDecisionsClient,
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
        petition_client: FinalPetitionDecisionsClient,
        mock_petition_response_empty: PetitionDecisionResponse,
    ) -> None:
        """Test _get_decision_from_response with empty response."""
        result = petition_client._get_decision_from_response(
            mock_petition_response_empty
        )
        assert result is None

    def test_get_decision_from_response_id_mismatch(
        self,
        petition_client: FinalPetitionDecisionsClient,
        mock_petition_response_with_data: PetitionDecisionResponse,
        capsys,
    ) -> None:
        """Test _get_decision_from_response with mismatched ID prints warning."""
        result = petition_client._get_decision_from_response(
            mock_petition_response_with_data,
            petition_decision_record_identifier_for_validation="different-id-12345",
        )
        assert result is not None

        # Capture stdout to verify warning was printed
        captured = capsys.readouterr()
        assert "Warning" in captured.out
        assert "different-id-12345" in captured.out
        assert "9f1a4a2b-eee1-58ec-a3aa-167c4075aed4" in captured.out
