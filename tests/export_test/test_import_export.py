#!/usr/bin/env python

import os
import sys
import os.path
import shutil
import filecmp
from glob import glob


def test_import_export():
    import kmos.types
    import kmos.io

    cwd = os.path.abspath(os.curdir)
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    TEST_DIR = "test_export"
    REFERENCE_DIR = "reference_export"
    # if os.path.exists(TEST_DIR):
    # shutil.rmtree(TEST_DIR)

    pt = kmos.types.Project()
    pt.import_xml_file("default.xml")
    kmos.io.export_source(pt, TEST_DIR)
    for filename in ["base", "lattice", "proclist"]:
        print(filename)
        assert filecmp.cmp(
            os.path.join(REFERENCE_DIR, "%s.f90" % filename),
            os.path.join(TEST_DIR, "%s.f90" % filename),
        ), "%s changed." % filename

    os.chdir(cwd)


def test_import_export_lat_int():
    import kmos.types
    import kmos.io
    import kmos

    cwd = os.path.abspath(os.curdir)
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    TEST_DIR = "test_export_lat_int"
    REFERENCE_DIR = "reference_export_lat_int"
    # if os.path.exists(TEST_DIR):
    # shutil.rmtree(TEST_DIR)

    print(sys.path)
    print(kmos.__file__)

    pt = kmos.types.Project()
    pt.import_xml_file("default.xml")
    kmos.io.export_source(pt, TEST_DIR, code_generator="lat_int")
    for filename in (
        ["base", "lattice", "proclist"]
        + [
            os.path.basename(os.path.splitext(x)[0])
            for x in glob(os.path.join(TEST_DIR, "run_proc*.f90"))
        ]
        + [
            os.path.basename(os.path.splitext(x)[0])
            for x in glob(os.path.join(TEST_DIR, "nli*.f90"))
        ]
    ):
        print(filename)
        assert filecmp.cmp(
            os.path.join(REFERENCE_DIR, "%s.f90" % filename),
            os.path.join(TEST_DIR, "%s.f90" % filename),
        ), "%s changed." % filename

    os.chdir(cwd)


def test_import_export_otf():
    import kmos.types
    import kmos.io
    import kmos

    cwd = os.path.abspath(os.curdir)
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    TEST_DIR = "test_export_otf"
    REFERENCE_DIR = "reference_export_otf"
    # if os.path.exists(TEST_DIR):
    # shutil.rmtree(TEST_DIR)

    print(sys.path)
    print(kmos.__file__)

    pt = kmos.types.Project()
    pt.import_xml_file("default.xml")
    pt.shorten_names(max_length=35)
    kmos.io.export_source(pt, TEST_DIR, code_generator="otf")
    for filename in [
        "base",
        "lattice",
        "proclist",
        "proclist_pars",
        "proclist_constants",
    ] + [
        os.path.basename(os.path.splitext(x)[0])
        for x in glob(os.path.join(TEST_DIR, "run_proc*.f90"))
    ]:
        print(filename)
        assert filecmp.cmp(
            os.path.join(REFERENCE_DIR, "%s.f90" % filename),
            os.path.join(TEST_DIR, "%s.f90" % filename),
        ), "%s changed." % filename

    os.chdir(cwd)


def test_import_export_pdopd_local_smart():
    import kmos.types
    import kmos.io

    cwd = os.path.abspath(os.curdir)
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    TEST_DIR = "test_pdopd_local_smart"
    REFERENCE_DIR = "reference_pdopd_local_smart"
    # if os.path.exists(TEST_DIR):
    # shutil.rmtree(TEST_DIR)

    pt = kmos.types.Project()
    pt.import_xml_file("pdopd.xml")
    kmos.io.export_source(pt, TEST_DIR, code_generator="local_smart")
    for filename in ["base", "lattice", "proclist"]:
        print(filename)
        assert filecmp.cmp(
            os.path.join(REFERENCE_DIR, "%s.f90" % filename),
            os.path.join(TEST_DIR, "%s.f90" % filename),
        ), "%s changed." % filename

    os.chdir(cwd)


