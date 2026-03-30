"""Tests for the pyUSPTO.models.oa_rejections module.

This module contains comprehensive tests for OARejectionsRecord,
OARejectionsResponse, and OARejectionsFieldsResponse.
"""

from datetime import datetime
from typing import Any

import pytest

from pyUSPTO.models.oa_rejections import (
    OARejectionsFieldsResponse,
    OARejectionsRecord,
    OARejectionsResponse,
)

# --- Fixtures ---


@pytest.fixture
def sample_record_dict() -> dict[str, Any]:
    """Real record from the OA Rejections API (app 12190351)."""
    return {
        "bilskiIndicator": False,
        "actionTypeCategory": "",
        "legacyDocumentCodeIdentifier": "CTNF",
        "hasRej101": 0,
        "hasRejDP": 0,
        "hasRej103": 1,
        "mayoIndicator": False,
        "hasRej102": 0,
        "nationalClass": "438",
        "closingMissing": 0,
        "cite103Max": 2,
        "cite103EQ1": 1,
        "obsoleteDocumentIdentifier": "GTYKOVWIPPOPPY5",
        "id": "14642e2cc522ac577468fb6fc026d135",
        "createUserIdentifier": "ETL_SYS",
        "claimNumberArrayDocument": ["1"],
        "patentApplicationNumber": "12190351",
        "legalSectionCode": "112",
        "submissionDate": "2011-10-19T00:00:00",
        "groupArtUnitNumber": "1713",
        "hasRej112": 1,
        "nationalSubclass": "725000",
        "rejectFormMissmatch": 0,
        "createDateTime": "2025-07-15T21:22:06",
        "formParagraphMissing": 0,
        "aliceIndicator": False,
        "allowedClaimIndicator": False,
        "paragraphNumber": "",
        "cite103GT3": 0,
        "myriadIndicator": False,
        "headerMissing": 0,
    }


@pytest.fixture
def sample_comma_claims_dict() -> dict[str, Any]:
    """Real record with comma-separated claim numbers (app 12190351, record 2)."""
    return {
        "id": "ed812f618d3a72142850669b6b608ac3",
        "patentApplicationNumber": "12190351",
        "legacyDocumentCodeIdentifier": "CTNF",
        "claimNumberArrayDocument": ["1,2,3,4,5"],
        "hasRej103": 1,
        "hasRej112": 1,
        "hasRej101": 0,
        "hasRej102": 0,
        "hasRejDP": 0,
        "bilskiIndicator": False,
        "mayoIndicator": False,
        "aliceIndicator": False,
        "myriadIndicator": False,
        "allowedClaimIndicator": False,
        "groupArtUnitNumber": "1713",
        "legalSectionCode": "",
        "submissionDate": "2011-10-19T00:00:00",
        "createDateTime": "2025-07-15T21:22:06",
        "nationalClass": "438",
        "nationalSubclass": "725000",
        "cite103Max": 2,
        "cite103EQ1": 1,
        "cite103GT3": 0,
        "closingMissing": 0,
        "rejectFormMissmatch": 0,
        "formParagraphMissing": 0,
        "headerMissing": 0,
        "obsoleteDocumentIdentifier": "GTYKOVWIPPOPPY5",
        "createUserIdentifier": "ETL_SYS",
        "paragraphNumber": "",
        "actionTypeCategory": "",
    }


@pytest.fixture
def sample_response_dict(sample_record_dict: dict[str, Any]) -> dict[str, Any]:
    return {
        "response": {
            "numFound": 86973947,
            "start": 0,
            "docs": [sample_record_dict],
        }
    }


