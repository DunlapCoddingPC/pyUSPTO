"""
USPTO API Client - A Python client library for interacting with the USPTO APIs.

This package provides clients for interacting with the USPTO Open Data Portal APIs.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version(distribution_name="pyUSPTO")
except PackageNotFoundError:
    # package is not installed
    pass

from pyUSPTO.clients.bulk_data import BulkDataClient
from pyUSPTO.clients.patent_data import PatentDataClient
from pyUSPTO.clients.petition_decisions import PetitionDecisionsClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.exceptions import (
    USPTOApiAuthError,
    USPTOApiError,
    USPTOApiNotFoundError,
    USPTOApiRateLimitError,
)

# Import model implementations
from pyUSPTO.models.bulk_data import (
    BulkDataProduct,
    BulkDataResponse,
    FileData,
    ProductFileBag,
)
from pyUSPTO.models.patent_data import PatentDataResponse, PatentFileWrapper
from pyUSPTO.models.petition_decisions import (
    PetitionDecision,
    PetitionDecisionsResponse,
)

__all__ = [
    # Base classes
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
    # Petition Decisions API
    "PetitionDecisionsClient",
    "PetitionDecisionsResponse",
    "PetitionDecision",
]
