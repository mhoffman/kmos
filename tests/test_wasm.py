"""
Comprehensive unit tests for WASM functionality.

Tests cover:
- apply_wasm_modifications() - Source code modifications for WASM compatibility
- create_c_bindings() - C bindings generation
- build_wasm() - Full WASM compilation pipeline (requires Docker)
- Backend compatibility - All three backends (local_smart, lat_int, otf)
"""

import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import functions to test
from kmos.utils import apply_wasm_modifications, create_c_bindings, build_wasm


class TestApplyWasmModifications:
    """Test WASM-specific source code modifications."""

    def test_array_slice_replacement(self, tmp_path):
        """Test that array slice assignments are replaced with explicit assignments."""
        # Create proclist.f90 with array slice pattern
        proclist = tmp_path / "proclist.f90"
        proclist_content = """
subroutine do_something()
    integer :: lsite(4)
    integer :: nr_site

    ! This line should be modified
        lsite = nr2lattice(nr_site, :)

end subroutine
"""
        proclist.write_text(proclist_content)

        # Apply modifications
        apply_wasm_modifications(str(tmp_path))

        # Verify replacement
        content = proclist.read_text()
        assert "! WASM: Explicit element assignment instead of array slice" in content
        assert "lsite(1) = nr2lattice(nr_site, 1)" in content
        assert "lsite(2) = nr2lattice(nr_site, 2)" in content
        assert "lsite(3) = nr2lattice(nr_site, 3)" in content
        assert "lsite(4) = nr2lattice(nr_site, 4)" in content
        # Original line should be gone
        assert "lsite = nr2lattice(nr_site, :)" not in content.replace("! WASM:", "")

    def test_multiple_array_slices(self, tmp_path):
        """Test that multiple array slice patterns are all replaced."""
        proclist = tmp_path / "proclist.f90"
        proclist_content = """
subroutine proc1()
        lsite = nr2lattice(nr_site, :)
end subroutine

subroutine proc2()
            lsite = nr2lattice(nr_site, :)
end subroutine
"""
        proclist.write_text(proclist_content)

        apply_wasm_modifications(str(tmp_path))

        content = proclist.read_text()
        # Both occurrences should be replaced
        assert content.count("lsite(1) = nr2lattice(nr_site, 1)") == 2
        assert content.count("lsite(2) = nr2lattice(nr_site, 2)") == 2

    def test_idempotency(self, tmp_path):
        """Test that modifications are idempotent (running twice doesn't double-modify)."""
        proclist = tmp_path / "proclist.f90"
        proclist_content = """
        lsite = nr2lattice(nr_site, :)
"""
        proclist.write_text(proclist_content)

        # Apply once
        apply_wasm_modifications(str(tmp_path))
        content_after_first = (tmp_path / "proclist.f90").read_text()

        # Apply again
        apply_wasm_modifications(str(tmp_path))
        content_after_second = (tmp_path / "proclist.f90").read_text()

        # Content should be identical after both applications
        assert content_after_first == content_after_second
        # Should only have one WASM comment
        assert content_after_second.count("! WASM:") == 1

    def test_no_modification_when_already_modified(self, tmp_path):
        """Test that files already containing WASM modifications are not modified again."""
        proclist = tmp_path / "proclist.f90"
        proclist_content = """
        ! WASM: Explicit element assignment instead of array slice
        lsite(1) = nr2lattice(nr_site, 1)
        lsite(2) = nr2lattice(nr_site, 2)
        lsite(3) = nr2lattice(nr_site, 3)
        lsite(4) = nr2lattice(nr_site, 4)
"""
        proclist.write_text(proclist_content)

        # Get content before
        content_before = proclist.read_text()

        # Apply modifications
        apply_wasm_modifications(str(tmp_path))

        # Content should be unchanged
        content_after = proclist.read_text()
        assert content_before == content_after

    def test_no_pattern_found(self, tmp_path):
        """Test behavior when no array slice patterns exist."""
        proclist = tmp_path / "proclist.f90"
        proclist_content = """
subroutine simple()
    integer :: x
    x = 5
end subroutine
"""
        proclist.write_text(proclist_content)

        # Should not raise error
        apply_wasm_modifications(str(tmp_path))

        # Content should be unchanged
        content = proclist.read_text()
        assert content == proclist_content
        assert "! WASM:" not in content

    def test_missing_proclist_file(self, tmp_path):
        """Test behavior when proclist.f90 doesn't exist."""
        # Should not raise error
        apply_wasm_modifications(str(tmp_path))

    def test_empty_proclist_file(self, tmp_path):
        """Test behavior with empty proclist.f90."""
        proclist = tmp_path / "proclist.f90"
        proclist.write_text("")

        # Should not raise error
        apply_wasm_modifications(str(tmp_path))

        # File should still be empty
        assert proclist.read_text() == ""

    def test_preserves_indentation(self, tmp_path):
        """Test that indentation is preserved in replacements."""
        proclist = tmp_path / "proclist.f90"
        proclist_content = """
subroutine test1()
    lsite = nr2lattice(nr_site, :)
end subroutine

subroutine test2()
        lsite = nr2lattice(nr_site, :)
end subroutine

subroutine test3()
            lsite = nr2lattice(nr_site, :)
end subroutine
"""
        proclist.write_text(proclist_content)

        apply_wasm_modifications(str(tmp_path))

        content = proclist.read_text()
        # Check that different indentation levels are preserved
        assert "    lsite(1) = nr2lattice(nr_site, 1)" in content
        assert "        lsite(1) = nr2lattice(nr_site, 1)" in content
        assert "            lsite(1) = nr2lattice(nr_site, 1)" in content


