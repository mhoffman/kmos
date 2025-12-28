#!/usr/bin/env python

from glob import glob


def test_ini_import():
    for ini_filename in glob("*.ini"):
        from kmos.types import Project

        pt = Project()
        pt.import_ini_file(open(ini_filename))
        pt.save("foo.ini")
        pt.save("foo.xml")


if __name__ == "__main__":
    test_ini_import()
