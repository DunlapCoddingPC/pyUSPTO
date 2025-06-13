"""Tests for PetitionDecisionsClient."""

from typing import Any, Dict
from unittest.mock import MagicMock, patch

from pyUSPTO.clients.petition_decisions import PetitionDecisionsClient
from pyUSPTO.models.petition_decisions import PetitionDecisionsResponse


class TestPetitionDecisionsClient:
    def test_search_decisions(self, mock_petition_decisions_client: PetitionDecisionsClient, petition_decisions_sample: Dict[str, Any]) -> None:
        mock_response = PetitionDecisionsResponse.from_dict(petition_decisions_sample)

        with patch.object(
            mock_petition_decisions_client,
            "_make_request",
            return_value=mock_response,
        ) as mock_request:
            result = mock_petition_decisions_client.search_decisions(query="test", limit=5)

        mock_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/petition/decisions/search",
            params={"q": "test", "limit": 5},
            response_class=PetitionDecisionsResponse,
        )
        assert result is mock_response
