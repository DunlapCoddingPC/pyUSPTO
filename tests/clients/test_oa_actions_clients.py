"""Tests for the pyUSPTO.clients.oa_actions.OAActionsClient.

This module contains comprehensive tests for initialization, search functionality,
field retrieval, and pagination.
"""

from collections.abc import Iterator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from pyUSPTO.clients.oa_actions import OAActionsClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.oa_actions import (
    OAActionsFieldsResponse,
    OAActionsRecord,
    OAActionsResponse,
)


# --- Fixtures ---

@pytest.fixture
def api_key_fixture() -> str:
    return "test_key"


@pytest.fixture
def uspto_config(api_key_fixture: str) -> USPTOConfig:
    return USPTOConfig(api_key=api_key_fixture)


@pytest.fixture
def oa_actions_client(uspto_config: USPTOConfig) -> OAActionsClient:
    return OAActionsClient(config=uspto_config)


@pytest.fixture
def mock_record() -> OAActionsRecord:
    return OAActionsRecord(
        id="813869284108aad9fc4821419bb120d78f2a1e69db5a33d77e16f396",
        patent_application_number=["14485382"],
        legacy_document_code_identifier=["NOA"],
        tech_center=["1700"],
        group_art_unit_number=1712,
    )


@pytest.fixture
def mock_response_with_data(mock_record: OAActionsRecord) -> OAActionsResponse:
    return OAActionsResponse(num_found=1, start=0, docs=[mock_record])


@pytest.fixture
def mock_response_empty() -> OAActionsResponse:
    return OAActionsResponse(num_found=0, start=0, docs=[])


@pytest.fixture
def client_with_mocked_request(
    oa_actions_client: OAActionsClient,
) -> Iterator[tuple[OAActionsClient, MagicMock]]:
    with patch.object(oa_actions_client, "_get_model", autospec=True) as mock_get_model:
        yield oa_actions_client, mock_get_model


# --- TestInit ---

