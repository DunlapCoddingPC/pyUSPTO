"""USPTO API Client - A Python client library for interacting with the USPTO APIs.

This package provides clients for interacting with the USPTO Open Data Portal APIs.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version(distribution_name="pyUSPTO")
except PackageNotFoundError:
    # package is not installed
    pass

from pyUSPTO.clients.bulk_data import BulkDataClient
from pyUSPTO.clients.enriched_citations import EnrichedCitationsClient
from pyUSPTO.clients.oa_actions import OAActionsClient
from pyUSPTO.clients.oa_rejections import OARejectionsClient
from pyUSPTO.clients.patent_data import PatentDataClient
from pyUSPTO.clients.petition_decisions import FinalPetitionDecisionsClient
from pyUSPTO.clients.ptab_appeals import PTABAppealsClient
from pyUSPTO.clients.ptab_interferences import PTABInterferencesClient
from pyUSPTO.clients.ptab_trials import PTABTrialsClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.exceptions import (
    FormatNotAvailableError,
    USPTOApiAuthError,
    USPTOApiError,
    USPTOApiNotFoundError,
    USPTOApiRateLimitError,
    USPTOConnectionError,
    USPTOTimeout,
)
from pyUSPTO.http_config import HTTPConfig
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

# Import model implementations
from pyUSPTO.models.oa_actions import (
    OAActionsFieldsResponse,
    OAActionsRecord,
    OAActionsResponse,
    OAActionsSection,
)
from pyUSPTO.models.oa_rejections import (
    OARejectionsFieldsResponse,
    OARejectionsRecord,
    OARejectionsResponse,
)
from pyUSPTO.models.patent_data import (
    ApplicationContinuityData,
    PatentDataResponse,
    PatentFileWrapper,
)
from pyUSPTO.models.petition_decisions import (
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
from pyUSPTO.warnings import (
    USPTOBooleanParseWarning,
    USPTODataMismatchWarning,
    USPTODataWarning,
    USPTODateParseWarning,
    USPTOEnumParseWarning,
    USPTOTimezoneWarning,
)

__all__ = [
    # Base classes
    "USPTOApiError",
    "USPTOApiAuthError",
    "USPTOApiRateLimitError",
    "USPTOApiNotFoundError",
    "FormatNotAvailableError",
    "USPTOConnectionError",
    "USPTOTimeout",
    "USPTOConfig",
    "HTTPConfig",
    # Warning classes
    "USPTODataWarning",
    "USPTODateParseWarning",
    "USPTOBooleanParseWarning",
    "USPTOTimezoneWarning",
    "USPTOEnumParseWarning",
    "USPTODataMismatchWarning",
    # OA Actions API
    "OAActionsClient",
    "OAActionsRecord",
    "OAActionsResponse",
    "OAActionsSection",
    "OAActionsFieldsResponse",
    # OA Rejections API
    "OARejectionsClient",
    "OARejectionsRecord",
    "OARejectionsResponse",
    "OARejectionsFieldsResponse",
    # Enriched Citations API
    "EnrichedCitationsClient",
    "CitationCategoryCode",
    "EnrichedCitation",
    "EnrichedCitationResponse",
    "EnrichedCitationFieldsResponse",
    # Bulk Data API
    "BulkDataClient",
    "BulkDataResponse",
    "BulkDataProduct",
    "ProductFileBag",
    "FileData",
    # Patent Data API
    "PatentDataClient",
    "ApplicationContinuityData",
    "PatentDataResponse",
    "PatentFileWrapper",
    # Final Petition Decisions API
    "FinalPetitionDecisionsClient",
    "PetitionDecisionResponse",
    "PetitionDecision",
    "PetitionDecisionDocument",
    "PetitionDecisionDownloadResponse",
    # PTAB API
    "PTABTrialsClient",
    "PTABAppealsClient",
    "PTABInterferencesClient",
    "PTABTrialProceeding",
    "PTABTrialProceedingResponse",
    "PTABAppealDecision",
    "PTABAppealResponse",
    "PTABInterferenceDecision",
    "PTABInterferenceResponse",
]
