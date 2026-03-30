"""clients.oa_actions - Client for USPTO Office Action Text Retrieval API.

This module provides a client for interacting with the USPTO Office Action
Text Retrieval API (v1). It allows users to search for full-text office action
documents issued during patent examination, including body text and structured
section data for rejections and allowances.
"""

from collections.abc import Iterator
from typing import Any

from pyUSPTO.clients.base import BaseUSPTOClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.oa_actions import (
    OAActionsFieldsResponse,
    OAActionsRecord,
    OAActionsResponse,
)


class OAActionsClient(BaseUSPTOClient[OAActionsResponse]):
    """Client for interacting with the USPTO Office Action Text Retrieval API.

    This client provides methods to search for full-text office action documents.
    The API refreshes daily and contains publicly available Office Actions starting
    with 12 series applications.
    """

    ENDPOINTS = {
        "search": "api/v1/patent/oa/oa_actions/v1/records",
        "get_fields": "api/v1/patent/oa/oa_actions/v1/fields",
    }

    def __init__(
        self,
        config: USPTOConfig | None = None,
        base_url: str | None = None,
    ):
        """Initialize the OAActionsClient.

        Args:
            config: USPTOConfig instance containing API key and settings. If not provided,
                creates config from environment variables (requires USPTO_API_KEY).
            base_url: Optional base URL override for the USPTO OA Actions API.
                If not provided, uses config.oa_actions_base_url or default.
        """
        if config is None:
            self.config = USPTOConfig.from_env()
        else:
            self.config = config

        effective_base_url = base_url or self.config.oa_actions_base_url

        super().__init__(base_url=effective_base_url, config=self.config)

    def search(
        self,
        criteria: str | None = None,
        sort: str | None = None,
        start: int | None = 0,
        rows: int | None = 25,
        post_body: dict[str, Any] | None = None,
        # Convenience query parameters
        patent_application_number_q: str | None = None,
        legacy_document_code_identifier_q: str | None = None,
        group_art_unit_number_q: str | int | None = None,
        tech_center_q: str | None = None,
        access_level_category_q: str | None = None,
        application_type_category_q: str | None = None,
        submission_date_from_q: str | None = None,
        submission_date_to_q: str | None = None,
        additional_query_params: dict[str, Any] | None = None,
    ) -> OAActionsResponse:
        """Return office action records matching the given criteria.

        This method performs a POST request (form-urlencoded) to search for
        office action documents. You can provide either a direct post_body,
        a criteria string, or use convenience parameters.

        Args:
            criteria: Direct Solr query string (e.g., ``"patentApplicationNumber:14485382"``).
            sort: Sort order for results (e.g., ``"submissionDate desc"``).
            start: Starting index for pagination (default: 0).
            rows: Maximum number of records to return (default: 25).
            post_body: Optional POST body dict for complex queries. When provided,
                all other parameters are ignored.
            patent_application_number_q: Filter by patent application number.
            legacy_document_code_identifier_q: Filter by document code (e.g., ``"CTNF"``, ``"NOA"``).
            group_art_unit_number_q: Filter by group art unit number.
            tech_center_q: Filter by technology center code.
            access_level_category_q: Filter by access level (e.g., ``"PUBLIC"``).
            application_type_category_q: Filter by application type (e.g., ``"REGULAR"``).
            submission_date_from_q: Filter from this submission date (``"YYYY-MM-DD"``).
            submission_date_to_q: Filter to this submission date (``"YYYY-MM-DD"``).
            additional_query_params: Additional custom POST body parameters.

        Returns:
            OAActionsResponse: Response containing matching office action records.

        Examples:
            # Search with a direct criteria string
            >>> response = client.search(
            ...     criteria="patentApplicationNumber:14485382"
            ... )

            # Search with convenience parameters
            >>> response = client.search(
            ...     tech_center_q="1700",
            ...     legacy_document_code_identifier_q="CTNF",
            ...     rows=50,
            ... )

            # Search with POST body
            >>> response = client.search(
            ...     post_body={"criteria": "techCenter:1700", "rows": 100}
            ... )
        """
        endpoint = self.ENDPOINTS["search"]

        if post_body is not None:
            return self._get_model(
                method="POST",
                endpoint=endpoint,
                response_class=OAActionsResponse,
                json_data=post_body,
                params=additional_query_params,
            )

        # Build POST body from parameters
        body: dict[str, Any] = {}

        # Build criteria from convenience parameters
        final_criteria = criteria
        if final_criteria is None:
            q_parts = []
            if patent_application_number_q:
                q_parts.append(f"patentApplicationNumber:{patent_application_number_q}")
            if legacy_document_code_identifier_q:
                q_parts.append(
                    f"legacyDocumentCodeIdentifier:{legacy_document_code_identifier_q}"
                )
            if group_art_unit_number_q is not None:
                q_parts.append(f"groupArtUnitNumber:{group_art_unit_number_q}")
            if tech_center_q:
                q_parts.append(f"techCenter:{tech_center_q}")
            if access_level_category_q:
                q_parts.append(f"accessLevelCategory:{access_level_category_q}")
            if application_type_category_q:
                q_parts.append(f"applicationTypeCategory:{application_type_category_q}")

            if submission_date_from_q and submission_date_to_q:
                q_parts.append(
                    f"submissionDate:[{submission_date_from_q} TO {submission_date_to_q}]"
                )
            elif submission_date_from_q:
                q_parts.append(f"submissionDate:>={submission_date_from_q}")
            elif submission_date_to_q:
                q_parts.append(f"submissionDate:<={submission_date_to_q}")

            if q_parts:
                final_criteria = " AND ".join(q_parts)

        if final_criteria is not None:
            body["criteria"] = final_criteria
        if sort is not None:
            body["sort"] = sort
        if start is not None:
            body["start"] = start
        if rows is not None:
            body["rows"] = rows

        if additional_query_params:
            body.update(additional_query_params)

        return self._get_model(
            method="POST",
            endpoint=endpoint,
            response_class=OAActionsResponse,
            json_data=body,
        )

    def get_fields(self) -> OAActionsFieldsResponse:
        """Retrieve available fields and API metadata for the OA Actions API.

        Returns:
            OAActionsFieldsResponse: API metadata including available field
                names and last data update timestamp.

        Examples:
            >>> fields_response = client.get_fields()
            >>> print(fields_response.field_count)
            56
            >>> print(fields_response.api_status)
            'PUBLISHED'
        """
        endpoint = self.ENDPOINTS["get_fields"]
        return self._get_model(
            method="GET",
            endpoint=endpoint,
            response_class=OAActionsFieldsResponse,
        )

    def paginate(
        self, post_body: dict[str, Any] | None = None, **kwargs: Any
    ) -> Iterator[OAActionsRecord]:
        """Provide an iterator to paginate through office action search results.

        Automatically handles pagination using Solr-style start/rows parameters.
        The ``start`` parameter is managed internally; providing it will raise a ValueError.

        Args:
            post_body: Optional POST body dict for complex search queries.
            **kwargs: Keyword arguments passed to :meth:`search`.

        Returns:
            Iterator[OAActionsRecord]: An iterator yielding OAActionsRecord objects.

        Examples:
            # Paginate through all CTNF actions in tech center 1700
            >>> for record in client.paginate(
            ...     tech_center_q="1700",
            ...     legacy_document_code_identifier_q="CTNF",
            ...     rows=50,
            ... ):
            ...     print(record.patent_application_number)

            # Paginate with POST body
            >>> for record in client.paginate(
            ...     post_body={"criteria": "techCenter:1700", "rows": 50}
            ... ):
            ...     process(record)
        """
        return self.paginate_solr_results(
            method_name="search",
            response_container_attr="docs",
            post_body=post_body,
            **kwargs,
        )
