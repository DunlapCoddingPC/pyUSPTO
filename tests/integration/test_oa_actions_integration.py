"""Integration tests for the USPTO OA Actions API client.

This module contains integration tests that make real API calls to the USPTO
Office Action Text Retrieval API. These tests are skipped by default unless
the ENABLE_INTEGRATION_TESTS environment variable is set to 'true'.
"""

import os

import pytest

from pyUSPTO.clients import OAActionsClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.oa_actions import (
    OAActionsFieldsResponse,
    OAActionsRecord,
    OAActionsResponse,
    OAActionsSection,
)

pytestmark = pytest.mark.skipif(
    os.environ.get("ENABLE_INTEGRATION_TESTS", "").lower() != "true",
    reason="Integration tests are disabled. Set ENABLE_INTEGRATION_TESTS=true to enable.",
)

# Known stable record used for exact-value assertions:
#   patentApplicationNumber: 11363598
#   id: 9c27199b54dc83c9a6f643b828990d0322071461557b31ead3428885
_KNOWN_ID = "9c27199b54dc83c9a6f643b828990d0322071461557b31ead3428885"
_KNOWN_APP_NUMBER = "11363598"


@pytest.fixture(scope="module")
def oa_actions_client(config: USPTOConfig) -> OAActionsClient:
    """Create an OAActionsClient instance for integration tests."""
    return OAActionsClient(config=config)


