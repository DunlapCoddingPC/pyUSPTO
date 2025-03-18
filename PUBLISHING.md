# Publishing pyUSPTO to PyPI

This document provides instructions for building and publishing the pyUSPTO package to PyPI.

## Prerequisites

Before publishing, ensure you have the following:

1. A PyPI account (create one at https://pypi.org/account/register/)
2. The latest version of build and twine:
   ```bash
   pip install --upgrade build twine
   ```

## Preparing for Release

1. **Update Version Number**: 
   - Update the version number in `setup.py` following semantic versioning (MAJOR.MINOR.PATCH)
   - Commit this change to your repository

2. **Check Package Structure**:
   - Ensure all necessary files are included in MANIFEST.in
   - Verify that pyproject.toml is properly configured

3. **Run Tests**:
   - Run the test suite to ensure everything is working:
     ```bash
     python -m pytest pyUSPTO/tests/
     ```

## Building the Package

1. **Clean Previous Builds**:
   ```bash
   rm -rf build/ dist/ *.egg-info/
   ```

2. **Build the Package**:
   ```bash
   python -m build
   ```
   This will create both source distribution (.tar.gz) and wheel (.whl) files in the `dist/` directory.

## Testing the Package

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

## Publishing to PyPI

Once you've verified the package works correctly:

1. **Upload to PyPI**:
   ```bash
   python -m twine upload dist/*
   ```

2. **Verify Installation from PyPI**:
   ```bash
   pip install pyUSPTO
   ```

3. **Tag the Release in Git**:
   ```bash
   git tag -a v0.1.1 -m "Release version 0.1.1"
   git push origin v0.1.1
   ```

## Updating the Package

When you need to update the package:

1. Make your changes
2. Update the version number in `setup.py`
3. Follow the build and publish steps above

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
