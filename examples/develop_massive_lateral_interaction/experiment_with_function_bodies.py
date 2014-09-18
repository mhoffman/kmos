#!/usr/bin/env python

rate_constant = """N_CO_bridge = CO@bridge1 + CO@bridge2"
""
"""

import re
from textwrap import dedent
from StringIO import StringIO
from tokenize import generate_tokens

def evaluate_rate_function(rate_constant, **env):
    if not '\n' in rate_constant:
        return rate_constant

    r = dedent(rate_constant)

    # replace occupation expression with 1s and 0s.
    r = r.replace('@', '__AT__')
    r = re.sub(r'(\b[a-zA-Z_]*?__AT__.*?\b)', '{\\1}', r)
    r = r.format(**env)

    # replace return statements by a series of statements
    # which first replace as many variables using locals()
    # and return the rest.
    r = r.split('\n')
    for i, line in enumerate(r):
        if line.strip().startswith('return '):
            indent_level = len(line) - len(line.strip())
            ind = ' ' * indent_level
            expression = re.search('^\s*return\s*["\'](?P<expr>[^"\']*)["\']\s*$', line).groupdict()['expr']
            line = "%s__res__ = re.sub('(\\\\b%%s\\\\b)' %% r'\\b|\\b'.join(locals().keys()), '{\\\\1}', '%s')\n" % (ind, expression)
            line += '%s__res__ = __res__.format(**locals()); return __res__\n' % (' ' * indent_level)
            r[i] = line
    r = '\n'.join(r)

    # wrap as a function and execute resulting function definition
    r = r.replace('\n', '\n    ')
    r = 'def __rate__():\n' + r
    exec(r)

    # return the result of that function
    return __rate__()

if __name__ == '__main__':
    rate_constant = """
    import math
    N_CO_bridge = CO@bridge1 + CO@bridge2
    N_O_bridge = O@bridge1 + O@bridge2
    foo = 2
    beta = 3
    return "exp(-foo*beta*(V_OCO*N_CO_bridge+ V22*N_O_bridge))"
    """

    print(evaluate_rate_function('100'))
    print(evaluate_rate_function(rate_constant,
    **{
        'CO__AT__bridge1' : 1,
        'CO__AT__bridge2' : 1,
        'O__AT__bridge1': 0,
        'O__AT__bridge2': 3,
    }
    ))
