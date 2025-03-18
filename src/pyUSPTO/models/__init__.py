"""
models - Data models for USPTO APIs

This package provides data models for USPTO APIs.
"""

from pyUSPTO.models.base import FromDictProtocol
from pyUSPTO.models.bulk_data import (
    BulkDataProduct,
    BulkDataResponse,
    FileData,
    ProductFileBag,
)

__all__ = [
    "FromDictProtocol",
    "FileData",
    "ProductFileBag",
    "BulkDataProduct",
    "BulkDataResponse",
]
