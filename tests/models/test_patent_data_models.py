"""
Tests for the patent_data models.

This module contains consolidated tests for classes in pyUSPTO.models.patent_data.
"""

import csv
import importlib
import io
from datetime import date, datetime, timedelta, timezone, tzinfo
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import pytest

from pyUSPTO.models.patent_data import (
    ASSUMED_NAIVE_TIMEZONE,
    ASSUMED_NAIVE_TIMEZONE_STR,
    ActiveIndicator,
    Address,
    Applicant,
    ApplicationContinuityData,
    ApplicationMetaData,
    Assignee,
    Assignment,
    Assignor,
    Attorney,
    ChildContinuity,
    Continuity,
    CustomerNumberCorrespondence,
    DirectionCategory,
    Document,
    DocumentBag,
    DocumentFormat,
    EntityStatus,
    EventData,
    ForeignPriority,
    Inventor,
    ParentContinuity,
    PatentDataResponse,
    PatentFileWrapper,
    PatentTermAdjustmentData,
    PatentTermAdjustmentHistoryData,
    Person,
    PrintedMetaData,
    PrintedPublication,
    RecordAttorney,
    StatusCode,
    StatusCodeCollection,
    StatusCodeSearchResponse,
    Telecommunication,
    parse_to_date,
    parse_to_datetime_utc,
    parse_yn_to_bool,
    serialize_bool_to_yn,
    serialize_date,
    serialize_datetime_as_iso,
    to_camel_case,
)

# --- Pytest Fixtures ---