@pytest.fixture
def sample_fields_dict() -> dict[str, Any]:
    return {
        "apiKey": "oa_rejections",
        "apiVersionNumber": "v2",
        "apiUrl": "https://api.uspto.gov/api/v1/patent/oa/oa_rejections/v2/fields",
        "apiDocumentationUrl": "https://data.uspto.gov/swagger/index.html",
        "apiStatus": "PUBLISHED",
        "fieldCount": 31,
        "fields": [
            "bilskiIndicator",
            "actionTypeCategory",
            "legacyDocumentCodeIdentifier",
            "hasRej101",
            "hasRej103",
            "hasRejDP",
            "mayoIndicator",
            "hasRej102",
            "nationalClass",
            "closingMissing",
            "cite103Max",
            "cite103EQ1",
            "obsoleteDocumentIdentifier",
            "id",
            "createUserIdentifier",
            "claimNumberArrayDocument",
            "patentApplicationNumber",
            "legalSectionCode",
            "submissionDate",
            "groupArtUnitNumber",
            "hasRej112",
            "nationalSubclass",
            "createDateTime",
            "rejectFormMissmatch",
            "formParagraphMissing",
            "aliceIndicator",
            "allowedClaimIndicator",
            "paragraphNumber",
            "cite103GT3",
            "myriadIndicator",
            "headerMissing",
        ],
        "lastDataUpdatedDate": "2021-05-26 08:17:45.0",
    }


# --- TestOARejectionsRecordFromDict ---


class TestOARejectionsRecordFromDict:
    def test_complete(self, sample_record_dict: dict[str, Any]) -> None:
        record = OARejectionsRecord.from_dict(sample_record_dict)
        assert record.id == "14642e2cc522ac577468fb6fc026d135"
        assert record.patent_application_number == "12190351"
        assert record.legacy_document_code_identifier == "CTNF"
        assert record.action_type_category == ""
        assert record.legal_section_code == "112"
        assert record.group_art_unit_number == "1713"
        assert record.national_class == "438"
        assert record.national_subclass == "725000"
        assert record.paragraph_number == ""
        assert record.obsolete_document_identifier == "GTYKOVWIPPOPPY5"
        assert record.create_user_identifier == "ETL_SYS"

    def test_rejection_flags(self, sample_record_dict: dict[str, Any]) -> None:
        record = OARejectionsRecord.from_dict(sample_record_dict)
        assert record.has_rej_101 is False
        assert record.has_rej_102 is False
        assert record.has_rej_103 is True
        assert record.has_rej_112 is True
        assert record.has_rej_dp is False

    def test_boolean_indicators(self, sample_record_dict: dict[str, Any]) -> None:
        record = OARejectionsRecord.from_dict(sample_record_dict)
        assert record.bilski_indicator is False
        assert record.mayo_indicator is False
        assert record.alice_indicator is False
        assert record.myriad_indicator is False
        assert record.allowed_claim_indicator is False

    def test_int_fields(self, sample_record_dict: dict[str, Any]) -> None:
        record = OARejectionsRecord.from_dict(sample_record_dict)
        assert record.cite_103_max == 2
        assert record.cite_103_eq1 == 1
        assert record.cite_103_gt3 == 0
        assert record.closing_missing == 0
        assert record.reject_form_missmatch == 0
        assert record.form_paragraph_missing == 0
        assert record.header_missing == 0

    def test_single_claim(self, sample_record_dict: dict[str, Any]) -> None:
        record = OARejectionsRecord.from_dict(sample_record_dict)
        assert record.claim_number_array_document == ["1"]

    def test_comma_separated_claims(
        self, sample_comma_claims_dict: dict[str, Any]
    ) -> None:
        record = OARejectionsRecord.from_dict(sample_comma_claims_dict)
        assert record.claim_number_array_document == ["1", "2", "3", "4", "5"]

    def test_claim_number_not_list(self) -> None:
        record = OARejectionsRecord.from_dict(
            {"id": "x", "claimNumberArrayDocument": "not-a-list"}
        )
        assert record.claim_number_array_document == []

    def test_claim_number_missing(self) -> None:
        record = OARejectionsRecord.from_dict({"id": "x"})
        assert record.claim_number_array_document == []

    def test_bool_from_int_zero(self) -> None:
        record = OARejectionsRecord.from_dict({"id": "x", "hasRej101": 0})
        assert record.has_rej_101 is False

    def test_bool_from_int_one(self) -> None:
        record = OARejectionsRecord.from_dict({"id": "x", "hasRej101": 1})
        assert record.has_rej_101 is True

    def test_bool_from_json_bool(self) -> None:
        record = OARejectionsRecord.from_dict({"id": "x", "bilskiIndicator": False})
        assert record.bilski_indicator is False

    def test_missing_bool_fields_are_none(self) -> None:
        record = OARejectionsRecord.from_dict({"id": "x"})
        assert record.has_rej_101 is None
        assert record.bilski_indicator is None
        assert record.allowed_claim_indicator is None

    def test_missing_int_fields_are_none(self) -> None:
        record = OARejectionsRecord.from_dict({"id": "x"})
        assert record.cite_103_max is None
        assert record.closing_missing is None

    def test_submission_date_parsed(self, sample_record_dict: dict[str, Any]) -> None:
        record = OARejectionsRecord.from_dict(sample_record_dict)
        assert isinstance(record.submission_date, datetime)
        assert record.submission_date.year == 2011
        assert record.submission_date.month == 10

    def test_create_date_time_parsed(
        self, sample_record_dict: dict[str, Any]
    ) -> None:
        record = OARejectionsRecord.from_dict(sample_record_dict)
        assert isinstance(record.create_date_time, datetime)
        assert record.create_date_time.year == 2025
        assert record.create_date_time.month == 7

    def test_minimal(self) -> None:
        record = OARejectionsRecord.from_dict({"id": "abc"})
        assert record.id == "abc"
        assert record.patent_application_number is None
        assert record.submission_date is None
        assert record.claim_number_array_document == []

    def test_empty_dict(self) -> None:
        record = OARejectionsRecord.from_dict({})
        assert record.id == ""
        assert record.has_rej_101 is None


