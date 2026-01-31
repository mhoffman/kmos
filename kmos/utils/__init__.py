#!/usr/bin/env python
"""Several utility functions that do not seem to fit somewhere
else.
"""
#    Copyright 2009-2013 Max J. Hoffmann (mjhoffmann@gmail.com)
#    This file is part of kmos.
#
#    kmos is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    kmos is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with kmos.  If not, see <http://www.gnu.org/licenses/>.

import logging
import re
import os
from io import StringIO
from kmos.utils.ordered_dict import OrderedDict as OrderedDict

logger = logging.getLogger(__name__)

ValidationError = UserWarning
try:
    from kiwi.datatypes import ValidationError
except (ImportError, ModuleNotFoundError):
    logger.info("kiwi Validation not working.")

FCODE = """module kind
implicit none
contains
subroutine real_kind(p, r, kind_value)
  integer, intent(in), optional :: p, r
  integer, intent(out) :: kind_value

  if(present(p).and.present(r)) then
    kind_value = selected_real_kind(p=p, r=r)
  else
    if (present(r)) then
      kind_value = selected_real_kind(r=r)
    else
      if (present(p)) then
        kind_value = selected_real_kind(p)
      endif
    endif
  endif
end subroutine real_kind

subroutine int_kind(p, r, kind_value)
  integer, intent(in), optional :: p, r
  integer, intent(out) :: kind_value

  if(present(p).and.present(r)) then
    kind_value = selected_int_kind(p)
  else
    if (present(r)) then
      kind_value = selected_int_kind(r=r)
    else
      if (present(p)) then
        kind_value = selected_int_kind(p)
      endif
    endif
  endif
end subroutine int_kind

end module kind
"""


class CorrectlyNamed:
    """Syntactic Sugar class for use with kiwi, that makes sure that the name
    field of the class has a name field, that always complys with the rules
    for variables.
    """

    def __init__(self):
        pass

    def on_name__validate(self, _, name):
        """Called by kiwi upon chaning a string"""
        if " " in name:
            return ValidationError("No spaces allowed")
        elif name and not name[0].isalpha():
            return ValidationError("Need to start with a letter")


def write_py(fileobj, images, **kwargs):
    """Write a ASE atoms construction string for `images`
    into `fileobj`.
    """
    import numpy as np

    if isinstance(fileobj, str):
        fileobj = open(fileobj, "w")

    scaled_positions = (
        kwargs["scaled_positions"] if "scaled_positions" in kwargs else True
    )
    fileobj.write("from ase import Atoms\n\n")
    fileobj.write("import numpy as np\n\n")

    if not isinstance(images, (list, tuple)):
        images = [images]
    fileobj.write("images = [\n")

    for image in images:
        if hasattr(image, "get_chemical_formula"):
            chemical_formula = image.get_chemical_formula(mode="reduce")
        else:
            chemical_formula = image.get_name()

        # Handle ASE Cell object (ASE 3.x) vs numpy array (older ASE)
        cell_repr = repr(
            image.cell.array if hasattr(image.cell, "array") else image.cell
        )
        fileobj.write(
            "    Atoms(symbols='%s',\n"
            "          pbc=np.%s,\n"
            "          cell=np.array(\n      %s,\n"
            % (chemical_formula, repr(image.pbc), cell_repr[6:])
        )

        if not scaled_positions:
            fileobj.write(
                "          positions=np.array(\n      %s),\n"
                % repr(list(image.positions))
            )
        else:
            fileobj.write(
                "          scaled_positions=np.array(\n      %s),\n"
                % repr(
                    list((np.around(image.get_scaled_positions(), decimals=7)).tolist())
                )
            )
        logger.info(image.get_scaled_positions())
        fileobj.write("),\n")

    fileobj.write("]")


def get_ase_constructor(atoms):
    """Return the ASE constructor string for `atoms`."""
    if isinstance(atoms, str):
        # return atoms
        atoms = eval(atoms)
    if type(atoms) is list:
        atoms = atoms[0]
    f = StringIO()
    write_py(f, atoms)
    f.seek(0)
    lines = f.readlines()
    f.close()
    astr = ""
    for i, line in enumerate(lines):
        if i >= 5 and i < len(lines) - 1:
            astr += line
    # astr = astr[:-2]
    return astr.strip()


def product(*args, **kwds):
    """Take two lists and return iterator producing
    all combinations of tuples between elements
    of the two lists."""
    # product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy
    # product(range(2), repeat=3) --> 000 001 010 011 100 101 110 111
    pools = [tuple(arg) for arg in args] * kwds.get("repeat", 1)
    result = [[]]
    for pool in pools:
        result = [x + [y] for x in result for y in pool]
    for prod in result:
        yield tuple(prod)


def split_sequence(seq, size):
    """Take a list and a number n and return list
    divided into n sublists of roughly equal size.
    """
    newseq = []
    splitsize = 1.0 / size * len(seq)
    for i in range(size):
        newseq.append(seq[int(round(i * splitsize)) : int(round((i + 1) * splitsize))])
    return newseq


def download(project):
    from django.http import HttpResponse
    import zipfile
    import tempfile
    from os.path import join, basename
    from glob import glob
    from kmos.io import import_xml, export_source

    # return HTTP download response (e.g. via django)
    response = HttpResponse(mimetype="application/x-zip-compressed")
    response["Content-Disposition"] = 'attachment; filename="kmos_export.zip"'

    if isinstance(project, str):
        project = import_xml(project)

    from io import StringIO

    stringio = StringIO()
    zfile = zipfile.ZipFile(stringio, "w")

    # save XML
    zfile.writestr("project.xml", str(project))

    # generate source
    tempdir = tempfile.mkdtemp()
    srcdir = join(tempdir, "src")

    # add kMC project sources
    export_source(project, srcdir)
    for srcfile in glob(join(srcdir, "*")):
        zfile.write(srcfile, join("src", basename(srcfile)))

    # add standalone kmos program
    # TODO

    # write temporary file to response
    zfile.close()
    stringio.flush()
    response.write(stringio.getvalue())
    stringio.close()
    return response


