"""
models.patent_data - Data models for USPTO patent data API

This module provides data models for the USPTO Patent Data API.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PatentDataResponse:
    """Top-level response from the patent data API."""

    count: int
    patent_file_wrapper_data_bag: List["PatentFileWrapper"]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PatentDataResponse":
        """Create a PatentDataResponse object from a dictionary."""
        return cls(
            count=data.get("count", 0),
            patent_file_wrapper_data_bag=[
                PatentFileWrapper.from_dict(data=wrapper)
                for wrapper in data.get("patentFileWrapperDataBag", [])
            ],
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert the PatentDataResponse object to a dictionary."""
        return {
            "count": self.count,
            "patentFileWrapperDataBag": [
                # If PatentFileWrapper had a to_dict method, we would use it here
                # For now, we'll just return a basic representation
                {
                    "applicationNumberText": wrapper.application_number_text,
                    # Add other fields as needed
                }
                for wrapper in self.patent_file_wrapper_data_bag
            ],
            # Add other fields that might be in the API response but not in our model
            "documentBag": [],  # Empty placeholder for document bag
        }


@dataclass
class Address:
    """Represents an address in the patent data API."""

    name_line_one_text: Optional[str] = None
    name_line_two_text: Optional[str] = None
    address_line_one_text: Optional[str] = None
    address_line_two_text: Optional[str] = None
    address_line_three_text: Optional[str] = None
    address_line_four_text: Optional[str] = None
    geographic_region_name: Optional[str] = None
    geographic_region_code: Optional[str] = None
    postal_code: Optional[str] = None
    city_name: Optional[str] = None
    country_code: Optional[str] = None
    country_name: Optional[str] = None
    postal_address_category: Optional[str] = None
    correspondent_name_text: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Address":
        """Create an Address object from a dictionary."""
        return cls(
            name_line_one_text=data.get("nameLineOneText"),
            name_line_two_text=data.get("nameLineTwoText"),
            address_line_one_text=data.get("addressLineOneText"),
            address_line_two_text=data.get("addressLineTwoText"),
            address_line_three_text=data.get("addressLineThreeText"),
            address_line_four_text=data.get("addressLineFourText"),
            geographic_region_name=data.get("geographicRegionName"),
            geographic_region_code=data.get("geographicRegionCode"),
            postal_code=data.get("postalCode"),
            city_name=data.get("cityName"),
            country_code=data.get("countryCode"),
            country_name=data.get("countryName"),
            postal_address_category=data.get("postalAddressCategory"),
            correspondent_name_text=data.get("correspondentNameText"),
        )


@dataclass
class Telecommunication:
    """Represents telecommunication information."""

    telecommunication_number: Optional[str] = None
    extension_number: Optional[str] = None
    telecom_type_code: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Telecommunication":
        """Create a Telecommunication object from a dictionary."""
        return cls(
            telecommunication_number=data.get("telecommunicationNumber"),
            extension_number=data.get("extensionNumber"),
            telecom_type_code=data.get("telecomTypeCode"),
        )


@dataclass
class Person:
    """Base class for person-related data."""

    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    name_prefix: Optional[str] = None
    name_suffix: Optional[str] = None
    preferred_name: Optional[str] = None
    country_code: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Person":
        """Create a Person object from a dictionary."""
        return cls(
            first_name=data.get("firstName"),
            middle_name=data.get("middleName"),
            last_name=data.get("lastName"),
            name_prefix=data.get("namePrefix"),
            name_suffix=data.get("nameSuffix"),
            preferred_name=data.get("preferredName"),
            country_code=data.get("countryCode"),
        )


@dataclass
class Applicant(Person):
    """Represents an applicant in the patent data."""

    applicant_name_text: Optional[str] = None
    correspondence_address_bag: List[Address] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Applicant":
        """Create an Applicant object from a dictionary."""
        person = Person.from_dict(data=data)
        addresses = []
        if "correspondenceAddressBag" in data:
            addresses = [
                Address.from_dict(data=addr)
                for addr in data.get("correspondenceAddressBag", [])
            ]

        return cls(
            first_name=person.first_name,
            middle_name=person.middle_name,
            last_name=person.last_name,
            name_prefix=person.name_prefix,
            name_suffix=person.name_suffix,
            preferred_name=person.preferred_name,
            country_code=person.country_code,
            applicant_name_text=data.get("applicantNameText"),
            correspondence_address_bag=addresses,
        )


