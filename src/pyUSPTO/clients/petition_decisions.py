"""Client for the USPTO Petition Decisions API."""

from typing import Any, Dict, Iterator, Optional

from pyUSPTO.clients.base import BaseUSPTOClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.petition_decisions import (
    PetitionDecision,
    PetitionDecisionsResponse,
)


class PetitionDecisionsClient(BaseUSPTOClient[PetitionDecisionsResponse]):
    """Client for interacting with the Petition Decisions API."""

    ENDPOINTS = {
        "search_decisions": "api/v1/petition/decisions/search",
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        config: Optional[USPTOConfig] = None,
    ) -> None:
        self.config = config or USPTOConfig(api_key=api_key)
        api_key_to_use = api_key or self.config.api_key
        effective_base_url = (
            base_url
            or self.config.petition_decisions_base_url
            or "https://api.uspto.gov"
        )
        super().__init__(api_key=api_key_to_use, base_url=effective_base_url)

    def search_decisions(
        self,
        query: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        facets: Optional[bool] = None,
        additional_query_params: Optional[Dict[str, Any]] = None,
    ) -> PetitionDecisionsResponse:
        """Search for petition decisions."""

        params: Dict[str, Any] = {}
        if query:
            params["q"] = query
        if offset is not None:
            params["offset"] = offset
        if limit is not None:
            params["limit"] = limit
        if facets is not None:
            params["facets"] = str(facets).lower()
        if additional_query_params:
            params.update(additional_query_params)

        result = self._make_request(
            method="GET",
            endpoint=self.ENDPOINTS["search_decisions"],
            params=params or None,
            response_class=PetitionDecisionsResponse,
        )
        assert isinstance(result, PetitionDecisionsResponse)
        return result

    def paginate_decisions(self, **kwargs: Any) -> Iterator[PetitionDecision]:
        """Paginate through all decisions matching the search criteria."""

        return self.paginate_results(
            method_name="search_decisions",
            response_container_attr="petition_decision_data_bag",
            **kwargs,
        )

