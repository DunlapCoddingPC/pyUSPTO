"""models.oa_actions - Data models for USPTO Office Action Text Retrieval API.

This module provides data models for representing responses from the USPTO
Office Action Text Retrieval API (v1). These models cover office action
documents including full body text and structured section data.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from pyUSPTO.models.utils import parse_to_datetime_utc, serialize_datetime_as_naive


@dataclass(frozen=True)
class OAActionsSection:
    """Structured section data extracted from an Office Action document.

    These fields are returned as flat ``sections.*`` keys alongside the
    top-level record fields in the API response.

    Attributes:
        section_101_rejection_text: Full text of the 35 U.S.C. § 101 rejection.
        grant_date: Grant date associated with this section.
        filing_date: Filing date associated with this section.
        submission_date: Submission date of this section.
        examiner_employee_number: Examiner employee number(s).
        section_103_rejection_text: Full text of the 35 U.S.C. § 103 rejection(s).
        specification_title_text: Title of the specification.
        detail_citation_text: Detailed citation text.
        national_subclass: National subclass code(s).
        tech_center_number: Technology center number(s).
        patent_application_number: Patent application number(s).
        national_class: National class code(s).
        work_group_number: Work group number(s).
        terminal_disclaimer_status_text: Terminal disclaimer status text.
        group_art_unit_number: Group art unit number(s).
        proceeding_appendix_text: Proceeding appendix text.
        office_action_identifier: Office action identifier(s).
        withdrawal_rejection_text: Withdrawal rejection text.
        obsolete_document_identifier: Legacy IFW document identifier(s).
        section_102_rejection_text: Full text of the 35 U.S.C. § 102 rejection(s).
        legacy_document_code_identifier: Legacy document code identifier(s).
        section_112_rejection_text: Full text of the 35 U.S.C. § 112 rejection(s).
        summary_text: Summary text of the office action.
        section_101_rejection_form_paragraph_text: Form paragraph text for § 101 rejection.
        section_102_rejection_form_paragraph_text: Form paragraph text for § 102 rejection.
        section_103_rejection_form_paragraph_text: Form paragraph text for § 103 rejection.
        section_112_rejection_form_paragraph_text: Form paragraph text for § 112 rejection.
    """

    section_101_rejection_text: str | None = None
    grant_date: datetime | None = None
    filing_date: datetime | None = None
    submission_date: datetime | None = None
    examiner_employee_number: list[str] = field(default_factory=list)
    section_103_rejection_text: list[str] = field(default_factory=list)
    specification_title_text: list[str] = field(default_factory=list)
    detail_citation_text: list[str] = field(default_factory=list)
    national_subclass: list[str] = field(default_factory=list)
    tech_center_number: list[str] = field(default_factory=list)
    patent_application_number: list[str] = field(default_factory=list)
    national_class: list[str] = field(default_factory=list)
    work_group_number: list[str] = field(default_factory=list)
    terminal_disclaimer_status_text: list[str] = field(default_factory=list)
    group_art_unit_number: list[str] = field(default_factory=list)
    proceeding_appendix_text: list[str] = field(default_factory=list)
    office_action_identifier: list[str] = field(default_factory=list)
    withdrawal_rejection_text: list[str] = field(default_factory=list)
    obsolete_document_identifier: list[str] = field(default_factory=list)
    section_102_rejection_text: list[str] = field(default_factory=list)
    legacy_document_code_identifier: list[str] = field(default_factory=list)
    section_112_rejection_text: list[str] = field(default_factory=list)
    summary_text: list[str] = field(default_factory=list)
    section_101_rejection_form_paragraph_text: list[str] = field(default_factory=list)
    section_102_rejection_form_paragraph_text: list[str] = field(default_factory=list)
    section_103_rejection_form_paragraph_text: list[str] = field(default_factory=list)
    section_112_rejection_form_paragraph_text: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OAActionsSection":
        """Create an OAActionsSection from a flat record dict containing sections.* keys.

        Args:
            data: The full flat record dictionary. Keys beginning with ``sections.``
                are read as section fields.

        Returns:
            OAActionsSection: An instance of OAActionsSection.
        """

        def _get_list(key: str) -> list[str]:
            val = data.get(key, [])
            return val if isinstance(val, list) else []

        def _get_str(key: str) -> str | None:
            val = data.get(key)
            if isinstance(val, list):
                return val[0] if val else None
            return val if isinstance(val, str) else None

        def _get_dt(key: str) -> datetime | None:
            val = data.get(key)
            if isinstance(val, list):
                val = val[0] if val else None
            return parse_to_datetime_utc(val)

        return cls(
            section_101_rejection_text=_get_str("sections.section101RejectionText"),
            grant_date=_get_dt("sections.grantDate"),
            filing_date=_get_dt("sections.filingDate"),
            submission_date=_get_dt("sections.submissionDate"),
            examiner_employee_number=_get_list("sections.examinerEmployeeNumber"),
            section_103_rejection_text=_get_list("sections.section103RejectionText"),
            specification_title_text=_get_list("sections.specificationTitleText"),
            detail_citation_text=_get_list("sections.detailCitationText"),
            national_subclass=_get_list("sections.nationalSubclass"),
            tech_center_number=_get_list("sections.techCenterNumber"),
            patent_application_number=_get_list("sections.patentApplicationNumber"),
            national_class=_get_list("sections.nationalClass"),
            work_group_number=_get_list("sections.workGroupNumber"),
            terminal_disclaimer_status_text=_get_list(
                "sections.terminalDisclaimerStatusText"
            ),
            group_art_unit_number=_get_list("sections.groupArtUnitNumber"),
            proceeding_appendix_text=_get_list("sections.proceedingAppendixText"),
            office_action_identifier=_get_list("sections.officeActionIdentifier"),
            withdrawal_rejection_text=_get_list("sections.withdrawalRejectionText"),
            obsolete_document_identifier=_get_list(
                "sections.obsoleteDocumentIdentifier"
            ),
            section_102_rejection_text=_get_list("sections.section102RejectionText"),
            legacy_document_code_identifier=_get_list(
                "sections.legacyDocumentCodeIdentifier"
            ),
            section_112_rejection_text=_get_list("sections.section112RejectionText"),
            summary_text=_get_list("sections.summaryText"),
            section_101_rejection_form_paragraph_text=_get_list(
                "sections.section101RejectionFormParagraphText"
            ),
            section_102_rejection_form_paragraph_text=_get_list(
                "sections.section102RejectionFormParagraphText"
            ),
            section_103_rejection_form_paragraph_text=_get_list(
                "sections.section103RejectionFormParagraphText"
            ),
            section_112_rejection_form_paragraph_text=_get_list(
                "sections.section112RejectionFormParagraphText"
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the OAActionsSection instance to a dictionary.

        Returns:
            Dict[str, Any]: Flat dictionary with ``sections.*`` keys matching the
                API format. None values and empty lists are omitted.
        """
        d: dict[str, Any] = {
            "sections.section101RejectionText": self.section_101_rejection_text,
            "sections.grantDate": (
                serialize_datetime_as_naive(self.grant_date)
                if self.grant_date
                else None
            ),
            "sections.filingDate": (
                serialize_datetime_as_naive(self.filing_date)
                if self.filing_date
                else None
            ),
            "sections.submissionDate": (
                serialize_datetime_as_naive(self.submission_date)
                if self.submission_date
                else None
            ),
            "sections.examinerEmployeeNumber": self.examiner_employee_number,
            "sections.section103RejectionText": self.section_103_rejection_text,
            "sections.specificationTitleText": self.specification_title_text,
            "sections.detailCitationText": self.detail_citation_text,
            "sections.nationalSubclass": self.national_subclass,
            "sections.techCenterNumber": self.tech_center_number,
            "sections.patentApplicationNumber": self.patent_application_number,
            "sections.nationalClass": self.national_class,
            "sections.workGroupNumber": self.work_group_number,
            "sections.terminalDisclaimerStatusText": self.terminal_disclaimer_status_text,
            "sections.groupArtUnitNumber": self.group_art_unit_number,
            "sections.proceedingAppendixText": self.proceeding_appendix_text,
            "sections.officeActionIdentifier": self.office_action_identifier,
            "sections.withdrawalRejectionText": self.withdrawal_rejection_text,
            "sections.obsoleteDocumentIdentifier": self.obsolete_document_identifier,
            "sections.section102RejectionText": self.section_102_rejection_text,
            "sections.legacyDocumentCodeIdentifier": self.legacy_document_code_identifier,
            "sections.section112RejectionText": self.section_112_rejection_text,
            "sections.summaryText": self.summary_text,
            "sections.section101RejectionFormParagraphText": self.section_101_rejection_form_paragraph_text,
            "sections.section102RejectionFormParagraphText": self.section_102_rejection_form_paragraph_text,
            "sections.section103RejectionFormParagraphText": self.section_103_rejection_form_paragraph_text,
            "sections.section112RejectionFormParagraphText": self.section_112_rejection_form_paragraph_text,
        }
        return {
            k: v
            for k, v in d.items()
            if v is not None and (not isinstance(v, list) or v)
        }


