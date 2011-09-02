#!/usr/bin/env python

from StringIO import StringIO
from kiwi.datatypes import ValidationError
from numpy.linalg import solve
from numpy import matrix


class CorrectlyNamed:
    """Syntactic Sugar class for use with kiwi, that makes sure that the name
    field of the class has a name field, that always complys with the rules
    for variables.
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


def write_py(fileobj, images, **kwargs):
    if isinstance(fileobj, str):
        fileobj = open(fileobj, 'w')

    scaled_positions = kwargs['scaled_positions'] \
        if 'scaled_positions' in kwargs else True
    fileobj.write('from ase import Atoms\n\n')
    fileobj.write('import numpy as np\n\n')

    if not isinstance(images, (list, tuple)):
        images = [images]
    fileobj.write('images = [\n')

    for image in images:
        fileobj.write("    Atoms(symbols='%s',\n"
                      "          pbc=np.%s,\n"
                      "          cell=np.array(\n      %s,\n" % (
            image.get_chemical_symbols(reduce=True),
            repr(image.pbc),
            repr(image.cell)[6:]))

        if not scaled_positions:
            fileobj.write("          positions=np.array(\n      %s),\n"
                % repr(image.positions)[6:])
        else:
            fileobj.write("          scaled_positions=np.array(\n      %s),\n"
                % repr(image.get_scaled_positions())[6:])

    fileobj.write(']')


def get_ase_constructor(atoms):
    f = StringIO()
    write_py(f, atoms)
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
