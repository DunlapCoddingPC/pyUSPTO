# Contributing to pyUSPTO

We welcome contributions from the community! pyUSPTO is designed to be a useful tool for interacting with USPTO APIs, and your input helps make it better for everyone.

## Ways to Contribute

- **Code Contributions**: Implement new features, fix bugs, or improve performance
- **Documentation**: Improve or expand documentation, add examples, fix typos
- **Bug Reports**: Report bugs or suggest improvements
- **Feature Requests**: Suggest new features or enhancements
- **Community Support**: Help answer questions and support other users

## Getting Started with Contributing

### Fork the Repository

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/your-username/pyUSPTO.git
cd pyUSPTO
```

### Set Up Development Environment

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .
```

### Create a Branch

```bash
# Create a branch for your contribution
git checkout -b feature/your-feature-name
```

### Make Your Changes

- Follow the code style guidelines
- Add tests for new functionality
- Update documentation as needed

### Run Tests

```bash
# Run the test suite
python -m pytest tests/ --cov=pyUSPTO --cov-report=term --cov-report=term-missing -vv

# Run linting and type checking
flake8 src/pyUSPTO --count --select=E9,F63,F7,F82,D100,D101,D102,D103 --show-source --statistics
mypy ./src/

# Correct Formatting 
black .


```

### Submit a Pull Request

- Push your changes to your fork
- Submit a pull request from your branch to our main branch
- Provide a clear description of the changes and any related issues

## Code Style Guidelines

- Follow PEP 8 for Python code style
- Use type hints for all function parameters and return values
- Write comprehensive docstrings for all functions, classes, and modules
- Keep functions focused
- Use meaningful variable and function names
- Follow existing patterns in the codebase

## Documentation Guidelines

- Use docstrings for all public modules, functions, classes, and methods
- Include type information in docstrings (already captured by type hints)
- Document parameters, return values, and raised exceptions
- Add examples where appropriate

## Commit Message Guidelines

We follow the Conventional Commits specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

Types include:

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code changes that neither fix bugs nor add features
- **test**: Adding or modifying tests
- **chore**: Changes to the build process or auxiliary tools

## Pull Request Process

1. Update the README.md or documentation with details of changes if appropriate
2. Update the CHANGELOG.md with details of changes
3. The PR should work for Python 3.10 and above
4. PRs require approval from at least one maintainer
5. Once approved, a maintainer will merge your PR

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

## Versioning

The project uses setuptools-scm for version management:

- Versions are derived from git tags
- When making releases, the maintainers will handle the versioning
