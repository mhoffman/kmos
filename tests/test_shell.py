#!/usr/bin/env python
"""Test that kmos shell properly supports IPython magic commands."""

from unittest.mock import patch


def test_shell_ipython_embed():
    """Test that sh() function properly calls IPython.embed with user namespace."""
    from kmos.cli import sh

    # Mock IPython.embed to capture the call
    with patch("IPython.embed") as mock_embed:
        # Create some test variables that should be in the namespace
        test_model = "mock_model"
        test_var = 42

        # Call sh() - it should capture these local variables
        try:
            sh(banner="Test banner")
        except SystemExit:
            # IPython.embed might raise SystemExit when mocked
            pass

        # Verify IPython.embed was called
        assert mock_embed.called, "IPython.embed should be called"

        # Get the call arguments
        call_kwargs = mock_embed.call_args.kwargs

        # Verify banner1 parameter is passed
        assert "banner1" in call_kwargs, "banner1 should be in kwargs"
        assert call_kwargs["banner1"] == "Test banner"

        # Verify user_ns parameter is passed
        assert "user_ns" in call_kwargs, "user_ns should be in kwargs"

        # Verify user_ns is a dict
        user_ns = call_kwargs["user_ns"]
        assert isinstance(user_ns, dict), "user_ns should be a dict"

        # Verify it contains expected variables from the calling scope
        assert "test_model" in user_ns, "user_ns should contain test_model"
        assert "test_var" in user_ns, "user_ns should contain test_var"
        assert user_ns["test_model"] == test_model
        assert user_ns["test_var"] == test_var


def test_shell_with_complex_objects():
    """Test that sh() preserves complex objects in the namespace."""
    from unittest.mock import patch, MagicMock
    from kmos.cli import sh
    import numpy as np

    # Create mock objects that simulate what would be in kmos shell
    mock_model = MagicMock()
    mock_model.__class__.__name__ = "KMC_Model"
    np_array = np.array([1, 2, 3])

    # Mock IPython.embed to verify the call
    with patch("IPython.embed") as mock_embed:
        # Variables that would be in the shell namespace
        model = mock_model
        data = np_array

        try:
            sh(banner="Test with complex objects")
        except SystemExit:
            pass

        # Verify IPython.embed was called with user_ns
        assert mock_embed.called, "IPython.embed should be called"
        call_kwargs = mock_embed.call_args.kwargs
        assert "user_ns" in call_kwargs, "user_ns should be in kwargs"

        user_ns = call_kwargs["user_ns"]

        # Verify objects are in the namespace
        assert "model" in user_ns, "model should be in namespace"
        assert "data" in user_ns, "data should be in namespace"
        assert "np" in user_ns, "np should be in namespace"

        # Verify they're the actual objects (use the local variables to satisfy linter)
        assert user_ns["model"] is model, "model should be the same object"
        assert user_ns["data"] is data, "data should be the same object"
        assert user_ns["np"] is np, "np should be numpy module"

        # With this setup, magic commands like %time would work on these objects
        # For example: %time model.do_steps(1000)
        # The namespace is properly configured for all IPython features


def test_ipython_magic_compatibility():
    """
    Test that verifies the shell setup is compatible with IPython magic commands.

    This test doesn't actually execute magic commands (that would require an
    interactive session), but it verifies that the shell is set up correctly
    to support them.
    """
    from unittest.mock import patch
    from kmos.cli import sh

    # Mock IPython.embed to verify the namespace is properly passed
    with patch("IPython.embed") as mock_embed:
        # Call sh with some variables in scope
        test_value = 123

        try:
            sh(banner="Test compatibility")
        except SystemExit:
            pass

        # Verify embed was called
        assert mock_embed.called, "IPython.embed should be called"

        # Verify it was called with banner1 and user_ns
        call_kwargs = mock_embed.call_args.kwargs

        # Check that user_ns was provided
        assert "user_ns" in call_kwargs, "user_ns should be provided to IPython.embed"

        # Verify test_value is in the namespace
        assert "test_value" in call_kwargs["user_ns"], "test_value should be in user_ns"
        assert call_kwargs["user_ns"]["test_value"] == test_value

        # The fact that user_ns is being passed means magic commands will work,
        # because IPython.embed() with user_ns properly sets up the interactive
        # namespace with all IPython features including magic commands


if __name__ == "__main__":
    test_shell_ipython_embed()
    test_shell_with_complex_objects()
    test_ipython_magic_compatibility()
    print("All tests passed!")
