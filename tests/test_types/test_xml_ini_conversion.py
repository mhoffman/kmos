#!/usr/bin/env python

import os
import filecmp

def test_xml_ini_conversion():
    import kmos.types
    import kmos.io

    cwd = os.path.abspath(os.curdir)
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    TEST_DIR = 'test'
    REFERENCE_DIR = 'reference'


    pt = kmos.types.Project()
    pt.import_file('reference/AB_model.xml')
    pt.save('test/AB_model.ini')

    assert filecmp.cmp('test/AB_model.ini', 'reference/AB_model.ini')

def test_ini_xml_conversion():
    import kmos.types
    import kmos.io

    cwd = os.path.abspath(os.curdir)
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    TEST_DIR = 'test'
    REFERENCE_DIR = 'reference'


    pt = kmos.types.Project()
    pt.import_file('reference/AB_model.ini')
    pt.save('test/AB_model.xml')

    assert filecmp.cmp('test/AB_model.xml', 'reference/AB_model.xml')