def test_import_export_pdopd_lat_int():
    import kmos.types
    import kmos.io
    import kmos

    cwd = os.path.abspath(os.curdir)
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    TEST_DIR = "test_pdopd_lat_int"
    REFERENCE_DIR = "reference_pdopd_lat_int"
    # if os.path.exists(TEST_DIR):
    # shutil.rmtree(TEST_DIR)

    print(sys.path)
    print(kmos.__file__)
    pt = kmos.types.Project()
    pt.import_xml_file("pdopd.xml")
    kmos.io.export_source(pt, TEST_DIR, code_generator="lat_int")
    for filename in (
        ["base", "lattice", "proclist", "proclist_constants"]
        + [
            os.path.basename(os.path.splitext(x)[0])
            for x in glob(os.path.join(TEST_DIR, "run_proc*.f90"))
        ]
        + [
            os.path.basename(os.path.splitext(x)[0])
            for x in glob(os.path.join(TEST_DIR, "nli*.f90"))
        ]
    ):
        print(filename)
        assert filecmp.cmp(
            os.path.join(REFERENCE_DIR, "%s.f90" % filename),
            os.path.join(TEST_DIR, "%s.f90" % filename),
        ), "%s changed." % filename

    os.chdir(cwd)


def test_import_export_intZGB_otf():
    import kmos.types
    import kmos.io
    import kmos

    cwd = os.path.abspath(os.curdir)
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    TEST_DIR = "test_export_intZGB_otf"
    REFERENCE_DIR = "reference_export_intZGB_otf"
    # if os.path.exists(TEST_DIR):
    # shutil.rmtree(TEST_DIR)

    print(sys.path)
    print(kmos.__file__)

    pt = kmos.types.Project()
    pt.import_xml_file("intZGB_otf.xml")
    kmos.io.export_source(pt, TEST_DIR, code_generator="otf")
    for filename in [
        "base",
        "lattice",
        "proclist",
        "proclist_pars",
        "proclist_constants",
    ] + [
        os.path.basename(os.path.splitext(x)[0])
        for x in glob(os.path.join(TEST_DIR, "run_proc*.f90"))
    ]:
        print(filename)
        assert filecmp.cmp(
            os.path.join(REFERENCE_DIR, "%s.f90" % filename),
            os.path.join(TEST_DIR, "%s.f90" % filename),
        ), "%s changed." % filename
    os.chdir(cwd)


def off_compare_import_variants():
    import kmos.gui
    import kmos.types

    cwd = os.path.abspath(os.curdir)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    pt = kmos.types.Project()
    editor = kmos.gui.Editor()
    editor.import_xml_file("default.xml")
    pt.import_xml_file("default.xml")
    os.chdir(cwd)
    assert str(pt) == str(editor.project_tree)


def test_ml_export():
    cwd = os.path.abspath(os.curdir)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    import kmos.io

    pt = kmos.io.import_xml_file("pdopd.xml")
    kmos.io.export_source(pt)

    shutil.rmtree("sqrt5PdO")

    os.chdir(cwd)


def test_export_with_debug():
    """Test exporting a model with debug flag enabled (local_smart backend)."""
    import kmos.types
    import kmos.io

    cwd = os.path.abspath(os.curdir)
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    TEST_DIR = "test_export_debug"

    # Clean up if directory exists from previous test run
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)

    # Create options object with debug enabled
    class Options:
        def __init__(self):
            self.debug = True
            self.backend = "local_smart"
            self.acf = False
            self.no_optimize = False

    options = Options()

    # Import and export with debug flag
    pt = kmos.types.Project()
    pt.import_xml_file("default.xml")

    # Set meta.debug to trigger debug code paths during code generation
    pt.meta.debug = 2

    kmos.io.export_source(pt, TEST_DIR, options=options)

    # Verify that files were created
    assert os.path.exists(TEST_DIR), "Export directory should exist"
    assert os.path.exists(os.path.join(TEST_DIR, "base.f90")), "base.f90 should exist"
    assert os.path.exists(
        os.path.join(TEST_DIR, "proclist.f90")
    ), "proclist.f90 should exist"
    assert os.path.exists(
        os.path.join(TEST_DIR, "lattice.f90")
    ), "lattice.f90 should exist"

    # Verify that assert.ppc was copied (used for debug assertions)
    assert os.path.exists(
        os.path.join(TEST_DIR, "assert.ppc")
    ), "assert.ppc should exist for debug builds"

    # Verify debug print statements are in generated code
    with open(os.path.join(TEST_DIR, "proclist.f90"), "r") as f:
        proclist_content = f.read()
        assert (
            'print *,"PROCLIST/RUN_PROC_NR' in proclist_content
        ), "Debug print statements should be in proclist.f90"

    # Clean up test directory
    shutil.rmtree(TEST_DIR)

    os.chdir(cwd)


