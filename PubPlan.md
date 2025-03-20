# PyPI Publication Plan for "pyUSPTO"

This is a comprehensive plan to prepare the USPTO ODP API client for PyPI publication under the name "pyUSPTO".

## Current Status

- Package name in `setup.py` is now "pyUSPTO"
- Version management implemented using setuptools-scm:
  - No hardcoded versions needed in `setup.py` or `__init__.py`
  - Version automatically derived from git tags
  - `pyproject.toml` configured with `setuptools_scm`
- Old files have been cleaned out
- Basic project structure is in place
- Duplicate exception definitions fixed

## Items for Immediate Action

### Items for Cline to Fix

1. **Documentation Setup**:

   - Set up Sphinx documentation as detailed in the docs-setup-guide.md file
   - Follow the step-by-step instructions to create the docs directory structure and necessary files

### Items for Manual Completion

4. **Git Tagging**: Since setuptools-scm derives versions from git tags, implement a consistent tagging convention (e.g., "v1.2.3") and document the release workflow.

5. **Packaging Configuration**: Enhance `pyproject.toml` with more project metadata:
   - Add project metadata like `name`, `description`, `authors`, `readme`, `license`, etc.
   - Consider moving more configuration from setup.py to pyproject.toml
   - Ensure setuptools_scm configuration is complete (currently minimal)
   - Add additional tool configurations (black, isort, pytest, etc.)

## Items for Future Consideration

1. **Read the Docs Integration**: Set up documentation hosting on Read the Docs.

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

### Pre-Publication Checklist

1. Ensure all "Items for Immediate Action" are completed
2. Run all tests to verify functionality
3. Check package rendering with `twine check dist/*`
4. Test installation from TestPyPI

### Publication Steps

1. **Tag the release in Git** (this must be done first since setuptools-scm uses git tags to determine the version):

   ```bash
   git tag -a v0.1.3 -m "Release version 0.1.3"
   git push origin v0.1.3
   ```

2. **Build the package** (this will automatically pick up the version from the git tag):

   ```bash
   python -m build
   ```

3. **Upload to TestPyPI first**:

   ```bash
   python -m twine upload --repository testpypi dist/*
   ```

4. **Verify installation from TestPyPI**:

   ```bash
   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pyUSPTO
   ```

5. **Upload to PyPI** (only after successful verification on TestPyPI):
   ```bash
   python -m twine upload dist/*
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
