"""Tests for PTABAppealsClient.

This module contains unit tests for the PTABAppealsClient class.
"""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from pyUSPTO import PTABAppealsClient, USPTOConfig
from pyUSPTO.models.ptab import PTABAppealResponse


@pytest.fixture
def api_key_fixture() -> str:
    """Fixture for test API key."""
    return "test_key"


@pytest.fixture
def appeal_decision_sample() -> dict[str, Any]:
    """Sample appeal decision data for testing."""
    return {
        "count": 2,
        "requestIdentifier": "req-123",
        "patentAppealDataBag": [
            {
                "appealNumber": "2023-001234",
                "appealRecordIdentifier": "appeal-uuid-1",
                "lastModifiedDateTime": "2023-06-15T10:30:00Z",
                "appealMetaData": {
                    "applicationNumberText": "15/123456",
                    "technologyCenterNumber": "3600",
                },
                "decisionData": {
                    "decisionTypeCategory": "Affirmed",
                    "decisionDate": "2023-06-01",
                },
            },
            {
                "appealNumber": "2023-001235",
                "appealRecordIdentifier": "appeal-uuid-2",
                "lastModifiedDateTime": "2023-06-20T14:00:00Z",
                "appealMetaData": {
                    "applicationNumberText": "16/789012",
                    "technologyCenterNumber": "2100",
                },
                "decisionData": {
                    "decisionTypeCategory": "Reversed",
                    "decisionDate": "2023-06-10",
                },
            },
        ],
    }


@pytest.fixture
def mock_ptab_appeals_client(api_key_fixture: str) -> PTABAppealsClient:
    """Fixture for mock PTABAppealsClient."""
    return PTABAppealsClient(api_key=api_key_fixture)


class TestPTABAppealsClientInit:
    """Tests for initialization of PTABAppealsClient."""

    def test_init_with_api_key(self, api_key_fixture: str) -> None:
        """Test initialization with API key."""
        client = PTABAppealsClient(api_key=api_key_fixture)
        assert client._api_key == api_key_fixture
        assert client.base_url == "https://api.uspto.gov"

    def test_init_with_custom_base_url(self, api_key_fixture: str) -> None:
        """Test initialization with custom base URL."""
        custom_url = "https://custom.api.test.com"
        client = PTABAppealsClient(api_key=api_key_fixture, base_url=custom_url)
        assert client._api_key == api_key_fixture
        assert client.base_url == custom_url

    def test_init_with_config(self) -> None:
        """Test initialization with config object."""
        config_key = "config_key"
        config_url = "https://config.api.test.com"
        config = USPTOConfig(api_key=config_key, ptab_base_url=config_url)
        client = PTABAppealsClient(config=config)
        assert client._api_key == config_key
        assert client.base_url == config_url
        assert client.config is config

    def test_init_with_api_key_and_config(self, api_key_fixture: str) -> None:
        """Test initialization with both API key and config."""
        config = USPTOConfig(
            api_key="config_key",
            ptab_base_url="https://config.api.test.com",
        )
        client = PTABAppealsClient(api_key=api_key_fixture, config=config)
        # API key parameter takes precedence
        assert client._api_key == api_key_fixture
        # But base_url comes from config
        assert client.base_url == "https://config.api.test.com"


