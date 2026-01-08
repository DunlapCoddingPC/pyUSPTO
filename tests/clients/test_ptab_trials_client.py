"""
Tests for PTABTrialsClient.

This module contains unit tests for the PTABTrialsClient class.
"""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from pyUSPTO import PTABTrialsClient, USPTOConfig
from pyUSPTO.models.ptab import (
    PTABTrialDocumentResponse,
    PTABTrialProceedingResponse,
)


@pytest.fixture
def api_key_fixture() -> str:
    """Fixture for test API key."""
    return "test_key"


@pytest.fixture
def trial_proceeding_sample() -> dict[str, Any]:
    """Sample trial proceeding data for testing."""
    return {
        "count": 2,
        "requestIdentifier": "req-123",
        "patentTrialProceedingDataBag": [
            {
                "trialNumber": "IPR2023-00001",
                "trialRecordIdentifier": "trial-uuid-1",
                "lastModifiedDateTime": "2023-01-15T10:30:00Z",
                "trialMetaData": {
                    "petitionFilingDate": "2023-01-01",
                    "trialStatusCategory": "Active",
                    "trialTypeCode": "IPR",
                },
                "patentOwnerData": {
                    "patentOwnerName": "Test Company",
                    "patentNumber": "US1234567",
                },
            },
            {
                "trialNumber": "IPR2023-00002",
                "trialRecordIdentifier": "trial-uuid-2",
                "lastModifiedDateTime": "2023-01-20T14:00:00Z",
                "trialMetaData": {
                    "petitionFilingDate": "2023-01-10",
                    "trialStatusCategory": "Terminated",
                    "trialTypeCode": "PGR",
                },
            },
        ],
    }


@pytest.fixture
def trial_document_sample() -> dict[str, Any]:
    """Sample trial document data for testing."""
    return {
        "count": 2,
        "patentTrialDocumentDataBag": [
            {
                "trialNumber": "IPR2023-00001",
                "trialDocumentCategory": "Document",
                "lastModifiedDateTime": "2023-01-15T10:30:00Z",
                "trialTypeCode": "IPR",
                "documentData": {
                    "documentName": "Petition.pdf",
                    "documentIdentifier": "doc-123",
                    "documentFilingDate": "2023-01-10",
                },
            },
            {
                "trialNumber": "IPR2023-00002",
                "trialDocumentCategory": "Decision",
                "lastModifiedDateTime": "2023-06-15T14:00:00Z",
                "trialTypeCode": "IPR",
                "decisionData": {
                    "decisionTypeCategory": "Final Written Decision",
                    "decisionIssueDate": "2023-06-10",
                },
            },
        ],
    }


@pytest.fixture
def mock_ptab_trials_client(api_key_fixture: str) -> PTABTrialsClient:
    """Fixture for mock PTABTrialsClient."""
    return PTABTrialsClient(api_key=api_key_fixture)


class TestPTABTrialsClientInit:
    """Tests for initialization of PTABTrialsClient."""

    def test_init_with_api_key(self, api_key_fixture: str) -> None:
        """Test initialization with API key."""
        client = PTABTrialsClient(api_key=api_key_fixture)
        assert client._api_key == api_key_fixture
        assert client.base_url == "https://api.uspto.gov"

    def test_init_with_custom_base_url(self, api_key_fixture: str) -> None:
        """Test initialization with custom base URL."""
        custom_url = "https://custom.api.test.com"
        client = PTABTrialsClient(api_key=api_key_fixture, base_url=custom_url)
        assert client._api_key == api_key_fixture
        assert client.base_url == custom_url

    def test_init_with_config(self) -> None:
        """Test initialization with config object."""
        config_key = "config_key"
        config_url = "https://config.api.test.com"
        config = USPTOConfig(api_key=config_key, ptab_base_url=config_url)
        client = PTABTrialsClient(config=config)
        assert client._api_key == config_key
        assert client.base_url == config_url
        assert client.config is config

    def test_init_with_api_key_and_config(self, api_key_fixture: str) -> None:
        """Test initialization with both API key and config."""
        config = USPTOConfig(
            api_key="config_key",
            ptab_base_url="https://config.api.test.com",
        )
        client = PTABTrialsClient(api_key=api_key_fixture, config=config)
        # API key parameter takes precedence
        assert client._api_key == api_key_fixture
        # But base_url comes from config
        assert client.base_url == "https://config.api.test.com"


