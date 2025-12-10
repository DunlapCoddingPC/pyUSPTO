# pyUSPTO

[![PyPI version](https://badge.fury.io/py/pyUSPTO.svg)](https://badge.fury.io/py/pyUSPTO)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Read the Docs](https://img.shields.io/readthedocs/pyuspto)](https://pyuspto.readthedocs.io/en/latest/)

A Python client library for interacting with the United Stated Patent and Trademark Office (USPTO) [Open Data Portal](https://data.uspto.gov/home) APIs.

This package provides clients for interacting with the USPTO Bulk Data API, Patent Data API, Final Petition Decisions API, and PTAB (Patent Trial and Appeal Board) APIs.

> [!IMPORTANT]
> The USPTO is in the process of moving their API. This package is only concerned with the new API. The [old API](https://developer.uspto.gov/) will be retired at the end of 2025.

## Quick Start

**Requirements**: Python ≥3.10

```bash
pip install pyUSPTO
```

> [!IMPORTANT]
> You must have an API key for the [USPTO Open Data Portal API](https://data.uspto.gov/myodp/landing).

```python
from pyUSPTO import PatentDataClient

# Initialize with your API key
client = PatentDataClient(api_key="your_api_key_here")

# Search for patent applications
results = client.search_applications(inventor_name_q="Smith", limit=10)
print(f"Found {results.count} applications")
```

## Configuration

All clients can be configured using one of three methods:

### Method 1: Direct API Key Initialization

> [!NOTE]
> This method is convenient for quick scripts but not recommended for production use. Consider using environment variables instead.

```python
from pyUSPTO import (
    BulkDataClient,
    PatentDataClient,
    FinalPetitionDecisionsClient,
    PTABTrialsClient,
    PTABAppealsClient,
    PTABInterferencesClient
)

patent_client = PatentDataClient(api_key="your_api_key_here")
bulk_client = BulkDataClient(api_key="your_api_key_here")
petition_client = FinalPetitionDecisionsClient(api_key="your_api_key_here")
trials_client = PTABTrialsClient(api_key="your_api_key_here")
appeals_client = PTABAppealsClient(api_key="your_api_key_here")
interferences_client = PTABInterferencesClient(api_key="your_api_key_here")
```

### Method 2: Using USPTOConfig

```python
from pyUSPTO import (
    BulkDataClient,
    PatentDataClient,
    FinalPetitionDecisionsClient,
    PTABTrialsClient,
    PTABAppealsClient,
    PTABInterferencesClient
)

from pyUSPTO.config import USPTOConfig

config = USPTOConfig(api_key="your_api_key_here")

patent_client = PatentDataClient(config=config)
bulk_client = BulkDataClient(config=config)
petition_client = FinalPetitionDecisionsClient(config=config)
trials_client = PTABTrialsClient(config=config)
appeals_client = PTABAppealsClient(config=config)
interferences_client = PTABInterferencesClient(config=config)
```

### Method 3: Environment Variables (Recommended)

Set the environment variable in your shell:

```bash
export USPTO_API_KEY="your_api_key_here"
```

Then use it in your Python code:

```python
from pyUSPTO import (
    BulkDataClient,
    PatentDataClient,
    FinalPetitionDecisionsClient,
    PTABTrialsClient,
    PTABAppealsClient,
    PTABInterferencesClient
)
from pyUSPTO.config import USPTOConfig

# Load configuration from environment
config = USPTOConfig.from_env()

patent_client = PatentDataClient(config=config)
bulk_client = BulkDataClient(config=config)
petition_client = FinalPetitionDecisionsClient(config=config)
trials_client = PTABTrialsClient(config=config)
appeals_client = PTABAppealsClient(config=config)
interferences_client = PTABInterferencesClient(config=config)
```

## API Usage Examples

### Patent Data API

```python
# Search for applications by inventor name
inventor_search = patent_client.search_applications(inventor_name_q="Smith")
print(f"Found {inventor_search.count} applications with 'Smith' as inventor")
# > Found 104926 applications with 'Smith' as inventor.
```

### Final Petition Decisions API

```python
# Search for petition decisions by date range
decisions = petition_client.search_decisions(
    decision_date_from_q="2023-01-01",
    limit=10
)
print(f"Found {decisions.count} petition decisions since 2023")

# Get a specific decision by ID
decision = petition_client.get_decision_by_id("decision_id_here")
print(f"Decision Type: {decision.decision_type_code}")
print(f"Application: {decision.application_number_text}")
```

### PTAB (Patent Trial and Appeal Board) APIs

The package provides three clients for accessing PTAB data:

#### PTAB Trials API

```python
from pyUSPTO import PTABTrialsClient

# Initialize client
trials_client = PTABTrialsClient(api_key="your_api_key_here")

# Search for IPR trial proceedings
proceedings = trials_client.search_proceedings(
    trial_type_code_q="IPR",
    trial_status_category_q="Instituted",
    petition_filing_date_from_q="2023-01-01",
    limit=10
)
print(f"Found {proceedings.count} instituted IPR proceedings")

# Search for trial documents with new convenience parameters
documents = trials_client.search_documents(
    trial_number_q="IPR2023-00001",
    petitioner_party_name_q="Acme Corp",
    patent_owner_name_q="XYZ Inc",
    limit=5
)

# Search for trial decisions
decisions = trials_client.search_decisions(
    trial_type_code_q="IPR",
    decision_type_category_q="Final Written Decision",
    patent_number_q="US1234567",
    decision_date_from_q="2023-01-01"
)

# Paginate through proceedings
for proceeding in trials_client.paginate_proceedings(trial_type_code_q="IPR", limit=25):
    print(f"Trial: {proceeding.trial_number}")
```

#### PTAB Appeals API

```python
from pyUSPTO import PTABAppealsClient

# Initialize client
appeals_client = PTABAppealsClient(api_key="your_api_key_here")

# Search for appeal decisions by technology center
decisions = appeals_client.search_decisions(
    technology_center_number_q="3600",
    decision_type_category_q="Affirmed",
    decision_date_from_q="2023-01-01",
    limit=10
)
print(f"Found {decisions.count} affirmed decisions from TC 3600")

# Search by application number
decisions = appeals_client.search_decisions(
    application_number_text_q="15/123456",
    limit=5
)

# Paginate through decisions
for decision in appeals_client.paginate_decisions(
    technology_center_number_q="2100",
    limit=25
):
    print(f"Appeal: {decision.appeal_number}")
```

#### PTAB Interferences API

```python
from pyUSPTO import PTABInterferencesClient

# Initialize client
interferences_client = PTABInterferencesClient(api_key="your_api_key_here")

# Search for interference decisions by outcome
decisions = interferences_client.search_decisions(
    interference_outcome_category_q="Priority to Senior Party",
    decision_date_from_q="2022-01-01",
    limit=10
)
print(f"Found {decisions.count} decisions awarding priority to senior party")

# Search by party name
decisions = interferences_client.search_decisions(
    senior_party_name_q="Example Corp",
    junior_party_name_q="Test Inc",
    limit=5
)

# Paginate through decisions
for decision in interferences_client.paginate_decisions(
    decision_type_category_q="Final Decision",
    limit=25
):
    print(f"Interference: {decision.interference_number}")
```

## Documentation

Full documentation may be found on [Read the Docs](https://pyuspto.readthedocs.io/).

## Advanced Topics

### Advanced HTTP Configuration

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

Configure HTTP settings via environment variables:

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

### Warning Control

The library uses Python's standard `warnings` module to report data parsing issues. This allows you to control how warnings are handled based on your needs.

**Warning Categories**

All warnings inherit from `USPTODataWarning`:

- `USPTODateParseWarning`: Date/datetime string parsing failures
- `USPTOBooleanParseWarning`: Y/N boolean string parsing failures
- `USPTOTimezoneWarning`: Timezone-related issues
- `USPTOEnumParseWarning`: Enum value parsing failures

**Controlling Warnings**

```python
import warnings
from pyUSPTO.warnings import (
    USPTODataWarning,
    USPTODateParseWarning,
    USPTOBooleanParseWarning,
    USPTOTimezoneWarning,
    USPTOEnumParseWarning
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

## Data Models

The library uses Python dataclasses to represent API responses. All data models include type annotations for attributes and methods, making them fully compatible with static type checkers.

#### Bulk Data API

- `BulkDataResponse`: Top-level response from the API
- `BulkDataProduct`: Information about a specific product
- `ProductFileBag`: Container for file data elements
- `FileData`: Information about an individual file

#### Patent Data API

- `PatentDataResponse`: Top-level response from the API
- `PatentFileWrapper`: Information about a patent application
- `ApplicationMetaData`: Metadata about a patent application
- `Address`: Represents an address in the patent data
- `Person`, `Applicant`, `Inventor`, `Attorney`: Person-related data classes
- `Assignment`, `Assignor`, `Assignee`: Assignment-related data classes
- `Continuity`, `ParentContinuity`, `ChildContinuity`: Continuity-related data classes
- `PatentTermAdjustmentData`: Patent term adjustment information
- And many more specialized classes for different aspects of patent data

#### Final Petition Decisions API

- `PetitionDecisionResponse`: Top-level response from the API
- `PetitionDecision`: Complete information about a petition decision
- `PetitionDecisionDocument`: Document associated with a petition decision
- `DocumentDownloadOption`: Download options for petition documents
- `DecisionTypeCode`: Enum for petition decision types
- `DocumentDirectionCategory`: Enum for document direction categories

#### PTAB Trials API

- `PTABTrialProceedingResponse`: Top-level response from the API
- `PTABTrialProceeding`: Information about a PTAB trial proceeding (IPR, PGR, CBM, DER)
- `PTABTrialDocument`: Document associated with a trial proceeding
- `PTABTrialDecision`: Decision information for a trial proceeding
- `RegularPetitionerData`, `RespondentData`, `DerivationPetitionerData`: Party data for different trial types
- `PTABTrialMetaData`: Trial metadata and status information

#### PTAB Appeals API

- `PTABAppealResponse`: Top-level response from the API
- `PTABAppealDecision`: Ex parte appeal decision information
- `AppellantData`: Appellant information and application details
- `PTABAppealMetaData`: Appeal metadata and filing information
- `PTABAppealDocumentData`: Document and decision details

#### PTAB Interferences API

- `PTABInterferenceResponse`: Top-level response from the API
- `PTABInterferenceDecision`: Interference proceeding decision information
- `SeniorPartyData`, `JuniorPartyData`, `AdditionalPartyData`: Party data classes
- `PTABInterferenceMetaData`: Interference metadata and status information
- `PTABInterferenceDocumentData`: Document and outcome details

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.
