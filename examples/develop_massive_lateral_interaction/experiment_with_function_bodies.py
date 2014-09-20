#!/usr/bin/env python

rate_constant = """N_CO_bridge = CO@bridge1 + CO@bridge2"
""
"""

import re
from textwrap import dedent
from io import StringIO
from tokenize import generate_tokens

def preprocess_rate_expression(rate_constant, **env):
    """
    This is a string preprocessing function for generating
    suitable rate constant expressions for a particular
    lateral interaction configuration. The syntax is
    the one of a python function (body) and should use
    indentation accordingly.  It may contain
    variables such as 'species@site' (without or without "'")
    as is used in the elementary step definition.
    Each resulting expression should be stated on it own single line
    initiated with a 'return' statement.

    During the evalution all 'species@site' are first replaced by 1 (True)
    or 0 (False) based on the current lateral interaction situation. Then
    a function body is evaluated and the variables in the returned expressions
    evaluated as much as possible based on the variable in the current scope.

    In general any python variable name can be used. However variable names
    starting and ending with a double-underscore (like __x__) are used for
    the evaluation and should be avoided.


    >>> preprocess_rate_expression('100')
    preprocess_rate_expression('100')
    <BLANKLINE>
    '100'

    >>> preprocess_rate_expression(
    ... \"\"\"
    ... N_CO = CO@bridge + CO@hollow
    ... N_O = O@bridge + O@hollow
    ... pref = "(kboltzmann*T)**(-1)"
    ... if O@site:
    ...     return "pref*exp(-beta*(E_Obind + N_O*V_O_O + N_CO*V_CO_O)*eV)"
    ... elif CO@site :
    ...     return "pref*exp(-beta*(E_Obind + N_O*V_CO_O + N_CO*V_CO_CO)*eV)"
    ... \"\"\", **{
    ... 'CO__AT__bridge' : True,
    ... 'CO__AT__hollow' : True,
    ... 'O__AT__bridge': False,
    ... 'O__AT__hollow' : True,
    ... 'O__AT__site' : False,
    ... 'CO__AT__site' : True,
    ... })
    preprocess_rate_expression(
    \"\"\"
    N_CO = CO@bridge + CO@hollow
    N_O = O@bridge + O@hollow
    pref = "(kboltzmann*T)**(-1)"
    if O@site:
        return "pref*exp(-beta*(E_Obind + N_O*V_O_O + N_CO*V_CO_O)*eV)"
    elif CO@site :
        return "pref*exp(-beta*(E_Obind + N_O*V_CO_O + N_CO*V_CO_CO)*eV)"
    \"\"\", **{
    'CO__AT__bridge' : True,
    'CO__AT__hollow' : True,
    'O__AT__bridge': False,
    'O__AT__hollow' : True,
    'O__AT__site' : False,
    'CO__AT__site' : True,
    })
    <BLANKLINE>
    '(kboltzmann*T)**(-1)*exp(-beta*(E_Obind + 1*V_CO_O + 2*V_CO_CO)*eV)'

    >>> preprocess_rate_expression(
    ... \"\"\"
    ... import math
    ... N_CO_bridge = CO@bridge1 + CO@bridge2
    ... N_O_bridge = O@bridge1 + O@bridge2
    ... foo = 2
    ... beta = 3
    ... if CO@bridge1 and CO@bridge2 :
    ...     return "exp(-foo*beta*(V_OCO*N_CO_bridge+ V22*N_O_bridge))"
    ... else:
    ...     return "foo"
    ... \"\"\" , **{
    ...     'CO__AT__bridge1' : 1,
    ...     'CO__AT__bridge2' : 1,
    ...     'O__AT__bridge1': 0,
    ...     'O__AT__bridge2': 3,
    ... })
    preprocess_rate_expression(
    \"\"\"
    import math
    N_CO_bridge = CO@bridge1 + CO@bridge2
    N_O_bridge = O@bridge1 + O@bridge2
    foo = 2
    beta = 3
    if CO@bridge1 and CO@bridge2 :
        return "exp(-foo*beta*(V_OCO*N_CO_bridge+ V22*N_O_bridge))"
    else:
        return "foo"
    \"\"\" , **{
        'CO__AT__bridge1' : 1,
        'CO__AT__bridge2' : 1,
        'O__AT__bridge1': 0,
        'O__AT__bridge2': 3,
    })
    <BLANKLINE>
    'exp(-2*3*(V_OCO*2+ V22*3))'




    """

    r = dedent(rate_constant)

    # replace occupation expression with 1s and 0s.
    r = r.replace('@', '__AT__')
    r = re.sub(r'(\b[a-zA-Z_]*?__AT__.*?\b)', '{\\1}', r)
    r = r.format(**env)

    # for a single line statement, don't look further
    if not '\n' in rate_constant:
        return rate_constant

    # replace return statements by a series of statements
    # which first replace as many variables using locals()
    # and return the rest.
    r = r.split('\n')
    for i, line in enumerate(r):
        if line.strip().startswith('return '):
            # determine current indentation level
            # for indenting replaced code correctly
            indent_level = len(line) - len(line.strip())
            ind = ' ' * indent_level
            # extract the returned expression
            expression = re.search('^\s*return\s*("|\'|""")(?P<expr>[^"\']*)("|\'|""")\s*$', line).groupdict()['expr']
            line = "%s__res__ = re.sub('(\\\\b%%s\\\\b)' %% r'\\b|\\b'.join(locals().keys()), '{\\\\1}', '%s')\n" % (ind, expression)
            line += '%s__res__ = __res__.format(**locals()); return __res__\n' % (' ' * indent_level)
            r[i] = line
    r = '\n'.join(r)

    # wrap as a function and execute resulting function definition
    r = r.replace('\n', '\n    ')
    r = 'def __rate__():\n' + r
    exec(r)

    # return the result of that function
    result =  __rate__()
    if result:
        return result
    else :
        raise Exception("""
                           The rate-constant function returned nothing.
                           Make sure every possible lateral interaction is treated.
                           Use 0 explicitly if that is the intention""")

if __name__ == '__main__':
    import doctest
    doctest.testmod()
