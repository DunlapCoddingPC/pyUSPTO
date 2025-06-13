"""Tests for petition decision models."""

from pyUSPTO.models.petition_decisions import PetitionDecision, PetitionDecisionsResponse


class TestPetitionDecisionModels:
    def test_petition_decision_from_empty_dict(self) -> None:
        decision = PetitionDecision.from_dict({})
        assert decision.application_number_text is None
        assert decision.court_action_indicator is None

    def test_petition_decisions_response_from_empty_dict(self) -> None:
        resp = PetitionDecisionsResponse.from_dict({})
        assert resp.count == 0
        assert resp.petition_decision_data_bag == []