class TestPTABTrialsClientSearchProceedings:
    """Tests for search_proceedings method."""

    def test_search_proceedings_get_with_query(
        self,
        mock_ptab_trials_client: PTABTrialsClient,
        trial_proceeding_sample: dict[str, Any],
    ) -> None:
        """Test search_proceedings with GET and direct query."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = trial_proceeding_sample
        mock_session.get.return_value = mock_response
        mock_ptab_trials_client.session = mock_session

        # Test
        result = mock_ptab_trials_client.search_proceedings(
            query="trialNumber:IPR2023-00001", limit=10
        )

        # Verify
        assert isinstance(result, PTABTrialProceedingResponse)
        assert result.count == 2
        assert len(result.patent_trial_proceeding_data_bag) == 2
        mock_session.get.assert_called_once()
        call_args = mock_session.get.call_args
        assert "q" in call_args[1]["params"]
        assert call_args[1]["params"]["q"] == "trialNumber:IPR2023-00001"

    def test_search_proceedings_get_with_convenience_params(
        self,
        mock_ptab_trials_client: PTABTrialsClient,
        trial_proceeding_sample: dict[str, Any],
    ) -> None:
        """Test search_proceedings with convenience parameters."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = trial_proceeding_sample
        mock_session.get.return_value = mock_response
        mock_ptab_trials_client.session = mock_session

        # Test
        result = mock_ptab_trials_client.search_proceedings(
            trial_number_q="IPR2023-00001",
            trial_type_code_q="IPR",
            petition_filing_date_from_q="2023-01-01",
            petition_filing_date_to_q="2023-12-31",
            limit=25,
        )

        # Verify
        assert isinstance(result, PTABTrialProceedingResponse)
        mock_session.get.assert_called_once()
        call_args = mock_session.get.call_args
        params = call_args[1]["params"]
        assert "q" in params
        assert "trialNumber:IPR2023-00001" in params["q"]
        assert "trialTypeCode:IPR" in params["q"]
        assert "petitionFilingDate:[2023-01-01 TO 2023-12-31]" in params["q"]
        assert params["limit"] == 25

    def test_search_proceedings_with_all_convenience_params(
        self,
        mock_ptab_trials_client: PTABTrialsClient,
        trial_proceeding_sample: dict[str, Any],
    ) -> None:
        """Test search_proceedings with all convenience parameters."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = trial_proceeding_sample
        mock_session.get.return_value = mock_response
        mock_ptab_trials_client.session = mock_session

        # Test
        result = mock_ptab_trials_client.search_proceedings(
            trial_number_q="IPR2023-00001",
            patent_owner_name_q="Test Owner",
            petitioner_real_party_in_interest_name_q="Test Petitioner",
            respondent_name_q="Test Respondent",
            trial_type_code_q="IPR",
            trial_status_category_q="Instituted",
            petition_filing_date_from_q="2023-01-01",
            petition_filing_date_to_q="2023-12-31",
        )

        # Verify
        assert isinstance(result, PTABTrialProceedingResponse)
        call_args = mock_session.get.call_args
        params = call_args[1]["params"]
        assert 'patentOwnerData.patentOwnerName:"Test Owner"' in params["q"]
        assert (
            'regularPetitionerData.realPartyInInterestName:"Test Petitioner"'
            in params["q"]
        )
        assert 'respondentData.patentOwnerName:"Test Respondent"' in params["q"]
        assert 'trialMetaData.trialStatusCategory:"Instituted"' in params["q"]

    def test_search_proceedings_with_date_from_only(
        self,
        mock_ptab_trials_client: PTABTrialsClient,
        trial_proceeding_sample: dict[str, Any],
    ) -> None:
        """Test search_proceedings with only petition_filing_date_from."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = trial_proceeding_sample
        mock_session.get.return_value = mock_response
        mock_ptab_trials_client.session = mock_session

        # Test
        result = mock_ptab_trials_client.search_proceedings(
            petition_filing_date_from_q="2023-01-01"
        )

        # Verify
        assert isinstance(result, PTABTrialProceedingResponse)
        call_args = mock_session.get.call_args
        params = call_args[1]["params"]
        assert "petitionFilingDate:>=2023-01-01" in params["q"]

    def test_search_proceedings_with_date_to_only(
        self,
        mock_ptab_trials_client: PTABTrialsClient,
        trial_proceeding_sample: dict[str, Any],
    ) -> None:
        """Test search_proceedings with only petition_filing_date_to."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = trial_proceeding_sample
        mock_session.get.return_value = mock_response
        mock_ptab_trials_client.session = mock_session

        # Test
        result = mock_ptab_trials_client.search_proceedings(
            petition_filing_date_to_q="2023-12-31"
        )

        # Verify
        assert isinstance(result, PTABTrialProceedingResponse)
        call_args = mock_session.get.call_args
        params = call_args[1]["params"]
        assert "petitionFilingDate:<=2023-12-31" in params["q"]

    def test_search_proceedings_with_optional_params(
        self,
        mock_ptab_trials_client: PTABTrialsClient,
        trial_proceeding_sample: dict[str, Any],
    ) -> None:
        """Test search_proceedings with optional parameters."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = trial_proceeding_sample
        mock_session.get.return_value = mock_response
        mock_ptab_trials_client.session = mock_session

        # Test
        result = mock_ptab_trials_client.search_proceedings(
            query="trialNumber:IPR2023-00001",
            sort="petitionFilingDate desc",
            offset=10,
            limit=50,
            facets="trialTypeCode",
            fields="trialNumber,petitionFilingDate",
            filters="trialStatusCategory:Instituted",
            range_filters="petitionFilingDate:[2023-01-01 TO 2023-12-31]",
            additional_query_params={"customParam": "value"},
        )

        # Verify
        assert isinstance(result, PTABTrialProceedingResponse)
        call_args = mock_session.get.call_args
        params = call_args[1]["params"]
        assert params["sort"] == "petitionFilingDate desc"
        assert params["offset"] == 10
        assert params["limit"] == 50
        assert params["facets"] == "trialTypeCode"
        assert params["fields"] == "trialNumber,petitionFilingDate"
        assert params["filters"] == "trialStatusCategory:Instituted"
        assert params["rangeFilters"] == "petitionFilingDate:[2023-01-01 TO 2023-12-31]"
        assert params["customParam"] == "value"

    def test_search_proceedings_post_with_body(
        self,
        mock_ptab_trials_client: PTABTrialsClient,
        trial_proceeding_sample: dict[str, Any],
    ) -> None:
        """Test search_proceedings with POST body."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = trial_proceeding_sample
        mock_session.post.return_value = mock_response
        mock_ptab_trials_client.session = mock_session

        post_body = {"q": "trialTypeCode:IPR", "limit": 100}

        # Test
        result = mock_ptab_trials_client.search_proceedings(post_body=post_body)

        # Verify
        assert isinstance(result, PTABTrialProceedingResponse)
        mock_session.post.assert_called_once()
        call_args = mock_session.post.call_args
        assert call_args[1]["json"] == post_body


class TestPTABTrialsClientSearchDocuments:
    """Tests for search_documents method."""

    def test_search_documents_get_with_query(
        self,
        mock_ptab_trials_client: PTABTrialsClient,
        trial_document_sample: dict[str, Any],
    ) -> None:
        """Test search_documents with GET and direct query."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = trial_document_sample
        mock_session.get.return_value = mock_response
        mock_ptab_trials_client.session = mock_session

        # Test
        result = mock_ptab_trials_client.search_documents(
            query="trialNumber:IPR2023-00001", limit=10
        )

        # Verify
        assert isinstance(result, PTABTrialDocumentResponse)
        mock_session.get.assert_called_once()

    def test_search_documents_with_convenience_params(
        self,
        mock_ptab_trials_client: PTABTrialsClient,
        trial_document_sample: dict[str, Any],
    ) -> None:
        """Test search_documents with convenience parameters."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = trial_document_sample
        mock_session.get.return_value = mock_response
        mock_ptab_trials_client.session = mock_session

        # Test
        result = mock_ptab_trials_client.search_documents(
            trial_number_q="IPR2023-00001",
            document_category_q="Paper",
            filing_date_from_q="2023-01-01",
            filing_date_to_q="2023-12-31",
        )

        # Verify
        assert isinstance(result, PTABTrialDocumentResponse)
        call_args = mock_session.get.call_args
        params = call_args[1]["params"]
        assert "q" in params
        assert (
            "documentData.documentFilingDate:[2023-01-01 TO 2023-12-31]" in params["q"]
        )

    def test_search_documents_with_all_convenience_params(
        self,
        mock_ptab_trials_client: PTABTrialsClient,
        trial_document_sample: dict[str, Any],
    ) -> None:
        """Test search_documents with all convenience parameters."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = trial_document_sample
        mock_session.get.return_value = mock_response
        mock_ptab_trials_client.session = mock_session

        # Test
        result = mock_ptab_trials_client.search_documents(
            trial_number_q="IPR2023-00001",
            document_category_q="Paper",
            document_type_name_q="Patent Owner Response",
            filing_date_from_q="2023-01-01",
            filing_date_to_q="2023-12-31",
            petitioner_real_party_in_interest_name_q="Test Petitioner",
            inventor_name_q="Jane Inventor",
            real_party_in_interest_name_q="Real Party LLC",
            patent_number_q="US1234567",
            patent_owner_name_q="Test Owner",
            limit=50,
        )

        # Verify
        assert isinstance(result, PTABTrialDocumentResponse)
        call_args = mock_session.get.call_args
        params = call_args[1]["params"]
        assert "trialNumber:IPR2023-00001" in params["q"]
        assert 'documentData.documentCategory:"Paper"' in params["q"]
        assert (
            'documentData.documentTypeDescriptionText:"Patent Owner Response"'
            in params["q"]
        )
        assert (
            'regularPetitionerData.realPartyInInterestName:"Test Petitioner"'
            in params["q"]
        )
        assert 'patentOwnerData.inventorName:"Jane Inventor"' in params["q"]
        assert (
            'regularPetitionerData.realPartyInInterestName:"Real Party LLC"'
            in params["q"]
        )
        assert "patentOwnerData.patentNumber:US1234567" in params["q"]
        assert 'patentOwnerData.patentOwnerName:"Test Owner"' in params["q"]
        assert params["limit"] == 50

    def test_search_documents_with_date_from_only(
        self,
        mock_ptab_trials_client: PTABTrialsClient,
        trial_document_sample: dict[str, Any],
    ) -> None:
        """Test search_documents with only filing_date_from."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = trial_document_sample
        mock_session.get.return_value = mock_response
        mock_ptab_trials_client.session = mock_session

        # Test
        result = mock_ptab_trials_client.search_documents(
            filing_date_from_q="2023-01-01"
        )

        # Verify
        assert isinstance(result, PTABTrialDocumentResponse)
        call_args = mock_session.get.call_args
        params = call_args[1]["params"]
        assert "documentData.documentFilingDate:>=2023-01-01" in params["q"]

    def test_search_documents_with_date_to_only(
        self,
        mock_ptab_trials_client: PTABTrialsClient,
        trial_document_sample: dict[str, Any],
    ) -> None:
        """Test search_documents with only filing_date_to."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = trial_document_sample
        mock_session.get.return_value = mock_response
        mock_ptab_trials_client.session = mock_session

        # Test
        result = mock_ptab_trials_client.search_documents(filing_date_to_q="2023-12-31")

        # Verify
        assert isinstance(result, PTABTrialDocumentResponse)
        call_args = mock_session.get.call_args
        params = call_args[1]["params"]
        assert "documentData.documentFilingDate:<=2023-12-31" in params["q"]

    def test_search_documents_post_with_body(
        self,
        mock_ptab_trials_client: PTABTrialsClient,
        trial_document_sample: dict[str, Any],
    ) -> None:
        """Test search_documents with POST body."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = trial_document_sample
        mock_session.post.return_value = mock_response
        mock_ptab_trials_client.session = mock_session

        post_body = {"q": "documentCategory:Paper", "limit": 100}

        # Test
        result = mock_ptab_trials_client.search_documents(post_body=post_body)

        # Verify
        assert isinstance(result, PTABTrialDocumentResponse)
        mock_session.post.assert_called_once()
        call_args = mock_session.post.call_args
        assert call_args[1]["json"] == post_body

    def test_search_documents_with_optional_params(
        self,
        mock_ptab_trials_client: PTABTrialsClient,
        trial_document_sample: dict[str, Any],
    ) -> None:
        """Test search_documents with optional parameters."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = trial_document_sample
        mock_session.get.return_value = mock_response
        mock_ptab_trials_client.session = mock_session

        # Test
        result = mock_ptab_trials_client.search_documents(
            query="trialNumber:IPR2023-00001",
            sort="filingDate desc",
            offset=10,
            limit=50,
            facets="documentCategory",
            fields="trialNumber,filingDate",
            filters="documentCategory:Paper",
            range_filters="filingDate:[2023-01-01 TO 2023-12-31]",
            additional_query_params={"customParam": "value"},
        )

        # Verify
        assert isinstance(result, PTABTrialDocumentResponse)
        call_args = mock_session.get.call_args
        params = call_args[1]["params"]
        assert params["sort"] == "filingDate desc"
        assert params["offset"] == 10
        assert params["limit"] == 50
        assert params["facets"] == "documentCategory"
        assert params["fields"] == "trialNumber,filingDate"
        assert params["filters"] == "documentCategory:Paper"
        assert params["rangeFilters"] == "filingDate:[2023-01-01 TO 2023-12-31]"
        assert params["customParam"] == "value"