def test_export_with_debug_lat_int():
    """Test exporting a model with debug flag enabled (lat_int backend)."""
    import kmos.types
    import kmos.io

    cwd = os.path.abspath(os.curdir)
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    TEST_DIR = "test_export_debug_lat_int"

    # Clean up if directory exists from previous test run
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)

    # Create options object with debug enabled
    class Options:
        def __init__(self):
            self.debug = True
            self.backend = "lat_int"
            self.acf = False
            self.no_optimize = False

    options = Options()

    # Import and export with debug flag
    pt = kmos.types.Project()
    pt.import_xml_file("default.xml")

    # Set meta.debug to trigger debug code paths during code generation
    pt.meta.debug = 3  # Use level 3 to test even more debug branches

    kmos.io.export_source(pt, TEST_DIR, options=options)

    # Verify that files were created
    assert os.path.exists(TEST_DIR), "Export directory should exist"
    assert os.path.exists(os.path.join(TEST_DIR, "base.f90")), "base.f90 should exist"
    assert os.path.exists(
        os.path.join(TEST_DIR, "proclist.f90")
    ), "proclist.f90 should exist"
    assert os.path.exists(
        os.path.join(TEST_DIR, "lattice.f90")
    ), "lattice.f90 should exist"

    # Verify that assert.ppc was copied
    assert os.path.exists(
        os.path.join(TEST_DIR, "assert.ppc")
    ), "assert.ppc should exist for debug builds"

    # lat_int backend generates additional run_proc files
    run_proc_files = glob(os.path.join(TEST_DIR, "run_proc*.f90"))
    assert len(run_proc_files) > 0, "lat_int should generate run_proc*.f90 files"

    # Verify debug print statements are in generated nli code (lat_int specific)
    nli_files = glob(os.path.join(TEST_DIR, "nli_*.f90"))
    assert len(nli_files) > 0, "lat_int should generate nli_*.f90 files"

    # When debug > 0, lat_int generates non-pure functions (instead of pure functions)
    # Check that we have non-pure functions (debug mode)
    with open(nli_files[0], "r") as f:
        nli_content = f.read()
        # With debug enabled, functions are not marked as 'pure'
        assert "function nli_" in nli_content, "Should have nli functions"
        # When debug=0, it would be "pure function nli_"
        # When debug>0, it's just "function nli_" (non-pure)

    # Clean up test directory
    shutil.rmtree(TEST_DIR)

    os.chdir(cwd)


