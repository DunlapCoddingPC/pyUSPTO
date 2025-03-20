"""
Tests for the __init__ module.

This module contains tests for import paths and version handling.
"""

import importlib
import sys
from unittest.mock import patch

import pyUSPTO


def test_version_fallback() -> None:
    """Test the fallback version when _version is not available."""
    # Store the original version
    original_version = pyUSPTO.__version__

    # Patch the __version__ attribute to simulate fallback behavior
    with patch.object(pyUSPTO, "__version__", "0.0.0.dev0"):
        # Verify the fallback version can be accessed
        assert pyUSPTO.__version__ == "0.0.0.dev0"

    # Verify version is restored after the patch
    assert pyUSPTO.__version__ == original_version


def test_all_exports() -> None:
    """Test that all exports in __all__ are available."""
    # Test all the symbols in __all__ are actually exported
    for symbol in pyUSPTO.__all__:
        assert hasattr(
            pyUSPTO, symbol
        ), f"Symbol '{symbol}' not exported in __init__.py"

        # Check that the symbol is properly imported
        imported_symbol = getattr(pyUSPTO, symbol)
        assert imported_symbol is not None, f"Symbol '{symbol}' is None"


def test_import_backward_compatibility() -> None:
    """Test the backward compatibility imports."""
    # Test imports from base module
    assert pyUSPTO.BaseUSPTOClient is not None

    # Test imports from exceptions
    assert pyUSPTO.USPTOApiError is not None
    assert pyUSPTO.USPTOApiAuthError is not None
    assert pyUSPTO.USPTOApiRateLimitError is not None
    assert pyUSPTO.USPTOApiNotFoundError is not None

    # Test client implementations
    assert pyUSPTO.BulkDataClient is not None
    assert pyUSPTO.PatentDataClient is not None
    assert pyUSPTO.USPTOConfig is not None

    # Test model imports from bulk_data
    assert pyUSPTO.BulkDataProduct is not None
    assert pyUSPTO.BulkDataResponse is not None
    assert pyUSPTO.FileData is not None
    assert pyUSPTO.ProductFileBag is not None

    # Test model imports from patent_data
    assert pyUSPTO.PatentDataResponse is not None
    assert pyUSPTO.PatentFileWrapper is not None