class TestPTABTrialsClientSearchDecisions:
    """Tests for search_decisions method."""

    def test_search_decisions_get_with_query(
        self,
        mock_ptab_trials_client: PTABTrialsClient,
        trial_document_sample: dict[str, Any],
    ) -> None:
        """Test search_decisions with GET and direct query."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = trial_document_sample
        mock_session.get.return_value = mock_response
        mock_ptab_trials_client.session = mock_session

        # Test
        result = mock_ptab_trials_client.search_decisions(
            query="trialNumber:IPR2023-00001", limit=10
        )

        # Verify
        assert isinstance(result, PTABTrialDocumentResponse)
        mock_session.get.assert_called_once()

    def test_search_decisions_with_convenience_params(
        self,
        mock_ptab_trials_client: PTABTrialsClient,
        trial_document_sample: dict[str, Any],
    ) -> None:
        """Test search_decisions with convenience parameters."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = trial_document_sample
        mock_session.get.return_value = mock_response
        mock_ptab_trials_client.session = mock_session

        # Test
        result = mock_ptab_trials_client.search_decisions(
            trial_number_q="IPR2023-00001",
            decision_type_category_q="Final Written Decision",
            decision_date_from_q="2023-01-01",
        )

        # Verify
        assert isinstance(result, PTABTrialDocumentResponse)
        call_args = mock_session.get.call_args
        params = call_args[1]["params"]
        assert "q" in params
        assert "decisionData.decisionIssueDate:>=2023-01-01" in params["q"]

    def test_search_decisions_with_all_convenience_params(
        self,
        mock_ptab_trials_client: PTABTrialsClient,
        trial_document_sample: dict[str, Any],
    ) -> None:
        """Test search_decisions with all convenience parameters."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = trial_document_sample
        mock_session.get.return_value = mock_response
        mock_ptab_trials_client.session = mock_session

        # Test
        result = mock_ptab_trials_client.search_decisions(
            trial_number_q="IPR2023-00001",
            decision_type_category_q="Final Written Decision",
            decision_date_from_q="2023-01-01",
            decision_date_to_q="2023-12-31",
            trial_type_code_q="IPR",
            patent_number_q="US1234567",
            application_number_q="15/123456",
            patent_owner_name_q="Test Owner",
            trial_status_category_q="Instituted",
            real_party_in_interest_name_q="Real Party LLC",
            document_category_q="Decision",
            limit=50,
        )

        # Verify
        assert isinstance(result, PTABTrialDocumentResponse)
        call_args = mock_session.get.call_args
        params = call_args[1]["params"]
        assert "trialNumber:IPR2023-00001" in params["q"]
        assert (
            'decisionData.decisionTypeCategory:"Final Written Decision"' in params["q"]
        )
        assert "trialTypeCode:IPR" in params["q"]
        assert "patentOwnerData.patentNumber:US1234567" in params["q"]
        assert "patentOwnerData.applicationNumberText:15/123456" in params["q"]
        assert 'patentOwnerData.patentOwnerName:"Test Owner"' in params["q"]
        assert 'trialMetaData.trialStatusCategory:"Instituted"' in params["q"]
        assert (
            'regularPetitionerData.realPartyInInterestName:"Real Party LLC"'
            in params["q"]
        )
        assert 'documentData.documentCategory:"Decision"' in params["q"]
        assert (
            "decisionData.decisionIssueDate:[2023-01-01 TO 2023-12-31]" in params["q"]
        )
        assert params["limit"] == 50

    def test_search_decisions_with_date_from_only(
        self,
        mock_ptab_trials_client: PTABTrialsClient,
        trial_document_sample: dict[str, Any],
    ) -> None:
        """Test search_decisions with only decision_date_from."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = trial_document_sample
        mock_session.get.return_value = mock_response
        mock_ptab_trials_client.session = mock_session

        # Test
        result = mock_ptab_trials_client.search_decisions(
            decision_date_from_q="2023-01-01"
        )

        # Verify
        assert isinstance(result, PTABTrialDocumentResponse)
        call_args = mock_session.get.call_args
        params = call_args[1]["params"]
        assert "decisionData.decisionIssueDate:>=2023-01-01" in params["q"]

    def test_search_decisions_with_date_to_only(
        self,
        mock_ptab_trials_client: PTABTrialsClient,
        trial_document_sample: dict[str, Any],
    ) -> None:
        """Test search_decisions with only decision_date_to."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = trial_document_sample
        mock_session.get.return_value = mock_response
        mock_ptab_trials_client.session = mock_session

        # Test
        result = mock_ptab_trials_client.search_decisions(
            decision_date_to_q="2023-12-31"
        )

        # Verify
        assert isinstance(result, PTABTrialDocumentResponse)
        call_args = mock_session.get.call_args
        params = call_args[1]["params"]
        assert "decisionData.decisionIssueDate:<=2023-12-31" in params["q"]

    def test_search_decisions_with_document_type_description_q(
        self,
        mock_ptab_trials_client: PTABTrialsClient,
        trial_document_sample: dict[str, Any],
    ) -> None:
        """Test search_decisions with document_type_description_q parameter."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = trial_document_sample
        mock_session.get.return_value = mock_response
        mock_ptab_trials_client.session = mock_session

        # Test
        result = mock_ptab_trials_client.search_decisions(
            document_type_description_q="Final Written Decision"
        )

        # Verify
        assert isinstance(result, PTABTrialDocumentResponse)
        call_args = mock_session.get.call_args
        params = call_args[1]["params"]
        assert (
            'documentData.documentTypeDescriptionText:"*Final Written Decision*"'
            in params["q"]
        )

    def test_search_decisions_post_with_body(
        self,
        mock_ptab_trials_client: PTABTrialsClient,
        trial_document_sample: dict[str, Any],
    ) -> None:
        """Test search_decisions with POST body."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = trial_document_sample
        mock_session.post.return_value = mock_response
        mock_ptab_trials_client.session = mock_session

        post_body = {"q": "decisionTypeCategory:Final Written Decision", "limit": 100}

        # Test
        result = mock_ptab_trials_client.search_decisions(post_body=post_body)

        # Verify
        assert isinstance(result, PTABTrialDocumentResponse)
        mock_session.post.assert_called_once()
        call_args = mock_session.post.call_args
        assert call_args[1]["json"] == post_body

    def test_search_decisions_with_optional_params(
        self,
        mock_ptab_trials_client: PTABTrialsClient,
        trial_document_sample: dict[str, Any],
    ) -> None:
        """Test search_decisions with optional parameters."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = trial_document_sample
        mock_session.get.return_value = mock_response
        mock_ptab_trials_client.session = mock_session

        # Test
        result = mock_ptab_trials_client.search_decisions(
            query="trialNumber:IPR2023-00001",
            sort="decisionDate desc",
            offset=10,
            limit=50,
            facets="decisionTypeCategory",
            fields="trialNumber,decisionDate",
            filters="decisionTypeCategory:Final Written Decision",
            range_filters="decisionDate:[2023-01-01 TO 2023-12-31]",
            additional_query_params={"customParam": "value"},
        )

        # Verify
        assert isinstance(result, PTABTrialDocumentResponse)
        call_args = mock_session.get.call_args
        params = call_args[1]["params"]
        assert params["sort"] == "decisionDate desc"
        assert params["offset"] == 10
        assert params["limit"] == 50
        assert params["facets"] == "decisionTypeCategory"
        assert params["fields"] == "trialNumber,decisionDate"
        assert params["filters"] == "decisionTypeCategory:Final Written Decision"
        assert params["rangeFilters"] == "decisionDate:[2023-01-01 TO 2023-12-31]"
        assert params["customParam"] == "value"


