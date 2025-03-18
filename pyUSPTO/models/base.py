"""
models.base - Base model classes and protocols for USPTO API models

This module provides base model classes and protocols for USPTO API models.
"""

from typing import Dict, Any, Protocol, runtime_checkable


@runtime_checkable
class FromDictProtocol(Protocol):
    """Protocol for classes that can be created from a dictionary."""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Any:
        """Create an object from a dictionary."""
        ...
