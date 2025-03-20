"""
Tests for the DocumentMetaData class in models/patent_data.py.

This module contains tests for the DocumentMetaData class.
"""

from pyUSPTO.models.patent_data import DocumentMetaData


def test_document_meta_data_with_null_input() -> None:
    """Test creation of DocumentMetaData with null input."""
    # Test with empty dict
    document_meta_data = DocumentMetaData.from_dict({})

    # Verify attributes are initialized to None
    assert document_meta_data.zip_file_name is None
    assert document_meta_data.product_identifier is None
    assert document_meta_data.file_location_uri is None
    assert document_meta_data.file_create_date_time is None
    assert document_meta_data.xml_file_name is None

    # Test with None (should be handled by get())
    document_meta_data = DocumentMetaData.from_dict({"zipFileName": None})
    assert document_meta_data.zip_file_name is None
