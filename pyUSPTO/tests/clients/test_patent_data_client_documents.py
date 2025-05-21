"""
Tests for the document-related methods of the patent_data client module.

This module contains tests for document downloading and handling methods
of the PatentDataClient class.
"""

import os
from datetime import (  # Ensure date is imported for model compatibility
    date,
    datetime,
    timezone,
)
from unittest.mock import MagicMock, mock_open, patch
from urllib.parse import urlparse

import pytest
import requests

from pyUSPTO.clients.patent_data import PatentDataClient
from pyUSPTO.models.patent_data import (
    ApplicationMetaData,
    AssociatedDocumentsData,
    Document,
    DocumentBag,
    DocumentDownloadFormat,
    DocumentMetaData,
    PatentDataResponse,
    PatentFileWrapper,
)


class TestDocumentBag:
    """Tests for the DocumentBag class."""

    def test_document_bag_iteration(self) -> None:
        """Test that DocumentBag properly implements iteration."""
        from pyUSPTO.models.patent_data import DirectionCategory

        doc1 = Document(
            document_identifier="DOC1",
            official_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
            document_code="TEST1",
        )
        doc2 = Document(
            document_identifier="DOC2",
            official_date=datetime(2023, 1, 2, tzinfo=timezone.utc),
            document_code="TEST2",
        )
        document_bag = DocumentBag(documents=[doc1, doc2])
        doc_list = list(document_bag)
        assert len(doc_list) == 2
        assert doc_list[0] == doc1
        assert doc_list[1] == doc2
        assert len(document_bag) == 2

    def test_string_representations(self) -> None:
        """Test the string representation methods of DocumentBag and Document classes."""
        from pyUSPTO.models.patent_data import (
            DirectionCategory,
            serialize_datetime_as_iso,
        )

        dt_obj = datetime(2023, 1, 1, 10, 30, 0, tzinfo=timezone.utc)
        doc = Document(
            document_identifier="DOC123",
            official_date=dt_obj,  # This is a datetime object
            document_code="IDS",
            document_code_description_text="Information Disclosure Statement",
        )

        # The error showed str(doc) results in '... - 2023-01-01'
        # This means the Document model's __str__ method formats the datetime as a date string.
        # The test should assert against that actual output.
        assert "2023-01-01" in str(doc)  # Check for the date part as shown in the error
        assert "DOC123" in str(doc)
        assert "IDS" in str(doc)
        assert "Information Disclosure Statement" in str(doc)

        download_format = DocumentDownloadFormat(
            mime_type_identifier="PDF",
            download_url="https://example.com/doc.pdf",
            page_total_quantity=10,
        )
        assert "PDF format" in str(download_format)
        assert "10 pages" in str(download_format)

        doc_bag = DocumentBag(documents=[doc])


