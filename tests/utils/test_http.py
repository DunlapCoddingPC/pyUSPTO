"""
Tests for the pyUSPTO.utils.http module.
"""

from unittest.mock import ANY, MagicMock, patch

import pytest

from pyUSPTO.utils.http import create_session


class TestHttpUtils:
    """Tests for HTTP utility functions."""

    def test_create_session(self) -> None:
        """Test that create_session configures session correctly."""
        with patch("pyUSPTO.utils.http.requests.Session") as mock_session:
            # Setup the mock
            mock_session_instance = MagicMock()
            mock_session.return_value = mock_session_instance

            # Call the function with custom headers
            headers = {"X-API-KEY": "test_key"}
            session = create_session(headers=headers)

            # Verify the session was created
            mock_session.assert_called_once()

            # Verify headers were set
            mock_session_instance.headers.update.assert_called_once_with(headers)

            # Verify adapters were mounted
            mock_session_instance.mount.assert_any_call("http://", ANY)
            mock_session_instance.mount.assert_any_call("https://", ANY)

            # Should be called exactly twice - once for http and once for https
            assert mock_session_instance.mount.call_count == 2

            # Return the session
            assert session == mock_session_instance

    def test_parse_response(self) -> None:
        """Test parse_response function."""
        from pyUSPTO.utils.http import parse_response

        # Create a mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"key": "value"}

        # Call the function
        result = parse_response(mock_response)

        # Verify the response was parsed
        mock_response.json.assert_called_once()
        assert result == {"key": "value"}

    def test_create_session_default_params(self) -> None:
        """Test create_session with default parameters."""
        with patch("pyUSPTO.utils.http.requests.Session") as mock_session:
            # Setup the mock
            mock_session_instance = MagicMock()
            mock_session.return_value = mock_session_instance

            # Call the function with defaults
            session = create_session()

            # Verify the session was created
            mock_session.assert_called_once()

            # Verify adapters were mounted
            mock_session_instance.mount.assert_any_call("http://", ANY)
            mock_session_instance.mount.assert_any_call("https://", ANY)

            # Return the session
            assert session == mock_session_instance
