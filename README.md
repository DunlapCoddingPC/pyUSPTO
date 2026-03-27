# USPTO Open Data Portal Client Library

[![PyPI version](https://badge.fury.io/py/pyUSPTO.svg)](https://badge.fury.io/py/pyUSPTO)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Read the Docs](https://img.shields.io/readthedocs/pyuspto)](https://pyuspto.readthedocs.io/en/latest/)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/pyuspto?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLUE&right_color=GREY&left_text=downloads)](https://pepy.tech/projects/pyuspto)

A Python client library for interacting with the United Stated Patent and Trademark Office (USPTO) [Open Data Portal](https://data.uspto.gov/home) APIs.

This package provides clients for interacting with the USPTO Bulk Data API, Patent Data API, Final Petition Decisions API, PTAB (Patent Trial and Appeal Board) APIs, Enriched Citations API, Office Action Text Retrieval API, and Office Action Rejections API.

> [!IMPORTANT]
> The USPTO is in the process of moving their Developer API. This package is only concerned with the new API. The [old API](https://developer.uspto.gov/) was officially retired at the end of 2025; however, some products have not yet been fully transitioned to the Open Data Portal API. The USPTO expects the remaining products to be transitioned to the Open Data Portal in early 2026.

## Quick Start

**Requirements**: Python ≥3.10

```bash
pip install pyUSPTO
```

> [!IMPORTANT]
> You must have an API key for the [USPTO Open Data Portal API](https://data.uspto.gov/myodp/landing).

```python
from pyUSPTO import PatentDataClient, USPTOConfig

# Initialize with config
config = USPTOConfig(api_key="your_api_key_here")
client = PatentDataClient(config=config)

# Search for patent applications
results = client.search_applications(inventor_name_q="Smith", limit=10)
print(f"Found {results.count} applications")
```

## Configuration

All clients require a `USPTOConfig` object. You can create one from environment variables (recommended) or by passing the API key directly.

> [!TIP]
> `USPTOConfig` manages an underlying HTTP session. For long-running applications, use it as a context manager (`with USPTOConfig(...) as config:`) or call `config.close()` when done. See [ADVANCED.md](ADVANCED.md#session-lifecycle) for details.

### Environment Variables (Recommended)

Set the environment variable in your shell:

```bash
export USPTO_API_KEY="your_api_key_here"
```

Then use it in your Python code:

```python
from pyUSPTO import (
    BulkDataClient,
    EnrichedCitationsClient,
    OAActionsClient,
    OARejectionsClient,
    PatentDataClient,
    FinalPetitionDecisionsClient,
    PTABTrialsClient,
    PTABAppealsClient,
    PTABInterferencesClient,
    USPTOConfig,
)

# Load configuration from environment
config = USPTOConfig.from_env()

patent_client = PatentDataClient(config=config)
bulk_client = BulkDataClient(config=config)
petition_client = FinalPetitionDecisionsClient(config=config)
trials_client = PTABTrialsClient(config=config)
appeals_client = PTABAppealsClient(config=config)
interferences_client = PTABInterferencesClient(config=config)
citations_client = EnrichedCitationsClient(config=config)
oa_client = OAActionsClient(config=config)
rejections_client = OARejectionsClient(config=config)
```

### Direct API Key

Alternatively, you can pass your API key directly when creating the config:

```python
from pyUSPTO import USPTOConfig

config = USPTOConfig(api_key="your_api_key_here")
```

## Client Usage Examples

> [!TIP]
> For comprehensive examples with detailed explanations, see the [`examples/`](examples/) directory.

### Patent Data API

```python
from pyUSPTO import PatentDataClient, USPTOConfig

config = USPTOConfig(api_key="your_api_key_here")
client = PatentDataClient(config=config)

# Search for applications by inventor name
response = client.search_applications(inventor_name_q="Smith", limit=2)
print(f"Found {response.count} applications with 'Smith' as inventor (showing up to 2).")

# Get a specific application
app = client.get_application_by_number("18045436")
if app.application_meta_data:
    print(f"Title: {app.application_meta_data.invention_title}")
```

`PatentDataClient` also provides convenience methods for common lookups:

```python
# Look up a patent wrapper by any identifier type (you must use keyword names).
wrapper = client.get_IFW_metadata(application_number="18/045,436")
wrapper = client.get_IFW_metadata(patent_number="11,234,567")
wrapper = client.get_IFW_metadata(publication_number="2023/0012345")
wrapper = client.get_IFW_metadata(PCT_app_number="PCT/US24/12345")

# Look up USPTO status codes
status_codes = client.get_status_codes()
```

See [`examples/patent_data_example.py`](examples/patent_data_example.py) for detailed examples including downloading documents and publications.

### Bulk Data API

```python
from pyUSPTO import BulkDataClient, USPTOConfig

config = USPTOConfig(api_key="your_api_key_here")
client = BulkDataClient(config=config)

# Search for bulk data products
response = client.search_products(query="patent", limit=5)
print(f"Found {response.count} products matching 'patent'")

for product in response.bulk_data_product_bag:
    print(f"  {product.product_title_text} ({product.product_identifier})")

# Get a specific product with its files
product = client.get_product_by_id("PTGRXML", include_files=True, latest=True)
print(f"Product: {product.product_title_text}")
```

See [`examples/bulk_data_example.py`](examples/bulk_data_example.py) for detailed examples including file downloads and archive extraction.

### Final Petition Decisions API

```python
from pyUSPTO import FinalPetitionDecisionsClient, USPTOConfig

config = USPTOConfig(api_key="your_api_key_here")
client = FinalPetitionDecisionsClient(config=config)

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
from pyUSPTO import PTABTrialsClient, USPTOConfig

config = USPTOConfig(api_key="your_api_key_here")
client = PTABTrialsClient(config=config)

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
from pyUSPTO import PTABAppealsClient, USPTOConfig

config = USPTOConfig(api_key="your_api_key_here")
client = PTABAppealsClient(config=config)

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
from pyUSPTO import PTABInterferencesClient, USPTOConfig

config = USPTOConfig(api_key="your_api_key_here")
client = PTABInterferencesClient(config=config)

# Search for interference decisions
response = client.search_decisions(
    decision_date_from_q="2023-01-01",
    limit=5,
)
print(f"Found {response.count} interference decisions since 2023")
```

See [`examples/ptab_interferences_example.py`](examples/ptab_interferences_example.py) for detailed examples including searching by party name and outcome.

### Enriched Citations API

```python
from pyUSPTO import EnrichedCitationsClient, USPTOConfig

config = USPTOConfig(api_key="your_api_key_here")
client = EnrichedCitationsClient(config=config)

# Search for enriched citations by technology center
response = client.search_citations(
    tech_center_q="1700",
    rows=5,
)
print(f"Found {response.count} citations from TC 1700")
```

See [`examples/enriched_citations_example.py`](examples/enriched_citations_example.py) for detailed examples including searching by application number and citation category.

### Office Action Text Retrieval API

```python
from pyUSPTO import OAActionsClient, USPTOConfig

config = USPTOConfig(api_key="your_api_key_here")
client = OAActionsClient(config=config)

# Search for office actions by technology center
response = client.search(
    tech_center_q="1700",
    rows=5,
)
print(f"Found {response.count} office actions from TC 1700")
```

See [`examples/oa_actions_example.py`](examples/oa_actions_example.py) for detailed examples including searching by document code and paginating results.

### Office Action Rejections API

```python
from pyUSPTO import OARejectionsClient, USPTOConfig

config = USPTOConfig(api_key="your_api_key_here")
client = OARejectionsClient(config=config)

# Search for rejections by application number
response = client.search(
    patent_application_number_q="12190351",
    rows=5,
)
print(f"Found {response.count} rejection records for application 12190351")
```

See [`examples/oa_rejections_example.py`](examples/oa_rejections_example.py) for detailed examples including searching by document code and inspecting rejection flags.

## Documentation

Full documentation may be found on [Read the Docs](https://pyuspto.readthedocs.io/).

## Data Models

The library uses Python dataclasses to represent API responses. All data models include type annotations and are fully compatible with static type checkers. For a complete list of all data models, see the [API Reference documentation](https://pyuspto.readthedocs.io/en/latest/api/models/index.html).

## Advanced Topics

For advanced configuration including HTTP settings, environment variables reference, debugging with raw data preservation, and warning control, see [ADVANCED.md](ADVANCED.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.
