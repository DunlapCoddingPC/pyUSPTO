"""http_config - HTTP client configuration for USPTO API requests.

This module provides configuration for HTTP transport-level settings including
timeouts, retries, connection pooling, and custom headers.
"""

import os
from dataclasses import dataclass, field


@dataclass
class HTTPConfig:
    """HTTP client configuration for request handling.

    This class separates transport-level HTTP concerns from API-level
    configuration, allowing fine-grained control over request behavior.

    Attributes:
        timeout: Read timeout in seconds for requests (default: 30.0)
        connect_timeout: Connection establishment timeout in seconds (default: 10.0)
        max_retries: Maximum number of retry attempts (default: 3)
        backoff_factor: Exponential backoff multiplier for retries (default: 1.0)
        retry_status_codes: HTTP status codes that trigger retries
        pool_connections: Number of connection pools to cache (default: 10)
        pool_maxsize: Maximum number of connections per pool (default: 10)
        download_chunk_size: Chunk size in bytes for streaming file downloads (default: 8192)
        custom_headers: Additional headers to include in all requests
    """

    # Timeout configuration
    timeout: float | None = 30.0
    connect_timeout: float | None = 10.0

    # Retry configuration
    max_retries: int = 3
    backoff_factor: float = 1.0
    retry_status_codes: list[int] = field(
        default_factory=lambda: [429, 500, 502, 503, 504]
    )

    # Connection pooling
    pool_connections: int = 10
    pool_maxsize: int = 10

    # Download configuration
    download_chunk_size: int = 8192  # Bytes per chunk when streaming downloads

    # Custom headers (User-Agent, tracking, etc.)
    custom_headers: dict[str, str] | None = None

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if self.download_chunk_size <= 0:
            raise ValueError(
                f"download_chunk_size must be positive, got {self.download_chunk_size}"
            )
        if self.download_chunk_size > 10485760:  # 10 MB
            import warnings

            warnings.warn(
                f"download_chunk_size of {self.download_chunk_size} bytes is very large "
                "and may cause memory issues. Consider using <= 1048576 (1 MB).",
                UserWarning,
            )

    @classmethod
    def from_env(cls) -> "HTTPConfig":
        """Create HTTPConfig from environment variables.

        Environment variables:
            USPTO_REQUEST_TIMEOUT: Request timeout in seconds
            USPTO_CONNECT_TIMEOUT: Connection timeout in seconds
            USPTO_MAX_RETRIES: Maximum retry attempts
            USPTO_BACKOFF_FACTOR: Retry backoff factor
            USPTO_POOL_CONNECTIONS: Connection pool size
            USPTO_POOL_MAXSIZE: Max connections per pool
            USPTO_DOWNLOAD_CHUNK_SIZE: Chunk size for streaming downloads (bytes)

        Returns:
            HTTPConfig instance with values from environment or defaults
        """
        return cls(
            timeout=float(os.environ.get("USPTO_REQUEST_TIMEOUT", "30.0")),
            connect_timeout=float(os.environ.get("USPTO_CONNECT_TIMEOUT", "10.0")),
            max_retries=int(os.environ.get("USPTO_MAX_RETRIES", "3")),
            backoff_factor=float(os.environ.get("USPTO_BACKOFF_FACTOR", "1.0")),
            pool_connections=int(os.environ.get("USPTO_POOL_CONNECTIONS", "10")),
            pool_maxsize=int(os.environ.get("USPTO_POOL_MAXSIZE", "10")),
            download_chunk_size=int(os.environ.get("USPTO_DOWNLOAD_CHUNK_SIZE", "8192")),
        )

    def get_timeout_tuple(self) -> tuple[float | None, float | None]:
        """Get timeout as tuple for requests library.

        Returns:
            Tuple of (connect_timeout, read_timeout) for requests
        """
        return (self.connect_timeout, self.timeout)
