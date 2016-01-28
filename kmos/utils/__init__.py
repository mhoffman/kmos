#!/usr/bin/env python
"""Several utility functions that do not seem to fit somewhere
   else.
"""
#    Copyright 2009-2013 Max J. Hoffmann (mjhoffmann@gmail.com)
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

from __future__ import with_statement
from time import time
from StringIO import StringIO
from kmos.utils.ordered_dict import OrderedDict

ValidationError = UserWarning
try:
    from kiwi.datatypes import ValidationError
except:
    print('kiwi Validation not working.')

FCODE = """module kind
implicit none
contains
subroutine real_kind(p, r, kind_value)
  integer, intent(in), optional :: p, r
  integer, intent(out) :: kind_value

  if(present(p).and.present(r)) then
    kind_value = selected_real_kind(p=p, r=r)
  else
    if (present(r)) then
      kind_value = selected_real_kind(r=r)
    else
      if (present(p)) then
        kind_value = selected_real_kind(p)
      endif
    endif
  endif
end subroutine real_kind

subroutine int_kind(p, r, kind_value)
  integer, intent(in), optional :: p, r
  integer, intent(out) :: kind_value

  if(present(p).and.present(r)) then
    kind_value = selected_int_kind(p)
  else
    if (present(r)) then
      kind_value = selected_int_kind(r=r)
    else
      if (present(p)) then
        kind_value = selected_int_kind(p)
      endif
    endif
  endif
end subroutine int_kind

end module kind
"""

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
        if hasattr(image, 'get_chemical_formula'):
            chemical_formula = image.get_chemical_formula(mode='reduce')
        else:
            chemical_formula = image.get_name()

        fileobj.write("    Atoms(symbols='%s',\n"
                      "          pbc=np.%s,\n"
                      "          cell=np.array(\n      %s,\n" % (
            chemical_formula,
            repr(image.pbc),
            repr(image.cell)[6:]))

        if not scaled_positions:
            fileobj.write("          positions=np.array(\n      %s),\n"
                % repr(list(image.positions)))
        else:
            fileobj.write("          scaled_positions=np.array(\n      %s),\n"
                % repr(list(image.get_scaled_positions().tolist())))
        fileobj.write('),\n')

    fileobj.write(']')


def get_ase_constructor(atoms):
    """Return the ASE constructor string for `atoms`."""
    if isinstance(atoms, basestring):
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
    #astr = astr[:-2]
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


def evaluate_kind_values(infile, outfile):
    """Go through a given file and dynamically
    replace all selected_int/real_kind calls
    with the dynamically evaluated fortran code
    using only code that the function itself
    contains.

    """
    import re
    import os
    import sys
    import shutil
    sys.path.append(os.path.abspath(os.curdir))

    with open(infile) as infh:
        intext = infh.read()
    if not ('selected_int_kind' in intext.lower()
            or 'selected_real_kind' in intext.lower()):
        shutil.copy(infile, outfile)
        return


    def import_selected_kind():
        """Tries to import the module which provides
        processor dependent kind values. If the module
        is not available it is compiled from a here-document
        and imported afterwards.

        Warning: creates both the source file and the
        compiled module in the current directory.

        """
        try:
            import f2py_selected_kind
        except:
            from numpy.f2py import compile
            # quick'n'dirty workaround for windoze
            if os.name == 'nt':
                f = open('f2py_selected_kind.f90', 'w')
                f.write(FCODE)
                f.close()
                from copy import deepcopy
                # save for later
                true_argv = deepcopy(sys.argv)
                sys.argv = (('%s -c --fcompiler=gnu95 --compiler=mingw32'
                             ' -m f2py_selected_kind'
                             ' f2py_selected_kind.f90')
                             % sys.executable).split()
                from numpy import f2py as f2py2e
                f2py2e.main()

                sys.argv = true_argv
            else:
                fcompiler = os.environ.get('F2PY_FCOMPILER', 'gfortran')
                compile(FCODE, source_fn='f2py_selected_kind.f90',
                        modulename='f2py_selected_kind',
                        extra_args='--fcompiler=%s' % fcompiler)
            try:
                import f2py_selected_kind
            except:
                raise Exception('Could create selected_kind module\n'
                + '%s\n' % os.path.abspath(os.curdir)
                + '%s\n' % os.listdir('.'))
        return f2py_selected_kind.kind

    def parse_args(args):
        """
            Parse the arguments for selected_(real/int)_kind
            to pass them on to the Fortran module.

        """
        in_args = [x.strip() for x in args.split(',')]
        args = []
        kwargs = {}

        for arg in in_args:
            if '=' in arg:
                symbol, value = arg.split('=')
                kwargs[symbol] = eval(value)
            else:
                args.append(eval(arg))

        return args, kwargs

    def int_kind(args):
        """Python wrapper around Fortran selected_int_kind
        function.
        """
        args, kwargs = parse_args(args)
        return import_selected_kind().int_kind(*args, **kwargs)

    def real_kind(args):
        """Python wrapper around Fortran selected_real_kind
        function.
        """
        args, kwargs = parse_args(args)
        return import_selected_kind().real_kind(*args, **kwargs)

    infile = file(infile)
    outfile = file(outfile, 'w')
    int_pattern = re.compile((r'(?P<before>.*)selected_int_kind'
                              '\((?P<args>.*)\)(?P<after>.*)'),
                              flags=re.IGNORECASE)
    real_pattern = re.compile((r'(?P<before>.*)selected_real_kind'
                                '\((?P<args>.*)\)(?P<after>.*)'),
                              flags=re.IGNORECASE)

    for line in infile:
        real_match = real_pattern.match(line)
        int_match = int_pattern.match(line)
        if int_match:
            match = int_match.groupdict()
            line = '%s%s%s\n' % (
                    match['before'],
                    int_kind(match['args']),
                    match['after'],)
        elif real_match:
            match = real_match.groupdict()
            line = '%s%s%s\n' % (
                    match['before'],
                    real_kind(match['args']),
                    match['after'],)
        outfile.write(line)
    infile.close()
    outfile.close()


