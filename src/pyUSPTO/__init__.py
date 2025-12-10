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
from pyUSPTO.clients.patent_data import PatentDataClient
from pyUSPTO.clients.petition_decisions import FinalPetitionDecisionsClient
from pyUSPTO.clients.ptab_appeals import PTABAppealsClient
from pyUSPTO.clients.ptab_interferences import PTABInterferencesClient
from pyUSPTO.clients.ptab_trials import PTABTrialsClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.exceptions import (
    USPTOApiAuthError,
    USPTOApiError,
    USPTOApiNotFoundError,
    USPTOApiRateLimitError,
)
from pyUSPTO.http_config import HTTPConfig

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
    PetitionDecisionDocument,
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
    "USPTOConfig",
    "HTTPConfig",
    # Warning classes
    "USPTODataWarning",
    "USPTODateParseWarning",
    "USPTOBooleanParseWarning",
    "USPTOTimezoneWarning",
    "USPTOEnumParseWarning",
    "USPTODataMismatchWarning",
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
    # Final Petition Decisions API
    "FinalPetitionDecisionsClient",
    "PetitionDecisionResponse",
    "PetitionDecision",
    "PetitionDecisionDocument",
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
