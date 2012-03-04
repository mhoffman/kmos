#!/usr/bin/env python
"""Several utility functions that do not seem to fit somewhere
   else.
"""
#    Copyright 2009-2012 Max J. Hoffmann (mjhoffmann@gmail.com)
#    This file is part of kmos.
#
#    kmos is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    kmos is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with kmos.  If not, see <http://www.gnu.org/licenses/>.

from StringIO import StringIO

try:
    from kiwi.datatypes import ValidationError
except:
    ValidationError = UserWarning


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
    """Write a ASE atoms construction string for `images`
       into `fileobj`.
    """
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
    """Return the ASE constructor string for `atoms`."""
    if type(atoms) is type(str):
        atoms = eval(atoms)
    if type(atoms) is list:
        atoms = atoms[0]
    f = StringIO()
    write_py(f, atoms)
    f.seek(0)
    lines = f.readlines()
    f.close()
    astr = ''
    for i, line in enumerate(lines):
        if i >= 5 and i < len(lines) - 1:
            astr += line
    astr = astr[:-2]
    return astr.strip()


def product(*args, **kwds):
    """Take two lists and return iterator producing
    all combinations of tuples between elements
    of the two lists."""
    # product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy
    # product(range(2), repeat=3) --> 000 001 010 011 100 101 110 111
    pools = [tuple(arg) for arg in args] * kwds.get('repeat', 1)
    result = [[]]
    for pool in pools:
        result = [x + [y] for x in result for y in pool]
    for prod in result:
        yield tuple(prod)


def split_sequence(seq, size):
    """Take a list and a number n and return list
       divided into n sublists of roughly equal size.
    """
    newseq = []
    splitsize = 1.0 / size * len(seq)
    for i in range(size):
        newseq.append(seq[int(round(i * splitsize)):
                      int(round((i + 1) * splitsize))])
    return newseq


def download(project):
    from django.http import HttpResponse
    import zipfile
    import tempfile
    from os.path import join, basename
    from glob import glob
    from kmos.io import import_xml, export_source

    # return HTTP download response (e.g. via django)
    response = HttpResponse(mimetype='application/x-zip-compressed')
    response['Content-Disposition'] = 'attachment; filename="kmos_export.zip"'

    if isinstance(project, basestring):
        project = import_xml(project)

    try:
        from cStringIO import StringIO
    except:
        from StringIO import StringIO
    stringio = StringIO()
    zfile = zipfile.ZipFile(stringio, 'w')

    # save XML
    zfile.writestr('project.xml', str(project))

    # generate source
    tempdir = tempfile.mkdtemp()
    srcdir = join(tempdir, 'src')

    # add kMC project sources
    export_source(project, srcdir)
    for srcfile in glob(join(srcdir, '*')):
        zfile.write(srcfile, join('src', basename(srcfile)))

    # add standalone kmos program
    # TODO

    # write temporary file to response
    zfile.close()
    stringio.flush()
    response.write(stringio.getvalue())
    stringio.close()
    return response
