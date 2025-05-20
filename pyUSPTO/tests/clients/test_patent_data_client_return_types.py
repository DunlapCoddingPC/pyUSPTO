"""
Tests specifically for the updated return types in the PatentDataClient.

This module tests the return types that were updated in the PatentDataClient
to provide more specific data models rather than returning the entire wrapper.
"""

from unittest.mock import Mock, patch

import pytest

from pyUSPTO.clients.patent_data import PatentDataClient
from pyUSPTO.models.patent_data import (
    ApplicationContinuityData,
    ApplicationMetaData,
    Assignment,
    AssociatedDocumentsData,
    ChildContinuity,
    DocumentMetaData,
    EventData,
    ForeignPriority,
    ParentContinuity,
    PatentDataResponse,
    PatentFileWrapper,
    PatentTermAdjustmentData,
    RecordAttorney,
)


@pytest.fixture
def mock_wrapper():
    """Create a mock PatentFileWrapper with all relevant data."""
    # Create mock data for the wrapper
    app_meta = Mock(spec=ApplicationMetaData)
    assignments = [Mock(spec=Assignment)]
    record_attorney = Mock(spec=RecordAttorney)
    foreign_priorities = [Mock(spec=ForeignPriority)]
    parent_continuities = [Mock(spec=ParentContinuity)]
    child_continuities = [Mock(spec=ChildContinuity)]
    pta_data = Mock(spec=PatentTermAdjustmentData)
    events = [Mock(spec=EventData)]
    pgpub_meta = Mock(spec=DocumentMetaData)
    grant_meta = Mock(spec=DocumentMetaData)

    # Create the wrapper with mock data
    wrapper = Mock(spec=PatentFileWrapper)
    wrapper.application_number_text = "12345678"
    wrapper.application_meta_data = app_meta
    wrapper.assignment_bag = assignments
    wrapper.record_attorney = record_attorney
    wrapper.foreign_priority_bag = foreign_priorities
    wrapper.parent_continuity_bag = parent_continuities
    wrapper.child_continuity_bag = child_continuities
    wrapper.patent_term_adjustment_data = pta_data
    wrapper.event_data_bag = events
    wrapper.pgpub_document_meta_data = pgpub_meta
    wrapper.grant_document_meta_data = grant_meta

    return wrapper


@pytest.fixture
def mock_client(mock_wrapper):
    """Create a mock PatentDataClient with a preset response."""
    # Create a mock response with our wrapper
    response = Mock(spec=PatentDataResponse)
    response.patent_file_wrapper_data_bag = [mock_wrapper]
    response.count = 1

    # Create a patched client that returns our mock response
    with patch(
        "pyUSPTO.clients.patent_data.PatentDataClient._make_request"
    ) as mock_make_request:
        mock_make_request.return_value = response
        client = PatentDataClient(api_key="test_key")
        yield client


