"""Tests for the pyUSPTO.clients.oa_citations.OACitationsClient.

This module contains comprehensive tests for initialization, search functionality,
field retrieval, and pagination.
"""

from collections.abc import Iterator
from unittest.mock import MagicMock, patch

import pytest

from pyUSPTO.clients.oa_citations import OACitationsClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.oa_citations import (
    OACitationRecord,
    OACitationsFieldsResponse,
    OACitationsResponse,
)

# --- Fixtures ---


@pytest.fixture
def api_key_fixture() -> str:
    return "test_key"


@pytest.fixture
def uspto_config(api_key_fixture: str) -> USPTOConfig:
    return USPTOConfig(api_key=api_key_fixture)


@pytest.fixture
def oa_citations_client(uspto_config: USPTOConfig) -> OACitationsClient:
    return OACitationsClient(config=uspto_config)


@pytest.fixture
def mock_record() -> OACitationRecord:
    return OACitationRecord(
        id="90d4b51ab322a638b1327494a7129975",
        patent_application_number="17519936",
        action_type_category="rejected",
        legal_section_code="103",
        tech_center="2800",
        group_art_unit_number="2858",
        examiner_cited_reference_indicator=True,
    )


@pytest.fixture
def mock_response_with_data(mock_record: OACitationRecord) -> OACitationsResponse:
    return OACitationsResponse(num_found=1, start=0, docs=[mock_record])


@pytest.fixture
def mock_response_empty() -> OACitationsResponse:
    return OACitationsResponse(num_found=0, start=0, docs=[])


@pytest.fixture
def client_with_mocked_request(
    oa_citations_client: OACitationsClient,
) -> Iterator[tuple[OACitationsClient, MagicMock]]:
    with patch.object(
        oa_citations_client, "_get_model", autospec=True
    ) as mock_get_model:
        yield oa_citations_client, mock_get_model


# --- TestInit ---


