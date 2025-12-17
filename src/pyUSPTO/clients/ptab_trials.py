"""clients.ptab_trials - Client for USPTO PTAB Trials API.

This module provides a client for interacting with the USPTO PTAB (Patent Trial
and Appeal Board) Trials API. It allows you to search for trial proceedings,
documents, and decisions.
"""

from collections.abc import Iterator
from typing import Any

from pyUSPTO.clients.base import BaseUSPTOClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.ptab import (
    PTABTrialDocumentResponse,
    PTABTrialProceeding,
    PTABTrialProceedingResponse,
    TrialDocumentData,
    TrialMetaData,
)


class PTABTrialsClient(
    BaseUSPTOClient[PTABTrialProceedingResponse | PTABTrialDocumentResponse]
):
    """Client for interacting with the USPTO PTAB Trials API.

    This client provides methods to search for trial proceedings, trial documents,
    and trial decisions from the Patent Trial and Appeal Board.

    Trial proceedings data includes IPR (Inter Partes Review), PGR (Post-Grant Review),
    CBM (Covered Business Method), and DER (Derivation) proceedings.
    """

    ENDPOINTS = {
        "search_proceedings": "api/v1/patent/trials/proceedings/search",
        "search_documents": "api/v1/patent/trials/documents/search",
        "search_decisions": "api/v1/patent/trials/decisions/search",
    }

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        config: USPTOConfig | None = None,
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
            api_key=api_key_to_use,
            base_url=effective_base_url,
            config=self.config,
        )

    def _perform_search(
        self,
        endpoint_key: str,
        response_class: Any,
        query: str | None,
        query_parts: list[str],
        post_body: dict[str, Any] | None,
        sort: str | None,
        offset: int | None,
        limit: int | None,
        facets: str | None,
        fields: str | None,
        filters: str | None,
        range_filters: str | None,
        additional_params: dict[str, Any] | None,
    ) -> PTABTrialProceedingResponse | PTABTrialDocumentResponse:
        """Execute a PTAB trial search request using GET or POST.

        If a POST body is provided, perform a POST request; otherwise, build
        query parameters and send a GET request.
        """
        endpoint = self.ENDPOINTS[endpoint_key]

        # Handle POST request
        if post_body is not None:
            result = self._make_request(
                method="POST",
                endpoint=endpoint,
                json_data=post_body,
                params=additional_params,
                response_class=response_class,
            )
            return result  # type: ignore

        # Handle GET request
        params: dict[str, Any] = {}
        final_q = query

        # Combine specific convenience query parts if no direct query is provided
        if final_q is None and query_parts:
            final_q = " AND ".join(query_parts)

        if final_q:
            params["q"] = final_q
        if sort:
            params["sort"] = sort
        if offset is not None:
            params["offset"] = offset
        if limit is not None:
            params["limit"] = limit
        if facets:
            params["facets"] = facets
        if fields:
            params["fields"] = fields
        if filters:
            params["filters"] = filters
        if range_filters:
            params["rangeFilters"] = range_filters

        if additional_params:
            params.update(additional_params)

        result = self._make_request(
            method="GET",
            endpoint=endpoint,
            params=params,
            response_class=response_class,
        )
        return result  # type: ignore

    def search_proceedings(
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
        trial_number_q: str | None = None,
        patent_owner_name_q: str | None = None,
        petitioner_real_party_in_interest_name_q: str | None = None,
        respondent_name_q: str | None = None,
        trial_type_code_q: str | None = None,
        trial_status_category_q: str | None = None,
        petition_filing_date_from_q: str | None = None,
        petition_filing_date_to_q: str | None = None,
        additional_query_params: dict[str, Any] | None = None,
    ) -> PTABTrialProceedingResponse:
        """Search for PTAB trial proceedings.

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
            petitioner_real_party_in_interest_name_q: Filter by petitioner real party in interest.
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
        """
        q_parts = []
        if trial_number_q:
            q_parts.append(f"trialNumber:{trial_number_q}")
        if patent_owner_name_q:
            q_parts.append(f'patentOwnerData.patentOwnerName:"{patent_owner_name_q}"')
        if petitioner_real_party_in_interest_name_q:
            q_parts.append(
                f'regularPetitionerData.realPartyInInterestName:"{petitioner_real_party_in_interest_name_q}"'
            )
        if respondent_name_q:
            q_parts.append(f'respondentData.patentOwnerName:"{respondent_name_q}"')
        if trial_type_code_q:
            q_parts.append(f"trialMetaData.trialTypeCode:{trial_type_code_q}")
        if trial_status_category_q:
            q_parts.append(
                f'trialMetaData.trialStatusCategory:"{trial_status_category_q}"'
            )

        if petition_filing_date_from_q and petition_filing_date_to_q:
            q_parts.append(
                f"trialMetaData.petitionFilingDate:[{petition_filing_date_from_q} TO {petition_filing_date_to_q}]"
            )
        elif petition_filing_date_from_q:
            q_parts.append(
                f"trialMetaData.petitionFilingDate:>={petition_filing_date_from_q}"
            )
        elif petition_filing_date_to_q:
            q_parts.append(
                f"trialMetaData.petitionFilingDate:<={petition_filing_date_to_q}"
            )

        return self._perform_search(
            endpoint_key="search_proceedings",
            response_class=PTABTrialProceedingResponse,
            query=query,
            query_parts=q_parts,
            post_body=post_body,
            sort=sort,
            offset=offset,
            limit=limit,
            facets=facets,
            fields=fields,
            filters=filters,
            range_filters=range_filters,
            additional_params=additional_query_params,
        )  # type: ignore

    def search_documents(
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
        trial_number_q: str | None = None,
        document_category_q: str | None = None,
        document_type_name_q: str | None = None,
        filing_date_from_q: str | None = None,
        filing_date_to_q: str | None = None,
        petitioner_real_party_in_interest_name_q: str | None = None,
        inventor_name_q: str | None = None,
        real_party_in_interest_name_q: str | None = None,
        patent_number_q: str | None = None,
        patent_owner_name_q: str | None = None,
        additional_query_params: dict[str, Any] | None = None,
    ) -> PTABTrialDocumentResponse:
        """Search for PTAB trial documents.

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
            document_category_q: Filter by document category (e.g., "Petition") DOCUMENTED BUT NOT IN API.
            document_type_name_q: Filter by document type name (description).
            filing_date_from_q: Filter documents from this date (YYYY-MM-DD).
            filing_date_to_q: Filter documents to this date (YYYY-MM-DD).
            petitioner_real_party_in_interest_name_q: Filter by petitioner real party in interest.
            inventor_name_q: Filter by inventor name.
            real_party_in_interest_name_q: Filter by real party in interest (generic).
            patent_number_q: Filter by patent number.
            patent_owner_name_q: Filter by patent owner name.
            additional_query_params: Additional custom query parameters.

        Returns:
            PTABTrialDocumentResponse: Response containing matching trial documents.

        Examples:
            # Search with direct query
            >>> response = client.search_documents(query="trialNumber:IPR2023-00001")

            # Search with convenience parameters
            >>> response = client.search_documents(
            ...     document_category_q="Paper",
            ...     filing_date_from_q="2023-01-01",
            ...     limit=50
            ... )
        """
        q_parts = []
        if trial_number_q:
            q_parts.append(f"trialNumber:{trial_number_q}")
        if document_category_q:
            q_parts.append(f'documentData.documentCategory:"{document_category_q}"')
        if document_type_name_q:
            q_parts.append(
                f'documentData.documentTypeDescriptionText:"{document_type_name_q}"'
            )
        if petitioner_real_party_in_interest_name_q:
            q_parts.append(
                f'regularPetitionerData.realPartyInInterestName:"{petitioner_real_party_in_interest_name_q}"'
            )
        if inventor_name_q:
            q_parts.append(f'patentOwnerData.inventorName:"{inventor_name_q}"')
        if real_party_in_interest_name_q:
            q_parts.append(
                f'regularPetitionerData.realPartyInInterestName:"{real_party_in_interest_name_q}"'
            )
        if patent_number_q:
            q_parts.append(f"patentOwnerData.patentNumber:{patent_number_q}")
        if patent_owner_name_q:
            q_parts.append(f'patentOwnerData.patentOwnerName:"{patent_owner_name_q}"')

        if filing_date_from_q and filing_date_to_q:
            q_parts.append(
                f"documentData.documentFilingDate:[{filing_date_from_q} TO {filing_date_to_q}]"
            )
        elif filing_date_from_q:
            q_parts.append(f"documentData.documentFilingDate:>={filing_date_from_q}")
        elif filing_date_to_q:
            q_parts.append(f"documentData.documentFilingDate:<={filing_date_to_q}")

        return self._perform_search(
            endpoint_key="search_documents",
            response_class=PTABTrialDocumentResponse,
            query=query,
            query_parts=q_parts,
            post_body=post_body,
            sort=sort,
            offset=offset,
            limit=limit,
            facets=facets,
            fields=fields,
            filters=filters,
            range_filters=range_filters,
            additional_params=additional_query_params,
        )  # type: ignore

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
        trial_number_q: str | None = None,
        decision_type_category_q: str | None = None,
        document_type_description_q: str | None = None,
        decision_date_from_q: str | None = None,
        decision_date_to_q: str | None = None,
        trial_type_code_q: str | None = None,
        patent_number_q: str | None = None,
        application_number_q: str | None = None,
        patent_owner_name_q: str | None = None,
        trial_status_category_q: str | None = None,
        real_party_in_interest_name_q: str | None = None,
        document_category_q: str | None = None,
        additional_query_params: dict[str, Any] | None = None,
    ) -> PTABTrialDocumentResponse:
        """Search for PTAB trial decisions.

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
            document_type_description_q: Filter by "*[description]*".
            decision_date_from_q: Filter decisions from this date (YYYY-MM-DD).
            decision_date_to_q: Filter decisions to this date (YYYY-MM-DD).
            trial_type_code_q: Filter by trial type code (e.g., "IPR", "PGR", "CBM", "DER").
            patent_number_q: Filter by patent number.
            application_number_q: Filter by application number.
            patent_owner_name_q: Filter by patent owner name.
            trial_status_category_q: Filter by trial status category.
            real_party_in_interest_name_q: Filter by real party in interest name.
            document_category_q: Filter by document category.
            additional_query_params: Additional custom query parameters.

        Returns:
            PTABTrialDocumentResponse: Response containing matching trial decisions.

        Examples:
            # Search with direct query
            >>> response = client.search_decisions(query="trialNumber:IPR2023-00001")

            # Search with convenience parameters
            >>> response = client.search_decisions(
            ...     decision_type_category_q="Final Written Decision",
            ...     decision_date_from_q="2023-01-01",
            ...     limit=50
            ... )
        """
        q_parts = []
        if trial_number_q:
            q_parts.append(f"trialNumber:{trial_number_q}")
        if decision_type_category_q:
            q_parts.append(
                f'decisionData.decisionTypeCategory:"{decision_type_category_q}"'
            )
        if document_type_description_q:
            q_parts.append(
                f'documentData.documentTypeDescriptionText:"*{document_type_description_q}*"'
            )
        if trial_type_code_q:
            q_parts.append(f"trialMetaData.trialTypeCode:{trial_type_code_q}")
        if patent_number_q:
            q_parts.append(f"patentOwnerData.patentNumber:{patent_number_q}")
        if application_number_q:
            q_parts.append(
                f"patentOwnerData.applicationNumberText:{application_number_q}"
            )
        if patent_owner_name_q:
            q_parts.append(f'patentOwnerData.patentOwnerName:"{patent_owner_name_q}"')
        if trial_status_category_q:
            q_parts.append(
                f'trialMetaData.trialStatusCategory:"{trial_status_category_q}"'
            )
        if real_party_in_interest_name_q:
            q_parts.append(
                f'regularPetitionerData.realPartyInInterestName:"{real_party_in_interest_name_q}"'
            )
        if document_category_q:
            q_parts.append(f'documentData.documentCategory:"{document_category_q}"')

        if decision_date_from_q and decision_date_to_q:
            q_parts.append(
                f"decisionData.decisionIssueDate:[{decision_date_from_q} TO {decision_date_to_q}]"
            )
        elif decision_date_from_q:
            q_parts.append(f"decisionData.decisionIssueDate:>={decision_date_from_q}")
        elif decision_date_to_q:
            q_parts.append(f"decisionData.decisionIssueDate:<={decision_date_to_q}")

        return self._perform_search(
            endpoint_key="search_decisions",
            response_class=PTABTrialDocumentResponse,
            query=query,
            query_parts=q_parts,
            post_body=post_body,
            sort=sort,
            offset=offset,
            limit=limit,
            facets=facets,
            fields=fields,
            filters=filters,
            range_filters=range_filters,
            additional_params=additional_query_params,
        )  # type: ignore

    def paginate_proceedings(
        self, post_body: dict[str, Any] | None = None, **kwargs: Any
    ) -> Iterator[PTABTrialProceeding]:
        """Provide an iterator to paginate through trial proceeding search results.

        Supports both GET and POST requests.

        Args:
            post_body: Optional POST body for complex search queries
            **kwargs: Keyword arguments for GET-based pagination

        Yields:
            PTABTrialProceeding objects
        """
        return self.paginate_results(
            method_name="search_proceedings",
            response_container_attr="patent_trial_proceeding_data_bag",
            post_body=post_body,
            **kwargs,
        )

    def download_trial_archive(
        self,
        trial_meta_data: TrialMetaData,
        destination: str | None = None,
        file_name: str | None = None,
        overwrite: bool = False,
    ) -> str:
        """Download trial archive (ZIP/TAR) without extraction.

        Args:
            trial_meta_data: TrialMetaData with file_download_uri
            destination: Directory to save to
            file_name: Override filename
            overwrite: Overwrite existing file

        Returns:
            Path to downloaded archive file

        Raises:
            ValueError: If trial_meta_data has no file_download_uri
        """
        if not trial_meta_data.file_download_uri:
            raise ValueError("TrialMetaData has no file_download_uri")

        return self._download_file(
            url=trial_meta_data.file_download_uri,
            destination=destination,
            file_name=file_name,
            overwrite=overwrite,
        )

    def download_trial_documents(
        self,
        trial_meta_data: TrialMetaData,
        destination: str | None = None,
        overwrite: bool = False,
    ) -> str:
        """Download and extract all trial documents.

        Args:
            trial_meta_data: TrialMetaData with file_download_uri
            destination: Directory to save/extract to
            overwrite: Overwrite existing files

        Returns:
            Path to extraction directory

        Raises:
            ValueError: If trial_meta_data has no file_download_uri
        """
        if not trial_meta_data.file_download_uri:
            raise ValueError("TrialMetaData has no file_download_uri")

        return self._download_and_extract(
            url=trial_meta_data.file_download_uri,
            destination=destination,
            overwrite=overwrite,
        )

    def download_trial_document(
        self,
        document_data: TrialDocumentData,
        destination: str | None = None,
        file_name: str | None = None,
        overwrite: bool = False,
    ) -> str:
        """Download individual trial document (auto-extracts if needed).

        Args:
            document_data: TrialDocumentData with file_download_uri
            destination: Directory to save to
            file_name: Override filename
            overwrite: Overwrite existing file

        Returns:
            Path to downloaded file

        Raises:
            ValueError: If document_data has no file_download_uri
        """
        if not document_data.file_download_uri:
            raise ValueError("TrialDocumentData has no file_download_uri")

        return self._download_and_extract(
            url=document_data.file_download_uri,
            destination=destination,
            file_name=file_name,
            overwrite=overwrite,
        )
