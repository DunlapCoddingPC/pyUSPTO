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
from pyUSPTO.models.enriched_citations import (
    CitationCategoryCode,
    EnrichedCitation,
    EnrichedCitationFieldsResponse,
    EnrichedCitationResponse,
)
from pyUSPTO.models.oa_actions import (
    OAActionsFieldsResponse,
    OAActionsRecord,
    OAActionsResponse,
    OAActionsSection,
)
from pyUSPTO.models.oa_citations import (
    OACitationRecord,
    OACitationsFieldsResponse,
    OACitationsResponse,
)
from pyUSPTO.models.oa_rejections import (
    OARejectionsFieldsResponse,
    OARejectionsRecord,
    OARejectionsResponse,
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
    # Enriched Citations Models
    "CitationCategoryCode",
    # OA Actions Models
    "OAActionsRecord",
    "OAActionsResponse",
    "OAActionsSection",
    "OAActionsFieldsResponse",
    # OA Citations Models
    "OACitationRecord",
    "OACitationsResponse",
    "OACitationsFieldsResponse",
    # OA Rejections Models
    "OARejectionsRecord",
    "OARejectionsResponse",
    "OARejectionsFieldsResponse",
    "EnrichedCitation",
    "EnrichedCitationResponse",
    "EnrichedCitationFieldsResponse",
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