class TestOACitationsClientInit:
    def test_default_base_url(self, uspto_config: USPTOConfig) -> None:
        client = OACitationsClient(config=uspto_config)
        assert client.base_url == "https://api.uspto.gov"

    def test_custom_base_url(self, uspto_config: USPTOConfig) -> None:
        client = OACitationsClient(
            config=uspto_config, base_url="https://custom.example.com"
        )
        assert client.base_url == "https://custom.example.com"

    def test_config_base_url(self) -> None:
        config = USPTOConfig(
            api_key="test",
            oa_citations_base_url="https://config.example.com",
        )
        client = OACitationsClient(config=config)
        assert client.base_url == "https://config.example.com"

    def test_env_fallback(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("USPTO_API_KEY", "env_key")
        client = OACitationsClient()
        assert client.base_url == "https://api.uspto.gov"

    def test_custom_url_overrides_config(self) -> None:
        config = USPTOConfig(
            api_key="test",
            oa_citations_base_url="https://config.example.com",
        )
        client = OACitationsClient(
            config=config, base_url="https://override.example.com"
        )
        assert client.base_url == "https://override.example.com"


# --- TestSearch ---


class TestOACitationsClientSearch:
    def test_post_body_passthrough(
        self,
        client_with_mocked_request: tuple[OACitationsClient, MagicMock],
        mock_response_with_data: OACitationsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        post_body = {"criteria": "techCenter:2800", "rows": 50}
        result = client.search(post_body=post_body)

        mock_get_model.assert_called_once_with(
            method="POST",
            endpoint="api/v1/patent/oa/oa_citations/v2/records",
            response_class=OACitationsResponse,
            json_data=post_body,
            params=None,
        )
        assert result is mock_response_with_data

    def test_post_body_with_additional_params(
        self,
        client_with_mocked_request: tuple[OACitationsClient, MagicMock],
        mock_response_with_data: OACitationsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        extra = {"fl": "id,patentApplicationNumber"}
        client.search(post_body={"criteria": "*:*"}, additional_query_params=extra)

        mock_get_model.assert_called_once_with(
            method="POST",
            endpoint="api/v1/patent/oa/oa_citations/v2/records",
            response_class=OACitationsResponse,
            json_data={"criteria": "*:*"},
            params=extra,
        )

    def test_direct_criteria(
        self,
        client_with_mocked_request: tuple[OACitationsClient, MagicMock],
        mock_response_with_data: OACitationsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(criteria="patentApplicationNumber:17519936")

        mock_get_model.assert_called_once_with(
            method="POST",
            endpoint="api/v1/patent/oa/oa_citations/v2/records",
            response_class=OACitationsResponse,
            json_data={
                "criteria": "patentApplicationNumber:17519936",
                "start": 0,
                "rows": 25,
            },
        )

    def test_patent_application_number_q(
        self,
        client_with_mocked_request: tuple[OACitationsClient, MagicMock],
        mock_response_with_data: OACitationsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(patent_application_number_q="17519936")

        call_kwargs = mock_get_model.call_args.kwargs
        assert (
            call_kwargs["json_data"]["criteria"]
            == "patentApplicationNumber:17519936"
        )

    def test_legal_section_code_q(
        self,
        client_with_mocked_request: tuple[OACitationsClient, MagicMock],
        mock_response_with_data: OACitationsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(legal_section_code_q="103")

        call_kwargs = mock_get_model.call_args.kwargs
        assert call_kwargs["json_data"]["criteria"] == "legalSectionCode:*103*"

    def test_action_type_category_q(
        self,
        client_with_mocked_request: tuple[OACitationsClient, MagicMock],
        mock_response_with_data: OACitationsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(action_type_category_q="rejected")

        call_kwargs = mock_get_model.call_args.kwargs
        assert call_kwargs["json_data"]["criteria"] == "actionTypeCategory:rejected"

    def test_tech_center_q(
        self,
        client_with_mocked_request: tuple[OACitationsClient, MagicMock],
        mock_response_with_data: OACitationsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(tech_center_q="2800")

        call_kwargs = mock_get_model.call_args.kwargs
        assert call_kwargs["json_data"]["criteria"] == "techCenter:2800"

    def test_work_group_q(
        self,
        client_with_mocked_request: tuple[OACitationsClient, MagicMock],
        mock_response_with_data: OACitationsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(work_group_q="2850")

        call_kwargs = mock_get_model.call_args.kwargs
        assert call_kwargs["json_data"]["criteria"] == "workGroup:2850"

    def test_group_art_unit_number_q(
        self,
        client_with_mocked_request: tuple[OACitationsClient, MagicMock],
        mock_response_with_data: OACitationsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(group_art_unit_number_q="2858")

        call_kwargs = mock_get_model.call_args.kwargs
        assert call_kwargs["json_data"]["criteria"] == "groupArtUnitNumber:2858"

    def test_examiner_cited_reference_indicator_q(
        self,
        client_with_mocked_request: tuple[OACitationsClient, MagicMock],
        mock_response_with_data: OACitationsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(examiner_cited_reference_indicator_q=True)

        call_kwargs = mock_get_model.call_args.kwargs
        assert (
            call_kwargs["json_data"]["criteria"]
            == "examinerCitedReferenceIndicator:true"
        )

    def test_applicant_cited_examiner_reference_indicator_q(
        self,
        client_with_mocked_request: tuple[OACitationsClient, MagicMock],
        mock_response_with_data: OACitationsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(applicant_cited_examiner_reference_indicator_q=False)

        call_kwargs = mock_get_model.call_args.kwargs
        assert (
            call_kwargs["json_data"]["criteria"]
            == "applicantCitedExaminerReferenceIndicator:false"
        )

    def test_create_date_time_range(
        self,
        client_with_mocked_request: tuple[OACitationsClient, MagicMock],
        mock_response_with_data: OACitationsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(
            create_date_time_from_q="2025-01-01",
            create_date_time_to_q="2025-06-30",
        )

        call_kwargs = mock_get_model.call_args.kwargs
        assert (
            call_kwargs["json_data"]["criteria"]
            == "createDateTime:[2025-01-01 TO 2025-06-30]"
        )

    def test_create_date_time_from_only(
        self,
        client_with_mocked_request: tuple[OACitationsClient, MagicMock],
        mock_response_with_data: OACitationsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(create_date_time_from_q="2025-01-01")

        call_kwargs = mock_get_model.call_args.kwargs
        assert (
            call_kwargs["json_data"]["criteria"] == "createDateTime:>=2025-01-01"
        )

    def test_create_date_time_to_only(
        self,
        client_with_mocked_request: tuple[OACitationsClient, MagicMock],
        mock_response_with_data: OACitationsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(create_date_time_to_q="2025-06-30")

        call_kwargs = mock_get_model.call_args.kwargs
        assert (
            call_kwargs["json_data"]["criteria"] == "createDateTime:<=2025-06-30"
        )

    def test_combined_convenience_params(
        self,
        client_with_mocked_request: tuple[OACitationsClient, MagicMock],
        mock_response_with_data: OACitationsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(
            tech_center_q="2800",
            legal_section_code_q="103",
        )

        call_kwargs = mock_get_model.call_args.kwargs
        criteria = call_kwargs["json_data"]["criteria"]
        assert "techCenter:2800" in criteria
        assert "legalSectionCode:*103*" in criteria
        assert " AND " in criteria

    def test_defaults_injected(
        self,
        client_with_mocked_request: tuple[OACitationsClient, MagicMock],
        mock_response_with_data: OACitationsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(patent_application_number_q="17519936")

        call_kwargs = mock_get_model.call_args.kwargs
        assert call_kwargs["json_data"]["start"] == 0
        assert call_kwargs["json_data"]["rows"] == 25

    def test_sort_included(
        self,
        client_with_mocked_request: tuple[OACitationsClient, MagicMock],
        mock_response_with_data: OACitationsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(tech_center_q="2800", sort="createDateTime desc")

        call_kwargs = mock_get_model.call_args.kwargs
        assert call_kwargs["json_data"]["sort"] == "createDateTime desc"

    def test_no_criteria_no_body_key(
        self,
        client_with_mocked_request: tuple[OACitationsClient, MagicMock],
        mock_response_with_data: OACitationsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search()

        call_kwargs = mock_get_model.call_args.kwargs
        assert "criteria" not in call_kwargs["json_data"]

    def test_additional_query_params_merged_into_body(
        self,
        client_with_mocked_request: tuple[OACitationsClient, MagicMock],
        mock_response_with_data: OACitationsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(
            tech_center_q="2800",
            additional_query_params={"fl": "id,patentApplicationNumber"},
        )

        call_kwargs = mock_get_model.call_args.kwargs
        assert call_kwargs["json_data"]["fl"] == "id,patentApplicationNumber"
        assert "techCenter:2800" in call_kwargs["json_data"]["criteria"]


# --- TestGetFields ---


class TestOACitationsClientGetFields:
    def test_get_fields_calls_correct_endpoint(
        self, oa_citations_client: OACitationsClient
    ) -> None:
        mock_fields = OACitationsFieldsResponse(
            api_key="oa_citations",
            api_status="PUBLISHED",
            field_count=16,
            fields=["patentApplicationNumber", "legalSectionCode"],
        )
        with patch.object(
            oa_citations_client, "_get_model", autospec=True
        ) as mock_get_model:
            mock_get_model.return_value = mock_fields
            result = oa_citations_client.get_fields()

        mock_get_model.assert_called_once_with(
            method="GET",
            endpoint="api/v1/patent/oa/oa_citations/v2/fields",
            response_class=OACitationsFieldsResponse,
        )
        assert result is mock_fields


# --- TestPaginate ---


class TestOACitationsClientPaginate:
    def test_delegates_to_paginate_solr_results(
        self, oa_citations_client: OACitationsClient
    ) -> None:
        with patch.object(
            oa_citations_client, "paginate_solr_results", autospec=True
        ) as mock_paginate:
            mock_paginate.return_value = iter([])
            oa_citations_client.paginate(tech_center_q="2800", rows=10)

        mock_paginate.assert_called_once_with(
            method_name="search",
            response_container_attr="docs",
            post_body=None,
            tech_center_q="2800",
            rows=10,
        )

    def test_passes_post_body(
        self, oa_citations_client: OACitationsClient
    ) -> None:
        with patch.object(
            oa_citations_client, "paginate_solr_results", autospec=True
        ) as mock_paginate:
            mock_paginate.return_value = iter([])
            post_body = {"criteria": "techCenter:2800", "rows": 50}
            oa_citations_client.paginate(post_body=post_body)

        mock_paginate.assert_called_once_with(
            method_name="search",
            response_container_attr="docs",
            post_body=post_body,
        )

    def test_yields_records(
        self,
        oa_citations_client: OACitationsClient,
        mock_record: OACitationRecord,
        mock_response_with_data: OACitationsResponse,
    ) -> None:
        with patch.object(
            oa_citations_client, "search", autospec=True
        ) as mock_search:
            # Two pages: first has data, second is empty to stop pagination
            mock_search.side_effect = [
                mock_response_with_data,
                OACitationsResponse(num_found=0, start=0, docs=[]),
            ]
            results = list(oa_citations_client.paginate(tech_center_q="2800"))

        assert len(results) == 1
        assert results[0] is mock_record
