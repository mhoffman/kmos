#!/usr/bin/env python
import os, sys
import os.path, shutil
import filecmp

def test_import_export():

    import kmos.types
    import kmos.io

    cwd = os.path.abspath(os.curdir)
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    TEST_DIR = 'test_export'
    REFERENCE_DIR = 'reference_export'
    #if os.path.exists(TEST_DIR):
        #shutil.rmtree(TEST_DIR)

    pt = kmos.types.ProjectTree()
    pt.import_xml_file('default.xml')
    kmos.io.export_source(pt, TEST_DIR)
    for filename in ['base', 'lattice', 'proclist']:
        assert filecmp.cmp(os.path.join(REFERENCE_DIR, '%s.f90' % filename),
                          os.path.join(TEST_DIR, '%s.f90' % filename))

    os.chdir(cwd)

def test_compare_import_variants():
    import kmos.gui
    import kmos.types

    cwd = os.path.abspath(os.curdir)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    pt = kmos.types.ProjectTree()
    editor = kmos.gui.Editor()
    editor.import_xml_file('default.xml')
    pt.import_xml_file('default.xml')
    os.chdir(cwd)
    assert str(pt) == str(editor.project_tree)

def test_ml_export():
    cwd = os.path.abspath(os.curdir)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))


    import kmos.io
    pt = kmos.io.import_xml('pdopd.xml')
    kmos.io.export_source(pt)
    import shutil
    shutil.rmtree('sqrt5PdO')


    os.chdir(cwd)
if __name__ == '__main__':
     test_import_export()
     test_compare_import_variants()