# --- TestOARejectionsRecordToDict ---


class TestOARejectionsRecordToDict:
    def test_roundtrip(self, sample_record_dict: dict[str, Any]) -> None:
        record = OARejectionsRecord.from_dict(sample_record_dict)
        d = record.to_dict()
        record2 = OARejectionsRecord.from_dict(d)
        assert record == record2

    def test_none_fields_filtered(self) -> None:
        record = OARejectionsRecord(id="x")
        d = record.to_dict()
        assert "patentApplicationNumber" not in d
        assert "legalSectionCode" not in d
        assert "submissionDate" not in d

    def test_empty_claims_filtered(self) -> None:
        record = OARejectionsRecord(id="x", claim_number_array_document=[])
        d = record.to_dict()
        assert "claimNumberArrayDocument" not in d

    def test_claims_joined_to_single_string(self) -> None:
        record = OARejectionsRecord(
            id="x", claim_number_array_document=["1", "2", "3"]
        )
        d = record.to_dict()
        assert d["claimNumberArrayDocument"] == ["1,2,3"]

    def test_false_bool_included(self) -> None:
        record = OARejectionsRecord(id="x", has_rej_101=False, bilski_indicator=False)
        d = record.to_dict()
        assert d["hasRej101"] is False
        assert d["bilskiIndicator"] is False

    def test_zero_int_included(self) -> None:
        record = OARejectionsRecord(id="x", closing_missing=0, cite_103_max=0)
        d = record.to_dict()
        assert d["closingMissing"] == 0
        assert d["cite103Max"] == 0

    def test_comma_claims_roundtrip(
        self, sample_comma_claims_dict: dict[str, Any]
    ) -> None:
        record = OARejectionsRecord.from_dict(sample_comma_claims_dict)
        assert record.claim_number_array_document == ["1", "2", "3", "4", "5"]
        d = record.to_dict()
        assert d["claimNumberArrayDocument"] == ["1,2,3,4,5"]


# --- TestOARejectionsResponseFromDict ---