def build(options):
    """Build binary with f2py binding from complete
    set of source file in the current directory.

    """

    from os.path import isfile
    import os
    import sys
    from glob import glob

    src_files = ['kind_values_f2py.f90', 'base.f90', 'lattice.f90']

    if isfile('proclist_constants.f90'): #
        src_files.append('proclist_constants.f90')
    src_files.extend(glob('nli_*.f90'))
    src_files.extend(glob('run_proc_*.f90'))
    src_files.append('proclist.f90')

    extra_flags = {}

    if options.no_optimize:
        extra_flags['gfortran'] = ('-ffree-line-length-none -ffree-form'
                                   ' -xf95-cpp-input -Wall -fimplicit-none')
        extra_flags['gnu95'] = extra_flags['gfortran']
        extra_flags['intel'] = '-fpp -Wall -I/opt/intel/fc/10.1.018/lib'
        extra_flags['intelem'] = '-fpp -Wall'

    else:
        extra_flags['gfortran'] = ('-ffree-line-length-none -ffree-form'
                                   ' -xf95-cpp-input -Wall -O3 -fimplicit-none')
        extra_flags['gnu95'] = extra_flags['gfortran']
        extra_flags['intel'] = '-fast -fpp -Wall -I/opt/intel/fc/10.1.018/lib'
        extra_flags['intelem'] = '-fast -fpp -Wall'

    # FIXME
    extra_libs = ''
    ccompiler = ''
    if os.name == 'nt':
        ccompiler = '--compiler=mingw32'
        if sys.version_info < (2, 7):
            extra_libs = ' -lmsvcr71 '
        else:
            extra_libs = ' -lmsvcr90 '

    module_name = 'kmc_model'

    if not isfile('kind_values_f2py.f90'):
        evaluate_kind_values('kind_values.f90', 'kind_values_f2py.f90')

    for src_file in src_files:
        if not isfile(src_file):
            raise IOError('File %s not found' % src_file)

    call = []
    call.append('-c')
    call.append('-c')
    call.append('--fcompiler=%s' % options.fcompiler)
    if os.name == 'nt':
        call.append('%s' % ccompiler)
    extra_flags = extra_flags.get(options.fcompiler, '')

    if options.debug:
        extra_flags += ' -DDEBUG'
    call.append('--f90flags="%s"' % extra_flags)
    call.append('-m')
    call.append(module_name)
    call += src_files

    print(call)
    from copy import deepcopy
    true_argv = deepcopy(sys.argv)  # save for later
    from numpy import f2py
    sys.argv = call
    f2py.main()
    sys.argv = true_argv


