"""
Tests for the document-related methods of the patent_data client module.

This module contains tests for document downloading and handling methods
of the PatentDataClient class.
"""

import os
from unittest.mock import MagicMock, mock_open, patch

import pytest
import requests

from pyUSPTO.clients.patent_data import PatentDataClient
from pyUSPTO.models.patent_data import (
    Document,
    DocumentBag,
    DocumentDownloadFormat,
    PatentDataResponse,
    PatentFileWrapper,
)


class TestDocumentBag:
    """Tests for the DocumentBag class."""

    def test_document_bag_iteration(self) -> None:
        """Test that DocumentBag properly implements iteration."""
        # Create test documents
        doc1 = Document(
            document_identifier="DOC1",
            official_date="2023-01-01",
            document_code="TEST1",
            document_code_description_text="Test Document 1",
            application_number_text="12345678",
            direction_category="INCOMING",
        )

        doc2 = Document(
            document_identifier="DOC2",
            official_date="2023-01-02",
            document_code="TEST2",
            document_code_description_text="Test Document 2",
            application_number_text="12345678",
            direction_category="OUTGOING",
        )

        # Create a DocumentBag with the test documents
        document_bag = DocumentBag(documents=[doc1, doc2])

        # Test __iter__ implementation
        doc_list = list(document_bag)
        assert len(doc_list) == 2
        assert doc_list[0] == doc1
        assert doc_list[1] == doc2

        # Test iteration over the bag
        for i, doc in enumerate(document_bag):
            if i == 0:
                assert doc.document_identifier == "DOC1"
                assert doc.document_code == "TEST1"
            elif i == 1:
                assert doc.document_identifier == "DOC2"
                assert doc.document_code == "TEST2"

        # Test empty bag iteration
        empty_bag = DocumentBag(documents=[])
        assert list(empty_bag) == []

        # Test __len__ implementation
        assert len(document_bag) == 2
        assert len(empty_bag) == 0

    def test_string_representations(self) -> None:
        """Test the string representation methods of DocumentBag and Document classes."""
        # Create a test document
        doc = Document(
            document_identifier="DOC123",
            official_date="2023-01-01",
            document_code="IDS",
            document_code_description_text="Information Disclosure Statement",
            application_number_text="12345678",
            direction_category="INCOMING",
        )

        # Test Document.__str__
        doc_str = str(doc)
        assert "2023-01-01" in doc_str
        assert "DOC123" in doc_str
        assert "IDS" in doc_str
        assert "Information Disclosure Statement" in doc_str

        # Test Document.__repr__
        doc_repr = repr(doc)
        assert "Document(id=DOC123" in doc_repr
        assert "code=IDS" in doc_repr
        assert "date=2023-01-01" in doc_repr

        # Create a download format for testing
        download_format = DocumentDownloadFormat(
            mime_type_identifier="PDF",
            download_url="https://example.com/doc.pdf",
            page_total_quantity=10,
        )

        # Test DocumentDownloadFormat.__str__
        format_str = str(download_format)
        assert "PDF format" in format_str
        assert "10 pages" in format_str

        # Test DocumentDownloadFormat.__repr__
        format_repr = repr(download_format)
        assert "DocumentDownloadFormat" in format_repr
        assert "mime_type=PDF" in format_repr
        assert "pages=10" in format_repr

        # Create DocumentBag for testing
        docs = [doc]
        doc_bag = DocumentBag(documents=docs)

        # Test DocumentBag.__str__
        bag_str = str(doc_bag)
        assert "DocumentBag with 1 documents" in bag_str

        # Test DocumentBag.__repr__
        bag_repr = repr(doc_bag)
        assert "DocumentBag(1 documents: DOC123)" in bag_repr

        # Test with empty bag
        empty_bag = DocumentBag(documents=[])
        assert str(empty_bag) == "DocumentBag with 0 documents"
        assert repr(empty_bag) == "DocumentBag(empty)"

        # Test with multiple documents
        docs = [
            Document(document_identifier=f"DOC{i}", document_code=f"CODE{i}")
            for i in range(1, 5)
        ]
        multi_doc_bag = DocumentBag(documents=docs)
        multi_bag_repr = repr(multi_doc_bag)
        assert "4 documents" in multi_bag_repr
        assert "more" in multi_bag_repr  # Should indicate there are more docs


