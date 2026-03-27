"""Integration tests for the USPTO OA Rejections API client.

This module contains integration tests that make real API calls to the USPTO
Office Action Rejections API. These tests are skipped by default unless
the ENABLE_INTEGRATION_TESTS environment variable is set to 'true'.
"""

import os

import pytest

from pyUSPTO.clients import OARejectionsClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.oa_rejections import (
    OARejectionsFieldsResponse,
    OARejectionsRecord,
    OARejectionsResponse,
)

pytestmark = pytest.mark.skipif(
    os.environ.get("ENABLE_INTEGRATION_TESTS", "").lower() != "true",
    reason="Integration tests are disabled. Set ENABLE_INTEGRATION_TESTS=true to enable.",
)

# Known stable record used for exact-value assertions:
#   patentApplicationNumber: 12190351
#   id: 14642e2cc522ac577468fb6fc026d135
_KNOWN_ID = "14642e2cc522ac577468fb6fc026d135"
_KNOWN_APP_NUMBER = "12190351"


@pytest.fixture(scope="module")
def oa_rejections_client(config: USPTOConfig) -> OARejectionsClient:
    """Create an OARejectionsClient instance for integration tests."""
    return OARejectionsClient(config=config)


class TestOARejectionsSearch:
    """Integration tests for search."""

    def test_search_returns_results(
        self, oa_rejections_client: OARejectionsClient
    ) -> None:
        response = oa_rejections_client.search(criteria="*:*", rows=5)
        assert isinstance(response, OARejectionsResponse)
        assert response.num_found > 0
        assert len(response.docs) == 5

    def test_search_by_application_number(
        self, oa_rejections_client: OARejectionsClient
    ) -> None:
        response = oa_rejections_client.search(
            patent_application_number_q=_KNOWN_APP_NUMBER
        )
        assert response.num_found > 0
        assert all(
            doc.patent_application_number == _KNOWN_APP_NUMBER for doc in response.docs
        )

    def test_search_by_doc_code(
        self, oa_rejections_client: OARejectionsClient
    ) -> None:
        response = oa_rejections_client.search(
            legacy_document_code_identifier_q="CTNF", rows=5
        )
        assert response.num_found > 0
        assert all(
            doc.legacy_document_code_identifier == "CTNF" for doc in response.docs
        )

    def test_search_by_id_exact_values(
        self, oa_rejections_client: OARejectionsClient
    ) -> None:
        response = oa_rejections_client.search(criteria=f"id:{_KNOWN_ID}", rows=1)
        assert response.num_found == 1
        record = response.docs[0]
        assert record.id == _KNOWN_ID
        assert record.patent_application_number == _KNOWN_APP_NUMBER
        assert record.legacy_document_code_identifier == "CTNF"
        assert record.group_art_unit_number == "1713"
        assert record.legal_section_code == "112"
        assert record.national_class == "438"
        assert record.national_subclass == "725000"
        assert record.obsolete_document_identifier == "GTYKOVWIPPOPPY5"
        assert record.create_user_identifier == "ETL_SYS"
        assert record.claim_number_array_document == ["1"]
        assert record.has_rej_101 is False
        assert record.has_rej_102 is False
        assert record.has_rej_103 is True
        assert record.has_rej_112 is True
        assert record.has_rej_dp is False
        assert record.bilski_indicator is False
        assert record.mayo_indicator is False
        assert record.alice_indicator is False
        assert record.myriad_indicator is False
        assert record.allowed_claim_indicator is False
        assert record.cite_103_max == 2
        assert record.cite_103_eq1 == 1
        assert record.cite_103_gt3 == 0
        assert record.closing_missing == 0
        assert record.submission_date is not None
        assert record.submission_date.year == 2011
        assert record.submission_date.month == 10

    def test_search_with_post_body(
        self, oa_rejections_client: OARejectionsClient
    ) -> None:
        response = oa_rejections_client.search(
            post_body={"criteria": f"id:{_KNOWN_ID}", "rows": 1}
        )
        assert response.num_found == 1
        assert response.docs[0].id == _KNOWN_ID

    def test_search_date_range(
        self, oa_rejections_client: OARejectionsClient
    ) -> None:
        response = oa_rejections_client.search(
            submission_date_from_q="2011-10-01",
            submission_date_to_q="2011-10-31",
            rows=5,
        )
        assert response.num_found > 0

    def test_search_pagination_start(
        self, oa_rejections_client: OARejectionsClient
    ) -> None:
        page1 = oa_rejections_client.search(
            patent_application_number_q=_KNOWN_APP_NUMBER, start=0, rows=1
        )
        page2 = oa_rejections_client.search(
            patent_application_number_q=_KNOWN_APP_NUMBER, start=1, rows=1
        )
        assert page1.num_found == page2.num_found
        assert page1.docs[0].id != page2.docs[0].id

    def test_search_count_property(
        self, oa_rejections_client: OARejectionsClient
    ) -> None:
        response = oa_rejections_client.search(criteria="*:*", rows=1)
        assert response.count == response.num_found


class TestOARejectionsPaginate:
    """Integration tests for paginate."""

    def test_paginate_yields_records(
        self, oa_rejections_client: OARejectionsClient
    ) -> None:
        records = list(
            oa_rejections_client.paginate(
                patent_application_number_q=_KNOWN_APP_NUMBER
            )
        )
        assert len(records) > 0
        assert all(isinstance(r, OARejectionsRecord) for r in records)

    def test_paginate_with_post_body(
        self, oa_rejections_client: OARejectionsClient
    ) -> None:
        records = list(
            oa_rejections_client.paginate(
                post_body={"criteria": f"id:{_KNOWN_ID}", "rows": 1}
            )
        )
        assert len(records) == 1
        assert records[0].id == _KNOWN_ID


class TestOARejectionsGetFields:
    """Integration tests for get_fields."""

    def test_get_fields_returns_response(
        self, oa_rejections_client: OARejectionsClient
    ) -> None:
        fields = oa_rejections_client.get_fields()
        assert isinstance(fields, OARejectionsFieldsResponse)

    def test_get_fields_exact_values(
        self, oa_rejections_client: OARejectionsClient
    ) -> None:
        fields = oa_rejections_client.get_fields()
        assert fields.api_key == "oa_rejections"
        assert fields.api_version_number == "v2"
        assert fields.api_status == "PUBLISHED"
        assert fields.field_count == 31
        assert len(fields.fields) == 31
        assert "patentApplicationNumber" in fields.fields
        assert "hasRej101" in fields.fields
        assert "hasRej103" in fields.fields
        assert "bilskiIndicator" in fields.fields
