"""models - Data models for USPTO APIs.

This package provides data models for USPTO APIs.
"""

from pyUSPTO.models.base import FromDictProtocol
from pyUSPTO.models.bulk_data import (
    BulkDataProduct,
    BulkDataResponse,
    FileData,
    ProductFileBag,
)
from pyUSPTO.models.petition_decisions import (
    DocumentDownloadOption,
    PetitionDecision,
    PetitionDecisionDocument,
    PetitionDecisionDownloadResponse,
    PetitionDecisionResponse,
)
from pyUSPTO.models.ptab import (
    PTABAppealDecision,
    PTABAppealResponse,
    PTABInterferenceDecision,
    PTABInterferenceResponse,
    PTABTrialProceeding,
    PTABTrialProceedingResponse,
)

__all__ = [
    "FromDictProtocol",
    "FileData",
    "ProductFileBag",
    "BulkDataProduct",
    "BulkDataResponse",
    "PetitionDecision",
    "PetitionDecisionDocument",
    "PetitionDecisionResponse",
    "PetitionDecisionDownloadResponse",
    "DocumentDownloadOption",
    # PTAB Models
    "PTABTrialProceeding",
    "PTABTrialProceedingResponse",
    "PTABAppealDecision",
    "PTABAppealResponse",
    "PTABInterferenceDecision",
    "PTABInterferenceResponse",
]