def T_grid(T_min, T_max, n):
    from numpy import linspace, array
    """Return a list of n temperatures between
       T_min and T_max such that the grid of T^(-1)
       is evenly spaced.
    """

    T_min1 = T_min ** (-1.)
    T_max1 = T_max ** (-1.)

    grid = list(linspace(T_max1, T_min1, n))
    grid.reverse()
    grid = [x ** (-1.) for x in grid]

    return array(grid)


def p_grid(p_min, p_max, n):
    from numpy import logspace, log10
    """Return a list of n pressures between
       p_min and p_max such that the grid of log(p)
       is evenly spaced.
    """
    p_minlog = log10(p_min)
    p_maxlog = log10(p_max)

    grid = logspace(p_minlog, p_maxlog, n)

    return grid


def timeit(func):
    """
    Generic timing decorator

    To stop time for function call f
    just ::
        from kmos.utils import timeit
        @timeit
        def f():
            ...

     """
    def wrapper(*args, **kwargs):
        time0 = time()
        func(*args, **kwargs)
        print('Executing %s took %.3f s' % (func.__name__, time() - time0))
    return wrapper


def col_tuple2str(tup):
    """Convenience function that turns a HTML type color
    into a tuple of three float between 0 and 1
    """
    r, g, b = tup
    b *= 255
    res = '#'
    res += hex(int(255 * r))[-2:].replace('x', '0')
    res += hex(int(255 * g))[-2:].replace('x', '0')
    res += hex(int(255 * b))[-2:].replace('x', '0')

    return res


def col_str2tuple(hex_string):
    """Convenience function that turns a HTML type color
    into a tuple of three float between 0 and 1
    """
    import gtk
    color = gtk.gdk.Color(hex_string)
    return (color.red_float, color.green_float, color.blue_float)


def jmolcolor_in_hex(i):
    """Return a given jmol color in hexadecimal representation."""
    from ase.data.colors import jmol_colors
    color = [int(x) for x in 255 * jmol_colors[i]]
    r, g, b = color
    a = 255
    color = (r << 24) | (g << 16) | (b << 8) | a
    return color

