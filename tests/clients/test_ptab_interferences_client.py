"""
Tests for PTABInterferencesClient.

This module contains unit tests for the PTABInterferencesClient class.
"""

from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

from pyUSPTO import PTABInterferencesClient, USPTOConfig
from pyUSPTO.models.ptab import PTABInterferenceDecision, PTABInterferenceResponse


@pytest.fixture
def api_key_fixture() -> str:
    """Fixture for test API key."""
    return "test_key"


@pytest.fixture
def interference_decision_sample() -> Dict[str, Any]:
    """Sample interference decision data for testing."""
    return {
        "count": 2,
        "requestIdentifier": "req-123",
        "patentInterferenceDataBag": [
            {
                "interferenceNumber": "106123",
                "interferenceRecordIdentifier": "interference-uuid-1",
                "lastModifiedDateTime": "2023-03-15T10:30:00Z",
                "interferenceMetaData": {
                    "seniorPartyApplicationNumber": "12/345678",
                    "juniorPartyApplicationNumber": "13/987654",
                    "seniorPartyName": "Senior Party Inc.",
                    "juniorPartyName": "Junior Party LLC",
                },
                "documentData": {
                    "interferenceOutcomeCategory": "Priority to Senior Party",
                    "decisionTypeCategory": "Final Decision",
                    "decisionDate": "2023-03-01",
                },
            },
            {
                "interferenceNumber": "106124",
                "interferenceRecordIdentifier": "interference-uuid-2",
                "lastModifiedDateTime": "2023-03-20T14:00:00Z",
                "interferenceMetaData": {
                    "seniorPartyApplicationNumber": "14/111222",
                    "juniorPartyApplicationNumber": "14/333444",
                },
                "documentData": {
                    "interferenceOutcomeCategory": "Priority to Junior Party",
                    "decisionTypeCategory": "Judgment",
                    "decisionDate": "2023-03-10",
                },
            },
        ],
    }


@pytest.fixture
def mock_ptab_interferences_client(api_key_fixture: str) -> PTABInterferencesClient:
    """Fixture for mock PTABInterferencesClient."""
    return PTABInterferencesClient(api_key=api_key_fixture)


class TestPTABInterferencesClientInit:
    """Tests for initialization of PTABInterferencesClient."""

    def test_init_with_api_key(self, api_key_fixture: str) -> None:
        """Test initialization with API key."""
        client = PTABInterferencesClient(api_key=api_key_fixture)
        assert client._api_key == api_key_fixture
        assert client.base_url == "https://api.uspto.gov"

    def test_init_with_custom_base_url(self, api_key_fixture: str) -> None:
        """Test initialization with custom base URL."""
        custom_url = "https://custom.api.test.com"
        client = PTABInterferencesClient(api_key=api_key_fixture, base_url=custom_url)
        assert client._api_key == api_key_fixture
        assert client.base_url == custom_url

    def test_init_with_config(self) -> None:
        """Test initialization with config object."""
        config_key = "config_key"
        config_url = "https://config.api.test.com"
        config = USPTOConfig(api_key=config_key, ptab_base_url=config_url)
        client = PTABInterferencesClient(config=config)
        assert client._api_key == config_key
        assert client.base_url == config_url
        assert client.config is config

    def test_init_with_api_key_and_config(self, api_key_fixture: str) -> None:
        """Test initialization with both API key and config."""
        config = USPTOConfig(
            api_key="config_key",
            ptab_base_url="https://config.api.test.com",
        )
        client = PTABInterferencesClient(api_key=api_key_fixture, config=config)
        # API key parameter takes precedence
        assert client._api_key == api_key_fixture
        # But base_url comes from config
        assert client.base_url == "https://config.api.test.com"