class TestCreateCBindings:
    """Test C bindings generation."""

    def test_bindings_file_created(self, tmp_path):
        """Test that c_bindings.f90 is created."""
        os.chdir(tmp_path)

        create_c_bindings()

        bindings_file = tmp_path / "c_bindings.f90"
        assert bindings_file.exists()
        assert bindings_file.stat().st_size > 0

    def test_bindings_content_structure(self, tmp_path):
        """Test that c_bindings.f90 has the correct structure."""
        os.chdir(tmp_path)

        create_c_bindings()

        content = (tmp_path / "c_bindings.f90").read_text()

        # Check module declaration
        assert "module c_bindings" in content
        assert "use iso_c_binding" in content
        assert "use kind_values" in content
        assert "use base" in content
        assert "use lattice" in content
        assert "use proclist" in content

        # Check end module
        assert "end module c_bindings" in content

    def test_required_functions_present(self, tmp_path):
        """Test that all required C-callable functions are present."""
        os.chdir(tmp_path)

        create_c_bindings()

        content = (tmp_path / "c_bindings.f90").read_text()

        # List of required functions for WASM interface
        required_functions = [
            "kmc_init",
            "kmc_do_step",
            "kmc_get_time",
            "kmc_get_species",
            "kmc_get_system_size",
            "kmc_set_rate",
            "kmc_get_nr_sites",
            "kmc_get_accum_rate",
            "kmc_get_rate",
            "kmc_update_accum_rate",
            "kmc_get_nr2lattice",
            "kmc_get_debug_last_proc",
            "kmc_get_debug_last_site",
        ]

        for func_name in required_functions:
            assert f'bind(C, name="{func_name}")' in content

    def test_overwrites_existing_bindings(self, tmp_path):
        """Test that creating bindings overwrites existing c_bindings.f90."""
        os.chdir(tmp_path)

        # Create initial bindings
        bindings_file = tmp_path / "c_bindings.f90"
        bindings_file.write_text("old content")

        # Create new bindings
        create_c_bindings()

        # Content should be new, not "old content"
        content = bindings_file.read_text()
        assert "old content" not in content
        assert "module c_bindings" in content

    def test_bindings_fortran_syntax(self, tmp_path):
        """Test that generated bindings have valid Fortran syntax."""
        os.chdir(tmp_path)

        create_c_bindings()

        content = (tmp_path / "c_bindings.f90").read_text()

        # Check for common Fortran syntax elements
        assert "implicit none" in content
        assert "contains" in content
        assert "subroutine" in content or "function" in content


