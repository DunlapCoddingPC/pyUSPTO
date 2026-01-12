"""clients.ptab_appeals - Client for USPTO PTAB Appeals API.

This module provides a client for interacting with the USPTO PTAB (Patent Trial
and Appeal Board) Appeals API. It allows you to search for ex parte appeal decisions.
"""

from collections.abc import Iterator
from typing import Any

from pyUSPTO.clients.base import BaseUSPTOClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.ptab import (
    AppealDocumentData,
    AppealMetaData,
    PTABAppealDecision,
    PTABAppealResponse,
)


class PTABAppealsClient(BaseUSPTOClient[PTABAppealResponse]):
    """Client for interacting with the USPTO PTAB Appeals API.

    This client provides methods to search for ex parte appeal decisions from the
    Patent Trial and Appeal Board.

    Appeals data includes decisions on patent application appeals from the examiner
    to the PTAB.
    """

    ENDPOINTS = {
        "search_decisions": "api/v1/patent/appeals/decisions/search",
    }

    def __init__(
        self,
        config: USPTOConfig | None = None,
        base_url: str | None = None,
    ):
        """Initialize the PTABAppealsClient.

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
        appeal_number_q: str | None = None,
        application_number_text_q: str | None = None,
        appellant_name_q: str | None = None,
        requestor_name_q: str | None = None,
        decision_type_category_q: str | None = None,
        decision_date_from_q: str | None = None,
        decision_date_to_q: str | None = None,
        technology_center_number_q: str | None = None,
        additional_query_params: dict[str, Any] | None = None,
    ) -> PTABAppealResponse:
        """Search for PTAB appeal decisions.

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
            appeal_number_q: Filter by appeal number.
            application_number_text_q: Filter by application number.
            appellant_name_q: Filter by appellant name.
            requestor_name_q: Filter by requestor name.
            decision_type_category_q: Filter by decision type category.
            decision_date_from_q: Filter decisions from this date (YYYY-MM-DD).
            decision_date_to_q: Filter decisions to this date (YYYY-MM-DD).
            technology_center_number_q: Filter by technology center number.
            additional_query_params: Additional custom query parameters.

        Returns:
            PTABAppealResponse: Response containing matching appeal decisions.

        Examples:
            # Search with direct query
            >>> response = client.search_decisions(query="appealNumber:2023-001234")

            # Search with convenience parameters
            >>> response = client.search_decisions(
            ...     technology_center_number_q="3600",
            ...     decision_date_from_q="2023-01-01",
            ...     limit=50
            ... )

            # Search with POST body
            >>> response = client.search_decisions(
            ...     post_body={"q": "decisionTypeCategory:Affirmed", "limit": 100}
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
                response_class=PTABAppealResponse,
            )
        else:
            # GET request path
            params: dict[str, Any] = {}
            final_q = query

            # Build query from convenience parameters
            if final_q is None:
                q_parts = []
                if appeal_number_q:
                    q_parts.append(f"appealNumber:{appeal_number_q}")
                if application_number_text_q:
                    q_parts.append(
                        f"appellantData.applicationNumberText:{application_number_text_q}"
                    )
                if appellant_name_q:
                    q_parts.append(
                        f"appellantData.realPartyInInterestName:{appellant_name_q}"
                    )
                if requestor_name_q:
                    q_parts.append(f"appellantData.counselName:{requestor_name_q}")
                if decision_type_category_q:
                    q_parts.append(
                        f"decisionData.decisionTypeCategory:{decision_type_category_q}"
                    )
                if technology_center_number_q:
                    q_parts.append(
                        f"appellantData.technologyCenterNumber:{technology_center_number_q}"
                    )

                # Handle decision date range
                if decision_date_from_q and decision_date_to_q:
                    q_parts.append(
                        f"decisionData.decisionIssueDate:[{decision_date_from_q} TO {decision_date_to_q}]"
                    )
                elif decision_date_from_q:
                    q_parts.append(
                        f"decisionData.decisionIssueDate:>={decision_date_from_q}"
                    )
                elif decision_date_to_q:
                    q_parts.append(
                        f"decisionData.decisionIssueDate:<={decision_date_to_q}"
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
                response_class=PTABAppealResponse,
            )

        assert isinstance(result, PTABAppealResponse)
        return result

    def paginate_decisions(
        self, post_body: dict[str, Any] | None = None, **kwargs: Any
    ) -> Iterator[PTABAppealDecision]:
        """Provide an iterator to paginate through appeal decision search results.

        This method simplifies fetching all appeal decisions matching a search query
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
            Iterator[PTABAppealDecision]: An iterator yielding PTABAppealDecision objects,
                allowing iteration over all matching decisions across multiple pages of results.

        Examples:
            # GET-based pagination with convenience parameters
            >>> for decision in client.paginate_decisions(technology_center_number_q="3600"):
            ...     print(f"{decision.appeal_meta_data.appeal_number}: "
            ...           f"{decision.decision_data.decision_type_category}")

            # GET-based pagination with date range and custom limit
            >>> for decision in client.paginate_decisions(
            ...     decision_date_from_q="2023-01-01",
            ...     decision_date_to_q="2023-12-31",
            ...     limit=50
            ... ):
            ...     process_decision(decision)

            # POST-based pagination
            >>> for decision in client.paginate_decisions(
            ...     post_body={"q": "decisionTypeCategory:Affirmed", "limit": 100}
            ... ):
            ...     process_decision(decision)
        """
        return self.paginate_results(
            method_name="search_decisions",
            response_container_attr="patent_appeal_data_bag",
            post_body=post_body,
            **kwargs,
        )

    def download_appeal_archive(
        self,
        appeal_meta_data: AppealMetaData,
        destination: str | None = None,
        file_name: str | None = None,
        overwrite: bool = False,
    ) -> str:
        """Download appeal archive (ZIP/TAR) without extraction.

        Args:
            appeal_meta_data: AppealMetaData with file_download_uri
            destination: Directory to save to
            file_name: Override filename
            overwrite: Overwrite existing file

        Returns:
            Path to downloaded archive file

        Raises:
            ValueError: If appeal_meta_data has no file_download_uri
        """
        if not appeal_meta_data.file_download_uri:
            raise ValueError("AppealMetaData has no file_download_uri")

        return self._download_file(
            url=appeal_meta_data.file_download_uri,
            destination=destination,
            file_name=file_name,
            overwrite=overwrite,
        )

    def download_appeal_documents(
        self,
        appeal_meta_data: AppealMetaData,
        destination: str | None = None,
        overwrite: bool = False,
    ) -> str:
        """Download and extract all appeal documents.

        Args:
            appeal_meta_data: AppealMetaData with file_download_uri
            destination: Directory to save/extract to
            overwrite: Overwrite existing files

        Returns:
            Path to extraction directory

        Raises:
            ValueError: If appeal_meta_data has no file_download_uri
        """
        if not appeal_meta_data.file_download_uri:
            raise ValueError("AppealMetaData has no file_download_uri")

        return self._download_and_extract(
            url=appeal_meta_data.file_download_uri,
            destination=destination,
            overwrite=overwrite,
        )

    def download_appeal_document(
        self,
        document_data: AppealDocumentData,
        destination: str | None = None,
        file_name: str | None = None,
        overwrite: bool = False,
    ) -> str:
        """Download individual appeal document (auto-extracts if needed).

        Args:
            document_data: AppealDocumentData with file_download_uri
            destination: Directory to save to
            file_name: Override filename
            overwrite: Overwrite existing file

        Returns:
            Path to downloaded file

        Raises:
            ValueError: If document_data has no file_download_uri
        """
        if not document_data.file_download_uri:
            raise ValueError("AppealDocumentData has no file_download_uri")

        return self._download_and_extract(
            url=document_data.file_download_uri,
            destination=destination,
            file_name=file_name,
            overwrite=overwrite,
        )
