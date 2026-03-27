"""Tests for the pyUSPTO.clients.oa_rejections.OARejectionsClient.

This module contains comprehensive tests for initialization, search functionality,
field retrieval, and pagination.
"""

from collections.abc import Iterator
from unittest.mock import MagicMock, patch

import pytest

from pyUSPTO.clients.oa_rejections import OARejectionsClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.oa_rejections import (
    OARejectionsFieldsResponse,
    OARejectionsRecord,
    OARejectionsResponse,
)

# --- Fixtures ---


@pytest.fixture
def api_key_fixture() -> str:
    return "test_key"


@pytest.fixture
def uspto_config(api_key_fixture: str) -> USPTOConfig:
    return USPTOConfig(api_key=api_key_fixture)


@pytest.fixture
def oa_rejections_client(uspto_config: USPTOConfig) -> OARejectionsClient:
    return OARejectionsClient(config=uspto_config)


@pytest.fixture
def mock_record() -> OARejectionsRecord:
    return OARejectionsRecord(
        id="14642e2cc522ac577468fb6fc026d135",
        patent_application_number="12190351",
        legacy_document_code_identifier="CTNF",
        group_art_unit_number="1713",
        has_rej_103=True,
    )


@pytest.fixture
def mock_response_with_data(mock_record: OARejectionsRecord) -> OARejectionsResponse:
    return OARejectionsResponse(num_found=1, start=0, docs=[mock_record])


@pytest.fixture
def mock_response_empty() -> OARejectionsResponse:
    return OARejectionsResponse(num_found=0, start=0, docs=[])


@pytest.fixture
def client_with_mocked_request(
    oa_rejections_client: OARejectionsClient,
) -> Iterator[tuple[OARejectionsClient, MagicMock]]:
    with patch.object(
        oa_rejections_client, "_get_model", autospec=True
    ) as mock_get_model:
        yield oa_rejections_client, mock_get_model


# --- TestInit ---


