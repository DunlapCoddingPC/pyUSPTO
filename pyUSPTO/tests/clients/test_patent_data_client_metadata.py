"""
Tests for the metadata and status-related methods of the patent_data client module.

This module contains tests for metadata retrieval, status code handling, and other
auxiliary data methods in the PatentDataClient class.
"""

from datetime import date, datetime, timezone
from unittest.mock import MagicMock, patch

import pytest  # Import pytest if not already for potential raises

from pyUSPTO.clients.patent_data import PatentDataClient

# Import all necessary model classes
from pyUSPTO.models.patent_data import Attorney  # For constructing RecordAttorney
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


class TestApplicationMetadata:
    """Tests for application metadata methods."""

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_metadata(self, mock_make_request: MagicMock) -> None:
        """Test get_application_metadata method."""
        app_num = "12345678"
        metadata = ApplicationMetaData(invention_title="Test Invention")
        # Ensure the mock_wrapper has application_number_text and is a PatentFileWrapper instance
        wrapper = PatentFileWrapper(
            application_number_text=app_num,
            application_meta_data=metadata,
        )
        mock_response = PatentDataResponse(
            count=1, patent_file_wrapper_data_bag=[wrapper]
        )
        mock_make_request.return_value = mock_response

        client = PatentDataClient(api_key="test_key")
        result = client.get_application_metadata(application_number=app_num)

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint=f"api/v1/patent/applications/{app_num}/meta-data",
            response_class=PatentDataResponse,
        )
        assert isinstance(result, ApplicationMetaData)
        assert result.invention_title == "Test Invention"

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_adjustment(self, mock_make_request: MagicMock) -> None:
        """Test get_application_adjustment method."""
        app_num = "12345678"
        adjustment_data = PatentTermAdjustmentData(adjustment_total_quantity=150.0)
        wrapper = PatentFileWrapper(
            application_number_text=app_num,
            patent_term_adjustment_data=adjustment_data,
        )
        mock_response = PatentDataResponse(
            count=1, patent_file_wrapper_data_bag=[wrapper]
        )
        mock_make_request.return_value = mock_response

        client = PatentDataClient(api_key="test_key")
        result = client.get_application_adjustment(application_number=app_num)

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint=f"api/v1/patent/applications/{app_num}/adjustment",
            response_class=PatentDataResponse,
        )
        assert isinstance(result, PatentTermAdjustmentData)
        assert result.adjustment_total_quantity == 150.0

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_assignment(self, mock_make_request: MagicMock) -> None:
        """Test get_application_assignment method."""
        app_num = "12345678"
        assignment = Assignment(reel_number="12345", frame_number="67890")
        wrapper = PatentFileWrapper(
            application_number_text=app_num,
            assignment_bag=[assignment],
        )
        mock_response = PatentDataResponse(
            count=1, patent_file_wrapper_data_bag=[wrapper]
        )
        mock_make_request.return_value = mock_response

        client = PatentDataClient(api_key="test_key")
        result = client.get_application_assignment(application_number=app_num)

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint=f"api/v1/patent/applications/{app_num}/assignment",
            response_class=PatentDataResponse,
        )
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Assignment)
        assert result[0].reel_number == "12345"

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_attorney(self, mock_make_request: MagicMock) -> None:
        """Test get_application_attorney method."""
        app_num = "12345678"
        attorney = Attorney(
            first_name="James", last_name="Legal", registration_number="12345"
        )
        record_attorney = RecordAttorney(attorney_bag=[attorney])
        wrapper = PatentFileWrapper(
            application_number_text=app_num,  # Ensure this matches
            record_attorney=record_attorney,
        )
        mock_response = PatentDataResponse(
            count=1, patent_file_wrapper_data_bag=[wrapper]
        )
        mock_make_request.return_value = mock_response

        client = PatentDataClient(api_key="test_key")
        result = client.get_application_attorney(application_number=app_num)

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint=f"api/v1/patent/applications/{app_num}/attorney",
            response_class=PatentDataResponse,
        )
        assert isinstance(result, RecordAttorney)
        assert len(result.attorney_bag) == 1
        assert result.attorney_bag[0].first_name == "James"

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_continuity(self, mock_make_request: MagicMock) -> None:
        """Test get_application_continuity method."""
        app_num = "12345678"
        parent_cont = ParentContinuity(parent_application_number_text="11111111")
        child_cont = ChildContinuity(child_application_number_text="99999999")
        wrapper = PatentFileWrapper(
            application_number_text=app_num,  # Ensure this matches
            parent_continuity_bag=[parent_cont],
            child_continuity_bag=[child_cont],
        )
        mock_response = PatentDataResponse(
            count=1, patent_file_wrapper_data_bag=[wrapper]
        )
        mock_make_request.return_value = mock_response

        client = PatentDataClient(api_key="test_key")
        result = client.get_application_continuity(application_number=app_num)

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint=f"api/v1/patent/applications/{app_num}/continuity",
            response_class=PatentDataResponse,
        )
        assert isinstance(result, ApplicationContinuityData)
        assert len(result.parent_continuity_bag) == 1
        assert (
            result.parent_continuity_bag[0].parent_application_number_text == "11111111"
        )
        assert len(result.child_continuity_bag) == 1
        assert (
            result.child_continuity_bag[0].child_application_number_text == "99999999"
        )

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_foreign_priority(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test get_application_foreign_priority method."""
        app_num = "12345678"
        foreign_priority = ForeignPriority(
            ip_office_name="European Patent Office",
            application_number_text="EP12345678",
        )
        wrapper = PatentFileWrapper(
            application_number_text=app_num,  # Ensure this matches
            foreign_priority_bag=[foreign_priority],
        )
        mock_response = PatentDataResponse(
            count=1, patent_file_wrapper_data_bag=[wrapper]
        )
        mock_make_request.return_value = mock_response

        client = PatentDataClient(api_key="test_key")
        result = client.get_application_foreign_priority(application_number=app_num)

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint=f"api/v1/patent/applications/{app_num}/foreign-priority",
            response_class=PatentDataResponse,
        )
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], ForeignPriority)
        assert result[0].ip_office_name == "European Patent Office"

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_transactions(self, mock_make_request: MagicMock) -> None:
        """Test get_application_transactions method."""
        app_num = "12345678"
        event = EventData(
            event_code="COMP",
            event_description_text="Application ready for examination",
            event_date=date(2022, 1, 1),
        )
        wrapper = PatentFileWrapper(
            application_number_text=app_num,  # Ensure this matches
            event_data_bag=[event],
        )
        mock_response = PatentDataResponse(
            count=1, patent_file_wrapper_data_bag=[wrapper]
        )
        mock_make_request.return_value = mock_response

        client = PatentDataClient(api_key="test_key")
        result = client.get_application_transactions(application_number=app_num)

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint=f"api/v1/patent/applications/{app_num}/transactions",
            response_class=PatentDataResponse,
        )
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], EventData)
        assert result[0].event_code == "COMP"

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_associated_documents(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test get_application_associated_documents method."""
        app_num = "12345678"
        pgpub_meta = DocumentMetaData(
            zip_file_name="pgpub.zip",
            product_identifier="PGPUB",
            file_create_date_time=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        )
        grant_meta = DocumentMetaData(
            zip_file_name="grant.zip",
            product_identifier="GRANT",
            file_create_date_time=datetime(2023, 2, 1, 12, 0, 0, tzinfo=timezone.utc),
        )
        wrapper = PatentFileWrapper(
            application_number_text=app_num,  # Ensure this matches
            pgpub_document_meta_data=pgpub_meta,
            grant_document_meta_data=grant_meta,
        )
        mock_response = PatentDataResponse(
            count=1, patent_file_wrapper_data_bag=[wrapper]
        )
        mock_make_request.return_value = mock_response

        client = PatentDataClient(api_key="test_key")
        result = client.get_application_associated_documents(application_number=app_num)

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint=f"api/v1/patent/applications/{app_num}/associated-documents",
            response_class=PatentDataResponse,
        )
        assert isinstance(result, AssociatedDocumentsData)
        assert result.pgpub_document_meta_data == pgpub_meta
        assert result.grant_document_meta_data == grant_meta
