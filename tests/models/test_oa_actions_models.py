"""Tests for the oa_actions models.

This module contains comprehensive tests for all classes in pyUSPTO.models.oa_actions.
"""

from typing import Any

import pytest

from pyUSPTO.models.oa_actions import (
    OAActionsFieldsResponse,
    OAActionsRecord,
    OAActionsResponse,
    OAActionsSection,
)


# --- Fixtures ---

@pytest.fixture
def sample_record_dict_no_sections() -> dict[str, Any]:
    """Sample record without sections fields."""
    return {
        "applicationDeemedWithdrawnDate": "0001-01-03T00:00:00",
        "workGroup": ["1710"],
        "filingDate": "2014-09-12T00:00:00",
        "documentActiveIndicator": ["0"],
        "legacyDocumentCodeIdentifier": ["NOA"],
        "applicationStatusNumber": 150,
        "nationalClass": ["427"],
        "effectiveFilingDate": "0001-01-03T00:00:00",
        "bodyText": ["DETAILED CORRESPONDENCE\nEXAMINER'S AMENDMENT"],
        "obsoleteDocumentIdentifier": ["JGW9HEY3RXEAPX3"],
        "accessLevelCategory": ["PUBLIC"],
        "id": "813869284108aad9fc4821419bb120d78f2a1e69db5a33d77e16f396",
        "applicationTypeCategory": ["REGULAR"],
        "patentNumber": ["10047236"],
        "patentApplicationNumber": ["14485382"],
        "grantDate": "2018-08-14T00:00:00",
        "submissionDate": "2018-05-09T00:00:00",
        "customerNumber": 157106,
        "groupArtUnitNumber": 1712,
        "inventionTitle": ["METHODS FOR MAKING COPPER INKS AND FILMS"],
        "nationalSubclass": ["553000"],
        "patentApplicationConfirmationNumber": 5549,
        "lastModifiedTimestamp": "2021-01-21T18:45:36",
        "examinerEmployeeNumber": ["85150"],
        "createDateTime": "2025-01-04T23:00:34",
        "techCenter": ["1700"],
        "inventionSubjectMatterCategory": ["UTL"],
        "sourceSystemName": ["OACS"],
        "legacyCMSIdentifier": ["PATENT-14485382-OACS-JGW9HEY3RXEAPX3"],
    }


@pytest.fixture
def sample_record_dict_with_sections() -> dict[str, Any]:
    """Sample record with sections fields."""
    return {
        "sections.section101RejectionText": "",
        "sections.examinerEmployeeNumber": ["71674"],
        "sections.section103RejectionText": [""],
        "applicationStatusNumber": 250,
        "bodyText": ["\n\n    Claim Rejections - 35 USC § 102\n\nThe following..."],
        "sections.specificationTitleText": [""],
        "sections.grantDate": "2010-08-31T00:00:00",
        "accessLevelCategory": ["PUBLIC"],
        "id": "9c27199b54dc83c9a6f643b828990d0322071461557b31ead3428885",
        "sections.detailCitationText": [""],
        "sections.nationalSubclass": ["634000"],
        "sections.techCenterNumber": ["2800"],
        "sections.patentApplicationNumber": ["11363598"],
        "sections.nationalClass": ["313"],
        "sections.workGroupNumber": ["2880"],
        "patentNumber": ["7786673"],
        "patentApplicationNumber": ["11363598"],
        "grantDate": "2010-08-31T00:00:00",
        "inventionTitle": ["GAS-FILLED SHROUD TO PROVIDE COOLER ARCTUBE"],
        "nationalSubclass": ["634000"],
        "patentApplicationConfirmationNumber": 6020,
        "sections.terminalDisclaimerStatusText": [""],
        "sections.groupArtUnitNumber": ["2889"],
        "sourceSystemName": ["OACS"],
        "sections.filingDate": "2006-02-28T00:00:00",
        "sections.proceedingAppendixText": [""],
        "sections.withdrawalRejectionText": [""],
        "sections.obsoleteDocumentIdentifier": ["G5SCPRI8PPOPPY5"],
        "workGroup": ["2880"],
        "sections.section102RejectionText": [
            "the following is a quotation of the appropriate paragraphs..."
        ],
        "filingDate": "2006-02-28T00:00:00",
        "documentActiveIndicator": ["0"],
        "legacyDocumentCodeIdentifier": ["CTNF"],
        "sections.submissionDate": "2010-02-19T00:00:00",
        "nationalClass": ["313"],
        "effectiveFilingDate": "2006-02-28T00:00:00",
        "obsoleteDocumentIdentifier": ["G5SCPRI8PPOPPY5"],
        "applicationTypeCategory": ["REGULAR"],
        "submissionDate": "2010-02-19T00:00:00",
        "customerNumber": 86378,
        "groupArtUnitNumber": 2889,
        "sections.legacyDocumentCodeIdentifier": ["CTNF"],
        "lastModifiedTimestamp": "2024-06-28T16:53:52",
        "examinerEmployeeNumber": ["71674"],
        "sections.section112RejectionText": [""],
        "createDateTime": "2025-01-04T23:00:34",
        "techCenter": ["2800"],
        "inventionSubjectMatterCategory": ["UTL"],
        "sections.summaryText": [""],
        "legacyCMSIdentifier": ["dcb1e491-ae2e-4c36-bb45-366ca8eaaf32"],
    }