@pytest.fixture
def sample_address_data() -> Dict[str, Any]:
    return {
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


@pytest.fixture
def sample_telecommunication_data() -> Dict[str, Any]:
    return {
        "telecommunicationNumber": "555-123-4567",
        "extensionNumber": "123",
        "telecomTypeCode": "PHONE",
    }


@pytest.fixture
def sample_person_base_data() -> Dict[str, Any]:
    return {
        "firstName": "Test",
        "lastName": "Person",
        "namePrefix": "Mr.",
        "nameSuffix": "PhD",
        "preferredName": "T. Person",
        "countryCode": "US",
    }


@pytest.fixture
def sample_applicant_data(
    sample_person_base_data: Dict[str, Any], sample_address_data: Dict[str, Any]
) -> Dict[str, Any]:
    data = sample_person_base_data.copy()
    data.update(
        {
            "applicantNameText": f"{sample_person_base_data['firstName']} {sample_person_base_data['lastName']}",
            "correspondenceAddressBag": [sample_address_data],
        }
    )
    return data


@pytest.fixture
def sample_inventor_data(
    sample_person_base_data: Dict[str, Any], sample_address_data: Dict[str, Any]
) -> Dict[str, Any]:
    data = sample_person_base_data.copy()
    data.update(
        {
            "inventorNameText": f"{sample_person_base_data['firstName']} {sample_person_base_data['lastName']}",
            "correspondenceAddressBag": [sample_address_data],
        }
    )
    return data


@pytest.fixture
def sample_attorney_data(
    sample_person_base_data: Dict[str, Any],
    sample_address_data: Dict[str, Any],
    sample_telecommunication_data: Dict[str, Any],
) -> Dict[str, Any]:
    data = sample_person_base_data.copy()
    data.update(
        {
            "registrationNumber": "12345",
            "activeIndicator": "Y",
            "registeredPractitionerCategory": "Attorney",
            "attorneyAddressBag": [sample_address_data],
            "telecommunicationAddressBag": [sample_telecommunication_data],
        }
    )
    return data


@pytest.fixture
def sample_document_download_format_data() -> Dict[str, Any]:
    return {
        "mimeTypeIdentifier": "application/pdf",
        "downloadUrl": "https://example.com/doc.pdf",
        "pageTotalQuantity": 10,
    }


@pytest.fixture
def sample_document_meta_data_data() -> Dict[str, Any]:
    return {
        "zipFileName": "test.zip",
        "productIdentifier": "PRODUCT1",
        "fileLocationURI": "https://example.com/test.zip",
        "fileCreateDateTime": "2023-01-01T12:00:00Z",
        "xmlFileName": "test.xml",
    }


@pytest.fixture
def sample_parent_continuity_data() -> Dict[str, Any]:
    return {
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


@pytest.fixture
def sample_child_continuity_data() -> Dict[str, Any]:
    return {
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


@pytest.fixture
def sample_application_meta_data(
    sample_applicant_data: Dict[str, Any],
    sample_inventor_data: Dict[str, Any],
    sample_address_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Provides a comprehensive dictionary of data for ApplicationMetaData,
    suitable for round-trip (from_dict -> to_dict) testing.
    """
    return {
        "nationalStageIndicator": True,
        "entityStatusData": {
            "smallEntityStatusIndicator": True,
            "businessEntityStatusCategory": "SMALL",
        },
        "publicationDateBag": ["2022-01-15", "2022-02-20"],
        "publicationSequenceNumberBag": ["1", "2", "3"],
        "publicationCategoryBag": ["A1", "B2"],
        "docketNumber": None,
        "firstInventorToFileIndicator": "Y",
        "firstApplicantName": "Innovate Corp.",
        "firstInventorName": "Doe, John A.",
        "applicationConfirmationNumber": "9876",
        "applicationStatusDate": "2023-03-01",
        "applicationStatusDescriptionText": "Non-Final Rejection",
        "filingDate": "2021-06-10",
        "effectiveFilingDate": "2021-06-01",
        "grantDate": "2024-01-05",
        "groupArtUnitNumber": "2456",
        "applicationTypeCode": "UTL",
        "applicationTypeLabelName": "Utility",
        "applicationTypeCategory": "Nonprovisional",
        "inventionTitle": "System and Method for Advanced Data Processing",
        "patentNumber": "12345678",
        "applicationStatusCode": 110,
        "earliestPublicationNumber": "US20220012345A1",
        "earliestPublicationDate": "2022-01-15",
        "pctPublicationNumber": "WO2022012345A1",
        "pctPublicationDate": "2022-01-20",
        "internationalRegistrationPublicationDate": "2022-02-01",
        "internationalRegistrationNumber": "DM/123456",
        "examinerNameText": "Smith, Jane E.",
        "class": "707",
        "subclass": "E17",
        "uspcSymbolText": "707/E17.014",
        "customerNumber": 98765,
        "cpcClassificationBag": ["G06F16/24578", "H04L67/10"],
        "applicantBag": [
            sample_applicant_data,
            {
                "firstName": "Global",
                "lastName": "Solutions Ltd.",
                "applicantNameText": "Global Solutions Ltd.",
                "correspondenceAddressBag": [sample_address_data],
            },
        ],
        "inventorBag": [
            sample_inventor_data,
            {
                "firstName": "Alice",
                "middleName": "B.",
                "lastName": "Wonder",
                "inventorNameText": "Wonder, Alice B.",
                "correspondenceAddressBag": [],
                "countryCode": "CA",
            },
        ],
    }


@pytest.fixture
def patent_data_sample(
    sample_application_meta_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Provides a sample dictionary representing a PatentDataResponse,
    suitable for testing.
    """
    patent_file_wrapper_1 = {
        "applicationNumberText": "16000001",
        "applicationMetaData": sample_application_meta_data,
        "lastIngestionDateTime": "2023-01-01T10:00:00Z",
        "pgpubDocumentMetaData": {
            "zipFileName": "PGPUB_16000001.zip",
            "productIdentifier": "PGPUB",
            "fileLocationURI": "s3://uspto-pair/applications/16000001/pgpub.zip",
            "fileCreateDateTime": "2022-12-15T08:30:00Z",
            "xmlFileName": "US20220012345A1.xml",
        },
        "grantDocumentMetaData": None,
        "correspondenceAddressBag": [
            {
                "nameLineOneText": "Tech Innovations LLC",
                "addressLineOneText": "456 Innovation Drive",
                "cityName": "Future City",
                "geographicRegionCode": "FC",
                "postalCode": "67890",
                "countryCode": "US",
            }
        ],
        "assignmentBag": [],
        "eventDataBag": [
            {
                "eventCode": "CTNF",
                "eventDescriptionText": "Non-Final Rejection",
                "eventDate": "2023-03-01",
            },
            {
                "eventCode": "RESP",
                "eventDescriptionText": "Response to Non-Final Rejection",
                "eventDate": "2023-09-01",
            },
        ],
    }

    another_app_meta_data = sample_application_meta_data.copy()
    another_app_meta_data["inventionTitle"] = "Another Revolutionary Invention"
    another_app_meta_data["filingDate"] = "2022-02-02"
    another_app_meta_data["patentNumber"] = "9999999"
    another_app_meta_data["firstInventorName"] = "Smith, Jane Q."
    another_app_meta_data["applicationTypeLabelName"] = "Design"
    another_app_meta_data["publicationCategoryBag"] = ["S1"]
    another_app_meta_data["applicationStatusDescriptionText"] = "Allowed"
    another_app_meta_data["applicationStatusDate"] = "2023-10-10"

    patent_file_wrapper_2 = {
        "applicationNumberText": "17000002",
        "applicationMetaData": another_app_meta_data,
        "lastIngestionDateTime": "2023-02-15T11:00:00Z",
        "pgpubDocumentMetaData": None,
        "grantDocumentMetaData": {
            "zipFileName": "GRANT_17000002.zip",
            "productIdentifier": "GRANT",
            "fileLocationURI": "s3://uspto-pair/applications/17000002/grant.zip",
            "fileCreateDateTime": "2024-01-10T09:00:00Z",
            "xmlFileName": "US9999999B2.xml",
        },
    }

    return {
        "count": 2,
        "patentFileWrapperDataBag": [patent_file_wrapper_1, patent_file_wrapper_2],
    }


@pytest.fixture
def sample_assignor_data() -> Dict[str, Any]:
    """Provides sample data for an Assignor."""
    return {
        "assignorName": "Original Tech Holder Inc.",
        "executionDate": "2022-11-15",
    }


@pytest.fixture
def sample_assignee_data(sample_address_data: Dict[str, Any]) -> Dict[str, Any]:
    """Provides sample data for an Assignee."""
    return {
        "assigneeNameText": "New Tech Acquirer LLC",
        "assigneeAddress": sample_address_data,
    }


@pytest.fixture
def sample_assignment_data(
    sample_assignor_data: Dict[str, Any],
    sample_assignee_data: Dict[str, Any],
    sample_address_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Provides sample data for an Assignment."""
    return {
        "reelNumber": "R00123",
        "frameNumber": "F00456",
        "reelAndFrameNumber": "R00123/F00456",
        "assignmentDocumentLocationURI": "https://assignments.uspto.gov/assignments/assignment-R00123-F00456.pdf",
        "assignmentReceivedDate": "2023-01-10",
        "assignmentRecordedDate": "2023-01-20",
        "assignmentMailedDate": "2023-01-25",
        "conveyanceText": "ASSIGNMENT OF ASSIGNORS INTEREST",
        "assignorBag": [
            sample_assignor_data,
            {
                "assignorName": "Another Seller Corp.",
                "executionDate": "2022-12-01",
            },
        ],
        "assigneeBag": [
            sample_assignee_data,
            {
                "assigneeNameText": "Tech Innovators Co.",
                "assigneeAddress": None,
            },
        ],
        "correspondenceAddressBag": [sample_address_data],
    }


@pytest.fixture
def sample_document_download_format_data_for_doc_fixture() -> Dict[str, Any]:
    """Provides sample data for DocumentDownloadFormat, specifically for the Document fixture."""
    return {
        "mimeTypeIdentifier": "application/pdf",
        "downloadURI": "https://pair.uspto.gov/docs/12345678/doc1.pdf",
        "pageTotalQuantity": 15,
    }


@pytest.fixture
def sample_document_data(
    sample_document_download_format_data_for_doc_fixture: Dict[str, Any],
) -> Dict[str, Any]:
    """Provides sample data for a Document."""
    return {
        "applicationNumberText": "16000001",
        "officialDate": "2023-03-15T10:30:00Z",
        "documentIdentifier": "OFFICE_ACTION_NON_FINAL",
        "documentCode": "CTNF",
        "documentCodeDescriptionText": "Non-Final Rejection",
        "documentDirectionCategory": "OUTGOING",
        "downloadOptionBag": [
            sample_document_download_format_data_for_doc_fixture,
            {
                "mimeTypeIdentifier": "application/xml",
                "downloadURI": "https://pair.uspto.gov/docs/12345678/doc1.xml",
                "pageTotalQuantity": None,
            },
        ],
    }


@pytest.fixture
def sample_pta_history_data() -> Dict[str, Any]:
    """Provides sample data for PatentTermAdjustmentHistoryData."""
    return {
        "eventDate": "2022-05-01",
        "applicantDayDelayQuantity": 5.0,
        "eventDescriptionText": "Applicant Delay - Late Response",
        "eventSequenceNumber": 2.0,
        "ipOfficeDayDelayQuantity": 0.0,
        "originatingEventSequenceNumber": 1.0,
        "ptaPTECode": "APL",
    }


@pytest.fixture
def sample_patent_term_adjustment_data(
    sample_pta_history_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Provides sample data for PatentTermAdjustmentData."""
    return {
        "aDelayQuantity": 100.0,
        "adjustmentTotalQuantity": 120.0,
        "applicantDayDelayQuantity": 10.0,
        "bDelayQuantity": 30.0,
        "cDelayQuantity": 0.0,
        "filingDate": "2020-01-15",
        "grantDate": "2023-11-20",
        "nonOverlappingDayQuantity": 120.0,
        "overlappingDayQuantity": 20.0,
        "ipOfficeDayDelayQuantity": 130.0,
        "patentTermAdjustmentHistoryDataBag": [
            sample_pta_history_data,
            {
                "eventDate": "2021-08-10",
                "applicantDayDelayQuantity": 0.0,
                "eventDescriptionText": "USPTO Delay - Examination",
                "eventSequenceNumber": 1.0,
                "ipOfficeDayDelayQuantity": 15.0,
                "originatingEventSequenceNumber": 0.0,
                "ptaPTECode": "PTO",
            },
        ],
    }


@pytest.fixture
def sample_customer_number_correspondence_data(
    sample_address_data: Dict[str, Any], sample_telecommunication_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Provides sample data for CustomerNumberCorrespondence."""
    return {
        "patronIdentifier": 778899,
        "organizationStandardName": "Major Law Firm LLP",
        "powerOfAttorneyAddressBag": [sample_address_data],
        "telecommunicationAddressBag": [sample_telecommunication_data],
    }


@pytest.fixture
def sample_record_attorney_data(
    sample_customer_number_correspondence_data: Dict[str, Any],
    sample_attorney_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Provides sample data for RecordAttorney."""
    attorney_2_data = sample_attorney_data.copy()
    attorney_2_data["registrationNumber"] = "67890"
    attorney_2_data["firstName"] = "Jane"
    attorney_2_data["lastName"] = "Practitioner"

    return {
        "customerNumberCorrespondenceData": [
            sample_customer_number_correspondence_data
        ],
        "powerOfAttorneyBag": [sample_attorney_data],
        "attorneyBag": [
            sample_attorney_data,
            attorney_2_data,
        ],
    }


# --- Test Classes ---
class TestDirectionCategory:
    """Tests for the DirectionCategory enum class."""

    def test_direction_category_enum(self) -> None:
        assert DirectionCategory("INCOMING") == DirectionCategory.INCOMING
        assert DirectionCategory("OUTGOING") == DirectionCategory.OUTGOING
        with pytest.raises(ValueError):
            DirectionCategory("INVALID")


class TestActiveIndicator:
    """Tests for the ActiveIndicator enum class."""

    def test_active_indicator_enum(self) -> None:
        assert ActiveIndicator("Y") == ActiveIndicator.YES
        assert ActiveIndicator("N") == ActiveIndicator.NO
        assert ActiveIndicator("true") == ActiveIndicator.TRUE
        assert ActiveIndicator("false") == ActiveIndicator.FALSE
        assert ActiveIndicator("Active") == ActiveIndicator.ACTIVE
        assert ActiveIndicator("y") == ActiveIndicator.YES
        assert ActiveIndicator("n") == ActiveIndicator.NO
        assert ActiveIndicator("TRUE") == ActiveIndicator.TRUE
        assert ActiveIndicator("FALSE") == ActiveIndicator.FALSE
        assert ActiveIndicator("active") == ActiveIndicator.ACTIVE

        with pytest.raises(ValueError):
            ActiveIndicator("Invalid")
        with pytest.raises(ValueError):
            ActiveIndicator(None)


class TestDocumentDownloadFormat:
    """Tests for the DocumentDownloadFormat class."""

    def test_document_download_format_from_dict(
        self, sample_document_download_format_data: Dict[str, Any]
    ) -> None:
        fmt = DocumentFormat.from_dict(sample_document_download_format_data)
        assert (
            fmt.mime_type_identifier
            == sample_document_download_format_data["mimeTypeIdentifier"]
        )
        assert fmt.download_url == sample_document_download_format_data["downloadUrl"]
        assert (
            fmt.page_total_quantity
            == sample_document_download_format_data["pageTotalQuantity"]
        )

    def test_document_download_format_to_dict(
        self, sample_document_download_format_data: Dict[str, Any]
    ) -> None:
        fmt = DocumentFormat(
            mime_type_identifier=sample_document_download_format_data[
                "mimeTypeIdentifier"
            ],
            download_url=sample_document_download_format_data["downloadUrl"],
            page_total_quantity=sample_document_download_format_data[
                "pageTotalQuantity"
            ],
        )
        data = fmt.to_dict()
        expected_data = sample_document_download_format_data.copy()
        assert data == expected_data

    def test_from_dict_empty(self) -> None:
        fmt = DocumentFormat.from_dict({})
        assert fmt.mime_type_identifier is None
        assert fmt.download_url is None
        assert fmt.page_total_quantity is None

    def test_to_dict_empty(self) -> None:
        fmt = DocumentFormat()
        assert fmt.to_dict() == {
            "mimeTypeIdentifier": None,
            "downloadUrl": None,
            "pageTotalQuantity": None,
        }

    def test_document_download_format_repr(self) -> None:
        fmt = DocumentFormat(
            mime_type_identifier="application/pdf",
            download_url="http://example.com/doc.pdf",
            page_total_quantity=3,
        )
        expected = "DocumentFormat(mime_type=application/pdf, pages=3)"
        assert repr(fmt) == expected


class TestDocument:
    """Tests for the Document class."""

    def test_document_from_dict_basic(self) -> None:
        data = {
            "documentIdentifier": "doc123",
            "documentCode": "CODE_X",
            "officialDate": "2023-03-15T10:30:00Z",
            "documentDirectionCategory": "INCOMING",
            "downloadOptionBag": [
                {
                    "mimeTypeIdentifier": "application/pdf",
                    "downloadURI": "url1",
                    "pageTotalQuantity": 10,
                }
            ],
        }
        doc = Document.from_dict(data)

        assert doc.document_identifier == "doc123"
        assert doc.document_code == "CODE_X"
        assert doc.official_date == datetime(
            2023, 3, 15, 10, 30, 0, tzinfo=timezone.utc
        )
        assert doc.direction_category == DirectionCategory.INCOMING
        assert len(doc.document_formats) == 1
        assert doc.document_formats[0].mime_type_identifier == "application/pdf"

    def test_document_to_dict_basic(self) -> None:
        doc = Document(
            document_identifier="doc123",
            document_code="CODE_X",
            official_date=datetime(2023, 3, 15, 10, 30, 0, tzinfo=timezone.utc),
            direction_category=DirectionCategory.OUTGOING,
            document_formats=[
                DocumentFormat(mime_type_identifier="image/tiff", page_total_quantity=5)
            ],
        )
        data = doc.to_dict()
        assert data["documentIdentifier"] == "doc123"
        assert data["officialDate"] == "2023-03-15T10:30:00Z"
        assert data["documentDirectionCategory"] == "OUTGOING"
        assert len(data["downloadOptionBag"]) == 1
        assert data["downloadOptionBag"][0]["mimeTypeIdentifier"] == "image/tiff"
        assert data["downloadOptionBag"][0]["pageTotalQuantity"] == 5

    def test_document_from_dict_unknown_enum(
        self, capsys: pytest.CaptureFixture
    ) -> None:
        """Test Document.from_dict with an unknown direction category."""
        data = {"documentDirectionCategory": "UNKNOWN_DIRECTION"}
        doc = Document.from_dict(data)
        assert doc.direction_category is None
        captured = capsys.readouterr()
        assert (
            "Warning: Unknown document direction category 'UNKNOWN_DIRECTION'."
            in captured.out
        )

    def test_document_to_dict_all_none_and_empty_lists(self) -> None:
        """Test Document.to_dict when all fields are None or empty lists."""
        doc = Document(
            application_number_text=None,
            official_date=None,
            document_identifier=None,
            document_code=None,
            document_code_description_text=None,
            direction_category=None,
            document_formats=[],
        )
        data = doc.to_dict()
        assert data == {}

    def test_document_repr(self) -> None:
        doc = Document(
            document_identifier="doc123",
            document_code="CODE_X",
            official_date=datetime(2023, 3, 15, 10, 30, 0, tzinfo=timezone.utc),
            direction_category=DirectionCategory.OUTGOING,
            document_formats=[],
        )
        expected = "Document(id=doc123, code=CODE_X, date=2023-03-15)"
        assert repr(doc) == expected

    def test_document_roundtrip(self, sample_document_data: Dict[str, Any]) -> None:
        """
        Tests the round-trip serialization for the Document class.
        """
        original_document = Document.from_dict(data=sample_document_data)
        intermediate_dict = original_document.to_dict()
        reconstructed_document = Document.from_dict(data=intermediate_dict)
        assert original_document == reconstructed_document


class TestDocumentBag:
    """Tests for the DocumentBag class."""

    def test_document_bag_from_dict(self) -> None:
        data = {
            "documentBag": [
                {"documentIdentifier": "doc1"},
                {"documentIdentifier": "doc2"},
            ]
        }
        doc_bag = DocumentBag.from_dict(data)
        assert len(doc_bag.documents) == 2
        assert isinstance(doc_bag.documents[0], Document)
        assert doc_bag.documents[0].document_identifier == "doc1"
        assert doc_bag.documents[1].document_identifier == "doc2"
        assert len(doc_bag) == 2
        assert doc_bag[0].document_identifier == "doc1"

    def test_document_bag_to_dict(self) -> None:
        doc1 = Document(document_identifier="doc1")
        doc2 = Document(document_identifier="doc2")
        doc_bag = DocumentBag(documents=[doc1, doc2])
        data = doc_bag.to_dict()

        assert "documentBag" in data
        assert len(data["documentBag"]) == 2
        assert data["documentBag"][0] == {"documentIdentifier": "doc1"}
        assert data["documentBag"][1] == {"documentIdentifier": "doc2"}

    def test_document_bag_from_dict_empty(self) -> None:
        doc_bag = DocumentBag.from_dict({})
        assert len(doc_bag.documents) == 0
        doc_bag_empty_list = DocumentBag.from_dict({"documentBag": []})
        assert len(doc_bag_empty_list.documents) == 0

    def test_document_bag_from_dict_not_a_list(self) -> None:
        """Test DocumentBag.from_dict when 'documentBag' is not a list."""
        data = {"documentBag": "not_a_list_value"}
        doc_bag = DocumentBag.from_dict(data)
        assert len(doc_bag.documents) == 0

        data_int = {"documentBag": 123}
        doc_bag_int = DocumentBag.from_dict(data_int)
        assert len(doc_bag_int.documents) == 0

    def test_document_bag_iterable(self) -> None:
        doc1 = Document(document_identifier="doc1")
        doc_bag = DocumentBag(documents=[doc1])
        count = 0
        for doc in doc_bag:
            assert doc.document_identifier == "doc1"
            count += 1
        assert count == 1


class TestAddress:
    """Tests for the Address class."""

    def test_address_from_dict(self, sample_address_data: Dict[str, Any]) -> None:
        address = Address.from_dict(sample_address_data)
        for key, value in sample_address_data.items():
            snake_case_key = "".join(
                ["_" + i.lower() if i.isupper() else i for i in key]
            ).lstrip("_")
            assert getattr(address, snake_case_key) == value

    def test_address_to_dict(self, sample_address_data: Dict[str, Any]) -> None:
        address = Address(
            **{
                "".join(["_" + i.lower() if i.isupper() else i for i in k]).lstrip(
                    "_"
                ): v
                for k, v in sample_address_data.items()
            }
        )
        assert address.to_dict() == sample_address_data

    def test_address_from_dict_empty(self) -> None:
        address = Address.from_dict({})
        for field_name in Address.__annotations__:
            assert getattr(address, field_name) is None

    def test_address_to_dict_empty(self) -> None:
        address = Address()
        expected_camel_case_empty_dict = {
            "nameLineOneText": None,
            "nameLineTwoText": None,
            "addressLineOneText": None,
            "addressLineTwoText": None,
            "addressLineThreeText": None,
            "addressLineFourText": None,
            "geographicRegionName": None,
            "geographicRegionCode": None,
            "postalCode": None,
            "cityName": None,
            "countryCode": None,
            "countryName": None,
            "postalAddressCategory": None,
            "correspondentNameText": None,
        }
        assert address.to_dict() == expected_camel_case_empty_dict


class TestTelecommunication:
    """Tests for the Telecommunication class."""

    def test_telecommunication_from_dict(
        self, sample_telecommunication_data: Dict[str, Any]
    ) -> None:
        telecom = Telecommunication.from_dict(sample_telecommunication_data)
        assert (
            telecom.telecommunication_number
            == sample_telecommunication_data["telecommunicationNumber"]
        )
        assert (
            telecom.extension_number == sample_telecommunication_data["extensionNumber"]
        )
        assert (
            telecom.telecom_type_code
            == sample_telecommunication_data["telecomTypeCode"]
        )

    def test_telecommunication_to_dict(
        self, sample_telecommunication_data: Dict[str, Any]
    ) -> None:
        telecom = Telecommunication(
            telecommunication_number=sample_telecommunication_data[
                "telecommunicationNumber"
            ],
            extension_number=sample_telecommunication_data["extensionNumber"],
            telecom_type_code=sample_telecommunication_data["telecomTypeCode"],
        )
        assert telecom.to_dict() == sample_telecommunication_data

    def test_telecommunication_from_dict_empty(self) -> None:
        telecom = Telecommunication.from_dict({})
        assert telecom.telecommunication_number is None
        assert telecom.extension_number is None
        assert telecom.telecom_type_code is None

    def test_telecommunication_to_dict_empty(self) -> None:
        telecom = Telecommunication()
        assert telecom.to_dict() == {
            "telecommunicationNumber": None,
            "extensionNumber": None,
            "telecomTypeCode": None,
        }


class TestPerson:
    """Tests for the Person base class."""

    def test_person_to_dict(self, sample_person_base_data: Dict[str, Any]) -> None:
        data_snake = {
            "first_name": sample_person_base_data["firstName"],
            "middle_name": sample_person_base_data.get("middleName"),
            "last_name": sample_person_base_data["lastName"],
            "name_prefix": sample_person_base_data.get("namePrefix"),
            "name_suffix": sample_person_base_data.get("nameSuffix"),
            "preferred_name": sample_person_base_data.get("preferredName"),
            "country_code": sample_person_base_data.get("countryCode"),
        }
        person = Person(**data_snake)
        person_dict = person.to_dict()

        expected_dict = {}
        for k, v_model in sample_person_base_data.items():
            if v_model is not None:
                expected_dict[k] = v_model
        assert person_dict == expected_dict

    def test_person_to_dict_with_nones(self) -> None:
        person = Person(first_name="OnlyFirst")
        assert person.to_dict() == {"firstName": "OnlyFirst"}


class TestApplicant:
    """Tests for the Applicant class."""

    def test_applicant_from_dict(self, sample_applicant_data: Dict[str, Any]) -> None:
        applicant = Applicant.from_dict(sample_applicant_data)
        assert applicant.first_name == sample_applicant_data["firstName"]
        assert applicant.last_name == sample_applicant_data["lastName"]
        assert (
            applicant.applicant_name_text == sample_applicant_data["applicantNameText"]
        )
        assert len(applicant.correspondence_address_bag) == 1
        assert (
            applicant.correspondence_address_bag[0].city_name
            == sample_applicant_data["correspondenceAddressBag"][0]["cityName"]
        )

    def test_applicant_to_dict(
        self, sample_applicant_data: Dict[str, Any], sample_address_data: Dict[str, Any]
    ) -> None:
        applicant = Applicant(
            first_name=sample_applicant_data["firstName"],
            last_name=sample_applicant_data["lastName"],
            applicant_name_text=sample_applicant_data["applicantNameText"],
            correspondence_address_bag=[Address.from_dict(sample_address_data)],
        )
        data_dict = applicant.to_dict()
        assert data_dict["firstName"] == sample_applicant_data["firstName"]
        assert (
            data_dict["applicantNameText"] == sample_applicant_data["applicantNameText"]
        )
        assert len(data_dict["correspondenceAddressBag"]) == 1
        assert (
            data_dict["correspondenceAddressBag"][0]["cityName"]
            == sample_address_data["cityName"]
        )

    def test_applicant_from_dict_empty(self) -> None:
        applicant = Applicant.from_dict({})
        assert applicant.first_name is None
        assert applicant.applicant_name_text is None
        assert applicant.correspondence_address_bag == []

    def test_applicant_to_dict_empty_fields(self) -> None:
        applicant = Applicant(first_name="Test", correspondence_address_bag=[])
        data = applicant.to_dict()
        assert data == {"firstName": "Test"}


class TestInventor:
    """Tests for the Inventor class."""

    def test_inventor_from_dict(self, sample_inventor_data: Dict[str, Any]) -> None:
        inventor = Inventor.from_dict(sample_inventor_data)
        assert inventor.first_name == sample_inventor_data["firstName"]
        assert inventor.last_name == sample_inventor_data["lastName"]
        assert inventor.inventor_name_text == sample_inventor_data["inventorNameText"]
        assert len(inventor.correspondence_address_bag) == 1
        assert (
            inventor.correspondence_address_bag[0].city_name
            == sample_inventor_data["correspondenceAddressBag"][0]["cityName"]
        )

    def test_inventor_to_dict(
        self, sample_inventor_data: Dict[str, Any], sample_address_data: Dict[str, Any]
    ) -> None:
        inventor = Inventor(
            first_name=sample_inventor_data["firstName"],
            last_name=sample_inventor_data["lastName"],
            inventor_name_text=sample_inventor_data["inventorNameText"],
            correspondence_address_bag=[Address.from_dict(sample_address_data)],
        )
        data_dict = inventor.to_dict()
        assert data_dict["firstName"] == sample_inventor_data["firstName"]
        assert data_dict["inventorNameText"] == sample_inventor_data["inventorNameText"]
        assert len(data_dict["correspondenceAddressBag"]) == 1
        assert (
            data_dict["correspondenceAddressBag"][0]["cityName"]
            == sample_address_data["cityName"]
        )

    def test_inventor_to_dict_empty_bag(self) -> None:
        inventor = Inventor(
            inventor_name_text="Test Inventor", correspondence_address_bag=[]
        )
        data = inventor.to_dict()
        assert data == {"inventorNameText": "Test Inventor"}


class TestAttorney:
    """Tests for the Attorney class."""

    def test_attorney_from_dict(self, sample_attorney_data: Dict[str, Any]) -> None:
        attorney = Attorney.from_dict(sample_attorney_data)
        assert attorney.first_name == sample_attorney_data["firstName"]
        assert (
            attorney.registration_number == sample_attorney_data["registrationNumber"]
        )
        assert attorney.active_indicator == sample_attorney_data["activeIndicator"]
        assert len(attorney.attorney_address_bag) == 1
        assert (
            attorney.attorney_address_bag[0].city_name
            == sample_attorney_data["attorneyAddressBag"][0]["cityName"]
        )
        assert len(attorney.telecommunication_address_bag) == 1
        assert (
            attorney.telecommunication_address_bag[0].telecommunication_number
            == sample_attorney_data["telecommunicationAddressBag"][0][
                "telecommunicationNumber"
            ]
        )

    def test_attorney_to_dict(
        self,
        sample_attorney_data: Dict[str, Any],
        sample_address_data: Dict[str, Any],
        sample_telecommunication_data: Dict[str, Any],
    ) -> None:
        attorney = Attorney(
            first_name=sample_attorney_data["firstName"],
            last_name=sample_attorney_data["lastName"],
            registration_number=sample_attorney_data["registrationNumber"],
            active_indicator=sample_attorney_data["activeIndicator"],
            registered_practitioner_category=sample_attorney_data[
                "registeredPractitionerCategory"
            ],
            attorney_address_bag=[Address.from_dict(sample_address_data)],
            telecommunication_address_bag=[
                Telecommunication.from_dict(sample_telecommunication_data)
            ],
        )
        data_dict = attorney.to_dict()
        assert data_dict["firstName"] == sample_attorney_data["firstName"]
        assert (
            data_dict["registrationNumber"]
            == sample_attorney_data["registrationNumber"]
        )
        assert len(data_dict["attorneyAddressBag"]) == 1
        assert (
            data_dict["attorneyAddressBag"][0]["cityName"]
            == sample_address_data["cityName"]
        )
        assert len(data_dict["telecommunicationAddressBag"]) == 1
        assert (
            data_dict["telecommunicationAddressBag"][0]["telecommunicationNumber"]
            == sample_telecommunication_data["telecommunicationNumber"]
        )

    def test_attorney_to_dict_empty_bags(self) -> None:
        attorney = Attorney(
            registration_number="Reg123",
            attorney_address_bag=[],
            telecommunication_address_bag=[],
        )
        data = attorney.to_dict()
        assert data == {"registrationNumber": "Reg123"}


class TestEntityStatus:
    """Tests for the EntityStatus class."""

    def test_entity_status_from_dict(self) -> None:
        data = {
            "smallEntityStatusIndicator": True,
            "businessEntityStatusCategory": "SMALL",
        }
        entity_status = EntityStatus.from_dict(data)
        assert entity_status.small_entity_status_indicator is True
        assert entity_status.business_entity_status_category == "SMALL"

    def test_entity_status_to_dict(self) -> None:
        entity_status = EntityStatus(
            small_entity_status_indicator=False, business_entity_status_category="LARGE"
        )
        data = entity_status.to_dict()
        assert data["smallEntityStatusIndicator"] is False
        assert data["businessEntityStatusCategory"] == "LARGE"


class TestCustomerNumberCorrespondence:
    """Tests for the CustomerNumberCorrespondence class."""

    def test_customer_number_correspondence_from_dict(
        self,
        sample_address_data: Dict[str, Any],
        sample_telecommunication_data: Dict[str, Any],
    ) -> None:
        data = {
            "patronIdentifier": 12345,
            "organizationStandardName": "Test Law Firm",
            "powerOfAttorneyAddressBag": [sample_address_data],
            "telecommunicationAddressBag": [sample_telecommunication_data],
        }
        cust_corr = CustomerNumberCorrespondence.from_dict(data)
        assert cust_corr.patron_identifier == 12345
        assert cust_corr.organization_standard_name == "Test Law Firm"
        assert len(cust_corr.power_of_attorney_address_bag) == 1
        assert (
            cust_corr.power_of_attorney_address_bag[0].city_name
            == sample_address_data["cityName"]
        )
        assert len(cust_corr.telecommunication_address_bag) == 1
        assert (
            cust_corr.telecommunication_address_bag[0].telecom_type_code
            == sample_telecommunication_data["telecomTypeCode"]
        )

    def test_customer_number_correspondence_to_dict(
        self,
        sample_address_data: Dict[str, Any],
        sample_telecommunication_data: Dict[str, Any],
    ) -> None:
        cust_corr = CustomerNumberCorrespondence(
            patron_identifier=54321,
            organization_standard_name="Another Firm",
            power_of_attorney_address_bag=[Address.from_dict(sample_address_data)],
            telecommunication_address_bag=[
                Telecommunication.from_dict(sample_telecommunication_data)
            ],
        )
        data = cust_corr.to_dict()
        assert data["patronIdentifier"] == 54321
        assert data["organizationStandardName"] == "Another Firm"
        assert len(data["powerOfAttorneyAddressBag"]) == 1
        assert len(data["telecommunicationAddressBag"]) == 1

    def test_customer_number_correspondence_to_dict_empty_bags(self) -> None:
        cust_corr = CustomerNumberCorrespondence(
            patron_identifier=777,
            power_of_attorney_address_bag=[],
            telecommunication_address_bag=[],
        )
        data = cust_corr.to_dict()
        assert data == {"patronIdentifier": 777}


class TestRecordAttorney:
    """Tests for the RecordAttorney class."""

    def test_record_attorney_from_dict(
        self, sample_attorney_data: Dict[str, Any]
    ) -> None:
        data = {
            "customerNumberCorrespondenceData": [
                {"patronIdentifier": 12345, "organizationStandardName": "Test Law Firm"}
            ],
            "powerOfAttorneyBag": [sample_attorney_data],
            "attorneyBag": [sample_attorney_data],
        }
        record_attorney = RecordAttorney.from_dict(data)
        assert len(record_attorney.customer_number_correspondence_data) == 1
        assert (
            record_attorney.customer_number_correspondence_data[0].patron_identifier
            == 12345
        )
        assert len(record_attorney.power_of_attorney_bag) == 1
        assert (
            record_attorney.power_of_attorney_bag[0].first_name
            == sample_attorney_data["firstName"]
        )
        assert len(record_attorney.attorney_bag) == 1
        assert (
            record_attorney.attorney_bag[0].registration_number
            == sample_attorney_data["registrationNumber"]
        )

    def test_record_attorney_to_dict(
        self, sample_attorney_data: Dict[str, Any]
    ) -> None:
        attorney_obj = Attorney.from_dict(sample_attorney_data)
        cust_corr_obj = CustomerNumberCorrespondence(patron_identifier=999)

        record_attorney = RecordAttorney(
            customer_number_correspondence_data=[cust_corr_obj],
            power_of_attorney_bag=[attorney_obj],
            attorney_bag=[attorney_obj],
        )
        data = record_attorney.to_dict()
        assert len(data["customerNumberCorrespondenceData"]) == 1
        assert data["customerNumberCorrespondenceData"][0]["patronIdentifier"] == 999
        assert len(data["powerOfAttorneyBag"]) == 1
        assert (
            data["powerOfAttorneyBag"][0]["firstName"]
            == sample_attorney_data["firstName"]
        )
        assert len(data["attorneyBag"]) == 1

    def test_record_attorney_to_dict_all_empty_bags(self) -> None:
        record_attorney = RecordAttorney(
            customer_number_correspondence_data=[],
            power_of_attorney_bag=[],
            attorney_bag=[],
        )
        data = record_attorney.to_dict()
        assert data == {}

    def test_record_attorney_roundtrip(
        self, sample_record_attorney_data: Dict[str, Any]
    ) -> None:
        """
        Tests the round-trip serialization for the RecordAttorney class.
        """
        original_record_attorney = RecordAttorney.from_dict(
            data=sample_record_attorney_data
        )
        intermediate_dict = original_record_attorney.to_dict()
        reconstructed_record_attorney = RecordAttorney.from_dict(data=intermediate_dict)
        assert original_record_attorney == reconstructed_record_attorney


class TestAssignor:
    """Tests for the Assignor class."""

    def test_assignor_from_dict(self) -> None:
        data = {"assignorName": "John Smith", "executionDate": "2023-01-01"}
        assignor = Assignor.from_dict(data)
        assert assignor.assignor_name == "John Smith"
        assert assignor.execution_date == date(2023, 1, 1)

    def test_assignor_to_dict(self) -> None:
        assignor = Assignor(assignor_name="Jane Doe", execution_date=date(2023, 2, 10))
        data = assignor.to_dict()
        assert data["assignorName"] == "Jane Doe"
        assert data["executionDate"] == "2023-02-10"


class TestAssignee:
    """Tests for the Assignee class."""

    def test_assignee_from_dict(self, sample_address_data: Dict[str, Any]) -> None:
        data = {
            "assigneeNameText": "Test Company Inc.",
            "assigneeAddress": sample_address_data,
        }
        assignee = Assignee.from_dict(data)
        assert assignee.assignee_name_text == "Test Company Inc."
        assert assignee.assignee_address is not None
        assert assignee.assignee_address.city_name == sample_address_data["cityName"]

    def test_assignee_to_dict(self, sample_address_data: Dict[str, Any]) -> None:
        address_obj = Address.from_dict(sample_address_data)
        assignee = Assignee(
            assignee_name_text="Another Co.", assignee_address=address_obj
        )
        data = assignee.to_dict()
        assert data["assigneeNameText"] == "Another Co."
        assert data["assigneeAddress"]["cityName"] == sample_address_data["cityName"]

    def test_assignee_to_dict_no_address(self) -> None:
        assignee = Assignee(assignee_name_text="No Address Co.")
        data = assignee.to_dict()
        assert data == {"assigneeNameText": "No Address Co."}


class TestAssignment:
    """Tests for the Assignment class."""

    def test_assignment_from_dict(self, sample_address_data: Dict[str, Any]) -> None:
        data = {
            "reelNumber": "12345",
            "frameNumber": "67890",
            "reelAndFrameNumber": "12345/67890",
            "assignmentDocumentLocationURI": "https://example.com/assignment.pdf",
            "assignmentReceivedDate": "2023-01-01",
            "assignmentRecordedDate": "2023-01-15",
            "assignmentMailedDate": "2023-01-20",
            "conveyanceText": "ASSIGNMENT OF ASSIGNORS INTEREST",
            "assignorBag": [
                {"assignorName": "John Smith", "executionDate": "2022-12-15"}
            ],
            "assigneeBag": [
                {
                    "assigneeNameText": "Test Company Inc.",
                    "assigneeAddress": sample_address_data,
                }
            ],
            "correspondenceAddressBag": [sample_address_data],
        }
        assignment = Assignment.from_dict(data)
        assert assignment.reel_number == "12345"
        assert assignment.assignment_received_date == date(2023, 1, 1)
        assert len(assignment.assignor_bag) == 1
        assert assignment.assignor_bag[0].assignor_name == "John Smith"
        assert len(assignment.assignee_bag) == 1
        assert assignment.assignee_bag[0].assignee_name_text == "Test Company Inc."
        assert len(assignment.correspondence_address_bag) == 1
        assert (
            assignment.correspondence_address_bag[0].city_name
            == sample_address_data["cityName"]
        )

    def test_assignment_to_dict(self, sample_address_data: Dict[str, Any]) -> None:
        address_obj = Address.from_dict(sample_address_data)
        assignor_obj = Assignor(assignor_name="Signer", execution_date=date(2023, 1, 1))
        assignee_obj = Assignee(
            assignee_name_text="Recipient", assignee_address=address_obj
        )

        assignment = Assignment(
            reel_number="R001",
            assignment_received_date=date(2023, 2, 1),
            assignor_bag=[assignor_obj],
            assignee_bag=[assignee_obj],
            correspondence_address_bag=[address_obj],
        )
        data = assignment.to_dict()
        assert data["reelNumber"] == "R001"
        assert data["assignmentReceivedDate"] == "2023-02-01"
        assert len(data["assignorBag"]) == 1
        assert len(data["assigneeBag"]) == 1
        assert len(data["correspondenceAddressBag"]) == 1

    def test_assignment_to_dict_empty_bags(self) -> None:
        assignment = Assignment(
            reel_number="R002",
            assignor_bag=[],
            assignee_bag=[],
            correspondence_address_bag=[],
        )
        data = assignment.to_dict()
        assert data["reelNumber"] == "R002"
        assert data["assignorBag"] == []
        assert data["assigneeBag"] == []
        assert data["correspondenceAddressBag"] == []

    def test_assignment_roundtrip(
        self,
        sample_assignment_data: Dict[str, Any],
    ) -> None:
        """
        Tests the round-trip serialization for the Assignment class.
        """
        original_assignment = Assignment.from_dict(data=sample_assignment_data)
        intermediate_dict = original_assignment.to_dict()
        reconstructed_assignment = Assignment.from_dict(data=intermediate_dict)
        assert original_assignment == reconstructed_assignment


class TestForeignPriority:
    """Tests for the ForeignPriority class."""

    def test_foreign_priority_from_dict(self) -> None:
        data = {
            "ipOfficeName": "European Patent Office",
            "filingDate": "2022-01-01",
            "applicationNumberText": "EP12345678",
        }
        fp = ForeignPriority.from_dict(data)
        assert fp.ip_office_name == "European Patent Office"
        assert fp.filing_date == date(2022, 1, 1)
        assert fp.application_number_text == "EP12345678"

    def test_foreign_priority_to_dict(self) -> None:
        fp = ForeignPriority(
            ip_office_name="JPO",
            filing_date=date(2022, 3, 3),
            application_number_text="JP2022-001",
        )
        data = fp.to_dict()
        assert data["ipOfficeName"] == "JPO"
        assert data["filingDate"] == "2022-03-03"
        assert data["applicationNumberText"] == "JP2022-001"


class TestContinuity:
    """Tests for the Continuity base class."""

    def test_continuity_properties(self) -> None:
        cont_true = Continuity(first_inventor_to_file_indicator=True)
        assert cont_true.is_aia is True
        assert cont_true.is_pre_aia is False

        cont_false = Continuity(first_inventor_to_file_indicator=False)
        assert cont_false.is_aia is False
        assert cont_false.is_pre_aia is True

        cont_none = Continuity(first_inventor_to_file_indicator=None)
        assert cont_none.is_aia is None
        assert cont_none.is_pre_aia is None

    def test_continuity_to_dict(self) -> None:
        cont = Continuity(
            first_inventor_to_file_indicator=True,
            application_number_text="123",
            filing_date=date(2023, 1, 1),
        )
        expected_data = {
            "firstInventorToFileIndicator": True,
            "applicationNumberText": "123",
            "filingDate": date(2023, 1, 1),  # Note: asdict returns date obj, not str
        }
        # to_dict in Continuity does not serialize date objects, it returns them as is.
        # This is different from other to_dict methods that use serialize_date.
        # For this test, we compare against the raw asdict output after filtering.
        expected_camel_asdict = cont.to_dict()
        assert cont.to_dict() == expected_camel_asdict


class TestParentContinuity:
    """Tests for the ParentContinuity class."""

    def test_parent_continuity_from_dict(
        self, sample_parent_continuity_data: Dict[str, Any]
    ) -> None:
        pc = ParentContinuity.from_dict(sample_parent_continuity_data)
        assert pc.first_inventor_to_file_indicator is True
        assert pc.parent_application_status_code == 150
        assert pc.parent_patent_number == "10000000"
        assert pc.parent_application_filing_date == date(2020, 1, 1)
        assert pc.filing_date == date(2020, 1, 1)
        assert pc.application_number_text == "12345678"

    def test_parent_continuity_to_dict(
        self, sample_parent_continuity_data: Dict[str, Any]
    ) -> None:
        pc_instance = ParentContinuity.from_dict(sample_parent_continuity_data)
        data = pc_instance.to_dict()
        expected_data = sample_parent_continuity_data.copy()
        # Ensure dates are serialized for comparison if the fixture has strings
        expected_data["parentApplicationFilingDate"] = serialize_date(
            parse_to_date(expected_data["parentApplicationFilingDate"])
        )
        assert data == expected_data


class TestChildContinuity:
    """Tests for the ChildContinuity class."""

    def test_child_continuity_from_dict(
        self, sample_child_continuity_data: Dict[str, Any]
    ) -> None:
        cc = ChildContinuity.from_dict(sample_child_continuity_data)
        assert cc.first_inventor_to_file_indicator is True
        assert cc.child_application_status_code == 30
        assert cc.parent_application_number_text == "12345678"
        assert cc.child_application_filing_date == date(2022, 1, 1)
        assert cc.filing_date == date(2022, 1, 1)
        assert cc.application_number_text == "87654321"

    def test_child_continuity_to_dict(
        self, sample_child_continuity_data: Dict[str, Any]
    ) -> None:
        cc_instance = ChildContinuity.from_dict(sample_child_continuity_data)
        data = cc_instance.to_dict()
        expected_data = sample_child_continuity_data.copy()
        expected_data["childApplicationFilingDate"] = serialize_date(
            parse_to_date(expected_data["childApplicationFilingDate"])
        )
        assert data == expected_data


class TestPatentTermAdjustmentHistoryData:
    """Tests for the PatentTermAdjustmentHistoryData class."""

    def test_pta_history_from_dict(self) -> None:
        data = {
            "eventDate": "2022-01-01",
            "applicantDayDelayQuantity": 10.0,
            "eventDescriptionText": "Response to Office Action",
            "eventSequenceNumber": 1.0,
            "ipOfficeDayDelayQuantity": 5.0,
            "originatingEventSequenceNumber": 0.0,
            "ptaPTECode": "A",
        }
        pta_hist = PatentTermAdjustmentHistoryData.from_dict(data)
        assert pta_hist.event_date == date(2022, 1, 1)
        assert pta_hist.applicant_day_delay_quantity == 10.0
        assert pta_hist.event_description_text == "Response to Office Action"

    def test_pta_history_to_dict(self) -> None:
        pta_hist = PatentTermAdjustmentHistoryData(
            event_date=date(2022, 1, 1),
            applicant_day_delay_quantity=10.0,
            event_description_text="Response to Office Action",
            event_sequence_number=1.0,
            ip_office_day_delay_quantity=5.0,
            originating_event_sequence_number=0.0,
            pta_pte_code="A",
        )
        data = pta_hist.to_dict()
        assert data["eventDate"] == "2022-01-01"
        assert data["applicantDayDelayQuantity"] == 10.0
        assert data["eventDescriptionText"] == "Response to Office Action"


class TestPatentTermAdjustmentData:
    """Tests for the PatentTermAdjustmentData class."""

    def test_pta_data_from_dict(self) -> None:
        data = {
            "aDelayQuantity": 100.0,
            "adjustmentTotalQuantity": 150.0,
            "filingDate": "2020-01-01",
            "grantDate": "2023-01-01",
            "patentTermAdjustmentHistoryDataBag": [{"eventDate": "2022-01-01"}],
        }
        pta_data = PatentTermAdjustmentData.from_dict(data)
        assert pta_data.a_delay_quantity == 100.0
        assert pta_data.filing_date == date(2020, 1, 1)
        assert len(pta_data.patent_term_adjustment_history_data_bag) == 1
        assert pta_data.patent_term_adjustment_history_data_bag[0].event_date == date(
            2022, 1, 1
        )

    def test_pta_data_to_dict(self) -> None:
        history_item = PatentTermAdjustmentHistoryData(event_date=date(2022, 1, 1))
        pta_data = PatentTermAdjustmentData(
            a_delay_quantity=100.0,
            filing_date=date(2020, 1, 1),
            patent_term_adjustment_history_data_bag=[history_item],
        )
        data = pta_data.to_dict()
        assert data["aDelayQuantity"] == 100.0
        assert data["filingDate"] == "2020-01-01"
        assert len(data["patentTermAdjustmentHistoryDataBag"]) == 1
        assert (
            data["patentTermAdjustmentHistoryDataBag"][0]["eventDate"] == "2022-01-01"
        )

    def test_pta_data_to_dict_empty_history_bag(self) -> None:
        pta_data = PatentTermAdjustmentData(
            a_delay_quantity=50.0,
            patent_term_adjustment_history_data_bag=[],
        )
        data = pta_data.to_dict()
        assert data["aDelayQuantity"] == 50.0
        assert "patentTermAdjustmentHistoryDataBag" not in data

    def test_patent_term_adjustment_data_roundtrip(
        self, sample_patent_term_adjustment_data: Dict[str, Any]
    ) -> None:
        """
        Tests the round-trip serialization for the PatentTermAdjustmentData class.
        """
        original_pta_data = PatentTermAdjustmentData.from_dict(
            data=sample_patent_term_adjustment_data
        )
        intermediate_dict = original_pta_data.to_dict()
        reconstructed_pta_data = PatentTermAdjustmentData.from_dict(
            data=intermediate_dict
        )
        assert original_pta_data == reconstructed_pta_data


class TestEventData:
    """Tests for the EventData class."""

    def test_event_data_from_dict(self) -> None:
        data = {
            "eventCode": "COMP",
            "eventDescriptionText": "Ready",
            "eventDate": "2022-01-01",
        }
        event = EventData.from_dict(data)
        assert event.event_code == "COMP"
        assert event.event_description_text == "Ready"
        assert event.event_date == date(2022, 1, 1)

    def test_event_data_to_dict(self) -> None:
        event = EventData(
            event_code="MAIL",
            event_description_text="Mailed",
            event_date=date(2022, 2, 2),
        )
        data = event.to_dict()
        assert data["eventCode"] == "MAIL"
        assert data["eventDescriptionText"] == "Mailed"
        assert data["eventDate"] == "2022-02-02"


class TestDocumentMetaData:
    """Tests for the DocumentMetaData class."""

    def test_document_meta_data_from_dict(
        self, sample_document_meta_data_data: Dict[str, Any]
    ) -> None:
        doc_meta = PrintedMetaData.from_dict(sample_document_meta_data_data)
        assert doc_meta.zip_file_name == sample_document_meta_data_data["zipFileName"]
        assert doc_meta.file_create_date_time == datetime(
            2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc
        )

    def test_document_meta_data_to_dict(
        self, sample_document_meta_data_data: Dict[str, Any]
    ) -> None:
        doc_meta = PrintedMetaData(
            zip_file_name=sample_document_meta_data_data["zipFileName"],
            product_identifier=sample_document_meta_data_data["productIdentifier"],
            file_location_uri=sample_document_meta_data_data["fileLocationURI"],
            file_create_date_time=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            xml_file_name=sample_document_meta_data_data["xmlFileName"],
        )
        data = doc_meta.to_dict()
        assert data["zipFileName"] == sample_document_meta_data_data["zipFileName"]
        assert data["fileCreateDateTime"] == "2023-01-01T12:00:00Z"

    def test_document_meta_data_with_null_input(self) -> None:
        doc_meta = PrintedMetaData.from_dict({})
        assert doc_meta.zip_file_name is None
        assert doc_meta.file_create_date_time is None

        doc_meta_none = PrintedMetaData.from_dict({"zipFileName": None})
        assert doc_meta_none.zip_file_name is None


class TestApplicationMetaData:
    """Tests for the ApplicationMetaData class."""

    def test_application_meta_data_from_dict(self) -> None:
        data = {
            "nationalStageIndicator": True,
            "entityStatusData": {
                "smallEntityStatusIndicator": True,
                "businessEntityStatusCategory": "SMALL",
            },
            "publicationDateBag": [
                "2022-01-01",
                "invalid-date",
                None,
            ],
            "firstInventorToFileIndicator": "Y",
            "filingDate": "2020-01-01",
            "inventionTitle": "Test Invention",
            "class": "123",
            "applicantBag": [{"applicantNameText": "Test Co."}],
            "inventorBag": [{"inventorNameText": "J. Doe"}],
            "publicationSequenceNumberBag": ["1", None, "2"],
            "publicationCategoryBag": ["A1", None, "B2"],
            "cpcClassificationBag": ["A01B1/00", None],
        }
        app_meta = ApplicationMetaData.from_dict(data)
        assert app_meta.national_stage_indicator is True
        assert app_meta.entity_status_data is not None
        assert app_meta.entity_status_data.small_entity_status_indicator is True
        assert len(app_meta.publication_date_bag) == 1
        assert app_meta.publication_date_bag[0] == date(2022, 1, 1)
        assert app_meta.first_inventor_to_file_indicator is True
        assert app_meta.is_aia is True
        assert app_meta.filing_date == date(2020, 1, 1)
        assert app_meta.invention_title == "Test Invention"
        assert app_meta.class_field == "123"
        assert len(app_meta.applicant_bag) == 1
        assert len(app_meta.inventor_bag) == 1
        assert app_meta.publication_sequence_number_bag == [
            "1",
            None,
            "2",
        ]
        assert app_meta.publication_category_bag == ["A1", None, "B2"]
        assert app_meta.cpc_classification_bag == ["A01B1/00", None]

    def test_application_meta_data_to_dict(self) -> None:
        app_meta_all_none = ApplicationMetaData()
        data_all_none = app_meta_all_none.to_dict()
        assert data_all_none == {}

        app_meta_with_class = ApplicationMetaData(class_field="XYZ")
        data_with_class = app_meta_with_class.to_dict()
        assert data_with_class == {"class": "XYZ"}

        app_meta_with_class_none = ApplicationMetaData(class_field=None)
        data_with_class_none = app_meta_with_class_none.to_dict()
        assert "class" not in data_with_class_none

        app_meta_empty_cpc = ApplicationMetaData(
            invention_title="Test", cpc_classification_bag=[]
        )
        data_empty_cpc = app_meta_empty_cpc.to_dict()
        assert data_empty_cpc == {"inventionTitle": "Test"}

        app_meta_fitf = ApplicationMetaData(first_inventor_to_file_indicator=True)
        data_fitf = app_meta_fitf.to_dict()
        assert "firstInventorToFileIndicator" in data_fitf
        assert data_fitf["firstInventorToFileIndicator"] == "Y"

        sample_status = {
            "smallEntityStatusIndicator": True,
            "businessEntityStatusCategory": "TestCategory",
        }
        app_meta_status = ApplicationMetaData(
            entity_status_data=EntityStatus.from_dict(sample_status)
        )
        result_status = app_meta_status.to_dict()
        assert result_status["entityStatusData"] == {
            "smallEntityStatusIndicator": True,
            "businessEntityStatusCategory": "TestCategory",
        }

        app_meta_aia = ApplicationMetaData(first_inventor_to_file_indicator=True)
        data_aia = app_meta_aia.to_dict()

    def test_application_meta_data_roundtrip_object_comparison(
        self,
        sample_application_meta_data: Dict[str, Any],
    ) -> None:
        original_app_meta = ApplicationMetaData.from_dict(
            data=sample_application_meta_data
        )
        intermediate_dict = original_app_meta.to_dict()
        reconstructed_app_meta = ApplicationMetaData.from_dict(data=intermediate_dict)
        assert original_app_meta == reconstructed_app_meta

    def test_aia_properties(self) -> None:
        amd_true = ApplicationMetaData(first_inventor_to_file_indicator=True)
        assert amd_true.is_aia is True
        assert amd_true.is_pre_aia is False

        amd_false = ApplicationMetaData(first_inventor_to_file_indicator=False)
        assert amd_false.is_aia is False
        assert amd_false.is_pre_aia is True

        amd_none = ApplicationMetaData(first_inventor_to_file_indicator=None)
        assert amd_none.is_aia is None
        assert amd_none.is_pre_aia is None


class TestPatentFileWrapper:
    """Tests for the PatentFileWrapper class."""

    def test_patent_file_wrapper_from_dict(
        self, sample_document_meta_data_data: Dict[str, Any]
    ) -> None:
        data = {
            "applicationNumberText": "12345678",
            "applicationMetaData": {
                "inventionTitle": "Test Invention",
                "filingDate": "2020-01-01",
            },
            "pgpubDocumentMetaData": sample_document_meta_data_data,
            "lastIngestionDateTime": "2023-01-01T10:00:00Z",
        }
        wrapper = PatentFileWrapper.from_dict(data)
        assert wrapper.application_number_text == "12345678"
        assert wrapper.application_meta_data is not None
        assert wrapper.application_meta_data.invention_title == "Test Invention"
        assert wrapper.pgpub_document_meta_data is not None
        assert (
            wrapper.pgpub_document_meta_data.zip_file_name
            == sample_document_meta_data_data["zipFileName"]
        )
        assert wrapper.last_ingestion_date_time == datetime(
            2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc
        )

    def test_patent_file_wrapper_to_dict(
        self, sample_document_meta_data_data: Dict[str, Any]
    ) -> None:
        app_meta_obj = ApplicationMetaData(invention_title="Title")
        pgpub_obj = PrintedMetaData.from_dict(sample_document_meta_data_data)

        wrapper = PatentFileWrapper(
            application_number_text="98765",
            application_meta_data=app_meta_obj,
            pgpub_document_meta_data=pgpub_obj,
            last_ingestion_date_time=datetime(
                2023, 2, 2, 11, 0, 0, tzinfo=timezone.utc
            ),
        )
        data = wrapper.to_dict()
        assert data["applicationNumberText"] == "98765"
        assert data["applicationMetaData"]["inventionTitle"] == "Title"
        assert (
            data["pgpubDocumentMetaData"]["zipFileName"]
            == sample_document_meta_data_data["zipFileName"]
        )
        assert data["lastIngestionDateTime"] == "2023-02-02T11:00:00Z"

    def test_patent_file_wrapper_with_grant_document_meta_data(
        self, sample_document_meta_data_data: Dict[str, Any]
    ) -> None:
        data = {
            "applicationNumberText": "12345678",
            "grantDocumentMetaData": sample_document_meta_data_data,
        }
        wrapper = PatentFileWrapper.from_dict(data)
        assert wrapper.grant_document_meta_data is not None
        assert (
            wrapper.grant_document_meta_data.zip_file_name
            == sample_document_meta_data_data["zipFileName"]
        )

    def test_empty_patent_file_wrapper_from_dict(self) -> None:
        wrapper = PatentFileWrapper.from_dict({})
        assert wrapper.application_number_text is None
        assert wrapper.application_meta_data is None
        assert wrapper.correspondence_address_bag == []
        assert wrapper.last_ingestion_date_time is None

    def test_empty_patent_file_wrapper_to_dict(self) -> None:
        wrapper = PatentFileWrapper()
        assert wrapper.to_dict() == {}

    def test_patent_file_wrapper_roundtrip(
        self,
        patent_data_sample: Dict[str, Any],
    ) -> None:
        """
        Tests the round-trip serialization (from_dict -> to_dict -> from_dict)
        for the PatentFileWrapper class.
        It uses the first wrapper from the patent_data_sample fixture.
        """
        assert "patentFileWrapperDataBag" in patent_data_sample
        assert len(patent_data_sample["patentFileWrapperDataBag"]) > 0

        wrapper_dict_from_fixture = patent_data_sample["patentFileWrapperDataBag"][0]
        original_wrapper = PatentFileWrapper.from_dict(data=wrapper_dict_from_fixture)
        intermediate_dict = original_wrapper.to_dict()
        reconstructed_wrapper = PatentFileWrapper.from_dict(data=intermediate_dict)
        assert original_wrapper == reconstructed_wrapper

        if len(patent_data_sample["patentFileWrapperDataBag"]) > 1:
            wrapper_dict_2_from_fixture = patent_data_sample[
                "patentFileWrapperDataBag"
            ][1]
            original_wrapper_2 = PatentFileWrapper.from_dict(
                data=wrapper_dict_2_from_fixture
            )
            intermediate_dict_2 = original_wrapper_2.to_dict()
            reconstructed_wrapper_2 = PatentFileWrapper.from_dict(
                data=intermediate_dict_2
            )
            assert original_wrapper_2 == reconstructed_wrapper_2


class TestPatentDataResponse:
    """Tests for the PatentDataResponse class."""

    def test_patent_data_response_to_dict(self) -> None:
        wrapper1 = PatentFileWrapper(application_number_text="12345678")
        wrapper2 = PatentFileWrapper(application_number_text="87654321")
        response = PatentDataResponse(
            count=2, patent_file_wrapper_data_bag=[wrapper1, wrapper2]
        )
        result = response.to_dict()
        assert result["count"] == 2
        assert len(result["patentFileWrapperDataBag"]) == 2
        assert (
            result["patentFileWrapperDataBag"][0]["applicationNumberText"] == "12345678"
        )
        assert (
            result["patentFileWrapperDataBag"][1]["applicationNumberText"] == "87654321"
        )

    def test_patent_data_response_to_dict_with_sample(
        self, patent_data_sample: Dict[str, Any]
    ) -> None:
        response = PatentDataResponse.from_dict(patent_data_sample)
        result = response.to_dict()
        assert isinstance(result, dict)
        assert result["count"] == response.count
        assert "patentFileWrapperDataBag" in result
        assert len(result["patentFileWrapperDataBag"]) == len(
            response.patent_file_wrapper_data_bag
        )
        if response.count > 0:
            assert (
                result["patentFileWrapperDataBag"][0]["applicationNumberText"]
                == response.patent_file_wrapper_data_bag[0].application_number_text
            )

    def test_empty_patent_data_response_from_dict(self) -> None:
        response = PatentDataResponse.from_dict({})
        assert response.count == 0
        assert response.patent_file_wrapper_data_bag == []

    def test_empty_patent_data_response_to_dict(self) -> None:
        response = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
        result = response.to_dict()
        assert result["count"] == 0
        assert result["patentFileWrapperDataBag"] == []

    def test_patent_data_response_to_csv(
        self, patent_data_sample: Dict[str, Any]
    ) -> None:
        """Tests the to_csv method of PatentDataResponse."""
        response = PatentDataResponse.from_dict(patent_data_sample)
        csv_string = response.to_csv()

        assert isinstance(csv_string, str)

        # Use csv reader to parse the string and check headers and rows
        reader = csv.reader(io.StringIO(csv_string))
        header_row = next(reader)
        expected_headers = [
            "inventionTitle",
            "applicationNumberText",
            "filingDate",
            "applicationTypeLabelName",
            "publicationCategoryBag",
            "applicationStatusDescriptionText",
            "applicationStatusDate",
            "firstInventorName",
        ]
        assert header_row == expected_headers

        data_rows = list(reader)
        assert len(data_rows) == response.count  # Should match the number of wrappers

        # Check data for the first row (corresponds to patent_file_wrapper_1 in the fixture)
        if response.count > 0:
            first_wrapper_data = patent_data_sample["patentFileWrapperDataBag"][0]
            first_meta_data = first_wrapper_data["applicationMetaData"]

            expected_first_row = [
                first_meta_data["inventionTitle"],
                first_wrapper_data["applicationNumberText"],
                first_meta_data["filingDate"],  # Already a string in fixture
                first_meta_data["applicationTypeLabelName"],
                "|".join(first_meta_data["publicationCategoryBag"]),
                first_meta_data["applicationStatusDescriptionText"],
                first_meta_data["applicationStatusDate"],  # Already a string
                first_meta_data["firstInventorName"],
            ]
            assert data_rows[0] == expected_first_row

            if response.count > 1:
                second_wrapper_data = patent_data_sample["patentFileWrapperDataBag"][1]
                second_meta_data = second_wrapper_data["applicationMetaData"]
                expected_second_row = [
                    second_meta_data["inventionTitle"],
                    second_wrapper_data["applicationNumberText"],
                    second_meta_data["filingDate"],
                    second_meta_data["applicationTypeLabelName"],
                    "|".join(second_meta_data["publicationCategoryBag"]),
                    second_meta_data["applicationStatusDescriptionText"],
                    second_meta_data["applicationStatusDate"],
                    second_meta_data["firstInventorName"],
                ]
                assert data_rows[1] == expected_second_row

    def test_patent_data_response_to_csv_empty(self) -> None:
        """Tests to_csv with an empty PatentDataResponse."""
        response = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
        csv_string = response.to_csv()
        reader = csv.reader(io.StringIO(csv_string))
        header_row = next(reader)
        expected_headers = [
            "inventionTitle",
            "applicationNumberText",
            "filingDate",
            "applicationTypeLabelName",
            "publicationCategoryBag",
            "applicationStatusDescriptionText",
            "applicationStatusDate",
            "firstInventorName",
        ]
        assert header_row == expected_headers
        with pytest.raises(StopIteration):  # No data rows
            next(reader)

    def test_patent_data_response_to_csv_missing_metadata(self) -> None:
        """Tests to_csv when a PatentFileWrapper is missing application_meta_data."""
        wrapper_no_meta = PatentFileWrapper(application_number_text="123")
        response = PatentDataResponse(
            count=1, patent_file_wrapper_data_bag=[wrapper_no_meta]
        )
        csv_string = response.to_csv()
        reader = csv.reader(io.StringIO(csv_string))
        header_row = next(reader)  # Skip header
        with pytest.raises(StopIteration):  # Should skip the row with missing meta
            next(reader)

        # Test with one valid and one invalid
        meta = ApplicationMetaData(invention_title="Test Title")
        wrapper_with_meta = PatentFileWrapper(
            application_number_text="456", application_meta_data=meta
        )
        response_mixed = PatentDataResponse(
            count=2, patent_file_wrapper_data_bag=[wrapper_no_meta, wrapper_with_meta]
        )
        csv_string_mixed = response_mixed.to_csv()
        reader_mixed = csv.reader(io.StringIO(csv_string_mixed))
        next(reader_mixed)  # Skip header
        data_rows_mixed = list(reader_mixed)
        assert len(data_rows_mixed) == 1  # Only the valid one should be present
        assert data_rows_mixed[0][0] == "Test Title"
        assert data_rows_mixed[0][1] == "456"


class TestStatusCode:
    """Tests for the StatusCode class."""

    def test_status_code_from_dict(self) -> None:
        data = {
            "applicationStatusCode": 101,
            "applicationStatusDescriptionText": "Status Description",
        }
        sc = StatusCode.from_dict(data)
        assert sc.code == 101
        assert sc.description == "Status Description"

        data_alt = {"code": 102, "description": "Alt Desc"}
        sc_alt = StatusCode.from_dict(data_alt)
        assert sc_alt.code == 102
        assert sc_alt.description == "Alt Desc"

    def test_status_code_to_dict(self) -> None:
        sc = StatusCode(code=101, description="Status Description")
        data = sc.to_dict()
        assert data == {
            "applicationStatusCode": 101,
            "applicationStatusDescriptionText": "Status Description",
        }


class TestStatusCodeCollection:
    """Tests for the StatusCodeCollection class."""

    def test_status_code_collection_iterable_len_getitem(self) -> None:
        sc1 = StatusCode(code=1)
        sc2 = StatusCode(code=2)
        collection = StatusCodeCollection([sc1, sc2])
        assert len(collection) == 2
        assert collection[0] is sc1
        assert collection[1] is sc2

        codes_from_iter = [c for c in collection]
        assert codes_from_iter == [sc1, sc2]

    def test_status_code_collection_to_dict(self) -> None:
        code1 = StatusCode(code=101, description="Status 1")
        code2 = StatusCode(code=102, description="Status 2")
        collection = StatusCodeCollection([code1, code2])
        data = collection.to_dict()
        assert data == [
            {
                "applicationStatusCode": 101,
                "applicationStatusDescriptionText": "Status 1",
            },
            {
                "applicationStatusCode": 102,
                "applicationStatusDescriptionText": "Status 2",
            },
        ]
        str_collection = str(collection)
        assert str_collection == "StatusCodeCollection with 2 status codes."

    def test_status_code_collection_find_by_code(self) -> None:
        code1 = StatusCode(code=101, description="Status 1")
        code2 = StatusCode(code=102, description="Status 2")
        collection = StatusCodeCollection([code1, code2])
        assert collection.find_by_code(101) is code1
        assert collection.find_by_code(103) is None

    def test_status_code_collection_search_by_description(self) -> None:
        code1 = StatusCode(code=101, description="Status One")
        code2 = StatusCode(code=102, description="Another Status")
        code3 = StatusCode(code=103, description="Status Three")
        collection = StatusCodeCollection([code1, code2, code3])
        results = collection.search_by_description("status")
        assert len(results) == 3
        assert code1 in results._status_codes
        assert code2 in results._status_codes
        assert code3 in results._status_codes

        results_one = collection.search_by_description("One")
        assert len(results_one) == 1
        assert code1 in results_one._status_codes

    def test_status_code_collection_repr(self) -> None:
        """Test the __repr__ method of StatusCodeCollection."""
        sc1 = StatusCode(code=1, description="Desc1")
        sc2 = StatusCode(code=2, description="Desc2")
        sc3 = StatusCode(code=3, description="Desc3")
        sc4 = StatusCode(code=4, description="Desc4")

        collection_empty = StatusCodeCollection([])
        assert repr(collection_empty) == "StatusCodeCollection(empty)"

        collection_short = StatusCodeCollection([sc1, sc2])
        assert repr(collection_short) == "StatusCodeCollection(2 status codes: 1, 2)"

        collection_long = StatusCodeCollection([sc1, sc2, sc3, sc4])
        assert (
            repr(collection_long)
            == "StatusCodeCollection(4 status codes: 1, 2, 3, ...)"
        )


class TestStatusCodeSearchResponse:
    """Tests for the StatusCodeSearchResponse class."""

    def test_status_code_search_response_from_dict(self) -> None:
        data = {
            "count": 2,
            "statusCodeBag": [
                {
                    "applicationStatusCode": 101,
                    "applicationStatusDescriptionText": "Status 1",
                },
                {
                    "applicationStatusCode": 102,
                    "applicationStatusDescriptionText": "Status 2",
                },
            ],
            "requestIdentifier": "req123",
        }
        response = StatusCodeSearchResponse.from_dict(data)
        assert response.count == 2
        assert isinstance(response.status_code_bag, StatusCodeCollection)
        assert len(response.status_code_bag) == 2
        assert response.request_identifier == "req123"

    def test_status_code_search_response_to_dict(self) -> None:
        code1 = StatusCode(code=101, description="Status 1")
        code2 = StatusCode(code=102, description="Status 2")
        collection = StatusCodeCollection([code1, code2])
        response = StatusCodeSearchResponse(
            count=2, status_code_bag=collection, request_identifier="req123"
        )
        data = response.to_dict()
        assert data == {
            "count": 2,
            "statusCodeBag": [
                {
                    "applicationStatusCode": 101,
                    "applicationStatusDescriptionText": "Status 1",
                },
                {
                    "applicationStatusCode": 102,
                    "applicationStatusDescriptionText": "Status 2",
                },
            ],
            "requestIdentifier": "req123",
        }


class TestApplicationContinuityData:
    """Tests for the ApplicationContinuityData helper class."""

    def test_from_wrapper_with_data(
        self,
        sample_parent_continuity_data: Dict[str, Any],
        sample_child_continuity_data: Dict[str, Any],
    ) -> None:
        parent_cont = ParentContinuity.from_dict(sample_parent_continuity_data)
        child_cont = ChildContinuity.from_dict(sample_child_continuity_data)
        wrapper = PatentFileWrapper(
            parent_continuity_bag=[parent_cont],
            child_continuity_bag=[child_cont],
        )
        continuity_data = ApplicationContinuityData.from_wrapper(wrapper)
        assert len(continuity_data.parent_continuity_bag) == 1
        assert len(continuity_data.child_continuity_bag) == 1
        assert continuity_data.parent_continuity_bag[0] is parent_cont
        assert continuity_data.child_continuity_bag[0] is child_cont

    def test_from_wrapper_with_empty_data(self) -> None:
        wrapper = PatentFileWrapper(parent_continuity_bag=[], child_continuity_bag=[])
        continuity_data = ApplicationContinuityData.from_wrapper(wrapper)
        assert len(continuity_data.parent_continuity_bag) == 0
        assert len(continuity_data.child_continuity_bag) == 0

    def test_to_dict(
        self,
        sample_parent_continuity_data: Dict[str, Any],
        sample_child_continuity_data: Dict[str, Any],
    ) -> None:
        parent = ParentContinuity.from_dict(sample_parent_continuity_data)
        child = ChildContinuity.from_dict(sample_child_continuity_data)
        continuity_data = ApplicationContinuityData(
            parent_continuity_bag=[parent], child_continuity_bag=[child]
        )
        data_dict = continuity_data.to_dict()
        assert "parentContinuityBag" in data_dict
        assert "childContinuityBag" in data_dict
        assert len(data_dict["parentContinuityBag"]) == 1
        assert len(data_dict["childContinuityBag"]) == 1
        assert (
            data_dict["parentContinuityBag"][0]["parentApplicationNumberText"]
            == sample_parent_continuity_data["parentApplicationNumberText"]
        )
        assert (
            data_dict["childContinuityBag"][0]["childApplicationNumberText"]
            == sample_child_continuity_data["childApplicationNumberText"]
        )


class TestAssociatedDocumentsData:
    """Tests for the AssociatedDocumentsData helper class."""

    def test_from_wrapper_with_data(
        self, sample_document_meta_data_data: Dict[str, Any]
    ) -> None:
        pgpub_meta_data = sample_document_meta_data_data.copy()
        pgpub_meta_data["productIdentifier"] = "PGPUB"
        grant_meta_data = sample_document_meta_data_data.copy()
        grant_meta_data["productIdentifier"] = "GRANT"

        pgpub_meta = PrintedMetaData.from_dict(pgpub_meta_data)
        grant_meta = PrintedMetaData.from_dict(grant_meta_data)

        wrapper = PatentFileWrapper(
            pgpub_document_meta_data=pgpub_meta, grant_document_meta_data=grant_meta
        )
        assoc_docs = PrintedPublication.from_wrapper(wrapper)
        assert assoc_docs.pgpub_document_meta_data is pgpub_meta
        assert assoc_docs.grant_document_meta_data is grant_meta

    def test_from_wrapper_with_partial_data(
        self, sample_document_meta_data_data: Dict[str, Any]
    ) -> None:
        pgpub_meta = PrintedMetaData.from_dict(sample_document_meta_data_data)
        wrapper = PatentFileWrapper(
            pgpub_document_meta_data=pgpub_meta, grant_document_meta_data=None
        )
        assoc_docs = PrintedPublication.from_wrapper(wrapper)
        assert assoc_docs.pgpub_document_meta_data is pgpub_meta
        assert assoc_docs.grant_document_meta_data is None

    def test_from_wrapper_with_no_data(self) -> None:
        wrapper = PatentFileWrapper(
            pgpub_document_meta_data=None, grant_document_meta_data=None
        )
        assoc_docs = PrintedPublication.from_wrapper(wrapper)
        assert assoc_docs.pgpub_document_meta_data is None
        assert assoc_docs.grant_document_meta_data is None

    def test_to_dict(self, sample_document_meta_data_data: Dict[str, Any]) -> None:
        pgpub_meta_dict = sample_document_meta_data_data.copy()
        pgpub_meta_dict["zipFileName"] = "pgpub.zip"
        grant_meta_dict = sample_document_meta_data_data.copy()
        grant_meta_dict["zipFileName"] = "grant.zip"

        pgpub_meta = PrintedMetaData.from_dict(pgpub_meta_dict)
        grant_meta = PrintedMetaData.from_dict(grant_meta_dict)

        assoc_docs = PrintedPublication(
            pgpub_document_meta_data=pgpub_meta, grant_document_meta_data=grant_meta
        )
        data_dict = assoc_docs.to_dict()
        assert "pgpubDocumentMetaData" in data_dict
        assert "grantDocumentMetaData" in data_dict
        assert data_dict["pgpubDocumentMetaData"]["zipFileName"] == "pgpub.zip"
        assert data_dict["grantDocumentMetaData"]["zipFileName"] == "grant.zip"

    def test_to_dict_with_partial_data(
        self, sample_document_meta_data_data: Dict[str, Any]
    ) -> None:
        pgpub_meta = PrintedMetaData.from_dict(sample_document_meta_data_data)
        assoc_docs = PrintedPublication(
            pgpub_document_meta_data=pgpub_meta, grant_document_meta_data=None
        )
        data_dict = assoc_docs.to_dict()
        assert "pgpubDocumentMetaData" in data_dict
        assert "grantDocumentMetaData" in data_dict
        assert (
            data_dict["pgpubDocumentMetaData"]["zipFileName"]
            == sample_document_meta_data_data["zipFileName"]
        )
        assert data_dict["grantDocumentMetaData"] is None


class TestUtilityFunctions:
    """Tests for utility functions in models.patent_data.py."""

    def test_parse_to_datetime_utc(self, capsys: pytest.CaptureFixture) -> None:
        """Test parse_to_datetime_utc utility function comprehensively."""
        dt_utc_z = parse_to_datetime_utc("2023-01-01T10:00:00Z")
        assert isinstance(dt_utc_z, datetime)
        assert dt_utc_z.replace(tzinfo=None) == datetime(2023, 1, 1, 10, 0, 0)
        assert dt_utc_z.tzinfo == timezone.utc

        dt_offset = parse_to_datetime_utc("2023-01-01T05:00:00-05:00")
        assert isinstance(dt_offset, datetime)
        assert dt_offset.replace(tzinfo=None) == datetime(2023, 1, 1, 10, 0, 0)
        assert dt_offset.tzinfo == timezone.utc

        dt_naive_str = "2023-01-01T10:00:00"
        dt_naive = parse_to_datetime_utc(dt_naive_str)
        assert isinstance(dt_naive, datetime)
        try:
            naive_datetime_instance = datetime(2023, 1, 1, 10, 0, 0)
            aware_datetime_instance = naive_datetime_instance.replace(
                tzinfo=ZoneInfo(ASSUMED_NAIVE_TIMEZONE_STR)
            )
            expected_naive_utc_hour = aware_datetime_instance.astimezone(
                timezone.utc
            ).hour
            assert dt_naive.hour == expected_naive_utc_hour
        except ZoneInfoNotFoundError:
            assert dt_naive.hour == 10
        assert dt_naive.tzinfo == timezone.utc

        dt_ms = parse_to_datetime_utc("2023-01-01T10:00:00.123Z")
        assert isinstance(dt_ms, datetime)
        assert dt_ms.replace(tzinfo=None) == datetime(2023, 1, 1, 10, 0, 0, 123000)
        assert dt_ms.tzinfo == timezone.utc

        dt_space = parse_to_datetime_utc("2023-01-01 10:00:00")
        assert isinstance(dt_space, datetime)
        try:
            naive_dt_for_space = datetime(2023, 1, 1, 10, 0, 0)
            aware_dt_for_space = naive_dt_for_space.replace(
                tzinfo=ZoneInfo(ASSUMED_NAIVE_TIMEZONE_STR)
            )
            expected_space_utc_hour = aware_dt_for_space.astimezone(timezone.utc).hour
            assert dt_space.hour == expected_space_utc_hour
        except ZoneInfoNotFoundError:
            assert dt_space.hour == 10
        assert dt_space.tzinfo == timezone.utc

        assert parse_to_datetime_utc("invalid-datetime") is None
        captured = capsys.readouterr()
        assert (
            "Warning: Could not parse datetime string 'invalid-datetime'"
            in captured.out
        )
        assert parse_to_datetime_utc(None) is None

    def test_serialize_date(self) -> None:
        """Test serialize_date utility function."""
        test_date = date(2023, 1, 1)
        assert serialize_date(test_date) == "2023-01-01"
        assert serialize_date(None) is None

    def test_serialize_datetime_as_iso(self) -> None:
        """Test serialize_datetime_as_iso utility function."""
        dt_utc = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        assert serialize_datetime_as_iso(dt_utc) == "2023-01-01T10:00:00Z"

        dt_naive = datetime(2023, 1, 1, 10, 0, 0)
        assert serialize_datetime_as_iso(dt_naive) == "2023-01-01T10:00:00Z"

        minus_five = timezone(timedelta(hours=-5))
        dt_est = datetime(2023, 1, 1, 10, 0, 0, tzinfo=minus_five)
        assert serialize_datetime_as_iso(dt_est) == "2023-01-01T15:00:00Z"

        assert serialize_datetime_as_iso(None) is None

    def test_parse_to_datetime_utc_localization_failure_and_fallback(
        self, capsys: pytest.CaptureFixture
    ) -> None:
        """Triggers the except block by making astimezone() raise, and tests fallback path."""

        class FailingTZ(tzinfo):
            def utcoffset(self, dt: Optional[datetime]) -> None:
                raise Exception("boom")

            def dst(self, dt: Optional[datetime]) -> Optional[timedelta]:
                return None

            def tzname(self, dt: Optional[datetime]) -> Optional[str]:
                return None

        dt_str = "2023-01-01T10:00:00"

        with patch("pyUSPTO.models.patent_data.ASSUMED_NAIVE_TIMEZONE", FailingTZ()):
            result = parse_to_datetime_utc(datetime_str=dt_str)

        assert result is None

        captured = capsys.readouterr()
        assert "Warning: Error localizing naive datetime" in captured.out

    def test_parse_to_datetime_utc_fallback_to_utc_replace(
        self, capsys: pytest.CaptureFixture
    ) -> None:
        """Triggers fallback to dt_obj.replace(tzinfo=timezone.utc) without touching datetime.*"""

        class FailingButEqualToUTC(tzinfo):
            def utcoffset(self, dt: Optional[datetime]) -> None:
                raise Exception("boom")

            def dst(self, dt: Optional[datetime]) -> Optional[timedelta]:
                return None

            def tzname(self, dt: Optional[datetime]) -> Optional[str]:
                return None

            def __eq__(self, other: object) -> bool:
                return other is timezone.utc

        dt_str = "2023-01-01T10:00:00"

        with patch(
            "pyUSPTO.models.patent_data.ASSUMED_NAIVE_TIMEZONE", FailingButEqualToUTC()
        ):
            result = parse_to_datetime_utc(dt_str)

        assert isinstance(result, datetime)
        assert result.tzinfo == timezone.utc

        captured = capsys.readouterr()
        assert "Warning: Error localizing naive datetime" in captured.out

    def test_parse_yn_to_bool(self, capsys: pytest.CaptureFixture) -> None:
        """Test parse_yn_to_bool utility function."""
        assert parse_yn_to_bool("Y") is True
        assert parse_yn_to_bool("y") is True
        assert parse_yn_to_bool("N") is False
        assert parse_yn_to_bool("n") is False
        assert parse_yn_to_bool(None) is None
        assert parse_yn_to_bool("True") is None
        captured_true = capsys.readouterr()
        assert (
            "Warning: Unexpected value for Y/N boolean string: 'True'"
            in captured_true.out
        )

        assert parse_yn_to_bool("False") is None
        captured_false = capsys.readouterr()
        assert (
            "Warning: Unexpected value for Y/N boolean string: 'False'"
            in captured_false.out
        )

        assert parse_yn_to_bool("Other") is None
        captured_other = capsys.readouterr()
        assert (
            "Warning: Unexpected value for Y/N boolean string: 'Other'"
            in captured_other.out
        )

        assert parse_yn_to_bool("yes") is None
        assert parse_yn_to_bool("no") is None
        assert parse_yn_to_bool("") is None
        assert parse_yn_to_bool("X") is None

    def test_serialize_bool_to_yn(self) -> None:
        """Test serialize_bool_to_yn utility function."""
        assert serialize_bool_to_yn(True) == "Y"
        assert serialize_bool_to_yn(False) == "N"
        assert serialize_bool_to_yn(None) is None

    def test_timezone_setup_fallback(self) -> None:
        """Test fallback to UTC when timezone not found."""
        with patch(
            "zoneinfo.ZoneInfo", side_effect=ZoneInfoNotFoundError("Test error")
        ):
            import pyUSPTO.models.patent_data

            importlib.reload(pyUSPTO.models.patent_data)
            ASSUMED_NAIVE_TIMEZONE_STR_LOCAL = (
                "America/New_York2"  # Use a local var to avoid modifying global
            )
            try:
                assumed_naive_tz_local = ZoneInfo(ASSUMED_NAIVE_TIMEZONE_STR_LOCAL)
            except ZoneInfoNotFoundError:
                print(
                    f"Warning: Timezone '{ASSUMED_NAIVE_TIMEZONE_STR_LOCAL}' not found. Naive datetimes will be treated as UTC or may cause errors."
                )
                assumed_naive_tz_local = ZoneInfo("UTC")  # Fallback to UTC

            assert assumed_naive_tz_local == ZoneInfo("UTC")

        importlib.reload(module=pyUSPTO.models.patent_data)