@dataclass
class Inventor(Person):
    """Represents an inventor in the patent data."""

    inventor_name_text: Optional[str] = None
    correspondence_address_bag: List[Address] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Inventor":
        """Create an Inventor object from a dictionary."""
        person = Person.from_dict(data=data)
        addresses = []
        if "correspondenceAddressBag" in data:
            addresses = [
                Address.from_dict(data=addr)
                for addr in data.get("correspondenceAddressBag", [])
            ]

        return cls(
            first_name=person.first_name,
            middle_name=person.middle_name,
            last_name=person.last_name,
            name_prefix=person.name_prefix,
            name_suffix=person.name_suffix,
            preferred_name=person.preferred_name,
            country_code=person.country_code,
            inventor_name_text=data.get("inventorNameText"),
            correspondence_address_bag=addresses,
        )


@dataclass
class Attorney(Person):
    """Represents an attorney in the patent data."""

    registration_number: Optional[str] = None
    active_indicator: Optional[str] = None
    registered_practitioner_category: Optional[str] = None
    attorney_address_bag: List[Address] = field(default_factory=list)
    telecommunication_address_bag: List[Telecommunication] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Attorney":
        """Create an Attorney object from a dictionary."""
        person = Person.from_dict(data=data)
        addresses = []
        if "attorneyAddressBag" in data:
            addresses = [
                Address.from_dict(data=addr)
                for addr in data.get("attorneyAddressBag", [])
            ]

        telecom_addresses = []
        if "telecommunicationAddressBag" in data:
            telecom_addresses = [
                Telecommunication.from_dict(data=telecom)
                for telecom in data.get("telecommunicationAddressBag", [])
            ]

        return cls(
            first_name=person.first_name,
            middle_name=person.middle_name,
            last_name=person.last_name,
            name_prefix=person.name_prefix,
            name_suffix=person.name_suffix,
            preferred_name=person.preferred_name,
            country_code=person.country_code,
            registration_number=data.get("registrationNumber"),
            active_indicator=data.get("activeIndicator"),
            registered_practitioner_category=data.get("registeredPractitionerCategory"),
            attorney_address_bag=addresses,
            telecommunication_address_bag=telecom_addresses,
        )


@dataclass
class EntityStatus:
    """Represents entity status data."""

    small_entity_status_indicator: Optional[bool] = None
    business_entity_status_category: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EntityStatus":
        """Create an EntityStatus object from a dictionary."""
        return cls(
            small_entity_status_indicator=data.get("smallEntityStatusIndicator"),
            business_entity_status_category=data.get("businessEntityStatusCategory"),
        )


@dataclass
class CustomerNumberCorrespondence:
    """Represents customer number correspondence data."""

    patron_identifier: Optional[int] = None
    organization_standard_name: Optional[str] = None
    power_of_attorney_address_bag: List[Address] = field(default_factory=list)
    telecommunication_address_bag: List[Telecommunication] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CustomerNumberCorrespondence":
        """Create a CustomerNumberCorrespondence object from a dictionary."""
        addresses = []
        if "powerOfAttorneyAddressBag" in data:
            power_of_attorney_bag = data.get("powerOfAttorneyAddressBag", [])
            # Ensure we only process dictionary objects
            addresses = [
                Address.from_dict(data=addr)
                for addr in power_of_attorney_bag
                if isinstance(addr, dict)
            ]

        telecom_addresses = []
        if "telecommunicationAddressBag" in data:
            telecom_bag = data.get("telecommunicationAddressBag", [])
            # Ensure we only process dictionary objects
            telecom_addresses = [
                Telecommunication.from_dict(data=telecom)
                for telecom in telecom_bag
                if isinstance(telecom, dict)
            ]

        return cls(
            patron_identifier=data.get("patronIdentifier"),
            organization_standard_name=data.get("organizationStandardName"),
            power_of_attorney_address_bag=addresses,
            telecommunication_address_bag=telecom_addresses,
        )


