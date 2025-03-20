"""
Final coverage tests specifically targeting the remaining uncovered lines in patent_data.py.

This module contains tests that explicitly target lines 457, 567, 578, 581, 586, and 601.
"""

import os
import sys
from importlib import reload
from unittest.mock import MagicMock, mock_open, patch

import pytest
import requests

from pyUSPTO.clients.patent_data import PatentDataClient
from pyUSPTO.models.patent_data import PatentDataResponse


class TestPatentDataFinalCoverage:
    """Tests specifically targeting the remaining uncovered lines in PatentDataClient."""

    @patch(
        "requests.Response", MagicMock
    )  # Ensure requests.Response is properly patched
    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_application_document_not_response_object_line_457(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test line 457 in download_application_document - specifically testing the isinstance check."""
        # This test specifically targets line 457: if not isinstance(response, requests.Response):

        # Create a dict object that will fail the isinstance check against requests.Response
        mock_response = {"not": "a response object"}
        mock_make_request.return_value = mock_response

        # Create client with required parameters
        client = PatentDataClient(api_key="test_key")

        # Line 457 should raise TypeError with a specific message
        with pytest.raises(
            TypeError, match="Expected a Response object for streaming download"
        ):
            # Call the method that should execute line 457
            result = client.download_application_document(
                application_number="12345678", document_id="DOC123", destination="/tmp"
            )

    @patch("requests.Response")
    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_search_patents_filing_date_from_alone_line_567(
        self, mock_make_request: MagicMock, mock_response: MagicMock
    ) -> None:
        """Test line 567 in search_patents - filing_date_from alone."""
        mock_response_obj = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        client = PatentDataClient(api_key="test_key")

        # Call with only filing_date_from to hit line 567
        # Make sure no other date parameters are provided
        result = client.search_patents(
            filing_date_from="2020-01-01",
            filing_date_to=None,
            grant_date_from=None,
            grant_date_to=None,
        )

        # Verify
        mock_make_request.assert_called_once()
        call_args = mock_make_request.call_args[1]
        assert call_args["params"]["q"] == "applicationMetaData.filingDate:>=2020-01-01"

    @patch("requests.Response")
    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_search_patents_filing_date_to_alone_line_578(
        self, mock_make_request: MagicMock, mock_response: MagicMock
    ) -> None:
        """Test line 578 in search_patents - filing_date_to alone."""
        mock_response_obj = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        client = PatentDataClient(api_key="test_key")

        # Call with only filing_date_to to hit line 578
        # Make sure no other date parameters are provided
        result = client.search_patents(
            filing_date_from=None,
            filing_date_to="2022-01-01",
            grant_date_from=None,
            grant_date_to=None,
        )

        # Verify
        mock_make_request.assert_called_once()
        call_args = mock_make_request.call_args[1]
        assert call_args["params"]["q"] == "applicationMetaData.filingDate:<=2022-01-01"

    @patch("requests.Response")
    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_search_patents_grant_date_from_alone_line_581(
        self, mock_make_request: MagicMock, mock_response: MagicMock
    ) -> None:
        """Test line 581 in search_patents - grant_date_from alone."""
        mock_response_obj = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        client = PatentDataClient(api_key="test_key")

        # Call with only grant_date_from to hit line 581
        # Make sure no other date parameters are provided
        result = client.search_patents(
            filing_date_from=None,
            filing_date_to=None,
            grant_date_from="2020-01-01",
            grant_date_to=None,
        )

        # Verify
        mock_make_request.assert_called_once()
        call_args = mock_make_request.call_args[1]
        assert call_args["params"]["q"] == "applicationMetaData.grantDate:>=2020-01-01"

    @patch("requests.Response")
    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_search_patents_grant_date_to_alone_line_586(
        self, mock_make_request: MagicMock, mock_response: MagicMock
    ) -> None:
        """Test line 586 in search_patents - grant_date_to alone."""
        mock_response_obj = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        client = PatentDataClient(api_key="test_key")

        # Call with only grant_date_to to hit line 586
        # Make sure no other date parameters are provided
        result = client.search_patents(
            filing_date_from=None,
            filing_date_to=None,
            grant_date_from=None,
            grant_date_to="2022-01-01",
        )

        # Verify
        mock_make_request.assert_called_once()
        call_args = mock_make_request.call_args[1]
        assert call_args["params"]["q"] == "applicationMetaData.grantDate:<=2022-01-01"

    @patch("requests.Response")
    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_search_patents_no_limit_offset_line_601(
        self, mock_make_request: MagicMock, mock_response: MagicMock
    ) -> None:
        """Test line 601 in search_patents - no limit/offset params."""
        mock_response_obj = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        client = PatentDataClient(api_key="test_key")

        # Explicitly pass None for both limit and offset
        result = client.search_patents(query="test query", limit=None, offset=None)

        # Verify that no limit/offset params were included
        mock_make_request.assert_called_once()
        call_args = mock_make_request.call_args[1]
        assert "limit" not in call_args["params"]
        assert "offset" not in call_args["params"]
        assert call_args["params"]["q"] == "test query"

    @patch("pyUSPTO.base.BaseUSPTOClient._make_request")
    def test_search_patents_explicit_q_parameter(self, mock_make_request):
        import inspect
        import linecache

        from pyUSPTO.models.patent_data import PatentDataResponse

        mock_response = MagicMock(spec=PatentDataResponse)
        mock_make_request.return_value = mock_response

        client = PatentDataClient(api_key="test_key")
        # Print the actual line at position 601
        file_path = inspect.getfile(client.__class__)
        print(
            f"The line at 601 is: {linecache.getline(filename=file_path, lineno=601).strip()}"
        )

        # Use only a simple query with no other parameters to isolate line 601
        client.search_patents(query="unique_test_query", limit=None, offset=None)

        # Verify the q parameter was added
        called_args = mock_make_request.call_args
        called_params = called_args[1]["params"]

        # Print for debugging
        print(f"Called params: {called_params}")
        assert "q" in called_params
        assert called_params["q"] == "unique_test_query"

    @patch("pyUSPTO.base.BaseUSPTOClient._make_request")
    def test_search_patents_application_number_filter(self, mock_make_request):
        from pyUSPTO.models.patent_data import PatentDataResponse

        mock_response = MagicMock(spec=PatentDataResponse)
        mock_make_request.return_value = mock_response

        client = PatentDataClient(api_key="test_key")
        application_number = "12345678"

        client.search_patents(application_number=application_number)

        called_args = mock_make_request.call_args
        called_params = called_args[1]["params"]

        assert "q" in called_params
        assert f"applicationNumberText:{application_number}" in called_params["q"]

    @patch("pyUSPTO.base.BaseUSPTOClient._make_request")
    def test_search_patents_applicant_name_filter(self, mock_make_request):
        from pyUSPTO.models.patent_data import PatentDataResponse

        mock_response = MagicMock(spec=PatentDataResponse)
        mock_make_request.return_value = mock_response

        client = PatentDataClient(api_key="test_key")
        applicant_name = "Test Applicant"

        client.search_patents(applicant_name=applicant_name)

        called_args = mock_make_request.call_args
        called_params = called_args[1]["params"]

        assert "q" in called_params
        assert (
            f"applicationMetaData.firstApplicantName:{applicant_name}"
            in called_params["q"]
        )

    @patch("pyUSPTO.base.BaseUSPTOClient._make_request")
    def test_search_patents_assignee_name_filter(self, mock_make_request):
        from pyUSPTO.models.patent_data import PatentDataResponse

        mock_response = MagicMock(spec=PatentDataResponse)
        mock_make_request.return_value = mock_response

        client = PatentDataClient(api_key="test_key")
        assignee_name = "Test Assignee"

        client.search_patents(assignee_name=assignee_name)

        called_args = mock_make_request.call_args
        called_params = called_args[1]["params"]

        assert "q" in called_params
        assert (
            f"assignmentBag.assigneeBag.assigneeNameText:{assignee_name}"
            in called_params["q"]
        )

    @patch("pyUSPTO.base.BaseUSPTOClient._make_request")
    def test_search_patents_classification_filter(self, mock_make_request):
        from pyUSPTO.models.patent_data import PatentDataResponse

        mock_response = MagicMock(spec=PatentDataResponse)
        mock_make_request.return_value = mock_response

        client = PatentDataClient(api_key="test_key")
        classification = "G06F"

        client.search_patents(classification=classification)

        called_args = mock_make_request.call_args
        called_params = called_args[1]["params"]

        assert "q" in called_params
        assert (
            f"applicationMetaData.cpcClassificationBag:{classification}"
            in called_params["q"]
        )

    @patch("pyUSPTO.base.BaseUSPTOClient._make_request")
    def test_search_patents_grant_date_range_filter(self, mock_make_request):
        from pyUSPTO.models.patent_data import PatentDataResponse

        mock_response = MagicMock(spec=PatentDataResponse)
        mock_make_request.return_value = mock_response

        client = PatentDataClient(api_key="test_key")
        grant_date_from = "2020-01-01"
        grant_date_to = "2020-12-31"

        client.search_patents(
            grant_date_from=grant_date_from, grant_date_to=grant_date_to
        )

        called_args = mock_make_request.call_args
        called_params = called_args[1]["params"]

        assert "q" in called_params
        assert (
            f"applicationMetaData.grantDate:[{grant_date_from} TO {grant_date_to}]"
            in called_params["q"]
        )
