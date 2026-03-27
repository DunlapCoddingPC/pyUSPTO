"""Tests for the pyUSPTO.clients.enriched_citations.EnrichedCitationsClient.

This module contains comprehensive tests for initialization, search functionality,
field retrieval, and pagination.
"""

from collections.abc import Iterator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from pyUSPTO.clients.enriched_citations import EnrichedCitationsClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.enriched_citations import (
    EnrichedCitation,
    EnrichedCitationFieldsResponse,
    EnrichedCitationResponse,
)


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
def enriched_client(uspto_config: USPTOConfig) -> EnrichedCitationsClient:
    """Provides an EnrichedCitationsClient instance."""
    return EnrichedCitationsClient(config=uspto_config)


@pytest.fixture
def mock_enriched_citation() -> EnrichedCitation:
    """Provides a mock EnrichedCitation instance."""
    return EnrichedCitation(
        id="d7e95803517f677b3875dc476a61a817",
        patent_application_number="15739603",
        cited_document_identifier="US 20190165601 A1",
        citation_category_code="Y",
        tech_center="2800",
        examiner_cited_reference_indicator=True,
    )


@pytest.fixture
def mock_enriched_response_with_data(
    mock_enriched_citation: EnrichedCitation,
) -> EnrichedCitationResponse:
    """Provides a mock EnrichedCitationResponse with data."""
    return EnrichedCitationResponse(
        num_found=1,
        start=0,
        docs=[mock_enriched_citation],
    )


@pytest.fixture
def mock_enriched_response_empty() -> EnrichedCitationResponse:
    """Provides an empty mock EnrichedCitationResponse."""
    return EnrichedCitationResponse(num_found=0, start=0, docs=[])


@pytest.fixture
def client_with_mocked_request(
    enriched_client: EnrichedCitationsClient,
) -> Iterator[tuple[EnrichedCitationsClient, MagicMock]]:
    """Provides a client with mocked _get_model method."""
    with patch.object(
        enriched_client, "_get_model", autospec=True
    ) as mock_get_model:
        yield enriched_client, mock_get_model


# --- Test Classes ---


class TestEnrichedCitationsClientInit:
    """Tests for initialization of EnrichedCitationsClient."""

    def test_init_with_config(
        self, enriched_client: EnrichedCitationsClient, uspto_config: USPTOConfig
    ) -> None:
        """Test initialization with config."""
        assert enriched_client._api_key == uspto_config.api_key
        assert enriched_client.base_url == "https://api.uspto.gov"

    def test_init_with_custom_base_url(self, uspto_config: USPTOConfig) -> None:
        """Test initialization with custom base URL."""
        custom_url = "https://custom.api.test.com"
        client = EnrichedCitationsClient(config=uspto_config, base_url=custom_url)
        assert client.base_url == custom_url

    def test_init_with_config_base_url(self) -> None:
        """Test initialization uses config's enriched_citations_base_url."""
        config_url = "https://config.api.test.com"
        config = USPTOConfig(
            api_key="config_key", enriched_citations_base_url=config_url
        )
        client = EnrichedCitationsClient(config=config)
        assert client._api_key == "config_key"
        assert client.base_url == config_url
        assert client.config is config

    def test_init_without_config(self, monkeypatch: Any) -> None:
        """Test initialization without config uses environment."""
        monkeypatch.setenv("USPTO_API_KEY", "env_key")
        client = EnrichedCitationsClient()
        assert client.config.api_key == "env_key"