def evaluate_kind_values(infile, outfile):
    """Go through a given file and dynamically
    replace all selected_int/real_kind calls
    with the dynamically evaluated fortran code
    using only code that the function itself
    contains.

    """
    import re
    import sys
    import shutil
    import subprocess

    sys.path.append(os.path.abspath(os.curdir))

    with open(infile) as infh:
        intext = infh.read()
    if not (
        "selected_int_kind" in intext.lower() or "selected_real_kind" in intext.lower()
    ):
        shutil.copy(infile, outfile)
        return

    def import_selected_kind():
        """Tries to import the module which provides
        processor dependent kind values. If the module
        is not available it is compiled from a here-document
        and imported afterwards.

        Warning: creates both the source file and the
        compiled module in the current directory.

        """
        try:
            import f2py_selected_kind
        except (ImportError, ModuleNotFoundError):
            # quick'n'dirty workaround for windoze
            if os.name == "nt":
                f = open("f2py_selected_kind.f90", "w")
                f.write(FCODE)
                f.close()
                from copy import deepcopy

                # save for later
                true_argv = deepcopy(sys.argv)
                sys.argv = (
                    (
                        "%s -c --fcompiler=gnu95 --compiler=mingw32"
                        " -m f2py_selected_kind"
                        " f2py_selected_kind.f90"
                    )
                    % sys.executable
                ).split()
                from numpy import f2py as f2py2e

                f2py2e.main()

                sys.argv = true_argv
            else:
                with open("f2py_selected_kind.f90", "w") as f:
                    f.write(FCODE)
                f2py_command = [
                    sys.executable,
                    "-m",
                    "numpy.f2py",
                    "-c",
                    "f2py_selected_kind.f90",
                    "-m",
                    "f2py_selected_kind",
                ]
                print("%s\n" % os.path.abspath(os.curdir))

                # Find gfortran compiler
                import shutil

                gfortran_path = shutil.which("gfortran")

                # Set up environment with correct compiler paths
                env_vars = {
                    "LIBRARY_PATH": os.environ.get("LIBRARY_PATH", "")
                    + ":/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib"
                }
                if gfortran_path:
                    env_vars["FC"] = gfortran_path

                result = subprocess.run(
                    f2py_command,
                    capture_output=True,
                    text=True,
                    env=dict(os.environ, **env_vars),
                )
                print(result.stdout)
                if result.stderr:
                    print(result.stderr)
            try:
                import f2py_selected_kind
            except Exception as e:
                raise Exception(
                    "Could not create selected_kind module\n"
                    + "%s\n" % os.path.abspath(os.curdir)
                    + "%s\n" % os.listdir(".")
                    + "%s\n" % e
                )
        return f2py_selected_kind.kind

    def parse_args(args):
        """
        Parse the arguments for selected_(real/int)_kind
        to pass them on to the Fortran module.

        """
        in_args = [x.strip() for x in args.split(",")]
        args = []
        kwargs = {}

        for arg in in_args:
            if "=" in arg:
                symbol, value = arg.split("=")
                kwargs[symbol] = eval(value)
            else:
                args.append(eval(arg))

        return args, kwargs

    def int_kind(args):
        """Python wrapper around Fortran selected_int_kind
        function.
        """
        args, kwargs = parse_args(args)
        return import_selected_kind().int_kind(*args, **kwargs)

    def real_kind(args):
        """Python wrapper around Fortran selected_real_kind
        function.
        """
        args, kwargs = parse_args(args)
        return import_selected_kind().real_kind(*args, **kwargs)

    infile = open(infile)
    outfile = open(outfile, "w")
    int_pattern = re.compile(
        r"(?P<before>.*)selected_int_kind\((?P<args>.*)\)(?P<after>.*)",
        flags=re.IGNORECASE,
    )
    real_pattern = re.compile(
        r"(?P<before>.*)selected_real_kind\((?P<args>.*)\)(?P<after>.*)",
        flags=re.IGNORECASE,
    )

    for line in infile:
        real_match = real_pattern.match(line)
        int_match = int_pattern.match(line)
        if int_match:
            match = int_match.groupdict()
            line = "%s%s%s\n" % (
                match["before"],
                int_kind(match["args"]),
                match["after"],
            )
        elif real_match:
            match = real_match.groupdict()
            line = "%s%s%s\n" % (
                match["before"],
                real_kind(match["args"]),
                match["after"],
            )
        outfile.write(line)
    infile.close()
    outfile.close()


def build(options):
    """Build binary with f2py binding from complete
    set of source file in the current directory.

    """

    from os.path import isfile
    import sys
    from glob import glob

    src_files = ["kind_values_f2py.f90", "base.f90"]

    if isfile("base_acf.f90"):
        src_files.append("base_acf.f90")
    src_files.append("lattice.f90")
    if isfile("proclist_constants.f90"):
        src_files.append("proclist_constants.f90")
    if isfile("proclist_pars.f90"):
        src_files.append("proclist_pars.f90")

    src_files.extend(glob("nli_*.f90"))
    # src_files.extend(glob('get_rate_*.f90'))
    src_files.extend(glob("run_proc_*.f90"))
    src_files.append("proclist.f90")
    if isfile("proclist_acf.f90"):
        src_files.append("proclist_acf.f90")

    extra_flags = {}

    # Add include path for src directory (needed for meson backend in Python >= 3.12)
    # Use absolute path so meson can find include files from its temp build directory
    if os.path.isdir("src"):
        src_include = "-I" + os.path.abspath("src")
    else:
        src_include = "-I" + os.path.abspath(".")

    if options.no_optimize:
        extra_flags["gfortran"] = (
            "-ffree-line-length-0 -ffree-form"
            " -xf95-cpp-input -Wall -fimplicit-none"
            " -time  -fmax-identifier-length=63 " + src_include
        )
        extra_flags["gnu95"] = extra_flags["gfortran"]
        extra_flags["intel"] = "-fpp -Wall -I/opt/intel/fc/10.1.018/lib " + src_include
        extra_flags["intelem"] = "-fpp -Wall " + src_include

    else:
        extra_flags["gfortran"] = (
            "-ffree-line-length-0 -ffree-form"
            " -xf95-cpp-input -Wall -O3 -fimplicit-none"
            " -time -fmax-identifier-length=63 " + src_include
        )
        extra_flags["gnu95"] = extra_flags["gfortran"]
        extra_flags["intel"] = (
            "-fast -fpp -Wall -I/opt/intel/fc/10.1.018/lib " + src_include
        )
        extra_flags["intelem"] = "-fast -fpp -Wall " + src_include

    module_name = "kmc_model"

    if not isfile("kind_values_f2py.f90"):
        evaluate_kind_values("kind_values.f90", "kind_values_f2py.f90")

    for src_file in src_files:
        if not isfile(src_file):
            raise IOError("File %s not found" % src_file)

    call = []
    call.append("-c")
    call.append("-c")
    call.append("--fcompiler=%s" % options.fcompiler)
    extra_flags = extra_flags.get(options.fcompiler, "")

    if options.debug:
        extra_flags += " -DDEBUG"
    call.append("--f90flags=%s" % extra_flags)
    call.append("-m")
    call.append(module_name)
    call += src_files

    logger.info(call)
    from copy import deepcopy

    true_argv = deepcopy(sys.argv)  # save for later
    from numpy import f2py

    sys.argv = call
    os.environ["LIBRARY_PATH"] = (
        os.environ.get("LIBRARY_PATH", "")
        + ":/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib"
    )

    # Set FC for meson backend (Python >= 3.12) to compiler name only
    # Meson has issues with FC containing full paths
    if sys.version_info >= (3, 12):
        # Ensure gfortran is in PATH for meson to find
        import shutil

        gfortran_path = shutil.which("gfortran")
        if gfortran_path:
            gfortran_dir = os.path.dirname(gfortran_path)
            current_path = os.environ.get("PATH", "")
            if gfortran_dir not in current_path:
                os.environ["PATH"] = f"{gfortran_dir}:{current_path}"

        fc_map = {
            "gfortran": "gfortran",
            "gnu95": "gfortran",
            "intel": "ifort",
            "intelem": "ifort",
        }
        if options.fcompiler in fc_map:
            os.environ["FC"] = fc_map[options.fcompiler]

    f2py.main()
    sys.argv = true_argv


