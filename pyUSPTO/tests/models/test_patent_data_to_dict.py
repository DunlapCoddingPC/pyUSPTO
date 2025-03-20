"""
Tests for the patent_data models to_dict method.

This module contains tests specifically for the to_dict methods in patent_data models.
"""

from pyUSPTO.models.patent_data import PatentDataResponse, PatentFileWrapper


def test_patent_data_response_to_dict() -> None:
    """Test the to_dict method of PatentDataResponse."""
    # Create a PatentDataResponse object with sample data
    wrapper1 = PatentFileWrapper(application_number_text="12345678")
    wrapper2 = PatentFileWrapper(application_number_text="87654321")

    response = PatentDataResponse(
        count=2, patent_file_wrapper_data_bag=[wrapper1, wrapper2]
    )

    # Convert to dictionary
    result = response.to_dict()

    # Verify the resulting dictionary
    assert result["count"] == 2
    assert len(result["patentFileWrapperDataBag"]) == 2
    assert result["patentFileWrapperDataBag"][0]["applicationNumberText"] == "12345678"
    assert result["patentFileWrapperDataBag"][1]["applicationNumberText"] == "87654321"
    assert "documentBag" in result  # Tests the creation of empty placeholders
    assert result["documentBag"] == []

    # Test with empty patent_file_wrapper_data_bag
    empty_response = PatentDataResponse(count=0, patent_file_wrapper_data_bag=[])
    empty_result = empty_response.to_dict()
    assert empty_result["count"] == 0
    assert len(empty_result["patentFileWrapperDataBag"]) == 0
    assert "documentBag" in empty_result
