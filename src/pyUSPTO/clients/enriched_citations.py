"""clients.enriched_citations - Client for USPTO Enriched Citations API.

This module provides a client for interacting with the USPTO Enriched Cited
Reference Metadata API (v3). It allows users to search for enriched citation
data extracted from patent office actions using AI/NLP algorithms.
"""

from collections.abc import Iterator
from typing import Any

from pyUSPTO.clients.base import BaseUSPTOClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.enriched_citations import (
    EnrichedCitation,
    EnrichedCitationFieldsResponse,
    EnrichedCitationResponse,
)


class EnrichedCitationsClient(BaseUSPTOClient[EnrichedCitationResponse]):
    """Client for interacting with the USPTO Enriched Citations API.

    This client provides methods to search for enriched citation data from
    office actions mailed from October 1, 2017 to 30 days prior to the current
    date. The data is extracted using AI/NLP algorithms and includes bibliographic
    information, rejected claims, and passage locations from cited prior art.
    """

    ENDPOINTS = {
        "search_citations": "api/v1/patent/oa/enriched_cited_reference_metadata/v3/records",
        "get_fields": "api/v1/patent/oa/enriched_cited_reference_metadata/v3/fields",
    }

    def __init__(
        self,
        config: USPTOConfig | None = None,
        base_url: str | None = None,
    ):
        """Initialize the EnrichedCitationsClient.

        Args:
            config: USPTOConfig instance containing API key and settings. If not provided,
                creates config from environment variables (requires USPTO_API_KEY).
            base_url: Optional base URL override for the USPTO Enriched Citations API.
                If not provided, uses config.enriched_citations_base_url or default.
        """
        # Use provided config or create from environment
        if config is None:
            self.config = USPTOConfig.from_env()
        else:
            self.config = config

        # Determine effective base URL
        effective_base_url = base_url or self.config.enriched_citations_base_url

        # Initialize base client
        super().__init__(
            base_url=effective_base_url,
            config=self.config,
        )

    def search_citations(
        self,
        query: str | None = None,
        sort: str | None = None,
        offset: int | None = 0,
        limit: int | None = 25,
        post_body: dict[str, Any] | None = None,
        # Convenience query parameters
        patent_application_number_q: str | None = None,
        cited_document_identifier_q: str | None = None,
        office_action_category_q: str | None = None,
        citation_category_code_q: str | None = None,
        tech_center_q: str | None = None,
        group_art_unit_number_q: str | None = None,
        examiner_cited_q: bool | None = None,
        office_action_date_from_q: str | None = None,
        office_action_date_to_q: str | None = None,
        additional_query_params: dict[str, Any] | None = None,
    ) -> EnrichedCitationResponse:
        """Return enriched citations matching the given criteria.

        This method performs a POST request to search for enriched citation records.
        You can provide either a direct post_body, a query string, or use convenience
        parameters that will be automatically combined into a query.

        Args:
            query: Direct query string in USPTO search syntax.
            sort: Sort order for results.
            offset: Number of records to skip (pagination).
            limit: Maximum number of records to return.
            post_body: Optional POST body for complex queries. When provided,
                all other parameters are ignored.
            patent_application_number_q: Filter by patent application number.
            cited_document_identifier_q: Filter by cited document identifier.
            office_action_category_q: Filter by office action category (e.g., "CTNF").
            citation_category_code_q: Filter by citation category code (e.g., "X", "Y").
            tech_center_q: Filter by technology center code.
            group_art_unit_number_q: Filter by group art unit number.
            examiner_cited_q: Filter by whether the examiner cited the reference.
            office_action_date_from_q: Filter from this date (YYYY-MM-DD).
            office_action_date_to_q: Filter to this date (YYYY-MM-DD).
            additional_query_params: Additional custom query parameters.

        Returns:
            EnrichedCitationResponse: Response containing matching enriched citations.

        Examples:
            # Search with direct query
            >>> response = client.search_citations(
            ...     query="patentApplicationNumber:15739603"
            ... )

            # Search with convenience parameters
            >>> response = client.search_citations(
            ...     tech_center_q="2800",
            ...     citation_category_code_q="X",
            ...     limit=50,
            ... )

            # Search with POST body
            >>> response = client.search_citations(
            ...     post_body={"q": "techCenter:2800", "rows": 100}
            ... )
        """
        endpoint = self.ENDPOINTS["search_citations"]

        if post_body is not None:
            # POST request with user-provided body
            return self._get_model(
                method="POST",
                endpoint=endpoint,
                response_class=EnrichedCitationResponse,
                json_data=post_body,
                params=additional_query_params,
            )

        # Build POST body from parameters
        body: dict[str, Any] = {}

        # Build query from convenience parameters
        final_q = query
        if final_q is None:
            q_parts = []
            if patent_application_number_q:
                q_parts.append(f"patentApplicationNumber:{patent_application_number_q}")
            if cited_document_identifier_q:
                v = (
                    f'"{cited_document_identifier_q}"'
                    if " " in cited_document_identifier_q
                    else cited_document_identifier_q
                )
                q_parts.append(f"citedDocumentIdentifier:{v}")
            if office_action_category_q:
                q_parts.append(f"officeActionCategory:{office_action_category_q}")
            if citation_category_code_q:
                q_parts.append(f"citationCategoryCode:{citation_category_code_q}")
            if tech_center_q:
                q_parts.append(f"techCenter:{tech_center_q}")
            if group_art_unit_number_q:
                q_parts.append(f"groupArtUnitNumber:{group_art_unit_number_q}")
            if examiner_cited_q is not None:
                q_parts.append(
                    f"examinerCitedReferenceIndicator:{str(examiner_cited_q).lower()}"
                )

            # Handle office action date range
            if office_action_date_from_q and office_action_date_to_q:
                q_parts.append(
                    f"officeActionDate:[{office_action_date_from_q} TO {office_action_date_to_q}]"
                )
            elif office_action_date_from_q:
                q_parts.append(f"officeActionDate:>={office_action_date_from_q}")
            elif office_action_date_to_q:
                q_parts.append(f"officeActionDate:<={office_action_date_to_q}")

            if q_parts:
                final_q = " AND ".join(q_parts)

        if final_q is not None:
            body["q"] = final_q
        if sort is not None:
            body["sort"] = sort
        if offset is not None:
            body["offset"] = offset
        if limit is not None:
            body["limit"] = limit

        if additional_query_params:
            body.update(additional_query_params)

        return self._get_model(
            method="POST",
            endpoint=endpoint,
            response_class=EnrichedCitationResponse,
            json_data=body,
        )

    def get_fields(self) -> EnrichedCitationFieldsResponse:
        """Retrieve available fields and API metadata for the Enriched Citations API.

        Returns:
            EnrichedCitationFieldsResponse: API metadata including available field
                names and last data update timestamp.

        Examples:
            >>> fields_response = client.get_fields()
            >>> print(fields_response.fields)
            ['officeActionDate', 'relatedClaimNumberText', ...]
            >>> print(fields_response.last_data_updated_date)
            '2024-07-11 11:33:41.0'
        """
        endpoint = self.ENDPOINTS["get_fields"]
        return self._get_model(
            method="GET",
            endpoint=endpoint,
            response_class=EnrichedCitationFieldsResponse,
        )

    def paginate_citations(
        self, post_body: dict[str, Any] | None = None, **kwargs: Any
    ) -> Iterator[EnrichedCitation]:
        """Provide an iterator to paginate through enriched citation search results.

        This method simplifies fetching all enriched citations matching a search query
        by automatically handling pagination.

        The offset parameter is managed by the pagination logic; setting it directly
        in kwargs or post_body will raise a ValueError.

        Args:
            post_body: Optional POST body for complex search queries.
            **kwargs: Keyword arguments passed to search_citations.

        Returns:
            Iterator[EnrichedCitation]: An iterator yielding EnrichedCitation objects.

        Examples:
            # Paginate through all citations for a tech center
            >>> for citation in client.paginate_citations(tech_center_q="2800"):
            ...     print(f"{citation.patent_application_number}: {citation.citation_category_code}")

            # Paginate with POST body
            >>> for citation in client.paginate_citations(
            ...     post_body={"q": "techCenter:2800", "limit": 50}
            ... ):
            ...     process_citation(citation)
        """
        return self.paginate_results(
            method_name="search_citations",
            response_container_attr="docs",
            post_body=post_body,
            **kwargs,
        )