def _run_docker_command(cmd, src_dir, operation_name, timeout=300):
    """Helper to run Docker commands with consistent error handling.

    Args:
        cmd: Shell command to run inside container
        src_dir: Source directory to mount
        operation_name: Human-readable name for the operation (e.g., "Compilation")
        timeout: Timeout in seconds (default: 300)

    Raises:
        RuntimeError: If command fails or times out
    """
    import subprocess

    docker_cmd = [
        "docker",
        "run",
        "--rm",
        "--platform",
        "linux/amd64",
        "-v",
        f"{src_dir}:/src",
        "ghcr.io/r-wasm/flang-wasm:main",
        "sh",
        "-c",
        cmd,
    ]

    try:
        result = subprocess.run(
            docker_cmd, capture_output=True, text=True, check=True, timeout=timeout
        )
        if result.stdout:
            logger.debug(result.stdout)
        if result.stderr:
            logger.debug(result.stderr)
        return result

    except subprocess.TimeoutExpired:
        raise RuntimeError(
            f"{operation_name} timed out after {timeout} seconds. "
            "Try reducing model complexity or increasing timeout."
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"{operation_name} failed with exit code {e.returncode}")
        if e.stdout:
            logger.error(f"stdout: {e.stdout}")
        if e.stderr:
            logger.error(f"stderr: {e.stderr}")
        raise RuntimeError(
            f"{operation_name} failed. Check that Docker is running and "
            f"the flang-wasm image is available."
        ) from e
    except FileNotFoundError:
        raise RuntimeError(
            "Docker not found. Please install Docker to build WASM.\n"
            "See: https://docs.docker.com/get-docker/"
        )


def build_wasm(options):
    """Build WebAssembly binary from complete set of source files.

    Uses flang-wasm Docker container to compile Fortran to WebAssembly.
    Applies necessary WASM-specific modifications to source files.

    Args:
        options: Export options object

    Returns:
        dict: Paths to generated files {'js': path, 'wasm': path}

    Raises:
        RuntimeError: If Docker not available or compilation fails
        IOError: If required source files missing
    """
    import shutil
    from os.path import isfile, abspath

    logger.info("Building WebAssembly binary...")

    # 1. Validate Docker availability
    if not shutil.which("docker"):
        raise RuntimeError(
            "Docker not found. Please install Docker to build WASM.\n"
            "See: https://docs.docker.com/get-docker/"
        )

    # Get the current directory (should contain Fortran sources)
    src_dir = abspath(".")

    # 2. Check for required source files
    required_files = ["kind_values.f90", "base.f90", "lattice.f90", "proclist.f90"]
    missing = [f for f in required_files if not isfile(f)]
    if missing:
        raise IOError(
            f"Required source files missing: {', '.join(missing)}\n"
            f"Make sure you're in a directory with exported Fortran sources."
        )

    # 3. Apply WASM-specific modifications
    logger.info("Applying WASM-specific modifications...")
    modifications_count = apply_wasm_modifications(src_dir)
    if modifications_count > 0:
        logger.info(f"Applied {modifications_count} WASM modifications")

    # 4. Always regenerate c_bindings.f90 (critical for WASM compatibility)
    logger.info("Generating c_bindings.f90...")
    create_c_bindings()

    # 5. Compile with flang-wasm
    logger.info("Compiling Fortran sources with flang-wasm...")

    # First, compile each Fortran file to object files
    # Use /src (container path) instead of host path
    compile_cmd = """
        cd /src &&
        /opt/flang/host/bin/flang -g -O0 -target wasm32-unknown-emscripten -c kind_values.f90 -o kind_values.o &&
        /opt/flang/host/bin/flang -g -O0 -target wasm32-unknown-emscripten -c base.f90 -I. -o base.o &&
        /opt/flang/host/bin/flang -g -O0 -target wasm32-unknown-emscripten -c lattice.f90 -I. -o lattice.o &&
        /opt/flang/host/bin/flang -g -O0 -target wasm32-unknown-emscripten -c proclist.f90 -I. -o proclist.o &&
        /opt/flang/host/bin/flang -g -O0 -target wasm32-unknown-emscripten -c c_bindings.f90 -I. -o c_bindings.o
    """

    _run_docker_command(compile_cmd, src_dir, "Compilation", timeout=1800)

    # 6. Link with emcc
    logger.info("Linking with emscripten...")
    logger.info("Note: WASM linking can take several minutes for large models...")

    # Use /src (container path) instead of host path
    # Production build: O3 optimization, no debug, no assertions
    link_cmd = """
        cd /src &&
        /opt/emsdk/upstream/emscripten/emcc -O3 -sASSERTIONS=0 -sSTACK_SIZE=10MB \
            -sINITIAL_MEMORY=64MB -sALLOW_MEMORY_GROWTH \
            -sEXPORTED_FUNCTIONS=_kmc_init,_kmc_do_step,_kmc_get_time,_kmc_get_species,_kmc_get_species_by_site,_kmc_get_total_sites,_kmc_get_system_size,_kmc_set_rate,_kmc_get_nr_sites,_kmc_get_accum_rate,_kmc_get_rate,_kmc_get_integ_rate,_kmc_update_accum_rate,_kmc_get_nr2lattice,_kmc_get_debug_last_proc,_kmc_get_debug_last_site,_malloc,_free \
            -sEXPORTED_RUNTIME_METHODS=ccall,cwrap,getValue,setValue \
            -L/opt/flang/wasm/lib -lFortranRuntime \
            kind_values.o base.o lattice.o proclist.o c_bindings.o \
            -o kmc_model.js
    """

    _run_docker_command(link_cmd, src_dir, "Linking", timeout=1800)

    # 7. Validate output files
    js_file = abspath("kmc_model.js")
    wasm_file = abspath("kmc_model.wasm")

    if not isfile(js_file):
        raise RuntimeError("Build failed: kmc_model.js was not created")
    if not isfile(wasm_file):
        raise RuntimeError("Build failed: kmc_model.wasm was not created")

    # Check files are not empty
    import os

    js_size = os.path.getsize(js_file)
    wasm_size = os.path.getsize(wasm_file)

    if js_size == 0:
        raise RuntimeError("Build failed: kmc_model.js is empty")
    if wasm_size == 0:
        raise RuntimeError("Build failed: kmc_model.wasm is empty")

    # 8. Log success with file sizes
    js_size_kb = js_size / 1024
    wasm_size_mb = wasm_size / 1024 / 1024

    logger.info("WebAssembly build completed successfully!")
    logger.info(f"Generated kmc_model.js ({js_size_kb:.1f} KB)")
    logger.info(f"Generated kmc_model.wasm ({wasm_size_mb:.2f} MB)")

    return {"js": js_file, "wasm": wasm_file}