class TestEnrichedCitationsClientSearch:
    """Tests for search_citations method."""

    def test_search_with_post_body(
        self,
        client_with_mocked_request: tuple[EnrichedCitationsClient, MagicMock],
        mock_enriched_response_with_data: EnrichedCitationResponse,
    ) -> None:
        """Test search with POST body passes it directly."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_enriched_response_with_data

        post_body = {"q": "techCenter:2800", "rows": 100}
        result = client.search_citations(post_body=post_body)

        mock_get_model.assert_called_once_with(
            method="POST",
            endpoint="api/v1/patent/oa/enriched_cited_reference_metadata/v3/records",
            json_data=post_body,
            params=None,
            response_class=EnrichedCitationResponse,
        )
        assert result is mock_enriched_response_with_data

    def test_search_with_query(
        self,
        client_with_mocked_request: tuple[EnrichedCitationsClient, MagicMock],
        mock_enriched_response_with_data: EnrichedCitationResponse,
    ) -> None:
        """Test search with direct query string."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_enriched_response_with_data

        result = client.search_citations(query="patentApplicationNumber:15739603")

        call_args = mock_get_model.call_args
        json_data = call_args[1]["json_data"]
        assert json_data["q"] == "patentApplicationNumber:15739603"
        assert json_data["offset"] == 0
        assert json_data["limit"] == 25

    def test_search_with_application_number(
        self,
        client_with_mocked_request: tuple[EnrichedCitationsClient, MagicMock],
        mock_enriched_response_with_data: EnrichedCitationResponse,
    ) -> None:
        """Test search with patent_application_number_q convenience parameter."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_enriched_response_with_data

        client.search_citations(patent_application_number_q="15739603")

        call_args = mock_get_model.call_args
        json_data = call_args[1]["json_data"]
        assert "patentApplicationNumber:15739603" in json_data["q"]

    def test_search_with_cited_document_identifier(
        self,
        client_with_mocked_request: tuple[EnrichedCitationsClient, MagicMock],
        mock_enriched_response_with_data: EnrichedCitationResponse,
    ) -> None:
        """Test search with cited_document_identifier_q (auto-quotes spaces)."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_enriched_response_with_data

        client.search_citations(cited_document_identifier_q="US 20190165601 A1")

        call_args = mock_get_model.call_args
        json_data = call_args[1]["json_data"]
        assert 'citedDocumentIdentifier:"US 20190165601 A1"' in json_data["q"]

    def test_search_with_multiple_params(
        self,
        client_with_mocked_request: tuple[EnrichedCitationsClient, MagicMock],
        mock_enriched_response_with_data: EnrichedCitationResponse,
    ) -> None:
        """Test search combining multiple convenience parameters."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_enriched_response_with_data

        client.search_citations(
            tech_center_q="2800",
            citation_category_code_q="X",
            examiner_cited_q=True,
            limit=50,
        )

        call_args = mock_get_model.call_args
        json_data = call_args[1]["json_data"]
        query = json_data["q"]
        assert "techCenter:2800" in query
        assert "citationCategoryCode:X" in query
        assert "examinerCitedReferenceIndicator:true" in query
        assert " AND " in query
        assert json_data["limit"] == 50

    def test_search_with_date_range(
        self,
        client_with_mocked_request: tuple[EnrichedCitationsClient, MagicMock],
        mock_enriched_response_with_data: EnrichedCitationResponse,
    ) -> None:
        """Test search with office action date range."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_enriched_response_with_data

        client.search_citations(
            office_action_date_from_q="2019-01-01",
            office_action_date_to_q="2019-12-31",
        )

        call_args = mock_get_model.call_args
        json_data = call_args[1]["json_data"]
        assert "officeActionDate:[2019-01-01 TO 2019-12-31]" in json_data["q"]

    def test_search_with_date_from_only(
        self,
        client_with_mocked_request: tuple[EnrichedCitationsClient, MagicMock],
        mock_enriched_response_with_data: EnrichedCitationResponse,
    ) -> None:
        """Test search with only a from date."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_enriched_response_with_data

        client.search_citations(office_action_date_from_q="2019-01-01")

        call_args = mock_get_model.call_args
        json_data = call_args[1]["json_data"]
        assert "officeActionDate:>=2019-01-01" in json_data["q"]

    def test_search_with_date_to_only(
        self,
        client_with_mocked_request: tuple[EnrichedCitationsClient, MagicMock],
        mock_enriched_response_with_data: EnrichedCitationResponse,
    ) -> None:
        """Test search with only a to date."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_enriched_response_with_data

        client.search_citations(office_action_date_to_q="2019-12-31")

        call_args = mock_get_model.call_args
        json_data = call_args[1]["json_data"]
        assert "officeActionDate:<=2019-12-31" in json_data["q"]

    def test_search_default_offset_limit(
        self,
        client_with_mocked_request: tuple[EnrichedCitationsClient, MagicMock],
        mock_enriched_response_with_data: EnrichedCitationResponse,
    ) -> None:
        """Test search applies default offset and limit."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_enriched_response_with_data

        client.search_citations(query="*:*")

        call_args = mock_get_model.call_args
        json_data = call_args[1]["json_data"]
        assert json_data["offset"] == 0
        assert json_data["limit"] == 25

    def test_search_with_sort(
        self,
        client_with_mocked_request: tuple[EnrichedCitationsClient, MagicMock],
        mock_enriched_response_with_data: EnrichedCitationResponse,
    ) -> None:
        """Test search with sort parameter."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_enriched_response_with_data

        client.search_citations(query="*:*", sort="officeActionDate desc")

        call_args = mock_get_model.call_args
        json_data = call_args[1]["json_data"]
        assert json_data["sort"] == "officeActionDate desc"

    def test_search_with_group_art_unit(
        self,
        client_with_mocked_request: tuple[EnrichedCitationsClient, MagicMock],
        mock_enriched_response_with_data: EnrichedCitationResponse,
    ) -> None:
        """Test search with group_art_unit_number_q convenience parameter."""
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_enriched_response_with_data

        client.search_citations(group_art_unit_number_q="2837")

        call_args = mock_get_model.call_args
        json_data = call_args[1]["json_data"]
        assert "groupArtUnitNumber:2837" in json_data["q"]


