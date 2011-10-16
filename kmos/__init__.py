"""

"""

#    Copyright 2009-2011 Max J. Hoffmann (mjhoffmann@gmail.com)
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
            tokens = list(tokenize.generate_tokens(
                            StringIO.StringIO(rate_expr).readline))
        except:
            raise
        for i, token, _, _, _ in tokens:
            if token in ['sqrt', 'exp', 'sin', 'cos', 'pi', 'pow']:
                replaced_tokens.append((i, 'math.' + token))
            elif token in dir(units):
                replaced_tokens.append((i, str(eval('units.' + token))))
            elif token.startswith('m_'):
                species_name = '_'.join(token.split('_')[1:])
                symbols = string2symbols(species_name)
                replaced_tokens.append((i,
                            '%s' % sum([atomic_masses[atomic_numbers[symbol]]
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
                    parameter_str = parameter_str.replace(
                                    unit, '%s' % eval('units.%s' % unit))
                replaced_tokens.append((i, parameter_str))
            else:
                replaced_tokens.append((i, token))

        rate_expr = tokenize.untokenize(replaced_tokens)
        try:
            rate_const = eval(rate_expr)
        except Exception as e:
            raise UserWarning(
            "Could not evaluate rate expression: %s\nException: %s" \
                % (rate_expr, e))

    return rate_const
