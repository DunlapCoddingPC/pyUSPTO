"""
USPTO API Client - A Python client library for interacting with the USPTO APIs.

This package provides clients for interacting with both the USPTO Bulk Data API
and the USPTO Patent Data API.
"""

__version__ = "0.1.2"

# Import from original locations for backward compatibility
from pyUSPTO.base import (
    BaseUSPTOClient,
)
from pyUSPTO.exceptions import (
    USPTOApiError,
    USPTOApiAuthError,
    USPTOApiRateLimitError,
    USPTOApiNotFoundError,
)
from pyUSPTO.config import USPTOConfig

# Import from original locations for backward compatibility
# These will be replaced with imports from models in the future
from pyUSPTO.models.bulk_data import (
    BulkDataResponse,
    BulkDataProduct,
    ProductFileBag,
    FileData,
)
from pyUSPTO.models.patent_data import (
    PatentDataResponse,
    PatentFileWrapper,
)

# Import client implementations from new locations
from pyUSPTO.clients.bulk_data import BulkDataClient
from pyUSPTO.clients.patent_data import PatentDataClient

__all__ = [
    # Base classes
    "BaseUSPTOClient",
    "USPTOApiError",
    "USPTOApiAuthError",
    "USPTOApiRateLimitError",
    "USPTOApiNotFoundError",
    "USPTOConfig",
    # Bulk Data API
    "BulkDataClient",
    "BulkDataResponse",
    "BulkDataProduct",
    "ProductFileBag",
    "FileData",
    # Patent Data API
    "PatentDataClient",
    "PatentDataResponse",
    "PatentFileWrapper",
]