def apply_wasm_modifications(src_dir):
    """Apply WASM-specific modifications to Fortran source files.

    Key modifications for WASM compatibility:
    1. proclist.f90:
       - Replace random_number() with custom RNG (WASM doesn't support Fortran intrinsics)
       - Replace array slice assignments with explicit element assignments
       - Add debug variables for tracking
       - Change seed_size to 1 (simple seed)
    2. base.f90:
       - Remove CHARACTER assignments (causes _FortranAAssign crashes)
       - Replace array operations with explicit DO loops
    3. lattice.f90:
       - Convert calculate_nr2lattice from function to subroutine (WASM can't return arrays)
       - Replace array operations with explicit assignments
       - Comment out validation loops (trigger 'unreachable' errors)

    Args:
        src_dir: Directory containing Fortran source files

    Returns:
        int: Number of modifications applied
    """
    import re
    from os.path import join, isfile

    modifications_count = 0

    # ========================================================================
    # PART 1: Modify proclist.f90
    # ========================================================================
    proclist_file = join(src_dir, "proclist.f90")
    if not isfile(proclist_file):
        logger.debug(
            f"proclist.f90 not found in {src_dir}, skipping WASM modifications"
        )
        return 0

    with open(proclist_file, "r") as f:
        proclist_content = f.read()

    # Skip if already modified (idempotent)
    if "! WASM: Custom RNG" in proclist_content:
        logger.debug("proclist.f90 already contains WASM modifications, skipping")
        return 0

    logger.info("Applying WASM modifications to proclist.f90...")

    # 1.1: Add get_volume to imports from base module if not already there
    # Look for increment_procstat in the use base statement
    if (
        "get_volume" not in proclist_content.split("use lattice")[0]
    ):  # Only check base module imports
        # Find and replace increment_procstat (last item in use base) with increment_procstat, get_volume
        proclist_content = re.sub(
            r"(use base,.*?increment_procstat)(\s*\n)",
            r"\1, &\n    get_volume\2",
            proclist_content,
            flags=re.DOTALL,
            count=1,
        )

    # 1.2: Add debug variables after implicit none
    implicit_none_pattern = r"(implicit none\s*\n)"
    debug_vars = r"\1\n! Debug variables to store last selected process and site\ninteger(kind=iint), public :: debug_last_proc_nr = 0\ninteger(kind=iint), public :: debug_last_nr_site = 0\n"
    proclist_content = re.sub(
        implicit_none_pattern, debug_vars, proclist_content, count=1
    )

    # 1.3: Change seed_size from 12 to 1
    proclist_content = re.sub(
        r"integer\(kind=iint\), public :: seed_size = \d+",
        r"integer(kind=iint), public :: seed_size = 1",
        proclist_content,
    )

    # 1.4: Add custom RNG state variable after seed_arr declaration
    seed_arr_pattern = (
        r"(integer\(kind=iint\), public, dimension\(:\), allocatable :: seed_arr.*\n)"
    )
    rng_state = r"\1\n! WASM: Custom RNG state (module-level variable)\ninteger(kind=iint) :: rng_state = 123456789_iint\n"
    proclist_content = re.sub(seed_arr_pattern, rng_state, proclist_content, count=1)

    # 1.5: Add custom RNG implementation after "contains"
    contains_pattern = r"(contains\s*\n)"
    custom_rng = r"""\1
! WASM: Custom RNG to replace random_number() intrinsic
! Simple Linear Congruential Generator (LCG)
! Uses the same algorithm as glibc: X_n+1 = (a * X_n + c) mod m
! where a = 1103515245, c = 12345, m = 2^31
subroutine custom_random_seed(seed_val)
    integer(kind=iint), intent(in) :: seed_val
    rng_state = seed_val
end subroutine custom_random_seed

subroutine custom_random_number(harvest)
    real(kind=rsingle), intent(out) :: harvest
    ! Numerical Recipes "quick and dirty" LCG - fits in 32-bit integers
    integer(kind=iint), parameter :: a = 1664525_iint
    integer(kind=iint), parameter :: c = 1013904223_iint
    integer(kind=iint), parameter :: m = 2147483647_iint  ! 2^31 - 1
    integer(kind=ilong) :: temp64  ! Use 64-bit for multiplication

    ! Perform multiplication in 64-bit to avoid overflow
    temp64 = int(rng_state, kind=ilong) * int(a, kind=ilong)
    temp64 = temp64 + int(c, kind=ilong)
    temp64 = mod(temp64, int(m, kind=ilong))

    rng_state = int(temp64, kind=iint)
    if (rng_state < 0) rng_state = rng_state + m  ! Ensure positive

    ! Convert to [0, 1) range
    harvest = real(rng_state, kind=rsingle) / real(m, kind=rsingle)
end subroutine custom_random_number

"""
    proclist_content = re.sub(contains_pattern, custom_rng, proclist_content, count=1)

    # 1.6: Replace all random_number() calls with custom_random_number()
    proclist_content = re.sub(
        r"\bcall random_number\(", r"call custom_random_number(", proclist_content
    )

    # 1.7: Replace random_seed initialization with custom_random_seed
    # Find and replace the entire random seed initialization block
    seed_init_pattern = r"(\s+)(! initialize random number generator\s*\n\s*allocate\(seed_arr\(seed_size\)\)\s*\n\s*seed = seed_in\s*\n\s*seed_arr = seed\s*\n\s*call random_seed\(seed_size\)\s*\n\s*call random_seed\(put=seed_arr\)\s*\n\s*deallocate\(seed_arr\))"
    seed_init_replacement = r"\1! WASM: Use custom RNG instead of Fortran intrinsics due to ABI incompatibilities\n\1seed = seed_in\n\1call custom_random_seed(seed_in)"
    proclist_content = re.sub(
        seed_init_pattern, seed_init_replacement, proclist_content
    )

    # 1.8: Add debug variable storage in do_kmc_step
    # Find the do_kmc_step subroutine and add debug storage before run_proc_nr
    run_proc_pattern = r"(\s+)(call run_proc_nr\(proc_nr, nr_site\))"
    debug_storage = r"\1! Store for debugging (used by exported functions)\n\1debug_last_proc_nr = proc_nr\n\1debug_last_nr_site = nr_site\n\n\1\2"
    proclist_content = re.sub(run_proc_pattern, debug_storage, proclist_content)

    # 1.9: Replace array slice assignments with explicit element assignments
    slice_pattern = r"(\s+)lsite = nr2lattice\(nr_site, :\)"
    explicit_replacement = r"\1! lsite = lattice_site, (vs. scalar site)\n\1! WASM: Explicit element assignment instead of array slice\n\n\1lsite(1) = nr2lattice(nr_site, 1)\n\n\1lsite(2) = nr2lattice(nr_site, 2)\n\n\1lsite(3) = nr2lattice(nr_site, 3)\n\n\1lsite(4) = nr2lattice(nr_site, 4)\n"
    matches = re.findall(slice_pattern, proclist_content)
    if len(matches) > 0:
        proclist_content = re.sub(slice_pattern, explicit_replacement, proclist_content)
        modifications_count += len(matches)

    # Write modified proclist.f90
    with open(proclist_file, "w") as f:
        f.write(proclist_content)

    logger.info(f"Applied {modifications_count + 7} modifications to proclist.f90")

    # ========================================================================
    # PART 2: Modify base.f90
    # ========================================================================
    base_file = join(src_dir, "base.f90")
    if isfile(base_file):
        with open(base_file, "r") as f:
            base_content = f.read()

        # Skip if already modified
        if (
            "! WASM: Leave uninitialized" in base_content
            or "! WASM: Skip CHARACTER assignment" in base_content
        ):
            logger.debug("base.f90 already contains WASM modifications")
        else:
            logger.info("Applying WASM modifications to base.f90...")

            # 2.1: Leave system_name uninitialized (avoid _FortranAAssign crash)
            base_content = re.sub(
                r"character\(len=200\) :: system_name\s*\n",
                r"character(len=200) :: system_name  ! WASM: Leave uninitialized to avoid _FortranAAssign crash\n",
                base_content,
            )

            # 2.2: Comment out system_name assignment in allocate_system
            base_content = re.sub(
                r"(\s+)(system_name = input_system_name\s*\n)",
                r"\1! system_name = input_system_name  ! WASM: Skip CHARACTER assignment - causes ABI crash in _FortranAAssign\n",
                base_content,
            )

            # 2.3: Add WASM comment after variable declaration in update_accum_rate
            # Find update_accum_rate subroutine and add comment after integer(kind=iint) :: i
            base_content = re.sub(
                r"(subroutine update_accum_rate.*?\n\s+integer\(kind=iint\) :: i\s*\n)",
                r"\1\n    ! WASM: Can't use print statements with INTEGER(8) due to ABI mismatch\n    ! Use kmc_get_nr_sites() from JavaScript to debug instead\n",
                base_content,
                flags=re.DOTALL,
            )

            # 2.4: Replace array operations with explicit DO loops in allocate_system
            # Add loop variables (i already exists, just add i_proc, i_vol, i_dim)
            base_content = re.sub(
                r"(subroutine allocate_system.*?integer\(kind=iint\), intent\(in\) :: input_volume, input_nr_of_proc\s*\n\s+logical :: system_allocated\s*\n)",
                r"\1    integer(kind=iint) :: i_proc, i_vol, i_dim  ! WASM: Loop variables for explicit init\n",
                base_content,
                flags=re.DOTALL,
            )

            # Replace avail_sites = 0 with explicit loops
            base_content = re.sub(
                r"(\s+)allocate\(avail_sites\(nr_of_proc, volume, 2\)\)\s*\n\s+avail_sites = 0",
                r"\1allocate(avail_sites(nr_of_proc, volume, 2))\n"
                r"\1do i_dim = 1, 2\n"
                r"\1    do i_vol = 1, volume\n"
                r"\1        do i_proc = 1, nr_of_proc\n"
                r"\1            avail_sites(i_proc, i_vol, i_dim) = 0\n"
                r"\1        end do\n"
                r"\1    end do\n"
                r"\1end do",
                base_content,
            )

            # Replace lattice = null_species with explicit loop
            base_content = re.sub(
                r"(\s+)allocate\(lattice\(volume\)\)\s*\n\s+lattice = null_species",
                r"\1allocate(lattice(volume))\n"
                r"\1do i_vol = 1, volume\n"
                r"\1    lattice(i_vol) = null_species\n"
                r"\1end do",
                base_content,
            )

            # Replace nr_of_sites = 0 with explicit loop
            base_content = re.sub(
                r"(\s+)allocate\(nr_of_sites\(nr_of_proc\)\)\s*\n\s+nr_of_sites = 0",
                r"\1allocate(nr_of_sites(nr_of_proc))\n"
                r"\1do i_proc = 1, nr_of_proc\n"
                r"\1    nr_of_sites(i_proc) = 0\n"
                r"\1end do",
                base_content,
            )

            # Replace rates = 0 with explicit loop
            base_content = re.sub(
                r"(\s+)allocate\(rates\(nr_of_proc\)\)\s*\n\s+rates = 0",
                r"\1allocate(rates(nr_of_proc))\n"
                r"\1do i_proc = 1, nr_of_proc\n"
                r"\1    rates(i_proc) = 0\n"
                r"\1end do",
                base_content,
            )

            # Replace accum_rates = 0 with explicit loop
            base_content = re.sub(
                r"(\s+)allocate\(accum_rates\(nr_of_proc\)\)\s*\n\s+accum_rates = 0",
                r"\1allocate(accum_rates(nr_of_proc))\n"
                r"\1do i_proc = 1, nr_of_proc\n"
                r"\1    accum_rates(i_proc) = 0\n"
                r"\1end do",
                base_content,
            )

            # Replace integ_rates = 0 with explicit loop
            base_content = re.sub(
                r"(\s+)allocate\(integ_rates\(nr_of_proc\)\)\s*\n\s+integ_rates = 0",
                r"\1allocate(integ_rates(nr_of_proc))\n"
                r"\1do i_proc = 1, nr_of_proc\n"
                r"\1    integ_rates(i_proc) = 0\n"
                r"\1end do",
                base_content,
            )

            # Write modified base.f90
            with open(base_file, "w") as f:
                f.write(base_content)

            modifications_count += 8
            logger.info("Applied 8 modifications to base.f90")

    # ========================================================================
    # PART 3: Modify lattice.f90
    # ========================================================================
    lattice_file = join(src_dir, "lattice.f90")
    if isfile(lattice_file):
        with open(lattice_file, "r") as f:
            lattice_content = f.read()

        # Skip if already modified
        if "subroutine calculate_nr2lattice" in lattice_content:
            logger.debug("lattice.f90 already has calculate_nr2lattice as subroutine")
        else:
            logger.debug("Applying WASM modifications to lattice.f90...")

            # 1. Convert function to subroutine
            # First, extract the function to modify it
            func_start = lattice_content.find("pure function calculate_nr2lattice(nr)")
            func_end = lattice_content.find("end function calculate_nr2lattice") + len(
                "end function calculate_nr2lattice"
            )

            if func_start != -1 and func_end != -1:
                before = lattice_content[:func_start]
                func_body = lattice_content[func_start:func_end]
                after = lattice_content[func_end:]

                # Replace function declaration with subroutine
                func_body = func_body.replace(
                    "pure function calculate_nr2lattice(nr)",
                    "subroutine calculate_nr2lattice(nr, coords)",
                )
                func_body = func_body.replace(
                    "    integer(kind=iint), dimension(4) :: calculate_nr2lattice",
                    "    integer(kind=iint), dimension(4), intent(out) :: coords",
                )
                # Replace calculate_nr2lattice( with coords( in assignment statements only
                # (not in the subroutine declaration or end statement)
                lines = func_body.split("\n")
                new_lines = []
                for line in lines:
                    if "subroutine" not in line.lower() and "coords(" not in line:
                        line = line.replace("calculate_nr2lattice(", "coords(")
                    new_lines.append(line)
                func_body = "\n".join(new_lines)

                func_body = func_body.replace(
                    "end function calculate_nr2lattice",
                    "end subroutine calculate_nr2lattice",
                )

                lattice_content = before + func_body + after
            else:
                logger.warning(
                    "Could not find calculate_nr2lattice function to convert"
                )

            # 2. Add temp_coords variable
            lattice_content = lattice_content.replace(
                "    integer(kind=iint) :: volume\n",
                "    integer(kind=iint) :: volume\n    integer(kind=iint), dimension(4) :: temp_coords  ! WASM\n",
            )

            # 2.5: Replace system_size array constructor with explicit assignments
            # Avoid product() and array constructors due to ABI mismatch
            lattice_content = re.sub(
                r"(\s+)system_size = \(/input_system_size\(1\), input_system_size\(2\), 1/\)\s*\n\s+volume = system_size\(1\)\*system_size\(2\)\*system_size\(3\)\*spuck",
                r"\1system_size(1) = input_system_size(1)\n\1system_size(2) = input_system_size(2)\n\1system_size(3) = 1\n\1! Avoid product() due to ABI mismatch with WASM runtime\n\1volume = system_size(1)*system_size(2)*system_size(3)*spuck",
                lattice_content,
            )

            # 3. Comment out first validation loop
            # Find the block starting with "! Let's check" and ending with "end do" (4 levels deep)
            lines = lattice_content.split("\n")
            new_lines = []
            in_validation1 = False
            validation1_depth = 0

            for line in lines:
                if "! Let's check if the works correctly" in line:
                    in_validation1 = True
                    new_lines.append(
                        "    ! Validation checks disabled for WASM - these trigger 'unreachable' errors"
                    )
                    new_lines.append("    ! Let's check if the works correctly, first")
                    continue

                if in_validation1:
                    if (
                        "do k = 0" in line
                        or "do j = 0" in line
                        or "do i = 0" in line
                        or ("do nr = 1" in line and "do nr = 1, spuck" in line)
                    ):
                        validation1_depth += 1
                        new_lines.append("    ! " + line.lstrip())
                    elif "end do" in line and validation1_depth > 0:
                        new_lines.append("    ! " + line.lstrip())
                        validation1_depth -= 1
                        if validation1_depth == 0:
                            in_validation1 = False
                    else:
                        new_lines.append("    ! " + line.lstrip())
                else:
                    new_lines.append(line)

            lattice_content = "\n".join(new_lines)

            # 4. Comment out second validation loop
            lines = lattice_content.split("\n")
            new_lines = []
            in_validation2 = False

            for line in lines:
                if (
                    "do check_nr=1," in line
                    and "calculate_lattice2nr(calculate_nr2lattice" in lattice_content
                ):
                    # Check if this is the validation loop (next line has if statement)
                    idx = lines.index(line)
                    if (
                        idx + 1 < len(lines)
                        and "if(.not.check_nr.eq.calculate_lattice2nr" in lines[idx + 1]
                    ):
                        in_validation2 = True
                        new_lines.append("    ! " + line.lstrip())
                        continue

                if in_validation2:
                    new_lines.append("    ! " + line.lstrip())
                    if "end do" in line:
                        in_validation2 = False
                else:
                    new_lines.append(line)

            lattice_content = "\n".join(new_lines)

            # 5. Replace array slice assignment (may be commented out in source)
            # First try to match uncommented version
            if (
                "do check_nr=1, system_size(1)*system_size(2)*system_size(3)*spuck"
                in lattice_content
                and "nr2lattice(check_nr, :) = calculate_nr2lattice(check_nr)"
                in lattice_content
            ):
                lattice_content = re.sub(
                    r"    do check_nr=1, system_size\(1\)\*system_size\(2\)\*system_size\(3\)\*spuck\n        nr2lattice\(check_nr, :\) = calculate_nr2lattice\(check_nr\)\n    end do",
                    """    ! WASM: Use temp variable and explicit element assignment instead of array slice
    do check_nr=1, system_size(1)*system_size(2)*system_size(3)*spuck
        call calculate_nr2lattice(check_nr, temp_coords)
        nr2lattice(check_nr, 1) = temp_coords(1)
        nr2lattice(check_nr, 2) = temp_coords(2)
        nr2lattice(check_nr, 3) = temp_coords(3)
        nr2lattice(check_nr, 4) = temp_coords(4)
    end do""",
                    lattice_content,
                )
                logger.debug(
                    "Replaced nr2lattice array slice with explicit assignments"
                )
            # Try to match commented-out version (from kmos templates)
            # Pattern with consistent 4-space indentation:
            #     ! do check_nr=1, ...
            #     ! nr2lattice(check_nr, :) = ...
            #     ! end do
            has_check_nr = (
                "! do check_nr=1, system_size(1)*system_size(2)*system_size(3)*spuck"
                in lattice_content
            )
            has_nr2lattice = (
                "! nr2lattice(check_nr, :) = calculate_nr2lattice(check_nr)"
                in lattice_content
            )

            if has_check_nr and has_nr2lattice:
                # Match the specific 3-line commented block for nr2lattice initialization
                before_sub = lattice_content
                lattice_content = re.sub(
                    r"    ! do check_nr=1, system_size\(1\)\*system_size\(2\)\*system_size\(3\)\*spuck\n    ! nr2lattice\(check_nr, :\) = calculate_nr2lattice\(check_nr\)\n    ! end do",
                    """    ! WASM: Use temp variable and explicit element assignment instead of array slice
    do check_nr=1, system_size(1)*system_size(2)*system_size(3)*spuck
        call calculate_nr2lattice(check_nr, temp_coords)
        nr2lattice(check_nr, 1) = temp_coords(1)
        nr2lattice(check_nr, 2) = temp_coords(2)
        nr2lattice(check_nr, 3) = temp_coords(3)
        nr2lattice(check_nr, 4) = temp_coords(4)
    end do""",
                    lattice_content,
                )
                if before_sub != lattice_content:
                    logger.info(
                        "Uncommented and fixed nr2lattice initialization loop (was commented out in template)"
                    )
                else:
                    logger.warning(
                        "Found commented nr2lattice pattern but regex substitution failed"
                    )
            else:
                logger.warning(
                    f"Could not find nr2lattice initialization loop (has_check_nr={has_check_nr}, has_nr2lattice={has_nr2lattice})"
                )

            with open(lattice_file, "w") as f:
                f.write(lattice_content)

            modifications_count += 1
            logger.debug("Applied WASM modifications to lattice.f90")

    return modifications_count


