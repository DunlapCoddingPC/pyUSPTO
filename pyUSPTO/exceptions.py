"""
exceptions - Exception classes for USPTO API clients

This module provides exception classes for USPTO API clients.
"""

from typing import Optional


class USPTOApiError(Exception):
    """Base exception for USPTO API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        self.status_code = status_code
        super().__init__(message)


class USPTOApiAuthError(USPTOApiError):
    """Authentication error."""

    pass


class USPTOApiRateLimitError(USPTOApiError):
    """Rate limit exceeded."""

    pass


class USPTOApiNotFoundError(USPTOApiError):
    """Resource not found."""

    pass
