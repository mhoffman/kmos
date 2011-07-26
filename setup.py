#!/usr/bin/python

from distutils.core import setup

author = 'Max J. Hoffmann'
author_email = 'mjhoffmann@gmail.com'
data_files = [
             ('f90sources','f90sources/*'), 
        
             ]
description = "kMC modeling on steroids"
license = 'COPYING'
long_description = "A vigorous attempt to make lattice kinetic Monte Carlo modelling more accessible"
packages = [
           'kmos',
           'kmos.pygtkcanvas',
           ]
name='python-kmos'
package_dir = {'kmos':'kmos',
               }
platforms = ['linux']
scripts = [
        'tools/kmos-gui',
        'tools/kmos-export-src',
        'tools/kmos-build',
        'tools/kmos-f2py',
        ]
url = 'https://github.com/mhoffman/kmos'
version = '0.1'

setup(
      author=author,
      author_email=author_email,
      data_files=data_files,
      description=description,
      license=license,
      long_description=long_description,
      name=name,
      packages=packages,
      package_dir=package_dir,
      platforms=platforms,
      scripts=scripts,
      url=url,
      version=version,
      )

