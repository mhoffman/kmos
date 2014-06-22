"""
Feature overview
================
With kmos you can:

    * easily create and modify kMC models through GUI
    * store and exchange kMC models through XML
    * generate fast, platform independent, self-contained code [#code]_
    * run kMC models through GUI or python bindings

kmos has been developed in the context of first-principles based modelling
of surface chemical reactions but might be of help for other types of
kMC models as well.

kmos' goal is to significantly reduce the time you need
to implement and run a lattice kmc simulation. However it can not help
you plan the model.


kmos can be invoked directly from the command line in one of the following
ways::

    kmos [help] (all|benchmark|build|edit|export|export-settings|help|import|rebuild|run|view) [options]

or it may be used as an API via the kmos module.

.. rubric:: Footnotes

.. [#code] The source code is generated in Fortran90, written in a modular
            fashion. Python bindings are generated using `f2py  <http://cens.ioc.ee/projects/f2py2e/>`_.
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


#import kmos.types
#import kmos.io

__version__ = "0.3.9"
VERSION = __version__


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
            elif token in parameters:
                parameter_str = str(parameters[token]['value'])
                # replace units used in parameters
                for unit in units.keys:
                    parameter_str = parameter_str.replace(
                                    unit, '%s' % eval('units.%s' % unit))
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
