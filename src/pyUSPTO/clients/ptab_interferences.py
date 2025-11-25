"""
clients.ptab_interferences - Client for USPTO PTAB Interferences API

This module provides a client for interacting with the USPTO PTAB (Patent Trial
and Appeal Board) Interferences API. It allows you to search for patent interference decisions.
"""

from typing import Any, Dict, Iterator, Optional

from pyUSPTO.clients.base import BaseUSPTOClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.ptab import PTABInterferenceDecision, PTABInterferenceResponse


class PTABInterferencesClient(BaseUSPTOClient[PTABInterferenceResponse]):
    """Client for interacting with the USPTO PTAB Interferences API.

    This client provides methods to search for patent interference decisions from the
    Patent Trial and Appeal Board.

    Interference proceedings are used to determine priority of invention when two or
    more parties claim the same patentable invention.
    """

    ENDPOINTS = {
        "search_decisions": "api/v1/ptab/interferences/decisions/search",
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        config: Optional[USPTOConfig] = None,
    ):
        """Initialize the PTABInterferencesClient.

        Args:
            api_key: Optional API key for authentication.
            base_url: Optional base URL override for the API.
            config: Optional USPTOConfig instance for configuration.
        """
        self.config = config or USPTOConfig(api_key=api_key)
        api_key_to_use = api_key or self.config.api_key
        effective_base_url = (
            base_url or self.config.ptab_base_url or "https://api.uspto.gov"
        )
        super().__init__(
            api_key=api_key_to_use, base_url=effective_base_url, config=self.config
        )

    def search_decisions(
        self,
        query: Optional[str] = None,
        sort: Optional[str] = None,
        offset: Optional[int] = 0,
        limit: Optional[int] = 25,
        facets: Optional[str] = None,
        fields: Optional[str] = None,
        filters: Optional[str] = None,
        range_filters: Optional[str] = None,
        post_body: Optional[Dict[str, Any]] = None,
        # Convenience query parameters
        interference_number_q: Optional[str] = None,
        senior_party_application_number_q: Optional[str] = None,
        junior_party_application_number_q: Optional[str] = None,
        senior_party_name_q: Optional[str] = None,
        junior_party_name_q: Optional[str] = None,
        interference_outcome_category_q: Optional[str] = None,
        decision_type_category_q: Optional[str] = None,
        decision_date_from_q: Optional[str] = None,
        decision_date_to_q: Optional[str] = None,
        additional_query_params: Optional[Dict[str, Any]] = None,
    ) -> PTABInterferenceResponse:
        """Searches for PTAB interference decisions.

        This method can perform either a GET request using query parameters or a POST
        request if post_body is specified. When using GET, you can provide either a
        direct query string or use convenience parameters that will be automatically
        combined into a query.

        Args:
            query: Direct query string in USPTO search syntax.
            sort: Sort order for results.
            offset: Number of records to skip (pagination).
            limit: Maximum number of records to return.
            facets: Facet configuration string.
            fields: Specific fields to return.
            filters: Filter configuration string.
            range_filters: Range filter configuration string.
            post_body: Optional POST body for complex queries.
            interference_number_q: Filter by interference number.
            senior_party_application_number_q: Filter by senior party application number.
            junior_party_application_number_q: Filter by junior party application number.
            senior_party_name_q: Filter by senior party name.
            junior_party_name_q: Filter by junior party name.
            interference_outcome_category_q: Filter by interference outcome category.
            decision_type_category_q: Filter by decision type category.
            decision_date_from_q: Filter decisions from this date (YYYY-MM-DD).
            decision_date_to_q: Filter decisions to this date (YYYY-MM-DD).
            additional_query_params: Additional custom query parameters.

        Returns:
            PTABInterferenceResponse: Response containing matching interference decisions.

        Examples:
            # Search with direct query
            >>> response = client.search_decisions(query="interferenceNumber:106123")

            # Search with convenience parameters
            >>> response = client.search_decisions(
            ...     interference_outcome_category_q="Priority to Senior Party",
            ...     decision_date_from_q="2020-01-01",
            ...     limit=50
            ... )

            # Search with POST body
            >>> response = client.search_decisions(
            ...     post_body={"q": "decisionTypeCategory:Final Decision", "limit": 100}
            ... )
        """
        endpoint = self.ENDPOINTS["search_decisions"]

        if post_body is not None:
            # POST request path
            result = self._make_request(
                method="POST",
                endpoint=endpoint,
                json_data=post_body,
                params=additional_query_params,
                response_class=PTABInterferenceResponse,
            )
        else:
            # GET request path
            params: Dict[str, Any] = {}
            final_q = query

            # Build query from convenience parameters
            if final_q is None:
                q_parts = []
                if interference_number_q:
                    q_parts.append(f"interferenceNumber:{interference_number_q}")
                if senior_party_application_number_q:
                    q_parts.append(
                        f"seniorPartyApplicationNumber:{senior_party_application_number_q}"
                    )
                if junior_party_application_number_q:
                    q_parts.append(
                        f"juniorPartyApplicationNumber:{junior_party_application_number_q}"
                    )
                if senior_party_name_q:
                    q_parts.append(f"seniorPartyName:{senior_party_name_q}")
                if junior_party_name_q:
                    q_parts.append(f"juniorPartyName:{junior_party_name_q}")
                if interference_outcome_category_q:
                    q_parts.append(
                        f"interferenceOutcomeCategory:{interference_outcome_category_q}"
                    )
                if decision_type_category_q:
                    q_parts.append(f"decisionTypeCategory:{decision_type_category_q}")

                # Handle decision date range
                if decision_date_from_q and decision_date_to_q:
                    q_parts.append(
                        f"decisionDate:[{decision_date_from_q} TO {decision_date_to_q}]"
                    )
                elif decision_date_from_q:
                    q_parts.append(f"decisionDate:>={decision_date_from_q}")
                elif decision_date_to_q:
                    q_parts.append(f"decisionDate:<={decision_date_to_q}")

                if q_parts:
                    final_q = " AND ".join(q_parts)

            # Add parameters
            if final_q is not None:
                params["q"] = final_q
            if sort is not None:
                params["sort"] = sort
            if offset is not None:
                params["offset"] = offset
            if limit is not None:
                params["limit"] = limit
            if facets is not None:
                params["facets"] = facets
            if fields is not None:
                params["fields"] = fields
            if filters is not None:
                params["filters"] = filters
            if range_filters is not None:
                params["rangeFilters"] = range_filters

            if additional_query_params:
                params.update(additional_query_params)

            result = self._make_request(
                method="GET",
                endpoint=endpoint,
                params=params,
                response_class=PTABInterferenceResponse,
            )

        assert isinstance(result, PTABInterferenceResponse)
        return result

    def paginate_decisions(self, **kwargs: Any) -> Iterator[PTABInterferenceDecision]:
        """Provides an iterator to paginate through interference decision search results.

        This method simplifies fetching all interference decisions matching a search query
        by automatically handling pagination. It internally calls the search_decisions
        method for GET requests, batching results and yielding them one by one.

        All keyword arguments are passed directly to search_decisions to define the
        search criteria. The offset and limit parameters are managed by the pagination
        logic; setting them directly in kwargs might lead to unexpected behavior.

        Args:
            **kwargs: Keyword arguments passed to search_decisions for constructing
                the search query. Do not include post_body.

        Returns:
            Iterator[PTABInterferenceDecision]: An iterator yielding PTABInterferenceDecision
                objects, allowing iteration over all matching decisions across multiple pages
                of results.

        Raises:
            ValueError: If post_body is included in kwargs, as this method only
                supports GET request parameters for pagination.

        Examples:
            # Paginate through all interference decisions
            >>> for decision in client.paginate_decisions():
            ...     print(f"{decision.interference_meta_data.interference_number}: "
            ...           f"{decision.document_data.interference_outcome_category}")

            # Paginate with date range
            >>> for decision in client.paginate_decisions(
            ...     decision_date_from_q="2020-01-01",
            ...     decision_date_to_q="2023-12-31"
            ... ):
            ...     process_decision(decision)
        """
        if "post_body" in kwargs:
            raise ValueError(
                "paginate_decisions uses GET requests and does not support 'post_body'. "
                "Use keyword arguments for search criteria."
            )

        return self.paginate_results(
            method_name="search_decisions",
            response_container_attr="patent_interference_data_bag",
            **kwargs,
        )