class TestPatentDataClientReturnTypes:
    """Tests for the updated return types in the PatentDataClient."""

    def test_get_application_metadata(self, mock_client, mock_wrapper):
        """Test get_application_metadata returns ApplicationMetaData."""
        result = mock_client.get_application_metadata("12345678")
        assert result is mock_wrapper.application_meta_data
        assert isinstance(result, Mock)  # It's a Mock that specs ApplicationMetaData

    def test_get_application_adjustment(self, mock_client, mock_wrapper):
        """Test get_application_adjustment returns PatentTermAdjustmentData."""
        result = mock_client.get_application_adjustment("12345678")
        assert result is mock_wrapper.patent_term_adjustment_data
        assert isinstance(
            result, Mock
        )  # It's a Mock that specs PatentTermAdjustmentData

    def test_get_application_assignment(self, mock_client, mock_wrapper):
        """Test get_application_assignment returns List[Assignment]."""
        result = mock_client.get_application_assignment("12345678")
        assert result is mock_wrapper.assignment_bag
        assert isinstance(result, list)

    def test_get_application_attorney(self, mock_client, mock_wrapper):
        """Test get_application_attorney returns RecordAttorney."""
        result = mock_client.get_application_attorney("12345678")
        assert result is mock_wrapper.record_attorney
        assert isinstance(result, Mock)  # It's a Mock that specs RecordAttorney

    def test_get_application_continuity(self, mock_client, mock_wrapper):
        """Test get_application_continuity returns ApplicationContinuityData."""
        result = mock_client.get_application_continuity("12345678")
        # This should create a new ApplicationContinuityData from the mock_wrapper
        assert isinstance(result, ApplicationContinuityData)
        assert result.parent_continuity_bag is mock_wrapper.parent_continuity_bag
        assert result.child_continuity_bag is mock_wrapper.child_continuity_bag

    def test_get_application_foreign_priority(self, mock_client, mock_wrapper):
        """Test get_application_foreign_priority returns List[ForeignPriority]."""
        result = mock_client.get_application_foreign_priority("12345678")
        assert result is mock_wrapper.foreign_priority_bag
        assert isinstance(result, list)

    def test_get_application_transactions(self, mock_client, mock_wrapper):
        """Test get_application_transactions returns List[EventData]."""
        result = mock_client.get_application_transactions("12345678")
        assert result is mock_wrapper.event_data_bag
        assert isinstance(result, list)

    def test_get_application_associated_documents(self, mock_client, mock_wrapper):
        """Test get_application_associated_documents returns AssociatedDocumentsData."""
        result = mock_client.get_application_associated_documents("12345678")
        # This should create a new AssociatedDocumentsData from the mock_wrapper
        assert isinstance(result, AssociatedDocumentsData)
        assert result.pgpub_document_meta_data is mock_wrapper.pgpub_document_meta_data
        assert result.grant_document_meta_data is mock_wrapper.grant_document_meta_data


class TestEdgeCases:
    """Test edge cases for the updated return types."""

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_empty_response(self, mock_make_request):
        """Test behavior when response is empty."""
        # Create empty response
        empty_response = Mock(spec=PatentDataResponse)
        empty_response.patent_file_wrapper_data_bag = []
        empty_response.count = 0
        mock_make_request.return_value = empty_response

        client = PatentDataClient(api_key="test_key")

        # Test each method with empty response
        assert client.get_application_metadata("12345678") is None
        assert client.get_application_adjustment("12345678") is None
        assert client.get_application_assignment("12345678") is None
        assert client.get_application_attorney("12345678") is None
        assert client.get_application_continuity("12345678") is None
        assert client.get_application_foreign_priority("12345678") is None
        assert client.get_application_transactions("12345678") is None
        assert client.get_application_associated_documents("12345678") is None

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_missing_fields(self, mock_make_request):
        """Test behavior when wrapper exists but fields are None."""
        # Create wrapper with missing fields
        wrapper = Mock(spec=PatentFileWrapper)
        wrapper.application_number_text = "12345678"
        wrapper.application_meta_data = None
        wrapper.assignment_bag = []
        wrapper.record_attorney = None
        wrapper.foreign_priority_bag = []
        wrapper.parent_continuity_bag = []
        wrapper.child_continuity_bag = []
        wrapper.patent_term_adjustment_data = None
        wrapper.event_data_bag = []
        wrapper.pgpub_document_meta_data = None
        wrapper.grant_document_meta_data = None

        # Create response with wrapper
        response = Mock(spec=PatentDataResponse)
        response.patent_file_wrapper_data_bag = [wrapper]
        response.count = 1
        mock_make_request.return_value = response

        client = PatentDataClient(api_key="test_key")

        # Test each method when fields are None or empty
        assert client.get_application_metadata("12345678") is None
        assert client.get_application_adjustment("12345678") is None
        assert client.get_application_assignment("12345678") == []
        assert client.get_application_attorney("12345678") is None

        # For these, we expect actual objects, but with empty bags
        continuity_result = client.get_application_continuity("12345678")
        assert isinstance(continuity_result, ApplicationContinuityData)
        assert continuity_result.parent_continuity_bag == []
        assert continuity_result.child_continuity_bag == []

        assert client.get_application_foreign_priority("12345678") == []
        assert client.get_application_transactions("12345678") == []

        assoc_docs_result = client.get_application_associated_documents("12345678")
        assert isinstance(assoc_docs_result, AssociatedDocumentsData)
        assert assoc_docs_result.pgpub_document_meta_data is None
        assert assoc_docs_result.grant_document_meta_data is None