class TestOARejectionsResponseFromDict:
    def test_complete(self, sample_response_dict: dict[str, Any]) -> None:
        response = OARejectionsResponse.from_dict(sample_response_dict)
        assert response.num_found == 86973947
        assert response.start == 0
        assert len(response.docs) == 1
        assert response.docs[0].id == "14642e2cc522ac577468fb6fc026d135"

    def test_empty(self) -> None:
        response = OARejectionsResponse.from_dict(
            {"response": {"numFound": 0, "start": 0, "docs": []}}
        )
        assert response.num_found == 0
        assert response.docs == []

    def test_unwrapped_dict(self) -> None:
        """from_dict handles a pre-unwrapped dict (no 'response' envelope)."""
        response = OARejectionsResponse.from_dict(
            {"numFound": 5, "start": 0, "docs": []}
        )
        assert response.num_found == 5

    def test_count_property(self, sample_response_dict: dict[str, Any]) -> None:
        response = OARejectionsResponse.from_dict(sample_response_dict)
        assert response.count == response.num_found == 86973947

    def test_raw_data_false(self, sample_response_dict: dict[str, Any]) -> None:
        response = OARejectionsResponse.from_dict(
            sample_response_dict, include_raw_data=False
        )
        assert response.raw_data is None

    def test_raw_data_true(self, sample_response_dict: dict[str, Any]) -> None:
        response = OARejectionsResponse.from_dict(
            sample_response_dict, include_raw_data=True
        )
        assert response.raw_data is not None
        assert "86973947" in response.raw_data

    def test_docs_not_list(self) -> None:
        response = OARejectionsResponse.from_dict(
            {"response": {"numFound": 0, "start": 0, "docs": "bad"}}
        )
        assert response.docs == []

    def test_non_dict_docs_skipped(self) -> None:
        response = OARejectionsResponse.from_dict(
            {"response": {"numFound": 1, "start": 0, "docs": ["not-a-dict"]}}
        )
        assert response.docs == []


# --- TestOARejectionsResponseToDict ---


class TestOARejectionsResponseToDict:
    def test_roundtrip(self, sample_response_dict: dict[str, Any]) -> None:
        response = OARejectionsResponse.from_dict(sample_response_dict)
        d = response.to_dict()
        assert d["response"]["numFound"] == 86973947
        assert d["response"]["start"] == 0
        assert len(d["response"]["docs"]) == 1

    def test_empty_roundtrip(self) -> None:
        response = OARejectionsResponse(num_found=0, start=0, docs=[])
        d = response.to_dict()
        assert d == {"response": {"numFound": 0, "start": 0, "docs": []}}


# --- TestOARejectionsFieldsResponseFromDict ---


class TestOARejectionsFieldsResponseFromDict:
    def test_complete(self, sample_fields_dict: dict[str, Any]) -> None:
        fields = OARejectionsFieldsResponse.from_dict(sample_fields_dict)
        assert fields.api_key == "oa_rejections"
        assert fields.api_version_number == "v2"
        assert fields.api_status == "PUBLISHED"
        assert fields.field_count == 31
        assert len(fields.fields) == 31
        assert "patentApplicationNumber" in fields.fields
        assert "hasRej101" in fields.fields
        assert fields.last_data_updated_date == "2021-05-26 08:17:45.0"

    def test_empty(self) -> None:
        fields = OARejectionsFieldsResponse.from_dict({})
        assert fields.api_key is None
        assert fields.field_count == 0
        assert fields.fields == []

    def test_fields_not_list_defensive(self) -> None:
        fields = OARejectionsFieldsResponse.from_dict({"fields": "bad"})
        assert fields.fields == []


# --- TestOARejectionsFieldsResponseToDict ---


class TestOARejectionsFieldsResponseToDict:
    def test_roundtrip(self, sample_fields_dict: dict[str, Any]) -> None:
        fields = OARejectionsFieldsResponse.from_dict(sample_fields_dict)
        d = fields.to_dict()
        assert d["apiKey"] == "oa_rejections"
        assert d["fieldCount"] == 31
        assert "patentApplicationNumber" in d["fields"]

    def test_none_filtered(self) -> None:
        fields = OARejectionsFieldsResponse(field_count=0)
        d = fields.to_dict()
        assert "apiKey" not in d
        assert "apiStatus" not in d