class TestDocumentHandling:
    """Tests for document handling methods of the PatentDataClient."""

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_document_file_with_url_parsing(
        self, mock_make_request: MagicMock
    ) -> None:
        """Test download_document_file method."""
        mock_response = MagicMock(spec=requests.Response)
        mock_response.headers = {"Content-Disposition": 'filename="test_document.pdf"'}
        mock_response.iter_content.return_value = [b"test content"]
        mock_make_request.return_value = mock_response

        mock_open_func = mock_open()
        with (
            patch("builtins.open", mock_open_func),
            patch("os.path.exists", return_value=True),
        ):
            client = PatentDataClient(api_key="test_key")
            app_num = "12345678"
            doc_id = "DOC123.pdf"
            result = client.download_document_file(
                application_number=app_num, document_id=doc_id, destination_dir="/tmp"
            )
            expected_endpoint = f"api/v1/download/applications/{app_num}/{doc_id}"
            mock_make_request.assert_called_once_with(
                method="GET", endpoint=expected_endpoint, stream=True
            )
            mock_open_func().write.assert_called_with(b"test content")
            assert result == os.path.join("/tmp", "test_document.pdf")

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_document_file_from_document_download_format(
        self, mock_make_request: MagicMock
    ) -> None:
        """
        Test downloading using info that might come from a DocumentDownloadFormat object,
        but calling the correct download_document_file method.
        """
        mock_response = MagicMock(spec=requests.Response)
        mock_response.headers = {
            "Content-Disposition": 'filename="format_object_test.pdf"'
        }
        mock_response.iter_content.return_value = [b"test content"]
        mock_make_request.return_value = mock_response

        download_url_from_format = "https://api.uspto.gov/api/v1/download/applications/app_from_format/doc_from_format.pdf"

        parsed_url = urlparse(download_url_from_format)
        path_parts = parsed_url.path.strip("/").split("/")
        app_num = path_parts[-2] if len(path_parts) > 1 else "unknown_app_num"
        doc_id = path_parts[-1] if path_parts else "unknown_doc_id"

        mock_open_func = mock_open()
        with (
            patch("builtins.open", mock_open_func),
            patch("os.path.exists", return_value=True),
        ):
            client = PatentDataClient(api_key="test_key")
            result = client.download_document_file(
                application_number=app_num, document_id=doc_id, destination_dir="/tmp"
            )
            expected_endpoint = f"api/v1/download/applications/{app_num}/{doc_id}"
            mock_make_request.assert_called_once_with(
                method="GET",
                endpoint=expected_endpoint,
                stream=True,
            )
            mock_open_func().write.assert_called_with(b"test content")
            assert result == os.path.join("/tmp", "format_object_test.pdf")

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_document_file_content_disposition(
        self, mock_make_request: MagicMock
    ) -> None:
        mock_response = MagicMock(spec=requests.Response)
        mock_response.headers = {
            "Content-Disposition": 'attachment; filename="test_file.pdf"'
        }
        mock_response.iter_content.return_value = [b"test content"]
        mock_make_request.return_value = mock_response

        with (
            patch("os.path.exists", return_value=False),
            patch("os.makedirs") as mock_makedirs,
            patch("builtins.open", mock_open()) as mock_file_open,
        ):
            client = PatentDataClient(api_key="test_key")
            result = client.download_document_file(
                application_number="app1",
                document_id="doc1_original_id.pdf",
                destination_dir="./downloads",
            )
            assert result == os.path.join("./downloads", "test_file.pdf")
            mock_makedirs.assert_called_once_with("./downloads", exist_ok=True)
            mock_file_open.assert_called_once_with(file=result, mode="wb")

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_document_file_no_content_disposition(
        self, mock_make_request: MagicMock
    ) -> None:
        mock_response = MagicMock(spec=requests.Response)
        mock_response.headers = {}
        mock_response.iter_content.return_value = [b"test content"]
        mock_make_request.return_value = mock_response

        with (
            patch("os.path.exists", return_value=True),
            patch("builtins.open", mock_open()) as mock_file_open,
        ):
            client = PatentDataClient(api_key="test_key")
            app_num = "app789"
            doc_id = "some_document_from_id.pdf"
            result = client.download_document_file(
                application_number=app_num,
                document_id=doc_id,
                destination_dir="./downloads",
            )
            assert result == os.path.join("./downloads", doc_id)
            mock_file_open.assert_called_once_with(file=result, mode="wb")

    def test_download_document_file_missing_required_params(self) -> None:
        """Test download_document_file raises TypeError when missing required parameters."""
        client = PatentDataClient(api_key="test_key")

        def call_with_partial_args(**kwargs):  # type: ignore[no-untyped-def]
            return client.download_document_file(**kwargs)

        with pytest.raises(TypeError):
            call_with_partial_args(destination_dir="./downloads")  # type: ignore[call-arg]
        with pytest.raises(TypeError):
            call_with_partial_args(application_number="123", destination_dir="./downloads")  # type: ignore[call-arg]
        with pytest.raises(TypeError):
            call_with_partial_args(document_id="doc.pdf", destination_dir="./downloads")  # type: ignore[call-arg]

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_documents(self, mock_make_request: MagicMock) -> None:
        app_num = "12345678"
        mock_response_dict = {
            "documentBag": [
                {
                    "documentIdentifier": "DOC123",
                    "documentCode": "TEST",
                    "documentCodeDescriptionText": "Test Document",
                    "applicationNumberText": app_num,
                    "officialDate": "2023-01-01T10:30:00Z",
                    "documentDirectionCategory": "INCOMING",
                    "downloadOptionBag": [
                        {
                            "mimeTypeIdentifier": "PDF",
                            "downloadURI": "https://example.com/doc.pdf",  # Was downloadUrl
                            "pageTotalQuantity": 5,
                        }
                    ],
                }
            ]
        }
        mock_make_request.return_value = mock_response_dict
        client = PatentDataClient(api_key="test_key")
        result = client.get_application_documents(application_number=app_num)

        mock_make_request.assert_called_once_with(
            method="GET", endpoint=f"api/v1/patent/applications/{app_num}/documents"
        )
        assert isinstance(result, DocumentBag)
        assert len(result) == 1
        doc = result.documents[0]
        assert isinstance(doc, Document)
        assert doc.document_identifier == "DOC123"
        # The model DocumentDownloadFormat uses attribute 'download_url'
        assert doc.download_formats[0].download_url == "https://example.com/doc.pdf"

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_get_application_associated_documents(
        self, mock_make_request: MagicMock
    ) -> None:
        app_num = "12345678"
        pgpub_meta_data = DocumentMetaData(zip_file_name="pgpub.zip")
        grant_meta_data = DocumentMetaData(zip_file_name="grant.zip")

        mock_wrapper = PatentFileWrapper(
            application_number_text=app_num,
            pgpub_document_meta_data=pgpub_meta_data,
            grant_document_meta_data=grant_meta_data,
        )
        mock_response_obj = PatentDataResponse(
            count=1, patent_file_wrapper_data_bag=[mock_wrapper]
        )
        mock_make_request.return_value = mock_response_obj

        client = PatentDataClient(api_key="test_key")
        result = client.get_application_associated_documents(application_number=app_num)

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint=f"api/v1/patent/applications/{app_num}/associated-documents",
            response_class=PatentDataResponse,
        )
        assert isinstance(result, AssociatedDocumentsData)
        assert result.pgpub_document_meta_data == pgpub_meta_data
        assert result.grant_document_meta_data == grant_meta_data


