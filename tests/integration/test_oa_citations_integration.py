"""Integration tests for the USPTO OA Citations API client.

This module contains integration tests that make real API calls to the USPTO
Office Action Citations API. These tests are skipped by default unless
the ENABLE_INTEGRATION_TESTS environment variable is set to 'true'.
"""

import os

import pytest

from pyUSPTO.clients import OACitationsClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.oa_citations import (
    OACitationRecord,
    OACitationsFieldsResponse,
    OACitationsResponse,
)

pytestmark = pytest.mark.skipif(
    os.environ.get("ENABLE_INTEGRATION_TESTS", "").lower() != "true",
    reason="Integration tests are disabled. Set ENABLE_INTEGRATION_TESTS=true to enable.",
)

# Known stable record used for exact-value assertions:
#   patentApplicationNumber: 17519936
#   id: 90d4b51ab322a638b1327494a7129975
_KNOWN_ID = "90d4b51ab322a638b1327494a7129975"
_KNOWN_APP_NUMBER = "17519936"


@pytest.fixture(scope="module")
def oa_citations_client(config: USPTOConfig) -> OACitationsClient:
    """Create an OACitationsClient instance for integration tests."""
    return OACitationsClient(config=config)


class TestOACitationsSearch:
    """Integration tests for search."""

    def test_search_returns_results(
        self, oa_citations_client: OACitationsClient
    ) -> None:
        response = oa_citations_client.search(criteria="*:*", rows=5)
        assert isinstance(response, OACitationsResponse)
        assert response.num_found > 0
        assert len(response.docs) == 5

    def test_search_by_application_number(
        self, oa_citations_client: OACitationsClient
    ) -> None:
        response = oa_citations_client.search(
            patent_application_number_q=_KNOWN_APP_NUMBER
        )
        assert isinstance(response, OACitationsResponse)
        assert response.num_found > 0
        assert len(response.docs) > 0
        for doc in response.docs:
            assert doc.patent_application_number == _KNOWN_APP_NUMBER

    def test_search_by_id_exact_values(
        self, oa_citations_client: OACitationsClient
    ) -> None:
        response = oa_citations_client.search(
            criteria=f'id:"{_KNOWN_ID}"',
            rows=1,
        )
        assert isinstance(response, OACitationsResponse)
        assert response.num_found == 1
        assert len(response.docs) == 1

        doc = response.docs[0]
        assert doc.id == _KNOWN_ID
        assert doc.patent_application_number == _KNOWN_APP_NUMBER
        assert doc.action_type_category == "rejected"
        assert doc.legal_section_code == "103"
        assert doc.group_art_unit_number == "2858"
        assert doc.work_group == "2850"
        assert doc.tech_center == "2800"
        assert doc.examiner_cited_reference_indicator is True
        assert doc.applicant_cited_examiner_reference_indicator is False
        assert doc.office_action_citation_reference_indicator is True
        assert doc.reference_identifier == "Itagaki; Takeshi US 20150044531 A1 "
        assert doc.parsed_reference_identifier == "20150044531"
        assert doc.obsolete_document_identifier == "LD1Q0FKGXBLUEX4"
        assert doc.create_user_identifier == "ETL_SYS"
        assert doc.create_date_time is not None
        assert doc.create_date_time.year == 2025
        assert doc.create_date_time.month == 7
        assert doc.create_date_time.day == 3

    def test_search_by_legal_section_code(
        self, oa_citations_client: OACitationsClient
    ) -> None:
        response = oa_citations_client.search(
            legal_section_code_q="103",
            rows=5,
        )
        assert isinstance(response, OACitationsResponse)
        assert response.num_found > 0
        for doc in response.docs:
            assert "103" in doc.legal_section_code

    def test_search_by_tech_center(
        self, oa_citations_client: OACitationsClient
    ) -> None:
        response = oa_citations_client.search(tech_center_q="2800", rows=5)
        assert isinstance(response, OACitationsResponse)
        assert response.num_found > 0
        for doc in response.docs:
            assert doc.tech_center == "2800"

    def test_search_by_action_type_category(
        self, oa_citations_client: OACitationsClient
    ) -> None:
        response = oa_citations_client.search(
            action_type_category_q="rejected",
            rows=5,
        )
        assert isinstance(response, OACitationsResponse)
        assert response.num_found > 0
        for doc in response.docs:
            assert doc.action_type_category == "rejected"

    def test_search_by_examiner_cited(
        self, oa_citations_client: OACitationsClient
    ) -> None:
        response = oa_citations_client.search(
            examiner_cited_reference_indicator_q=True,
            rows=5,
        )
        assert isinstance(response, OACitationsResponse)
        assert response.num_found > 0
        for doc in response.docs:
            assert doc.examiner_cited_reference_indicator is True

    def test_search_by_date_range(
        self, oa_citations_client: OACitationsClient
    ) -> None:
        response = oa_citations_client.search(
            create_date_time_from_q="2025-07-01",
            create_date_time_to_q="2025-07-04",
            rows=5,
        )
        assert isinstance(response, OACitationsResponse)
        assert response.num_found > 0
        for doc in response.docs:
            assert doc.create_date_time is not None
            assert doc.create_date_time.year == 2025
            assert doc.create_date_time.month == 7

    def test_search_combined_params(
        self, oa_citations_client: OACitationsClient
    ) -> None:
        response = oa_citations_client.search(
            tech_center_q="2800",
            legal_section_code_q="103",
            rows=5,
        )
        assert isinstance(response, OACitationsResponse)
        assert response.num_found > 0
        for doc in response.docs:
            assert doc.tech_center == "2800"
            assert "103" in doc.legal_section_code

    def test_search_with_sort(
        self, oa_citations_client: OACitationsClient
    ) -> None:
        response = oa_citations_client.search(
            tech_center_q="2800",
            sort="createDateTime desc",
            rows=5,
        )
        assert isinstance(response, OACitationsResponse)
        assert response.num_found > 0
        assert len(response.docs) <= 5

    def test_search_direct_query(
        self, oa_citations_client: OACitationsClient
    ) -> None:
        response = oa_citations_client.search(
            criteria=f"patentApplicationNumber:{_KNOWN_APP_NUMBER}"
        )
        assert isinstance(response, OACitationsResponse)
        assert response.num_found > 0
        for doc in response.docs:
            assert doc.patent_application_number == _KNOWN_APP_NUMBER

    def test_search_post_body(
        self, oa_citations_client: OACitationsClient
    ) -> None:
        response = oa_citations_client.search(
            post_body={
                "criteria": f"patentApplicationNumber:{_KNOWN_APP_NUMBER}",
                "rows": 5,
            }
        )
        assert isinstance(response, OACitationsResponse)
        assert response.num_found > 0


class TestOACitationsGetFields:
    """Integration tests for get_fields."""

    def test_get_fields(self, oa_citations_client: OACitationsClient) -> None:
        response = oa_citations_client.get_fields()
        assert isinstance(response, OACitationsFieldsResponse)
        assert response.api_status == "PUBLISHED"
        assert response.field_count == 16
        assert len(response.fields) == 16
        assert "patentApplicationNumber" in response.fields
        assert "legalSectionCode" in response.fields
        assert "examinerCitedReferenceIndicator" in response.fields
        assert "createDateTime" in response.fields


class TestOACitationsPaginate:
    """Integration tests for paginate."""

    def test_paginate_yields_records(
        self, oa_citations_client: OACitationsClient
    ) -> None:
        count = 0
        for record in oa_citations_client.paginate(
            tech_center_q="2800",
            rows=10,
        ):
            assert isinstance(record, OACitationRecord)
            assert record.tech_center == "2800"
            count += 1
            if count >= 25:
                break

        assert count == 25
