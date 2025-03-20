"""Test that executes setup.py to get coverage."""

import os
import sys
import unittest
from importlib.util import module_from_spec, spec_from_file_location
from unittest.mock import MagicMock, mock_open, patch


class TestSetupExecution(unittest.TestCase):
    @patch("setuptools.setup")
    def test_setup_execution(self, mock_setup) -> None:
        """Test that setup.py executes and calls setup() with correct args."""
        # Mock open for README.md
        readme_content = "# pyUSPTO\nTest README content"

        with patch("builtins.open", mock_open(read_data=readme_content)):
            # Add the directory containing setup.py to sys.path
            sys.path.insert(0, os.path.abspath("."))

            # Load setup.py as a module
            spec = spec_from_file_location("setup_module", "setup.py")
            if spec is None:
                self.fail("Could not find setup.py file")

            setup_module = module_from_spec(spec)
            if spec.loader is None:
                self.fail("No loader found for setup.py")

            spec.loader.exec_module(setup_module)

            # Check that setup was called
            mock_setup.assert_called_once()

            # Verify the arguments passed to setup()
            args, kwargs = mock_setup.call_args
            self.assertEqual(kwargs["name"], "pyUSPTO")
            self.assertTrue(kwargs["use_scm_version"])
            self.assertEqual(kwargs["author"], "Andrew Piechocki")
            self.assertEqual(kwargs["author_email"], "apiechocki@dunlapcodding.com")
            self.assertEqual(
                kwargs["description"], "Python client for accessing USPTO APIs"
            )
            self.assertEqual(kwargs["long_description"], readme_content)
            self.assertEqual(kwargs["long_description_content_type"], "text/markdown")
            self.assertEqual(
                kwargs["url"], "https://github.com/DunlapCoddingPC/pyUSPTO"
            )
            self.assertEqual(kwargs["python_requires"], ">=3.10")

            # Check install_requires
            self.assertIn("requests>=2.25.0", kwargs["install_requires"])

            # Check classifiers
            classifiers = kwargs["classifiers"]
            self.assertIn("Programming Language :: Python :: 3", classifiers)
            self.assertIn("License :: OSI Approved :: MIT License", classifiers)

            # Check keywords
            self.assertIn("uspto", kwargs["keywords"])
            self.assertIn("patent", kwargs["keywords"])


if __name__ == "__main__":
    unittest.main()
