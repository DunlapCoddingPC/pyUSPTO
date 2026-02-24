# Advanced Topics

## Advanced HTTP Configuration

Control timeout behavior, retry logic, and connection pooling using `HTTPConfig`:

```python
from pyUSPTO import PatentDataClient, USPTOConfig, HTTPConfig

# Create HTTP configuration
http_config = HTTPConfig(
    timeout=60.0,              # 60 second read timeout
    connect_timeout=10.0,      # 10 seconds to establish connection
    max_retries=5,             # Retry up to 5 times on failure
    backoff_factor=2.0,        # Exponential backoff: 2, 4, 8, 16, 32 seconds
    retry_status_codes=[429, 500, 502, 503, 504],  # Retry on these status codes
    pool_connections=20,       # Connection pool size
    pool_maxsize=20,          # Max connections per pool
    custom_headers={          # Additional headers for all requests
        "User-Agent": "MyApp/1.0",
        "X-Tracking-ID": "abc123"
    }
)

# Pass HTTPConfig via USPTOConfig
config = USPTOConfig(
    api_key="your_api_key",
    http_config=http_config
)

client = PatentDataClient(config=config)
```

## Session Lifecycle

`USPTOConfig` manages an underlying `requests.Session`. For short-lived scripts this is cleaned up automatically, but for long-running applications or tests you may close it explicitly:

```python
from pyUSPTO import PatentDataClient, USPTOConfig

# Option 1: Context manager
with USPTOConfig(api_key="your_key") as config:
    client = PatentDataClient(config=config)
    response = client.search_applications(limit=1)

# Option 2: Explicit close
config = USPTOConfig(api_key="your_key")
try:
    client = PatentDataClient(config=config)
    response = client.search_applications(limit=1)
finally:
    config.close()
```

## HTTP Configuration via Environment Variables

```bash
export USPTO_REQUEST_TIMEOUT=60.0       # Read timeout
export USPTO_CONNECT_TIMEOUT=10.0       # Connection timeout
export USPTO_MAX_RETRIES=5              # Max retry attempts
export USPTO_BACKOFF_FACTOR=2.0         # Retry backoff multiplier
export USPTO_POOL_CONNECTIONS=20        # Connection pool size
export USPTO_POOL_MAXSIZE=20            # Max connections per pool
```

Then create config from environment:

```python
config = USPTOConfig.from_env()  # Reads both API and HTTP config from env
client = PatentDataClient(config=config)
```

Share HTTP configuration across multiple clients:

```python
# Create once, use multiple times
http_config = HTTPConfig(timeout=60.0, max_retries=5)

patent_config = USPTOConfig(api_key="key1", http_config=http_config)
petition_config = USPTOConfig(api_key="key2", http_config=http_config)

patent_client = PatentDataClient(config=patent_config)
petition_client = FinalPetitionDecisionsClient(config=petition_config)
```

## Environment Variables Reference

All clients support configuration via environment variables. This is the recommended approach.

### API Configuration

| Environment Variable                  | Description                                    | Default                   |
| ------------------------------------- | ---------------------------------------------- | ------------------------- |
| `USPTO_API_KEY`                     | Your USPTO Open Data Portal API key (required) | None                      |
| `USPTO_BULK_DATA_BASE_URL`          | Base URL for Bulk Data API                     | `https://api.uspto.gov` |
| `USPTO_PATENT_DATA_BASE_URL`        | Base URL for Patent Data API                   | `https://api.uspto.gov` |
| `USPTO_PETITION_DECISIONS_BASE_URL` | Base URL for Petition Decisions API            | `https://api.uspto.gov` |
| `USPTO_PTAB_BASE_URL`               | Base URL for PTAB APIs                         | `https://api.uspto.gov` |

> [!NOTE]
> The base URL variables are provided in case the USPTO introduces alternate environments (e.g., a development or testing endpoint) in the future. Currently there are no such endpoints, and these defaults should not be changed.

### HTTP Transport Configuration

| Environment Variable          | Description                                | Default         |
| ----------------------------- | ------------------------------------------ | --------------- |
| `USPTO_REQUEST_TIMEOUT`     | Read timeout in seconds                    | `30.0`        |
| `USPTO_CONNECT_TIMEOUT`     | Connection timeout in seconds              | `10.0`        |
| `USPTO_MAX_RETRIES`         | Maximum number of retry attempts           | `3`           |
| `USPTO_BACKOFF_FACTOR`      | Exponential backoff multiplier for retries | `2.0`         |
| `USPTO_POOL_CONNECTIONS`    | Number of connection pools to cache        | `10`          |
| `USPTO_POOL_MAXSIZE`        | Maximum connections per pool               | `10`          |
| `USPTO_DOWNLOAD_CHUNK_SIZE` | Chunk size in bytes for file downloads     | `8192`        |
| `USPTO_MAX_EXTRACT_SIZE`    | Maximum bytes to extract from archives     | None (no limit) |

### Example: Configuration

