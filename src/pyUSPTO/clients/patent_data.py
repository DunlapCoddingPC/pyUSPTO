"""
clients.patent_data - Client for USPTO patent data API

This module provides a client for interacting with the USPTO Patent Data API.
It allows you to search for and retrieve patent application data.
"""

from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional
from urllib.parse import urljoin, urlparse

from pyUSPTO.clients.base import BaseUSPTOClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.patent_data import (
    ApplicationContinuityData,
    ApplicationMetaData,
    Assignment,
    ChildContinuity,
    DocumentBag,
    DocumentFormat,
    EventData,
    ForeignPriority,
    ParentContinuity,
    PatentDataResponse,
    PatentFileWrapper,
    PatentTermAdjustmentData,
    PrintedMetaData,
    PrintedPublication,
    RecordAttorney,
    StatusCodeCollection,
    StatusCodeSearchResponse,
)


class PatentDataClient(BaseUSPTOClient[PatentDataResponse]):
    """Client for interacting with the USPTO Patent Data API."""

    ENDPOINTS = {
        "search_applications": "api/v1/patent/applications/search",
        "get_search_results": "api/v1/patent/applications/search/download",
        "get_application_by_number": "api/v1/patent/applications/{application_number}",
        "get_application_metadata": "api/v1/patent/applications/{application_number}/meta-data",
        "get_application_adjustment": "api/v1/patent/applications/{application_number}/adjustment",
        "get_application_assignment": "api/v1/patent/applications/{application_number}/assignment",
        "get_application_attorney": "api/v1/patent/applications/{application_number}/attorney",
        "get_application_continuity": "api/v1/patent/applications/{application_number}/continuity",
        "get_application_foreign_priority": "api/v1/patent/applications/{application_number}/foreign-priority",
        "get_application_transactions": "api/v1/patent/applications/{application_number}/transactions",
        "get_application_documents": "api/v1/patent/applications/{application_number}/documents",
        "get_application_associated_documents": "api/v1/patent/applications/{application_number}/associated-documents",
        "download_application_document": "api/v1/download/applications/{application_number}/{document_id}",
        "status_codes": "api/v1/patent/status-codes",
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        config: Optional[USPTOConfig] = None,
    ):
        self.config = config or USPTOConfig(api_key=api_key)
        api_key_to_use = api_key or self.config.api_key
        effective_base_url = (
            base_url or self.config.patent_data_base_url or "https://api.uspto.gov"
        )
        super().__init__(api_key=api_key_to_use, base_url=effective_base_url)

    # TODO: def sanitize_application_no(inputNumber: str) -> str:

    def _get_wrapper_from_response(
        self,
        response_data: PatentDataResponse,
        application_number_for_validation: Optional[str] = None,
    ) -> Optional[PatentFileWrapper]:
        """Helper to extract a single PatentFileWrapper, optionally validating the app number."""
        if not response_data or not response_data.patent_file_wrapper_data_bag:
            return None

        wrapper = response_data.patent_file_wrapper_data_bag[0]

        if (
            application_number_for_validation
            and wrapper.application_number_text != application_number_for_validation
        ):
            print(
                f"Warning: Fetched wrapper application number '{wrapper.application_number_text}' "
                f"does not match requested '{application_number_for_validation}'."
            )
        return wrapper

    def search_applications(
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
        application_number_q: Optional[str] = None,
        patent_number_q: Optional[str] = None,
        inventor_name_q: Optional[str] = None,
        applicant_name_q: Optional[str] = None,
        assignee_name_q: Optional[str] = None,
        filing_date_from_q: Optional[str] = None,
        filing_date_to_q: Optional[str] = None,
        grant_date_from_q: Optional[str] = None,
        grant_date_to_q: Optional[str] = None,
        classification_q: Optional[str] = None,
        earliestPublicationNumber_q: Optional[str] = None,
        pctPublicationNumber_q: Optional[str] = None,
        additional_query_params: Optional[Dict[str, Any]] = None,
    ) -> PatentDataResponse:
        """
        Searches for patent applications.
        Can perform a GET request based on OpenAPI query parameters or a POST request if post_body is specified.
        """
        endpoint = self.ENDPOINTS["search_applications"]

        if post_body is not None:
            result = self._make_request(
                method="POST",
                endpoint=endpoint,
                json_data=post_body,
                params=additional_query_params,
                response_class=PatentDataResponse,
            )
        else:
            params: Dict[str, Any] = {}
            final_q = query

            if final_q is None:
                q_parts = []
                if application_number_q:
                    q_parts.append(f"applicationNumberText:{application_number_q}")
                if patent_number_q:
                    q_parts.append(
                        f"applicationMetaData.patentNumber:{patent_number_q}"
                    )
                if inventor_name_q:
                    q_parts.append(
                        f"applicationMetaData.inventorBag.inventorNameText:{inventor_name_q}"
                    )
                if applicant_name_q:
                    q_parts.append(
                        f"applicationMetaData.firstApplicantName:{applicant_name_q}"
                    )
                if assignee_name_q:
                    q_parts.append(
                        f"assignmentBag.assigneeBag.assigneeNameText:{assignee_name_q}"
                    )
                if classification_q:
                    q_parts.append(
                        f"applicationMetaData.cpcClassificationBag:{classification_q}"
                    )
                if earliestPublicationNumber_q:
                    q_parts.append(
                        f"applicationMetaData.earliestPublicationNumber:{earliestPublicationNumber_q}"
                    )
                if pctPublicationNumber_q:
                    q_parts.append(
                        f"applicationMetaData.pctPublicationNumber:{pctPublicationNumber_q}"
                    )
                if filing_date_from_q and filing_date_to_q:
                    q_parts.append(
                        f"applicationMetaData.filingDate:[{filing_date_from_q} TO {filing_date_to_q}]"
                    )
                elif filing_date_from_q:
                    q_parts.append(
                        f"applicationMetaData.filingDate:>={filing_date_from_q}"
                    )
                elif filing_date_to_q:
                    q_parts.append(
                        f"applicationMetaData.filingDate:<={filing_date_to_q}"
                    )

                if grant_date_from_q and grant_date_to_q:
                    q_parts.append(
                        f"applicationMetaData.grantDate:[{grant_date_from_q} TO {grant_date_to_q}]"
                    )
                elif grant_date_from_q:
                    q_parts.append(
                        f"applicationMetaData.grantDate:>={grant_date_from_q}"
                    )
                elif grant_date_to_q:
                    q_parts.append(f"applicationMetaData.grantDate:<={grant_date_to_q}")

                if q_parts:
                    final_q = " AND ".join(q_parts)

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
                response_class=PatentDataResponse,
            )
        assert isinstance(result, PatentDataResponse)
        return result

    def get_search_results(
        self,
        query: Optional[str] = None,
        sort: Optional[str] = None,
        offset: Optional[int] = 0,
        limit: Optional[int] = 25,
        fields_param: Optional[str] = None,
        filters_param: Optional[str] = None,
        range_filters_param: Optional[str] = None,
        post_body: Optional[Dict[str, Any]] = None,
        application_number_q: Optional[str] = None,
        patent_number_q: Optional[str] = None,
        inventor_name_q: Optional[str] = None,
        applicant_name_q: Optional[str] = None,
        assignee_name_q: Optional[str] = None,
        filing_date_from_q: Optional[str] = None,
        filing_date_to_q: Optional[str] = None,
        grant_date_from_q: Optional[str] = None,
        grant_date_to_q: Optional[str] = None,
        classification_q: Optional[str] = None,
        additional_query_params: Optional[Dict[str, Any]] = None,
    ) -> PatentDataResponse:
        """
        Fetches a dataset of patent applications based on search criteria, always requesting JSON format.
        For GET, parameters align with OpenAPI for /api/v1/patent/applications/search/download.
        For POST, post_body should conform to PatentDownloadRequest schema.
        """
        endpoint = self.ENDPOINTS["get_search_results"]

        if post_body is not None:
            if "format" not in post_body:
                post_body["format"] = "json"

            result = self._make_request(
                method="POST",
                endpoint=endpoint,
                json_data=post_body,
                params=additional_query_params,
                response_class=PatentDataResponse,
            )
        else:
            params: Dict[str, Any] = {}
            final_q = query

            if final_q is None:
                q_parts = []
                if application_number_q:
                    q_parts.append(f"applicationNumberText:{application_number_q}")
                if patent_number_q:
                    q_parts.append(
                        f"applicationMetaData.patentNumber:{patent_number_q}"
                    )
                if inventor_name_q:
                    q_parts.append(
                        f"applicationMetaData.inventorBag.inventorNameText:{inventor_name_q}"
                    )
                if applicant_name_q:
                    q_parts.append(
                        f"applicationMetaData.firstApplicantName:{applicant_name_q}"
                    )
                if assignee_name_q:
                    q_parts.append(
                        f"assignmentBag.assigneeBag.assigneeNameText:{assignee_name_q}"
                    )
                if classification_q:
                    q_parts.append(
                        f"applicationMetaData.cpcClassificationBag:{classification_q}"
                    )

                if filing_date_from_q and filing_date_to_q:
                    q_parts.append(
                        f"applicationMetaData.filingDate:[{filing_date_from_q} TO {filing_date_to_q}]"
                    )
                elif filing_date_from_q:
                    q_parts.append(
                        f"applicationMetaData.filingDate:>={filing_date_from_q}"
                    )
                elif filing_date_to_q:
                    q_parts.append(
                        f"applicationMetaData.filingDate:<={filing_date_to_q}"
                    )

                if grant_date_from_q and grant_date_to_q:
                    q_parts.append(
                        f"applicationMetaData.grantDate:[{grant_date_from_q} TO {grant_date_to_q}]"
                    )
                elif grant_date_from_q:
                    q_parts.append(
                        f"applicationMetaData.grantDate:>={grant_date_from_q}"
                    )
                elif grant_date_to_q:
                    q_parts.append(f"applicationMetaData.grantDate:<={grant_date_to_q}")

                if q_parts:
                    final_q = " AND ".join(q_parts)

            if final_q is not None:
                params["q"] = final_q
            if sort is not None:
                params["sort"] = sort
            if offset is not None:
                params["offset"] = offset
            if limit is not None:
                params["limit"] = limit
            if fields_param is not None:
                params["fields"] = fields_param
            if filters_param is not None:
                params["filters"] = filters_param
            if range_filters_param is not None:
                params["rangeFilters"] = range_filters_param

            params["format"] = "json"

            if additional_query_params:
                params.update(additional_query_params)

            result = self._make_request(
                method="GET",
                endpoint=endpoint,
                params=params,
                response_class=PatentDataResponse,
            )
        assert isinstance(result, PatentDataResponse)
        return result

    def get_application_by_number(
        self, application_number: str
    ) -> Optional[PatentFileWrapper]:
        """Retrieves the full details for a specific patent application by its number.

        This method fetches comprehensive information for a single patent application
        identified by its unique application number.

        Args:
            application_number (str): The USPTO application number for the patent
                application (e.g., "16123456").

        Returns:
            Optional[PatentFileWrapper]: A `PatentFileWrapper` object representing
                the complete file wrapper for the application if found. This object
                contains all data sections related to the application, such as
                metadata, addresses, assignments, attorney/agent data, continuity
                data, PTA/PTE data, transactions, and associated documents.
                Returns None if the application cannot be found or if the response
                does not contain the expected data.
        """
        endpoint = self.ENDPOINTS["get_application_by_number"].format(
            application_number=application_number
        )
        response_data = self._make_request(
            method="GET", endpoint=endpoint, response_class=PatentDataResponse
        )
        assert isinstance(response_data, PatentDataResponse)
        return self._get_wrapper_from_response(
            response_data=response_data,
            application_number_for_validation=application_number,
        )

    def get_application_metadata(
        self, application_number: str
    ) -> Optional[ApplicationMetaData]:
        """Retrieves key metadata for a specific patent application.

        This method fetches the `ApplicationMetaData` component from the full
        patent file wrapper. The metadata includes a wide range of information
        such as application status, important dates (filing, grant, publication),
        applicant and inventor details, classification data, and other core
        identifying information for the application.

        Args:
            application_number (str): The USPTO application number for which
                metadata is being requested (e.g., "16123456").

        Returns:
            Optional[ApplicationMetaData]: An `ApplicationMetaData` object
                containing the core details of the patent application if found.
                Returns None if the application cannot be found or if metadata
                is not available in the response.
        """
        endpoint = self.ENDPOINTS["get_application_metadata"].format(
            application_number=application_number
        )
        response_data = self._make_request(
            method="GET", endpoint=endpoint, response_class=PatentDataResponse
        )
        assert isinstance(response_data, PatentDataResponse)
        wrapper = self._get_wrapper_from_response(response_data, application_number)
        return wrapper.application_meta_data if wrapper else None

    def get_application_adjustment(
        self, application_number: str
    ) -> Optional[PatentTermAdjustmentData]:
        """Retrieves patent term adjustment (PTA) data for a specific application.

        This method fetches the `PatentTermAdjustmentData` component from the
        full patent file wrapper. This data includes details on various delay
        quantities (e.g., A, B, C delays, applicant delays), the total
        calculated adjustment, and a history of PTA events that influenced the
        term.

        Args:
            application_number (str): The USPTO application number for which PTA
                data is being requested (e.g., "16123456").

        Returns:
            Optional[PatentTermAdjustmentData]: A `PatentTermAdjustmentData`
                object containing the PTA details if the application is found
                and has such data. Returns None if the application cannot be
                found or if PTA data is not available in the response.
        """
        endpoint = self.ENDPOINTS["get_application_adjustment"].format(
            application_number=application_number
        )
        response_data = self._make_request(
            method="GET", endpoint=endpoint, response_class=PatentDataResponse
        )
        assert isinstance(response_data, PatentDataResponse)
        wrapper = self._get_wrapper_from_response(response_data, application_number)
        return wrapper.patent_term_adjustment_data if wrapper else None

    def get_application_assignment(
        self, application_number: str
    ) -> Optional[List[Assignment]]:
        """Retrieves a list of patent assignments for a specific application.

        This method fetches the `assignment_bag` from the patent file wrapper,
        which contains a list of `Assignment` objects. Each `Assignment` object
        details an assignment including information such as reel and frame numbers,
        recording dates, conveyance text, and details about the assignors and assignees.

        Args:
            application_number (str): The USPTO application number for which
                assignment data is being requested (e.g., "16123456").

        Returns:
            Optional[List[Assignment]]: A list of `Assignment` objects, each
                representing a recorded assignment for the application. Returns
                None if the application cannot be found, or if no assignment
                data is available in the response. An empty list may be
                returned if the application is found but has no recorded
                assignments.
        """
        endpoint = self.ENDPOINTS["get_application_assignment"].format(
            application_number=application_number
        )
        response_data = self._make_request(
            method="GET", endpoint=endpoint, response_class=PatentDataResponse
        )
        assert isinstance(response_data, PatentDataResponse)
        wrapper = self._get_wrapper_from_response(response_data, application_number)
        return wrapper.assignment_bag if wrapper else None

    def get_application_attorney(
        self, application_number: str
    ) -> Optional[RecordAttorney]:
        """Retrieves data for the attorney(s) of record for a specific application.

        This method fetches the `RecordAttorney` object associated with the
        patent application. This object contains details about the attorney(s)
        of record, including customer number correspondence data, power of attorney
        information, and a list of listed attorneys.

        Args:
            application_number (str): The USPTO application number for which
                attorney data is being requested (e.g., "16123456").

        Returns:
            Optional[RecordAttorney]: A `RecordAttorney` object with details
                about the attorney(s) of record if the application is found
                and such data exists. Returns None if the application cannot
                be found or if no attorney data is available in the response.
        """
        endpoint = self.ENDPOINTS["get_application_attorney"].format(
            application_number=application_number
        )
        response_data = self._make_request(
            method="GET", endpoint=endpoint, response_class=PatentDataResponse
        )
        assert isinstance(response_data, PatentDataResponse)
        wrapper = self._get_wrapper_from_response(response_data, application_number)
        return wrapper.record_attorney if wrapper else None

    def get_application_continuity(
        self, application_number: str
    ) -> Optional[ApplicationContinuityData]:
        """Retrieves continuity data (parent/child applications) for a specific application.

        This method fetches the lineage of the specified application, returning an
        `ApplicationContinuityData` object. This object consolidates lists of
        `ParentContinuity` (applications to which the current one claims priority)
        and `ChildContinuity` (applications claiming priority to the current one)
        objects, each detailing the related application's key identifiers and status.

        Args:
            application_number (str): The USPTO application number for which
                continuity data is being requested (e.g., "16123456").

        Returns:
            Optional[ApplicationContinuityData]: An `ApplicationContinuityData`
                object containing lists of parent and child continuity relationships.
                Returns None if the application cannot be found or if the underlying
                data to construct continuity is not available. The lists within
                the returned object may be empty if no parent or child continuity
                links exist.
        """
        endpoint = self.ENDPOINTS["get_application_continuity"].format(
            application_number=application_number
        )
        response_data = self._make_request(
            method="GET", endpoint=endpoint, response_class=PatentDataResponse
        )
        assert isinstance(response_data, PatentDataResponse)
        wrapper = self._get_wrapper_from_response(response_data, application_number)
        return ApplicationContinuityData.from_wrapper(wrapper) if wrapper else None

    def get_application_foreign_priority(
        self, application_number: str
    ) -> Optional[List[ForeignPriority]]:
        """Retrieves a list of foreign priority claims for a specific application.

        This method fetches the `foreign_priority_bag` from the patent file
        wrapper. This bag contains a list of `ForeignPriority` objects, each
        representing a claim to a foreign patent application's priority date.
        Details include the IP office name, filing date, and application number
        of the foreign priority application.

        Args:
            application_number (str): The USPTO application number for which
                foreign priority data is being requested (e.g., "16123456").

        Returns:
            Optional[List[ForeignPriority]]: A list of `ForeignPriority` objects,
                each detailing a claimed foreign priority. Returns None if the
                application cannot be found or if no foreign priority data is
                available. An empty list may be returned if the application
                is found but has no foreign priority claims.
        """
        endpoint = self.ENDPOINTS["get_application_foreign_priority"].format(
            application_number=application_number
        )
        response_data = self._make_request(
            method="GET", endpoint=endpoint, response_class=PatentDataResponse
        )
        assert isinstance(response_data, PatentDataResponse)
        wrapper = self._get_wrapper_from_response(response_data, application_number)
        return wrapper.foreign_priority_bag if wrapper else None

    def get_application_transactions(
        self, application_number: str
    ) -> Optional[List[EventData]]:
        """Retrieves the transaction history (events) for a specific application.

        This method fetches the `event_data_bag` from the patent file wrapper.
        This bag contains a list of `EventData` objects, each representing a
        single recorded event in the prosecution history of the patent application.
        Events include details like an event code, a textual description, and
        the date the event was recorded.

        Args:
            application_number (str): The USPTO application number for which
                transaction history is being requested (e.g., "16123456").

        Returns:
            Optional[List[EventData]]: A list of `EventData` objects, each
                detailing a transaction or event in the application's history.
                Returns None if the application cannot be found or if no
                transaction data is available. An empty list may be returned if
                the application is found but has no recorded transaction events.
        """
        endpoint = self.ENDPOINTS["get_application_transactions"].format(
            application_number=application_number
        )
        response_data = self._make_request(
            method="GET", endpoint=endpoint, response_class=PatentDataResponse
        )
        assert isinstance(response_data, PatentDataResponse)
        wrapper = self._get_wrapper_from_response(response_data, application_number)
        return wrapper.event_data_bag if wrapper else None

    def get_application_documents(self, application_number: str) -> DocumentBag:
        """Retrieves metadata for documents associated with a specific application.

        This method fetches a collection of document metadata related to the given
        patent application. The result is a `DocumentBag` object, which is an
        iterable collection of `Document` instances. Each `Document` object
        contains metadata such as its identifier, official date, document code
        and description, direction (incoming/outgoing), and available download
        formats.

        Args:
            application_number (str): The USPTO application number for which
                document metadata is being requested (e.g., "16123456").

        Returns:
            DocumentBag: A `DocumentBag` object containing metadata for all
                publicly available documents associated with the application.
                The bag will be empty if no documents are found or if the
                API response indicates no documents. It does not return None
                for "not found" cases; an empty collection is returned instead.
        """
        endpoint = self.ENDPOINTS["get_application_documents"].format(
            application_number=application_number
        )
        result_dict = self._make_request(method="GET", endpoint=endpoint)
        assert isinstance(result_dict, dict)
        return DocumentBag.from_dict(result_dict)

    def get_application_associated_documents(
        self, application_number: str
    ) -> Optional[PrintedPublication]:
        """Retrieves metadata for Pre-Grant Publication and Grant documents.

        This method fetches metadata specifically for published documents associated
        with the patent application, such as Pre-Grant Publications (PGPUBs)
        and granted patent documents. It does not retrieve the prosecution
        history documents (see `get_application_documents` for that).
        The result is a `PrintedPublication` object, which holds
        `PrintedMetaData` including file URIs and names. Download with download_archive.

        Args:
            application_number (str): The USPTO application number for which
                associated PGPUB/Grant document metadata is being requested
                (e.g., "16123456").

        Returns:
            Optional[PrintedPublication]: A `PrintedPublication` object
                containing `PrintedMetaData` for the Pre-Grant Publication
                and/or the Grant document, if available. Returns None if the
                application cannot be found or if no such associated document
                metadata is available. The fields within the returned object
                (`pgpub_document_meta_data`, `grant_document_meta_data`)
                may themselves be None if a particular type of document
                (e.g., PGPUB) does not exist for the application.
        """
        endpoint = self.ENDPOINTS["get_application_associated_documents"].format(
            application_number=application_number
        )
        response_data = self._make_request(
            method="GET", endpoint=endpoint, response_class=PatentDataResponse
        )
        assert isinstance(response_data, PatentDataResponse)
        wrapper = self._get_wrapper_from_response(response_data, application_number)
        return PrintedPublication.from_wrapper(wrapper) if wrapper else None

    def paginate_applications(self, **kwargs: Any) -> Iterator[PatentFileWrapper]:
        """Provides an iterator to easily paginate through patent application search results.

        This method simplifies the process of fetching all patent applications
        that match a given search query by automatically handling pagination.
        It internally calls the `search_applications` method for GET requests,
        batching results and yielding them one by one.

        All keyword arguments provided to this method (`**kwargs`) are passed
        directly to the `search_applications` method to define the search
        criteria. See the `search_applications` method for more details
        on available parameters.
        The `offset` and `limit` parameters are managed by the pagination logic;
        setting them directly in `kwargs` might lead to unexpected behavior.

        Args:
            **kwargs (Any): Keyword arguments to be passed to the
                `search_applications` method for constructing the search query.
                These define the criteria for the patent applications to be
                retrieved. Do not include `post_body`.

        Returns:
            Iterator[PatentFileWrapper]: An iterator that yields `PatentFileWrapper`
                objects, allowing iteration over all matching patent applications
                across multiple pages of results.

        Raises:
            ValueError: If `post_body` is included in `kwargs`, as this
                method only supports GET request parameters for pagination.
        """
        if "post_body" in kwargs:
            raise ValueError(
                "paginate_applications uses GET requests and does not support 'post_body'. "
                "Use keyword arguments for search criteria."
            )

        return self.paginate_results(
            method_name="search_applications",
            response_container_attr="patent_file_wrapper_data_bag",
            **kwargs,
        )

    def get_status_codes(
        self, params: Optional[Dict[str, Any]] = None
    ) -> StatusCodeSearchResponse:
        """Retrieves USPTO patent application status codes and their descriptions.

        This method fetches a list of defined USPTO patent application status codes
        (e.g., codes for "Pending," "Abandoned," "Issued") using a GET request.
        The request can be customized with query parameters to filter or paginate
        the results if supported by the API endpoint.

        Args:
            params (Optional[Dict[str, Any]], optional): A dictionary of query
                parameters to be sent with the GET request. These parameters can
                be used to filter or control the output of the status codes
                list. Defaults to None, which typically retrieves all available
                status codes or the API's default set.

        Returns:
            StatusCodeSearchResponse: An object containing a count of matching
                status codes, a `StatusCodeCollection` of the `StatusCode`
                objects (code and description), and a request identifier.
        """
        result_dict = self._make_request(
            method="GET", endpoint=self.ENDPOINTS["status_codes"], params=params
        )
        assert isinstance(result_dict, dict)
        return StatusCodeSearchResponse.from_dict(result_dict)

    def search_status_codes(
        self, search_request: Dict[str, Any]
    ) -> StatusCodeSearchResponse:
        """Searches USPTO patent application status codes using POST criteria.

        Performs targeted searches for USPTO patent application status codes
        (e.g., for "Pending," "Abandoned," "Issued") by sending a POST request
        with a JSON body containing the `search_request` criteria. This method
        is suited for more complex queries than the GET-based `get_status_codes`.

        Args:
            search_request (Dict[str, Any]): A dictionary with search criteria,
                sent as the JSON POST body. The structure must conform to USPTO
                API requirements for this endpoint (e.g., for searching by code
                or description keywords).

        Returns:
            StatusCodeSearchResponse: An object containing a count of matching
                status codes, a `StatusCodeCollection` of the `StatusCode`
                objects (code and description), and a request identifier.
        """
        result_dict = self._make_request(
            method="POST",
            endpoint=self.ENDPOINTS["status_codes"],
            json_data=search_request,
        )
        assert isinstance(result_dict, dict)
        return StatusCodeSearchResponse.from_dict(result_dict)

    def download_document(
        self,
        document_format: DocumentFormat,
        file_name: Optional[str] = None,
        destination_path: Optional[str] = None,
        overwrite: bool = False,
        stream: bool = True,
    ) -> str:
        """Downloads a document in the specified format.

        Args:
            document_format: DocumentFormat object containing download URL and metadata
            file_name: Optional filename. If not provided, extracted from URL
            destination_path: Optional path - can be a directory OR a complete file path
            overwrite: Whether to overwrite existing files. Default False
            stream: Whether to stream the download. Default True for large files

        Returns:
            str: Path to the downloaded file

        Raises:
            ValueError: If document_format has no download URL
            FileExistsError: If file exists and overwrite=False
        """
        # Validate we have a download URL
        if document_format.download_url is None:
            raise ValueError("DocumentFormat must have a download_url")

        # Get filename - either provided or extract from URL
        if file_name is None:
            url_filename = document_format.download_url.split("/")[-1]
            if "." in url_filename:
                file_name = url_filename
            else:
                extension = (
                    document_format.mime_type_identifier.lower()
                    if document_format.mime_type_identifier
                    else "pdf"
                )
                file_name = f"document.{extension}"

        # Determine final file path
        if destination_path is None:
            final_file_path = Path(file_name)
        else:
            # destination_path is ALWAYS treated as a directory path
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
            url=document_format.download_url, file_path=final_file_path.as_posix()
        )

    def get_IFW_metadata(
        self,
        application_number: Optional[str] = None,
        publication_number: Optional[str] = None,
        patent_number: Optional[str] = None,
        PCT_app_number: Optional[str] = None,
        PCT_pub_number: Optional[str] = None,
    ) -> Optional[PatentFileWrapper]:
        """Retrieves complete patent file wrapper data using common identifiers.

        This utility fetches the `PatentFileWrapper`, which contains comprehensive
        IFW metadata, application details, and more. Provide only one
        identifier if possible. If multiple are given, they are processed in the
        order listed in the arguments, and the first successful match is returned.

        Args:
            application_number (Optional[str], optional): USPTO application number
                (e.g., "16123456"). Checked first (direct lookup).
            patent_number (Optional[str], optional): USPTO patent number
                (e.g., "11000000"). Checked second (uses search).
            publication_number (Optional[str], optional): USPTO pre-grant
                publication number (e.g., "20230123456"). Checked third (uses search).
            PCT_app_number (Optional[str], optional): PCT application number.
                Checked fourth (direct lookup, treated as USPTO app#).
            PCT_pub_number (Optional[str], optional): PCT publication number
                (e.g., "2023012345"). Checked fifth (uses search).

        Returns:
            Optional[PatentFileWrapper]: A `PatentFileWrapper` object with
                comprehensive data if found using one of the identifiers,
                otherwise None.
        """

        if application_number:
            return self.get_application_by_number(application_number=application_number)
        if patent_number:
            pdr = self.search_applications(patent_number_q=patent_number, limit=1)
            if pdr.patent_file_wrapper_data_bag:
                return pdr.patent_file_wrapper_data_bag[0]
        if publication_number:
            pdr = self.search_applications(
                earliestPublicationNumber_q=publication_number, limit=1
            )
            if pdr.patent_file_wrapper_data_bag:
                return pdr.patent_file_wrapper_data_bag[0]
        if PCT_app_number:
            return self.get_application_by_number(application_number=PCT_app_number)
        if PCT_pub_number:
            pdr = self.search_applications(
                pctPublicationNumber_q=PCT_pub_number, limit=1
            )
            if pdr.patent_file_wrapper_data_bag:
                return pdr.patent_file_wrapper_data_bag[0]
        return None

    def download_archive(
        self,
        printed_metadata: PrintedMetaData,
        file_name: Optional[str] = None,
        destination_path: Optional[str] = None,
        overwrite: bool = False,
    ) -> str:
        """Downloads Printed Metadata (XML data). These are XML files of the patent as printed.

        Args:
            printed_metadata: ArchiveMetaData object containing download URL and metadata
            file_name: Optional filename. If not provided, uses zip_file_name from metadata
            destination_path: Optional directory path to save the archive
            overwrite: Whether to overwrite existing files. Default False

        Returns:
            str: Path to the downloaded archive file

        Raises:
            ValueError: If archive_metadata has no download URL
            FileExistsError: If file exists and overwrite=False
        """
        # Validate we have a download URL
        if printed_metadata.file_location_uri is None:
            raise ValueError("ArchiveMetaData must have a file_location_uri")

        # Get filename - either provided or from metadata
        if file_name is None:
            if printed_metadata.xml_file_name:
                file_name = printed_metadata.xml_file_name
            else:
                # Fallback: extract from URL
                url_filename = printed_metadata.file_location_uri.split("/")[-1]
                if "." in url_filename:
                    file_name = url_filename
                else:
                    # Last resort: use product identifier
                    product_id = printed_metadata.product_identifier or "patent_text"
                    file_name = f"{product_id}.xml"

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

        # Download the Printed Metadata
        return self._download_file(
            url=printed_metadata.file_location_uri, file_path=final_file_path.as_posix()
        )