class TestDocumentHandling:
    """Tests for document handling methods of the PatentDataClient."""

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_application_document(self, mock_make_request: MagicMock) -> None:
        """Test download_application_document method."""
        # Setup mock for the response
        mock_response = MagicMock(spec=requests.Response)
        mock_response.headers = {"Content-Disposition": 'filename="test_document.pdf"'}
        mock_response.iter_content.return_value = [b"test content"]
        mock_make_request.return_value = mock_response

        # Mock open function
        mock_open_func = mock_open()
        mock_file = MagicMock()
        mock_open_func.return_value.__enter__.return_value = mock_file

        with (
            patch("builtins.open", mock_open_func),
            patch("os.path.exists", return_value=True),
        ):
            # Create client and call method
            client = PatentDataClient(api_key="test_key")
            result = client.download_application_document(
                application_number="12345678", document_id="DOC123", destination="/tmp"
            )

            # Verify request was made correctly with correct base URL handling
            mock_make_request.assert_called_once_with(
                method="GET",
                endpoint="download/applications/12345678/DOC123.pdf",
                stream=True,
                custom_base_url=client.base_url.split("/patent")[0],
            )

            # Verify file was written correctly
            mock_file.write.assert_called_with(b"test content")
            # Use os.path.join for cross-platform paths
            assert result == os.path.join("/tmp", "test_document.pdf")

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_application_document_content_disposition_parsing(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test download_application_document with Content-Disposition header parsing."""
        # Setup mock to simulate a Response object
        mock_response = MagicMock(spec=requests.Response)
        mock_response.headers = {
            "Content-Disposition": 'attachment; filename="test_file.pdf"'
        }
        mock_response.iter_content.return_value = [b"test content"]
        mock_make_request.return_value = mock_response

        # Setup os.path.exists to return False so os.makedirs is called
        with (
            patch("os.path.exists", return_value=False),
            patch("os.makedirs") as mock_makedirs,
            patch("builtins.open", mock_open()) as mock_file,
        ):
            # Create client
            client = PatentDataClient(api_key="test_key")

            # Call the method
            result = client.download_application_document(
                application_number="12345678",
                document_id="document123",
                destination="./downloads",
            )

            # Verify the path extraction from Content-Disposition header
            assert result == os.path.join("./downloads", "test_file.pdf")
            mock_makedirs.assert_called_once_with("./downloads")
            mock_file.assert_called_once_with(file=result, mode="wb")

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_application_document_no_filename_in_header(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test download_application_document with Content-Disposition header but no filename."""
        # Setup mock to simulate a Response object
        mock_response = MagicMock(spec=requests.Response)
        mock_response.headers = {"Content-Disposition": "attachment;"}  # No filename
        mock_response.iter_content.return_value = [b"test content"]
        mock_make_request.return_value = mock_response

        # Setup os.path.exists to return False so os.makedirs is called
        with (
            patch("os.path.exists", return_value=False),
            patch("os.makedirs") as mock_makedirs,
            patch("builtins.open", mock_open()) as mock_file,
        ):
            # Create client
            client = PatentDataClient(api_key="test_key")

            # Call the method
            result = client.download_application_document(
                application_number="12345678",
                document_id="document123",
                destination="./downloads",
            )

            # Should use document_id as filename
            assert result == os.path.join("./downloads", "document123")

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_application_document_no_content_disposition(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test download_application_document without Content-Disposition header."""
        # Setup mock to simulate a Response object
        mock_response = MagicMock(spec=requests.Response)
        mock_response.headers = {}  # No Content-Disposition header
        mock_response.iter_content.return_value = [b"test content"]
        mock_make_request.return_value = mock_response

        # Setup os.path.exists to return False so os.makedirs is called
        with (
            patch("os.path.exists", return_value=False),
            patch("os.makedirs") as mock_makedirs,
            patch("builtins.open", mock_open()) as mock_file,
        ):
            # Create client
            client = PatentDataClient(api_key="test_key")

            # Call the method
            result = client.download_application_document(
                application_number="12345678",
                document_id="document123",
                destination="./downloads",
            )

            # Should use document_id as filename when no Content-Disposition header
            assert result == os.path.join("./downloads", "document123")

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_documents(self, mock_make_request: MagicMock) -> None:
        """Test get_application_documents method."""
        # Setup mock - return a dictionary that will be converted to DocumentBag
        mock_response_dict = {
            "documentBag": [
                {
                    "documentIdentifier": "DOC123",
                    "documentCode": "TEST",
                    "documentCodeDescriptionText": "Test Document",
                    "applicationNumberText": "12345678",
                    "officialDate": "2023-01-01",
                    "directionCategory": "INCOMING",
                    "downloadOptionBag": [
                        {
                            "mimeTypeIdentifier": "PDF",
                            "downloadUrl": "https://example.com/doc.pdf",
                            "pageTotalQuantity": 5,
                        }
                    ],
                }
            ]
        }
        mock_make_request.return_value = mock_response_dict

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        result = client.get_application_documents(application_number="12345678")

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/12345678/documents",
        )

        # Verify result
        assert isinstance(result, DocumentBag)
        assert len(result) == 1
        doc = result.documents[0]
        assert isinstance(doc, Document)
        assert doc.document_identifier == "DOC123"
        assert doc.document_code == "TEST"
        assert doc.document_code_description_text == "Test Document"
        assert len(doc.download_formats) == 1
        assert doc.download_formats[0].mime_type_identifier == "PDF"
        assert doc.download_formats[0].download_url == "https://example.com/doc.pdf"

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_associated_documents(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test get_application_associated_documents method."""
        # Setup mock
        mock_response_obj = PatentDataResponse(count=1, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        result = client.get_application_associated_documents(
            application_number="12345678"
        )

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/12345678/associated-documents",
            response_class=PatentDataResponse,
        )

        # Verify result
        assert isinstance(result, PatentDataResponse)
        assert result.count == 1


class TestPatentApplicationDownloads:
    """Tests for patent application download methods."""

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_patent_applications_default_params(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test download_patent_applications with default parameters."""
        # Setup mock response
        mock_response_obj = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        # Create client and call method without params
        client = PatentDataClient(api_key="test_key")
        result = client.download_patent_applications()

        # Verify request was made correctly with default format
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/search/download",
            params={"format": "json"},
            response_class=PatentDataResponse,
        )

        # Verify the result type
        assert isinstance(result, PatentDataResponse)

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_patent_applications_missing_format(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test download_patent_applications when format is missing in params."""
        # Setup mock response
        mock_response_obj = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        # Create client and call method with params missing 'format'
        client = PatentDataClient(api_key="test_key")
        result = client.download_patent_applications(params={"q": "test"})

        # Verify request was made correctly with default format added
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/search/download",
            params={"q": "test", "format": "json"},
            response_class=PatentDataResponse,
        )

        # Verify the result type
        assert isinstance(result, PatentDataResponse)

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_patent_applications_custom_format(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test download_patent_applications with custom format."""
        # Setup mock response
        mock_response_obj = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        # Create client and call method with custom format
        client = PatentDataClient(api_key="test_key")
        result = client.download_patent_applications(format="csv")

        # Verify request was made correctly with custom format
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/search/download",
            params={"format": "csv"},
            response_class=PatentDataResponse,
        )

        # Verify the result type
        assert isinstance(result, PatentDataResponse)

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_patent_applications_format_argument(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test download_patent_applications with format passed as a separate argument."""
        # Setup mock response
        mock_response_obj = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj

        # Create client and call method with format passed as a separate argument
        client = PatentDataClient(api_key="test_key")
        result = client.download_patent_applications(params={"q": "test"}, format="csv")

        # Verify request was made correctly with format added to params
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="applications/search/download",
            params={"q": "test", "format": "csv"},
            response_class=PatentDataResponse,
        )

        # Verify the result type
        assert isinstance(result, PatentDataResponse)

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_patent_applications_post(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test download_patent_applications_post method."""
        # Setup mock
        mock_response_obj = PatentDataResponse(
            count=1,
            patent_file_wrapper_data_bag=[
                PatentFileWrapper(
                    application_number_text="12345678",
                    application_meta_data=MagicMock(invention_title="Test Invention"),
                ),
            ],
        )
        mock_make_request.return_value = mock_response_obj

        # Create client and call method
        client = PatentDataClient(api_key="test_key")
        download_request = {
            "q": "Test",
            "format": "csv",
            "fields": ["patentNumber", "inventionTitle"],
        }
        result = client.download_patent_applications_post(
            download_request=download_request
        )

        # Verify request was made correctly
        mock_make_request.assert_called_once_with(
            method="POST",
            endpoint="applications/search/download",
            json_data=download_request,
            response_class=PatentDataResponse,
        )

        # Verify result
        assert isinstance(result, PatentDataResponse)
        assert result.count == 1
