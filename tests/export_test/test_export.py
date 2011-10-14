#!/usr/bin/env python

def test_import_export():
    import os, sys
    import os.path, shutil
    import filecmp

    import kmos.types
    import kmos.export

    cwd = os.path.abspath(os.curdir)
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    TEST_DIR = 'test_export'
    #if os.path.exists(TEST_DIR):
        #shutil.rmtree(TEST_DIR)

    pt = kmos.types.ProjectTree()
    pt.import_xml_file('default.xml')
    kmos.export.export_source(pt, TEST_DIR)
    for filename in ['base', 'lattice', 'proclist']:
        assert filecmp.cmp(os.path.join('reference_test', '%s.f90' % filename),
                          os.path.join(TEST_DIR, '%s.f90' % filename))

    os.chdir(cwd)

if __name__ == '__main__':
     test_import_export()
