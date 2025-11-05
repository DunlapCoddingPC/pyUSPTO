"""
clients - USPTO API client implementations

This package provides client implementations for USPTO APIs.
"""

from pyUSPTO.clients.bulk_data import BulkDataClient
from pyUSPTO.clients.patent_data import PatentDataClient
from pyUSPTO.clients.petition_decisions import FinalPetitionDecisionsClient

__all__ = [
    "BulkDataClient",
    "PatentDataClient",
    "FinalPetitionDecisionsClient",
]