@pytest.mark.docker
class TestBuildWasm:
    """Test WASM compilation (requires Docker)."""

    def create_minimal_fortran_sources(self, directory):
        """Helper to create minimal Fortran source files for testing."""
        # Create kind_values.f90
        (directory / "kind_values.f90").write_text("""
module kind_values
    implicit none
    integer, parameter :: iint = selected_int_kind(9)
    integer, parameter :: rsingle = selected_real_kind(6, 37)
    integer, parameter :: rdouble = selected_real_kind(15, 307)
end module kind_values
""")

        # Create base.f90
        (directory / "base.f90").write_text("""
module base
    use kind_values
    implicit none
    real(kind=rdouble), private :: kmc_time = 0.0d0
contains
    subroutine get_kmc_time(time)
        real(kind=rdouble), intent(out) :: time
        time = kmc_time
    end subroutine

    subroutine get_kmc_step(step)
        integer(kind=iint), intent(out) :: step
        step = 0
    end subroutine
end module base
""")

        # Create lattice.f90
        (directory / "lattice.f90").write_text("""
module lattice
    use kind_values
    implicit none
    integer(kind=iint), dimension(3), public :: system_size = [10, 10, 1]
    integer(kind=iint), public :: spuck = 1
    integer(kind=iint), dimension(:,:), allocatable :: nr2lattice
contains
    subroutine allocate_system(n, system_name, layer, seed, no_banner)
        integer(kind=iint), dimension(2), intent(in) :: n
        character(len=*), intent(in) :: system_name
        integer(kind=iint), intent(in) :: layer, seed
        logical, intent(in) :: no_banner
        system_size(1:2) = n
        allocate(nr2lattice(100, 4))
    end subroutine

    function lattice2nr(lattice)
        integer(kind=iint), dimension(4), intent(in) :: lattice
        integer(kind=iint) :: lattice2nr
        lattice2nr = 1
    end function

    function get_species(lattice)
        integer(kind=iint), dimension(4), intent(in) :: lattice
        integer(kind=iint) :: get_species
        get_species = 0
    end function
end module lattice
""")

        # Create proclist.f90
        (directory / "proclist.f90").write_text("""
module proclist
    use kind_values
    use base
    use lattice
    implicit none
    integer(kind=iint), public :: nr_of_proc = 1
    integer(kind=iint), dimension(:), allocatable, public :: avail_sites
contains
    subroutine init(system_size, system_name, layer, seed, no_banner)
        integer(kind=iint), dimension(2), intent(in) :: system_size
        character(len=*), intent(in) :: system_name
        integer(kind=iint), intent(in) :: layer, seed
        logical, intent(in) :: no_banner
        call allocate_system(system_size, system_name, layer, seed, no_banner)
    end subroutine

    subroutine do_kmc_step()
        ! Minimal implementation
    end subroutine

    subroutine set_rate_const(proc_nr, rate)
        integer(kind=iint), intent(in) :: proc_nr
        real(kind=rsingle), intent(in) :: rate
    end subroutine
end module proclist
""")

    def test_build_success_with_valid_sources(self, tmp_path):
        """Test successful WASM build with valid Fortran sources."""
        os.chdir(tmp_path)
        self.create_minimal_fortran_sources(tmp_path)

        # Create a mock options object
        options = MagicMock()

        # This will actually try to run Docker
        try:
            build_wasm(options)

            # Check that output files were created
            assert (tmp_path / "kmc_model.js").exists()
            assert (tmp_path / "kmc_model.wasm").exists()

            # Check file sizes are reasonable (not empty, not too small)
            js_size = (tmp_path / "kmc_model.js").stat().st_size
            wasm_size = (tmp_path / "kmc_model.wasm").stat().st_size

            assert js_size > 1000, "JS file too small"
            assert wasm_size > 1000, "WASM file too small"

        except Exception as e:
            if "docker" in str(e).lower():
                pytest.skip(f"Docker not available: {e}")
            else:
                raise

    def test_build_fails_with_missing_files(self, tmp_path):
        """Test that build fails with clear error when source files missing."""
        os.chdir(tmp_path)

        # Don't create source files
        options = MagicMock()

        with pytest.raises(IOError) as exc_info:
            build_wasm(options)

        assert "kind_values.f90" in str(exc_info.value)

    def test_build_creates_c_bindings(self, tmp_path):
        """Test that build_wasm creates c_bindings.f90 if it doesn't exist."""
        os.chdir(tmp_path)
        self.create_minimal_fortran_sources(tmp_path)

        options = MagicMock()

        try:
            build_wasm(options)

            # c_bindings.f90 should have been created
            assert (tmp_path / "c_bindings.f90").exists()

        except Exception as e:
            if "docker" in str(e).lower():
                pytest.skip(f"Docker not available: {e}")
            else:
                raise

    def test_build_applies_wasm_modifications(self, tmp_path):
        """Test that build_wasm applies WASM modifications to source files."""
        os.chdir(tmp_path)
        self.create_minimal_fortran_sources(tmp_path)

        # Add array slice pattern to proclist.f90
        proclist = tmp_path / "proclist.f90"
        content = proclist.read_text()
        content += """
subroutine test_proc()
    integer :: lsite(4), nr_site
    lsite = nr2lattice(nr_site, :)
end subroutine
"""
        proclist.write_text(content)

        options = MagicMock()

        try:
            build_wasm(options)

            # Check that modifications were applied
            modified_content = proclist.read_text()
            assert "! WASM:" in modified_content
            assert "lsite(1) = nr2lattice(nr_site, 1)" in modified_content

        except Exception as e:
            if "docker" in str(e).lower():
                pytest.skip(f"Docker not available: {e}")
            else:
                raise