@pytest.fixture
def sample_response_dict(sample_record_dict_no_sections: dict[str, Any]) -> dict[str, Any]:
    """Sample response dict with the outer Solr envelope."""
    return {
        "response": {
            "start": 0,
            "numFound": 2,
            "docs": [
                sample_record_dict_no_sections,
                {"id": "abc123", "patentApplicationNumber": ["99999999"]},
            ],
        }
    }


@pytest.fixture
def sample_fields_response_dict() -> dict[str, Any]:
    """Sample fields response dict."""
    return {
        "apiKey": "oa_actions",
        "apiVersionNumber": "v1",
        "apiUrl": "https://api.uspto.gov/api/v1/patent/oa/oa_actions/v1/fields",
        "apiDocumentationUrl": "https://data.uspto.gov/swagger/index.html",
        "apiStatus": "PUBLISHED",
        "fieldCount": 56,
        "fields": [
            "patentApplicationNumber",
            "bodyText",
            "submissionDate",
            "legacyDocumentCodeIdentifier",
            "techCenter",
            "groupArtUnitNumber",
        ],
        "lastDataUpdatedDate": "2020-03-12 11:19:05.0",
    }


# --- OAActionsSection Tests ---

class TestOAActionsSectionFromDict:
    def test_complete(self, sample_record_dict_with_sections: dict[str, Any]) -> None:
        section = OAActionsSection.from_dict(sample_record_dict_with_sections)
        assert section.section_101_rejection_text == ""
        assert section.examiner_employee_number == ["71674"]
        assert section.section_103_rejection_text == [""]
        assert section.specification_title_text == [""]
        assert section.grant_date is not None
        assert section.grant_date.year == 2010
        assert section.grant_date.month == 8
        assert section.grant_date.day == 31
        assert section.national_subclass == ["634000"]
        assert section.tech_center_number == ["2800"]
        assert section.patent_application_number == ["11363598"]
        assert section.national_class == ["313"]
        assert section.work_group_number == ["2880"]
        assert section.group_art_unit_number == ["2889"]
        assert section.filing_date is not None
        assert section.filing_date.year == 2006
        assert section.obsolete_document_identifier == ["G5SCPRI8PPOPPY5"]
        assert section.section_102_rejection_text == [
            "the following is a quotation of the appropriate paragraphs..."
        ]
        assert section.legacy_document_code_identifier == ["CTNF"]
        assert section.submission_date is not None
        assert section.submission_date.year == 2010
        assert section.submission_date.month == 2
        assert section.submission_date.day == 19

    def test_empty_dict(self) -> None:
        section = OAActionsSection.from_dict({})
        assert section.section_101_rejection_text is None
        assert section.grant_date is None
        assert section.filing_date is None
        assert section.submission_date is None
        assert section.examiner_employee_number == []
        assert section.section_102_rejection_text == []
        assert section.section_103_rejection_text == []
        assert section.section_112_rejection_text == []

    def test_defensive_list_handling(self) -> None:
        data = {
            "sections.examinerEmployeeNumber": "not-a-list",
            "sections.section102RejectionText": None,
        }
        section = OAActionsSection.from_dict(data)
        assert section.examiner_employee_number == []
        assert section.section_102_rejection_text == []

    def test_plain_string_as_list_for_datetime(self) -> None:
        data = {"sections.filingDate": ["2006-02-28T00:00:00"]}
        section = OAActionsSection.from_dict(data)
        assert section.filing_date is not None
        assert section.filing_date.year == 2006

    def test_str_field_as_nonempty_list(self) -> None:
        data = {"sections.section101RejectionText": ["some rejection text"]}
        section = OAActionsSection.from_dict(data)
        assert section.section_101_rejection_text == "some rejection text"

    def test_form_paragraph_fields_absent(self) -> None:
        section = OAActionsSection.from_dict({})
        assert section.section_101_rejection_form_paragraph_text == []
        assert section.section_102_rejection_form_paragraph_text == []
        assert section.section_103_rejection_form_paragraph_text == []
        assert section.section_112_rejection_form_paragraph_text == []


