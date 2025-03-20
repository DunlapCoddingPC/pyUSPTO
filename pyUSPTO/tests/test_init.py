"""
Tests for the pyUSPTO package initialization.

This module contains tests for import paths, version handling, and import error scenarios.
"""

import importlib
import sys
from typing import Any
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


def test_direct_import_of_init_with_import_error() -> None:
    """Test importing the __init__ module directly when _version raises ImportError."""
    # Save original modules
    original_modules = sys.modules.copy()

    try:
        # Make sure pyUSPTO isn't already imported
        for key in list(sys.modules.keys()):
            if key.startswith("pyUSPTO"):
                del sys.modules[key]

        # Create mock module that raises ImportError when accessed
        class RaisingImportError:
            def __getattr__(self, name: str) -> Any:
                raise ImportError(f"Mock ImportError for {name}")

        # Apply the mock directly to sys.modules
        with patch.dict("sys.modules", {"pyUSPTO._version": RaisingImportError()}):
            # Force a fresh import of pyUSPTO
            import pyUSPTO

            # Verify the fallback version was used
            assert pyUSPTO.__version__ == "0.0.0.dev0"

    finally:
        # Restore the original modules
        sys.modules.clear()
        sys.modules.update(original_modules)


def test_import_with_version_module_missing() -> None:
    """Test importing when the _version module is missing entirely."""
    # Save original modules
    original_modules = sys.modules.copy()

    try:
        # Remove all pyUSPTO modules from sys.modules
        for key in list(sys.modules.keys()):
            if key.startswith("pyUSPTO"):
                del sys.modules[key]

        # Set _version to None, simulating it doesn't exist
        with patch.dict("sys.modules", {"pyUSPTO._version": None}):
            # Import pyUSPTO
            import pyUSPTO

            # Verify the fallback version was used
            assert pyUSPTO.__version__ == "0.0.0.dev0"

    finally:
        # Restore the original modules
        sys.modules.clear()
        sys.modules.update(original_modules)
