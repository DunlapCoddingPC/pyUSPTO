"""
clients.petition_decisions - Client for USPTO Final Petition Decisions API

This module provides a client for interacting with the USPTO Final Petition
Decisions API. It allows you to search for and retrieve final agency petition
decisions in publicly available patent applications and patents filed in 2001 or later.
"""

from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Union

import requests

from pyUSPTO.clients.base import BaseUSPTOClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.petition_decisions import (
    DocumentDownloadOption,
    PetitionDecision,
    PetitionDecisionDownloadResponse,
    PetitionDecisionResponse,
)


class FinalPetitionDecisionsClient(BaseUSPTOClient[PetitionDecisionResponse]):
    """Client for interacting with the USPTO Final Petition Decisions API.

    This client provides methods to search for petition decisions, retrieve specific
    decisions by ID, download decision data, and download associated documents.

    Final petition decisions data are incrementally added to the USPTO Open Data Portal
    on a monthly basis starting with data from 2022 and later.
    """

    ENDPOINTS = {
        "search_decisions": "api/v1/petition/decisions/search",
        "get_decision_by_id": "api/v1/petition/decisions/{petitionDecisionRecordIdentifier}",
        "download_decisions": "api/v1/petition/decisions/search/download",
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        config: Optional[USPTOConfig] = None,
    ):
        """Initialize the FinalPetitionDecisionsClient.

        Args:
            api_key: Optional API key for authentication.
            base_url: Optional base URL override for the API.
            config: Optional USPTOConfig instance for configuration.
        """
        self.config = config or USPTOConfig(api_key=api_key)
        api_key_to_use = api_key or self.config.api_key
        effective_base_url = (
            base_url
            or self.config.petition_decisions_base_url
            or "https://api.uspto.gov"
        )
        super().__init__(api_key=api_key_to_use, base_url=effective_base_url)

    def _get_decision_from_response(
        self,
        response_data: PetitionDecisionResponse,
        petition_decision_record_identifier_for_validation: Optional[str] = None,
    ) -> Optional[PetitionDecision]:
        """Helper to extract a single PetitionDecision from response.

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
            print(
                f"Warning: Fetched decision identifier '{decision.petition_decision_record_identifier}' "
                f"does not match requested '{petition_decision_record_identifier_for_validation}'."
            )
        return decision

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
        application_number_q: Optional[str] = None,
        patent_number_q: Optional[str] = None,
        inventor_name_q: Optional[str] = None,
        applicant_name_q: Optional[str] = None,
        invention_title_q: Optional[str] = None,
        decision_type_code_q: Optional[str] = None,
        decision_date_from_q: Optional[str] = None,
        decision_date_to_q: Optional[str] = None,
        petition_mail_date_from_q: Optional[str] = None,
        petition_mail_date_to_q: Optional[str] = None,
        technology_center_q: Optional[str] = None,
        final_deciding_office_name_q: Optional[str] = None,
        additional_query_params: Optional[Dict[str, Any]] = None,
    ) -> PetitionDecisionResponse:
        """Searches for final petition decisions.

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
            application_number_q: Filter by application number.
            patent_number_q: Filter by patent number.
            inventor_name_q: Filter by inventor name.
            applicant_name_q: Filter by applicant name.
            invention_title_q: Filter by invention title.
            decision_type_code_q: Filter by decision type code.
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
            ...     post_body={"q": "technologyCenter:1700", "limit": 100}
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
                response_class=PetitionDecisionResponse,
            )
        else:
            # GET request path
            params: Dict[str, Any] = {}
            final_q = query

            # Build query from convenience parameters
            if final_q is None:
                q_parts = []
                if application_number_q:
                    q_parts.append(f"applicationNumberText:{application_number_q}")
                if patent_number_q:
                    q_parts.append(f"patentNumber:{patent_number_q}")
                if inventor_name_q:
                    q_parts.append(f"inventorBag:{inventor_name_q}")
                if applicant_name_q:
                    q_parts.append(f"firstApplicantName:{applicant_name_q}")
                if invention_title_q:
                    q_parts.append(f"inventionTitle:{invention_title_q}")
                if decision_type_code_q:
                    q_parts.append(f"decisionTypeCode:{decision_type_code_q}")
                if technology_center_q:
                    q_parts.append(f"technologyCenter:{technology_center_q}")
                if final_deciding_office_name_q:
                    q_parts.append(
                        f"finalDecidingOfficeName:{final_deciding_office_name_q}"
                    )

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

            result = self._make_request(
                method="GET",
                endpoint=endpoint,
                params=params,
                response_class=PetitionDecisionResponse,
            )

        assert isinstance(result, PetitionDecisionResponse)
        return result

    def get_decision_by_id(
        self,
        petition_decision_record_identifier: str,
        include_documents: Optional[bool] = None,
    ) -> Optional[PetitionDecision]:
        """Retrieves a specific petition decision by its record identifier.

        Args:
            petition_decision_record_identifier: The unique identifier for the petition
                decision record (UUID format).
            include_documents: Whether to include associated documents in the response.
                If True, adds includeDocuments=true query parameter.

        Returns:
            Optional[PetitionDecision]: The petition decision if found, None otherwise.

        Examples:
            # Get decision without documents
            >>> decision = client.get_decision_by_id(
            ...     "9f1a4a2b-eee1-58ec-a3aa-167c4075aed4"
            ... )

            # Get decision with documents
            >>> decision = client.get_decision_by_id(
            ...     "34044333-4b40-515f-a684-2515325c57c5",
            ...     include_documents=True
            ... )
        """
        endpoint = self.ENDPOINTS["get_decision_by_id"].format(
            petitionDecisionRecordIdentifier=petition_decision_record_identifier
        )

        params = {}
        if include_documents is not None:
            params["includeDocuments"] = str(include_documents).lower()

        response_data = self._make_request(
            method="GET",
            endpoint=endpoint,
            params=params if params else None,
            response_class=PetitionDecisionResponse,
        )
        assert isinstance(response_data, PetitionDecisionResponse)
        return self._get_decision_from_response(
            response_data=response_data,
            petition_decision_record_identifier_for_validation=petition_decision_record_identifier,
        )

    def download_decisions(
        self,
        format: str = "json",
        query: Optional[str] = None,
        sort: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        fields: Optional[str] = None,
        filters: Optional[str] = None,
        range_filters: Optional[str] = None,
        # Convenience query parameters
        application_number_q: Optional[str] = None,
        patent_number_q: Optional[str] = None,
        inventor_name_q: Optional[str] = None,
        applicant_name_q: Optional[str] = None,
        decision_date_from_q: Optional[str] = None,
        decision_date_to_q: Optional[str] = None,
        additional_query_params: Optional[Dict[str, Any]] = None,
        # File save options (for CSV format)
        file_name: Optional[str] = None,
        destination_path: Optional[str] = None,
        overwrite: bool = False,
    ) -> Union[PetitionDecisionDownloadResponse, requests.Response, str]:
        """Downloads petition decisions data in the specified format.

        This endpoint is designed for bulk downloads of petition decisions data.
        It supports JSON and CSV formats.

        Args:
            format: Download format, either "json" or "csv". Defaults to "json".
            query: Direct query string in USPTO search syntax.
            sort: Sort order for results.
            offset: Number of records to skip (pagination).
            limit: Maximum number of records to return.
            fields: Specific fields to return.
            filters: Filter configuration string.
            range_filters: Range filter configuration string.
            application_number_q: Filter by application number.
            patent_number_q: Filter by patent number.
            inventor_name_q: Filter by inventor name.
            applicant_name_q: Filter by applicant name.
            decision_date_from_q: Filter decisions from this date (YYYY-MM-DD).
            decision_date_to_q: Filter decisions to this date (YYYY-MM-DD).
            additional_query_params: Additional custom query parameters.
            file_name: Optional filename for CSV downloads. Defaults to "petition_decisions.csv".
            destination_path: Optional directory path to save CSV file. If None, returns Response.
            overwrite: Whether to overwrite existing files. Default False.

        Returns:
            Union[PetitionDecisionDownloadResponse, requests.Response, str]:
                - If format="json": Returns PetitionDecisionDownloadResponse
                - If format="csv" and destination_path is None: Returns streaming Response
                - If format="csv" and destination_path is set: Returns str path to saved file

        Raises:
            FileExistsError: If CSV file exists and overwrite=False

        Examples:
            # Download as JSON
            >>> download = client.download_decisions(
            ...     format="json",
            ...     technology_center_q="1700",
            ...     limit=1000
            ... )
            >>> for decision in download.petition_decision_data:
            ...     print(decision.application_number_text)

            # Download CSV and save to file
            >>> file_path = client.download_decisions(
            ...     format="csv",
            ...     decision_date_from_q="2023-01-01",
            ...     destination_path="./downloads"
            ... )
            >>> print(f"Saved to: {file_path}")

            # Download CSV as streaming response (advanced usage)
            >>> response = client.download_decisions(format="csv")
            >>> with open("decisions.csv", "wb") as f:
            ...     for chunk in response.iter_content(chunk_size=8192):
            ...         f.write(chunk)
        """
        endpoint = self.ENDPOINTS["download_decisions"]

        params: Dict[str, Any] = {"format": format}
        final_q = query

        # Build query from convenience parameters
        if final_q is None:
            q_parts = []
            if application_number_q:
                q_parts.append(f"applicationNumberText:{application_number_q}")
            if patent_number_q:
                q_parts.append(f"patentNumber:{patent_number_q}")
            if inventor_name_q:
                q_parts.append(f"inventorBag:{inventor_name_q}")
            if applicant_name_q:
                q_parts.append(f"firstApplicantName:{applicant_name_q}")

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

        if format.lower() == "json":
            # For JSON, parse the response
            result_dict = self._make_request(
                method="GET", endpoint=endpoint, params=params
            )
            assert isinstance(result_dict, dict)
            return PetitionDecisionDownloadResponse.from_dict(result_dict)
        else:
            # For CSV or other formats, get streaming response
            result = self._make_request(
                method="GET", endpoint=endpoint, params=params, stream=True
            )
            assert isinstance(result, requests.Response)

            if destination_path is not None:
                # Save to file using the base class helper
                from pathlib import Path

                # Determine filename
                if file_name is None:
                    file_name = "petition_decisions.csv"

                # Build full file path
                destination_dir = Path(destination_path)
                destination_dir.mkdir(parents=True, exist_ok=True)
                final_file_path = destination_dir / file_name

                # Save streaming response to file (overwrite check handled by base class)
                return self._save_response_to_file(
                    response=result, file_path=str(final_file_path), overwrite=overwrite
                )
            else:
                # Return streaming response for manual handling
                return result

    def paginate_decisions(self, **kwargs: Any) -> Iterator[PetitionDecision]:
        """Provides an iterator to paginate through petition decision search results.

        This method simplifies fetching all petition decisions matching a search query
        by automatically handling pagination. It internally calls the search_decisions
        method for GET requests, batching results and yielding them one by one.

        All keyword arguments are passed directly to search_decisions to define the
        search criteria. The offset and limit parameters are managed by the pagination
        logic; setting them directly in kwargs might lead to unexpected behavior.

        Args:
            **kwargs: Keyword arguments passed to search_decisions for constructing
                the search query. Do not include post_body.

        Returns:
            Iterator[PetitionDecision]: An iterator yielding PetitionDecision objects,
                allowing iteration over all matching petition decisions across multiple
                pages of results.

        Raises:
            ValueError: If post_body is included in kwargs, as this method only
                supports GET request parameters for pagination.

        Examples:
            # Paginate through all decisions for a technology center
            >>> for decision in client.paginate_decisions(technology_center_q="1700"):
            ...     print(f"{decision.application_number_text}: {decision.decision_type_code}")

            # Paginate with date range
            >>> for decision in client.paginate_decisions(
            ...     decision_date_from_q="2023-01-01",
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
            response_container_attr="petition_decision_data_bag",
            **kwargs,
        )

    def download_petition_document(
        self,
        download_option: DocumentDownloadOption,
        file_name: Optional[str] = None,
        destination_path: Optional[str] = None,
        overwrite: bool = False,
    ) -> str:
        """Downloads a petition decision document in the specified format.

        Args:
            download_option: DocumentDownloadOption object containing the download
                URL and metadata.
            file_name: Optional filename for the downloaded file. If not provided,
                it will be extracted from the URL or generated based on the MIME type.
            destination_path: Optional directory path where the file should be saved.
                If not provided, saves to the current directory.
            overwrite: Whether to overwrite an existing file. Defaults to False.

        Returns:
            str: The absolute path to the downloaded file.

        Raises:
            ValueError: If download_option has no download URL.
            FileExistsError: If the file exists and overwrite=False.

        Examples:
            # Download first document from a decision
            >>> decision = client.get_decision_by_id(
            ...     "34044333-4b40-515f-a684-2515325c57c5",
            ...     include_documents=True
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
            ...             destination_path="./downloads"
            ...         )
            ...         print(f"Downloaded to: {path}")
        """
        if download_option.download_url is None:
            raise ValueError("DocumentDownloadOption must have a download_url")

        # Determine filename
        if file_name is None:
            url_filename = download_option.download_url.split("/")[-1]
            if "." in url_filename:
                file_name = url_filename
            else:
                # Generate filename from MIME type
                extension = (
                    download_option.mime_type_identifier.lower()
                    if download_option.mime_type_identifier
                    else "pdf"
                )
                file_name = f"document.{extension}"

        # Determine final file path
        if destination_path is None:
            final_file_path = Path(file_name)
        else:
            destination_dir = Path(destination_path)
            destination_dir.mkdir(parents=True, exist_ok=True)
            final_file_path = destination_dir / file_name

        # Check for existing file
        if final_file_path.exists() and overwrite is False:
            raise FileExistsError(
                f"File already exists: {final_file_path}. Use overwrite=True to replace."
            )

        # Download the file
        return self._download_file(
            url=download_option.download_url, file_path=final_file_path.as_posix()
        )
