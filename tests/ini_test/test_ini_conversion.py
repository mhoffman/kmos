#!/usr/bin/env python 

from glob import glob
from os.path import splitext
from kmos.io import import_xml_file


def test_ini_conversion():
    for xml_filename in glob('*.xml'):
        seed = splitext(xml_filename)[0]
        pt = import_xml_file(xml_filename)
        with open('%s.ini' % seed, 'w') as outfile:
            ini_string = pt._get_ini_string()
            assert ini_string
            outfile.write(ini_string)
        
if __name__ == '__main__':
    test_ini_conversion()
