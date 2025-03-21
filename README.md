# pyUSPTO

A Python client library for interacting with the USPTO APIs.

This package provides clients for interacting with both the USPTO Bulk Data API and the USPTO Patent Data API. It features comprehensive type hints and docstrings for improved developer experience.

## Installation

```bash
pip install pyUSPTO
```

Or install from source:

```bash
git clone https://github.com/DunlapCoddingPC/pyUSPTO.git
cd pyUSPTO
pip install -e .
```

### Development Setup

For development, you can install the required dependencies using the provided requirements files:

```bash
# Install core dependencies
pip install -r requirements.txt

# Install development dependencies (includes testing, linting, etc.)
pip install -r requirements-dev.txt
```

## Features

- Access to both USPTO Bulk Data API and Patent Data API
- Search for products and patents using various filters
- Download files and documents from the APIs
- Type-safe data models using Python dataclasses
- Well-organized package structure for better maintainability

## Package Structure

The library is organized into the following modules:

```
pyUSPTO/
├── __init__.py                # Package initialization and top-level exports
├── config.py                  # Configuration management
├── exceptions.py              # All exceptions in one place
├── clients/                   # Client implementations
│   ├── __init__.py
│   ├── bulk_data.py           # Bulk data client
│   └── patent_data.py         # Patent data client
├── models/                    # Data models
│   ├── __init__.py
│   ├── base.py                # Common model utilities
│   ├── bulk_data.py           # Bulk data models
│   └── patent_data.py         # Patent data models
└── utils/                     # Utilities
    ├── __init__.py
    └── http.py                # HTTP-related utilities
```

This structure provides better separation of concerns, improved maintainability, and a clearer dependency graph.

## Development Status

The development of this library is at version 0.1.6-dev. The following major features have been implemented:

### Documentation Setup (Complete)

The project documentation is set up using Sphinx with the following features:

- ✅ Read the Docs theme
- ✅ Auto-documentation from docstrings using autodoc and napoleon
- ✅ Advanced features like intersphinx, typehints, and copybutton
- ✅ Full documentation structure with installation, quickstart, and API reference

The documentation is structured as follows:

- `index.rst` - Main landing page
- `installation.rst` - Installation instructions
- `quickstart.rst` - Quick start guide
- `api/` - API reference (auto-generated)
- `examples/` - Code examples with explanations
- `development/` - Contributing guidelines

### Package Configuration (Complete)

The project uses modern Python packaging with:

- ✅ Comprehensive pyproject.toml configuration
- ✅ Automatic versioning via setuptools-scm
- ✅ Tool configurations for testing, linting, and type checking

### Future Improvements

- Add more code examples
- Set up documentation hosting on Read the Docs
- Expand test coverage

## Quick Start

### Configuration Options

There are multiple ways to configure the USPTO API clients:

```python
from pyUSPTO import BulkDataClient, PatentDataClient
from pyUSPTO.config import USPTOConfig
import os

# Method 1: Direct API key initialization
client1 = BulkDataClient(api_key="your_api_key_here")

# Method 2: Using USPTOConfig with explicit parameters
config = USPTOConfig(
    api_key="your_api_key_here",
    bulk_data_base_url="https://api.uspto.gov/api/v1/datasets",
    patent_data_base_url="https://api.uspto.gov/api/v1/patent"
)
client2 = BulkDataClient(config=config)

# Method 3: Using environment variables (recommended for production)
os.environ["USPTO_API_KEY"] = "your_api_key_here"
config_from_env = USPTOConfig.from_env()
client3 = BulkDataClient(config=config_from_env)
```

### Securely Handling API Keys

When working with the USPTO APIs, it's important to handle your API keys securely:

1. **Never hardcode API keys in your source code**

   - Hardcoded keys can accidentally be committed to version control
   - This creates security risks if your repository is public or compromised

2. **Environment Variables (Recommended)**

   - Store API keys in environment variables
   - Access them at runtime using `os.environ`
   - For development, use a `.env` file with a package like `python-dotenv`
   - For production, configure environment variables in your deployment platform

   ```python
   # Example using python-dotenv (pip install python-dotenv)
   from dotenv import load_dotenv
   import os

   # Load variables from .env file
   load_dotenv()

   # Access the API key
   api_key = os.environ.get("USPTO_API_KEY")
   client = BulkDataClient(api_key=api_key)
   ```

3. **Secret Management Services**

   - For production applications, consider using a secret management service
   - Options include AWS Secrets Manager, Google Secret Manager, HashiCorp Vault, etc.

4. **Configuration Files**
   - If you must use configuration files, ensure they are:
     - Added to your `.gitignore` file
     - Have restricted file permissions
     - Located outside your application's source directory

Remember that the most secure approach is to use environment variables or a dedicated secrets management solution, especially in production environments.