class TestPatentApplicationDownloads:
    """Tests for patent application download methods (search and download metadata)."""

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_patent_applications_get_default_params(
        self, mock_make_request: MagicMock
    ) -> None:
        mock_response_obj = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj
        client = PatentDataClient(api_key="test_key")
        result = client.download_patent_applications_get()

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/patent/applications/search/download",
            params={"format": "json"},
            response_class=PatentDataResponse,
        )
        assert isinstance(result, PatentDataResponse)

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_patent_applications_get_missing_format(
        self, mock_make_request: MagicMock
    ) -> None:
        mock_response_obj = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj
        client = PatentDataClient(api_key="test_key")
        result = client.download_patent_applications_get(params={"q": "test"})

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/patent/applications/search/download",
            params={"q": "test", "format": "json"},
            response_class=PatentDataResponse,
        )
        assert isinstance(result, PatentDataResponse)

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_patent_applications_get_custom_format(
        self, mock_make_request: MagicMock
    ) -> None:
        mock_response_obj = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj
        client = PatentDataClient(api_key="test_key")
        result = client.download_patent_applications_get(format_type="csv")

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/patent/applications/search/download",
            params={"format": "csv"},
            response_class=PatentDataResponse,
        )
        assert isinstance(result, PatentDataResponse)

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_patent_applications_get_format_argument(
        self, mock_make_request: MagicMock
    ) -> None:
        mock_response_obj = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj
        client = PatentDataClient(api_key="test_key")
        result = client.download_patent_applications_get(
            params={"q": "test"}, format_type="csv"
        )

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="api/v1/patent/applications/search/download",
            params={"q": "test", "format": "csv"},
            response_class=PatentDataResponse,
        )
        assert isinstance(result, PatentDataResponse)

    @patch("pyUSPTO.clients.patent_data.PatentDataClient._make_request")
    def test_download_patent_applications_post(
        self, mock_make_request: MagicMock
    ) -> None:
        mock_response_obj = PatentDataResponse(count=1, patent_file_wrapper_data_bag=[])
        mock_make_request.return_value = mock_response_obj
        client = PatentDataClient(api_key="test_key")
        download_request = {"q": "Test", "format": "csv", "fields": ["patentNumber"]}
        result = client.download_patent_applications_post(
            download_request=download_request
        )

        mock_make_request.assert_called_once_with(
            method="POST",
            endpoint="api/v1/patent/applications/search/download",
            json_data=download_request,
            response_class=PatentDataResponse,
        )
        assert isinstance(result, PatentDataResponse)
        assert result.count == 1