@dataclass
class RecordAttorney:
    """Represents record attorney data."""

    customer_number_correspondence_data: List[CustomerNumberCorrespondence] = field(
        default_factory=list
    )
    power_of_attorney_bag: List[Attorney] = field(default_factory=list)
    attorney_bag: List[Attorney] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RecordAttorney":
        """Create a RecordAttorney object from a dictionary."""
        customer_correspondence = []
        if "customerNumberCorrespondenceData" in data:
            correspondence_data = data.get("customerNumberCorrespondenceData", [])
            # Ensure we only process dictionary objects
            customer_correspondence = [
                CustomerNumberCorrespondence.from_dict(corr)
                for corr in correspondence_data
                if isinstance(corr, dict)
            ]

        power_attorneys = []
        if "powerOfAttorneyBag" in data:
            power_attorneys = [
                Attorney.from_dict(data=attorney)
                for attorney in data.get("powerOfAttorneyBag", [])
            ]

        attorneys = []
        if "attorneyBag" in data:
            attorneys = [
                Attorney.from_dict(data=attorney)
                for attorney in data.get("attorneyBag", [])
            ]

        return cls(
            customer_number_correspondence_data=customer_correspondence,
            power_of_attorney_bag=power_attorneys,
            attorney_bag=attorneys,
        )


@dataclass
class Assignor:
    """Represents an assignor in an assignment."""

    assignor_name: Optional[str] = None
    execution_date: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Assignor":
        """Create an Assignor object from a dictionary."""
        return cls(
            assignor_name=data.get("assignorName"),
            execution_date=data.get("executionDate"),
        )


@dataclass
class Assignee:
    """Represents an assignee in an assignment."""

    assignee_name_text: Optional[str] = None
    assignee_address: Optional[Address] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Assignee":
        """Create an Assignee object from a dictionary."""
        address = None
        if "assigneeAddress" in data and data.get("assigneeAddress") is not None:
            address = Address.from_dict(data=data.get("assigneeAddress", {}))

        return cls(
            assignee_name_text=data.get("assigneeNameText"), assignee_address=address
        )


@dataclass
class Assignment:
    """Represents an assignment in the patent data."""

    reel_number: Optional[int] = None
    frame_number: Optional[int] = None
    reel_and_frame_number: Optional[str] = None
    assignment_document_location_uri: Optional[str] = None
    assignment_received_date: Optional[str] = None
    assignment_recorded_date: Optional[str] = None
    assignment_mailed_date: Optional[str] = None
    conveyance_text: Optional[str] = None
    assignor_bag: List[Assignor] = field(default_factory=list)
    assignee_bag: List[Assignee] = field(default_factory=list)
    correspondence_address_bag: List[Address] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Assignment":
        """Create an Assignment object from a dictionary."""
        assignors = []
        if "assignorBag" in data:
            assignors = [
                Assignor.from_dict(data=assignor)
                for assignor in data.get("assignorBag", [])
            ]

        assignees = []
        if "assigneeBag" in data:
            assignees = [
                Assignee.from_dict(data=assignee)
                for assignee in data.get("assigneeBag", [])
            ]

        addresses = []
        if "correspondenceAddressBag" in data:
            addresses = [
                Address.from_dict(data=addr)
                for addr in data.get("correspondenceAddressBag", [])
            ]

        return cls(
            reel_number=data.get("reelNumber"),
            frame_number=data.get("frameNumber"),
            reel_and_frame_number=data.get("reelAndFrameNumber"),
            assignment_document_location_uri=data.get("assignmentDocumentLocationURI"),
            assignment_received_date=data.get("assignmentReceivedDate"),
            assignment_recorded_date=data.get("assignmentRecordedDate"),
            assignment_mailed_date=data.get("assignmentMailedDate"),
            conveyance_text=data.get("conveyanceText"),
            assignor_bag=assignors,
            assignee_bag=assignees,
            correspondence_address_bag=addresses,
        )


