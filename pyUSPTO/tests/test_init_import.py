"""
Tests for the import behavior in __init__.py.

This module specifically tests the direct import functionality.
"""

import importlib
import sys
from unittest.mock import patch


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
            def __getattr__(self, name):
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