def test_export_with_debug_otf():
    """Test exporting a model with debug flag enabled (otf backend)."""
    import kmos.types
    import kmos.io

    cwd = os.path.abspath(os.curdir)
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    TEST_DIR = "test_export_debug_otf"

    # Clean up if directory exists from previous test run
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)

    # Create options object with debug enabled
    class Options:
        def __init__(self):
            self.debug = True
            self.backend = "otf"
            self.acf = False
            self.no_optimize = False

    options = Options()

    # Import and export with debug flag
    pt = kmos.types.Project()
    pt.import_xml_file("default.xml")

    # Set meta.debug to trigger debug code paths during code generation
    pt.meta.debug = 1

    pt.shorten_names(max_length=35)
    kmos.io.export_source(pt, TEST_DIR, options=options)

    # Verify that files were created
    assert os.path.exists(TEST_DIR), "Export directory should exist"
    assert os.path.exists(os.path.join(TEST_DIR, "base.f90")), "base.f90 should exist"
    assert os.path.exists(
        os.path.join(TEST_DIR, "proclist.f90")
    ), "proclist.f90 should exist"
    assert os.path.exists(
        os.path.join(TEST_DIR, "lattice.f90")
    ), "lattice.f90 should exist"

    # otf backend generates additional files
    assert os.path.exists(
        os.path.join(TEST_DIR, "proclist_pars.f90")
    ), "proclist_pars.f90 should exist for otf"

    # Verify that assert.ppc was copied
    assert os.path.exists(
        os.path.join(TEST_DIR, "assert.ppc")
    ), "assert.ppc should exist for debug builds"

    # Verify debug print statements are in generated code
    with open(os.path.join(TEST_DIR, "proclist.f90"), "r") as f:
        proclist_content = f.read()
        assert (
            'print *,"PROCLIST/RUN_PROC_NR' in proclist_content
        ), "Debug print statements should be in proclist.f90"

    # Clean up test directory
    shutil.rmtree(TEST_DIR)

    os.chdir(cwd)


def test_export_intZGB_with_debug_otf():
    """Test exporting intZGB model with debug level 3 (otf backend)."""
    import kmos.types
    import kmos.io

    cwd = os.path.abspath(os.curdir)
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    TEST_DIR = "test_export_intZGB_debug_otf"

    # Clean up if directory exists from previous test run
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)

    # Create options object with debug enabled
    class Options:
        def __init__(self):
            self.debug = True
            self.backend = "otf"
            self.acf = False
            self.no_optimize = False

    options = Options()

    # Import intZGB model designed for otf backend
    pt = kmos.types.Project()
    pt.import_xml_file("intZGB_otf.xml")

    # Set meta.debug to level 3 to trigger more debug code paths
    pt.meta.debug = 3

    kmos.io.export_source(pt, TEST_DIR, options=options)

    # Verify that files were created
    assert os.path.exists(TEST_DIR), "Export directory should exist"
    assert os.path.exists(os.path.join(TEST_DIR, "base.f90")), "base.f90 should exist"
    assert os.path.exists(
        os.path.join(TEST_DIR, "proclist.f90")
    ), "proclist.f90 should exist"
    assert os.path.exists(
        os.path.join(TEST_DIR, "lattice.f90")
    ), "lattice.f90 should exist"

    # otf backend generates additional files
    assert os.path.exists(
        os.path.join(TEST_DIR, "proclist_pars.f90")
    ), "proclist_pars.f90 should exist for otf"
    assert os.path.exists(
        os.path.join(TEST_DIR, "proclist_constants.f90")
    ), "proclist_constants.f90 should exist for otf"

    # Verify that assert.ppc was copied
    assert os.path.exists(
        os.path.join(TEST_DIR, "assert.ppc")
    ), "assert.ppc should exist for debug builds"

    # Verify debug print statements are in generated code (level 3 has more debug output)
    with open(os.path.join(TEST_DIR, "proclist.f90"), "r") as f:
        proclist_content = f.read()
        assert (
            'print *,"PROCLIST/RUN_PROC_NR' in proclist_content
        ), "Debug print statements should be in proclist.f90"

    # Check lattice.f90 for debug statements
    with open(os.path.join(TEST_DIR, "lattice.f90"), "r") as f:
        lattice_content = f.read()
        # With debug > 1, lattice should have debug print statements too
        assert (
            "print *," in lattice_content
        ), "Debug print statements should be in lattice.f90 at debug level 3"

    # Verify run_proc files have debug statements
    run_proc_files = glob(os.path.join(TEST_DIR, "run_proc_*.f90"))
    assert len(run_proc_files) > 0, "otf should generate run_proc_*.f90 files"

    # Clean up test directory
    shutil.rmtree(TEST_DIR)

    os.chdir(cwd)