@dataclass
class ForeignPriority:
    """Represents foreign priority information."""

    ip_office_name: Optional[str] = None
    filing_date: Optional[str] = None
    application_number_text: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ForeignPriority":
        """Create a ForeignPriority object from a dictionary."""
        return cls(
            ip_office_name=data.get("ipOfficeName"),
            filing_date=data.get("filingDate"),
            application_number_text=data.get("applicationNumberText"),
        )


@dataclass
class Continuity:
    """Base class for continuity information."""

    first_inventor_to_file_indicator: Optional[bool] = None
    application_number_text: Optional[str] = None
    filing_date: Optional[str] = None
    status_code: Optional[int] = None
    status_description_text: Optional[str] = None
    patent_number: Optional[str] = None
    claim_parentage_type_code: Optional[str] = None
    claim_parentage_type_code_description_text: Optional[str] = None


@dataclass
class ParentContinuity(Continuity):
    """Represents parent continuity information."""

    parent_application_status_code: Optional[int] = None
    parent_patent_number: Optional[str] = None
    parent_application_status_description_text: Optional[str] = None
    parent_application_filing_date: Optional[str] = None
    parent_application_number_text: Optional[str] = None
    child_application_number_text: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ParentContinuity":
        """Create a ParentContinuity object from a dictionary."""
        return cls(
            first_inventor_to_file_indicator=data.get("firstInventorToFileIndicator"),
            parent_application_status_code=data.get("parentApplicationStatusCode"),
            parent_patent_number=data.get("parentPatentNumber"),
            parent_application_status_description_text=data.get(
                "parentApplicationStatusDescriptionText"
            ),
            parent_application_filing_date=data.get("parentApplicationFilingDate"),
            parent_application_number_text=data.get("parentApplicationNumberText"),
            child_application_number_text=data.get("childApplicationNumberText"),
            claim_parentage_type_code=data.get("claimParentageTypeCode"),
            claim_parentage_type_code_description_text=data.get(
                "claimParentageTypeCodeDescriptionText"
            ),
            # Map parent-specific fields to base class fields
            status_code=data.get("parentApplicationStatusCode"),
            status_description_text=data.get("parentApplicationStatusDescriptionText"),
            filing_date=data.get("parentApplicationFilingDate"),
            application_number_text=data.get("parentApplicationNumberText"),
            patent_number=data.get("parentPatentNumber"),
        )


@dataclass
class ChildContinuity(Continuity):
    """Represents child continuity information."""

    child_application_status_code: Optional[int] = None
    parent_application_number_text: Optional[str] = None
    child_application_number_text: Optional[str] = None
    child_application_status_description_text: Optional[str] = None
    child_application_filing_date: Optional[str] = None
    child_patent_number: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChildContinuity":
        """Create a ChildContinuity object from a dictionary."""
        return cls(
            first_inventor_to_file_indicator=data.get("firstInventorToFileIndicator"),
            child_application_status_code=data.get("childApplicationStatusCode"),
            parent_application_number_text=data.get("parentApplicationNumberText"),
            child_application_number_text=data.get("childApplicationNumberText"),
            child_application_status_description_text=data.get(
                "childApplicationStatusDescriptionText"
            ),
            child_application_filing_date=data.get("childApplicationFilingDate"),
            child_patent_number=data.get("childPatentNumber"),
            claim_parentage_type_code=data.get("claimParentageTypeCode"),
            claim_parentage_type_code_description_text=data.get(
                "claimParentageTypeCodeDescriptionText"
            ),
            # Map child-specific fields to base class fields
            status_code=data.get("childApplicationStatusCode"),
            status_description_text=data.get("childApplicationStatusDescriptionText"),
            filing_date=data.get("childApplicationFilingDate"),
            application_number_text=data.get("childApplicationNumberText"),
            patent_number=data.get("childPatentNumber"),
        )


