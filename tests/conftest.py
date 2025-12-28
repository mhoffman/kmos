"""pytest configuration and fixtures for kmos tests."""

import sys
import os
import tempfile
from unittest.mock import MagicMock


# Mock janaf_data module before any kmos imports
# This prevents the interactive download prompt from triggering during test collection
def pytest_configure(config):
    """Create a mock janaf_data module to prevent download prompts during testing."""
    # Create a temporary directory for mock JANAF data
    # This prevents errors when Species tries to load JANAF files at import time
    temp_janaf_dir = tempfile.mkdtemp(prefix="janaf_test_")

    # Create a mock janaf_data module
    janaf_data_mock = MagicMock()
    janaf_data_mock.__path__ = [temp_janaf_dir]

    # Add it to sys.modules before any imports
    sys.modules["janaf_data"] = janaf_data_mock


def pytest_unconfigure(config):
    """Clean up mock janaf_data module after tests."""
    # Clean up the temporary directory if it exists
    if "janaf_data" in sys.modules:
        janaf_mock = sys.modules["janaf_data"]
        if hasattr(janaf_mock, "__path__") and janaf_mock.__path__:
            temp_dir = janaf_mock.__path__[0]
            if os.path.exists(temp_dir) and temp_dir.startswith(tempfile.gettempdir()):
                # Only delete if it's in the temp directory
                import shutil

                shutil.rmtree(temp_dir, ignore_errors=True)