@dataclass(frozen=True)
class OAActionsRecord:
    """A single Office Action document record from the OA Actions API.

    Attributes:
        id: Unique document identifier (hex hash).
        application_deemed_withdrawn_date: Date the application was deemed withdrawn.
        work_group: Work group code(s).
        filing_date: Filing date of the application.
        document_active_indicator: Whether the document is active (``"0"`` = inactive).
        legacy_document_code_identifier: Document code (e.g., ``"CTNF"``, ``"NOA"``).
        application_status_number: Numeric application status code.
        national_class: USPC national class code(s).
        effective_filing_date: Effective filing date of the application.
        body_text: Full text of the office action document.
        obsolete_document_identifier: Legacy IFW document identifier(s).
        access_level_category: Access level (e.g., ``"PUBLIC"``).
        application_type_category: Application type (e.g., ``"REGULAR"``).
        patent_number: Issued patent number(s). Empty list when no patent granted.
        patent_application_number: Patent application number(s).
        grant_date: Date the patent was granted.
        submission_date: Date the office action was submitted.
        customer_number: USPTO customer number.
        group_art_unit_number: Art unit number (integer).
        invention_title: Title of the invention.
        national_subclass: USPC national subclass code(s).
        patent_application_confirmation_number: Confirmation number for the application.
        last_modified_timestamp: Timestamp of the last record modification.
        examiner_employee_number: Examiner employee number(s).
        create_date_time: Timestamp when this record was created in the database.
        tech_center: Technology center code(s).
        invention_subject_matter_category: Subject matter category (e.g., ``"UTL"``).
        source_system_name: Source system that produced this record.
        legacy_cms_identifier: Legacy CMS identifier(s).
        section: Structured section data, or ``None`` if no section fields are present.
    """

    id: str = ""
    application_deemed_withdrawn_date: datetime | None = None
    work_group: list[str] = field(default_factory=list)
    filing_date: datetime | None = None
    document_active_indicator: list[str] = field(default_factory=list)
    legacy_document_code_identifier: list[str] = field(default_factory=list)
    application_status_number: int | None = None
    national_class: list[str] = field(default_factory=list)
    effective_filing_date: datetime | None = None
    body_text: list[str] = field(default_factory=list)
    obsolete_document_identifier: list[str] = field(default_factory=list)
    access_level_category: list[str] = field(default_factory=list)
    application_type_category: list[str] = field(default_factory=list)
    patent_number: list[str] = field(default_factory=list)
    patent_application_number: list[str] = field(default_factory=list)
    grant_date: datetime | None = None
    submission_date: datetime | None = None
    customer_number: int | None = None
    group_art_unit_number: int | None = None
    invention_title: list[str] = field(default_factory=list)
    national_subclass: list[str] = field(default_factory=list)
    patent_application_confirmation_number: int | None = None
    last_modified_timestamp: datetime | None = None
    examiner_employee_number: list[str] = field(default_factory=list)
    create_date_time: datetime | None = None
    tech_center: list[str] = field(default_factory=list)
    invention_subject_matter_category: list[str] = field(default_factory=list)
    source_system_name: list[str] = field(default_factory=list)
    legacy_cms_identifier: list[str] = field(default_factory=list)
    section: OAActionsSection | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OAActionsRecord":
        """Create an OAActionsRecord from a dictionary.

        Args:
            data: Dictionary containing office action record data from API response.
                May include flat ``sections.*`` keys.

        Returns:
            OAActionsRecord: An instance of OAActionsRecord.
        """

        def _get_list(key: str) -> list[str]:
            val = data.get(key, [])
            return val if isinstance(val, list) else []

        # Filter out literal "null" strings from patent_number
        patent_number_raw = _get_list("patentNumber")
        patent_number = [pn for pn in patent_number_raw if pn != "null"]

        # Detect and parse section data from flat sections.* keys
        has_sections = any(k.startswith("sections.") for k in data)
        section = OAActionsSection.from_dict(data) if has_sections else None

        return cls(
            id=data.get("id", ""),
            application_deemed_withdrawn_date=parse_to_datetime_utc(
                data.get("applicationDeemedWithdrawnDate")
            ),
            work_group=_get_list("workGroup"),
            filing_date=parse_to_datetime_utc(data.get("filingDate")),
            document_active_indicator=_get_list("documentActiveIndicator"),
            legacy_document_code_identifier=_get_list("legacyDocumentCodeIdentifier"),
            application_status_number=data.get("applicationStatusNumber"),
            national_class=_get_list("nationalClass"),
            effective_filing_date=parse_to_datetime_utc(
                data.get("effectiveFilingDate")
            ),
            body_text=_get_list("bodyText"),
            obsolete_document_identifier=_get_list("obsoleteDocumentIdentifier"),
            access_level_category=_get_list("accessLevelCategory"),
            application_type_category=_get_list("applicationTypeCategory"),
            patent_number=patent_number,
            patent_application_number=_get_list("patentApplicationNumber"),
            grant_date=parse_to_datetime_utc(data.get("grantDate")),
            submission_date=parse_to_datetime_utc(data.get("submissionDate")),
            customer_number=data.get("customerNumber"),
            group_art_unit_number=data.get("groupArtUnitNumber"),
            invention_title=_get_list("inventionTitle"),
            national_subclass=_get_list("nationalSubclass"),
            patent_application_confirmation_number=data.get(
                "patentApplicationConfirmationNumber"
            ),
            last_modified_timestamp=parse_to_datetime_utc(
                data.get("lastModifiedTimestamp")
            ),
            examiner_employee_number=_get_list("examinerEmployeeNumber"),
            create_date_time=parse_to_datetime_utc(data.get("createDateTime")),
            tech_center=_get_list("techCenter"),
            invention_subject_matter_category=_get_list(
                "inventionSubjectMatterCategory"
            ),
            source_system_name=_get_list("sourceSystemName"),
            legacy_cms_identifier=_get_list("legacyCMSIdentifier"),
            section=section,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the OAActionsRecord instance to a dictionary.

        Returns:
            Dict[str, Any]: Flat dictionary with camelCase keys matching the API format.
                ``sections.*`` keys are included when section data is present.
                None values and empty lists are omitted.
        """
        d: dict[str, Any] = {
            "id": self.id,
            "applicationDeemedWithdrawnDate": (
                serialize_datetime_as_naive(self.application_deemed_withdrawn_date)
                if self.application_deemed_withdrawn_date
                else None
            ),
            "workGroup": self.work_group,
            "filingDate": (
                serialize_datetime_as_naive(self.filing_date)
                if self.filing_date
                else None
            ),
            "documentActiveIndicator": self.document_active_indicator,
            "legacyDocumentCodeIdentifier": self.legacy_document_code_identifier,
            "applicationStatusNumber": self.application_status_number,
            "nationalClass": self.national_class,
            "effectiveFilingDate": (
                serialize_datetime_as_naive(self.effective_filing_date)
                if self.effective_filing_date
                else None
            ),
            "bodyText": self.body_text,
            "obsoleteDocumentIdentifier": self.obsolete_document_identifier,
            "accessLevelCategory": self.access_level_category,
            "applicationTypeCategory": self.application_type_category,
            "patentNumber": self.patent_number,
            "patentApplicationNumber": self.patent_application_number,
            "grantDate": (
                serialize_datetime_as_naive(self.grant_date)
                if self.grant_date
                else None
            ),
            "submissionDate": (
                serialize_datetime_as_naive(self.submission_date)
                if self.submission_date
                else None
            ),
            "customerNumber": self.customer_number,
            "groupArtUnitNumber": self.group_art_unit_number,
            "inventionTitle": self.invention_title,
            "nationalSubclass": self.national_subclass,
            "patentApplicationConfirmationNumber": self.patent_application_confirmation_number,
            "lastModifiedTimestamp": (
                serialize_datetime_as_naive(self.last_modified_timestamp)
                if self.last_modified_timestamp
                else None
            ),
            "examinerEmployeeNumber": self.examiner_employee_number,
            "createDateTime": (
                serialize_datetime_as_naive(self.create_date_time)
                if self.create_date_time
                else None
            ),
            "techCenter": self.tech_center,
            "inventionSubjectMatterCategory": self.invention_subject_matter_category,
            "sourceSystemName": self.source_system_name,
            "legacyCMSIdentifier": self.legacy_cms_identifier,
        }
        if self.section is not None:
            d.update(self.section.to_dict())
        return {
            k: v
            for k, v in d.items()
            if v is not None and (not isinstance(v, list) or v)
        }


@dataclass(frozen=True)
class OAActionsResponse:
    """Response from the OA Actions API search endpoint.

    The API returns a Solr-style response with ``start``, ``numFound``, and ``docs``.
    The outer envelope key is ``"response"``.

    Attributes:
        num_found: Total number of matching records.
        start: The start index of the first result in this page.
        docs: List of office action records in this page.
        raw_data: Optional raw JSON data from the API response (for debugging).
    """

    num_found: int = 0
    start: int = 0
    docs: list[OAActionsRecord] = field(default_factory=list)
    raw_data: str | None = field(default=None, compare=False, repr=False)

    @property
    def count(self) -> int:
        """Return total result count for pagination compatibility."""
        return self.num_found

    @classmethod
    def from_dict(
        cls, data: dict[str, Any], include_raw_data: bool = False
    ) -> "OAActionsResponse":
        """Create an OAActionsResponse from a dictionary.

        Handles both the raw API envelope (``{"response": {...}}``) and
        a pre-unwrapped dictionary.

        Args:
            data: Dictionary containing API response data.
            include_raw_data: If True, store the raw JSON for debugging.

        Returns:
            OAActionsResponse: An instance of OAActionsResponse.
        """
        inner = data.get("response", data)

        docs_data = inner.get("docs", [])
        docs = (
            [
                OAActionsRecord.from_dict(doc)
                for doc in docs_data
                if isinstance(doc, dict)
            ]
            if isinstance(docs_data, list)
            else []
        )

        return cls(
            num_found=inner.get("numFound", 0),
            start=inner.get("start", 0),
            docs=docs,
            raw_data=json.dumps(data) if include_raw_data else None,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the OAActionsResponse instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary wrapped in the ``"response"`` envelope
                matching the API format.
        """
        return {
            "response": {
                "numFound": self.num_found,
                "start": self.start,
                "docs": [doc.to_dict() for doc in self.docs],
            }
        }


@dataclass(frozen=True)
class OAActionsFieldsResponse:
    """Response from the OA Actions API fields endpoint.

    Contains metadata about the API including available field names
    and the last data update timestamp.

    Attributes:
        api_key: The dataset key (e.g., ``"oa_actions"``).
        api_version_number: API version (e.g., ``"v1"``).
        api_url: The URL of this fields endpoint.
        api_documentation_url: URL to the Swagger documentation.
        api_status: Publication status (e.g., ``"PUBLISHED"``).
        field_count: Number of available fields.
        fields: List of available field names.
        last_data_updated_date: Timestamp of the last data update (non-standard format).
    """

    api_key: str | None = None
    api_version_number: str | None = None
    api_url: str | None = None
    api_documentation_url: str | None = None
    api_status: str | None = None
    field_count: int = 0
    fields: list[str] = field(default_factory=list)
    last_data_updated_date: str | None = None

    @classmethod
    def from_dict(
        cls, data: dict[str, Any], include_raw_data: bool = False
    ) -> "OAActionsFieldsResponse":
        """Create an OAActionsFieldsResponse from a dictionary.

        Args:
            data: Dictionary containing API response data.
            include_raw_data: Unused. Present for FromDictProtocol conformance.

        Returns:
            OAActionsFieldsResponse: An instance of OAActionsFieldsResponse.
        """
        fields_data = data.get("fields", [])
        if not isinstance(fields_data, list):
            fields_data = []

        return cls(
            api_key=data.get("apiKey"),
            api_version_number=data.get("apiVersionNumber"),
            api_url=data.get("apiUrl"),
            api_documentation_url=data.get("apiDocumentationUrl"),
            api_status=data.get("apiStatus"),
            field_count=data.get("fieldCount", 0),
            fields=fields_data,
            last_data_updated_date=data.get("lastDataUpdatedDate"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the OAActionsFieldsResponse instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation with camelCase keys.
        """
        d: dict[str, Any] = {
            "apiKey": self.api_key,
            "apiVersionNumber": self.api_version_number,
            "apiUrl": self.api_url,
            "apiDocumentationUrl": self.api_documentation_url,
            "apiStatus": self.api_status,
            "fieldCount": self.field_count,
            "fields": self.fields,
            "lastDataUpdatedDate": self.last_data_updated_date,
        }
        return {
            k: v
            for k, v in d.items()
            if v is not None and (not isinstance(v, list) or v)
        }