### Bulk Data API

```python
from pyUSPTO import BulkDataClient

# Initialize the client (see Configuration Options for more methods)
client = BulkDataClient(api_key="your_api_key_here")

# Get all available products
response = client.get_products()
print(f"Found {response.count} products")

# Get a specific product by ID
product = client.get_product_by_id("EXAMPLE_PRODUCT_123")

# Download a file
if product.product_file_bag.file_data_bag:
    file_data = product.product_file_bag.file_data_bag[0]
    downloaded_path = client.download_file(file_data, "./downloads")
    print(f"Downloaded file to: {downloaded_path}")
```

### Patent Data API

```python
from pyUSPTO import PatentDataClient

# Initialize the client (see Configuration Options for more methods)
client = PatentDataClient(api_key="your_api_key_here")

# Search for patents by inventor name
inventor_search = client.search_patents(inventor_name="Smith")
print(f"Found {inventor_search.count} patents with 'Smith' as inventor")

# Get a specific patent by application number
patent = client.get_patent_by_application_number("12345678")
print(f"Retrieved patent application: {patent.application_number_text}")

# Get a specific patent by patent number
patent_search = client.search_patents(patent_number="10000000", limit=1)
if patent_search.count > 0:
    patent = patent_search.patent_file_wrapper_data_bag[0]
    print(f"Retrieved patent: US{patent.application_meta_data.patent_number}")
```

## Type Hints and Documentation

This library is fully typed with Python type hints, making it compatible with static type checkers like mypy and providing excellent IDE support with autocompletion and inline documentation. Every function, method, class, and module has comprehensive docstrings that explain:

- Purpose and functionality
- Parameters with types and descriptions
- Return values with types and descriptions
- Examples where appropriate

Example of type hints in action:

```python
def search_patents(
    self,
    query: Optional[str] = None,
    inventor_name: Optional[str] = None,
    filing_date_from: Optional[str] = None,
    filing_date_to: Optional[str] = None,
    limit: Optional[int] = 25,
) -> PatentDataResponse:
    """
    Search for patents with various filters.

    Args:
        query: Search text in all fields
        inventor_name: Filter by inventor name
        filing_date_from: Filter by filing date from (YYYY-MM-DD)
        filing_date_to: Filter by filing date to (YYYY-MM-DD)
        limit: Number of results to return (default 25)

    Returns:
        PatentDataResponse object containing matching patents
    """
```

## Data Models

The library uses Python dataclasses to represent API responses. All data models include comprehensive type hints and docstrings for improved IDE support and documentation:

### Bulk Data API

- `BulkDataResponse`: Top-level response from the API
- `BulkDataProduct`: Information about a specific product
- `ProductFileBag`: Container for file data elements
- `FileData`: Information about an individual file

Example of a data model with type hints:

```python
@dataclass
class FileData:
    """Represents a file in the bulk data API."""

    file_name: str
    file_size: int
    file_data_from_date: str
    file_data_to_date: str
    file_type_text: str
    file_release_date: str
    file_download_uri: Optional[str] = None
    file_date: Optional[str] = None
    file_last_modified_date_time: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FileData":
        """Create a FileData object from a dictionary."""
        # Implementation...
```

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

All data models include proper type annotations for attributes and methods, making them fully compatible with static type checkers.

## Testing

The library includes unit and integration tests using pytest.

### Running Tests

1. **Run all tests (excluding integration tests)**:

   ```bash
   python -m pytest pyUSPTO/tests/
   ```

2. **Run tests with verbose output**:

   ```bash
   python -m pytest pyUSPTO/tests/ -v
   ```

3. **Run specific test files**:

   ```bash
   python -m pytest pyUSPTO/tests/test_base_client.py
   python -m pytest pyUSPTO/tests/test_bulk_data.py
   python -m pytest pyUSPTO/tests/test_patent_data.py
   ```

4. **Run specific test classes or methods**:

   ```bash
   python -m pytest pyUSPTO/tests/test_bulk_data.py::TestBulkDataClient
   python -m pytest pyUSPTO/tests/test_bulk_data.py::TestBulkDataClient::test_download_file
   ```

5. **Run integration tests** (these are skipped by default):

   ```bash
   # On Windows
   set ENABLE_INTEGRATION_TESTS=true
   python -m pytest pyUSPTO/tests/test_integration.py -v

   # On Unix/Linux/macOS
   ENABLE_INTEGRATION_TESTS=true python -m pytest pyUSPTO/tests/test_integration.py -v
   ```

6. **Run tests with coverage report**:
   ```bash
   python -m pytest pyUSPTO/tests/ --cov=pyUSPTO
   ```

The tests are designed to use mocking to avoid making real API calls, making them fast and reliable. The integration tests are optional and will make real API calls to the USPTO API if enabled.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
