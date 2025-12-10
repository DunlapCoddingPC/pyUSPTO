"""
Tests for PTABInterferencesClient.

This module contains unit tests for the PTABInterferencesClient class.
"""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from pyUSPTO import PTABInterferencesClient, USPTOConfig
from pyUSPTO.models.ptab import PTABInterferenceResponse


@pytest.fixture
def api_key_fixture() -> str:
    """Fixture for test API key."""
    return "test_key"


@pytest.fixture
def interference_decision_sample() -> dict[str, Any]:
    """Sample interference decision data for testing."""
    return {
        "count": 2,
        "requestIdentifier": "c76aa849-bd60-40db-a98b-c8cbc143d4f9",
        "patentInterferenceDataBag": [
            {
                "interferenceNumber": "104807",
                "lastModifiedDateTime": "2025-11-20T03:12:32",
                "interferenceMetaData": {
                    "interferenceLastModifiedDateTime": "2006-12-22T00:00:00",
                    "interferenceLastModifiedDate": "2006-12-22",
                    "declarationDate": "2002-12-11",
                    "interferenceStyleName": "VINOGRADOV V. FLAMM",
                    "fileDownloadURI": "https://api.uspto.gov/api/v1/patent/ptab-files/INTF/104807/104807.zip",
                },
                "seniorPartyData": {
                    "applicationNumberText": "08739037",
                    "grantDate": "1999-10-12",
                    "groupArtUnitNumber": "1763",
                    "inventorName": "GEORGY  VINOGRADOV et al",
                    "patentNumber": "5965034",
                    "patentOwnerName": "GEORGY  VINOGRADOV et al",
                    "realPartyInInterestName": "GEORGY  VINOGRADOV et al",
                    "technologyCenterNumber": "1700",
                },
                "juniorPartyData": {
                    "applicationNumberText": "08748746",
                    "grantDate": "2005-02-22",
                    "groupArtUnitNumber": "1763",
                    "inventorName": "DANIEL L.  FLAMM et al",
                    "patentNumber": "6858112",
                    "patentOwnerName": "DANIEL L.  FLAMM et al",
                    "publicationDate": "2003-09-11",
                    "publicationNumber": "20030168427A1",
                    "realPartyInInterestName": "DANIEL L.  FLAMM et al",
                    "technologyCenterNumber": "1700",
                },
                "documentData": {
                    "documentIdentifier": "b8c473a3bcab88d5c33ef3231daf45a10f967103a89b8db9c791d1ee",
                    "documentName": "fd10480712-11-2002",
                    "documentSizeQuantity": 160468,
                    "documentOCRText": "The opinion in support of the decision being \nentered today is not binding precedent of the Board.  \n\nPaper 20 \nFiled by: Trial Section Motions Panel \n\nBox Interference Filed: December 11, 2002 \nWashington, D.C. 20231 \nTel: 703-308-9797 \nFax: 703-305-0942 \n\nUNITED STATES PATENT AND TRADEMARK OFFICE \n\nBEFORE THE BOARD OF PATENT APPEALS \nAND INTERFERENCES \n\nMAILED \nDANIEL L. FLAMM \n\nJunior Party DEC 2002 \n(U.S. Application 08/748,746), \n\nPAT & TM OFFICE BOARD OF PATENT \nV. AND INTERFER,'N\"FALS \n\nGEORGY",
                    "documentTitleText": "DECISION-104807",
                    "interferenceOutcomeCategory": "Final Decision",
                    "decisionIssueDate": "2002-12-11",
                    "decisionTypeCategory": "Decision",
                    "fileDownloadURI": "https://api.uspto.gov/api/v1/patent/ptab-files/INTF/104807/Intf608_10480708739037_1039582800000.pdf",
                    "documentFilingDate": "2002-12-11",
                },
            },
            {
                "interferenceNumber": "103751",
                "lastModifiedDateTime": "2025-11-20T03:12:32",
                "interferenceMetaData": {
                    "interferenceLastModifiedDateTime": "2006-02-08T00:00:00",
                    "interferenceLastModifiedDate": "2006-02-08",
                    "declarationDate": "2002-02-25",
                    "interferenceStyleName": "TANG",
                    "fileDownloadURI": "https://api.uspto.gov/api/v1/patent/ptab-files/INTF/103751/103751.zip",
                },
                "seniorPartyData": {
                    "applicationNumberText": "07996817",
                    "grantDate": "2003-09-02",
                    "groupArtUnitNumber": "1763",
                    "inventorName": "  TANG",
                    "patentNumber": "6614529",
                    "patentOwnerName": "  TANG",
                    "realPartyInInterestName": "  TANG",
                    "technologyCenterNumber": "1700",
                },
                "documentData": {
                    "documentIdentifier": "a1adf3e98f9e07271420b607222b5ad0ddc7198317be600b7c48a3be",
                    "documentName": "jd103751",
                    "documentSizeQuantity": 45224,
                    "documentOCRText": "E:\\FY2002~5\\FEB200~7\\FEB200~4\\JD103751.WPD\n\n\nThe opinion in support of the decision being\nentered today is not binding precedent of the Board.\n\n                                                  Paper 62\nFiled by: Interference Trial Section Merits Panel\n           Box Interference                       Filed:\n           Washington, D.C.  20231                    25 February 2002\n           Tel:  703-308-9797\n           Fax:  703-305-0942\n\nUNITED STATES PATENT AND TRADEMARK OFFICE\n____________",
                    "documentTitleText": "DECISION-103751",
                    "interferenceOutcomeCategory": "Final Decision",
                    "decisionIssueDate": "2002-02-25",
                    "decisionTypeCategory": "Decision",
                    "fileDownloadURI": "https://api.uspto.gov/api/v1/patent/ptab-files/INTF/103751/Intf608_10375107996817_1014613200000.pdf",
                    "documentFilingDate": "2002-02-25",
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
        interference_decision_sample: dict[str, Any],
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
        interference_decision_sample: dict[str, Any],
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
            interference_outcome_category_q="Final Decision",
            decision_type_category_q="Decision",
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
        assert 'seniorPartyData.patentOwnerName:"Senior Party Inc."' in params["q"]
        assert 'juniorPartyData.patentOwnerName:"Junior Party LLC"' in params["q"]
        assert (
            'documentData.interferenceOutcomeCategory:"Final Decision"' in params["q"]
        )
        assert 'documentData.decisionTypeCategory:"Decision"' in params["q"]
        assert (
            "documentData.decisionIssueDate:[2023-01-01 TO 2023-12-31]" in params["q"]
        )
        assert params["limit"] == 25

    def test_search_decisions_get_with_date_from_only(
        self,
        mock_ptab_interferences_client: PTABInterferencesClient,
        interference_decision_sample: dict[str, Any],
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
        assert "documentData.decisionIssueDate:>=2023-01-01" in params["q"]

    def test_search_decisions_get_with_date_to_only(
        self,
        mock_ptab_interferences_client: PTABInterferencesClient,
        interference_decision_sample: dict[str, Any],
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
        assert "documentData.decisionIssueDate:<=2023-12-31" in params["q"]

    def test_search_decisions_get_with_all_convenience_params(
        self,
        mock_ptab_interferences_client: PTABInterferencesClient,
        interference_decision_sample: dict[str, Any],
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
        assert "seniorPartyData.applicationNumberText:12/345678" in params["q"]
        assert "juniorPartyData.applicationNumberText:13/987654" in params["q"]
        assert 'seniorPartyData.patentOwnerName:"Senior Party Inc."' in params["q"]
        assert 'juniorPartyData.patentOwnerName:"Junior Party LLC"' in params["q"]
        assert (
            'documentData.interferenceOutcomeCategory:"Priority to Senior Party"'
            in params["q"]
        )
        assert 'documentData.decisionTypeCategory:"Final Decision"' in params["q"]

    def test_search_decisions_with_real_party_in_interest_q(
        self,
        mock_ptab_interferences_client: PTABInterferencesClient,
        interference_decision_sample: dict[str, Any],
    ) -> None:
        """Test search_decisions with real_party_in_interest_q parameter."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = interference_decision_sample
        mock_session.get.return_value = mock_response
        mock_ptab_interferences_client.session = mock_session

        # Test
        result = mock_ptab_interferences_client.search_decisions(
            real_party_in_interest_q="Tech Company Inc."
        )

        # Verify
        assert isinstance(result, PTABInterferenceResponse)
        call_args = mock_session.get.call_args
        params = call_args[1]["params"]
        assert (
            'seniorPartyData.realPartyInInterestName:"Tech Company Inc." OR juniorPartyData.realPartyInInterestName:"Tech Company Inc."'
            in params["q"]
        )

    def test_search_decisions_post_with_body(
        self,
        mock_ptab_interferences_client: PTABInterferencesClient,
        interference_decision_sample: dict[str, Any],
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
        interference_decision_sample: dict[str, Any],
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
