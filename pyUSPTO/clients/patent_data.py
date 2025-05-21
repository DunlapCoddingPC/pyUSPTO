"""
clients.patent_data - Client for USPTO patent data API

This module provides a client for interacting with the USPTO Patent Data API.
It allows you to search for and retrieve patent application data.
"""

import os
import re
from typing import Any, Dict, Iterator, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

# Assuming these are from your project structure
from pyUSPTO.base import BaseUSPTOClient
from pyUSPTO.config import USPTOConfig

# Updated model imports
from pyUSPTO.models.patent_data import (
    ApplicationContinuityData,
    ApplicationMetaData,
    Assignment,
    AssociatedDocumentsData,
    ChildContinuity,
    DocumentBag,
    DocumentDownloadFormat,
    DocumentMetaData,
    EventData,
    ForeignPriority,
    ParentContinuity,
    PatentDataResponse,
    PatentFileWrapper,
    PatentTermAdjustmentData,
    RecordAttorney,
    StatusCodeCollection,
    StatusCodeSearchResponse,
)


class PatentDataClient(BaseUSPTOClient[PatentDataResponse]):
    """Client for interacting with the USPTO Patent Data API."""

    ENDPOINTS = {
        "applications_search": "api/v1/patent/applications/search",
        "applications_search_download": "api/v1/patent/applications/search/download",
        "application_by_number": "api/v1/patent/applications/{application_number}",
        "application_metadata": "api/v1/patent/applications/{application_number}/meta-data",
        "application_adjustment": "api/v1/patent/applications/{application_number}/adjustment",
        "application_assignment": "api/v1/patent/applications/{application_number}/assignment",
        "application_attorney": "api/v1/patent/applications/{application_number}/attorney",
        "application_continuity": "api/v1/patent/applications/{application_number}/continuity",
        "application_foreign_priority": "api/v1/patent/applications/{application_number}/foreign-priority",
        "application_transactions": "api/v1/patent/applications/{application_number}/transactions",
        "application_documents": "api/v1/patent/applications/{application_number}/documents",
        "application_associated_documents": "api/v1/patent/applications/{application_number}/associated-documents",
        "download_document": "api/v1/download/applications/{application_number}/{document_id}",
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

    def _get_wrapper_from_response(
        self,
        response_data: PatentDataResponse,
        application_number_for_validation: Optional[str] = None,
    ) -> Optional[PatentFileWrapper]:
        """Helper to extract a single PatentFileWrapper, optionally validating the app number."""
        if not response_data or not response_data.patent_file_wrapper_data_bag:
            return None

        wrapper = response_data.patent_file_wrapper_data_bag[0]
        if not isinstance(wrapper, PatentFileWrapper):
            # This case should ideally not happen if response_class parsing works
            print(
                f"Warning: Expected PatentFileWrapper, got {type(wrapper)}. Attempting manual parse."
            )
            if isinstance(wrapper, dict):  # type: ignore
                wrapper = PatentFileWrapper.from_dict(wrapper)  # type: ignore
            else:
                return None

        if (
            application_number_for_validation
            and wrapper.application_number_text != application_number_for_validation
        ):
            print(
                f"Warning: Fetched wrapper application number '{wrapper.application_number_text}' "
                f"does not match requested '{application_number_for_validation}'."
            )
            # Depending on strictness, could return None here or still return the wrapper.
            # For now, returning it, as the API should have filtered.
        return wrapper

    def get_patent_applications(
        self, params: Optional[Dict[str, Any]] = None
    ) -> PatentDataResponse:
        result = self._make_request(
            method="GET",
            endpoint=self.ENDPOINTS["applications_search"],
            params=params,
            response_class=PatentDataResponse,
        )
        assert isinstance(result, PatentDataResponse)
        return result

    def search_patent_applications_post(
        self, search_request: Dict[str, Any]
    ) -> PatentDataResponse:
        result = self._make_request(
            method="POST",
            endpoint=self.ENDPOINTS["applications_search"],
            json_data=search_request,
            response_class=PatentDataResponse,
        )
        assert isinstance(result, PatentDataResponse)
        return result

    def download_patent_applications_get(
        self, params: Optional[Dict[str, Any]] = None, format_type: str = "json"
    ) -> PatentDataResponse:
        if params is None:
            params = {}
        if "format" not in params:
            params["format"] = format_type
        result = self._make_request(
            method="GET",
            endpoint=self.ENDPOINTS["applications_search_download"],
            params=params,
            response_class=PatentDataResponse,
        )
        assert isinstance(result, PatentDataResponse)
        return result

    def download_patent_applications_post(
        self, download_request: Dict[str, Any]
    ) -> PatentDataResponse:
        result = self._make_request(
            method="POST",
            endpoint=self.ENDPOINTS["applications_search_download"],
            json_data=download_request,
            response_class=PatentDataResponse,
        )
        assert isinstance(result, PatentDataResponse)
        return result

    def get_patent_application_details(
        self, application_number: str
    ) -> Optional[PatentFileWrapper]:
        endpoint = self.ENDPOINTS["application_by_number"].format(
            application_number=application_number
        )
        response_data = self._make_request(
            method="GET", endpoint=endpoint, response_class=PatentDataResponse
        )
        assert isinstance(response_data, PatentDataResponse)
        return self._get_wrapper_from_response(response_data, application_number)

    def get_application_metadata(
        self, application_number: str
    ) -> Optional[ApplicationMetaData]:  # Changed return type
        endpoint = self.ENDPOINTS["application_metadata"].format(
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
    ) -> Optional[PatentTermAdjustmentData]:  # Changed return type
        endpoint = self.ENDPOINTS["application_adjustment"].format(
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
    ) -> Optional[List[Assignment]]:  # Changed return type
        endpoint = self.ENDPOINTS["application_assignment"].format(
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
    ) -> Optional[RecordAttorney]:  # Changed return type
        endpoint = self.ENDPOINTS["application_attorney"].format(
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
    ) -> Optional[ApplicationContinuityData]:  # Changed return type
        endpoint = self.ENDPOINTS["application_continuity"].format(
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
    ) -> Optional[List[ForeignPriority]]:  # Changed return type
        endpoint = self.ENDPOINTS["application_foreign_priority"].format(
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
    ) -> Optional[List[EventData]]:  # Changed return type
        endpoint = self.ENDPOINTS["application_transactions"].format(
            application_number=application_number
        )
        response_data = self._make_request(
            method="GET", endpoint=endpoint, response_class=PatentDataResponse
        )
        assert isinstance(response_data, PatentDataResponse)
        wrapper = self._get_wrapper_from_response(response_data, application_number)
        return wrapper.event_data_bag if wrapper else None

    def get_application_documents(self, application_number: str) -> DocumentBag:
        endpoint = self.ENDPOINTS["application_documents"].format(
            application_number=application_number
        )
        result_dict = self._make_request(method="GET", endpoint=endpoint)
        assert isinstance(result_dict, dict)
        return DocumentBag.from_dict(result_dict)

    def get_application_associated_documents(
        self, application_number: str
    ) -> Optional[AssociatedDocumentsData]:  # Changed return type
        endpoint = self.ENDPOINTS["application_associated_documents"].format(
            application_number=application_number
        )
        response_data = self._make_request(
            method="GET", endpoint=endpoint, response_class=PatentDataResponse
        )
        assert isinstance(response_data, PatentDataResponse)
        wrapper = self._get_wrapper_from_response(response_data, application_number)
        return AssociatedDocumentsData.from_wrapper(wrapper) if wrapper else None

    def download_document_file(
        self,
        application_number: str,
        document_id: str,
        destination_dir: str,
    ) -> str:
        endpoint = self.ENDPOINTS["download_document"].format(
            application_number=application_number, document_id=document_id
        )
        response = self._make_request(method="GET", endpoint=endpoint, stream=True)
        import requests

        if not isinstance(response, requests.Response):
            raise TypeError(
                f"Expected a requests.Response object for streaming download, got {type(response)}"
            )
        os.makedirs(destination_dir, exist_ok=True)
        content_disposition = response.headers.get("Content-Disposition")
        filename = document_id
        if content_disposition and "filename=" in content_disposition:
            filename_match = re.search(r'filename="?(.+?)"?$', content_disposition)
            if filename_match:
                filename = filename_match.group(1)
        file_path = os.path.join(destination_dir, filename)
        with open(file=file_path, mode="wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Document downloaded to: {file_path}")
        return file_path

    def paginate_patents(self, **kwargs: Any) -> Iterator[PatentFileWrapper]:
        return self.paginate_results(
            method_name="get_patent_applications",
            response_container_attr="patent_file_wrapper_data_bag",
            **kwargs,
        )

    def get_patent_status_codes(
        self, params: Optional[Dict[str, Any]] = None
    ) -> StatusCodeSearchResponse:
        result_dict = self._make_request(
            method="GET", endpoint=self.ENDPOINTS["status_codes"], params=params
        )
        assert isinstance(result_dict, dict)
        return StatusCodeSearchResponse.from_dict(result_dict)

    def search_patent_status_codes_post(
        self, search_request: Dict[str, Any]
    ) -> StatusCodeSearchResponse:
        result_dict = self._make_request(
            method="POST",
            endpoint=self.ENDPOINTS["status_codes"],
            json_data=search_request,
        )
        assert isinstance(result_dict, dict)
        return StatusCodeSearchResponse.from_dict(result_dict)

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
        q_parts = []
        if application_number:
            q_parts.append(f"applicationNumberText:{application_number}")
        if patent_number:
            q_parts.append(f"applicationMetaData.patentNumber:{patent_number}")
        # ... (rest of query building logic remains the same)
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
        if filing_date_from and filing_date_to:
            q_parts.append(
                f"applicationMetaData.filingDate:[{filing_date_from} TO {filing_date_to}]"
            )
        elif filing_date_from:
            q_parts.append(f"applicationMetaData.filingDate:>={filing_date_from}")
        elif filing_date_to:
            q_parts.append(f"applicationMetaData.filingDate:<={filing_date_to}")
        if grant_date_from and grant_date_to:
            q_parts.append(
                f"applicationMetaData.grantDate:[{grant_date_from} TO {grant_date_to}]"
            )
        elif grant_date_from:
            q_parts.append(f"applicationMetaData.grantDate:>={grant_date_from}")
        elif grant_date_to:
            q_parts.append(f"applicationMetaData.grantDate:<={grant_date_to}")
        if query:
            q_parts.append(query)
        final_q = " AND ".join(q_parts) if q_parts else None
        params: Dict[str, Any] = {}
        if offset is not None:
            params["offset"] = offset
        if limit is not None:
            params["limit"] = limit
        if final_q:
            params["q"] = final_q
        # Changed from self.search_patent_applications_get to self.get_patent_applications
        return self.get_patent_applications(params=params)