class TestPTABAppealsClientSearchDecisions:
    """Tests for search_decisions method."""

    def test_search_decisions_get_with_query(
        self,
        mock_ptab_appeals_client: PTABAppealsClient,
        appeal_decision_sample: dict[str, Any],
    ) -> None:
        """Test search_decisions with GET and direct query."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = appeal_decision_sample
        mock_session.get.return_value = mock_response
        mock_ptab_appeals_client.session = mock_session

        # Test
        result = mock_ptab_appeals_client.search_decisions(
            query="appealNumber:2024518758", limit=10
        )

        # Verify
        assert isinstance(result, PTABAppealResponse)
        assert result.count == 2
        assert len(result.patent_appeal_data_bag) == 2
        mock_session.get.assert_called_once()
        call_args = mock_session.get.call_args
        assert "q" in call_args[1]["params"]
        assert call_args[1]["params"]["q"] == "appealNumber:2024518758"

    def test_search_decisions_get_with_convenience_params(
        self,
        mock_ptab_appeals_client: PTABAppealsClient,
        appeal_decision_sample: dict[str, Any],
    ) -> None:
        """Test search_decisions with convenience parameters."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = appeal_decision_sample
        mock_session.get.return_value = mock_response
        mock_ptab_appeals_client.session = mock_session

        # Test
        result = mock_ptab_appeals_client.search_decisions(
            additional_query_params={"appealNumber": "2015000194"},
            technology_center_number_q="3600",
            decision_type_category_q="Affirmed",
            decision_date_from_q="2023-01-01",
            decision_date_to_q="2023-12-31",
            limit=25,
        )

        # Verify
        assert isinstance(result, PTABAppealResponse)
        mock_session.get.assert_called_once()
        call_args = mock_session.get.call_args
        params = call_args[1]["params"]
        assert "q" in params
        assert "2015000194" in params["appealNumber"]
        assert "technologyCenterNumber:3600" in params["q"]
        assert "decisionTypeCategory:Affirmed" in params["q"]
        assert (
            "decisionData.decisionIssueDate:[2023-01-01 TO 2023-12-31]" in params["q"]
        )
        assert params["limit"] == 25

    def test_search_decisions_get_with_date_from_only(
        self,
        mock_ptab_appeals_client: PTABAppealsClient,
        appeal_decision_sample: dict[str, Any],
    ) -> None:
        """Test search_decisions with only date_from parameter."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = appeal_decision_sample
        mock_session.get.return_value = mock_response
        mock_ptab_appeals_client.session = mock_session

        # Test
        result = mock_ptab_appeals_client.search_decisions(
            decision_date_from_q="2023-01-01"
        )

        # Verify
        assert isinstance(result, PTABAppealResponse)
        call_args = mock_session.get.call_args
        params = call_args[1]["params"]
        assert "decisionData.decisionIssueDate:>=2023-01-01" in params["q"]

    def test_search_decisions_get_with_date_to_only(
        self,
        mock_ptab_appeals_client: PTABAppealsClient,
        appeal_decision_sample: dict[str, Any],
    ) -> None:
        """Test search_decisions with only date_to parameter."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = appeal_decision_sample
        mock_session.get.return_value = mock_response
        mock_ptab_appeals_client.session = mock_session

        # Test
        result = mock_ptab_appeals_client.search_decisions(
            decision_date_to_q="2023-12-31"
        )

        # Verify
        assert isinstance(result, PTABAppealResponse)
        call_args = mock_session.get.call_args
        params = call_args[1]["params"]
        assert "decisionData.decisionIssueDate:<=2023-12-31" in params["q"]

    def test_search_decisions_get_with_all_convenience_params(
        self,
        mock_ptab_appeals_client: PTABAppealsClient,
        appeal_decision_sample: dict[str, Any],
    ) -> None:
        """Test search_decisions with all convenience parameters."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = appeal_decision_sample
        mock_session.get.return_value = mock_response
        mock_ptab_appeals_client.session = mock_session

        # Test
        result = mock_ptab_appeals_client.search_decisions(
            appeal_number_q="2023-001234",
            application_number_text_q="15/123456",
            appellant_name_q="Test Appellant",
            requestor_name_q="Test Requestor",
            decision_type_category_q="Affirmed",
            technology_center_number_q="3600",
            decision_date_from_q="2023-01-01",
            decision_date_to_q="2023-12-31",
        )

        # Verify
        assert isinstance(result, PTABAppealResponse)
        call_args = mock_session.get.call_args
        params = call_args[1]["params"]
        assert "appealNumber:2023-001234" in params["q"]
        assert "applicationNumberText:15/123456" in params["q"]
        assert "appellantData.realPartyInInterestName:Test Appellant" in params["q"]
        assert "appellantData.counselName:Test Requestor" in params["q"]
        assert "decisionTypeCategory:Affirmed" in params["q"]
        assert "technologyCenterNumber:3600" in params["q"]

    def test_search_decisions_post_with_body(
        self,
        mock_ptab_appeals_client: PTABAppealsClient,
        appeal_decision_sample: dict[str, Any],
    ) -> None:
        """Test search_decisions with POST body."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = appeal_decision_sample
        mock_session.post.return_value = mock_response
        mock_ptab_appeals_client.session = mock_session

        post_body = {"q": "technologyCenterNumber:3600", "limit": 100}

        # Test
        result = mock_ptab_appeals_client.search_decisions(post_body=post_body)

        # Verify
        assert isinstance(result, PTABAppealResponse)
        mock_session.post.assert_called_once()
        call_args = mock_session.post.call_args
        assert call_args[1]["json"] == post_body

    def test_search_decisions_with_optional_params(
        self,
        mock_ptab_appeals_client: PTABAppealsClient,
        appeal_decision_sample: dict[str, Any],
    ) -> None:
        """Test search_decisions with optional parameters like sort, facets, etc."""
        # Setup
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = appeal_decision_sample
        mock_session.get.return_value = mock_response
        mock_ptab_appeals_client.session = mock_session

        # Test
        result = mock_ptab_appeals_client.search_decisions(
            query="appealNumber:2023-001234",
            sort="decisionDate desc",
            offset=10,
            limit=50,
            facets="technologyCenterNumber",
            fields="appealNumber,decisionDate",
            filters="decisionTypeCategory:Affirmed",
            range_filters="decisionData.decisionIssueDate:[2023-01-01 TO 2023-12-31]",
        )

        # Verify
        assert isinstance(result, PTABAppealResponse)
        call_args = mock_session.get.call_args
        params = call_args[1]["params"]
        assert params["sort"] == "decisionDate desc"
        assert params["offset"] == 10
        assert params["limit"] == 50
        assert params["facets"] == "technologyCenterNumber"
        assert params["fields"] == "appealNumber,decisionDate"
        assert params["filters"] == "decisionTypeCategory:Affirmed"
        assert (
            params["rangeFilters"]
            == "decisionData.decisionIssueDate:[2023-01-01 TO 2023-12-31]"
        )