class TestOAActionsSearch:
    """Integration tests for search."""

    def test_search_returns_results(
        self, oa_actions_client: OAActionsClient
    ) -> None:
        response = oa_actions_client.search(criteria="*:*", rows=5)
        assert isinstance(response, OAActionsResponse)
        assert response.num_found > 0
        assert len(response.docs) == 5

    def test_search_by_application_number(
        self, oa_actions_client: OAActionsClient
    ) -> None:
        response = oa_actions_client.search(
            patent_application_number_q=_KNOWN_APP_NUMBER
        )
        assert isinstance(response, OAActionsResponse)
        assert response.num_found > 0
        assert len(response.docs) > 0
        for doc in response.docs:
            assert _KNOWN_APP_NUMBER in doc.patent_application_number

    def test_search_by_id_exact_values(
        self, oa_actions_client: OAActionsClient
    ) -> None:
        response = oa_actions_client.search(
            criteria=f'id:"{_KNOWN_ID}"',
            rows=1,
        )
        assert isinstance(response, OAActionsResponse)
        assert response.num_found == 1
        assert len(response.docs) == 1

        doc = response.docs[0]
        assert doc.id == _KNOWN_ID
        assert doc.patent_application_number == [_KNOWN_APP_NUMBER]
        assert doc.group_art_unit_number == 2889
        assert doc.tech_center == ["2800"]
        assert doc.patent_number == ["7786673"]
        assert doc.legacy_document_code_identifier == ["CTNF"]
        assert doc.application_status_number == 250
        assert doc.customer_number == 86378
        assert doc.patent_application_confirmation_number == 6020
        assert doc.invention_title == ["GAS-FILLED SHROUD TO PROVIDE COOLER ARCTUBE"]
        assert doc.access_level_category == ["PUBLIC"]
        assert doc.application_type_category == ["REGULAR"]
        assert doc.source_system_name == ["OACS"]
        assert doc.submission_date is not None
        assert doc.submission_date.year == 2010
        assert doc.submission_date.month == 2
        assert doc.submission_date.day == 19
        assert doc.grant_date is not None
        assert doc.grant_date.year == 2010
        assert doc.grant_date.month == 8
        assert doc.grant_date.day == 31
        assert doc.filing_date is not None
        assert doc.filing_date.year == 2006
        assert doc.filing_date.month == 2
        assert doc.filing_date.day == 28

    def test_search_by_id_sections_populated(
        self, oa_actions_client: OAActionsClient
    ) -> None:
        response = oa_actions_client.search(
            criteria=f'id:"{_KNOWN_ID}"',
            rows=1,
        )
        doc = response.docs[0]
        assert doc.section is not None
        assert isinstance(doc.section, OAActionsSection)
        assert doc.section.patent_application_number == [_KNOWN_APP_NUMBER]
        assert doc.section.group_art_unit_number == ["2889"]
        assert doc.section.tech_center_number == ["2800"]
        assert doc.section.legacy_document_code_identifier == ["CTNF"]
        assert doc.section.obsolete_document_identifier == ["G5SCPRI8PPOPPY5"]
        assert len(doc.section.section_102_rejection_text) > 0
        assert doc.section.section_102_rejection_text[0].startswith(
            "the following is a quotation"
        )
        assert doc.section.submission_date is not None
        assert doc.section.submission_date.year == 2010
        assert doc.section.grant_date is not None
        assert doc.section.grant_date.year == 2010

    def test_search_by_legacy_doc_code(
        self, oa_actions_client: OAActionsClient
    ) -> None:
        response = oa_actions_client.search(
            legacy_document_code_identifier_q="CTNF",
            rows=5,
        )
        assert isinstance(response, OAActionsResponse)
        assert response.num_found > 0
        for doc in response.docs:
            assert "CTNF" in doc.legacy_document_code_identifier

    def test_search_by_tech_center(
        self, oa_actions_client: OAActionsClient
    ) -> None:
        response = oa_actions_client.search(tech_center_q="2800", rows=5)
        assert isinstance(response, OAActionsResponse)
        assert response.num_found > 0
        for doc in response.docs:
            assert "2800" in doc.tech_center

    def test_search_by_submission_date_range(
        self, oa_actions_client: OAActionsClient
    ) -> None:
        response = oa_actions_client.search(
            submission_date_from_q="2010-01-01",
            submission_date_to_q="2010-12-31",
            rows=5,
        )
        assert isinstance(response, OAActionsResponse)
        assert response.num_found > 0
        for doc in response.docs:
            assert doc.submission_date is not None
            assert doc.submission_date.year == 2010

    def test_search_combined_params(
        self, oa_actions_client: OAActionsClient
    ) -> None:
        response = oa_actions_client.search(
            tech_center_q="2800",
            legacy_document_code_identifier_q="CTNF",
            rows=5,
        )
        assert isinstance(response, OAActionsResponse)
        assert response.num_found > 0
        for doc in response.docs:
            assert "2800" in doc.tech_center
            assert "CTNF" in doc.legacy_document_code_identifier

    def test_search_with_sort(self, oa_actions_client: OAActionsClient) -> None:
        response = oa_actions_client.search(
            tech_center_q="1700",
            sort="submissionDate desc",
            rows=5,
        )
        assert isinstance(response, OAActionsResponse)
        assert response.num_found > 0
        assert len(response.docs) <= 5

    def test_search_direct_query(self, oa_actions_client: OAActionsClient) -> None:
        response = oa_actions_client.search(
            criteria=f"patentApplicationNumber:{_KNOWN_APP_NUMBER}"
        )
        assert isinstance(response, OAActionsResponse)
        assert response.num_found > 0
        for doc in response.docs:
            assert _KNOWN_APP_NUMBER in doc.patent_application_number

    def test_search_post_body(self, oa_actions_client: OAActionsClient) -> None:
        response = oa_actions_client.search(
            post_body={
                "criteria": f"patentApplicationNumber:{_KNOWN_APP_NUMBER}",
                "rows": 5,
            }
        )
        assert isinstance(response, OAActionsResponse)
        assert response.num_found > 0


class TestOAActionsGetFields:
    """Integration tests for get_fields."""

    def test_get_fields(self, oa_actions_client: OAActionsClient) -> None:
        response = oa_actions_client.get_fields()
        assert isinstance(response, OAActionsFieldsResponse)
        assert response.api_status == "PUBLISHED"
        assert response.field_count == 56
        assert len(response.fields) == 56
        assert "patentApplicationNumber" in response.fields
        assert "bodyText" in response.fields
        assert "submissionDate" in response.fields
        assert "legacyDocumentCodeIdentifier" in response.fields
        assert "sections.section102RejectionText" in response.fields
        assert "sections.groupArtUnitNumber" in response.fields


class TestOAActionsPaginate:
    """Integration tests for paginate."""

    def test_paginate_yields_records(
        self, oa_actions_client: OAActionsClient
    ) -> None:
        count = 0
        for record in oa_actions_client.paginate(
            tech_center_q="1700",
            rows=10,
        ):
            assert isinstance(record, OAActionsRecord)
            assert "1700" in record.tech_center
            count += 1
            if count >= 25:
                break

        assert count == 25