class TestOARejectionsClientInit:
    def test_default_base_url(self, uspto_config: USPTOConfig) -> None:
        client = OARejectionsClient(config=uspto_config)
        assert client.base_url == "https://api.uspto.gov"

    def test_custom_base_url(self, uspto_config: USPTOConfig) -> None:
        client = OARejectionsClient(
            config=uspto_config, base_url="https://custom.example.com"
        )
        assert client.base_url == "https://custom.example.com"

    def test_config_base_url(self) -> None:
        config = USPTOConfig(
            api_key="test",
            oa_rejections_base_url="https://config.example.com",
        )
        client = OARejectionsClient(config=config)
        assert client.base_url == "https://config.example.com"

    def test_env_fallback(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("USPTO_API_KEY", "env_key")
        client = OARejectionsClient()
        assert client.base_url == "https://api.uspto.gov"

    def test_custom_url_overrides_config(self) -> None:
        config = USPTOConfig(
            api_key="test",
            oa_rejections_base_url="https://config.example.com",
        )
        client = OARejectionsClient(
            config=config, base_url="https://override.example.com"
        )
        assert client.base_url == "https://override.example.com"


# --- TestSearch ---


class TestOARejectionsClientSearch:
    def test_post_body_passthrough(
        self,
        client_with_mocked_request: tuple[OARejectionsClient, MagicMock],
        mock_response_with_data: OARejectionsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        post_body = {"criteria": "hasRej103:1", "rows": 50}
        result = client.search(post_body=post_body)

        mock_get_model.assert_called_once_with(
            method="POST",
            endpoint="api/v1/patent/oa/oa_rejections/v2/records",
            response_class=OARejectionsResponse,
            json_data=post_body,
            params=None,
        )
        assert result is mock_response_with_data

    def test_post_body_with_additional_params(
        self,
        client_with_mocked_request: tuple[OARejectionsClient, MagicMock],
        mock_response_with_data: OARejectionsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        extra = {"fl": "id,patentApplicationNumber"}
        client.search(post_body={"criteria": "*:*"}, additional_query_params=extra)

        mock_get_model.assert_called_once_with(
            method="POST",
            endpoint="api/v1/patent/oa/oa_rejections/v2/records",
            response_class=OARejectionsResponse,
            json_data={"criteria": "*:*"},
            params=extra,
        )

    def test_direct_criteria(
        self,
        client_with_mocked_request: tuple[OARejectionsClient, MagicMock],
        mock_response_with_data: OARejectionsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(criteria="patentApplicationNumber:12190351")

        mock_get_model.assert_called_once_with(
            method="POST",
            endpoint="api/v1/patent/oa/oa_rejections/v2/records",
            response_class=OARejectionsResponse,
            json_data={
                "criteria": "patentApplicationNumber:12190351",
                "start": 0,
                "rows": 25,
            },
        )

    def test_patent_application_number_q(
        self,
        client_with_mocked_request: tuple[OARejectionsClient, MagicMock],
        mock_response_with_data: OARejectionsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(patent_application_number_q="12190351")

        call_kwargs = mock_get_model.call_args.kwargs
        assert (
            call_kwargs["json_data"]["criteria"] == "patentApplicationNumber:12190351"
        )

    def test_legacy_document_code_identifier_q(
        self,
        client_with_mocked_request: tuple[OARejectionsClient, MagicMock],
        mock_response_with_data: OARejectionsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(legacy_document_code_identifier_q="CTNF")

        call_kwargs = mock_get_model.call_args.kwargs
        assert (
            call_kwargs["json_data"]["criteria"] == "legacyDocumentCodeIdentifier:CTNF"
        )

    def test_group_art_unit_number_q(
        self,
        client_with_mocked_request: tuple[OARejectionsClient, MagicMock],
        mock_response_with_data: OARejectionsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(group_art_unit_number_q="1713")

        call_kwargs = mock_get_model.call_args.kwargs
        assert call_kwargs["json_data"]["criteria"] == "groupArtUnitNumber:1713"

    def test_legal_section_code_q(
        self,
        client_with_mocked_request: tuple[OARejectionsClient, MagicMock],
        mock_response_with_data: OARejectionsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(legal_section_code_q="112")

        call_kwargs = mock_get_model.call_args.kwargs
        assert call_kwargs["json_data"]["criteria"] == "legalSectionCode:112"

    def test_action_type_category_q(
        self,
        client_with_mocked_request: tuple[OARejectionsClient, MagicMock],
        mock_response_with_data: OARejectionsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(action_type_category_q="rejected")

        call_kwargs = mock_get_model.call_args.kwargs
        assert call_kwargs["json_data"]["criteria"] == "actionTypeCategory:rejected"

    def test_submission_date_range(
        self,
        client_with_mocked_request: tuple[OARejectionsClient, MagicMock],
        mock_response_with_data: OARejectionsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(
            submission_date_from_q="2019-01-01",
            submission_date_to_q="2019-12-31",
        )

        call_kwargs = mock_get_model.call_args.kwargs
        assert (
            call_kwargs["json_data"]["criteria"]
            == "submissionDate:[2019-01-01 TO 2019-12-31]"
        )

    def test_submission_date_from_only(
        self,
        client_with_mocked_request: tuple[OARejectionsClient, MagicMock],
        mock_response_with_data: OARejectionsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(submission_date_from_q="2019-01-01")

        call_kwargs = mock_get_model.call_args.kwargs
        assert call_kwargs["json_data"]["criteria"] == "submissionDate:>=2019-01-01"

    def test_submission_date_to_only(
        self,
        client_with_mocked_request: tuple[OARejectionsClient, MagicMock],
        mock_response_with_data: OARejectionsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(submission_date_to_q="2019-12-31")

        call_kwargs = mock_get_model.call_args.kwargs
        assert call_kwargs["json_data"]["criteria"] == "submissionDate:<=2019-12-31"

    def test_combined_convenience_params(
        self,
        client_with_mocked_request: tuple[OARejectionsClient, MagicMock],
        mock_response_with_data: OARejectionsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(
            legacy_document_code_identifier_q="CTNF",
            group_art_unit_number_q="1700",
        )

        call_kwargs = mock_get_model.call_args.kwargs
        criteria = call_kwargs["json_data"]["criteria"]
        assert "legacyDocumentCodeIdentifier:CTNF" in criteria
        assert "groupArtUnitNumber:1700" in criteria
        assert " AND " in criteria

    def test_defaults_injected(
        self,
        client_with_mocked_request: tuple[OARejectionsClient, MagicMock],
        mock_response_with_data: OARejectionsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(patent_application_number_q="12190351")

        call_kwargs = mock_get_model.call_args.kwargs
        assert call_kwargs["json_data"]["start"] == 0
        assert call_kwargs["json_data"]["rows"] == 25

    def test_sort_included(
        self,
        client_with_mocked_request: tuple[OARejectionsClient, MagicMock],
        mock_response_with_data: OARejectionsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(
            legacy_document_code_identifier_q="CTNF", sort="submissionDate desc"
        )

        call_kwargs = mock_get_model.call_args.kwargs
        assert call_kwargs["json_data"]["sort"] == "submissionDate desc"

    def test_no_criteria_no_body_key(
        self,
        client_with_mocked_request: tuple[OARejectionsClient, MagicMock],
        mock_response_with_data: OARejectionsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search()

        call_kwargs = mock_get_model.call_args.kwargs
        assert "criteria" not in call_kwargs["json_data"]

    def test_additional_query_params_merged_into_body(
        self,
        client_with_mocked_request: tuple[OARejectionsClient, MagicMock],
        mock_response_with_data: OARejectionsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(
            legal_section_code_q="103",
            additional_query_params={"fl": "id,patentApplicationNumber"},
        )

        call_kwargs = mock_get_model.call_args.kwargs
        assert call_kwargs["json_data"]["fl"] == "id,patentApplicationNumber"
        assert "legalSectionCode:103" in call_kwargs["json_data"]["criteria"]


# --- TestGetFields ---


class TestOARejectionsClientGetFields:
    def test_get_fields_calls_correct_endpoint(
        self, oa_rejections_client: OARejectionsClient
    ) -> None:
        mock_fields = OARejectionsFieldsResponse(
            api_key="oa_rejections",
            api_status="PUBLISHED",
            field_count=31,
            fields=["patentApplicationNumber", "hasRej101"],
        )
        with patch.object(
            oa_rejections_client, "_get_model", autospec=True
        ) as mock_get_model:
            mock_get_model.return_value = mock_fields
            result = oa_rejections_client.get_fields()

        mock_get_model.assert_called_once_with(
            method="GET",
            endpoint="api/v1/patent/oa/oa_rejections/v2/fields",
            response_class=OARejectionsFieldsResponse,
        )
        assert result is mock_fields


# --- TestPaginate ---


class TestOARejectionsClientPaginate:
    def test_delegates_to_paginate_solr_results(
        self, oa_rejections_client: OARejectionsClient
    ) -> None:
        with patch.object(
            oa_rejections_client, "paginate_solr_results", autospec=True
        ) as mock_paginate:
            mock_paginate.return_value = iter([])
            oa_rejections_client.paginate(legacy_document_code_identifier_q="CTNF", rows=10)

        mock_paginate.assert_called_once_with(
            method_name="search",
            response_container_attr="docs",
            post_body=None,
            legacy_document_code_identifier_q="CTNF",
            rows=10,
        )

    def test_passes_post_body(self, oa_rejections_client: OARejectionsClient) -> None:
        with patch.object(
            oa_rejections_client, "paginate_solr_results", autospec=True
        ) as mock_paginate:
            mock_paginate.return_value = iter([])
            post_body = {"criteria": "hasRej103:1", "rows": 50}
            oa_rejections_client.paginate(post_body=post_body)

        mock_paginate.assert_called_once_with(
            method_name="search",
            response_container_attr="docs",
            post_body=post_body,
        )

    def test_yields_records(
        self,
        oa_rejections_client: OARejectionsClient,
        mock_record: OARejectionsRecord,
        mock_response_with_data: OARejectionsResponse,
    ) -> None:
        with patch.object(
            oa_rejections_client, "search", autospec=True
        ) as mock_search:
            mock_search.side_effect = [
                mock_response_with_data,
                OARejectionsResponse(num_found=0, start=0, docs=[]),
            ]
            results = list(
                oa_rejections_client.paginate(legacy_document_code_identifier_q="CTNF")
            )

        assert len(results) == 1
        assert results[0] is mock_record