class TestPTABAppealsClientPaginate:
    """Tests for paginate_decisions method."""

    def test_paginate_decisions(
        self, mock_ptab_appeals_client: PTABAppealsClient
    ) -> None:
        """Test paginate_decisions method."""
        # Setup mock responses
        first_response = PTABAppealResponse.from_dict(
            {
                "count": 2,
                "requestIdentifier": "req-1",
                "patentAppealDataBag": [
                    {"appealNumber": "2023-001234"},
                    {"appealNumber": "2023-001235"},
                ],
            }
        )

        second_response = PTABAppealResponse.from_dict(
            {
                "count": 1,
                "requestIdentifier": "req-2",
                "patentAppealDataBag": [
                    {"appealNumber": "2023-001236"},
                ],
            }
        )

        third_response = PTABAppealResponse.from_dict(
            {
                "count": 0,
                "requestIdentifier": "req-3",
                "patentAppealDataBag": [],
            }
        )

        # Mock search_decisions to return different responses
        with patch.object(mock_ptab_appeals_client, "search_decisions") as mock_search:
            mock_search.side_effect = [first_response, second_response, third_response]

            # Test
            results = list(
                mock_ptab_appeals_client.paginate_decisions(
                    technology_center_number_q="3600", limit=2
                )
            )

            # Verify
            assert len(results) == 3
            assert results[0].appeal_number == "2023-001234"
            assert results[1].appeal_number == "2023-001235"
            assert results[2].appeal_number == "2023-001236"
            assert mock_search.call_count == 2  # Stops when count < limit

    def test_paginate_decisions_rejects_offset_in_kwargs(
        self, mock_ptab_appeals_client: PTABAppealsClient
    ) -> None:
        """Test that paginate_decisions raises ValueError with offset in kwargs."""
        with pytest.raises(ValueError, match="Cannot specify 'offset'"):
            list(mock_ptab_appeals_client.paginate_decisions(query="test", offset=10))

    def test_paginate_decisions_with_multiple_params(
        self, mock_ptab_appeals_client: PTABAppealsClient
    ) -> None:
        """Test paginate_decisions with multiple search parameters."""
        # Setup mock responses
        first_response = PTABAppealResponse.from_dict(
            {
                "count": 2,
                "requestIdentifier": "req-1",
                "patentAppealDataBag": [
                    {"appealNumber": "2023-001234"},
                    {"appealNumber": "2023-001235"},
                ],
            }
        )

        second_response = PTABAppealResponse.from_dict(
            {
                "count": 0,
                "requestIdentifier": "req-2",
                "patentAppealDataBag": [],
            }
        )

        with patch.object(mock_ptab_appeals_client, "search_decisions") as mock_search:
            mock_search.side_effect = [first_response, second_response]

            # Test
            results = list(
                mock_ptab_appeals_client.paginate_decisions(
                    technology_center_number_q="3600",
                    decision_type_category_q="Affirmed",
                    decision_date_from_q="2023-01-01",
                    limit=2,
                )
            )

            # Verify
            assert len(results) == 2
            # Verify that search_decisions was called with correct params
            call_args = mock_search.call_args_list[0]
            assert call_args[1]["technology_center_number_q"] == "3600"
            assert call_args[1]["decision_type_category_q"] == "Affirmed"
            assert call_args[1]["decision_date_from_q"] == "2023-01-01"


