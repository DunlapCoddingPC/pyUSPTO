"""clients - USPTO API client implementations.

This package provides client implementations for USPTO APIs.
"""

from pyUSPTO.clients.bulk_data import BulkDataClient
from pyUSPTO.clients.enriched_citations import EnrichedCitationsClient
from pyUSPTO.clients.oa_actions import OAActionsClient
from pyUSPTO.clients.oa_citations import OACitationsClient
from pyUSPTO.clients.oa_rejections import OARejectionsClient
from pyUSPTO.clients.patent_data import PatentDataClient
from pyUSPTO.clients.petition_decisions import FinalPetitionDecisionsClient
from pyUSPTO.clients.ptab_appeals import PTABAppealsClient
from pyUSPTO.clients.ptab_interferences import PTABInterferencesClient
from pyUSPTO.clients.ptab_trials import PTABTrialsClient

__all__ = [
    "BulkDataClient",
    "EnrichedCitationsClient",
    "OAActionsClient",
    "OACitationsClient",
    "OARejectionsClient",
    "PatentDataClient",
    "FinalPetitionDecisionsClient",
    "PTABTrialsClient",
    "PTABAppealsClient",
    "PTABInterferencesClient",
]
