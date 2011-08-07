#!/usr/bin/python

import tokenize
import StringIO
import math
from kmos import units

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
            elif token.startswith('mu_'):
                species_name = '_'.join(token.split('_')[1:])
                replaced_tokens.append((i, '0'))
            elif token in parameters:
                replaced_tokens.append((i, str(parameters[token]['value'])))
            else:
                replaced_tokens.append((i, token))

        rate_expr = tokenize.untokenize(replaced_tokens)
        try:
            rate_const = eval(rate_expr)
        except Exception as e:
            raise UserWarning("Could not evaluate rate expression: %s\nException: %s" % (rate_expr, e))

    return rate_const
