"""Data models for the Petition Decisions API."""

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pyUSPTO.models.patent_data import (
    parse_to_date,
    parse_to_datetime_utc,
    serialize_date,
    serialize_datetime_as_iso,
    to_camel_case,
)


@dataclass(frozen=True)
class PetitionDecision:
    """Represents a single petition decision record."""

    action_taken_by_court_name: Optional[str] = None
    application_number_text: Optional[str] = None
    business_entity_status_category: Optional[str] = None
    court_action_indicator: Optional[bool] = None
    customer_number: Optional[int] = None
    decision_date: Optional[date] = None
    decision_petition_type_code: Optional[int] = None
    decision_type_code: Optional[str] = None
    decision_type_code_description_text: Optional[str] = None
    final_deciding_office_name: Optional[str] = None
    first_applicant_name: Optional[str] = None
    first_inventor_to_file_indicator: Optional[bool] = None
    group_art_unit_number: Optional[str] = None
    invention_title: Optional[str] = None
    inventor_bag: List[str] = field(default_factory=list)
    last_ingestion_date_time: Optional[datetime] = None
    petition_decision_record_identifier: Optional[str] = None
    petition_issue_considered_text_bag: List[str] = field(default_factory=list)
    petition_mail_date: Optional[date] = None
    rule_bag: List[str] = field(default_factory=list)
    technology_center: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PetitionDecision":
        """Create a :class:`PetitionDecision` from API data."""
        return cls(
            action_taken_by_court_name=data.get("actionTakenByCourtName"),
            application_number_text=data.get("applicationNumberText"),
            business_entity_status_category=data.get("businessEntityStatusCategory"),
            court_action_indicator=data.get("courtActionIndicator"),
            customer_number=data.get("customerNumber"),
            decision_date=parse_to_date(data.get("decisionDate")),
            decision_petition_type_code=data.get("decisionPetitionTypeCode"),
            decision_type_code=data.get("decisionTypeCode"),
            decision_type_code_description_text=data.get("decisionTypeCodeDescriptionText"),
            final_deciding_office_name=data.get("finalDecidingOfficeName"),
            first_applicant_name=data.get("firstApplicantName"),
            first_inventor_to_file_indicator=data.get("firstInventorToFileIndicator"),
            group_art_unit_number=data.get("groupArtUnitNumber"),
            invention_title=data.get("inventionTitle"),
            inventor_bag=data.get("inventorBag", []),
            last_ingestion_date_time=parse_to_datetime_utc(data.get("lastIngestionDateTime")),
            petition_decision_record_identifier=data.get("petitionDecisionRecordIdentifier"),
            petition_issue_considered_text_bag=data.get("petitionIssueConsideredTextBag", []),
            petition_mail_date=parse_to_date(data.get("petitionMailDate")),
            rule_bag=data.get("ruleBag", []),
            technology_center=data.get("technologyCenter"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert the decision to a dictionary with camelCase keys."""

        d = asdict(self)
        d["decision_date"] = serialize_date(self.decision_date)
        d["petition_mail_date"] = serialize_date(self.petition_mail_date)
        d["last_ingestion_date_time"] = serialize_datetime_as_iso(
            self.last_ingestion_date_time
        )
        return {
            to_camel_case(k): v
            for k, v in d.items()
            if v is not None and (not isinstance(v, list) or v)
        }


@dataclass(frozen=True)
class PetitionDecisionsResponse:
    """Top level response from the Petition Decisions API."""

    count: int
    request_identifier: Optional[str] = None
    petition_decision_data_bag: List[PetitionDecision] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PetitionDecisionsResponse":
        """Create a :class:`PetitionDecisionsResponse` from API data."""
        return cls(
            count=data.get("count", 0),
            request_identifier=data.get("requestIdentifier"),
            petition_decision_data_bag=[
                PetitionDecision.from_dict(d)
                for d in data.get("petitionDecisionDataBag", [])
                if isinstance(d, dict)
            ],
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert this response object back to a dictionary."""
        d = asdict(self)
        d["petition_decision_data_bag"] = [
            dec.to_dict() for dec in self.petition_decision_data_bag
        ]
        return {
            to_camel_case(k): v
            for k, v in d.items()
            if v is not None and (not isinstance(v, list) or v)
        }

