"""models.base - Base model classes and protocols for USPTO API models.

This module provides base model classes and protocols for USPTO API models.
"""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class FromDictProtocol(Protocol):
    """Protocol for classes that can be created from a dictionary."""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Any:
        """Create an object from a dictionary."""
        ...


class BaseModel:
    """A base model providing common functionality like raw data storage."""

    raw_data: Any | None

    def __init__(self, raw_data: Any | None = None, **kwargs: Any) -> None:
        """Initialize the BaseModel.

        Args:
            raw_data: The original API JSON data to store for reference.
            **kwargs: Additional keyword arguments to set as attributes on the instance.
        """
        # raw_data holds the original API JSON data.
        self.raw_data = raw_data

        # Process additional keywords for further initialization if needed.
        for key, value in kwargs.items():
            setattr(self, key, value)
