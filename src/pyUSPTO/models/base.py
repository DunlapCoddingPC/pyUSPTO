"""
models.base - Base model classes and protocols for USPTO API models

This module provides base model classes and protocols for USPTO API models.
"""

from typing import Any, Dict, Optional, Protocol, runtime_checkable


@runtime_checkable
class FromDictProtocol(Protocol):
    """Protocol for classes that can be created from a dictionary."""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Any:
        """Create an object from a dictionary."""
        ...


class BaseModel:
    """A base model providing common functionality like raw data storage."""

    raw_data: Optional[Any]

    def __init__(self, raw_data: Optional[Any] = None, **kwargs: Any) -> None:
        # raw_data holds the original API JSON data.
        self.raw_data = raw_data

        # Process additional keywords for further initialization if needed.
        for key, value in kwargs.items():
            setattr(self, key, value)