def evaluate_param_expression(param, parameters={}):
    import tokenize
    import StringIO
    import math
    from kmos import units

    # convert parameters to dict if passed as list of Parameters()
    if type(parameters) is list:
        param_dict = {}
        for parameter in parameters:
            param_dict[parameter.name] = {'value': parameter.value}
        parameters = param_dict

    parameter_str = str(parameters[param]['value'])

    # replace some aliases
    parameter_str = parameter_str.replace('beta', '(1./(kboltzmann*T))')
    # replace units used in parameters
    for unit in units.keys:
        parameter_str = parameter_str.replace(
                        unit, '%s' % eval('units.%s' % unit))
    try:
        return eval(parameter_str)
    except:
        try:
            replaced_tokens=[]
            input = StringIO.StringIO(parameter_str).readline
            tokens = list(tokenize.generate_tokens(input))
        except:
            raise Exception('Could not tokenize expression: %s' % input)
        for i, token, _, _, _ in tokens:
            if token in ['sqrt', 'exp', 'sin', 'cos', 'pi', 'pow', 'log']:
                replaced_tokens.append((i, 'math.' + token))
            elif token.startswith('GibbsGas_'):
                #evaluate gas phase gibbs free energy using ase thermochemistry module,
                #experimental data from NIST CCCBDB, the electronic energy 
                #and current temperature and partial pressure
                from kmos import species
                species_name = '_'.join(token.split('_')[1:])
                if species_name in dir(species):
                    if not 'T' in parameters:
                        raise Exception('Need "T" in parameters to evaluate gas phase gibbs free energy.')

                    if not ('p_%s' % species_name) in parameters:
                        raise Exception('Need "p_%s" in parameters to evaluate gas phase gibbs free energy.' % species_name)

                    replaced_tokens.append((i, 'species.%s.GibbsGas(%s,%s,%s)' % (
                                species_name,
                                parameters['E_'+species_name]['value'],
                                parameters['T']['value'],
                                parameters['p_%s' % species_name]['value'],
                                )))
                else:
                    print('No NIST data assigned for %s' % species_name)
                    print('Setting chemical potential to zero')
                    replaced_tokens.append((i, '0'))

                #gibbs=eval(replaced_tokens2[-1][-1])
                #print species_name+': %.3f'%gibbs

            elif token.startswith('GibbsAds_'):
                #evaluate gibbs free energy of adsorbate using ase thermochemistry module,
                #calculated frequencies and electronic energy and current temperature
                from kmos import species
                species_name = '_'.join(token.split('_')[1:])
                if not 'T' in parameters:
                    raise Exception('Need "T" in parameters to evaluate adsorbate gibbs free energy.')
                energy=parameters['E_'+species_name]['value']
                try:
                    eval(energy)
                except:
                    try:
                        replaced_tokens2=[]
                        input = StringIO.StringIO(energy).readline
                        tokens2 = list(tokenize.generate_tokens(input))
                    except:
                        raise Exception('Could not tokenize expression: %s' % input)
                    for j, token2, _, _, _ in tokens2:
                        if token2 in parameters:
                            parameter_str2 = str(parameters[token2]['value'])
                            try:
                                eval(parameter_str2)
                                replaced_tokens2.append((j, parameter_str2))
                            except:
                                try:
                                    input = StringIO.StringIO(parameter_str2).readline
                                    tokens3 = list(tokenize.generate_tokens(input))
                                except:
                                    raise Exception('Could not tokenize expression: %s' % input)
                                for k, token3, _, _, _ in tokens3:
                                    if token3 in parameters:
                                        parameter_str3 = str(parameters[token3]['value'])
                                        replaced_tokens2.append((k, parameter_str3))
                                    else:
                                        replaced_tokens2.append((k, token3))
                        else:
                            replaced_tokens2.append((j, token2))
                    energy = tokenize.untokenize(replaced_tokens2)
                replaced_tokens.append((i, 'species.GibbsAds(%s,%s,%s)' % (
                            energy,
                            parameters['f_'+species_name]['value'],
                            parameters['T']['value'],
                            )))

                #gibbs=eval(replaced_tokens2[-1][-1])
                #print species_name+': %.3f'%gibbs

            elif token in parameters:
                replaced_tokens.append((i, str(parameters[token]['value'])))
            else:
                replaced_tokens.append((i, token))
        parameter_str = tokenize.untokenize(replaced_tokens)
        return eval(parameter_str)
        #print parameter_str
        #print token+': %.7f'%eval(parameter_str)

