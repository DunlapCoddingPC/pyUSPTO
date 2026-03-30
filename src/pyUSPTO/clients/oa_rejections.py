"""clients.oa_rejections - Client for USPTO Office Action Rejections API.

This module provides a client for interacting with the USPTO Office Action
Rejections API (v2). It allows users to search for rejection-level data from
Office Actions mailed from October 1, 2017 to 30 days prior to the current
date, including rejection type indicators, claim arrays, and examiner metadata.
"""

from collections.abc import Iterator
from typing import Any

from pyUSPTO.clients.base import BaseUSPTOClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.oa_rejections import (
    OARejectionsFieldsResponse,
    OARejectionsRecord,
    OARejectionsResponse,
)


class OARejectionsClient(BaseUSPTOClient[OARejectionsResponse]):
    """Client for interacting with the USPTO Office Action Rejections API.

    This client provides methods to search for rejection data from Office
    Actions. The API refreshes daily and contains publicly available data
    starting with 12 series applications.
    """

    ENDPOINTS = {
        "search": "api/v1/patent/oa/oa_rejections/v2/records",
        "get_fields": "api/v1/patent/oa/oa_rejections/v2/fields",
    }

    def __init__(
        self,
        config: USPTOConfig | None = None,
        base_url: str | None = None,
    ):
        """Initialize the OARejectionsClient.

        Args:
            config: USPTOConfig instance containing API key and settings. If not provided,
                creates config from environment variables (requires USPTO_API_KEY).
            base_url: Optional base URL override for the USPTO OA Rejections API.
                If not provided, uses config.oa_rejections_base_url or default.
        """
        if config is None:
            self.config = USPTOConfig.from_env()
        else:
            self.config = config

        effective_base_url = base_url or self.config.oa_rejections_base_url

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
        group_art_unit_number_q: str | None = None,
        legal_section_code_q: str | None = None,
        action_type_category_q: str | None = None,
        submission_date_from_q: str | None = None,
        submission_date_to_q: str | None = None,
        additional_query_params: dict[str, Any] | None = None,
    ) -> OARejectionsResponse:
        """Return rejection records matching the given criteria.

        This method performs a POST request (form-urlencoded) to search for
        office action rejection records. You can provide either a direct
        post_body, a criteria string, or use convenience parameters.

        Args:
            criteria: Direct Solr query string (e.g., ``"patentApplicationNumber:12190351"``).
            sort: Sort order for results (e.g., ``"submissionDate desc"``).
            start: Starting index for pagination (default: 0).
            rows: Maximum number of records to return (default: 25).
            post_body: Optional POST body dict for complex queries. When provided,
                all other parameters are ignored.
            patent_application_number_q: Filter by patent application number.
            legacy_document_code_identifier_q: Filter by document code (e.g., ``"CTNF"``).
            group_art_unit_number_q: Filter by group art unit number.
            legal_section_code_q: Filter by legal section code.
            action_type_category_q: Filter by action type category.
            submission_date_from_q: Filter from this submission date (``"YYYY-MM-DD"``).
            submission_date_to_q: Filter to this submission date (``"YYYY-MM-DD"``).
            additional_query_params: Additional custom POST body parameters.

        Returns:
            OARejectionsResponse: Response containing matching rejection records.

        Examples:
            # Search with a direct criteria string
            >>> response = client.search(
            ...     criteria="patentApplicationNumber:12190351"
            ... )

            # Search with convenience parameters
            >>> response = client.search(
            ...     legacy_document_code_identifier_q="CTNF",
            ...     submission_date_from_q="2020-01-01",
            ...     rows=50,
            ... )

            # Search with POST body
            >>> response = client.search(
            ...     post_body={"criteria": "hasRej103:1", "rows": 100}
            ... )
        """
        endpoint = self.ENDPOINTS["search"]

        if post_body is not None:
            return self._get_model(
                method="POST",
                endpoint=endpoint,
                response_class=OARejectionsResponse,
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
            if group_art_unit_number_q:
                q_parts.append(f"groupArtUnitNumber:{group_art_unit_number_q}")
            if legal_section_code_q:
                q_parts.append(f"legalSectionCode:{legal_section_code_q}")
            if action_type_category_q:
                q_parts.append(f"actionTypeCategory:{action_type_category_q}")

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
            response_class=OARejectionsResponse,
            json_data=body,
        )

    def get_fields(self) -> OARejectionsFieldsResponse:
        """Retrieve available fields and API metadata for the OA Rejections API.

        Returns:
            OARejectionsFieldsResponse: API metadata including available field
                names and last data update timestamp.

        Examples:
            >>> fields_response = client.get_fields()
            >>> print(fields_response.field_count)
            31
            >>> print(fields_response.api_status)
            'PUBLISHED'
        """
        endpoint = self.ENDPOINTS["get_fields"]
        return self._get_model(
            method="GET",
            endpoint=endpoint,
            response_class=OARejectionsFieldsResponse,
        )

    def paginate(
        self, post_body: dict[str, Any] | None = None, **kwargs: Any
    ) -> Iterator[OARejectionsRecord]:
        """Provide an iterator to paginate through rejection search results.

        Automatically handles pagination using Solr-style start/rows parameters.
        The ``start`` parameter is managed internally; providing it will raise a ValueError.

        Args:
            post_body: Optional POST body dict for complex search queries.
            **kwargs: Keyword arguments passed to :meth:`search`.

        Returns:
            Iterator[OARejectionsRecord]: An iterator yielding OARejectionsRecord objects.

        Examples:
            # Paginate through all CTNF rejections
            >>> for record in client.paginate(
            ...     legacy_document_code_identifier_q="CTNF",
            ...     rows=50,
            ... ):
            ...     print(record.patent_application_number)

            # Paginate with POST body
            >>> for record in client.paginate(
            ...     post_body={"criteria": "hasRej103:1", "rows": 50}
            ... ):
            ...     process(record)
        """
        return self.paginate_solr_results(
            method_name="search",
            response_container_attr="docs",
            post_body=post_body,
            **kwargs,
        )
