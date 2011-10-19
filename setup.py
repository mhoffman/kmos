#!/usr/bin/python

from distutils.core import setup

maintainer = 'Max J. Hoffmann'
maintainer_email = 'mjhoffmann@gmail.com'
author = 'Max J. Hoffmann'
author_email = 'mjhoffmann@gmail.com'
description = "kMC modeling on steroids"
license = 'COPYING'
long_description = file('README.rst').read()
name='python-kmos'
packages = [
           'kmos',
           'kmos.pygtkcanvas',
           ]
package_dir = {'kmos':'kmos'}
package_data = {'kmos':['fortran_src/*f90',
                        'kmc_editor.glade',
                        'fortran_src/assert.ppc',
                        'kmc_project_v0.2.dtd']}
platforms = ['linux']
requires = ['kiwi', 'ase','lxml','matplotlib', 'pygtk', 'gtk']
scripts = [
        'tools/kmos-editor',
        'tools/kmos-export-program',
        'tools/kmos-build',
        'tools/kmos-view',
        'tools/kmos-build-standalone',
        'tools/kmos'
        ]
url = 'https://github.com/mhoffman/kmos'
version = '0.1'

setup(
      author=author,
      author_email=author_email,
      maintainer=maintainer,
      maintainer_email=maintainer_email,
      description=description,
      license=license,
      long_description=long_description,
      name=name,
      packages=packages,
      package_dir=package_dir,
      package_data=package_data,
      platforms=platforms,
      requires=requires,
      scripts=scripts,
      url=url,
      version=version,
      )
