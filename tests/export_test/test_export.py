#!/usr/bin/env python

def test_export():
    import os, sys
    import os.path, shutil
    import filecmp

    cwd = os.path.abspath(os.curdir)
    os.chdir(os.path.dirname(__file__))

    TEST_DIR = 'test_export'
    #if os.path.exists(TEST_DIR):
        #shutil.rmtree(TEST_DIR)

    os.system('kmos export default.xml %s' % TEST_DIR)

    cmp = filecmp.cmp('reference_test/proclist.f90', '%s/proclist.f90' % TEST_DIR)

    os.chdir(cwd)
    if cmp:
        print("Test passed")
    else:
        print("Test failed")
