#!/usr/bin/env python
"""Tests for kmos.cli module."""

from unittest.mock import Mock
from kmos import cli


def test_cli_match_keys_none():
    """Test whether expressive error is raised when no usage argument matches."""
    parser = Mock()
    usage = {"export": "...", "import": "...", "build": "..."}

    # Try to match a command that doesn't exist
    cli.match_keys("xyz", usage, parser)

    # Verify parser.error was called with appropriate message
    parser.error.assert_called_once()
    error_msg = parser.error.call_args[0][0]
    assert 'Command "xyz" not understood' in error_msg


def test_cli_match_keys_multiple():
    """Test whether expressive error is raised when multiple usage arguments match."""
    parser = Mock()
    usage = {"export": "...", "extract": "...", "build": "..."}

    # Try to match a command prefix that matches multiple commands
    cli.match_keys("ex", usage, parser)

    # Verify parser.error was called with appropriate message
    parser.error.assert_called_once()
    error_msg = parser.error.call_args[0][0]
    assert 'Command "ex" ambiguous' in error_msg
    assert "export" in error_msg or "extract" in error_msg


def test_cli_match_keys_single():
    """Test that matching usage arg is returned if exactly one candidate matches."""
    parser = Mock()
    usage = {"export": "...", "import": "...", "build": "..."}

    # Test exact match
    result = cli.match_keys("export", usage, parser)
    assert result == "export"
    parser.error.assert_not_called()

    # Test prefix match with single candidate
    result = cli.match_keys("exp", usage, parser)
    assert result == "export"
    parser.error.assert_not_called()

    # Test another prefix
    result = cli.match_keys("b", usage, parser)
    assert result == "build"
    parser.error.assert_not_called()
