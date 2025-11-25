"""
clients.ptab_trials - Client for USPTO PTAB Trials API

This module provides a client for interacting with the USPTO PTAB (Patent Trial
and Appeal Board) Trials API. It allows you to search for trial proceedings,
documents, and decisions.
"""

from typing import Any, Dict, Iterator, Optional

from pyUSPTO.clients.base import BaseUSPTOClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.ptab import PTABTrialProceeding, PTABTrialProceedingResponse


class PTABTrialsClient(BaseUSPTOClient[PTABTrialProceedingResponse]):
    """Client for interacting with the USPTO PTAB Trials API.

    This client provides methods to search for trial proceedings, trial documents,
    and trial decisions from the Patent Trial and Appeal Board.

    Trial proceedings data includes IPR (Inter Partes Review), PGR (Post-Grant Review),
    CBM (Covered Business Method), and DER (Derivation) proceedings.
    """

    ENDPOINTS = {
        "search_proceedings": "api/v1/ptab/trials/proceedings/search",
        "search_documents": "api/v1/ptab/trials/documents/search",
        "search_decisions": "api/v1/ptab/trials/decisions/search",
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        config: Optional[USPTOConfig] = None,
    ):
        """Initialize the PTABTrialsClient.

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

    def search_proceedings(
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
        trial_number_q: Optional[str] = None,
        patent_owner_name_q: Optional[str] = None,
        petitioner_party_name_q: Optional[str] = None,
        respondent_name_q: Optional[str] = None,
        trial_type_code_q: Optional[str] = None,
        trial_status_category_q: Optional[str] = None,
        petition_filing_date_from_q: Optional[str] = None,
        petition_filing_date_to_q: Optional[str] = None,
        additional_query_params: Optional[Dict[str, Any]] = None,
    ) -> PTABTrialProceedingResponse:
        """Searches for PTAB trial proceedings.

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
            trial_number_q: Filter by trial number (e.g., "IPR2023-00001").
            patent_owner_name_q: Filter by patent owner name.
            petitioner_party_name_q: Filter by petitioner party name.
            respondent_name_q: Filter by respondent name.
            trial_type_code_q: Filter by trial type code (e.g., "IPR", "PGR", "CBM", "DER").
            trial_status_category_q: Filter by trial status category.
            petition_filing_date_from_q: Filter proceedings from this date (YYYY-MM-DD).
            petition_filing_date_to_q: Filter proceedings to this date (YYYY-MM-DD).
            additional_query_params: Additional custom query parameters.

        Returns:
            PTABTrialProceedingResponse: Response containing matching trial proceedings.

        Examples:
            # Search with direct query
            >>> response = client.search_proceedings(query="trialNumber:IPR2023-00001")

            # Search with convenience parameters
            >>> response = client.search_proceedings(
            ...     trial_type_code_q="IPR",
            ...     petition_filing_date_from_q="2023-01-01",
            ...     limit=50
            ... )

            # Search with POST body
            >>> response = client.search_proceedings(
            ...     post_body={"q": "trialStatusCategory:Terminated", "limit": 100}
            ... )
        """
        endpoint = self.ENDPOINTS["search_proceedings"]

        if post_body is not None:
            # POST request path
            result = self._make_request(
                method="POST",
                endpoint=endpoint,
                json_data=post_body,
                params=additional_query_params,
                response_class=PTABTrialProceedingResponse,
            )
        else:
            # GET request path
            params: Dict[str, Any] = {}
            final_q = query

            # Build query from convenience parameters
            if final_q is None:
                q_parts = []
                if trial_number_q:
                    q_parts.append(f"trialNumber:{trial_number_q}")
                if patent_owner_name_q:
                    q_parts.append(f"patentOwnerName:{patent_owner_name_q}")
                if petitioner_party_name_q:
                    q_parts.append(f"petitionerPartyName:{petitioner_party_name_q}")
                if respondent_name_q:
                    q_parts.append(f"respondentName:{respondent_name_q}")
                if trial_type_code_q:
                    q_parts.append(f"trialTypeCode:{trial_type_code_q}")
                if trial_status_category_q:
                    q_parts.append(f"trialStatusCategory:{trial_status_category_q}")

                # Handle petition filing date range
                if petition_filing_date_from_q and petition_filing_date_to_q:
                    q_parts.append(
                        f"petitionFilingDate:[{petition_filing_date_from_q} TO {petition_filing_date_to_q}]"
                    )
                elif petition_filing_date_from_q:
                    q_parts.append(
                        f"petitionFilingDate:>={petition_filing_date_from_q}"
                    )
                elif petition_filing_date_to_q:
                    q_parts.append(f"petitionFilingDate:<={petition_filing_date_to_q}")

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
                response_class=PTABTrialProceedingResponse,
            )

        assert isinstance(result, PTABTrialProceedingResponse)
        return result

    def search_documents(
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
        trial_number_q: Optional[str] = None,
        document_category_q: Optional[str] = None,
        document_type_name_q: Optional[str] = None,
        filing_date_from_q: Optional[str] = None,
        filing_date_to_q: Optional[str] = None,
        additional_query_params: Optional[Dict[str, Any]] = None,
    ) -> PTABTrialProceedingResponse:
        """Searches for PTAB trial documents.

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
            trial_number_q: Filter by trial number.
            document_category_q: Filter by document category.
            document_type_name_q: Filter by document type name.
            filing_date_from_q: Filter documents from this date (YYYY-MM-DD).
            filing_date_to_q: Filter documents to this date (YYYY-MM-DD).
            additional_query_params: Additional custom query parameters.

        Returns:
            PTABTrialProceedingResponse: Response containing matching trial documents.

        Examples:
            # Search with direct query
            >>> response = client.search_documents(query="trialNumber:IPR2023-00001")

            # Search with convenience parameters
            >>> response = client.search_documents(
            ...     document_category_q="Paper",
            ...     filing_date_from_q="2023-01-01",
            ...     limit=50
            ... )

            # Search with POST body
            >>> response = client.search_documents(
            ...     post_body={"q": "documentTypeName:Decision", "limit": 100}
            ... )
        """
        endpoint = self.ENDPOINTS["search_documents"]

        if post_body is not None:
            # POST request path
            result = self._make_request(
                method="POST",
                endpoint=endpoint,
                json_data=post_body,
                params=additional_query_params,
                response_class=PTABTrialProceedingResponse,
            )
        else:
            # GET request path
            params: Dict[str, Any] = {}
            final_q = query

            # TODO: Add convenience parameters for Petitioner, inventor, real party in interest, patent number, patent owner,
            # Build query from convenience parameters
            if final_q is None:
                q_parts = []
                if trial_number_q:
                    q_parts.append(f"trialNumber:{trial_number_q}")
                if document_category_q:
                    q_parts.append(f"documentCategory:{document_category_q}")
                if document_type_name_q:
                    q_parts.append(f"documentTypeName:{document_type_name_q}")

                # Handle filing date range
                if filing_date_from_q and filing_date_to_q:
                    q_parts.append(
                        f"filingDate:[{filing_date_from_q} TO {filing_date_to_q}]"
                    )
                elif filing_date_from_q:
                    q_parts.append(f"filingDate:>={filing_date_from_q}")
                elif filing_date_to_q:
                    q_parts.append(f"filingDate:<={filing_date_to_q}")

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
                response_class=PTABTrialProceedingResponse,
            )

        assert isinstance(result, PTABTrialProceedingResponse)
        return result

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
        # TODO: parameter for trialTypeCode, patent number, application number, patent owner, trial status, real party in interest, document categroy.
        trial_number_q: Optional[str] = None,
        decision_type_category_q: Optional[str] = None,
        decision_date_from_q: Optional[str] = None,
        decision_date_to_q: Optional[str] = None,
        additional_query_params: Optional[Dict[str, Any]] = None,
    ) -> PTABTrialProceedingResponse:
        """Searches for PTAB trial decisions.

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
            trial_number_q: Filter by trial number.
            decision_type_category_q: Filter by decision type category.
            decision_date_from_q: Filter decisions from this date (YYYY-MM-DD).
            decision_date_to_q: Filter decisions to this date (YYYY-MM-DD).
            additional_query_params: Additional custom query parameters.

        Returns:
            PTABTrialProceedingResponse: Response containing matching trial decisions.

        Examples:
            # Search with direct query
            >>> response = client.search_decisions(query="trialNumber:IPR2023-00001")

            # Search with convenience parameters
            >>> response = client.search_decisions(
            ...     decision_type_category_q="Final Written Decision",
            ...     decision_date_from_q="2023-01-01",
            ...     limit=50
            ... )

            # Search with POST body
            >>> response = client.search_decisions(
            ...     post_body={"q": "decisionTypeCategory:Institution Decision", "limit": 100}
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
                response_class=PTABTrialProceedingResponse,
            )
        else:
            # GET request path
            params: Dict[str, Any] = {}
            final_q = query

            # Build query from convenience parameters
            if final_q is None:
                q_parts = []
                if trial_number_q:
                    q_parts.append(f"trialNumber:{trial_number_q}")
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
                response_class=PTABTrialProceedingResponse,
            )

        assert isinstance(result, PTABTrialProceedingResponse)
        return result

    def paginate_proceedings(self, **kwargs: Any) -> Iterator[PTABTrialProceeding]:
        """Provides an iterator to paginate through trial proceeding search results.

        This method simplifies fetching all trial proceedings matching a search query
        by automatically handling pagination. It internally calls the search_proceedings
        method for GET requests, batching results and yielding them one by one.

        All keyword arguments are passed directly to search_proceedings to define the
        search criteria. The offset and limit parameters are managed by the pagination
        logic; setting them directly in kwargs might lead to unexpected behavior.

        Args:
            **kwargs: Keyword arguments passed to search_proceedings for constructing
                the search query. Do not include post_body.

        Returns:
            Iterator[PTABTrialProceeding]: An iterator yielding PTABTrialProceeding objects,
                allowing iteration over all matching proceedings across multiple pages of results.

        Raises:
            ValueError: If post_body is included in kwargs, as this method only
                supports GET request parameters for pagination.

        Examples:
            # Paginate through all IPR proceedings
            >>> for proceeding in client.paginate_proceedings(trial_type_code_q="IPR"):
            ...     print(f"{proceeding.trial_meta_data.trial_number}: "
            ...           f"{proceeding.trial_meta_data.trial_status_category}")

            # Paginate with date range
            >>> for proceeding in client.paginate_proceedings(
            ...     petition_filing_date_from_q="2023-01-01",
            ...     petition_filing_date_to_q="2023-12-31"
            ... ):
            ...     process_proceeding(proceeding)
        """
        if "post_body" in kwargs:
            raise ValueError(
                "paginate_proceedings uses GET requests and does not support 'post_body'. "
                "Use keyword arguments for search criteria."
            )

        return self.paginate_results(
            method_name="search_proceedings",
            response_container_attr="patent_trial_proceeding_data_bag",
            **kwargs,
        )
