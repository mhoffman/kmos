"""Unit tests for JANAF data download functionality."""

import os
from unittest.mock import MagicMock, patch


class TestJanafDownload:
    """Tests for JANAF data download functionality."""

    def test_download_janaf_data_creates_directory(self, tmp_path, monkeypatch):
        """Test that download_janaf_data creates the required directory structure."""
        # Set up a temporary kmos directory
        test_kmos_dir = tmp_path / ".kmos"
        test_janaf_dir = test_kmos_dir / "janaf_data"

        # Mock expanduser to return our test directory
        monkeypatch.setattr(
            os.path,
            "expanduser",
            lambda x: str(tmp_path / ".kmos") if "~/.kmos" in x else x,
        )

        # Mock urllib.request.urlretrieve to avoid actual downloads
        mock_urlretrieve = MagicMock()
        with patch("urllib.request.urlretrieve", mock_urlretrieve):
            from kmos.species import download_janaf_data

            result_dir = download_janaf_data()

            # Verify directory was created
            assert os.path.exists(test_janaf_dir)
            assert os.path.isdir(test_janaf_dir)

            # Verify __init__.py was created
            init_file = test_janaf_dir / "__init__.py"
            assert os.path.exists(init_file)

            # Verify function returns the janaf directory path
            assert result_dir == str(test_janaf_dir)

    def test_download_janaf_data_downloads_all_files(self, tmp_path, monkeypatch):
        """Test that download_janaf_data attempts to download all supported files."""
        # Set up a temporary kmos directory

        # Mock expanduser to return our test directory
        monkeypatch.setattr(
            os.path,
            "expanduser",
            lambda x: str(tmp_path / ".kmos") if "~/.kmos" in x else x,
        )

        # Mock urllib.request.urlretrieve to track downloads
        mock_urlretrieve = MagicMock()

        with patch("urllib.request.urlretrieve", mock_urlretrieve):
            from kmos.species import download_janaf_data, SUPPORTED_JANAF_FILES

            download_janaf_data()

            # Verify urlretrieve was called for each supported file
            assert mock_urlretrieve.call_count == len(SUPPORTED_JANAF_FILES)

            # Verify the correct URLs were used
            for filename in SUPPORTED_JANAF_FILES:
                expected_url = f"https://janaf.nist.gov/tables/{filename}"
                # Check that this URL was requested
                urls_called = [call[0][0] for call in mock_urlretrieve.call_args_list]
                assert expected_url in urls_called

    def test_download_janaf_data_skips_existing_files(self, tmp_path, monkeypatch):
        """Test that download_janaf_data skips files that already exist."""
        # Set up a temporary kmos directory with some existing files
        test_kmos_dir = tmp_path / ".kmos"
        test_janaf_dir = test_kmos_dir / "janaf_data"
        test_janaf_dir.mkdir(parents=True)

        # Create a couple of "existing" files
        existing_files = ["C-067.txt", "H-050.txt"]
        for filename in existing_files:
            (test_janaf_dir / filename).write_text("mock data")

        # Mock expanduser to return our test directory
        monkeypatch.setattr(
            os.path,
            "expanduser",
            lambda x: str(tmp_path / ".kmos") if "~/.kmos" in x else x,
        )

        # Mock urllib.request.urlretrieve to track downloads
        mock_urlretrieve = MagicMock()

        with patch("urllib.request.urlretrieve", mock_urlretrieve):
            from kmos.species import download_janaf_data, SUPPORTED_JANAF_FILES

            download_janaf_data()

            # Should only download files that don't exist
            expected_downloads = len(SUPPORTED_JANAF_FILES) - len(existing_files)
            assert mock_urlretrieve.call_count == expected_downloads

            # Verify existing files were NOT re-downloaded
            urls_called = [call[0][0] for call in mock_urlretrieve.call_args_list]
            for filename in existing_files:
                url = f"https://janaf.nist.gov/tables/{filename}"
                assert url not in urls_called

    def test_module_import_without_janaf_data_in_test_env(self):
        """Test that kmos.species can be imported in test environment without interactive prompt.

        This test verifies that our conftest.py mock prevents the interactive
        download prompt from being triggered during test collection/import.
        """
        # This should not raise an error or prompt for input
        # because conftest.py mocks janaf_data
        from kmos import species

        # Verify the module imported successfully
        assert species is not None
        assert hasattr(species, "download_janaf_data")
        assert hasattr(species, "Species")

    def test_interactive_prompt_calls_download_on_yes(self):
        """Test that answering 'yes' to the interactive prompt calls download_janaf_data.

        This test verifies the download function exists and documents the expected behavior
        when janaf_data is not available and the user is prompted for download.

        The actual code flow in species.py (lines 106-130):
        1. Try: import janaf_data (line 107)
        2. Except ImportError: prompt user (line 118)
        3. If response is yes: call download_janaf_data() (line 124)
        4. Then: import janaf_data again (line 126)

        Note: We can't easily test the actual import-time behavior in a unit test
        because the module is already imported by the time tests run. The conftest.py
        mock prevents the interactive prompt from being triggered during test collection.
        This test verifies the download function exists and is properly structured.
        """
        from kmos.species import download_janaf_data, SUPPORTED_JANAF_FILES

        # Verify the download function exists and is callable
        assert callable(download_janaf_data)

        # Verify the function signature matches what's called in species.py line 124
        import inspect

        sig = inspect.signature(download_janaf_data)
        # download_janaf_data() takes no required parameters
        assert (
            len(
                [
                    p
                    for p in sig.parameters.values()
                    if p.default == inspect.Parameter.empty
                ]
            )
            == 0
        )

        # Verify SUPPORTED_JANAF_FILES exists (used by download function)
        assert isinstance(SUPPORTED_JANAF_FILES, list)
        assert len(SUPPORTED_JANAF_FILES) > 0

    def test_supported_janaf_files_list_exists(self):
        """Test that SUPPORTED_JANAF_FILES list is defined and contains expected files."""
        from kmos.species import SUPPORTED_JANAF_FILES

        # Verify it's a list
        assert isinstance(SUPPORTED_JANAF_FILES, list)

        # Verify it's not empty
        assert len(SUPPORTED_JANAF_FILES) > 0

        # Verify it contains some expected files
        expected_files = ["C-067.txt", "H-050.txt", "O-029.txt"]
        for expected_file in expected_files:
            assert expected_file in SUPPORTED_JANAF_FILES

        # Verify all files have the correct format (letter-number.txt)
        for filename in SUPPORTED_JANAF_FILES:
            assert filename.endswith(".txt")
            assert "-" in filename
