"""clients.oa_citations - Client for USPTO Office Action Citations API.

This module provides a client for interacting with the USPTO Office Action
Citations API (v2). It allows users to search citation data from Office Actions
mailed from October 1, 2017 to 30 days prior to the current date, derived from
Form PTO-892, Form PTO-1449, and Office Action text.
"""

from collections.abc import Iterator
from typing import Any

from pyUSPTO.clients.base import BaseUSPTOClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.oa_citations import (
    OACitationRecord,
    OACitationsFieldsResponse,
    OACitationsResponse,
)


class OACitationsClient(BaseUSPTOClient[OACitationsResponse]):
    """Client for interacting with the USPTO Office Action Citations API.

    This client provides methods to search for citation data referenced in
    Office Actions. The API refreshes daily and uses information derived from
    citations on Form PTO-892, Form PTO-1449, and Office Action text.
    """

    ENDPOINTS = {
        "search": "api/v1/patent/oa/oa_citations/v2/records",
        "get_fields": "api/v1/patent/oa/oa_citations/v2/fields",
    }

    def __init__(
        self,
        config: USPTOConfig | None = None,
        base_url: str | None = None,
    ):
        """Initialize the OACitationsClient.

        Args:
            config: USPTOConfig instance containing API key and settings. If not provided,
                creates config from environment variables (requires USPTO_API_KEY).
            base_url: Optional base URL override for the USPTO OA Citations API.
                If not provided, uses config.oa_citations_base_url or default.
        """
        if config is None:
            self.config = USPTOConfig.from_env()
        else:
            self.config = config

        effective_base_url = base_url or self.config.oa_citations_base_url

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
        legal_section_code_q: str | None = None,
        action_type_category_q: str | None = None,
        tech_center_q: str | None = None,
        work_group_q: str | None = None,
        group_art_unit_number_q: str | None = None,
        examiner_cited_reference_indicator_q: bool | None = None,
        applicant_cited_examiner_reference_indicator_q: bool | None = None,
        create_date_time_from_q: str | None = None,
        create_date_time_to_q: str | None = None,
        additional_query_params: dict[str, Any] | None = None,
    ) -> OACitationsResponse:
        """Return citation records matching the given criteria.

        This method performs a POST request (form-urlencoded) to search for
        Office Action citation records. You can provide either a direct post_body,
        a criteria string, or use convenience parameters.

        Args:
            criteria: Direct Solr query string (e.g., ``"patentApplicationNumber:16845502"``).
            sort: Sort order for results (e.g., ``"createDateTime desc"``).
            start: Starting index for pagination (default: 0).
            rows: Maximum number of records to return (default: 25).
            post_body: Optional POST body dict for complex queries. When provided,
                all other parameters are ignored.
            patent_application_number_q: Filter by patent application number.
            legal_section_code_q: Filter by legal section code (e.g., ``"101"``, ``"103"``).
            action_type_category_q: Filter by action type (e.g., ``"rejected"``).
            tech_center_q: Filter by technology center code.
            work_group_q: Filter by work group code.
            group_art_unit_number_q: Filter by group art unit number.
            examiner_cited_reference_indicator_q: Filter by examiner-cited indicator.
            applicant_cited_examiner_reference_indicator_q: Filter by applicant-cited
                examiner reference indicator.
            create_date_time_from_q: Filter from this create date (``"YYYY-MM-DD"``).
            create_date_time_to_q: Filter to this create date (``"YYYY-MM-DD"``).
            additional_query_params: Additional custom POST body parameters.

        Returns:
            OACitationsResponse: Response containing matching citation records.

        Examples:
            # Search with a direct criteria string
            >>> response = client.search(
            ...     criteria="patentApplicationNumber:16845502"
            ... )

            # Search with convenience parameters
            >>> response = client.search(
            ...     legal_section_code_q="103",
            ...     examiner_cited_reference_indicator_q=True,
            ...     rows=50,
            ... )

            # Search with POST body
            >>> response = client.search(
            ...     post_body={"criteria": "techCenter:2800", "rows": 100}
            ... )
        """
        endpoint = self.ENDPOINTS["search"]

        if post_body is not None:
            return self._get_model(
                method="POST",
                endpoint=endpoint,
                response_class=OACitationsResponse,
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
            if legal_section_code_q:
                q_parts.append(f"legalSectionCode:*{legal_section_code_q}*")
            if action_type_category_q:
                q_parts.append(f"actionTypeCategory:{action_type_category_q}")
            if tech_center_q:
                q_parts.append(f"techCenter:{tech_center_q}")
            if work_group_q:
                q_parts.append(f"workGroup:{work_group_q}")
            if group_art_unit_number_q:
                q_parts.append(f"groupArtUnitNumber:{group_art_unit_number_q}")
            if examiner_cited_reference_indicator_q is not None:
                val = str(examiner_cited_reference_indicator_q).lower()
                q_parts.append(f"examinerCitedReferenceIndicator:{val}")
            if applicant_cited_examiner_reference_indicator_q is not None:
                val = str(applicant_cited_examiner_reference_indicator_q).lower()
                q_parts.append(f"applicantCitedExaminerReferenceIndicator:{val}")

            if create_date_time_from_q and create_date_time_to_q:
                q_parts.append(
                    f"createDateTime:[{create_date_time_from_q} TO {create_date_time_to_q}]"
                )
            elif create_date_time_from_q:
                q_parts.append(f"createDateTime:>={create_date_time_from_q}")
            elif create_date_time_to_q:
                q_parts.append(f"createDateTime:<={create_date_time_to_q}")

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
            response_class=OACitationsResponse,
            json_data=body,
        )

    def get_fields(self) -> OACitationsFieldsResponse:
        """Retrieve available fields and API metadata for the OA Citations API.

        Returns:
            OACitationsFieldsResponse: API metadata including available field
                names and last data update timestamp.

        Examples:
            >>> fields_response = client.get_fields()
            >>> print(fields_response.field_count)
            16
            >>> print(fields_response.api_status)
            'PUBLISHED'
        """
        endpoint = self.ENDPOINTS["get_fields"]
        return self._get_model(
            method="GET",
            endpoint=endpoint,
            response_class=OACitationsFieldsResponse,
        )

    def paginate(
        self, post_body: dict[str, Any] | None = None, **kwargs: Any
    ) -> Iterator[OACitationRecord]:
        """Provide an iterator to paginate through citation search results.

        Automatically handles pagination using Solr-style start/rows parameters.
        The ``start`` parameter is managed internally; providing it will raise a ValueError.

        Args:
            post_body: Optional POST body dict for complex search queries.
            **kwargs: Keyword arguments passed to :meth:`search`.

        Returns:
            Iterator[OACitationRecord]: An iterator yielding OACitationRecord objects.

        Examples:
            # Paginate through all 103 rejections with examiner-cited references
            >>> for record in client.paginate(
            ...     legal_section_code_q="103",
            ...     examiner_cited_reference_indicator_q=True,
            ...     rows=50,
            ... ):
            ...     print(record.parsed_reference_identifier)

            # Paginate with POST body
            >>> for record in client.paginate(
            ...     post_body={"criteria": "techCenter:2800", "rows": 50}
            ... ):
            ...     process(record)
        """
        return self.paginate_solr_results(
            method_name="search",
            response_container_attr="docs",
            post_body=post_body,
            **kwargs,
        )
