"""clients.ptab_interferences - Client for USPTO PTAB Interferences API.

This module provides a client for interacting with the USPTO PTAB (Patent Trial
and Appeal Board) Interferences API. It allows you to search for patent interference decisions.
"""

from collections.abc import Iterator
from typing import Any

from pyUSPTO.clients.base import BaseUSPTOClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.ptab import (
    InterferenceDocumentData,
    InterferenceMetaData,
    PTABInterferenceDecision,
    PTABInterferenceResponse,
)


class PTABInterferencesClient(BaseUSPTOClient[PTABInterferenceResponse]):
    """Client for interacting with the USPTO PTAB Interferences API.

    This client provides methods to search for patent interference decisions from the
    Patent Trial and Appeal Board.

    Interference proceedings are used to determine priority of invention when two or
    more parties claim the same patentable invention.
    """

    ENDPOINTS = {
        "search_decisions": "api/v1/patent/interferences/decisions/search",
    }

    def __init__(
        self,
        config: USPTOConfig | None = None,
        base_url: str | None = None,
    ):
        """Initialize the PTABInterferencesClient.

        Args:
            config: USPTOConfig instance containing API key and settings. If not provided,
                creates config from environment variables (requires USPTO_API_KEY).
            base_url: Optional base URL override for the USPTO PTAB API.
                If not provided, uses config.ptab_base_url or default.
        """
        # Use provided config or create from environment
        if config is None:
            self.config = USPTOConfig.from_env()
        else:
            self.config = config

        # Determine effective base URL
        effective_base_url = (
            base_url or self.config.ptab_base_url or "https://api.uspto.gov"
        )

        # Initialize base client
        super().__init__(
            base_url=effective_base_url,
            config=self.config,
        )

    def search_decisions(
        self,
        query: str | None = None,
        sort: str | None = None,
        offset: int | None = 0,
        limit: int | None = 25,
        facets: str | None = None,
        fields: str | None = None,
        filters: str | None = None,
        range_filters: str | None = None,
        post_body: dict[str, Any] | None = None,
        # Convenience query parameters
        interference_number_q: str | None = None,
        senior_party_application_number_q: str | None = None,
        junior_party_application_number_q: str | None = None,
        senior_party_name_q: str | None = None,
        junior_party_name_q: str | None = None,
        real_party_in_interest_q: str | None = None,
        interference_outcome_category_q: str | None = None,
        decision_type_category_q: str | None = None,
        decision_date_from_q: str | None = None,
        decision_date_to_q: str | None = None,
        additional_query_params: dict[str, Any] | None = None,
    ) -> PTABInterferenceResponse:
        """Search for PTAB interference decisions.

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
            real_party_in_interest_q: Filter by Real Party in Interest.
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
            params: dict[str, Any] = {}
            final_q = query

            # Build query from convenience parameters
            if final_q is None:
                q_parts = []
                if interference_number_q:
                    q_parts.append(f"interferenceNumber:{interference_number_q}")
                if senior_party_application_number_q:
                    q_parts.append(
                        f"seniorPartyData.applicationNumberText:{senior_party_application_number_q}"
                    )
                if junior_party_application_number_q:
                    q_parts.append(
                        f"juniorPartyData.applicationNumberText:{junior_party_application_number_q}"
                    )
                if senior_party_name_q:
                    q_parts.append(
                        f'seniorPartyData.patentOwnerName:"{senior_party_name_q}" OR seniorPartyData.inventorName:"{senior_party_name_q}" OR seniorPartyData.realPartyInInterestName:"{senior_party_name_q}"'
                    )
                if junior_party_name_q:
                    q_parts.append(
                        f'juniorPartyData.patentOwnerName:"{junior_party_name_q}" OR juniorPartyData.inventorName:"{junior_party_name_q}" OR juniorPartyData.realPartyInInterestName:"{junior_party_name_q}"'
                    )
                if real_party_in_interest_q:
                    q_parts.append(
                        f'seniorPartyData.realPartyInInterestName:"{real_party_in_interest_q}" OR juniorPartyData.realPartyInInterestName:"{real_party_in_interest_q}"'
                    )

                if interference_outcome_category_q:
                    q_parts.append(
                        f'documentData.interferenceOutcomeCategory:"{interference_outcome_category_q}"'
                    )
                if decision_type_category_q:
                    q_parts.append(
                        f'documentData.decisionTypeCategory:"{decision_type_category_q}"'
                    )

                # Handle decision date range
                if decision_date_from_q and decision_date_to_q:
                    q_parts.append(
                        f"documentData.decisionIssueDate:[{decision_date_from_q} TO {decision_date_to_q}]"
                    )
                elif decision_date_from_q:
                    q_parts.append(
                        f"documentData.decisionIssueDate:>={decision_date_from_q}"
                    )
                elif decision_date_to_q:
                    q_parts.append(
                        f"documentData.decisionIssueDate:<={decision_date_to_q}"
                    )

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

    def paginate_decisions(
        self, post_body: dict[str, Any] | None = None, **kwargs: Any
    ) -> Iterator[PTABInterferenceDecision]:
        """Provide an iterator to paginate through interference decision search results.

        This method simplifies fetching all interference decisions matching a search query
        by automatically handling pagination. It internally calls the search_decisions
        method, batching results and yielding them one by one.

        Supports both GET and POST requests. For POST requests, provide the
        search criteria in `post_body`. For GET requests, use keyword arguments.

        The offset parameter is managed by the pagination logic and should not be
        provided by the user. The limit parameter can be customized.

        Args:
            post_body: Optional POST body for complex search queries.
            **kwargs: Keyword arguments passed to search_decisions for constructing
                the search query (for GET-based pagination).

        Returns:
            Iterator[PTABInterferenceDecision]: An iterator yielding PTABInterferenceDecision
                objects, allowing iteration over all matching decisions across multiple pages
                of results.

        Examples:
            # GET-based pagination through all decisions
            >>> for decision in client.paginate_decisions():
            ...     print(f"{decision.interference_meta_data.interference_number}: "
            ...           f"{decision.document_data.interference_outcome_category}")

            # GET-based pagination with date range and custom limit
            >>> for decision in client.paginate_decisions(
            ...     decision_date_from_q="2020-01-01",
            ...     decision_date_to_q="2023-12-31",
            ...     limit=50
            ... ):
            ...     process_decision(decision)

            # POST-based pagination
            >>> for decision in client.paginate_decisions(
            ...     post_body={"q": "interferenceOutcomeCategory:Priority to Senior Party"}
            ... ):
            ...     process_decision(decision)
        """
        return self.paginate_results(
            method_name="search_decisions",
            response_container_attr="patent_interference_data_bag",
            post_body=post_body,
            **kwargs,
        )

    def download_interference_archive(
        self,
        interference_meta_data: InterferenceMetaData,
        destination: str | None = None,
        file_name: str | None = None,
        overwrite: bool = False,
    ) -> str:
        """Download interference archive (ZIP/TAR) without extraction.

        Args:
            interference_meta_data: InterferenceMetaData with file_download_uri
            destination: Directory to save to
            file_name: Override filename
            overwrite: Overwrite existing file

        Returns:
            Path to downloaded archive file

        Raises:
            ValueError: If interference_meta_data has no file_download_uri
        """
        if not interference_meta_data.file_download_uri:
            raise ValueError("InterferenceMetaData has no file_download_uri")

        return self._download_file(
            url=interference_meta_data.file_download_uri,
            destination=destination,
            file_name=file_name,
            overwrite=overwrite,
        )

    def download_interference_documents(
        self,
        interference_meta_data: InterferenceMetaData,
        destination: str | None = None,
        overwrite: bool = False,
    ) -> str:
        """Download and extract all interference documents.

        Args:
            interference_meta_data: InterferenceMetaData with file_download_uri
            destination: Directory to save/extract to
            overwrite: Overwrite existing files

        Returns:
            Path to extraction directory

        Raises:
            ValueError: If interference_meta_data has no file_download_uri
        """
        if not interference_meta_data.file_download_uri:
            raise ValueError("InterferenceMetaData has no file_download_uri")

        return self._download_and_extract(
            url=interference_meta_data.file_download_uri,
            destination=destination,
            overwrite=overwrite,
        )

    def download_interference_document(
        self,
        document_data: InterferenceDocumentData,
        destination: str | None = None,
        file_name: str | None = None,
        overwrite: bool = False,
    ) -> str:
        """Download individual interference document (auto-extracts if needed).

        Args:
            document_data: InterferenceDocumentData with file_download_uri
            destination: Directory to save to
            file_name: Override filename
            overwrite: Overwrite existing file

        Returns:
            Path to downloaded file

        Raises:
            ValueError: If document_data has no file_download_uri
        """
        if not document_data.file_download_uri:
            raise ValueError("InterferenceDocumentData has no file_download_uri")

        return self._download_and_extract(
            url=document_data.file_download_uri,
            destination=destination,
            file_name=file_name,
            overwrite=overwrite,
        )