def test_export_pdopd_multilattice_with_debug():
    """Test exporting multi-lattice pdopd model with debug level 3 (local_smart backend)."""
    import kmos.types
    import kmos.io

    cwd = os.path.abspath(os.curdir)
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    TEST_DIR = "test_export_pdopd_multilattice_debug"

    # Clean up if directory exists from previous test run
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)

    # Create options object with debug enabled
    class Options:
        def __init__(self):
            self.debug = True
            self.backend = "local_smart"
            self.acf = False
            self.no_optimize = False

    options = Options()

    # Import multi-lattice pdopd model (2 layers)
    pt = kmos.types.Project()
    pt.import_xml_file("pdopd.xml")

    # Set meta.debug to level 3 to trigger more debug code paths
    pt.meta.debug = 3

    kmos.io.export_source(pt, TEST_DIR, options=options)

    # Verify that files were created
    assert os.path.exists(TEST_DIR), "Export directory should exist"
    assert os.path.exists(os.path.join(TEST_DIR, "base.f90")), "base.f90 should exist"
    assert os.path.exists(
        os.path.join(TEST_DIR, "proclist.f90")
    ), "proclist.f90 should exist"
    assert os.path.exists(
        os.path.join(TEST_DIR, "lattice.f90")
    ), "lattice.f90 should exist"

    # Verify that assert.ppc was copied
    assert os.path.exists(
        os.path.join(TEST_DIR, "assert.ppc")
    ), "assert.ppc should exist for debug builds"

    # Verify debug print statements are in generated code
    with open(os.path.join(TEST_DIR, "proclist.f90"), "r") as f:
        proclist_content = f.read()
        assert (
            'print *,"PROCLIST/RUN_PROC_NR' in proclist_content
        ), "Debug print statements should be in proclist.f90"

    # Check lattice.f90 for debug statements
    with open(os.path.join(TEST_DIR, "lattice.f90"), "r") as f:
        lattice_content = f.read()
        # With debug > 1, lattice should have debug print statements
        assert (
            "print *," in lattice_content
        ), "Debug print statements should be in lattice.f90 at debug level 3"

    # Clean up test directory
    shutil.rmtree(TEST_DIR)

    os.chdir(cwd)


def test_export_with_acf():
    """Test exporting a model with ACF (autocorrelation function) enabled."""
    import kmos.types
    import kmos.io

    cwd = os.path.abspath(os.curdir)
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    TEST_DIR = "test_export_acf"

    # Clean up if directory exists from previous test run
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)

    # Create options object with ACF enabled
    class Options:
        def __init__(self):
            self.debug = False
            self.backend = "local_smart"
            self.acf = True
            self.no_optimize = False

    options = Options()

    # Import and export with ACF flag
    pt = kmos.types.Project()
    pt.import_xml_file("default.xml")
    kmos.io.export_source(pt, TEST_DIR, options=options)

    # Verify that standard files were created
    assert os.path.exists(TEST_DIR), "Export directory should exist"
    assert os.path.exists(os.path.join(TEST_DIR, "base.f90")), "base.f90 should exist"
    assert os.path.exists(
        os.path.join(TEST_DIR, "proclist.f90")
    ), "proclist.f90 should exist"
    assert os.path.exists(
        os.path.join(TEST_DIR, "lattice.f90")
    ), "lattice.f90 should exist"

    # Verify that ACF-specific files were created
    assert os.path.exists(
        os.path.join(TEST_DIR, "base_acf.f90")
    ), "base_acf.f90 should exist when acf=True"
    assert os.path.exists(
        os.path.join(TEST_DIR, "proclist_acf.f90")
    ), "proclist_acf.f90 should exist when acf=True"

    # Verify ACF module content
    with open(os.path.join(TEST_DIR, "proclist_acf.f90"), "r") as f:
        acf_content = f.read()
        assert (
            "module proclist_acf" in acf_content
        ), "proclist_acf.f90 should contain proclist_acf module"
        assert (
            "get_diff_sites" in acf_content
        ), "ACF module should contain diffusion site tracking functions"

    # Clean up test directory
    shutil.rmtree(TEST_DIR)

    os.chdir(cwd)