```bash
# API Configuration
export USPTO_API_KEY="your_api_key"
export USPTO_BULK_DATA_BASE_URL="https://api.uspto.gov"
export USPTO_PATENT_DATA_BASE_URL="https://api.uspto.gov"
export USPTO_PETITION_DECISIONS_BASE_URL="https://api.uspto.gov"
export USPTO_PTAB_BASE_URL="https://api.uspto.gov"

# Increase timeouts for large downloads
export USPTO_REQUEST_TIMEOUT=120.0
export USPTO_CONNECT_TIMEOUT=20.0

# More aggressive retry policy
export USPTO_MAX_RETRIES=5
export USPTO_BACKOFF_FACTOR=2.0

# Larger connection pool for concurrent requests
export USPTO_POOL_CONNECTIONS=20
export USPTO_POOL_MAXSIZE=20

# Larger chunk size for faster downloads
export USPTO_DOWNLOAD_CHUNK_SIZE=65536

# Limit total bytes extracted from archives
export USPTO_MAX_EXTRACT_SIZE=10737418240
```

## Debugging with Raw Data Preservation

When debugging API response issues or investigating data parsing problems, you can preserve the raw JSON response alongside the parsed data models using the `include_raw_data` flag:

```python
from pyUSPTO import PatentDataClient, USPTOConfig

# Enable raw data preservation
config = USPTOConfig(
    api_key="your_api_key",
    include_raw_data=True  # Preserve original API responses
)

client = PatentDataClient(config=config)

# Make an API call
response = client.search_applications(inventor_name_q="Smith", limit=1)

# Access the parsed data normally
print(f"Found {response.count} applications")

# Access the raw JSON response for debugging
if response.raw_data:
    print("Raw API response:")
    import json
    print(json.dumps(response.raw_data, indent=2))
```

**When to use `include_raw_data`:**

- **Debugging parsing issues**: When data isn't appearing in the parsed models as expected
- **Investigating API changes**: When you need to see exactly what the API returned
- **Reporting bugs**: Include raw responses when filing issue reports
- **Development and testing**: Useful during development to verify API responses

**Important notes:**

- Raw data is stored in the `raw_data` attribute of response objects
- This increases memory usage as both parsed and raw data are kept
- Only enable when needed for debugging - disable for better performance
- Response models support `raw_data` when this flag is enabled (except StatusCodeSearchResponse)

**Example: Debugging a missing field**

```python
config = USPTOConfig(api_key="your_api_key", include_raw_data=True)
client = PatentDataClient(config=config)

response = client.search_applications(limit=1)
if response.patent_file_wrapper_data_bag:
    wrapper = response.patent_file_wrapper_data_bag[0]

    # Check if a field is missing in the parsed model
    if wrapper.application_meta_data is None:
        # Inspect the raw data to see what was actually returned
        print("Raw wrapper data:", wrapper.raw_data)
```

## Warning Control

The library uses Python's standard `warnings` module to report data parsing issues. This allows you to control how warnings are handled based on your needs.

**Warning Categories**

All warnings inherit from `USPTODataWarning`:

- `USPTODateParseWarning`: Date/datetime string parsing failures
- `USPTOBooleanParseWarning`: Y/N boolean string parsing failures
- `USPTOTimezoneWarning`: Timezone-related issues
- `USPTOEnumParseWarning`: Enum value parsing failures
- `USPTODataMismatchWarning`: API returns data with different identifier than requested

**Controlling Warnings**

```python
import warnings
from pyUSPTO.warnings import (
    USPTODataWarning,
    USPTODateParseWarning,
    USPTOBooleanParseWarning,
    USPTOTimezoneWarning,
    USPTOEnumParseWarning,
    USPTODataMismatchWarning
)

# Suppress all pyUSPTO data warnings
warnings.filterwarnings('ignore', category=USPTODataWarning)

# Suppress only date parsing warnings
warnings.filterwarnings('ignore', category=USPTODateParseWarning)

# Turn warnings into errors (strict mode)
warnings.filterwarnings('error', category=USPTODataWarning)

# Show warnings once per location
warnings.filterwarnings('once', category=USPTODataWarning)

# Always show all warnings (default Python behavior)
warnings.filterwarnings('always', category=USPTODataWarning)
```

The library's permissive parsing philosophy returns `None` for fields that cannot be parsed, allowing you to retrieve partial data even when some fields have issues. Warnings inform you when this happens without stopping execution.

## Archive Extraction Safety

Download methods that accept `extract=True` (e.g., `BulkDataClient.download_file`) automatically extract archive files (tar.gz, zip). The extraction includes the following protections:

- **Path traversal protection**: Archive members with paths that resolve outside the extraction directory are rejected.
- **Size limits**: Set `max_extract_size` on `HTTPConfig` to cap the total bytes extracted, protecting against zip bombs or file system size limitations.

```python
from pyUSPTO import USPTOConfig, HTTPConfig, BulkDataClient

http_config = HTTPConfig(
    max_extract_size=10 * 1024 * 1024 * 1024  # 10 GB
)
config = USPTOConfig(api_key="your_key", http_config=http_config)
client = BulkDataClient(config=config)

# Extraction will raise ValueError if total extracted size exceeds 10 GB
client.download_file(product_file, destination="/tmp", extract=True)
```

Or via environment variable:

```bash
export USPTO_MAX_EXTRACT_SIZE=10737418240  # 10 GB
```

By default, `extract` is `False` on `BulkDataClient.download_file` and there is no size limit.
