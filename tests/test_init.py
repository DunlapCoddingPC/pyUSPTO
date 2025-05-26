"""
Tests for the pyUSPTO package initialization.

This module contains tests for import paths, version handling, and import error scenarios.
"""

import importlib
import sys
from importlib.metadata import PackageNotFoundError, version
from typing import Any
from unittest.mock import patch

import pyUSPTO


def test_version() -> None:
    """Test the version."""
    # Test case 1: Package is installed and version is available
    # This tests the normal case where pyUSPTO is properly installed
    if hasattr(pyUSPTO, "__version__"):
        # If version is set, it should be a string
        assert isinstance(pyUSPTO.__version__, str)
        assert len(pyUSPTO.__version__) > 0

    # Test case 2: Simulate package not found scenario by reloading module
    with patch("importlib.metadata.version") as mock_version:
        mock_version.side_effect = PackageNotFoundError("pyUSPTO")

        # Save original modules
        original_modules = sys.modules.copy()

        try:
            # Remove pyUSPTO from sys.modules to force reimport
            for key in list(sys.modules.keys()):
                if key.startswith("pyUSPTO"):
                    del sys.modules[key]

            # Import pyUSPTO with mocked version function
            import pyUSPTO as test_module

            # The module should import successfully without raising an exception
            # __version__ should not be set when PackageNotFoundError occurs
            assert not hasattr(test_module, "__version__")

        finally:
            # Restore original modules
            sys.modules.clear()
            sys.modules.update(original_modules)

    # Test case 3: Simulate successful version retrieval by reloading module
    with patch("importlib.metadata.version") as mock_version:
        mock_version.return_value = "1.2.3"

        # Save original modules
        original_modules = sys.modules.copy()

        try:
            # Remove pyUSPTO from sys.modules to force reimport
            for key in list(sys.modules.keys()):
                if key.startswith("pyUSPTO"):
                    del sys.modules[key]

            # Import pyUSPTO with mocked version function
            import pyUSPTO as test_module

            # Version should be set to our mocked value
            assert hasattr(test_module, "__version__")
            assert test_module.__version__ == "1.2.3"

        finally:
            # Restore original modules
            sys.modules.clear()
            sys.modules.update(original_modules)


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
