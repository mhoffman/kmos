#!/usr/bin/env python

import os, sys
import os.path, shutil
import filecmp

TEST_DIR = 'test_export'
if os.path.exists(TEST_DIR):
    shutil.rmtree(TEST_DIR)

os.system('../../main.py -o default.xml -x %s' % TEST_DIR)

cmp = filecmp.cmp('reference_test/proclist.f90', '%s/proclist.f90' % TEST_DIR)
if cmp:
    print("Test passed")
else:
    print("Test failed")