class TestOAActionsClientInit:
    def test_default_base_url(self, uspto_config: USPTOConfig) -> None:
        client = OAActionsClient(config=uspto_config)
        assert client.base_url == "https://api.uspto.gov"

    def test_custom_base_url(self, uspto_config: USPTOConfig) -> None:
        client = OAActionsClient(config=uspto_config, base_url="https://custom.example.com")
        assert client.base_url == "https://custom.example.com"

    def test_config_base_url(self) -> None:
        config = USPTOConfig(
            api_key="test",
            oa_actions_base_url="https://config.example.com",
        )
        client = OAActionsClient(config=config)
        assert client.base_url == "https://config.example.com"

    def test_env_fallback(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("USPTO_API_KEY", "env_key")
        client = OAActionsClient()
        assert client.base_url == "https://api.uspto.gov"

    def test_custom_url_overrides_config(self) -> None:
        config = USPTOConfig(
            api_key="test",
            oa_actions_base_url="https://config.example.com",
        )
        client = OAActionsClient(config=config, base_url="https://override.example.com")
        assert client.base_url == "https://override.example.com"


# --- TestSearch ---

class TestOAActionsClientSearch:
    def test_post_body_passthrough(
        self,
        client_with_mocked_request: tuple[OAActionsClient, MagicMock],
        mock_response_with_data: OAActionsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        post_body = {"criteria": "techCenter:1700", "rows": 50}
        result = client.search(post_body=post_body)

        mock_get_model.assert_called_once_with(
            method="POST",
            endpoint="api/v1/patent/oa/oa_actions/v1/records",
            response_class=OAActionsResponse,
            json_data=post_body,
            params=None,
        )
        assert result is mock_response_with_data

    def test_post_body_with_additional_params(
        self,
        client_with_mocked_request: tuple[OAActionsClient, MagicMock],
        mock_response_with_data: OAActionsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        extra = {"fl": "id,patentApplicationNumber"}
        client.search(post_body={"criteria": "*:*"}, additional_query_params=extra)

        mock_get_model.assert_called_once_with(
            method="POST",
            endpoint="api/v1/patent/oa/oa_actions/v1/records",
            response_class=OAActionsResponse,
            json_data={"criteria": "*:*"},
            params=extra,
        )

    def test_direct_criteria(
        self,
        client_with_mocked_request: tuple[OAActionsClient, MagicMock],
        mock_response_with_data: OAActionsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(criteria="patentApplicationNumber:14485382")

        mock_get_model.assert_called_once_with(
            method="POST",
            endpoint="api/v1/patent/oa/oa_actions/v1/records",
            response_class=OAActionsResponse,
            json_data={
                "criteria": "patentApplicationNumber:14485382",
                "start": 0,
                "rows": 25,
            },
        )

    def test_patent_application_number_q(
        self,
        client_with_mocked_request: tuple[OAActionsClient, MagicMock],
        mock_response_with_data: OAActionsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(patent_application_number_q="14485382")

        call_kwargs = mock_get_model.call_args.kwargs
        assert call_kwargs["json_data"]["criteria"] == "patentApplicationNumber:14485382"

    def test_legacy_document_code_identifier_q(
        self,
        client_with_mocked_request: tuple[OAActionsClient, MagicMock],
        mock_response_with_data: OAActionsResponse,
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
        client_with_mocked_request: tuple[OAActionsClient, MagicMock],
        mock_response_with_data: OAActionsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(group_art_unit_number_q=2889)

        call_kwargs = mock_get_model.call_args.kwargs
        assert call_kwargs["json_data"]["criteria"] == "groupArtUnitNumber:2889"

    def test_tech_center_q(
        self,
        client_with_mocked_request: tuple[OAActionsClient, MagicMock],
        mock_response_with_data: OAActionsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(tech_center_q="2800")

        call_kwargs = mock_get_model.call_args.kwargs
        assert call_kwargs["json_data"]["criteria"] == "techCenter:2800"

    def test_access_level_category_q(
        self,
        client_with_mocked_request: tuple[OAActionsClient, MagicMock],
        mock_response_with_data: OAActionsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(access_level_category_q="PUBLIC")

        call_kwargs = mock_get_model.call_args.kwargs
        assert call_kwargs["json_data"]["criteria"] == "accessLevelCategory:PUBLIC"

    def test_application_type_category_q(
        self,
        client_with_mocked_request: tuple[OAActionsClient, MagicMock],
        mock_response_with_data: OAActionsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(application_type_category_q="REGULAR")

        call_kwargs = mock_get_model.call_args.kwargs
        assert call_kwargs["json_data"]["criteria"] == "applicationTypeCategory:REGULAR"

    def test_submission_date_range(
        self,
        client_with_mocked_request: tuple[OAActionsClient, MagicMock],
        mock_response_with_data: OAActionsResponse,
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
        client_with_mocked_request: tuple[OAActionsClient, MagicMock],
        mock_response_with_data: OAActionsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(submission_date_from_q="2019-01-01")

        call_kwargs = mock_get_model.call_args.kwargs
        assert call_kwargs["json_data"]["criteria"] == "submissionDate:>=2019-01-01"

    def test_submission_date_to_only(
        self,
        client_with_mocked_request: tuple[OAActionsClient, MagicMock],
        mock_response_with_data: OAActionsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(submission_date_to_q="2019-12-31")

        call_kwargs = mock_get_model.call_args.kwargs
        assert call_kwargs["json_data"]["criteria"] == "submissionDate:<=2019-12-31"

    def test_combined_convenience_params(
        self,
        client_with_mocked_request: tuple[OAActionsClient, MagicMock],
        mock_response_with_data: OAActionsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(
            tech_center_q="2800",
            legacy_document_code_identifier_q="CTNF",
        )

        call_kwargs = mock_get_model.call_args.kwargs
        criteria = call_kwargs["json_data"]["criteria"]
        assert "techCenter:2800" in criteria
        assert "legacyDocumentCodeIdentifier:CTNF" in criteria
        assert " AND " in criteria

    def test_defaults_injected(
        self,
        client_with_mocked_request: tuple[OAActionsClient, MagicMock],
        mock_response_with_data: OAActionsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(patent_application_number_q="12345678")

        call_kwargs = mock_get_model.call_args.kwargs
        assert call_kwargs["json_data"]["start"] == 0
        assert call_kwargs["json_data"]["rows"] == 25

    def test_sort_included(
        self,
        client_with_mocked_request: tuple[OAActionsClient, MagicMock],
        mock_response_with_data: OAActionsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(tech_center_q="1700", sort="submissionDate desc")

        call_kwargs = mock_get_model.call_args.kwargs
        assert call_kwargs["json_data"]["sort"] == "submissionDate desc"

    def test_no_criteria_no_body_key(
        self,
        client_with_mocked_request: tuple[OAActionsClient, MagicMock],
        mock_response_with_data: OAActionsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search()

        call_kwargs = mock_get_model.call_args.kwargs
        assert "criteria" not in call_kwargs["json_data"]

    def test_additional_query_params_merged_into_body(
        self,
        client_with_mocked_request: tuple[OAActionsClient, MagicMock],
        mock_response_with_data: OAActionsResponse,
    ) -> None:
        client, mock_get_model = client_with_mocked_request
        mock_get_model.return_value = mock_response_with_data

        client.search(
            tech_center_q="1700",
            additional_query_params={"fl": "id,patentApplicationNumber"},
        )

        call_kwargs = mock_get_model.call_args.kwargs
        assert call_kwargs["json_data"]["fl"] == "id,patentApplicationNumber"
        assert "techCenter:1700" in call_kwargs["json_data"]["criteria"]


# --- TestGetFields ---

class TestOAActionsClientGetFields:
    def test_get_fields_calls_correct_endpoint(
        self, oa_actions_client: OAActionsClient
    ) -> None:
        mock_fields = OAActionsFieldsResponse(
            api_key="oa_actions",
            api_status="PUBLISHED",
            field_count=56,
            fields=["patentApplicationNumber", "bodyText"],
        )
        with patch.object(
            oa_actions_client, "_get_model", autospec=True
        ) as mock_get_model:
            mock_get_model.return_value = mock_fields
            result = oa_actions_client.get_fields()

        mock_get_model.assert_called_once_with(
            method="GET",
            endpoint="api/v1/patent/oa/oa_actions/v1/fields",
            response_class=OAActionsFieldsResponse,
        )
        assert result is mock_fields


# --- TestPaginate ---

class TestOAActionsClientPaginate:
    def test_delegates_to_paginate_solr_results(
        self, oa_actions_client: OAActionsClient
    ) -> None:
        with patch.object(
            oa_actions_client, "paginate_solr_results", autospec=True
        ) as mock_paginate:
            mock_paginate.return_value = iter([])
            oa_actions_client.paginate(tech_center_q="2800", rows=10)

        mock_paginate.assert_called_once_with(
            method_name="search",
            response_container_attr="docs",
            post_body=None,
            tech_center_q="2800",
            rows=10,
        )

    def test_passes_post_body(self, oa_actions_client: OAActionsClient) -> None:
        with patch.object(
            oa_actions_client, "paginate_solr_results", autospec=True
        ) as mock_paginate:
            mock_paginate.return_value = iter([])
            post_body = {"criteria": "techCenter:2800", "rows": 50}
            oa_actions_client.paginate(post_body=post_body)

        mock_paginate.assert_called_once_with(
            method_name="search",
            response_container_attr="docs",
            post_body=post_body,
        )

    def test_yields_records(
        self,
        oa_actions_client: OAActionsClient,
        mock_record: OAActionsRecord,
        mock_response_with_data: OAActionsResponse,
    ) -> None:
        with patch.object(oa_actions_client, "search", autospec=True) as mock_search:
            # Two pages: first has data, second is empty to stop pagination
            mock_search.side_effect = [
                mock_response_with_data,
                OAActionsResponse(num_found=0, start=0, docs=[]),
            ]
            results = list(oa_actions_client.paginate(tech_center_q="1700"))

        assert len(results) == 1
        assert results[0] is mock_record
