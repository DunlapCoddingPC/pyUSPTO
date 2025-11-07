# pyUSPTO
[![PyPI version](https://badge.fury.io/py/pyUSPTO.svg)](https://badge.fury.io/py/pyUSPTO)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Read the Docs](https://img.shields.io/readthedocs/pyuspto)](https://pyuspto.readthedocs.io/en/latest/)

A Python client library for interacting with the United Stated Patent and Trademark Office (USPTO) [Open Data Portal](https://data.uspto.gov/home) APIs.

This package provides clients for interacting with the USPTO Bulk Data API, the USPTO Patent Data API, and the USPTO Final Petition Decisions API. 

> [!IMPORTANT]
> The USPTO is in the process of moving their API. This package is only concerned with the new API. The [old API](https://developer.uspto.gov/) will be retired at the end of 2025.

## Quick Start

### Installation

**Requirements**: Python ≥3.10

```bash
pip install pyUSPTO
```

Or install from source:

```bash
git clone https://github.com/DunlapCoddingPC/pyUSPTO.git
cd pyUSPTO
pip install -e .
```


### Configuration Options

> [!IMPORTANT]
> You must have an API key for the [USPTO Open Data Portal API](https://data.uspto.gov/myodp/landing).

There are multiple ways to configure the USPTO API clients:


```python
from pyUSPTO import PatentDataClient, FinalPetitionDecisionsClient

# Method 1: Direct API key initialization
patent_client = PatentDataClient(api_key="your_api_key_here")
petition_client = FinalPetitionDecisionsClient(api_key="your_api_key_here")

# Method 2: Using USPTOConfig with explicit parameters
from pyUSPTO.config import USPTOConfig
config = USPTOConfig(
    api_key="your_api_key_here",
    bulk_data_base_url="https://api.uspto.gov",
    patent_data_base_url="https://api.uspto.gov",
    petition_decisions_base_url="https://api.uspto.gov"
)
patent_client = PatentDataClient(config=config)
petition_client = FinalPetitionDecisionsClient(config=config)

# Method 3: Using environment variables (recommended for production)
import os
os.environ["USPTO_API_KEY"] = "your_api_key_here"
config_from_env = USPTOConfig.from_env()
patent_client = PatentDataClient(config=config_from_env)
petition_client = FinalPetitionDecisionsClient(config=config_from_env)
```

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

## Features

- Access to USPTO Bulk Data API, Patent Data API, and Final Petition Decisions API
- Search for patent applications using various filters
- Search and retrieve petition decisions with detailed information
- Download files, documents, and petition decision documents from the APIs
- Pagination support for large result sets
- Full type annotations and comprehensive test coverage

## Documentation

Full documentation may be found on [Read the Docs](https://pyuspto.readthedocs.io/).

### Data Models

The library uses Python dataclasses to represent API responses. All data models include  type annotations for attributes and methods, making them fully compatible with static type checkers.

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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.