def evaluate_rate_expression(rate_expr, parameters={}):
    """Evaluates an expression for a typical kMC rate constant.
     External parameters can be passed in as dictionary, like the
     following:
        parameters = {'p_CO':{'value':1},
                      'T':{'value':1}}

     or as a list of parameters:
        parameters = [Parameter(), ... ]
     """
    import tokenize
    import StringIO
    import math
    from kmos import units

    # convert parameters to dict if passed as list of Parameters()
    if type(parameters) is list:
        param_dict = {}
        for parameter in parameters:
            param_dict[parameter.name] = {'value': parameter.value}
        parameters = param_dict

    if not rate_expr:
        rate_const = 0.0
    else:
        replaced_tokens = []

        # replace some aliases
        rate_expr = rate_expr.replace('beta', '(1./(kboltzmann*T))')
        try:
            input = StringIO.StringIO(rate_expr).readline
            tokens = list(tokenize.generate_tokens(input))
        except:
            raise Exception('Could not tokenize expression: %s' % input)
        for i, token, _, _, _ in tokens:
            if token in ['sqrt', 'exp', 'sin', 'cos', 'pi', 'pow', 'log']:
                replaced_tokens.append((i, 'math.' + token))
            elif token in dir(units):
                replaced_tokens.append((i, str(eval('units.' + token))))
            elif token.startswith('m_'):
                from ase.atoms import string2symbols
                from ase.data import atomic_masses
                from ase.data import atomic_numbers
                species_name = '_'.join(token.split('_')[1:])
                symbols = string2symbols(species_name)
                replaced_tokens.append((i,
                            '%s' % sum([atomic_masses[atomic_numbers[symbol]]
                            for symbol in symbols])))
            elif token.startswith('mu_'):
                # evaluate gas phase chemical potential if among
                # available JANAF tables if from current temperature
                # and corresponding partial pressure
                from kmos import species
                species_name = '_'.join(token.split('_')[1:])
                if species_name in dir(species):
                    if not 'T' in parameters:
                        raise Exception('Need "T" in parameters to evaluate chemical potential.')

                    if not ('p_%s' % species_name) in parameters:
                        raise Exception('Need "p_%s" in parameters to evaluate chemical potential.' % species_name)

                    replaced_tokens.append((i, 'species.%s.mu(%s,%s)' % (
                                   species_name,
                                   parameters['T']['value'],
                                   parameters['p_%s' % species_name]['value'],
                                   )))
                else:
                    print('No JANAF table assigned for %s' % species_name)
                    print('Setting chemical potential to zero')
                    replaced_tokens.append((i, '0'))

            elif token.startswith('GibbsGas_'):
                #evaluate gas phase gibbs free energy using ase thermochemistry module,
                #experimental data from NIST CCCBDB, the electronic energy 
                #and current temperature and partial pressure
                from kmos import species
                species_name = '_'.join(token.split('_')[1:])
                if species_name in dir(species):
                    if not 'T' in parameters:
                        raise Exception('Need "T" in parameters to evaluate gas phase gibbs free energy.')

                    if not ('p_%s' % species_name) in parameters:
                        raise Exception('Need "p_%s" in parameters to evaluate gas phase gibbs free energy.' % species_name)

                    replaced_tokens.append((i, 'species.%s.GibbsGas(%s,%s,%s)' % (
                                   species_name,
                                   parameters['E_'+species_name]['value'],
                                   parameters['T']['value'],
                                   parameters['p_%s' % species_name]['value'],
                                   )))
                else:
                    print('No NIST data assigned for %s' % species_name)
                    print('Setting chemical potential to zero')
                    replaced_tokens.append((i, '0'))

                #gibbs=eval(replaced_tokens[-1][-1])
                #print species_name+': %.3f'%gibbs

            elif token.startswith('GibbsAds_'):
                #evaluate gibbs free energy of adsorbate using ase thermochemistry module,
                #calculated frequencies and electronic energy and current temperature
                from kmos import species
                species_name = '_'.join(token.split('_')[1:])
                if not 'T' in parameters:
                    raise Exception('Need "T" in parameters to evaluate adsorbate gibbs free energy.')
                energy=parameters['E_'+species_name]['value']
                try:
                    eval(energy)
                except:
                    try:
                        replaced_tokens2=[]
                        input = StringIO.StringIO(energy).readline
                        tokens2 = list(tokenize.generate_tokens(input))
                    except:
                        raise Exception('Could not tokenize expression: %s' % input)
                    for j, token2, _, _, _ in tokens2:
                        if token2 in parameters:
                            parameter_str = str(parameters[token2]['value'])
                            try:
                                eval(parameter_str)
                                replaced_tokens2.append((j, parameter_str))
                            except:
                                try:
                                    input = StringIO.StringIO(parameter_str).readline
                                    tokens3 = list(tokenize.generate_tokens(input))
                                except:
                                    raise Exception('Could not tokenize expression: %s' % input)
                                for k, token3, _, _, _ in tokens3:
                                    if token3 in parameters:
                                        parameter_str = str(parameters[token3]['value'])
                                        replaced_tokens2.append((k, parameter_str))
                                    else:
                                        replaced_tokens2.append((k, token3))
                        else:
                            replaced_tokens2.append((j, token2))
                    energy = tokenize.untokenize(replaced_tokens2)
                replaced_tokens.append((i, 'species.GibbsAds(%s,%s,%s)' % (
                               energy,
                               parameters['f_'+species_name]['value'],
                               parameters['T']['value'],
                               )))

                #gibbs=eval(replaced_tokens[-1][-1])
                #print species_name+': %.3f'%gibbs

            elif token in parameters:
                parameter_str = str(parameters[token]['value'])
                # replace some aliases
                parameter_str = parameter_str.replace('beta', '(1./(kboltzmann*T))')
                # replace units used in parameters
                for unit in units.keys:
                    parameter_str = parameter_str.replace(
                                    unit, '%s' % eval('units.%s' % unit))
                try:
                    eval(parameter_str)
                    replaced_tokens.append((i, parameter_str))
                except:
                    try:
                        replaced_tokens2=[]
                        input = StringIO.StringIO(parameter_str).readline
                        tokens2 = list(tokenize.generate_tokens(input))
                    except:
                        raise Exception('Could not tokenize expression: %s' % input)
                    for i, token2, _, _, _ in tokens2:
                        if token2 in ['sqrt', 'exp', 'sin', 'cos', 'pi', 'pow', 'log']:
                            replaced_tokens2.append((i, 'math.' + token2))
                        elif token2.startswith('GibbsGas_'):
                            #evaluate gas phase gibbs free energy using ase thermochemistry module,
                            #experimental data from NIST CCCBDB, the electronic energy 
                            #and current temperature and partial pressure
                            from kmos import species
                            species_name = '_'.join(token2.split('_')[1:])
                            if species_name in dir(species):
                                if not 'T' in parameters:
                                    raise Exception('Need "T" in parameters to evaluate gas phase gibbs free energy.')

                                if not ('p_%s' % species_name) in parameters:
                                    raise Exception('Need "p_%s" in parameters to evaluate gas phase gibbs free energy.' % species_name)

                                replaced_tokens2.append((i, 'species.%s.GibbsGas(%s,%s,%s)' % (
                                            species_name,
                                            parameters['E_'+species_name]['value'],
                                            parameters['T']['value'],
                                            parameters['p_%s' % species_name]['value'],
                                            )))
                            else:
                                print('No NIST data assigned for %s' % species_name)
                                print('Setting chemical potential to zero')
                                replaced_tokens2.append((i, '0'))

                            #gibbs=eval(replaced_tokens2[-1][-1])
                            #print species_name+': %.3f'%gibbs

                        elif token2.startswith('GibbsAds_'):
                            #evaluate gibbs free energy of adsorbate using ase thermochemistry module,
                            #calculated frequencies and electronic energy and current temperature
                            from kmos import species
                            species_name = '_'.join(token2.split('_')[1:])
                            if not 'T' in parameters:
                                raise Exception('Need "T" in parameters to evaluate adsorbate gibbs free energy.')
                            energy=parameters['E_'+species_name]['value']
                            try:
                                eval(energy)
                            except:
                                try:
                                    replaced_tokens3=[]
                                    input = StringIO.StringIO(energy).readline
                                    tokens3 = list(tokenize.generate_tokens(input))
                                except:
                                    raise Exception('Could not tokenize expression: %s' % input)
                                for j, token3, _, _, _ in tokens3:
                                    if token3 in parameters:
                                        parameter_str = str(parameters[token3]['value'])
                                        try:
                                            eval(parameter_str)
                                            replaced_tokens3.append((j, parameter_str))
                                        except:
                                            try:
                                                input = StringIO.StringIO(parameter_str).readline
                                                tokens4 = list(tokenize.generate_tokens(input))
                                            except:
                                                raise Exception('Could not tokenize expression: %s' % input)
                                            for k, token4, _, _, _ in tokens4:
                                                if token4 in parameters:
                                                    parameter_str = str(parameters[token4]['value'])
                                                    replaced_tokens3.append((k, parameter_str))
                                                else:
                                                    replaced_tokens3.append((k, token4))
                                    else:
                                        replaced_tokens3.append((j, token3))
                                energy = tokenize.untokenize(replaced_tokens3)
                            replaced_tokens2.append((i, 'species.GibbsAds(%s,%s,%s)' % (
                                        energy,
                                        parameters['f_'+species_name]['value'],
                                        parameters['T']['value'],
                                        )))

                            #gibbs=eval(replaced_tokens2[-1][-1])
                            #print species_name+': %.3f'%gibbs

                        elif token2 in parameters:
                            replaced_tokens2.append((i, str(parameters[token2]['value'])))
                        else:
                            replaced_tokens2.append((i, token2))
                    parameter_str = tokenize.untokenize(replaced_tokens2)

                    #print parameter_str
                    #print token+': %.7f'%eval(parameter_str)

                    replaced_tokens.append((i, parameter_str))
            else:
                replaced_tokens.append((i, token))

        rate_expr = tokenize.untokenize(replaced_tokens)
        try:
            rate_const = eval(rate_expr)
        except Exception, e:
            raise UserWarning(
            "Could not evaluate rate expression: %s\nException: %s" \
                % (rate_expr, e))

    return rate_const