class TestPTABTrialsClientPaginate:
    """Tests for paginate_proceedings method."""

    def test_paginate_proceedings(
        self, mock_ptab_trials_client: PTABTrialsClient
    ) -> None:
        """Test paginate_proceedings method."""
        # Setup mock responses
        first_response = PTABTrialProceedingResponse.from_dict(
            {
                "count": 2,
                "requestIdentifier": "req-1",
                "patentTrialProceedingDataBag": [
                    {"trialNumber": "IPR2023-00001"},
                    {"trialNumber": "IPR2023-00002"},
                ],
            }
        )

        second_response = PTABTrialProceedingResponse.from_dict(
            {
                "count": 1,
                "requestIdentifier": "req-2",
                "patentTrialProceedingDataBag": [
                    {"trialNumber": "IPR2023-00003"},
                ],
            }
        )

        third_response = PTABTrialProceedingResponse.from_dict(
            {
                "count": 0,
                "requestIdentifier": "req-3",
                "patentTrialProceedingDataBag": [],
            }
        )

        # Mock search_proceedings to return different responses
        with patch.object(mock_ptab_trials_client, "search_proceedings") as mock_search:
            mock_search.side_effect = [first_response, second_response, third_response]

            # Test
            results = list(
                mock_ptab_trials_client.paginate_proceedings(
                    trial_type_code_q="IPR", limit=2
                )
            )

            # Verify
            assert len(results) == 3
            assert results[0].trial_number == "IPR2023-00001"
            assert results[1].trial_number == "IPR2023-00002"
            assert results[2].trial_number == "IPR2023-00003"
            assert mock_search.call_count == 2  # Stops when count < limit

    def test_paginate_proceedings_rejects_offset_in_kwargs(
        self, mock_ptab_trials_client: PTABTrialsClient
    ) -> None:
        """Test that paginate_proceedings raises ValueError with offset in kwargs."""
        with pytest.raises(ValueError, match="Cannot specify 'offset'"):
            list(mock_ptab_trials_client.paginate_proceedings(query="test", offset=10))


