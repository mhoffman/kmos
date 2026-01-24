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
        (r"(?P<before>.*)selected_int_kind" "\((?P<args>.*)\)(?P<after>.*)"),
        flags=re.IGNORECASE,
    )
    real_pattern = re.compile(
        (r"(?P<before>.*)selected_real_kind" "\((?P<args>.*)\)(?P<after>.*)"),
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

    # 4. Create c_bindings.f90 if it doesn't exist
    if not isfile("c_bindings.f90"):
        logger.info("Creating c_bindings.f90...")
        create_c_bindings()
    else:
        logger.info("Using existing c_bindings.f90")

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
    link_cmd = """
        cd /src &&
        /opt/emsdk/upstream/emscripten/emcc -g -O0 -sASSERTIONS=2 -sSTACK_SIZE=10MB \
            -sEXPORTED_FUNCTIONS=_kmc_init,_kmc_do_step,_kmc_get_time,_kmc_get_species,_kmc_get_system_size,_kmc_set_rate,_kmc_get_nr_sites,_kmc_get_accum_rate,_kmc_get_rate,_kmc_update_accum_rate,_kmc_get_nr2lattice,_kmc_get_debug_last_proc,_kmc_get_debug_last_site,_malloc,_free \
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

    Key modifications:
    - Replace array slice assignments with explicit element assignments

    Args:
        src_dir: Directory containing Fortran source files

    Returns:
        int: Number of modifications applied
    """
    import re
    from os.path import join, isfile

    modifications_count = 0

    # Modify proclist.f90
    proclist_file = join(src_dir, "proclist.f90")
    if not isfile(proclist_file):
        logger.debug(
            f"proclist.f90 not found in {src_dir}, skipping WASM modifications"
        )
        return 0

    with open(proclist_file, "r") as f:
        content = f.read()

    # Skip if already modified (idempotent)
    if "! WASM:" in content:
        logger.debug("proclist.f90 already contains WASM modifications, skipping")
        return 0

    logger.debug("Scanning proclist.f90 for array slice patterns...")

    # Replace array slice assignments with explicit element assignments
    # Pattern: lsite = nr2lattice(nr_site, :)
    slice_pattern = r"(\s+)lsite = nr2lattice\(nr_site, :\)"
    explicit_replacement = r"\1! WASM: Explicit element assignment instead of array slice\n\1lsite(1) = nr2lattice(nr_site, 1)\n\1lsite(2) = nr2lattice(nr_site, 2)\n\1lsite(3) = nr2lattice(nr_site, 3)\n\1lsite(4) = nr2lattice(nr_site, 4)"

    # Count matches before replacement
    matches = re.findall(slice_pattern, content)
    modifications_count = len(matches)

    if modifications_count > 0:
        modified_content = re.sub(slice_pattern, explicit_replacement, content)

        with open(proclist_file, "w") as f:
            f.write(modified_content)

        logger.debug(
            f"Replaced {modifications_count} array slice pattern(s) in proclist.f90"
        )
    else:
        logger.debug("No array slice patterns found in proclist.f90")

    return modifications_count


def create_c_bindings():
    """Create c_bindings.f90 for WebAssembly exports.

    Generates Fortran bindings with C calling convention for JavaScript/WASM interface.

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
    from os.path import abspath

    c_bindings_code = """module c_bindings
    use iso_c_binding
    use kind_values
    use base, only: get_kmc_time, get_kmc_step
    use lattice, only: allocate_system, base_get_species => get_species, &
                       lattice2nr, nr2lattice, spuck, system_size
    use proclist, only: do_kmc_step, init, &
                        set_rate_const, avail_sites, nr_of_proc

    implicit none

contains

    subroutine kmc_init(nr_procs, sys_size, sys_name, name_len) bind(C, name="kmc_init")
        integer(c_int), value :: nr_procs, name_len
        integer(c_int), dimension(3) :: sys_size
        character(kind=c_char), dimension(200) :: sys_name

        integer(kind=iint) :: f_nr_procs
        integer(kind=iint), dimension(2) :: f_sys_size
        character(len=200) :: f_sys_name
        integer :: i
        integer(kind=iint) :: f_layer, f_seed

        f_nr_procs = int(nr_procs, iint)
        f_sys_size = int(sys_size(1:2), iint)

        do i = 1, min(name_len, 200)
            f_sys_name(i:i) = sys_name(i)
        end do
        if (name_len < 200) f_sys_name(name_len+1:) = ' '

        ! Initialize with default layer (0) and seed
        f_layer = 0
        f_seed = 42

        call init(f_sys_size, f_sys_name, f_layer, f_seed, .true.)
    end subroutine kmc_init

    subroutine kmc_do_step() bind(C, name="kmc_do_step")
        call do_kmc_step()
    end subroutine kmc_do_step

    function kmc_get_time() result(time) bind(C, name="kmc_get_time")
        real(c_double) :: time
        real(kind=rdouble) :: kmc_time
        call get_kmc_time(kmc_time)
        time = real(kmc_time, c_double)
    end function kmc_get_time

    subroutine kmc_get_species(site_nr, species_out) bind(C, name="kmc_get_species")
        integer(c_int), value :: site_nr
        integer(c_int), intent(out) :: species_out
        integer(kind=iint), dimension(4) :: lattice_coords
        integer(kind=iint) :: species

        ! Use array access to nr2lattice
        lattice_coords = nr2lattice(int(site_nr, iint), :)
        species = base_get_species(lattice_coords)
        species_out = int(species, c_int)
    end subroutine kmc_get_species

    function kmc_get_system_size() result(total_size) bind(C, name="kmc_get_system_size")
        integer(c_int) :: total_size
        total_size = int(system_size(1) * system_size(2) * system_size(3) * spuck, c_int)
    end function kmc_get_system_size

    subroutine kmc_set_rate(proc_nr, rate) bind(C, name="kmc_set_rate")
        integer(c_int), value :: proc_nr
        real(c_double), value :: rate
        call set_rate_const(int(proc_nr, iint), real(rate, rsingle))
    end subroutine kmc_set_rate

    function kmc_get_nr_sites() result(nr_sites) bind(C, name="kmc_get_nr_sites")
        integer(c_int) :: nr_sites
        nr_sites = int(system_size(1) * system_size(2) * system_size(3) * spuck, c_int)
    end function kmc_get_nr_sites

    function kmc_get_accum_rate() result(rate) bind(C, name="kmc_get_accum_rate")
        real(c_double) :: rate
        ! Placeholder - implement actual function
        rate = 0.0d0
    end function kmc_get_accum_rate

    function kmc_get_rate(proc_nr) result(rate) bind(C, name="kmc_get_rate")
        integer(c_int), value :: proc_nr
        real(c_double) :: rate
        ! Placeholder - implement actual function
        rate = 0.0d0
    end function kmc_get_rate

    subroutine kmc_update_accum_rate() bind(C, name="kmc_update_accum_rate")
        ! Placeholder - implement actual function
    end subroutine kmc_update_accum_rate

    subroutine kmc_get_nr2lattice(site_nr, coord_idx, coord_out) bind(C, name="kmc_get_nr2lattice")
        integer(c_int), value :: site_nr, coord_idx
        integer(c_int), intent(out) :: coord_out

        ! Use array access to nr2lattice
        coord_out = int(nr2lattice(int(site_nr, iint), coord_idx), c_int)
    end subroutine kmc_get_nr2lattice

    function kmc_get_debug_last_proc() result(proc_nr) bind(C, name="kmc_get_debug_last_proc")
        integer(c_int) :: proc_nr
        ! Debug variables not available in generated code
        proc_nr = 0
    end function kmc_get_debug_last_proc

    function kmc_get_debug_last_site() result(site_nr) bind(C, name="kmc_get_debug_last_site")
        integer(c_int) :: site_nr
        ! Debug variables not available in generated code
        site_nr = 0
    end function kmc_get_debug_last_site

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
            if re.match("^\s*%s ?" % PREFIX, line):
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
            if re.match("^\s*%s " % PREFIX, line):
                python_lines += line.lstrip()[3:]
            elif re.match("^\s*%s$" % PREFIX, line):
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
            if re.match("\s*%s ?" % PREFIX, line):
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
            if re.match("\s*%s " % PREFIX, line):
                python_lines += '%sresult += ("""%s""".format(**dict(locals())))\n' % (
                    " " * (len(line) - len(line.lstrip())),
                    line.lstrip()[3:],
                )
            elif re.match("\s*%s" % PREFIX, line):
                python_lines += '%sresult += "\\n"\n' % (
                    " " * (len(line) - len(line.lstrip()))
                )
            else:
                python_lines += line

        exec(python_lines, namespace)

    return namespace["result"]