@dataclass
class PatentTermAdjustmentHistoryData:
    """Represents patent term adjustment history data."""

    event_date: Optional[str] = None
    applicant_day_delay_quantity: Optional[float] = None
    event_description_text: Optional[str] = None
    event_sequence_number: Optional[float] = None
    ip_office_day_delay_quantity: Optional[float] = None
    originating_event_sequence_number: Optional[float] = None
    pta_pte_code: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PatentTermAdjustmentHistoryData":
        """Create a PatentTermAdjustmentHistoryData object from a dictionary."""
        return cls(
            event_date=data.get("eventDate"),
            applicant_day_delay_quantity=data.get("applicantDayDelayQuantity"),
            event_description_text=data.get("eventDescriptionText"),
            event_sequence_number=data.get("eventSequenceNumber"),
            ip_office_day_delay_quantity=data.get("ipOfficeDayDelayQuantity"),
            originating_event_sequence_number=data.get(
                "originatingEventSequenceNumber"
            ),
            pta_pte_code=data.get("ptaPTECode"),
        )


@dataclass
class PatentTermAdjustmentData:
    """Represents patent term adjustment data."""

    a_delay_quantity: Optional[float] = None
    adjustment_total_quantity: Optional[float] = None
    applicant_day_delay_quantity: Optional[float] = None
    b_delay_quantity: Optional[float] = None
    c_delay_quantity: Optional[float] = None
    filing_date: Optional[str] = None
    grant_date: Optional[str] = None
    non_overlapping_day_quantity: Optional[float] = None
    overlapping_day_quantity: Optional[float] = None
    ip_office_day_delay_quantity: Optional[float] = None
    patent_term_adjustment_history_data_bag: List[PatentTermAdjustmentHistoryData] = (
        field(default_factory=list)
    )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PatentTermAdjustmentData":
        """Create a PatentTermAdjustmentData object from a dictionary."""
        history_data = []
        if "patentTermAdjustmentHistoryDataBag" in data:
            history_data = [
                PatentTermAdjustmentHistoryData.from_dict(history)
                for history in data.get("patentTermAdjustmentHistoryDataBag", [])
            ]

        return cls(
            a_delay_quantity=data.get("aDelayQuantity"),
            adjustment_total_quantity=data.get("adjustmentTotalQuantity"),
            applicant_day_delay_quantity=data.get("applicantDayDelayQuantity"),
            b_delay_quantity=data.get("bDelayQuantity"),
            c_delay_quantity=data.get("cDelayQuantity"),
            filing_date=data.get("filingDate"),
            grant_date=data.get("grantDate"),
            non_overlapping_day_quantity=data.get("nonOverlappingDayQuantity"),
            overlapping_day_quantity=data.get("overlappingDayQuantity"),
            ip_office_day_delay_quantity=data.get("ipOfficeDayDelayQuantity"),
            patent_term_adjustment_history_data_bag=history_data,
        )


@dataclass
class Event:
    """Represents an event in the patent data."""

    event_code: Optional[str] = None
    event_description_text: Optional[str] = None
    event_date: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        """Create an Event object from a dictionary."""
        return cls(
            event_code=data.get("eventCode"),
            event_description_text=data.get("eventDescriptionText"),
            event_date=data.get("eventDate"),
        )


@dataclass
class DocumentMetaData:
    """Represents document metadata."""

    zip_file_name: Optional[str] = None
    product_identifier: Optional[str] = None
    file_location_uri: Optional[str] = None
    file_create_date_time: Optional[str] = None
    xml_file_name: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentMetaData":
        """Create a DocumentMetaData object from a dictionary."""
        return cls(
            zip_file_name=data.get("zipFileName"),
            product_identifier=data.get("productIdentifier"),
            file_location_uri=data.get("fileLocationURI"),
            file_create_date_time=data.get("fileCreateDateTime"),
            xml_file_name=data.get("xmlFileName"),
        )


