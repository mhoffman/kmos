#!/usr/bin/env python

from StringIO import StringIO
from kiwi.datatypes import ValidationError

class CorrectlyNamed:
    """Syntactic Sugar class for use with kiwi, that makes sure that the name
    field of the class has a name field, that always complys with the rules for variables
    """
    def __init__(self):
        pass

    def on_name__validate(self, _, name):
        """Called by kiwi upon chaning a string
        """
        if ' ' in name:
            return ValidationError('No spaces allowed')
        elif name and not name[0].isalpha():
            return ValidationError('Need to start with a letter')

def get_ase_constructor(atoms):
    import ase.io.py
    f = StringIO()
    ase.io.py.write_py(f, atoms)
    for line in f:
        astr += line.strip()
    f.seek(0)
    lines = f.readlines()
    f.close()
    astr = ''
    for i, line in enumerate(lines):
        if i >= 5 and i < len(lines) - 1:
            astr += line
    astr = astr[:-2]
    return astr.strip()