class TestOAActionsSectionToDict:
    def test_roundtrip(self, sample_record_dict_with_sections: dict[str, Any]) -> None:
        section = OAActionsSection.from_dict(sample_record_dict_with_sections)
        d = section.to_dict()
        assert d["sections.examinerEmployeeNumber"] == ["71674"]
        assert d["sections.patentApplicationNumber"] == ["11363598"]
        assert d["sections.techCenterNumber"] == ["2800"]
        assert d["sections.groupArtUnitNumber"] == ["2889"]
        assert d["sections.obsoleteDocumentIdentifier"] == ["G5SCPRI8PPOPPY5"]
        assert d["sections.legacyDocumentCodeIdentifier"] == ["CTNF"]
        assert d["sections.section102RejectionText"] == [
            "the following is a quotation of the appropriate paragraphs..."
        ]

    def test_none_and_empty_list_omitted(self) -> None:
        section = OAActionsSection()
        d = section.to_dict()
        assert d == {}

    def test_datetime_serialized(self) -> None:
        data = {"sections.filingDate": "2006-02-28T00:00:00"}
        section = OAActionsSection.from_dict(data)
        d = section.to_dict()
        assert "sections.filingDate" in d
        assert "2006" in d["sections.filingDate"]


# --- OAActionsRecord Tests ---

