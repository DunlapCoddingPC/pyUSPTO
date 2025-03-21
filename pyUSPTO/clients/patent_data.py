"""
clients.patent_data - Client for USPTO patent data API

This module provides a client for interacting with the USPTO Patent Data API.
It allows you to search for and retrieve patent application data.
"""

import os
import re
from typing import Any, Dict, Iterator, Optional
from urllib.parse import urlparse

from pyUSPTO.base import BaseUSPTOClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.patent_data import PatentDataResponse, PatentFileWrapper


class PatentDataClient(BaseUSPTOClient[PatentDataResponse]):
    """Client for interacting with the USPTO Patent Data API."""

    # Centralized endpoint configuration
    ENDPOINTS = {
        # Application endpoints
        "applications_search": "applications/search",
        "applications_search_download": "applications/search/download",
        "application_by_number": "applications/{application_number}",
        "application_metadata": "applications/{application_number}/meta-data",
        "application_adjustment": "applications/{application_number}/adjustment",
        "application_assignment": "applications/{application_number}/assignment",
        "application_attorney": "applications/{application_number}/attorney",
        "application_continuity": "applications/{application_number}/continuity",
        "application_foreign_priority": "applications/{application_number}/foreign-priority",
        "application_transactions": "applications/{application_number}/transactions",
        "application_documents": "applications/{application_number}/documents",
        "application_associated_documents": "applications/{application_number}/associated-documents",
        # Document download endpoint (different base URL)
        "download_document": "download/applications/{application_number}/{document_id}.pdf",
        # Status code endpoints
        "status_codes": "status-codes",
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        config: Optional[USPTOConfig] = None,
    ):
        """
        Initialize the PatentDataClient.

        Args:
            api_key: Optional API key for authentication
            base_url: The base URL of the API, defaults to config.patent_data_base_url or "https://api.uspto.gov/api/v1/patent"
            config: Optional USPTOConfig instance
        """
        # Use config if provided, otherwise create default config
        self.config = config or USPTOConfig(api_key=api_key)

        # Use provided API key or get from config
        api_key = api_key or self.config.api_key

        # Use provided base_url or get from config
        base_url = base_url or self.config.patent_data_base_url

        super().__init__(api_key=api_key, base_url=base_url)

    def get_patent_applications(
        self, params: Optional[Dict[str, Any]] = None
    ) -> PatentDataResponse:
        """
        Get a list of patent applications using the search endpoint.

        Args:
            params: Optional query parameters including:
                - q: Search query string
                - sort: Field to sort by followed by sort order
                - offset: Position in dataset to start from
                - limit: Number of results to return
                - facets: List of fields to facet upon
                - fields: Fields to include in response
                - filters: Field filters
                - rangeFilters: Range filters

        Returns:
            PatentDataResponse object containing the API response
        """
        result = self._make_request(
            method="GET",
            endpoint=self.ENDPOINTS["applications_search"],
            params=params,
            response_class=PatentDataResponse,
        )
        # Since we specified response_class=BulkDataResponse, the result should be a BulkDataResponse
        assert isinstance(result, PatentDataResponse)
        return result

    def search_patent_applications_post(
        self, search_request: Dict[str, Any]
    ) -> PatentDataResponse:
        """
        Search patent applications using POST method with JSON payload.

        Args:
            search_request: JSON payload with search parameters including:
                - q: Search query string
                - filters: Array of filter objects
                - rangeFilters: Array of range filter objects
                - sort: Array of sort objects
                - fields: Array of field names to include
                - pagination: Pagination object
                - facets: Array of facet field names

        Returns:
            PatentDataResponse object containing the API response
        """
        result = self._make_request(
            method="POST",
            endpoint=self.ENDPOINTS["applications_search"],
            json_data=search_request,
            response_class=PatentDataResponse,
        )
        # Since we specified response_class=BulkDataResponse, the result should be a BulkDataResponse
        assert isinstance(result, PatentDataResponse)
        return result

    def download_patent_applications(
        self, params: Optional[Dict[str, Any]] = None, format: str = "json"
    ) -> PatentDataResponse:
        """
        Download patent data with specified format.

        Args:
            params: Optional query parameters
            format: Download format (json or csv)

        Returns:
            PatentDataResponse object containing the API response
        """
        # Add format parameter if not already in params
        if params is None:
            params = {}
        if "format" not in params:
            params["format"] = format

        result = self._make_request(
            method="GET",
            endpoint=self.ENDPOINTS["applications_search_download"],
            params=params,
            response_class=PatentDataResponse,
        )
        # Since we specified response_class=BulkDataResponse, the result should be a BulkDataResponse
        assert isinstance(result, PatentDataResponse)
        return result

    def download_patent_applications_post(
        self, download_request: Dict[str, Any]
    ) -> PatentDataResponse:
        """
        Download patent data using POST method with JSON payload.

        Args:
            download_request: JSON payload with download parameters including format

        Returns:
            PatentDataResponse object containing the API response
        """
        result = self._make_request(
            method="POST",
            endpoint=self.ENDPOINTS["applications_search_download"],
            json_data=download_request,
            response_class=PatentDataResponse,
        )
        # Since we specified response_class=BulkDataResponse, the result should be a BulkDataResponse
        assert isinstance(result, PatentDataResponse)
        return result

    def get_patent_by_application_number(
        self, application_number: str
    ) -> PatentFileWrapper:
        """
        Get a specific patent by application number.

        Args:
            application_number: The application number

        Returns:
            PatentFileWrapper object containing the patent data
        """
        endpoint = self.ENDPOINTS["application_by_number"].format(
            application_number=application_number
        )
        data = self._make_request(method="GET", endpoint=endpoint)

        # Handling different response formats
        if isinstance(data, dict):
            if "patentFileWrapperDataBag" in data:
                for wrapper in data["patentFileWrapperDataBag"]:
                    if wrapper.get("applicationNumberText") == application_number:
                        return PatentFileWrapper.from_dict(wrapper)
                raise ValueError(
                    f"Patent with application number {application_number} not found in response"
                )
            else:
                # If response doesn't contain patentFileWrapperDataBag, assume it's a direct PatentFileWrapper
                return PatentFileWrapper.from_dict(data)
        elif isinstance(data, PatentFileWrapper):
            return data
        else:
            raise TypeError(f"Unexpected response type: {type(data)}")

    def get_application_metadata(self, application_number: str) -> PatentDataResponse:
        """
        Get metadata for a specific patent application.

        Args:
            application_number: The application number

        Returns:
            PatentDataResponse object containing the application metadata
        """
        endpoint = self.ENDPOINTS["application_metadata"].format(
            application_number=application_number
        )
        result = self._make_request(
            method="GET",
            endpoint=endpoint,
            response_class=PatentDataResponse,
        )
        # Since we specified response_class=BulkDataResponse, the result should be a BulkDataResponse
        assert isinstance(result, PatentDataResponse)
        return result

    def get_application_adjustment(self, application_number: str) -> PatentDataResponse:
        """
        Get patent term adjustment data for an application.

        Args:
            application_number: The application number

        Returns:
            PatentDataResponse object containing the adjustment data
        """
        endpoint = self.ENDPOINTS["application_adjustment"].format(
            application_number=application_number
        )
        result = self._make_request(
            method="GET",
            endpoint=endpoint,
            response_class=PatentDataResponse,
        )
        # Since we specified response_class=BulkDataResponse, the result should be a BulkDataResponse
        assert isinstance(result, PatentDataResponse)
        return result

    def get_application_assignment(self, application_number: str) -> PatentDataResponse:
        """
        Get assignment data for an application.

        Args:
            application_number: The application number

        Returns:
            PatentDataResponse object containing the assignment data
        """
        endpoint = self.ENDPOINTS["application_assignment"].format(
            application_number=application_number
        )
        result = self._make_request(
            method="GET",
            endpoint=endpoint,
            response_class=PatentDataResponse,
        )
        # Since we specified response_class=BulkDataResponse, the result should be a BulkDataResponse
        assert isinstance(result, PatentDataResponse)
        return result

    def get_application_attorney(self, application_number: str) -> PatentDataResponse:
        """
        Get attorney/agent data for an application.

        Args:
            application_number: The application number

        Returns:
            PatentDataResponse object containing the attorney data
        """
        endpoint = self.ENDPOINTS["application_attorney"].format(
            application_number=application_number
        )
        result = self._make_request(
            method="GET",
            endpoint=endpoint,
            response_class=PatentDataResponse,
        )
        # Since we specified response_class=BulkDataResponse, the result should be a BulkDataResponse
        assert isinstance(result, PatentDataResponse)
        return result

    def get_application_continuity(self, application_number: str) -> PatentDataResponse:
        """
        Get continuity data for an application.

        Args:
            application_number: The application number

        Returns:
            PatentDataResponse object containing the continuity data
        """
        endpoint = self.ENDPOINTS["application_continuity"].format(
            application_number=application_number
        )
        result = self._make_request(
            method="GET",
            endpoint=endpoint,
            response_class=PatentDataResponse,
        )
        # Since we specified response_class=BulkDataResponse, the result should be a BulkDataResponse
        assert isinstance(result, PatentDataResponse)
        return result

    def get_application_foreign_priority(
        self, application_number: str
    ) -> PatentDataResponse:
        """
        Get foreign priority data for an application.

        Args:
            application_number: The application number

        Returns:
            PatentDataResponse object containing the foreign priority data
        """
        endpoint = self.ENDPOINTS["application_foreign_priority"].format(
            application_number=application_number
        )
        result = self._make_request(
            method="GET",
            endpoint=endpoint,
            response_class=PatentDataResponse,
        )
        # Since we specified response_class=BulkDataResponse, the result should be a BulkDataResponse
        assert isinstance(result, PatentDataResponse)
        return result

    def get_application_transactions(
        self, application_number: str
    ) -> PatentDataResponse:
        """
        Get transaction data for an application.

        Args:
            application_number: The application number

        Returns:
            PatentDataResponse object containing the transaction data
        """
        endpoint = self.ENDPOINTS["application_transactions"].format(
            application_number=application_number
        )
        result = self._make_request(
            method="GET",
            endpoint=endpoint,
            response_class=PatentDataResponse,
        )
        # Since we specified response_class=BulkDataResponse, the result should be a BulkDataResponse
        assert isinstance(result, PatentDataResponse)
        return result

    def get_application_documents(self, application_number: str) -> Dict[str, Any]:
        """
        Get document details for an application.

        Args:
            application_number: The application number

        Returns:
            Dictionary containing document details with a 'documentBag' key
        """
        endpoint = self.ENDPOINTS["application_documents"].format(
            application_number=application_number
        )
        result = self._make_request(
            method="GET",
            endpoint=endpoint,
        )
        # The USPTO API returns a dictionary with a 'documentBag' key for this endpoint
        assert isinstance(result, dict)
        return result

    def get_application_associated_documents(
        self, application_number: str
    ) -> PatentDataResponse:
        """
        Get associated documents metadata for an application.

        Args:
            application_number: The application number

        Returns:
            PatentDataResponse object containing the associated documents metadata
        """
        endpoint = self.ENDPOINTS["application_associated_documents"].format(
            application_number=application_number
        )
        result = self._make_request(
            method="GET",
            endpoint=endpoint,
            response_class=PatentDataResponse,
        )
        # Since we specified response_class=BulkDataResponse, the result should be a BulkDataResponse
        assert isinstance(result, PatentDataResponse)
        return result

    def download_application_document(
        self, application_number: str, document_id: str, destination: str
    ) -> str:
        """
        Download a document for a patent application.

        Args:
            application_number: The application number
            document_id: The document identifier
            destination: Directory where the file should be saved

        Returns:
            Path to the downloaded file
        """
        # This endpoint is at a different base URL level
        base_url_parts = self.base_url.split("/patent")
        base_url_root = base_url_parts[0]
        endpoint = self.ENDPOINTS["download_document"].format(
            application_number=application_number, document_id=document_id
        )
        # Get the response with streaming enabled
        response = self._make_request(
            method="GET", endpoint=endpoint, stream=True, custom_base_url=base_url_root
        )

        # Ensure we have a Response object with iter_content
        import requests

        if not isinstance(response, requests.Response):
            raise TypeError("Expected a Response object for streaming download")

        if not os.path.exists(destination):
            os.makedirs(destination)

        # Get filename from Content-Disposition header if available
        content_disposition = response.headers.get("Content-Disposition")
        if content_disposition and "filename=" in content_disposition:
            filename_match = re.search(r'filename="(.+?)"', content_disposition)
            if filename_match:
                filename = filename_match.group(1)
        else:
            filename = document_id

        file_path = os.path.join(destination, filename)

        with open(file=file_path, mode="wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return file_path

    def paginate_patents(self, **kwargs: Any) -> Iterator[PatentFileWrapper]:
        """
        Paginate through all patents matching the search criteria.

        Args:
            **kwargs: Keyword arguments to pass to search_patents

        Yields:
            PatentFileWrapper objects
        """
        return self.paginate_results(
            method_name="get_patent_applications",
            response_container_attr="patent_file_wrapper_data_bag",
            **kwargs,
        )

    def get_patent_status_codes(
        self, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get patent application status codes and descriptions.

        Args:
            params: Optional query parameters including:
                - q: Search query string
                - offset: Position in dataset to start from
                - limit: Number of results to return

        Returns:
            Dictionary containing status codes and descriptions
        """
        result = self._make_request(
            method="GET", endpoint=self.ENDPOINTS["status_codes"], params=params
        )
        assert isinstance(result, dict)
        return result

    def search_patent_status_codes_post(
        self, search_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Search patent status codes using POST method with JSON payload.

        Args:
            search_request: JSON payload with search parameters

        Returns:
            Dictionary containing status codes and descriptions
        """
        result = self._make_request(
            method="POST",
            endpoint=self.ENDPOINTS["status_codes"],
            json_data=search_request,
        )
        assert isinstance(result, dict)
        return result

    def search_patents(
        self,
        query: Optional[str] = None,
        application_number: Optional[str] = None,
        patent_number: Optional[str] = None,
        inventor_name: Optional[str] = None,
        applicant_name: Optional[str] = None,
        assignee_name: Optional[str] = None,
        filing_date_from: Optional[str] = None,
        filing_date_to: Optional[str] = None,
        grant_date_from: Optional[str] = None,
        grant_date_to: Optional[str] = None,
        classification: Optional[str] = None,
        limit: Optional[int] = 25,
        offset: Optional[int] = 0,
    ) -> PatentDataResponse:
        """
        Search for patents with various filters.

        Args:
            query: Search text in all fields
            application_number: Filter by application number
            patent_number: Filter by patent number
            inventor_name: Filter by inventor name
            applicant_name: Filter by applicant name
            assignee_name: Filter by assignee name
            filing_date_from: Filter by filing date from (YYYY-MM-DD)
            filing_date_to: Filter by filing date to (YYYY-MM-DD)
            grant_date_from: Filter by grant date from (YYYY-MM-DD)
            grant_date_to: Filter by grant date to (YYYY-MM-DD)
            classification: Filter by CPC classification
            limit: Number of results to return (default 25)
            offset: Position in dataset to start from (default 0)

        Returns:
            PatentDataResponse object containing matching patents
        """
        # Build the query string
        q_parts = []

        if application_number:
            q_parts.append(f"applicationNumberText:{application_number}")

        if patent_number:
            q_parts.append(f"applicationMetaData.patentNumber:{patent_number}")

        if inventor_name:
            q_parts.append(
                f"applicationMetaData.inventorBag.inventorNameText:{inventor_name}"
            )

        if applicant_name:
            q_parts.append(f"applicationMetaData.firstApplicantName:{applicant_name}")

        if assignee_name:
            q_parts.append(
                f"assignmentBag.assigneeBag.assigneeNameText:{assignee_name}"
            )

        if classification:
            q_parts.append(f"applicationMetaData.cpcClassificationBag:{classification}")

        # Add date range filters
        range_filters = []

        if filing_date_from and filing_date_to:
            range_filters.append(
                f"applicationMetaData.filingDate:[{filing_date_from} TO {filing_date_to}]"
            )
        elif filing_date_from:
            range_filters.append(f"applicationMetaData.filingDate:>={filing_date_from}")
        elif filing_date_to:
            range_filters.append(f"applicationMetaData.filingDate:<={filing_date_to}")

        if grant_date_from and grant_date_to:
            range_filters.append(
                f"applicationMetaData.grantDate:[{grant_date_from} TO {grant_date_to}]"
            )
        elif grant_date_from:
            range_filters.append(f"applicationMetaData.grantDate:>={grant_date_from}")
        elif grant_date_to:
            range_filters.append(f"applicationMetaData.grantDate:<={grant_date_to}")

        # Combine all query parts
        if query:
            q_parts.append(query)

        q_parts.extend(range_filters)

        # Build the final query string
        q = " AND ".join(q_parts) if q_parts else None

        # Set up parameters
        params = {}

        if offset is not None:
            params["offset"] = str(offset)

        if limit is not None:
            params["limit"] = str(limit)

        if q:
            params["q"] = q

        # Use the applications_search endpoint from ENDPOINTS
        result = self._make_request(
            method="GET",
            endpoint=self.ENDPOINTS["applications_search"],
            params=params,
            response_class=PatentDataResponse,
        )
        # Since we specified response_class=BulkDataResponse, the result should be a BulkDataResponse
        assert isinstance(result, PatentDataResponse)
        return result