class TestPTABAppealsDownloadMethods:
    """Tests for PTAB Appeals download methods."""

    def test_download_appeal_archive_missing_uri_raises_error(self) -> None:
        """Test download_appeal_archive raises ValueError when file_download_uri is None."""
        from pyUSPTO.models.ptab import AppealMetaData

        client = PTABAppealsClient(api_key="test")

        # Create AppealMetaData without file_download_uri
        meta_data = AppealMetaData(file_download_uri=None)

        with pytest.raises(ValueError, match="AppealMetaData has no file_download_uri"):
            client.download_appeal_archive(meta_data)

    def test_download_appeal_archive_with_uri(self) -> None:
        """Test download_appeal_archive calls _download_file with URI."""
        from pyUSPTO.models.ptab import AppealMetaData
        from unittest.mock import patch

        client = PTABAppealsClient(api_key="test")
        meta_data = AppealMetaData(file_download_uri="https://test.com/appeal.tar")

        with patch.object(client, "_download_file", return_value="/path/to/file") as mock_download:
            result = client.download_appeal_archive(meta_data, destination="/dest", file_name="custom.tar", overwrite=True)
            mock_download.assert_called_once_with(
                url="https://test.com/appeal.tar",
                destination="/dest",
                file_name="custom.tar",
                overwrite=True
            )
            assert result == "/path/to/file"

    def test_download_appeal_documents_missing_uri_raises_error(self) -> None:
        """Test download_appeal_documents raises ValueError when file_download_uri is None."""
        from pyUSPTO.models.ptab import AppealMetaData

        client = PTABAppealsClient(api_key="test")

        # Create AppealMetaData without file_download_uri
        meta_data = AppealMetaData(file_download_uri=None)

        with pytest.raises(ValueError, match="AppealMetaData has no file_download_uri"):
            client.download_appeal_documents(meta_data)

    def test_download_appeal_documents_with_uri(self) -> None:
        """Test download_appeal_documents calls _download_and_extract with URI."""
        from pyUSPTO.models.ptab import AppealMetaData
        from unittest.mock import patch

        client = PTABAppealsClient(api_key="test")
        meta_data = AppealMetaData(file_download_uri="https://test.com/appeal.tar")

        with patch.object(client, "_download_and_extract", return_value="/path/to/extracted") as mock_extract:
            result = client.download_appeal_documents(meta_data, destination="/dest", overwrite=True)
            mock_extract.assert_called_once_with(
                url="https://test.com/appeal.tar",
                destination="/dest",
                overwrite=True
            )
            assert result == "/path/to/extracted"

    def test_download_appeal_document_missing_uri_raises_error(self) -> None:
        """Test download_appeal_document raises ValueError when file_download_uri is None."""
        from pyUSPTO.models.ptab import AppealDocumentData

        client = PTABAppealsClient(api_key="test")

        # Create AppealDocumentData without file_download_uri
        document_data = AppealDocumentData(file_download_uri=None)

        with pytest.raises(ValueError, match="AppealDocumentData has no file_download_uri"):
            client.download_appeal_document(document_data)

    def test_download_appeal_document_with_uri(self) -> None:
        """Test download_appeal_document calls _download_and_extract with URI."""
        from pyUSPTO.models.ptab import AppealDocumentData
        from unittest.mock import patch

        client = PTABAppealsClient(api_key="test")
        document_data = AppealDocumentData(file_download_uri="https://test.com/doc.pdf")

        with patch.object(client, "_download_and_extract", return_value="/path/to/doc.pdf") as mock_extract:
            result = client.download_appeal_document(document_data, destination="/dest", file_name="doc.pdf", overwrite=True)
            mock_extract.assert_called_once_with(
                url="https://test.com/doc.pdf",
                destination="/dest",
                file_name="doc.pdf",
                overwrite=True
            )
            assert result == "/path/to/doc.pdf"