class TestOAActionsRecordFromDict:
    def test_complete_no_sections(
        self, sample_record_dict_no_sections: dict[str, Any]
    ) -> None:
        record = OAActionsRecord.from_dict(sample_record_dict_no_sections)
        assert record.id == "813869284108aad9fc4821419bb120d78f2a1e69db5a33d77e16f396"
        assert record.work_group == ["1710"]
        assert record.document_active_indicator == ["0"]
        assert record.legacy_document_code_identifier == ["NOA"]
        assert record.application_status_number == 150
        assert record.national_class == ["427"]
        assert record.body_text == ["DETAILED CORRESPONDENCE\nEXAMINER'S AMENDMENT"]
        assert record.obsolete_document_identifier == ["JGW9HEY3RXEAPX3"]
        assert record.access_level_category == ["PUBLIC"]
        assert record.application_type_category == ["REGULAR"]
        assert record.patent_number == ["10047236"]
        assert record.patent_application_number == ["14485382"]
        assert record.customer_number == 157106
        assert record.group_art_unit_number == 1712
        assert record.invention_title == ["METHODS FOR MAKING COPPER INKS AND FILMS"]
        assert record.national_subclass == ["553000"]
        assert record.patent_application_confirmation_number == 5549
        assert record.examiner_employee_number == ["85150"]
        assert record.tech_center == ["1700"]
        assert record.invention_subject_matter_category == ["UTL"]
        assert record.source_system_name == ["OACS"]
        assert record.legacy_cms_identifier == ["PATENT-14485382-OACS-JGW9HEY3RXEAPX3"]
        assert record.section is None

    def test_filing_date_parsed(
        self, sample_record_dict_no_sections: dict[str, Any]
    ) -> None:
        record = OAActionsRecord.from_dict(sample_record_dict_no_sections)
        assert record.filing_date is not None
        assert record.filing_date.year == 2014
        assert record.filing_date.month == 9
        assert record.filing_date.day == 12

    def test_submission_date_parsed(
        self, sample_record_dict_no_sections: dict[str, Any]
    ) -> None:
        record = OAActionsRecord.from_dict(sample_record_dict_no_sections)
        assert record.submission_date is not None
        assert record.submission_date.year == 2018
        assert record.submission_date.month == 5
        assert record.submission_date.day == 9

    def test_grant_date_parsed(
        self, sample_record_dict_no_sections: dict[str, Any]
    ) -> None:
        record = OAActionsRecord.from_dict(sample_record_dict_no_sections)
        assert record.grant_date is not None
        assert record.grant_date.year == 2018
        assert record.grant_date.month == 8

    def test_patent_number_null_string_filtered(self) -> None:
        record = OAActionsRecord.from_dict({"patentNumber": ["null"]})
        assert record.patent_number == []

    def test_patent_number_mixed_null_filtered(self) -> None:
        record = OAActionsRecord.from_dict(
            {"patentNumber": ["10047236", "null", "9999999"]}
        )
        assert record.patent_number == ["10047236", "9999999"]

    def test_with_sections(
        self, sample_record_dict_with_sections: dict[str, Any]
    ) -> None:
        record = OAActionsRecord.from_dict(sample_record_dict_with_sections)
        assert record.section is not None
        assert isinstance(record.section, OAActionsSection)
        assert record.section.patent_application_number == ["11363598"]
        assert record.section.tech_center_number == ["2800"]

    def test_no_sections_when_no_sections_keys(
        self, sample_record_dict_no_sections: dict[str, Any]
    ) -> None:
        record = OAActionsRecord.from_dict(sample_record_dict_no_sections)
        assert record.section is None

    def test_empty_dict(self) -> None:
        record = OAActionsRecord.from_dict({})
        assert record.id == ""
        assert record.patent_number == []
        assert record.work_group == []
        assert record.body_text == []
        assert record.section is None
        assert record.group_art_unit_number is None
        assert record.customer_number is None

    def test_defensive_list_handling(self) -> None:
        record = OAActionsRecord.from_dict(
            {"workGroup": "not-a-list", "bodyText": None}
        )
        assert record.work_group == []
        assert record.body_text == []


class TestOAActionsRecordToDict:
    def test_roundtrip_no_sections(
        self, sample_record_dict_no_sections: dict[str, Any]
    ) -> None:
        record = OAActionsRecord.from_dict(sample_record_dict_no_sections)
        d = record.to_dict()
        assert d["id"] == "813869284108aad9fc4821419bb120d78f2a1e69db5a33d77e16f396"
        assert d["patentApplicationNumber"] == ["14485382"]
        assert d["patentNumber"] == ["10047236"]
        assert d["groupArtUnitNumber"] == 1712
        assert d["applicationStatusNumber"] == 150
        assert d["customerNumber"] == 157106
        assert "sections.examinerEmployeeNumber" not in d

    def test_roundtrip_with_sections(
        self, sample_record_dict_with_sections: dict[str, Any]
    ) -> None:
        record = OAActionsRecord.from_dict(sample_record_dict_with_sections)
        d = record.to_dict()
        assert d["id"] == "9c27199b54dc83c9a6f643b828990d0322071461557b31ead3428885"
        assert d["patentApplicationNumber"] == ["11363598"]
        assert "sections.examinerEmployeeNumber" in d
        assert d["sections.examinerEmployeeNumber"] == ["71674"]
        assert d["sections.techCenterNumber"] == ["2800"]

    def test_none_and_empty_list_omitted(self) -> None:
        record = OAActionsRecord.from_dict({})
        d = record.to_dict()
        assert "filingDate" not in d
        assert "workGroup" not in d
        assert "patentNumber" not in d


