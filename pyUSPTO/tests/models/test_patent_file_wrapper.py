"""
Tests for the PatentFileWrapper class in models/patent_data.py.

This module contains tests to ensure complete coverage of the from_dict method.
"""

from pyUSPTO.models.patent_data import PatentFileWrapper


def test_patent_file_wrapper_with_grant_document_meta_data() -> None:
    """Test creation of PatentFileWrapper with grant document metadata."""
    # Test data with grant document metadata
    data = {
        "applicationNumberText": "12345678",
        "grantDocumentMetaData": {
            "zipFileName": "test.zip",
            "productIdentifier": "PROD123",
            "fileLocationURI": "https://example.com/test.zip",
            "fileCreateDateTime": "2023-01-01T12:00:00",
            "xmlFileName": "test.xml",
        },
    }

    # Create a PatentFileWrapper from the data
    wrapper = PatentFileWrapper.from_dict(data)

    # Verify grant_document_meta_data was correctly created
    assert wrapper.grant_document_meta_data is not None
    assert wrapper.grant_document_meta_data.zip_file_name == "test.zip"
    assert wrapper.grant_document_meta_data.product_identifier == "PROD123"
    assert (
        wrapper.grant_document_meta_data.file_location_uri
        == "https://example.com/test.zip"
    )
    assert (
        wrapper.grant_document_meta_data.file_create_date_time == "2023-01-01T12:00:00"
    )
    assert wrapper.grant_document_meta_data.xml_file_name == "test.xml"
