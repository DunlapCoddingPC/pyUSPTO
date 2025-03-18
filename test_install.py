"""
USPTO API Package Installation Test

This script verifies that the uspto_api package has been correctly installed
and that the main client classes are accessible. It prints the package version
and confirms that the BulkDataClient and PatentDataClient classes can be imported.

Usage:
    python test_install.py
"""

import pyUSPTO
from typing import Any

print(f"USPTO API Client version: {pyUSPTO.__version__}")
print("Available classes:")
print(f"- BulkDataClient: {pyUSPTO.BulkDataClient}")
print(f"- PatentDataClient: {pyUSPTO.PatentDataClient}")
print("\nPackage successfully imported!")