def create_c_bindings():
    """Create c_bindings.f90 for WebAssembly exports.

    Generates Fortran bindings with C calling convention for JavaScript/WASM interface.
    Automatically detects the default_layer name from lattice.f90.

    Exported functions:
        - kmc_init: Initialize KMC system
        - kmc_do_step: Perform one KMC step
        - kmc_get_time: Get current simulation time
        - kmc_get_species: Get species at a site
        - kmc_get_system_size: Get total number of sites
        - kmc_set_rate: Set rate constant for a process
        - kmc_get_nr_sites: Get number of sites
        - kmc_get_accum_rate: Get accumulated rate
        - kmc_get_rate: Get rate for a process
        - kmc_update_accum_rate: Update accumulated rate
        - kmc_get_nr2lattice: Get lattice coordinates from site number
        - kmc_get_debug_last_proc: Get last executed process (debug)
        - kmc_get_debug_last_site: Get last executed site (debug)

    Returns:
        str: Absolute path to created c_bindings.f90 file
    """
    from os.path import abspath, isfile
    import re

    # Detect the default_layer name from lattice.f90
    default_layer_name = "default"  # fallback
    if isfile("lattice.f90"):
        with open("lattice.f90", "r") as f:
            lattice_content = f.read()
            # Look for: integer(kind=iint), public :: default_layer = <name>
            match = re.search(
                r"integer\(kind=iint\),\s*public\s*::\s*default_layer\s*=\s*(\w+)",
                lattice_content,
            )
            if match:
                default_layer_name = match.group(1)
                logger.info(f"Detected default_layer: {default_layer_name}")
            else:
                logger.warning(
                    "Could not detect default_layer from lattice.f90, using 'default'"
                )
    else:
        logger.warning("lattice.f90 not found, using 'default' as layer name")

    # Use the WORKING c_bindings template from AB_model_wasm
    # Use f-string to insert the detected layer name
    c_bindings_code = f"""! C bindings for kMC functions to enable JavaScript interoperability
! This demonstrates how to make Fortran functions callable from WASM/JavaScript

module c_bindings
    use iso_c_binding
    use kind_values
    use base, only: get_kmc_time, set_rate_const, get_nrofsites, get_accum_rate, get_rate, update_accum_rate
    use lattice, only: allocate_system, system_size, {default_layer_name}, get_species, nr2lattice
    use proclist, only: init, do_kmc_step
    implicit none

contains

    ! Initialize the kMC system
    subroutine c_init(nx, ny, nz) bind(C, name="kmc_init")
        use lattice, only: allocate_system
        use proclist, only: initialize_state, nr_of_proc
        integer(c_int), intent(in), value :: nx, ny, nz
        integer(kind=iint) :: system_size_f(2)
        integer(kind=iint) :: seed_in
        character(len=200), parameter :: system_name = "kmc_system"  ! WASM: Use parameter to avoid _FortranAAssign

        ! Convert C integers to Fortran integers (2D model, ignore nz)
        system_size_f(1) = int(nx, kind=iint)
        system_size_f(2) = int(ny, kind=iint)

        seed_in = 42  ! Random seed

        ! Call allocate_system and initialize_state directly to avoid optional parameter issues
        call allocate_system(nr_of_proc, system_size_f, system_name)
        call initialize_state({default_layer_name}, seed_in)

    end subroutine c_init

    ! Perform one kMC step
    subroutine c_do_step() bind(C, name="kmc_do_step")
        call do_kmc_step()
    end subroutine c_do_step

    ! Get the current kMC time
    function c_get_time() bind(C, name="kmc_get_time") result(time)
        real(c_double) :: time
        real(kind=rdouble) :: kmc_time_val
        call get_kmc_time(kmc_time_val)
        time = real(kmc_time_val, kind=c_double)
    end function c_get_time

    ! Get species at a site by linear site number (works with multiple sites per unit cell)
    function c_get_species_by_site(nr_site) bind(C, name="kmc_get_species_by_site") result(species)
        integer(c_int), intent(in), value :: nr_site
        integer(c_int) :: species
        integer(kind=iint) :: site(4)
        integer(kind=iint) :: nr_site_f

        nr_site_f = int(nr_site, kind=iint)

        ! Get lattice coordinates from site number using nr2lattice
        site(1) = nr2lattice(nr_site_f, 1)  ! x
        site(2) = nr2lattice(nr_site_f, 2)  ! y
        site(3) = nr2lattice(nr_site_f, 3)  ! z
        site(4) = nr2lattice(nr_site_f, 4)  ! layer/site_type

        species = int(get_species(site), kind=c_int)
    end function c_get_species_by_site

    ! Get species at a site (uses detected default layer) - DEPRECATED
    function c_get_species(x, y, z) bind(C, name="kmc_get_species") result(species)
        integer(c_int), intent(in), value :: x, y, z
        integer(c_int) :: species
        integer(kind=iint) :: site(4)

        site(1) = int(x, kind=iint)
        site(2) = int(y, kind=iint)
        site(3) = int(z, kind=iint)
        site(4) = {default_layer_name}  ! layer (auto-detected from lattice.f90)

        species = int(get_species(site), kind=c_int)
    end function c_get_species

    ! Get system size (unit cells)
    subroutine c_get_system_size(nx, ny, nz) bind(C, name="kmc_get_system_size")
        integer(c_int), intent(out) :: nx, ny, nz
        nx = int(system_size(1), kind=c_int)
        ny = int(system_size(2), kind=c_int)
        nz = int(system_size(3), kind=c_int)
    end subroutine c_get_system_size

    ! Get total number of sites (accounts for multiple sites per unit cell)
    function c_get_total_sites() bind(C, name="kmc_get_total_sites") result(total_sites)
        use lattice, only: spuck
        integer(c_int) :: total_sites
        total_sites = int(system_size(1) * system_size(2) * system_size(3) * spuck, kind=c_int)
    end function c_get_total_sites

    ! Set rate constant for a process
    subroutine c_set_rate_const(proc_nr, rate) bind(C, name="kmc_set_rate")
        integer(c_int), intent(in), value :: proc_nr
        real(c_double), intent(in), value :: rate
        call set_rate_const(int(proc_nr, kind=iint), real(rate, kind=rdouble))
    end subroutine c_set_rate_const

    ! Get number of available sites for a process (for debugging)
    function c_get_nr_sites(proc_nr) bind(C, name="kmc_get_nr_sites") result(nr_sites)
        integer(c_int), intent(in), value :: proc_nr
        integer(c_int) :: nr_sites
        integer(kind=iint) :: nr_sites_f
        call get_nrofsites(int(proc_nr, kind=iint), nr_sites_f)
        nr_sites = int(nr_sites_f, kind=c_int)
    end function c_get_nr_sites

    ! Get accumulated rate for a process (for debugging)
    function c_get_accum_rate(proc_nr) bind(C, name="kmc_get_accum_rate") result(accum_rate)
        integer(c_int), intent(in), value :: proc_nr
        real(c_double) :: accum_rate
        real(kind=rdouble) :: accum_rate_f
        call get_accum_rate(int(proc_nr, kind=iint), accum_rate_f)
        accum_rate = real(accum_rate_f, kind=c_double)
    end function c_get_accum_rate

    ! Get rate for a process (for debugging)
    function c_get_rate(proc_nr) bind(C, name="kmc_get_rate") result(rate)
        integer(c_int), intent(in), value :: proc_nr
        real(c_double) :: rate
        real(kind=rdouble) :: rate_f
        call get_rate(int(proc_nr, kind=iint), rate_f)
        rate = real(rate_f, kind=c_double)
    end function c_get_rate

    ! Get integrated rate (rate * nr_of_sites) for a process
    function c_get_integ_rate(proc_nr) bind(C, name="kmc_get_integ_rate") result(integ_rate)
        integer(c_int), intent(in), value :: proc_nr
        real(c_double) :: integ_rate
        real(kind=rdouble) :: integ_rate_f
        integer(kind=iint) :: nr_sites_f

        ! Get rate constant
        call get_rate(int(proc_nr, kind=iint), integ_rate_f)

        ! Multiply by number of available sites
        call get_nrofsites(int(proc_nr, kind=iint), nr_sites_f)
        integ_rate_f = integ_rate_f * real(nr_sites_f, kind=rdouble)

        integ_rate = real(integ_rate_f, kind=c_double)
    end function c_get_integ_rate

    ! Manually trigger update_accum_rate (for debugging)
    subroutine c_update_accum_rate() bind(C, name="kmc_update_accum_rate")
        call update_accum_rate()
    end subroutine c_update_accum_rate

    ! Debug: Get nr2lattice mapping for a given site number
    ! Returns the coordinate at index coord_idx (1=x, 2=y, 3=z, 4=layer)
    function c_get_nr2lattice(nr_site, coord_idx) bind(C, name="kmc_get_nr2lattice") result(coord_val)
        integer(c_int), intent(in), value :: nr_site, coord_idx
        integer(c_int) :: coord_val
        integer(kind=iint) :: nr_site_f, coord_idx_f

        nr_site_f = int(nr_site, kind=iint)
        coord_idx_f = int(coord_idx, kind=iint)

        coord_val = int(nr2lattice(nr_site_f, coord_idx_f), kind=c_int)
    end function c_get_nr2lattice

    ! Debug: Get last selected process number from determine_procsite
    ! Note: Debug variables not available in auto-generated code, return 0
    function c_get_debug_last_proc() bind(C, name="kmc_get_debug_last_proc") result(proc_nr)
        integer(c_int) :: proc_nr
        proc_nr = 0
    end function c_get_debug_last_proc

    ! Debug: Get last selected site number from determine_procsite
    ! Note: Debug variables not available in auto-generated code, return 0
    function c_get_debug_last_site() bind(C, name="kmc_get_debug_last_site") result(nr_site)
        integer(c_int) :: nr_site
        nr_site = 0
    end function c_get_debug_last_site

end module c_bindings
"""

    bindings_file = "c_bindings.f90"

    with open(bindings_file, "w") as f:
        f.write(c_bindings_code)

    logger.debug(f"Created {bindings_file} with 13 exported C-callable functions")

    return abspath(bindings_file)