@dataclass
class ApplicationMetaData:
    """Represents application metadata."""

    national_stage_indicator: Optional[bool] = None
    entity_status_data: Optional[EntityStatus] = None
    publication_date_bag: List[str] = field(default_factory=list)
    publication_sequence_number_bag: List[str] = field(default_factory=list)
    publication_category_bag: List[str] = field(default_factory=list)
    docket_number: Optional[str] = None
    first_inventor_to_file_indicator: Optional[str] = None
    first_applicant_name: Optional[str] = None
    first_inventor_name: Optional[str] = None
    application_confirmation_number: Optional[int] = None
    application_status_date: Optional[str] = None
    application_status_description_text: Optional[str] = None
    filing_date: Optional[str] = None
    effective_filing_date: Optional[str] = None
    grant_date: Optional[str] = None
    group_art_unit_number: Optional[str] = None
    application_type_code: Optional[str] = None
    application_type_label_name: Optional[str] = None
    application_type_category: Optional[str] = None
    invention_title: Optional[str] = None
    patent_number: Optional[str] = None
    application_status_code: Optional[int] = None
    earliest_publication_number: Optional[str] = None
    earliest_publication_date: Optional[str] = None
    pct_publication_number: Optional[str] = None
    pct_publication_date: Optional[str] = None
    international_registration_publication_date: Optional[str] = None
    international_registration_number: Optional[str] = None
    examiner_name_text: Optional[str] = None
    class_field: Optional[str] = None  # 'class' is a reserved keyword
    subclass: Optional[str] = None
    uspc_symbol_text: Optional[str] = None
    customer_number: Optional[int] = None
    cpc_classification_bag: List[str] = field(default_factory=list)
    applicant_bag: List[Applicant] = field(default_factory=list)
    inventor_bag: List[Inventor] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ApplicationMetaData":
        """Create an ApplicationMetaData object from a dictionary."""
        entity_status = None
        if "entityStatusData" in data and data.get("entityStatusData") is not None:
            entity_status = EntityStatus.from_dict(
                data=data.get("entityStatusData", {})
            )

        applicants = []
        if "applicantBag" in data:
            applicants = [
                Applicant.from_dict(data=applicant)
                for applicant in data.get("applicantBag", [])
            ]

        inventors = []
        if "inventorBag" in data:
            inventors = [
                Inventor.from_dict(data=inventor)
                for inventor in data.get("inventorBag", [])
            ]

        return cls(
            national_stage_indicator=data.get("nationalStageIndicator"),
            entity_status_data=entity_status,
            publication_date_bag=data.get("publicationDateBag", []),
            publication_sequence_number_bag=data.get(
                "publicationSequenceNumberBag", []
            ),
            publication_category_bag=data.get("publicationCategoryBag", []),
            docket_number=data.get("docketNumber"),
            first_inventor_to_file_indicator=data.get("firstInventorToFileIndicator"),
            first_applicant_name=data.get("firstApplicantName"),
            first_inventor_name=data.get("firstInventorName"),
            application_confirmation_number=data.get("applicationConfirmationNumber"),
            application_status_date=data.get("applicationStatusDate"),
            application_status_description_text=data.get(
                "applicationStatusDescriptionText"
            ),
            filing_date=data.get("filingDate"),
            effective_filing_date=data.get("effectiveFilingDate"),
            grant_date=data.get("grantDate"),
            group_art_unit_number=data.get("groupArtUnitNumber"),
            application_type_code=data.get("applicationTypeCode"),
            application_type_label_name=data.get("applicationTypeLabelName"),
            application_type_category=data.get("applicationTypeCategory"),
            invention_title=data.get("inventionTitle"),
            patent_number=data.get("patentNumber"),
            application_status_code=data.get("applicationStatusCode"),
            earliest_publication_number=data.get("earliestPublicationNumber"),
            earliest_publication_date=data.get("earliestPublicationDate"),
            pct_publication_number=data.get("pctPublicationNumber"),
            pct_publication_date=data.get("pctPublicationDate"),
            international_registration_publication_date=data.get(
                "internationalRegistrationPublicationDate"
            ),
            international_registration_number=data.get(
                "internationalRegistrationNumber"
            ),
            examiner_name_text=data.get("examinerNameText"),
            class_field=data.get("class"),  # Renamed due to reserved keyword
            subclass=data.get("subclass"),
            uspc_symbol_text=data.get("uspcSymbolText"),
            customer_number=data.get("customerNumber"),
            cpc_classification_bag=data.get("cpcClassificationBag", []),
            applicant_bag=applicants,
            inventor_bag=inventors,
        )


