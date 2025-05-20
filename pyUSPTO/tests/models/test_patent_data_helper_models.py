"""
Tests for the new helper classes in patent_data models.

This module contains tests for the helper dataclasses added to the patent_data models
module to facilitate specific return types from the PatentDataClient.
"""

from unittest.mock import Mock

import pytest

from pyUSPTO.models.patent_data import (
    ApplicationContinuityData,
    AssociatedDocumentsData,
    ChildContinuity,
    DocumentMetaData,
    ParentContinuity,
    PatentFileWrapper,
    parse_yn_to_bool,
    serialize_bool_to_yn,
)


class TestApplicationContinuityData:
    """Tests for the ApplicationContinuityData helper class."""

    def test_from_wrapper_with_data(self):
        """Test from_wrapper method with populated continuity data."""
        # Create test patent wrapper with parent and child continuity
        parent_cont = ParentContinuity(parent_application_number_text="12345678")
        child_cont = ChildContinuity(child_application_number_text="87654321")
        wrapper = PatentFileWrapper(
            parent_continuity_bag=[parent_cont],
            child_continuity_bag=[child_cont],
        )

        # Create continuity data from wrapper
        continuity_data = ApplicationContinuityData.from_wrapper(wrapper)

        # Verify data was extracted correctly
        assert len(continuity_data.parent_continuity_bag) == 1
        assert len(continuity_data.child_continuity_bag) == 1
        assert continuity_data.parent_continuity_bag[0] is parent_cont
        assert continuity_data.child_continuity_bag[0] is child_cont

    def test_from_wrapper_with_empty_data(self):
        """Test from_wrapper method with empty continuity data."""
        # Create test patent wrapper with empty continuity bags
        wrapper = PatentFileWrapper(
            parent_continuity_bag=[],
            child_continuity_bag=[],
        )

        # Create continuity data from wrapper
        continuity_data = ApplicationContinuityData.from_wrapper(wrapper)

        # Verify empty bags are preserved
        assert len(continuity_data.parent_continuity_bag) == 0
        assert len(continuity_data.child_continuity_bag) == 0

    def test_to_dict(self):
        """Test to_dict method for serialization."""
        # Create test parent and child continuity objects with serializable data
        parent = ParentContinuity(
            parent_application_number_text="12345678",
            parent_application_status_code=150,
            claim_parentage_type_code="CON",
        )
        child = ChildContinuity(
            child_application_number_text="87654321",
            child_application_status_code=30,
            claim_parentage_type_code="DIV",
        )

        # Create continuity data with these objects
        continuity_data = ApplicationContinuityData(
            parent_continuity_bag=[parent],
            child_continuity_bag=[child],
        )

        # Get serialized dictionary
        data_dict = continuity_data.to_dict()

        # Verify structure and content
        assert "parentContinuityBag" in data_dict
        assert "childContinuityBag" in data_dict
        assert len(data_dict["parentContinuityBag"]) == 1
        assert len(data_dict["childContinuityBag"]) == 1
        assert (
            data_dict["parentContinuityBag"][0]["parentApplicationNumberText"]
            == "12345678"
        )
        assert (
            data_dict["childContinuityBag"][0]["childApplicationNumberText"]
            == "87654321"
        )


