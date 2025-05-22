# PyPI Publication Plan for "pyUSPTO"

This is a comprehensive plan to prepare the USPTO Open Data Portal (ODP) API client for PyPI publication under the name "pyUSPTO".


## Completed Items

1. **Documentation Setup**:

   - ✅ Sphinx documentation has been set up in the docs directory
   - ✅ Configured with extensions: autodoc, viewcode, napoleon, intersphinx, sphinx_autodoc_typehints, sphinx_copybutton, myst_parser
   - ✅ ReadTheDocs theme is configured

2. **Packaging Configuration**:
   - ✅ Enhanced `pyproject.toml` with project metadata:
     - Added name, description, authors, readme, license information
     - Moved configuration from setup.py to pyproject.toml using the newer [project] format
     - setuptools_scm configuration is complete
     - Tool configurations for mypy, isort, pytest, and coverage are in place

## Items for Future Consideration

1. **Read the Docs Integration**: Set up documentation hosting on Read the Docs.

2. **Comprehensive Integration Tests**: Add complete test coverage for USPTO API endpoints:
   - Enhance test infrastructure with improved fixtures and utilities
   - Add tests for missing Patent Data API detail endpoints:
     - `/api/v1/patent/applications/{applicationNumberText}/meta-data`
     - `/api/v1/patent/applications/{applicationNumberText}/adjustment`
     - `/api/v1/patent/applications/{applicationNumberText}/assignment`
     - `/api/v1/patent/applications/{applicationNumberText}/attorney`
     - `/api/v1/patent/applications/{applicationNumberText}/continuity`
     - `/api/v1/patent/applications/{applicationNumberText}/foreign-priority`
     - `/api/v1/patent/applications/{applicationNumberText}/transactions`
     - `/api/v1/patent/applications/{applicationNumberText}/documents`
     - `/api/v1/patent/applications/{applicationNumberText}/associated-documents`
     - `/api/v1/download/applications/{applicationNumber}/{documentId}`
   - Add tests for POST versions of search endpoints
   - Implement edge case testing for error responses and special characters

## Recently Completed

1. **Changelog**: Added a CHANGELOG.md file to track version changes, providing benefits beyond GitHub releases:

   - Accessible to users who download from PyPI without visiting GitHub
   - Documentation that stays with the codebase
   - More detailed explanations than typical in commit messages
   - Historical record when browsing the repository files

2. **Contributing Guidelines**: Added a CONTRIBUTING.md file with guidelines for contributors:
   - Clear process for setting up the development environment
   - Instructions for making changes and submitting PRs
   - Code style and documentation guidelines
   - Commit message and PR process guidelines
   - Information about versioning with setuptools-scm

## Publication Process

### Prerequisites

Before publishing, ensure you have the following:

1. A PyPI account (create one at https://pypi.org/account/register/)
2. The latest version of build and twine:
   ```bash
   pip install --upgrade build twine
   ```

### Preparing for Release

1. **Update Version Number**:

   - With setuptools-scm, this is handled through git tags
   - Ensure all changes are committed to your repository

2. **Check Package Structure**:

   - Ensure all necessary files are included in MANIFEST.in
   - Verify that pyproject.toml is properly configured

3. **Run Tests**:

   - Run the test suite to ensure everything is working:
      ```bash
      python -m pytest -v
      ```

   - Test Coverage:
     ```bash
     python -m pytest --cov=pyUSPTO --cov-report=term --cov-report=term-missing -vv > ./notes/full_coverage_report.txt
     ```

   - Test Typecheck
     ```bash
     mypy pyUSPTO > ./notes/mypy_results.txt
     ```

### Pre-Publication Checklist

1. Ensure all "Items for Immediate Action" are completed
2. Run all tests to verify functionality
3. Check package rendering with `twine check dist/*`
4. Test installation from TestPyPI

### Building the Package

1. **Clean Previous Builds**:

   ```bash
   rm -rf build/ dist/ *.egg-info/
   ```

2. **Tag the release in Git** (this must be done first since setuptools-scm uses git tags to determine the version):

   ```bash
   git tag -a v0.1.3 -m "Release version 0.1.3"
   git push origin v0.1.3
   ```

3. **Build the Package** (this will automatically pick up the version from the git tag):
   ```bash
   python -m build
   ```
   This will create both source distribution (.tar.gz) and wheel (.whl) files in the `dist/` directory.

### Testing the Package

Before uploading to PyPI, it's recommended to test your package using TestPyPI:

1. **Upload to TestPyPI**:

   ```bash
   python -m twine upload --repository testpypi dist/*
   ```

2. **Install from TestPyPI**:

   ```bash
   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pyUSPTO
   ```

3. **Verify Installation**:
   ```python
   from pyUSPTO import BulkDataClient
   # Basic test to ensure the package is working
   ```

### Publishing to PyPI

Once you've verified the package works correctly:

1. **Upload to PyPI**:

   ```bash
   python -m twine upload dist/*
   ```

2. **Verify Installation from PyPI**:
   ```bash
   pip install pyUSPTO
   ```

### Future Updates

For future updates:

1. Update documentation
2. Follow the versioning workflow:
   - Make code changes
   - Ensure tests pass
   - Create a new git tag for the version
   - Build and publish the package

## Understanding setuptools-scm

The project uses setuptools-scm for automatic version management based on git tags:

### Key Components

- `setup.py`: Uses `use_scm_version=True` instead of hardcoded version
- `pyproject.toml`: Contains configuration in the `[tool.setuptools_scm]` section
- `_version.py`: Automatically generated file containing the current version
- `__init__.py`: Imports version from `_version.py` with a fallback

### How It Works

1. When building the package, setuptools-scm:

   - Examines git tags to determine the version
   - For tagged commits: Uses the tag name as the version (e.g., "v1.2.3" becomes "1.2.3")
   - For development: Adds local version identifiers based on commit distance and hash
   - Writes the determined version to `_version.py`

2. Benefits:
   - Single source of truth for version (git tags)
   - Automatically handles pre-release and dev versions
   - No need to manually update version in multiple files
   - Consistent version across package metadata and runtime

## Troubleshooting

- **Description Rendering Issues**: If the long description doesn't render correctly on PyPI, check your Markdown syntax and consider using the `--strict` flag with twine to check for rendering issues:

  ```bash
  python -m twine check dist/*
  ```

- **Package Name Conflicts**: If the name is already taken on PyPI, you'll need to choose a different name.

- **Authentication Issues**: If you encounter authentication problems, you can create a `.pypirc` file in your home directory:

  ```
  [distutils]
  index-servers =
      pypi
      testpypi

  [pypi]
  username = your_username
  password = your_password

  [testpypi]
  repository = https://test.pypi.org/legacy/
  username = your_username
  password = your_password
  ```

## Security Best Practices

- Consider using API tokens instead of your password for authentication
- Enable two-factor authentication on your PyPI account
- Use a `.pypirc` file with restricted permissions (chmod 600)
