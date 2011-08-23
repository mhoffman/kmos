"""
kmos is a vigorous attempt to make lattice kMC modelling more accessible.

This package features an XML format to define lattice-kMC models, a graphical
editor for these XML files, a tools which converts a project description into
compilable python/Fortran90 code and graphical front end to run and watch kMC simulations::

    kmos [help] (edit|view|export) [options]

kmos' goal is to significantly reduce the time you need
to implement and run a lattice kmc simulation. However it can not help
you plan the model. It is therefore highly recommend that you have clear
idea of your model before you start implementing it.

A good way to define a model is to use a paper and pencil to draw
your lattice, choose the species that you will need, draw
each process and write down an expression for each rate constant, and
finally fix all energy barriers and external parameters that you will need.
Putting a model prepared like this into a computer is a simple exercise.
You enter a new model by filling in

    * meta information
    * lattice
    * species
    * parameters
    * processes

in roughly this order or open an existing one by opening a kMC XML file.

If you want to see the model run
`kmos export <xml-file>` and you will get a subfolder with a self-contained
Fortran90 code, which solves the model. If all necessary dependencies are
installed you can simply run kmc view in the export folder.

kmos kMC project DTD
####################

.. literalinclude:: ../../kmos/kmc_project_v0.2.dtd
"""

import tokenize
import StringIO
import math
from kmos import units, species
from ase.data import atomic_numbers, atomic_masses
from ase.atoms import string2symbols

def evaluate_rate_expression(rate_expr, parameters={}):
    """Evaluates an expression for a typical kMC rate constant.
     External parameters can be passed in as dictionary, like the
     following:
        parameters = {'p_CO':{'value':1},
                      'T':{'value':1}}
     """
    if not rate_expr:
        rate_const = 0.0
    else:
        replaced_tokens = []

        # replace some aliases
        rate_expr = rate_expr.replace('beta', '(1./(kboltzmann*T))')
        try:
            tokens = list(tokenize.generate_tokens(StringIO.StringIO(rate_expr).readline))
        except:
            print('Trouble with expression: %s' % rate_expr)
            raise
        for i, token, _, _, _ in tokens:
            if token in ['sqrt','exp','sin','cos','pi','pow']:
                replaced_tokens.append((i,'math.'+token))
            elif token in dir(units):
                replaced_tokens.append((i, str(eval('units.' + token))))
            elif token.startswith('m_'):
                species_name = '_'.join(token.split('_')[1:])
                symbols = string2symbols(species_name)
                replaced_tokens.append((i, '%s' % sum([atomic_masses[atomic_numbers[symbol]]
                            for symbol in symbols])))
            elif token.startswith('mu_'):
                species_name = '_'.join(token.split('_')[1:])
                if species_name in dir(species):
                    replaced_tokens.append((i, 'species.%s.mu(%s,%s)' % (
                                   species_name,
                                   parameters['T']['value'],
                                   parameters['p_%s' % species_name]['value'],
                                   )))
                else:
                    print('No JANAF table assigned for %s' % species_name)
                    print('Setting chemical potential to zero')
                    replaced_tokens.append((i, '0'))
            elif token in parameters:
                parameter_str = str(parameters[token]['value'])
                # replace units used in parameters
                for unit in units.keys:
                    parameter_str = parameter_str.replace(unit, '%s' % eval('units.%s' % unit))
                replaced_tokens.append((i, parameter_str))
            else:
                replaced_tokens.append((i, token))

        rate_expr = tokenize.untokenize(replaced_tokens)
        try:
            rate_const = eval(rate_expr)
        except Exception as e:
            raise UserWarning("Could not evaluate rate expression: %s\nException: %s" % (rate_expr, e))

    return rate_const