@dataclass
class PatentFileWrapper:
    """Represents a patent file wrapper."""

    application_number_text: Optional[str] = None
    application_meta_data: Optional[ApplicationMetaData] = None
    correspondence_address_bag: List[Address] = field(default_factory=list)
    assignment_bag: List[Assignment] = field(default_factory=list)
    record_attorney: Optional[RecordAttorney] = None
    foreign_priority_bag: List[ForeignPriority] = field(default_factory=list)
    parent_continuity_bag: List[ParentContinuity] = field(default_factory=list)
    child_continuity_bag: List[ChildContinuity] = field(default_factory=list)
    patent_term_adjustment_data: Optional[PatentTermAdjustmentData] = None
    event_data_bag: List[Event] = field(default_factory=list)
    pgpub_document_meta_data: Optional[DocumentMetaData] = None
    grant_document_meta_data: Optional[DocumentMetaData] = None
    last_ingestion_date_time: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PatentFileWrapper":
        """Create a PatentFileWrapper object from a dictionary."""
        application_meta = None
        if (
            "applicationMetaData" in data
            and data.get("applicationMetaData") is not None
        ):
            application_meta = ApplicationMetaData.from_dict(
                data=data.get("applicationMetaData", {})
            )

        addresses = []
        if "correspondenceAddressBag" in data:
            addresses = [
                Address.from_dict(data=addr)
                for addr in data.get("correspondenceAddressBag", [])
            ]

        assignments = []
        if "assignmentBag" in data:
            assignments = [
                Assignment.from_dict(data=assignment)
                for assignment in data.get("assignmentBag", [])
            ]

        record_atty = None
        if "recordAttorney" in data and data.get("recordAttorney") is not None:
            record_atty = RecordAttorney.from_dict(data=data.get("recordAttorney", {}))

        foreign_priorities = []
        if "foreignPriorityBag" in data:
            foreign_priorities = [
                ForeignPriority.from_dict(data=priority)
                for priority in data.get("foreignPriorityBag", [])
            ]

        parent_continuities = []
        if "parentContinuityBag" in data:
            parent_continuities = [
                ParentContinuity.from_dict(data=continuity)
                for continuity in data.get("parentContinuityBag", [])
            ]

        child_continuities = []
        if "childContinuityBag" in data:
            child_continuities = [
                ChildContinuity.from_dict(data=continuity)
                for continuity in data.get("childContinuityBag", [])
            ]

        patent_term = None
        if (
            "patentTermAdjustmentData" in data
            and data.get("patentTermAdjustmentData") is not None
        ):
            patent_term = PatentTermAdjustmentData.from_dict(
                data=data.get("patentTermAdjustmentData", {})
            )

        events = []
        if "eventDataBag" in data:
            events = [
                Event.from_dict(data=event) for event in data.get("eventDataBag", [])
            ]

        pgpub_meta = None
        if (
            "pgpubDocumentMetaData" in data
            and data.get("pgpubDocumentMetaData") is not None
        ):
            pgpub_meta = DocumentMetaData.from_dict(
                data=data.get("pgpubDocumentMetaData", {})
            )

        grant_meta = None
        if (
            "grantDocumentMetaData" in data
            and data.get("grantDocumentMetaData") is not None
        ):
            grant_meta = DocumentMetaData.from_dict(
                data=data.get("grantDocumentMetaData", {})
            )

        return cls(
            application_number_text=data.get("applicationNumberText"),
            application_meta_data=application_meta,
            correspondence_address_bag=addresses,
            assignment_bag=assignments,
            record_attorney=record_atty,
            foreign_priority_bag=foreign_priorities,
            parent_continuity_bag=parent_continuities,
            child_continuity_bag=child_continuities,
            patent_term_adjustment_data=patent_term,
            event_data_bag=events,
            pgpub_document_meta_data=pgpub_meta,
            grant_document_meta_data=grant_meta,
            last_ingestion_date_time=data.get("lastIngestionDateTime"),
        )