class TestAssociatedDocumentsData:
    """Tests for the AssociatedDocumentsData helper class."""

    def test_from_wrapper_with_data(self):
        """Test from_wrapper method with document metadata."""
        # Create test document metadata
        pgpub_meta = DocumentMetaData(
            zip_file_name="pgpub.zip",
            product_identifier="PGPUB",
            file_location_uri="https://example.com/pgpub.zip",
        )
        grant_meta = DocumentMetaData(
            zip_file_name="grant.zip",
            product_identifier="GRANT",
            file_location_uri="https://example.com/grant.zip",
        )

        # Create test patent wrapper with document metadata
        wrapper = PatentFileWrapper(
            pgpub_document_meta_data=pgpub_meta,
            grant_document_meta_data=grant_meta,
        )

        # Create associated documents data from wrapper
        assoc_docs = AssociatedDocumentsData.from_wrapper(wrapper)

        # Verify data was extracted correctly
        assert assoc_docs.pgpub_document_meta_data is pgpub_meta
        assert assoc_docs.grant_document_meta_data is grant_meta

    def test_from_wrapper_with_partial_data(self):
        """Test from_wrapper method with only pgpub metadata."""
        # Create test document metadata for pgpub only
        pgpub_meta = DocumentMetaData(
            zip_file_name="pgpub.zip",
            product_identifier="PGPUB",
        )

        # Create test patent wrapper with only pgpub metadata
        wrapper = PatentFileWrapper(
            pgpub_document_meta_data=pgpub_meta,
            grant_document_meta_data=None,
        )

        # Create associated documents data from wrapper
        assoc_docs = AssociatedDocumentsData.from_wrapper(wrapper)

        # Verify data was extracted correctly
        assert assoc_docs.pgpub_document_meta_data is pgpub_meta
        assert assoc_docs.grant_document_meta_data is None

    def test_from_wrapper_with_no_data(self):
        """Test from_wrapper method with no document metadata."""
        # Create test patent wrapper with no document metadata
        wrapper = PatentFileWrapper(
            pgpub_document_meta_data=None,
            grant_document_meta_data=None,
        )

        # Create associated documents data from wrapper
        assoc_docs = AssociatedDocumentsData.from_wrapper(wrapper)

        # Verify null values are preserved
        assert assoc_docs.pgpub_document_meta_data is None
        assert assoc_docs.grant_document_meta_data is None

    def test_to_dict(self):
        """Test to_dict method for serialization."""
        # Create test document metadata
        pgpub_meta = DocumentMetaData(
            zip_file_name="pgpub.zip",
            product_identifier="PGPUB",
        )
        grant_meta = DocumentMetaData(
            zip_file_name="grant.zip",
            product_identifier="GRANT",
        )

        # Create associated documents data
        assoc_docs = AssociatedDocumentsData(
            pgpub_document_meta_data=pgpub_meta,
            grant_document_meta_data=grant_meta,
        )

        # Get serialized dictionary
        data_dict = assoc_docs.to_dict()

        # Verify structure and content
        assert "pgpubDocumentMetaData" in data_dict
        assert "grantDocumentMetaData" in data_dict
        assert data_dict["pgpubDocumentMetaData"]["zipFileName"] == "pgpub.zip"
        assert data_dict["grantDocumentMetaData"]["zipFileName"] == "grant.zip"

    def test_to_dict_with_partial_data(self):
        """Test to_dict method with only pgpub metadata."""
        # Create test document metadata for pgpub only
        pgpub_meta = DocumentMetaData(
            zip_file_name="pgpub.zip",
            product_identifier="PGPUB",
        )

        # Create associated documents data with only pgpub metadata
        assoc_docs = AssociatedDocumentsData(
            pgpub_document_meta_data=pgpub_meta,
            grant_document_meta_data=None,
        )

        # Get serialized dictionary
        data_dict = assoc_docs.to_dict()

        # Verify structure and content
        assert "pgpubDocumentMetaData" in data_dict
        assert "grantDocumentMetaData" in data_dict
        assert data_dict["pgpubDocumentMetaData"]["zipFileName"] == "pgpub.zip"
        assert data_dict["grantDocumentMetaData"] is None


class TestYNBooleanConversion:
    """Additional tests for Y/N boolean conversion utilities."""

    def test_parse_yn_to_bool_with_lowercase(self):
        """Test parsing lowercase y/n values."""
        assert parse_yn_to_bool("y") is True
        assert parse_yn_to_bool("n") is False

    def test_parse_yn_to_bool_with_invalid_values(self):
        """Test parsing invalid values."""
        assert parse_yn_to_bool("yes") is None
        assert parse_yn_to_bool("no") is None
        assert parse_yn_to_bool("true") is None
        assert parse_yn_to_bool("false") is None
        assert parse_yn_to_bool("") is None
        assert parse_yn_to_bool("X") is None

    def test_serialize_bool_to_yn_edge_cases(self):
        """Test serializing boolean edge cases."""
        assert serialize_bool_to_yn(True) == "Y"
        assert serialize_bool_to_yn(False) == "N"
        assert serialize_bool_to_yn(None) is None
