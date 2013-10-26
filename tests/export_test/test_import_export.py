#!/usr/bin/env python
import os, sys
import os.path, shutil
import filecmp
from glob import glob

def test_import_export():

    import kmos.types
    import kmos.io

    cwd = os.path.abspath(os.curdir)
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    TEST_DIR = 'test_export'
    REFERENCE_DIR = 'reference_export'
    #if os.path.exists(TEST_DIR):
        #shutil.rmtree(TEST_DIR)

    pt = kmos.types.Project()
    pt.import_xml_file('default.xml')
    kmos.io.export_source(pt, TEST_DIR)
    for filename in ['base', 'lattice', 'proclist']:
        print(filename)
        assert filecmp.cmp(os.path.join(REFERENCE_DIR, '%s.f90' % filename),
                          os.path.join(TEST_DIR, '%s.f90' % filename)),\
             '%s changed.' % filename

    os.chdir(cwd)

def test_import_export_lat_int():

    import kmos.types
    import kmos.io
    import kmos

    cwd = os.path.abspath(os.curdir)
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    TEST_DIR = 'test_export_lat_int'
    REFERENCE_DIR = 'reference_export_lat_int'
    #if os.path.exists(TEST_DIR):
        #shutil.rmtree(TEST_DIR)

    print(sys.path)
    print(kmos.__file__)

    pt = kmos.types.Project()
    pt.import_xml_file('default.xml')
    kmos.io.export_source(pt, TEST_DIR, code_generator='lat_int')
    for filename in ['base', 'lattice', 'proclist'] \
        + [os.path.basename(os.path.splitext(x)[0]) for x in glob(os.path.join(TEST_DIR, 'run_proc*.f90'))] \
        + [os.path.basename(os.path.splitext(x)[0]) for x in glob(os.path.join(TEST_DIR, 'nli*.f90'))]:
        print(filename)
        assert filecmp.cmp(os.path.join(REFERENCE_DIR, '%s.f90' % filename),
                          os.path.join(TEST_DIR, '%s.f90' % filename)),\
             '%s changed.' % filename

    os.chdir(cwd)

def test_import_export_pdopd_local_smart():

    import kmos.types
    import kmos.io

    cwd = os.path.abspath(os.curdir)
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    TEST_DIR = 'test_pdopd_local_smart'
    REFERENCE_DIR = 'reference_pdopd_local_smart'
    #if os.path.exists(TEST_DIR):
        #shutil.rmtree(TEST_DIR)

    pt = kmos.types.Project()
    pt.import_xml_file('pdopd.xml')
    kmos.io.export_source(pt, TEST_DIR, code_generator='local_smart')
    for filename in ['base', 'lattice', 'proclist']:
        print(filename)
        assert filecmp.cmp(os.path.join(REFERENCE_DIR, '%s.f90' % filename),
                          os.path.join(TEST_DIR, '%s.f90' % filename)),\
             '%s changed.' % filename

    os.chdir(cwd)
def test_import_export_pdopd_lat_int():

    import kmos.types
    import kmos.io
    import kmos

    cwd = os.path.abspath(os.curdir)
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    TEST_DIR = 'test_pdopd_lat_int'
    REFERENCE_DIR = 'reference_pdopd_lat_int'
    #if os.path.exists(TEST_DIR):
        #shutil.rmtree(TEST_DIR)

    print(sys.path)
    print(kmos.__file__)
    pt = kmos.types.Project()
    pt.import_xml_file('pdopd.xml')
    kmos.io.export_source(pt, TEST_DIR, code_generator='lat_int')
    for filename in ['base', 'lattice', 'proclist', 'proclist_constants'] \
        + [os.path.basename(os.path.splitext(x)[0]) for x in glob(os.path.join(TEST_DIR, 'run_proc*.f90'))] \
        + [os.path.basename(os.path.splitext(x)[0]) for x in glob(os.path.join(TEST_DIR, 'nli*.f90'))]:

        print(filename)
        assert filecmp.cmp(os.path.join(REFERENCE_DIR, '%s.f90' % filename),
                          os.path.join(TEST_DIR, '%s.f90' % filename)),\
             '%s changed.' % filename

    os.chdir(cwd)

def test_compare_import_variants():
    import kmos.gui
    import kmos.types

    cwd = os.path.abspath(os.curdir)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    pt = kmos.types.Project()
    editor = kmos.gui.Editor()
    editor.import_xml_file('default.xml')
    pt.import_xml_file('default.xml')
    os.chdir(cwd)
    assert str(pt) == str(editor.project_tree)

def test_ml_export():
    cwd = os.path.abspath(os.curdir)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))


    import kmos.io
    pt = kmos.io.import_xml_file('pdopd.xml')
    kmos.io.export_source(pt)
    import shutil
    shutil.rmtree('sqrt5PdO')


    os.chdir(cwd)
if __name__ == '__main__':
     test_import_export()
     test_compare_import_variants()
