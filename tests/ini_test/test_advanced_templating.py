#!/usr/bin/env python

from os.path import dirname, join

def test_advanced_templating():
    from kmos.utils import evaluate_template
    with open(join(dirname(__file__), 'pairwise_interaction.ini')) as infile:
        ini = infile.read()
        
    print(evaluate_template(ini, escape_python=True))

if __name__ == '__main__':
    test_advanced_templating()