@pytest.mark.wasm
@pytest.mark.parametrize("backend", ["local_smart", "lat_int", "otf"])
class TestWasmBackendCompatibility:
    """Test WASM export with all backends."""

    def test_export_backend_creates_bindings(self, backend, tmp_path):
        """Test that WASM export creates c_bindings.f90 for all backends."""
        # This test would typically use kmos export command
        # For now, we test that create_c_bindings works regardless of backend
        os.chdir(tmp_path)

        create_c_bindings()

        bindings_file = tmp_path / "c_bindings.f90"
        assert bindings_file.exists()

        # Bindings content should be the same for all backends
        content = bindings_file.read_text()
        assert "module c_bindings" in content

    def test_modifications_work_for_backend(self, backend, tmp_path):
        """Test that WASM modifications work regardless of backend."""
        # Create a proclist.f90 with array slice pattern
        proclist = tmp_path / "proclist.f90"
        proclist.write_text("""
        lsite = nr2lattice(nr_site, :)
""")

        # Apply modifications (backend-agnostic)
        apply_wasm_modifications(str(tmp_path))

        content = proclist.read_text()
        assert "! WASM:" in content
        assert "lsite(1) = nr2lattice(nr_site, 1)" in content


class TestWasmHelperFunctions:
    """Test helper functions and edge cases."""

    def test_apply_modifications_preserves_file_permissions(self, tmp_path):
        """Test that file permissions are preserved after modifications."""
        proclist = tmp_path / "proclist.f90"
        proclist.write_text("        lsite = nr2lattice(nr_site, :)")

        # Set specific permissions
        os.chmod(proclist, 0o644)
        original_mode = os.stat(proclist).st_mode

        apply_wasm_modifications(str(tmp_path))

        # Permissions should be preserved
        new_mode = os.stat(proclist).st_mode
        assert original_mode == new_mode

    def test_create_bindings_in_current_directory(self, tmp_path):
        """Test that bindings are created in current working directory."""
        # Change to tmp directory
        original_dir = os.getcwd()
        try:
            # Clean up any existing c_bindings.f90 from previous tests
            bindings_in_original = Path(original_dir) / "c_bindings.f90"
            if bindings_in_original.exists():
                bindings_in_original.unlink()

            os.chdir(tmp_path)

            create_c_bindings()

            # File should be in tmp_path
            assert (tmp_path / "c_bindings.f90").exists()

        finally:
            os.chdir(original_dir)


@pytest.mark.docker
class TestWasmDockerIntegration:
    """Test Docker-specific functionality."""

    @pytest.mark.slow
    def test_docker_image_availability(self):
        """Test that the flang-wasm Docker image can be pulled."""
        import subprocess

        try:
            result = subprocess.run(
                ["docker", "pull", "ghcr.io/r-wasm/flang-wasm:main"],
                capture_output=True,
                timeout=300,  # 5 minutes
            )
            assert result.returncode == 0, "Failed to pull flang-wasm image"
        except FileNotFoundError:
            pytest.skip("Docker not installed")
        except subprocess.TimeoutExpired:
            pytest.fail("Docker pull timed out")

    def test_docker_command_construction(self, tmp_path):
        """Test that Docker commands are constructed correctly."""
        # This is more of a smoke test to ensure build_wasm doesn't crash
        # when constructing Docker commands

        os.chdir(tmp_path)

        # Create minimal sources
        for filename in ["kind_values.f90", "base.f90", "lattice.f90", "proclist.f90"]:
            (tmp_path / filename).write_text("! minimal")

        # Mock subprocess to check command construction
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

            options = MagicMock()

            try:
                build_wasm(options)
            except Exception:
                pass  # We're just testing command construction

            # Check that subprocess.run was called with docker commands
            assert mock_run.called
            first_call_args = mock_run.call_args_list[0][0][0]
            assert first_call_args[0] == "docker"
            assert "ghcr.io/r-wasm/flang-wasm:main" in first_call_args


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
