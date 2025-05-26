"""
utils.http - HTTP utilities for USPTO API clients

This module provides HTTP utilities for USPTO API clients.
"""

from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def create_session(headers: Optional[Dict[str, str]] = None) -> requests.Session:
    """
    Create a requests session with retry configuration.

    Args:
        headers: Optional headers to add to the session

    Returns:
        Configured requests.Session object
    """
    session = requests.Session()

    if headers:
        session.headers.update(headers)

    # Configure retries
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


def parse_response(response: requests.Response) -> Dict[str, Any]:
    """
    Parse a response from the USPTO API.

    Args:
        response: Response from the USPTO API

    Returns:
        Parsed response data
    """
    json_response: Dict[str, Any] = response.json()
    return json_response