class TestPTABTrialsDownloadMethods:
    """Tests for PTAB Trials download methods."""

    def test_download_trial_archive_missing_uri_raises_error(self) -> None:
        """Test download_trial_archive raises ValueError when file_download_uri is None."""
        from pyUSPTO.models.ptab import TrialMetaData

        client = PTABTrialsClient(api_key="test")

        # Create TrialMetaData without file_download_uri
        meta_data = TrialMetaData(file_download_uri=None)

        with pytest.raises(ValueError, match="TrialMetaData has no file_download_uri"):
            client.download_trial_archive(meta_data)

    def test_download_trial_archive_with_uri(self) -> None:
        """Test download_trial_archive calls _download_file with URI."""
        from unittest.mock import patch

        from pyUSPTO.models.ptab import TrialMetaData

        client = PTABTrialsClient(api_key="test")
        meta_data = TrialMetaData(file_download_uri="https://test.com/trial.tar")

        with patch.object(client, "_download_file", return_value="/path/to/file") as mock_download:
            result = client.download_trial_archive(meta_data, destination="/dest", file_name="custom.tar", overwrite=True)
            mock_download.assert_called_once_with(
                url="https://test.com/trial.tar",
                destination="/dest",
                file_name="custom.tar",
                overwrite=True
            )
            assert result == "/path/to/file"

    def test_download_trial_documents_missing_uri_raises_error(self) -> None:
        """Test download_trial_documents raises ValueError when file_download_uri is None."""
        from pyUSPTO.models.ptab import TrialMetaData

        client = PTABTrialsClient(api_key="test")

        # Create TrialMetaData without file_download_uri
        meta_data = TrialMetaData(file_download_uri=None)

        with pytest.raises(ValueError, match="TrialMetaData has no file_download_uri"):
            client.download_trial_documents(meta_data)

    def test_download_trial_documents_with_uri(self) -> None:
        """Test download_trial_documents calls _download_and_extract with URI."""
        from unittest.mock import patch

        from pyUSPTO.models.ptab import TrialMetaData

        client = PTABTrialsClient(api_key="test")
        meta_data = TrialMetaData(file_download_uri="https://test.com/trial.tar")

        with patch.object(client, "_download_and_extract", return_value="/path/to/extracted") as mock_extract:
            result = client.download_trial_documents(meta_data, destination="/dest", overwrite=True)
            mock_extract.assert_called_once_with(
                url="https://test.com/trial.tar",
                destination="/dest",
                overwrite=True
            )
            assert result == "/path/to/extracted"

    def test_download_trial_document_missing_uri_raises_error(self) -> None:
        """Test download_trial_document raises ValueError when file_download_uri is None."""
        from pyUSPTO.models.ptab import TrialDocumentData

        client = PTABTrialsClient(api_key="test")

        # Create TrialDocumentData without file_download_uri
        document_data = TrialDocumentData(file_download_uri=None)

        with pytest.raises(ValueError, match="TrialDocumentData has no file_download_uri"):
            client.download_trial_document(document_data)

    def test_download_trial_document_with_uri(self) -> None:
        """Test download_trial_document calls _download_and_extract with URI."""
        from unittest.mock import patch

        from pyUSPTO.models.ptab import TrialDocumentData

        client = PTABTrialsClient(api_key="test")
        document_data = TrialDocumentData(file_download_uri="https://test.com/doc.pdf")

        with patch.object(client, "_download_and_extract", return_value="/path/to/doc.pdf") as mock_extract:
            result = client.download_trial_document(document_data, destination="/dest", file_name="doc.pdf", overwrite=True)
            mock_extract.assert_called_once_with(
                url="https://test.com/doc.pdf",
                destination="/dest",
                file_name="doc.pdf",
                overwrite=True
            )
            assert result == "/path/to/doc.pdf"