class TestEnrichedCitationsClientGetFields:
    """Tests for get_fields method."""

    def test_get_fields(
        self,
        client_with_mocked_request: tuple[EnrichedCitationsClient, MagicMock],
    ) -> None:
        """Test get_fields sends a GET request."""
        client, mock_get_model = client_with_mocked_request
        mock_response = EnrichedCitationFieldsResponse(
            api_key="enriched_cited_reference_metadata",
            api_version_number="v3",
            field_count=22,
            fields=["officeActionDate", "patentApplicationNumber"],
        )
        mock_get_model.return_value = mock_response

        result = client.get_fields()

        mock_get_model.assert_called_once_with(
            method="GET",
            endpoint="api/v1/patent/oa/enriched_cited_reference_metadata/v3/fields",
            response_class=EnrichedCitationFieldsResponse,
        )
        assert result is mock_response
        assert result.api_key == "enriched_cited_reference_metadata"


class TestEnrichedCitationsClientPaginate:
    """Tests for paginate_citations method."""

    def test_paginate_calls_paginate_results(
        self,
        enriched_client: EnrichedCitationsClient,
    ) -> None:
        """Test paginate_citations delegates to paginate_results."""
        with patch.object(
            enriched_client, "paginate_results", autospec=True
        ) as mock_paginate:
            mock_paginate.return_value = iter([])

            result = enriched_client.paginate_citations(tech_center_q="2800")

            mock_paginate.assert_called_once_with(
                method_name="search_citations",
                response_container_attr="docs",
                post_body=None,
                tech_center_q="2800",
            )

    def test_paginate_with_post_body(
        self,
        enriched_client: EnrichedCitationsClient,
    ) -> None:
        """Test paginate_citations passes post_body to paginate_results."""
        with patch.object(
            enriched_client, "paginate_results", autospec=True
        ) as mock_paginate:
            mock_paginate.return_value = iter([])
            post_body = {"q": "techCenter:2800", "limit": 50}

            result = enriched_client.paginate_citations(post_body=post_body)

            mock_paginate.assert_called_once_with(
                method_name="search_citations",
                response_container_attr="docs",
                post_body=post_body,
            )

    def test_paginate_yields_citations(
        self,
        enriched_client: EnrichedCitationsClient,
        mock_enriched_citation: EnrichedCitation,
    ) -> None:
        """Test paginate_citations yields EnrichedCitation objects."""
        with patch.object(
            enriched_client, "paginate_results", autospec=True
        ) as mock_paginate:
            mock_paginate.return_value = iter([mock_enriched_citation])

            citations = list(enriched_client.paginate_citations(query="*:*"))

            assert len(citations) == 1
            assert citations[0] is mock_enriched_citation