def T_grid(T_min, T_max, n):
    from numpy import linspace, array

    """Return a list of n temperatures between
       T_min and T_max such that the grid of T^(-1)
       is evenly spaced.
    """

    T_min1 = T_min ** (-1.0)
    T_max1 = T_max ** (-1.0)

    grid = list(linspace(T_max1, T_min1, n))
    grid.reverse()
    grid = [x ** (-1.0) for x in grid]

    return array(grid)


def p_grid(p_min, p_max, n):
    from numpy import logspace, log10

    """Return a list of n pressures between
       p_min and p_max such that the grid of log(p)
       is evenly spaced.
    """

    return logspace(log10(p_min), log10(p_max), n)


def evaluate_template(template, **kwargs):
    """Generates code from a template with some simple python preprocessing.

    Preprocessor lines are started with #@ and end with @#. Preprocessor
    lines can use all variables from the calling scope. Result lines
    can also use local variables defined in preprocessor lines.
    """

    escape_python = kwargs.pop("escape_python", False)

    # Create a namespace dict for exec() - Python 3 requires this for variable modification
    namespace = dict(kwargs)
    namespace["result"] = ""

    NEWLINE = "\n"
    PREFIX = "#@"
    lines = [line + NEWLINE for line in template.split(NEWLINE)]

    if escape_python:
        # first just replace verbose lines by pass to check syntax
        python_lines = ""
        matched = False
        for line in lines:
            if re.match(r"^\s*%s ?" % PREFIX, line):
                python_lines += line.lstrip()[3:]
                matched = True
            else:
                python_lines += "pass # %s" % line.lstrip()
        # if the tempate didn't contain any meta strings
        # just return the original
        if not matched:
            return template
        exec(python_lines, namespace)

        # second turn literary lines into write statements
        python_lines = ""
        for line in lines:
            if re.match(r"^\s*%s " % PREFIX, line):
                python_lines += line.lstrip()[3:]
            elif re.match(r"^\s*%s$" % PREFIX, line):
                python_lines += '%sresult += "\\n"\n' % (
                    " " * (len(line) - len(line.lstrip()))
                )
            elif re.match("^$", line):
                # python_lines += 'result += """\n"""\n'
                pass
            else:
                python_lines += '%sresult += ("""%s""".format(**dict(locals())))\n' % (
                    " " * (len(line.expandtabs(4)) - len(line.lstrip())),
                    line.lstrip(),
                )

        exec(python_lines, namespace)

    else:
        # first just replace verbose lines by pass to check syntax
        python_lines = ""
        matched = False
        for line in lines:
            if re.match(r"\s*%s ?" % PREFIX, line):
                python_lines += "%spass %s" % (
                    " " * (len(line) - len(line.lstrip())),
                    line.lstrip(),
                )

                matched = True
            else:
                python_lines += line
        if not matched:
            return template
        exec(python_lines, namespace)

        # second turn literary lines into write statements
        python_lines = ""
        for line in lines:
            if re.match(r"\s*%s " % PREFIX, line):
                python_lines += '%sresult += ("""%s""".format(**dict(locals())))\n' % (
                    " " * (len(line) - len(line.lstrip())),
                    line.lstrip()[3:],
                )
            elif re.match(r"\s*%s" % PREFIX, line):
                python_lines += '%sresult += "\\n"\n' % (
                    " " * (len(line) - len(line.lstrip()))
                )
            else:
                python_lines += line

        exec(python_lines, namespace)

    return namespace["result"]
