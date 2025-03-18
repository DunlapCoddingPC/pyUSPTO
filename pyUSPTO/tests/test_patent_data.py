"""
Tests for the patent_data module.

This module contains tests for the PatentDataClient class and related functionality.
"""

import os
import re
import pytest
from unittest.mock import MagicMock, patch, mock_open
from typing import Dict, Any, List

from pyUSPTO.clients import PatentDataClient
from pyUSPTO.models.patent_data import (
    PatentDataResponse,
    PatentFileWrapper,
    ApplicationMetaData,
    Address,
    Person,
    Applicant,
    Inventor,
    Attorney,
    EntityStatus,
    CustomerNumberCorrespondence,
    RecordAttorney,
    Assignor,
    Assignee,
    Assignment,
    ForeignPriority,
    ParentContinuity,
    ChildContinuity,
    PatentTermAdjustmentHistoryData,
    PatentTermAdjustmentData,
    Event,
    DocumentMetaData,
)
from pyUSPTO.config import USPTOConfig
from pyUSPTO.base import USPTOApiError


class TestPatentDataModels:
    """Tests for the patent data model classes."""

    def test_address_from_dict(self) -> None:
        """Test Address.from_dict method."""
        data = {
            "nameLineOneText": "Test Name",
            "nameLineTwoText": "Test Name 2",
            "addressLineOneText": "123 Test St",
            "addressLineTwoText": "Suite 100",
            "addressLineThreeText": "Floor 2",
            "addressLineFourText": "Building A",
            "geographicRegionName": "California",
            "geographicRegionCode": "CA",
            "postalCode": "12345",
            "cityName": "Test City",
            "countryCode": "US",
            "countryName": "United States",
            "postalAddressCategory": "Mailing",
            "correspondentNameText": "Test Correspondent",
        }

        address = Address.from_dict(data)

        assert address.name_line_one_text == "Test Name"
        assert address.name_line_two_text == "Test Name 2"
        assert address.address_line_one_text == "123 Test St"
        assert address.address_line_two_text == "Suite 100"
        assert address.address_line_three_text == "Floor 2"
        assert address.address_line_four_text == "Building A"
        assert address.geographic_region_name == "California"
        assert address.geographic_region_code == "CA"
        assert address.postal_code == "12345"
        assert address.city_name == "Test City"
        assert address.country_code == "US"
        assert address.country_name == "United States"
        assert address.postal_address_category == "Mailing"
        assert address.correspondent_name_text == "Test Correspondent"

    def test_person_from_dict(self) -> None:
        """Test Person.from_dict method."""
        data = {
            "firstName": "John",
            "middleName": "A",
            "lastName": "Smith",
            "namePrefix": "Dr.",
            "nameSuffix": "Jr.",
            "preferredName": "Johnny",
            "countryCode": "US",
        }

        person = Person.from_dict(data)

        assert person.first_name == "John"
        assert person.middle_name == "A"
        assert person.last_name == "Smith"
        assert person.name_prefix == "Dr."
        assert person.name_suffix == "Jr."
        assert person.preferred_name == "Johnny"
        assert person.country_code == "US"

    def test_applicant_from_dict(self) -> None:
        """Test Applicant.from_dict method."""
        data = {
            "firstName": "John",
            "lastName": "Smith",
            "applicantNameText": "John Smith",
            "correspondenceAddressBag": [
                {
                    "cityName": "Test City",
                    "geographicRegionCode": "CA",
                    "countryCode": "US",
                }
            ],
        }

        applicant = Applicant.from_dict(data)

        assert applicant.first_name == "John"
        assert applicant.last_name == "Smith"
        assert applicant.applicant_name_text == "John Smith"
        assert len(applicant.correspondence_address_bag) == 1
        assert applicant.correspondence_address_bag[0].city_name == "Test City"

    def test_inventor_from_dict(self) -> None:
        """Test Inventor.from_dict method."""
        data = {
            "firstName": "Jane",
            "lastName": "Doe",
            "inventorNameText": "Jane Doe",
            "correspondenceAddressBag": [
                {
                    "cityName": "Test City",
                    "geographicRegionCode": "NY",
                    "countryCode": "US",
                }
            ],
        }

        inventor = Inventor.from_dict(data)

        assert inventor.first_name == "Jane"
        assert inventor.last_name == "Doe"
        assert inventor.inventor_name_text == "Jane Doe"
        assert len(inventor.correspondence_address_bag) == 1
        assert inventor.correspondence_address_bag[0].city_name == "Test City"

    def test_attorney_from_dict(self) -> None:
        """Test Attorney.from_dict method."""
        data = {
            "firstName": "James",
            "lastName": "Legal",
            "registrationNumber": "12345",
            "activeIndicator": "Y",
            "registeredPractitionerCategory": "Attorney",
            "attorneyAddressBag": [
                {
                    "cityName": "Washington",
                    "geographicRegionCode": "DC",
                    "countryCode": "US",
                }
            ],
            "telecommunicationAddressBag": [
                {
                    "telecommunicationNumber": "555-123-4567",
                    "extensionNumber": "123",
                    "telecomTypeCode": "PHONE",
                }
            ],
        }

        attorney = Attorney.from_dict(data)

        assert attorney.first_name == "James"
        assert attorney.last_name == "Legal"
        assert attorney.registration_number == "12345"
        assert attorney.active_indicator == "Y"
        assert attorney.registered_practitioner_category == "Attorney"
        assert len(attorney.attorney_address_bag) == 1
        assert attorney.attorney_address_bag[0].city_name == "Washington"
        assert len(attorney.telecommunication_address_bag) == 1
        assert (
            attorney.telecommunication_address_bag[0].telecommunication_number
            == "555-123-4567"
        )

    def test_entity_status_from_dict(self) -> None:
        """Test EntityStatus.from_dict method."""
        data = {
            "smallEntityStatusIndicator": True,
            "businessEntityStatusCategory": "SMALL",
        }

        entity_status = EntityStatus.from_dict(data)

        assert entity_status.small_entity_status_indicator is True
        assert entity_status.business_entity_status_category == "SMALL"

    def test_customer_number_correspondence_from_dict(self) -> None:
        """Test CustomerNumberCorrespondence.from_dict method."""
        data = {
            "patronIdentifier": 12345,
            "organizationStandardName": "Test Law Firm",
            "powerOfAttorneyAddressBag": [
                {
                    "cityName": "Washington",
                    "geographicRegionCode": "DC",
                    "countryCode": "US",
                }
            ],
            "telecommunicationAddressBag": [
                {
                    "telecommunicationNumber": "555-123-4567",
                    "telecomTypeCode": "PHONE",
                }
            ],
        }

        customer_correspondence = CustomerNumberCorrespondence.from_dict(data)

        assert customer_correspondence.patron_identifier == 12345
        assert customer_correspondence.organization_standard_name == "Test Law Firm"
        assert len(customer_correspondence.power_of_attorney_address_bag) == 1
        assert (
            customer_correspondence.power_of_attorney_address_bag[0].city_name
            == "Washington"
        )
        assert len(customer_correspondence.telecommunication_address_bag) == 1
        assert (
            customer_correspondence.telecommunication_address_bag[
                0
            ].telecommunication_number
            == "555-123-4567"
        )

    def test_record_attorney_from_dict(self) -> None:
        """Test RecordAttorney.from_dict method."""
        data = {
            "customerNumberCorrespondenceData": [
                {
                    "patronIdentifier": 12345,
                    "organizationStandardName": "Test Law Firm",
                }
            ],
            "powerOfAttorneyBag": [
                {
                    "firstName": "James",
                    "lastName": "Legal",
                    "registrationNumber": "12345",
                }
            ],
            "attorneyBag": [
                {
                    "firstName": "Jane",
                    "lastName": "Lawyer",
                    "registrationNumber": "67890",
                }
            ],
        }

        record_attorney = RecordAttorney.from_dict(data)

        assert len(record_attorney.customer_number_correspondence_data) == 1
        assert (
            record_attorney.customer_number_correspondence_data[0].patron_identifier
            == 12345
        )
        assert len(record_attorney.power_of_attorney_bag) == 1
        assert record_attorney.power_of_attorney_bag[0].first_name == "James"
        assert len(record_attorney.attorney_bag) == 1
        assert record_attorney.attorney_bag[0].first_name == "Jane"

    def test_assignor_from_dict(self) -> None:
        """Test Assignor.from_dict method."""
        data = {
            "assignorName": "John Smith",
            "executionDate": "2023-01-01",
        }

        assignor = Assignor.from_dict(data)

        assert assignor.assignor_name == "John Smith"
        assert assignor.execution_date == "2023-01-01"

    def test_assignee_from_dict(self) -> None:
        """Test Assignee.from_dict method."""
        data = {
            "assigneeNameText": "Test Company Inc.",
            "assigneeAddress": {
                "cityName": "San Francisco",
                "geographicRegionCode": "CA",
                "countryCode": "US",
            },
        }

        assignee = Assignee.from_dict(data)

        assert assignee.assignee_name_text == "Test Company Inc."
        assert assignee.assignee_address is not None
        assert assignee.assignee_address.city_name == "San Francisco"

    def test_assignment_from_dict(self) -> None:
        """Test Assignment.from_dict method."""
        data = {
            "reelNumber": 12345,
            "frameNumber": 67890,
            "reelAndFrameNumber": "12345/67890",
            "assignmentDocumentLocationURI": "https://example.com/assignment.pdf",
            "assignmentReceivedDate": "2023-01-01",
            "assignmentRecordedDate": "2023-01-15",
            "assignmentMailedDate": "2023-01-20",
            "conveyanceText": "ASSIGNMENT OF ASSIGNORS INTEREST",
            "assignorBag": [
                {
                    "assignorName": "John Smith",
                    "executionDate": "2022-12-15",
                }
            ],
            "assigneeBag": [
                {
                    "assigneeNameText": "Test Company Inc.",
                    "assigneeAddress": {
                        "cityName": "San Francisco",
                        "geographicRegionCode": "CA",
                        "countryCode": "US",
                    },
                }
            ],
            "correspondenceAddressBag": [
                {
                    "cityName": "Washington",
                    "geographicRegionCode": "DC",
                    "countryCode": "US",
                }
            ],
        }

        assignment = Assignment.from_dict(data)

        assert assignment.reel_number == 12345
        assert assignment.frame_number == 67890
        assert assignment.reel_and_frame_number == "12345/67890"
        assert (
            assignment.assignment_document_location_uri
            == "https://example.com/assignment.pdf"
        )
        assert assignment.assignment_received_date == "2023-01-01"
        assert assignment.assignment_recorded_date == "2023-01-15"
        assert assignment.assignment_mailed_date == "2023-01-20"
        assert assignment.conveyance_text == "ASSIGNMENT OF ASSIGNORS INTEREST"
        assert len(assignment.assignor_bag) == 1
        assert assignment.assignor_bag[0].assignor_name == "John Smith"
        assert len(assignment.assignee_bag) == 1
        assert assignment.assignee_bag[0].assignee_name_text == "Test Company Inc."
        assert len(assignment.correspondence_address_bag) == 1
        assert assignment.correspondence_address_bag[0].city_name == "Washington"

    def test_foreign_priority_from_dict(self) -> None:
        """Test ForeignPriority.from_dict method."""
        data = {
            "ipOfficeName": "European Patent Office",
            "filingDate": "2022-01-01",
            "applicationNumberText": "EP12345678",
        }

        foreign_priority = ForeignPriority.from_dict(data)

        assert foreign_priority.ip_office_name == "European Patent Office"
        assert foreign_priority.filing_date == "2022-01-01"
        assert foreign_priority.application_number_text == "EP12345678"

    def test_parent_continuity_from_dict(self) -> None:
        """Test ParentContinuity.from_dict method."""
        data = {
            "firstInventorToFileIndicator": True,
            "parentApplicationStatusCode": 150,
            "parentPatentNumber": "10000000",
            "parentApplicationStatusDescriptionText": "Patented Case",
            "parentApplicationFilingDate": "2020-01-01",
            "parentApplicationNumberText": "12345678",
            "childApplicationNumberText": "87654321",
            "claimParentageTypeCode": "CON",
            "claimParentageTypeCodeDescriptionText": "Continuation",
        }

        parent_continuity = ParentContinuity.from_dict(data)

        assert parent_continuity.first_inventor_to_file_indicator is True
        assert parent_continuity.parent_application_status_code == 150
        assert parent_continuity.parent_patent_number == "10000000"
        assert (
            parent_continuity.parent_application_status_description_text
            == "Patented Case"
        )
        assert parent_continuity.parent_application_filing_date == "2020-01-01"
        assert parent_continuity.parent_application_number_text == "12345678"
        assert parent_continuity.child_application_number_text == "87654321"
        assert parent_continuity.claim_parentage_type_code == "CON"
        assert (
            parent_continuity.claim_parentage_type_code_description_text
            == "Continuation"
        )
        # Check base class fields are mapped correctly
        assert parent_continuity.status_code == 150
        assert parent_continuity.status_description_text == "Patented Case"
        assert parent_continuity.filing_date == "2020-01-01"
        assert parent_continuity.application_number_text == "12345678"
        assert parent_continuity.patent_number == "10000000"

    def test_child_continuity_from_dict(self) -> None:
        """Test ChildContinuity.from_dict method."""
        data = {
            "firstInventorToFileIndicator": True,
            "childApplicationStatusCode": 30,
            "parentApplicationNumberText": "12345678",
            "childApplicationNumberText": "87654321",
            "childApplicationStatusDescriptionText": "Docketed New Case - Ready for Examination",
            "childApplicationFilingDate": "2022-01-01",
            "childPatentNumber": None,
            "claimParentageTypeCode": "CON",
            "claimParentageTypeCodeDescriptionText": "Continuation",
        }

        child_continuity = ChildContinuity.from_dict(data)

        assert child_continuity.first_inventor_to_file_indicator is True
        assert child_continuity.child_application_status_code == 30
        assert child_continuity.parent_application_number_text == "12345678"
        assert child_continuity.child_application_number_text == "87654321"
        assert (
            child_continuity.child_application_status_description_text
            == "Docketed New Case - Ready for Examination"
        )
        assert child_continuity.child_application_filing_date == "2022-01-01"
        assert child_continuity.child_patent_number is None
        assert child_continuity.claim_parentage_type_code == "CON"
        assert (
            child_continuity.claim_parentage_type_code_description_text
            == "Continuation"
        )
        # Check base class fields are mapped correctly
        assert child_continuity.status_code == 30
        assert (
            child_continuity.status_description_text
            == "Docketed New Case - Ready for Examination"
        )
        assert child_continuity.filing_date == "2022-01-01"
        assert child_continuity.application_number_text == "87654321"
        assert child_continuity.patent_number is None

    def test_patent_term_adjustment_history_data_from_dict(self) -> None:
        """Test PatentTermAdjustmentHistoryData.from_dict method."""
        data = {
            "eventDate": "2022-01-01",
            "applicantDayDelayQuantity": 10.0,
            "eventDescriptionText": "Response to Office Action",
            "eventSequenceNumber": 1.0,
            "ipOfficeDayDelayQuantity": 5.0,
            "originatingEventSequenceNumber": 0.0,
            "ptaPTECode": "A",
        }

        pta_history = PatentTermAdjustmentHistoryData.from_dict(data)

        assert pta_history.event_date == "2022-01-01"
        assert pta_history.applicant_day_delay_quantity == 10.0
        assert pta_history.event_description_text == "Response to Office Action"
        assert pta_history.event_sequence_number == 1.0
        assert pta_history.ip_office_day_delay_quantity == 5.0
        assert pta_history.originating_event_sequence_number == 0.0
        assert pta_history.pta_pte_code == "A"

    def test_patent_term_adjustment_data_from_dict(self) -> None:
        """Test PatentTermAdjustmentData.from_dict method."""
        data = {
            "aDelayQuantity": 100.0,
            "adjustmentTotalQuantity": 150.0,
            "applicantDayDelayQuantity": 50.0,
            "bDelayQuantity": 75.0,
            "cDelayQuantity": 25.0,
            "filingDate": "2020-01-01",
            "grantDate": "2023-01-01",
            "nonOverlappingDayQuantity": 175.0,
            "overlappingDayQuantity": 25.0,
            "ipOfficeDayDelayQuantity": 200.0,
            "patentTermAdjustmentHistoryDataBag": [
                {
                    "eventDate": "2022-01-01",
                    "applicantDayDelayQuantity": 10.0,
                    "eventDescriptionText": "Response to Office Action",
                }
            ],
        }

        pta_data = PatentTermAdjustmentData.from_dict(data)

        assert pta_data.a_delay_quantity == 100.0
        assert pta_data.adjustment_total_quantity == 150.0
        assert pta_data.applicant_day_delay_quantity == 50.0
        assert pta_data.b_delay_quantity == 75.0
        assert pta_data.c_delay_quantity == 25.0
        assert pta_data.filing_date == "2020-01-01"
        assert pta_data.grant_date == "2023-01-01"
        assert pta_data.non_overlapping_day_quantity == 175.0
        assert pta_data.overlapping_day_quantity == 25.0
        assert pta_data.ip_office_day_delay_quantity == 200.0
        assert len(pta_data.patent_term_adjustment_history_data_bag) == 1
        assert (
            pta_data.patent_term_adjustment_history_data_bag[0].event_date
            == "2022-01-01"
        )

    def test_event_from_dict(self) -> None:
        """Test Event.from_dict method."""
        data = {
            "eventCode": "COMP",
            "eventDescriptionText": "Application ready for examination",
            "eventDate": "2022-01-01",
        }

        event = Event.from_dict(data)

        assert event.event_code == "COMP"
        assert event.event_description_text == "Application ready for examination"
        assert event.event_date == "2022-01-01"

    def test_document_meta_data_from_dict(self) -> None:
        """Test DocumentMetaData.from_dict method."""
        data = {
            "zipFileName": "test.zip",
            "productIdentifier": "PRODUCT1",
            "fileLocationURI": "https://example.com/test.zip",
            "fileCreateDateTime": "2023-01-01T12:00:00",
            "xmlFileName": "test.xml",
        }

        document_meta = DocumentMetaData.from_dict(data)

        assert document_meta.zip_file_name == "test.zip"
        assert document_meta.product_identifier == "PRODUCT1"
        assert document_meta.file_location_uri == "https://example.com/test.zip"
        assert document_meta.file_create_date_time == "2023-01-01T12:00:00"
        assert document_meta.xml_file_name == "test.xml"

    def test_application_meta_data_from_dict(self) -> None:
        """Test ApplicationMetaData.from_dict method."""
        data = {
            "nationalStageIndicator": True,
            "entityStatusData": {
                "smallEntityStatusIndicator": True,
                "businessEntityStatusCategory": "SMALL",
            },
            "publicationDateBag": ["2022-01-01"],
            "publicationSequenceNumberBag": ["1"],
            "publicationCategoryBag": ["A1"],
            "docketNumber": "TEST-123",
            "firstInventorToFileIndicator": "Y",
            "firstApplicantName": "Test Company Inc.",
            "firstInventorName": "John Smith",
            "applicationConfirmationNumber": 1234,
            "applicationStatusDate": "2022-01-01",
            "applicationStatusDescriptionText": "Docketed New Case - Ready for Examination",
            "filingDate": "2020-01-01",
            "effectiveFilingDate": "2020-01-01",
            "grantDate": None,
            "groupArtUnitNumber": "1600",
            "applicationTypeCode": "14",
            "applicationTypeLabelName": "Regular",
            "applicationTypeCategory": "Utility",
            "inventionTitle": "Test Invention",
            "patentNumber": None,
            "applicationStatusCode": 30,
            "earliestPublicationNumber": "US20220000001A1",
            "earliestPublicationDate": "2022-01-01",
            "pctPublicationNumber": None,
            "pctPublicationDate": None,
            "internationalRegistrationPublicationDate": None,
            "internationalRegistrationNumber": None,
            "examinerNameText": "Smith, John",
            "class": "123",
            "subclass": "456",
            "uspcSymbolText": "123/456",
            "customerNumber": 12345,
            "cpcClassificationBag": ["A01B1/00"],
            "applicantBag": [
                {
                    "applicantNameText": "Test Company Inc.",
                }
            ],
            "inventorBag": [
                {
                    "firstName": "John",
                    "lastName": "Smith",
                    "inventorNameText": "John Smith",
                }
            ],
        }

        app_meta = ApplicationMetaData.from_dict(data)

        assert app_meta.national_stage_indicator is True
        assert app_meta.entity_status_data is not None
        assert app_meta.entity_status_data.small_entity_status_indicator is True
        assert app_meta.publication_date_bag == ["2022-01-01"]
        assert app_meta.publication_sequence_number_bag == ["1"]
        assert app_meta.publication_category_bag == ["A1"]
        assert app_meta.docket_number == "TEST-123"
        assert app_meta.first_inventor_to_file_indicator == "Y"
        assert app_meta.first_applicant_name == "Test Company Inc."
        assert app_meta.first_inventor_name == "John Smith"
        assert app_meta.application_confirmation_number == 1234
        assert app_meta.application_status_date == "2022-01-01"
        assert (
            app_meta.application_status_description_text
            == "Docketed New Case - Ready for Examination"
        )
        assert app_meta.filing_date == "2020-01-01"
        assert app_meta.effective_filing_date == "2020-01-01"
        assert app_meta.grant_date is None
        assert app_meta.group_art_unit_number == "1600"
        assert app_meta.application_type_code == "14"
        assert app_meta.application_type_label_name == "Regular"
        assert app_meta.application_type_category == "Utility"
        assert app_meta.invention_title == "Test Invention"
        assert app_meta.patent_number is None
        assert app_meta.application_status_code == 30
        assert app_meta.earliest_publication_number == "US20220000001A1"
        assert app_meta.earliest_publication_date == "2022-01-01"
        assert app_meta.pct_publication_number is None
        assert app_meta.pct_publication_date is None
        assert app_meta.international_registration_publication_date is None
        assert app_meta.international_registration_number is None
        assert app_meta.examiner_name_text == "Smith, John"
        assert app_meta.class_field == "123"  # Renamed from 'class'
        assert app_meta.subclass == "456"
        assert app_meta.uspc_symbol_text == "123/456"
        assert app_meta.customer_number == 12345
        assert app_meta.cpc_classification_bag == ["A01B1/00"]
        assert len(app_meta.applicant_bag) == 1
        assert app_meta.applicant_bag[0].applicant_name_text == "Test Company Inc."
        assert len(app_meta.inventor_bag) == 1
        assert app_meta.inventor_bag[0].inventor_name_text == "John Smith"

    def test_patent_file_wrapper_from_dict(self) -> None:
        """Test PatentFileWrapper.from_dict method."""
        data = {
            "applicationNumberText": "12345678",
            "applicationMetaData": {
                "inventionTitle": "Test Invention",
                "filingDate": "2020-01-01",
                "applicationStatusCode": 30,
                "applicationStatusDescriptionText": "Docketed New Case - Ready for Examination",
            },
            "correspondenceAddressBag": [
                {
                    "cityName": "Washington",
                    "geographicRegionCode": "DC",
                    "countryCode": "US",
                }
            ],
            "assignmentBag": [
                {
                    "reelNumber": 12345,
                    "frameNumber": 67890,
                    "assignmentRecordedDate": "2023-01-15",
                }
            ],
            "recordAttorney": {
                "customerNumberCorrespondenceData": [
                    {
                        "patronIdentifier": 12345,
                        "organizationStandardName": "Test Law Firm",
                    }
                ],
            },
            "foreignPriorityBag": [
                {
                    "ipOfficeName": "European Patent Office",
                    "filingDate": "2019-01-01",
                    "applicationNumberText": "EP12345678",
                }
            ],
            "parentContinuityBag": [
                {
                    "parentApplicationNumberText": "11111111",
                    "parentApplicationFilingDate": "2018-01-01",
                    "claimParentageTypeCode": "CON",
                }
            ],
            "childContinuityBag": [
                {
                    "childApplicationNumberText": "99999999",
                    "childApplicationFilingDate": "2022-01-01",
                    "claimParentageTypeCode": "CON",
                }
            ],
            "patentTermAdjustmentData": {
                "adjustmentTotalQuantity": 150.0,
                "filingDate": "2020-01-01",
                "grantDate": None,
            },
            "eventDataBag": [
                {
                    "eventCode": "COMP",
                    "eventDescriptionText": "Application ready for examination",
                    "eventDate": "2022-01-01",
                }
            ],
            "pgpubDocumentMetaData": {
                "zipFileName": "pgpub.zip",
                "productIdentifier": "PGPUB",
                "fileLocationURI": "https://example.com/pgpub.zip",
            },
            "grantDocumentMetaData": None,
            "lastIngestionDateTime": "2023-01-01T12:00:00",
        }

        patent_wrapper = PatentFileWrapper.from_dict(data)

        assert patent_wrapper.application_number_text == "12345678"
        assert patent_wrapper.application_meta_data is not None
        assert patent_wrapper.application_meta_data.invention_title == "Test Invention"
        assert len(patent_wrapper.correspondence_address_bag) == 1
        assert patent_wrapper.correspondence_address_bag[0].city_name == "Washington"
        assert len(patent_wrapper.assignment_bag) == 1
        assert patent_wrapper.assignment_bag[0].reel_number == 12345
        assert patent_wrapper.record_attorney is not None
        assert (
            len(patent_wrapper.record_attorney.customer_number_correspondence_data) == 1
        )
        assert (
            patent_wrapper.record_attorney.customer_number_correspondence_data[
                0
            ].patron_identifier
            == 12345
        )
        assert len(patent_wrapper.foreign_priority_bag) == 1
        assert (
            patent_wrapper.foreign_priority_bag[0].ip_office_name
            == "European Patent Office"
        )
        assert len(patent_wrapper.parent_continuity_bag) == 1
        assert (
            patent_wrapper.parent_continuity_bag[0].parent_application_number_text
            == "11111111"
        )
        assert len(patent_wrapper.child_continuity_bag) == 1
        assert (
            patent_wrapper.child_continuity_bag[0].child_application_number_text
            == "99999999"
        )
        assert patent_wrapper.patent_term_adjustment_data is not None
        assert (
            patent_wrapper.patent_term_adjustment_data.adjustment_total_quantity
            == 150.0
        )
        assert patent_wrapper.pgpub_document_meta_data is not None
        assert patent_wrapper.pgpub_document_meta_data.zip_file_name == "pgpub.zip"
        assert patent_wrapper.grant_document_meta_data is None
        assert patent_wrapper.last_ingestion_date_time == "2023-01-01T12:00:00"
