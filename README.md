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
> This method is convenient for quick scripts but not recommended. Consider using environment variables instead.

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

> [!TIP]
> For comprehensive examples with detailed explanations, see the [`examples/`](examples/) directory.

### Patent Data API

```python
from pyUSPTO import PatentDataClient

client = PatentDataClient(api_key="your_api_key_here")

# Search for applications by inventor name
response = client.search_applications(inventor_name_q="Smith", limit=2)
print(f"Found {response.count} applications with 'Smith' as inventor (showing up to 2).")

# Get a specific application
app = client.get_application_by_number("18045436")
if app.application_meta_data:
    print(f"Title: {app.application_meta_data.invention_title}")
```

See [`examples/patent_data_example.py`](examples/patent_data_example.py) for detailed examples including downloading documents and publications.

### Final Petition Decisions API

```python
from pyUSPTO import FinalPetitionDecisionsClient

client = FinalPetitionDecisionsClient(api_key="your_api_key_here")

# Search for petition decisions
response = client.search_decisions(
    decision_date_from_q="2023-01-01", decision_date_to_q="2023-12-31", limit=5
)
print(f"Found {response.count} decisions from 2023.")

# Get a specific decision by ID from search results
response = client.search_decisions(limit=1)
if response.count > 0:
    decision_id = response.petition_decision_data_bag[0].petition_decision_record_identifier
    decision = client.get_decision_by_id(decision_id)
    print(f"Decision Type: {decision.decision_type_code}")
```

See [`examples/petition_decisions_example.py`](examples/petition_decisions_example.py) for detailed examples including downloading decision documents.

### PTAB Trials API

```python
from pyUSPTO import PTABTrialsClient

client = PTABTrialsClient(api_key="your_api_key_here")

# Search for IPR proceedings
response = client.search_proceedings(
    trial_type_code_q="IPR",
    petition_filing_date_from_q="2023-01-01",
    petition_filing_date_to_q="2023-12-31",
    limit=5,
)
print(f"Found {response.count} IPR proceedings filed in 2023")

# Paginate through results
for proceeding in client.paginate_proceedings(
    trial_type_code_q="IPR",
    petition_filing_date_from_q="2024-01-01",
    limit=5,
):
    print(f"{proceeding.trial_number}")
```

See [`examples/ptab_trials_example.py`](examples/ptab_trials_example.py) for detailed examples including searching documents and decisions.

### PTAB Appeals API

```python
from pyUSPTO import PTABAppealsClient

client = PTABAppealsClient(api_key="your_api_key_here")

# Search for appeal decisions
response = client.search_decisions(
    technology_center_number_q="3600",
    decision_date_from_q="2023-01-01",
    decision_date_to_q="2023-12-31",
    limit=5,
)
print(f"Found {response.count} appeal decisions from TC 3600 in 2023")
```

See [`examples/ptab_appeals_example.py`](examples/ptab_appeals_example.py) for detailed examples including searching by decision type and application number.

### PTAB Interferences API

```python
from pyUSPTO import PTABInterferencesClient

client = PTABInterferencesClient(api_key="your_api_key_here")

# Search for interference decisions
response = client.search_decisions(
    decision_date_from_q="2023-01-01",
    limit=5,
)
print(f"Found {response.count} interference decisions since 2023")
```

See [`examples/ptab_interferences_example.py`](examples/ptab_interferences_example.py) for detailed examples including searching by party name and outcome.

## Documentation

Full documentation may be found on [Read the Docs](https://pyuspto.readthedocs.io/).

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

## Advanced Topics

For advanced configuration including HTTP settings, environment variables reference, debugging with raw data preservation, and warning control, see [ADVANCED.md](ADVANCED.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.
