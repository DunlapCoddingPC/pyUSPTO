"""clients.petition_decisions - Clients for the USPTO Petition Decisions API.

This module provides clients for interacting with the USPTO Petition Decisions
API. It allows you to search for and retrieve petition decisions in publicly
available patent applications and patents filed in 2001 or later.
"""

import warnings
from collections.abc import Iterator
from typing import Any, ClassVar

import requests

from pyUSPTO.clients.base import BaseUSPTOClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.petition_decisions import (
    DocumentDownloadOption,
    PetitionDecision,
    PetitionDecisionDownloadResponse,
    PetitionDecisionResponse,
)
from pyUSPTO.warnings import USPTODataMismatchWarning


class PetitionDecisionsClient(BaseUSPTOClient[PetitionDecisionResponse]):
    """Client for interacting with the USPTO Petition Decisions API.

    This client provides methods to search for petition decisions, retrieve specific
    decisions by ID, download decision data, and download associated documents.

    Since USPTO ODP Release 5.0 the API returns all petition decisions, final and
    non-final. Use ``FinalPetitionDecisionsClient`` for final decisions only.
    """

    ENDPOINTS = {
        "search_decisions": "api/v1/petition/decisions/search",
        "get_decision_by_id": "api/v1/petition/decisions/{petitionDecisionRecordIdentifier}",
        "download_decisions": "api/v1/petition/decisions/search/download",
    }

    # Filters added to every search and download request, as {field: value}.
    # Subclasses set this to scope the client to a subset of decisions.
    FIXED_FILTERS: ClassVar[dict[str, str]] = {}

    # Paginated sorts end on this unique field: the API orders tied records
    # differently on each request, so offset pages would repeat and skip decisions.
    TIEBREAK_SORT_FIELD: ClassVar[str] = "petitionDecisionRecordIdentifier"

    def __init__(
        self,
        config: USPTOConfig | None = None,
        base_url: str | None = None,
    ):
        """Initialize the PetitionDecisionsClient.

        Args:
            config: USPTOConfig instance containing API key and settings. If not provided,
                creates config from environment variables (requires USPTO_API_KEY).
            base_url: Optional base URL override for the USPTO Petition Decisions API.
                If not provided, uses config.petition_decisions_base_url or default.
        """
        # Use provided config or create from environment
        if config is None:
            self.config = USPTOConfig.from_env()
        else:
            self.config = config

        # Determine effective base URL
        effective_base_url = base_url or self.config.petition_decisions_base_url

        # Initialize base client
        super().__init__(
            base_url=effective_base_url,
            config=self.config,
        )

    def _get_decision_from_response(
        self,
        response_data: PetitionDecisionResponse,
        petition_decision_record_identifier_for_validation: str | None = None,
    ) -> PetitionDecision | None:
        """Extract a single PetitionDecision from the response.

        Args:
            response_data: The API response containing petition decisions.
            petition_decision_record_identifier_for_validation: Optional identifier
                to validate against the returned decision.

        Returns:
            Optional[PetitionDecision]: The first petition decision if found, None otherwise.
        """
        if not response_data or not response_data.petition_decision_data_bag:
            return None

        decision = response_data.petition_decision_data_bag[0]

        if (
            petition_decision_record_identifier_for_validation
            and decision.petition_decision_record_identifier
            != petition_decision_record_identifier_for_validation
        ):
            warnings.warn(
                f"API returned decision identifier '{decision.petition_decision_record_identifier}' "
                f"but requested '{petition_decision_record_identifier_for_validation}'. "
                f"This may indicate an API data inconsistency.",
                USPTODataMismatchWarning,
                stacklevel=2,
            )
        return decision

    def _add_fixed_filters(self, params: dict[str, Any]) -> dict[str, Any]:
        """Add FIXED_FILTERS to GET params as repeated ``filters`` values.

        The API ANDs repeated ``filters`` parameters, so these combine with any
        filters the caller passed.
        """
        if not self.FIXED_FILTERS:
            return params
        existing = params.get("filters")
        if existing is None:
            values: list[str] = []
        elif isinstance(existing, str):
            values = [existing]
        else:
            values = list(existing)
        values.extend(f"{name} {value}" for name, value in self.FIXED_FILTERS.items())
        return {**params, "filters": values}

    def _add_fixed_filters_to_body(self, post_body: dict[str, Any]) -> dict[str, Any]:
        """Return a copy of a POST body with FIXED_FILTERS added to its ``filters`` list.

        Builds new containers so the caller's body, which pagination reuses for
        every page, is never modified.
        """
        if not self.FIXED_FILTERS:
            return post_body
        fixed = [
            {"name": name, "value": [value]}
            for name, value in self.FIXED_FILTERS.items()
        ]
        existing = post_body.get("filters")
        caller_filters = [] if existing is None else existing
        return {**post_body, "filters": [*caller_filters, *fixed]}

    def search_decisions(
        self,
        query: str | None = None,
        sort: str | list[str] | None = None,
        offset: int | None = 0,
        limit: int | None = 25,
        facets: str | None = None,
        fields: str | None = None,
        filters: str | None = None,
        range_filters: str | None = None,
        post_body: dict[str, Any] | None = None,
        # Convenience query parameters
        application_number_q: str | None = None,
        patent_number_q: str | None = None,
        inventor_name_q: str | None = None,
        applicant_name_q: str | None = None,
        invention_title_q: str | None = None,
        decided_petition_type_code_q: str | None = None,
        decision_date_from_q: str | None = None,
        decision_date_to_q: str | None = None,
        petition_mail_date_from_q: str | None = None,
        petition_mail_date_to_q: str | None = None,
        technology_center_q: str | None = None,
        final_deciding_office_name_q: str | None = None,
        additional_query_params: dict[str, Any] | None = None,
    ) -> PetitionDecisionResponse:
        """Return petition decisions matching the given criteria.

        This method can perform either a GET request using query parameters or a POST
        request if post_body is specified. When using GET, you can provide either a
        direct query string or use convenience parameters that will be automatically
        combined into a query.

        Args:
            query: Direct query string in USPTO search syntax.
            sort: Sort as "field order", e.g. "decisionDate desc". A list sends one
                sort parameter per key; the API rejects comma-joined keys.
            offset: Number of records to skip (pagination).
            limit: Maximum number of records to return.
            facets: Facet configuration string.
            fields: Specific fields to return.
            filters: Filter as "field value" (a space, not a colon), e.g.
                "decidedPetitionTypeCode A".
                A value containing a space only works in post_body filters.
            range_filters: Range filter configuration string.
            post_body: Optional POST body for complex queries.
            application_number_q: Filter by application number.
            patent_number_q: Filter by patent number.
            inventor_name_q: Filter by inventor name.
            applicant_name_q: Filter by applicant name.
            invention_title_q: Filter by invention title.
            decided_petition_type_code_q: Filter by decided type code ("A" GRANTED,
                "B" GRANTED-IN-PART, "C" DENIED, "D" DISMISSED).
            decision_date_from_q: Filter decisions from this date (YYYY-MM-DD).
            decision_date_to_q: Filter decisions to this date (YYYY-MM-DD).
            petition_mail_date_from_q: Filter petition mail dates from (YYYY-MM-DD).
            petition_mail_date_to_q: Filter petition mail dates to (YYYY-MM-DD).
            technology_center_q: Filter by technology center.
            final_deciding_office_name_q: Filter by deciding office name.
            additional_query_params: Additional custom query parameters.

        Returns:
            PetitionDecisionResponse: Response containing matching petition decisions.

        Examples:
            # Search with direct query
            >>> response = client.search_decisions(query="applicationNumberText:17765301")

            # Search with convenience parameters
            >>> response = client.search_decisions(
            ...     applicant_name_q="ACME Corp",
            ...     decision_date_from_q="2022-01-01",
            ...     limit=50
            ... )

            # Search with POST body
            >>> response = client.search_decisions(
            ...     post_body={"q": "technologyCenter:1700", "pagination": {"limit": 100}}
            ... )
        """
        endpoint = self.ENDPOINTS["search_decisions"]

        if post_body is not None:
            # POST request path
            result = self._get_model(
                method="POST",
                endpoint=endpoint,
                response_class=PetitionDecisionResponse,
                json_data=self._add_fixed_filters_to_body(post_body),
                params=additional_query_params,
            )
        else:
            # GET request path
            params: dict[str, Any] = {}
            final_q = query

            # Build query from convenience parameters
            if final_q is None:
                q_parts = []
                if application_number_q:
                    q_parts.append(f"applicationNumberText:{application_number_q}")
                if patent_number_q:
                    q_parts.append(f"patentNumber:{patent_number_q}")
                if inventor_name_q:
                    v = (
                        f'"{inventor_name_q}"'
                        if " " in inventor_name_q
                        else inventor_name_q
                    )
                    q_parts.append(f"inventorBag:{v}")
                if applicant_name_q:
                    v = (
                        f'"{applicant_name_q}"'
                        if " " in applicant_name_q
                        else applicant_name_q
                    )
                    q_parts.append(f"firstApplicantName:{v}")
                if invention_title_q:
                    v = (
                        f'"{invention_title_q}"'
                        if " " in invention_title_q
                        else invention_title_q
                    )
                    q_parts.append(f"inventionTitle:{v}")
                if decided_petition_type_code_q:
                    q_parts.append(
                        f"decidedPetitionTypeCode:{decided_petition_type_code_q}"
                    )
                if technology_center_q:
                    q_parts.append(f"technologyCenter:{technology_center_q}")
                if final_deciding_office_name_q:
                    v = (
                        f'"{final_deciding_office_name_q}"'
                        if " " in final_deciding_office_name_q
                        else final_deciding_office_name_q
                    )
                    q_parts.append(f"finalDecidingOfficeName:{v}")

                # Handle decision date range
                if decision_date_from_q and decision_date_to_q:
                    q_parts.append(
                        f"decisionDate:[{decision_date_from_q} TO {decision_date_to_q}]"
                    )
                elif decision_date_from_q:
                    q_parts.append(f"decisionDate:>={decision_date_from_q}")
                elif decision_date_to_q:
                    q_parts.append(f"decisionDate:<={decision_date_to_q}")

                # Handle petition mail date range
                if petition_mail_date_from_q and petition_mail_date_to_q:
                    q_parts.append(
                        f"petitionMailDate:[{petition_mail_date_from_q} TO {petition_mail_date_to_q}]"
                    )
                elif petition_mail_date_from_q:
                    q_parts.append(f"petitionMailDate:>={petition_mail_date_from_q}")
                elif petition_mail_date_to_q:
                    q_parts.append(f"petitionMailDate:<={petition_mail_date_to_q}")

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

            result = self._get_model(
                method="GET",
                endpoint=endpoint,
                response_class=PetitionDecisionResponse,
                params=self._add_fixed_filters(params),
            )
        return result

    def get_decision_by_id(
        self,
        petition_decision_record_identifier: str,
    ) -> PetitionDecision | None:
        """Retrieve a specific petition decision by its record identifier.

        The decision's documents are included. The request sends no query
        parameters: with any present, including the documented
        ``includeDocuments``, the API ignores the identifier and returns
        unrelated decisions.

        Args:
            petition_decision_record_identifier: The unique identifier for the petition
                decision record (UUID format).

        Returns:
            Optional[PetitionDecision]: The petition decision if found, None otherwise.

        Examples:
            >>> decision = client.get_decision_by_id(
            ...     "1a552446-1d2b-570a-9bb6-b4fef39b0a91"
            ... )
        """
        endpoint = self.ENDPOINTS["get_decision_by_id"].format(
            petitionDecisionRecordIdentifier=petition_decision_record_identifier
        )

        response_data = self._get_model(
            method="GET",
            endpoint=endpoint,
            response_class=PetitionDecisionResponse,
            params=None,
        )
        return self._get_decision_from_response(
            response_data=response_data,
            petition_decision_record_identifier_for_validation=petition_decision_record_identifier,
        )

    def download_decisions(
        self,
        format: str = "json",
        query: str | None = None,
        sort: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        fields: str | None = None,
        filters: str | None = None,
        range_filters: str | None = None,
        # Convenience query parameters
        application_number_q: str | None = None,
        patent_number_q: str | None = None,
        inventor_name_q: str | None = None,
        applicant_name_q: str | None = None,
        decision_date_from_q: str | None = None,
        decision_date_to_q: str | None = None,
        additional_query_params: dict[str, Any] | None = None,
        # File save options (for CSV format)
        file_name: str | None = None,
        destination: str | None = None,
        overwrite: bool = False,
    ) -> PetitionDecisionDownloadResponse | requests.Response | str:
        """Download petition decisions data in the specified format.

        This endpoint is designed for bulk downloads of petition decisions data.
        It supports JSON and CSV formats.

        Args:
            format: Download format, either "json" or "csv". Defaults to "json".
            query: Direct query string in USPTO search syntax.
            sort: Sort order for results.
            offset: Number of records to skip (pagination).
            limit: Maximum number of records to return.
            fields: Specific fields to return.
            filters: Filter as "field value" (a space, not a colon), e.g.
                "decidedPetitionTypeCode A".
                A value containing a space only works in post_body filters.
            range_filters: Range filter configuration string.
            application_number_q: Filter by application number.
            patent_number_q: Filter by patent number.
            inventor_name_q: Filter by inventor name.
            applicant_name_q: Filter by applicant name.
            decision_date_from_q: Filter decisions from this date (YYYY-MM-DD).
            decision_date_to_q: Filter decisions to this date (YYYY-MM-DD).
            additional_query_params: Additional custom query parameters.
            file_name: Optional filename for CSV downloads. Defaults to "petition_decisions.csv".
            destination: Optional directory path to save CSV file. If None, returns Response.
            overwrite: Whether to overwrite existing files. Default False.

        Returns:
            Union[PetitionDecisionDownloadResponse, requests.Response, str]:
                - If format="json": Returns PetitionDecisionDownloadResponse
                - If format="csv" and destination is None: Returns streaming Response
                - If format="csv" and destination is set: Returns str path to saved file

        Raises:
            FileExistsError: If CSV file exists and overwrite=False

        Examples:
            # Download as JSON
            >>> download = client.download_decisions(
            ...     format="json",
            ...     query="technologyCenter:1700",
            ...     limit=1000
            ... )
            >>> for decision in download.petition_decision_data:
            ...     print(decision.application_number_text)

            # Download CSV and save to file
            >>> file_path = client.download_decisions(
            ...     format="csv",
            ...     decision_date_from_q="2023-01-01",
            ...     destination="./downloads"
            ... )
            >>> print(f"Saved to: {file_path}")

            # Download CSV as streaming response (advanced usage)
            >>> response = client.download_decisions(format="csv")
            >>> with open("decisions.csv", "wb") as f:
            ...     for chunk in response.iter_content(chunk_size=8192):
            ...         f.write(chunk)
        """
        endpoint = self.ENDPOINTS["download_decisions"]

        params: dict[str, Any] = {"format": format}
        final_q = query

        # Build query from convenience parameters
        if final_q is None:
            q_parts = []
            if application_number_q:
                q_parts.append(f"applicationNumberText:{application_number_q}")
            if patent_number_q:
                q_parts.append(f"patentNumber:{patent_number_q}")
            if inventor_name_q:
                v = (
                    f'"{inventor_name_q}"'
                    if " " in inventor_name_q
                    else inventor_name_q
                )
                q_parts.append(f"inventorBag:{v}")
            if applicant_name_q:
                v = (
                    f'"{applicant_name_q}"'
                    if " " in applicant_name_q
                    else applicant_name_q
                )
                q_parts.append(f"firstApplicantName:{v}")

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
        if fields is not None:
            params["fields"] = fields
        if filters is not None:
            params["filters"] = filters
        if range_filters is not None:
            params["rangeFilters"] = range_filters

        if additional_query_params:
            params.update(additional_query_params)

        params = self._add_fixed_filters(params)

        if format.lower() == "json":
            # For JSON, parse the response
            return self._get_model(
                method="GET",
                endpoint=endpoint,
                response_class=PetitionDecisionDownloadResponse,
                params=params,
            )
        else:
            # For CSV or other formats, get streaming response
            result = self._stream_request(
                method="GET", endpoint=endpoint, params=params
            )

            if destination is not None:
                # Save to file using the base class helper
                return self._save_response_to_file(
                    response=result,
                    destination=destination,
                    file_name=file_name or "petition_decisions.csv",
                    overwrite=overwrite,
                )
            else:
                # Return streaming response for manual handling
                return result

    def paginate_decisions(
        self, post_body: dict[str, Any] | None = None, **kwargs: Any
    ) -> Iterator[PetitionDecision]:
        """Provide an iterator to paginate through petition decision search results.

        This method simplifies fetching all petition decisions matching a search query
        by automatically handling pagination. Supports both GET and POST requests.

        The offset is managed by the pagination logic. Set the page size with
        ``limit`` (GET) or ``post_body["pagination"]["limit"]`` (POST).

        Results are sorted on ``petitionDecisionRecordIdentifier`` last, ascending
        unless your sort already includes it. The API orders tied records
        differently on each request, so pages would otherwise repeat and skip
        decisions.

        Args:
            post_body: Optional POST body for complex search queries
            **kwargs: Keyword arguments for GET-based pagination

        Returns:
            Iterator[PetitionDecision]: An iterator yielding PetitionDecision objects,
                allowing iteration over all matching petition decisions across multiple
                pages of results.

        Examples:
            # GET pagination through all decisions for a technology center
            >>> for decision in client.paginate_decisions(technology_center_q="1700"):
            ...     print(f"{decision.application_number_text}: {decision.decided_petition_type_code}")

            # POST pagination with a date range
            >>> for decision in client.paginate_decisions(
            ...     post_body={"q": "decisionDate:[2023-01-01 TO 2023-12-31]"}
            ... ):
            ...     process_decision(decision)
        """
        field = self.TIEBREAK_SORT_FIELD
        if post_body is not None:
            body_sort = post_body.get("sort") or []
            if not any(key.get("field") == field for key in body_sort):
                post_body = {
                    **post_body,
                    "sort": [*body_sort, {"field": field, "order": "asc"}],
                }
        else:
            caller_sort = kwargs.get("sort")
            sort_keys = (
                [caller_sort]
                if isinstance(caller_sort, str)
                else list(caller_sort or [])
            )
            if not any(key.split(" ", 1)[0] == field for key in sort_keys):
                sort_keys.append(f"{field} asc")
            kwargs["sort"] = sort_keys
        return self.paginate_results(
            method_name="search_decisions",
            response_container_attr="petition_decision_data_bag",
            post_body=post_body,
            **kwargs,
        )

    def download_petition_document(
        self,
        download_option: DocumentDownloadOption,
        destination: str | None = None,
        file_name: str | None = None,
        overwrite: bool = False,
    ) -> str:
        """Download petition document (auto-extracts if in archive).

        Args:
            download_option: DocumentDownloadOption object containing the download
                URL and metadata.
            destination: Optional directory path where the file should be saved.
                If not provided, saves to the current directory.
            file_name: Optional filename for the downloaded file. If not provided,
                it will be extracted from Content-Disposition header or URL.
            overwrite: Whether to overwrite an existing file. Defaults to False.

        Returns:
            str: The absolute path to the downloaded file (extracted if was in archive).

        Raises:
            ValueError: If download_option has no download URL.
            FileExistsError: If the file exists and overwrite=False.

        Examples:
            # Download first document from a decision
            >>> decision = client.get_decision_by_id(
            ...     "1a552446-1d2b-570a-9bb6-b4fef39b0a91"
            ... )
            >>> if decision.document_bag:
            ...     doc = decision.document_bag[0]
            ...     if doc.download_option_bag:
            ...         # Download PDF version
            ...         pdf_option = next(
            ...             opt for opt in doc.download_option_bag
            ...             if opt.mime_type_identifier == "PDF"
            ...         )
            ...         path = client.download_petition_document(
            ...             pdf_option,
            ...             destination="./downloads"
            ...         )
            ...         print(f"Downloaded to: {path}")
        """
        if download_option.download_url is None:
            raise ValueError("DocumentDownloadOption has no download_url")

        return self._download_and_extract(
            url=download_option.download_url,
            destination=destination,
            file_name=file_name,
            overwrite=overwrite,
        )


class FinalPetitionDecisionsClient(PetitionDecisionsClient):
    """Client for final petition decisions only.

    Works like ``PetitionDecisionsClient``, but every search, pagination, and
    ``download_decisions`` call is restricted to decisions whose
    ``finalPetitionDecisionIndicator`` is true. The API can't filter lookups by
    ID, so ``get_decision_by_id`` returns None for a decision that isn't final.
    """

    FIXED_FILTERS = {"finalPetitionDecisionIndicator": "true"}

    def get_decision_by_id(
        self,
        petition_decision_record_identifier: str,
    ) -> PetitionDecision | None:
        """Retrieve a final petition decision by its record identifier.

        Args:
            petition_decision_record_identifier: The unique identifier for the petition
                decision record (UUID format).

        Returns:
            Optional[PetitionDecision]: The decision if found and final, None otherwise.
        """
        decision = super().get_decision_by_id(petition_decision_record_identifier)
        if decision is None or decision.final_petition_decision_indicator is not True:
            return None
        return decision