class TestPTABInterferencesClientSearchDecisions:
    """Tests for search_decisions method."""

    def test_search_decisions_get_with_query(
        self,
        mock_ptab_interferences_client: PTABInterferencesClient,
        interference_decision_sample: Dict[str, Any],
    ) -> None:
        """Test search_decisions with GET and direct query."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = interference_decision_sample
        mock_session.get.return_value = mock_response
        mock_ptab_interferences_client.session = mock_session

        # Test
        result = mock_ptab_interferences_client.search_decisions(
            query="interferenceNumber:106123", limit=10
        )

        # Verify
        assert isinstance(result, PTABInterferenceResponse)
        assert result.count == 2
        assert len(result.patent_interference_data_bag) == 2
        mock_session.get.assert_called_once()
        call_args = mock_session.get.call_args
        assert "q" in call_args[1]["params"]
        assert call_args[1]["params"]["q"] == "interferenceNumber:106123"

    def test_search_decisions_get_with_convenience_params(
        self,
        mock_ptab_interferences_client: PTABInterferencesClient,
        interference_decision_sample: Dict[str, Any],
    ) -> None:
        """Test search_decisions with convenience parameters."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = interference_decision_sample
        mock_session.get.return_value = mock_response
        mock_ptab_interferences_client.session = mock_session

        # Test
        result = mock_ptab_interferences_client.search_decisions(
            interference_number_q="106123",
            senior_party_name_q="Senior Party Inc.",
            junior_party_name_q="Junior Party LLC",
            interference_outcome_category_q="Priority to Senior Party",
            decision_type_category_q="Final Decision",
            decision_date_from_q="2023-01-01",
            decision_date_to_q="2023-12-31",
            limit=25,
            additional_query_params={"interferenceNumber": "106123"},
        )

        # Verify
        assert isinstance(result, PTABInterferenceResponse)
        mock_session.get.assert_called_once()
        call_args = mock_session.get.call_args
        params = call_args[1]["params"]
        assert "q" in params
        assert "106123" in params["interferenceNumber"]
        assert "seniorPartyName:Senior Party Inc." in params["q"]
        assert "juniorPartyName:Junior Party LLC" in params["q"]
        assert "interferenceOutcomeCategory:Priority to Senior Party" in params["q"]
        assert "decisionTypeCategory:Final Decision" in params["q"]
        assert "decisionDate:[2023-01-01 TO 2023-12-31]" in params["q"]
        assert params["limit"] == 25

    def test_search_decisions_get_with_date_from_only(
        self,
        mock_ptab_interferences_client: PTABInterferencesClient,
        interference_decision_sample: Dict[str, Any],
    ) -> None:
        """Test search_decisions with only date_from parameter."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = interference_decision_sample
        mock_session.get.return_value = mock_response
        mock_ptab_interferences_client.session = mock_session

        # Test
        result = mock_ptab_interferences_client.search_decisions(
            decision_date_from_q="2023-01-01"
        )

        # Verify
        assert isinstance(result, PTABInterferenceResponse)
        call_args = mock_session.get.call_args
        params = call_args[1]["params"]
        assert "decisionDate:>=2023-01-01" in params["q"]

    def test_search_decisions_get_with_date_to_only(
        self,
        mock_ptab_interferences_client: PTABInterferencesClient,
        interference_decision_sample: Dict[str, Any],
    ) -> None:
        """Test search_decisions with only date_to parameter."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = interference_decision_sample
        mock_session.get.return_value = mock_response
        mock_ptab_interferences_client.session = mock_session

        # Test
        result = mock_ptab_interferences_client.search_decisions(
            decision_date_to_q="2023-12-31"
        )

        # Verify
        assert isinstance(result, PTABInterferenceResponse)
        call_args = mock_session.get.call_args
        params = call_args[1]["params"]
        assert "decisionDate:<=2023-12-31" in params["q"]

    def test_search_decisions_get_with_all_convenience_params(
        self,
        mock_ptab_interferences_client: PTABInterferencesClient,
        interference_decision_sample: Dict[str, Any],
    ) -> None:
        """Test search_decisions with all convenience parameters."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = interference_decision_sample
        mock_session.get.return_value = mock_response
        mock_ptab_interferences_client.session = mock_session

        # Test
        result = mock_ptab_interferences_client.search_decisions(
            interference_number_q="106123",
            senior_party_application_number_q="12/345678",
            junior_party_application_number_q="13/987654",
            senior_party_name_q="Senior Party Inc.",
            junior_party_name_q="Junior Party LLC",
            interference_outcome_category_q="Priority to Senior Party",
            decision_type_category_q="Final Decision",
            decision_date_from_q="2023-01-01",
            decision_date_to_q="2023-12-31",
        )

        # Verify
        assert isinstance(result, PTABInterferenceResponse)
        call_args = mock_session.get.call_args
        params = call_args[1]["params"]
        assert "interferenceNumber:106123" in params["q"]
        assert "seniorPartyApplicationNumber:12/345678" in params["q"]
        assert "juniorPartyApplicationNumber:13/987654" in params["q"]
        assert "seniorPartyName:Senior Party Inc." in params["q"]
        assert "juniorPartyName:Junior Party LLC" in params["q"]
        assert "interferenceOutcomeCategory:Priority to Senior Party" in params["q"]
        assert "decisionTypeCategory:Final Decision" in params["q"]

    def test_search_decisions_post_with_body(
        self,
        mock_ptab_interferences_client: PTABInterferencesClient,
        interference_decision_sample: Dict[str, Any],
    ) -> None:
        """Test search_decisions with POST body."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = interference_decision_sample
        mock_session.post.return_value = mock_response
        mock_ptab_interferences_client.session = mock_session

        post_body = {
            "q": "interferenceOutcomeCategory:Priority to Senior Party",
            "limit": 100,
        }

        # Test
        result = mock_ptab_interferences_client.search_decisions(post_body=post_body)

        # Verify
        assert isinstance(result, PTABInterferenceResponse)
        mock_session.post.assert_called_once()
        call_args = mock_session.post.call_args
        assert call_args[1]["json"] == post_body

    def test_search_decisions_with_optional_params(
        self,
        mock_ptab_interferences_client: PTABInterferencesClient,
        interference_decision_sample: Dict[str, Any],
    ) -> None:
        """Test search_decisions with optional parameters like sort, facets, etc."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = interference_decision_sample
        mock_session.get.return_value = mock_response
        mock_ptab_interferences_client.session = mock_session

        # Test
        result = mock_ptab_interferences_client.search_decisions(
            query="interferenceNumber:106123",
            sort="decisionDate desc",
            offset=10,
            limit=50,
            facets="interferenceOutcomeCategory",
            fields="interferenceNumber,decisionDate",
            filters="decisionTypeCategory:Final Decision",
            range_filters="decisionDate:[2023-01-01 TO 2023-12-31]",
        )

        # Verify
        assert isinstance(result, PTABInterferenceResponse)
        call_args = mock_session.get.call_args
        params = call_args[1]["params"]
        assert params["sort"] == "decisionDate desc"
        assert params["offset"] == 10
        assert params["limit"] == 50
        assert params["facets"] == "interferenceOutcomeCategory"
        assert params["fields"] == "interferenceNumber,decisionDate"
        assert params["filters"] == "decisionTypeCategory:Final Decision"
        assert params["rangeFilters"] == "decisionDate:[2023-01-01 TO 2023-12-31]"


class TestPTABInterferencesClientPaginate:
    """Tests for paginate_decisions method."""

    def test_paginate_decisions(
        self, mock_ptab_interferences_client: PTABInterferencesClient
    ) -> None:
        """Test paginate_decisions method."""
        # Setup mock responses
        first_response = PTABInterferenceResponse.from_dict(
            {
                "count": 2,
                "requestIdentifier": "req-1",
                "patentInterferenceDataBag": [
                    {"interferenceNumber": "106123"},
                    {"interferenceNumber": "106124"},
                ],
            }
        )

        second_response = PTABInterferenceResponse.from_dict(
            {
                "count": 1,
                "requestIdentifier": "req-2",
                "patentInterferenceDataBag": [
                    {"interferenceNumber": "106125"},
                ],
            }
        )

        third_response = PTABInterferenceResponse.from_dict(
            {
                "count": 0,
                "requestIdentifier": "req-3",
                "patentInterferenceDataBag": [],
            }
        )

        # Mock search_decisions to return different responses
        with patch.object(
            mock_ptab_interferences_client, "search_decisions"
        ) as mock_search:
            mock_search.side_effect = [first_response, second_response, third_response]

            # Test
            results = list(
                mock_ptab_interferences_client.paginate_decisions(
                    interference_outcome_category_q="Priority to Senior Party", limit=2
                )
            )

            # Verify
            assert len(results) == 3
            assert results[0].interference_number == "106123"
            assert results[1].interference_number == "106124"
            assert results[2].interference_number == "106125"
            assert mock_search.call_count == 2  # Stops when count < limit

    def test_paginate_decisions_raises_on_post_body(
        self, mock_ptab_interferences_client: PTABInterferencesClient
    ) -> None:
        """Test that paginate_decisions raises ValueError with post_body."""
        with pytest.raises(ValueError, match="does not support 'post_body'"):
            list(
                mock_ptab_interferences_client.paginate_decisions(
                    post_body={"q": "test"}
                )
            )

    def test_paginate_decisions_with_multiple_params(
        self, mock_ptab_interferences_client: PTABInterferencesClient
    ) -> None:
        """Test paginate_decisions with multiple search parameters."""
        # Setup mock responses
        first_response = PTABInterferenceResponse.from_dict(
            {
                "count": 2,
                "requestIdentifier": "req-1",
                "patentInterferenceDataBag": [
                    {"interferenceNumber": "106123"},
                    {"interferenceNumber": "106124"},
                ],
            }
        )

        second_response = PTABInterferenceResponse.from_dict(
            {
                "count": 0,
                "requestIdentifier": "req-2",
                "patentInterferenceDataBag": [],
            }
        )

        with patch.object(
            mock_ptab_interferences_client, "search_decisions"
        ) as mock_search:
            mock_search.side_effect = [first_response, second_response]

            # Test
            results = list(
                mock_ptab_interferences_client.paginate_decisions(
                    interference_outcome_category_q="Priority to Senior Party",
                    decision_type_category_q="Final Decision",
                    decision_date_from_q="2023-01-01",
                    limit=2,
                )
            )

            # Verify
            assert len(results) == 2
            # Verify that search_decisions was called with correct params
            call_args = mock_search.call_args_list[0]
            assert (
                call_args[1]["interference_outcome_category_q"]
                == "Priority to Senior Party"
            )
            assert call_args[1]["decision_type_category_q"] == "Final Decision"
            assert call_args[1]["decision_date_from_q"] == "2023-01-01"