# --- OAActionsResponse Tests ---

class TestOAActionsResponseFromDict:
    def test_complete(self, sample_response_dict: dict[str, Any]) -> None:
        response = OAActionsResponse.from_dict(sample_response_dict)
        assert response.num_found == 2
        assert response.start == 0
        assert len(response.docs) == 2
        assert response.raw_data is None

    def test_count_property(self, sample_response_dict: dict[str, Any]) -> None:
        response = OAActionsResponse.from_dict(sample_response_dict)
        assert response.count == 2
        assert response.count == response.num_found

    def test_raw_data_included(self, sample_response_dict: dict[str, Any]) -> None:
        response = OAActionsResponse.from_dict(
            sample_response_dict, include_raw_data=True
        )
        assert response.raw_data is not None
        assert '"numFound"' in response.raw_data

    def test_empty_response(self) -> None:
        response = OAActionsResponse.from_dict(
            {"response": {"start": 0, "numFound": 0, "docs": []}}
        )
        assert response.num_found == 0
        assert response.docs == []

    def test_unwrapped_dict(self) -> None:
        response = OAActionsResponse.from_dict(
            {"start": 0, "numFound": 1, "docs": [{"id": "abc"}]}
        )
        assert response.num_found == 1
        assert len(response.docs) == 1

    def test_docs_non_dict_skipped(self) -> None:
        response = OAActionsResponse.from_dict(
            {"response": {"start": 0, "numFound": 3, "docs": [{"id": "a"}, "bad", None]}}
        )
        assert len(response.docs) == 1

    def test_docs_not_list(self) -> None:
        response = OAActionsResponse.from_dict(
            {"response": {"start": 0, "numFound": 0, "docs": None}}
        )
        assert response.docs == []


class TestOAActionsResponseToDict:
    def test_roundtrip(self, sample_response_dict: dict[str, Any]) -> None:
        response = OAActionsResponse.from_dict(sample_response_dict)
        d = response.to_dict()
        assert "response" in d
        assert d["response"]["numFound"] == 2
        assert d["response"]["start"] == 0
        assert len(d["response"]["docs"]) == 2


# --- OAActionsFieldsResponse Tests ---

class TestOAActionsFieldsResponseFromDict:
    def test_complete(self, sample_fields_response_dict: dict[str, Any]) -> None:
        response = OAActionsFieldsResponse.from_dict(sample_fields_response_dict)
        assert response.api_key == "oa_actions"
        assert response.api_version_number == "v1"
        assert response.api_status == "PUBLISHED"
        assert response.field_count == 56
        assert len(response.fields) == 6
        assert "patentApplicationNumber" in response.fields
        assert "bodyText" in response.fields
        assert response.last_data_updated_date == "2020-03-12 11:19:05.0"

    def test_empty(self) -> None:
        response = OAActionsFieldsResponse.from_dict({})
        assert response.api_key is None
        assert response.api_status is None
        assert response.field_count == 0
        assert response.fields == []

    def test_fields_not_list(self) -> None:
        response = OAActionsFieldsResponse.from_dict({"fields": "not-a-list"})
        assert response.fields == []


class TestOAActionsFieldsResponseToDict:
    def test_roundtrip(self, sample_fields_response_dict: dict[str, Any]) -> None:
        response = OAActionsFieldsResponse.from_dict(sample_fields_response_dict)
        d = response.to_dict()
        assert d["apiKey"] == "oa_actions"
        assert d["apiStatus"] == "PUBLISHED"
        assert d["fieldCount"] == 56
        assert "patentApplicationNumber" in d["fields"]

    def test_none_omitted(self) -> None:
        response = OAActionsFieldsResponse.from_dict({})
        d = response.to_dict()
        assert "apiKey" not in d
        assert "apiStatus" not in d
