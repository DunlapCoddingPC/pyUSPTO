import re

import pytest


def test_package_has_version():
    """Test that the package has a version attribute."""
    import pyUSPTO

    # Test version exists and is accessible
    assert hasattr(pyUSPTO, "__version__")
    assert isinstance(pyUSPTO.__version__, str)
    assert len(pyUSPTO.__version__) > 0

    # Test version format (setuptools-scm style)
    # Pattern matches: major.minor.patch[.devN][+gHASH[.dYYYYMMDD]]
    version_pattern = r"^\d+\.\d+\.\d+(?:\.dev\d+)?(?:\+g[a-f0-9]+(?:\.d\d{8})?)?$"
    assert re.match(
        version_pattern, pyUSPTO.__version__
    ), f"Version format invalid: {pyUSPTO.__version__}"


def test_version_module_attributes():
    """Test that _version module has expected attributes."""
    from pyUSPTO import _version

    # Test all expected attributes exist
    expected_attrs = ["__version__", "version", "__version_tuple__", "version_tuple"]
    for attr in expected_attrs:
        assert hasattr(_version, attr), f"Missing attribute: {attr}"

    # Test string versions are identical
    assert _version.__version__ == _version.version
    assert isinstance(_version.__version__, str)
    assert isinstance(_version.version, str)

    # Test tuple versions are identical
    assert _version.__version_tuple__ == _version.version_tuple
    assert isinstance(_version.__version_tuple__, tuple)
    assert isinstance(_version.version_tuple, tuple)

    # Test __all__ contains expected exports
    assert hasattr(_version, "__all__")
    expected_all = ["__version__", "__version_tuple__", "version", "version_tuple"]
    assert set(_version.__all__) == set(expected_all)


def test_version_tuple_structure():
    """Test the structure of version tuple."""
    from pyUSPTO import _version

    version_tuple = _version.version_tuple

    # Should have at least 3 elements (major, minor, patch)
    assert len(version_tuple) >= 3

    # First three elements should be integers
    assert isinstance(version_tuple[0], int)  # major
    assert isinstance(version_tuple[1], int)  # minor
    assert isinstance(version_tuple[2], int)  # patch

    # # If there are additional elements, they should be strings
    for i in range(3, len(version_tuple)):
        assert isinstance(
            version_tuple[i], str
        ), f"Element {i} should be string, got {type(version_tuple[i])}"


def test_version_consistency():
    """Test that package version is compatible with _version module."""
    import pyUSPTO
    from pyUSPTO import _version

    # Package version and _version module should have compatible base versions
    # They might differ in local version identifiers (the part after +)
    pkg_version = pyUSPTO.__version__
    mod_version = _version.__version__

    # Extract base version (before any + local version identifier)
    pkg_base = pkg_version.split("+")[0]
    mod_base = mod_version.split("+")[0]

    # Base versions should be identical
    assert pkg_base == mod_base, f"Base versions differ: {pkg_base} != {mod_base}"

    # Both should start with the same core version
    assert pkg_version.startswith(pkg_base)
    assert mod_version.startswith(mod_base)


def test_development_version_format():
    """Test specific format for development versions."""
    from pyUSPTO import _version

    version = _version.version

    # If it's a dev version, test the format more specifically
    if ".dev" in version:
        # Should match pattern like: 0.1.6.dev43+g305e1a5.d20250523
        dev_pattern = r"^\d+\.\d+\.\d+\.dev\d+\+g[a-f0-9]+\.d\d{8}$"
        assert re.match(
            dev_pattern, version
        ), f"Development version format invalid: {version}"

        # Test tuple has dev info
        version_tuple = _version.version_tuple
        assert len(version_tuple) >= 4
        assert any(
            "dev" in str(elem) for elem in version_tuple
        ), "Dev version should have 'dev' in tuple"
