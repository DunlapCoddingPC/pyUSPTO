# pyUSPTO
[![PyPI version](https://badge.fury.io/py/pyUSPTO.svg)](https://badge.fury.io/py/pyUSPTO)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Read the Docs](https://img.shields.io/readthedocs/pyuspto)](https://pyuspto.readthedocs.io/en/latest/)

A Python client library for interacting with the USPTO APIs.

This package provides clients for interacting with both the USPTO Bulk Data API and the USPTO Patent Data API.

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

There are multiple ways to configure the USPTO API clients:

```python
from pyUSPTO import PatentDataClient
from pyUSPTO.config import USPTOConfig
import os

# Method 1: Direct API key initialization
client1 = PatentDataClient(api_key="your_api_key_here")

# Method 2: Using USPTOConfig with explicit parameters
config = USPTOConfig(
    api_key="your_api_key_here",
    bulk_data_base_url="https://api.uspto.gov/api/v1/datasets",
    patent_data_base_url="https://api.uspto.gov/api/v1/patent"
)
client2 = PatentDataClient(config=config)

# Method 3: Using environment variables (recommended for production)
os.environ["USPTO_API_KEY"] = "your_api_key_here"
config_from_env = USPTOConfig.from_env()
client3 = PatentDataClient(config=config_from_env)
```

### Patent Data API

```python
# Search for applications by inventor name
inventor_search = client1.search_applications(inventor_name_q="Smith")
print(f"Found {inventor_search.count} applications with 'Smith' as inventor")
# > Found 104926 applications with 'Smith' as inventor.
```

## Features

- Access to both USPTO Bulk Data API and Patent Data API
- Search for patent applications using various filters
- Download files and documents from the APIs

## Data Models

The library uses Python dataclasses to represent API responses. All data models include  type annotations for attributes and methods, making them fully compatible with static type checkers.

### Bulk Data API

- `BulkDataResponse`: Top-level response from the API
- `BulkDataProduct`: Information about a specific product
- `ProductFileBag`: Container for file data elements
- `FileData`: Information about an individual file

### Patent Data API

- `PatentDataResponse`: Top-level response from the API
- `PatentFileWrapper`: Information about a patent application
- `ApplicationMetaData`: Metadata about a patent application
- `Address`: Represents an address in the patent data
- `Person`, `Applicant`, `Inventor`, `Attorney`: Person-related data classes
- `Assignment`, `Assignor`, `Assignee`: Assignment-related data classes
- `Continuity`, `ParentContinuity`, `ChildContinuity`: Continuity-related data classes
- `PatentTermAdjustmentData`: Patent term adjustment information
- And many more specialized classes for different aspects of patent data

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.
