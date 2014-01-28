#!/usr/bin/env python
"""kMC modeling on steroids"""

import os
from distutils.core import setup
from kmos import __version__ as version

maintainer = 'Max J. Hoffmann'
maintainer_email = 'mjhoffmann@gmail.com'
author = 'Max J. Hoffmann'
author_email = 'mjhoffmann@gmail.com'
description =  __doc__
classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Operating System :: POSIX :: Windows',
        'Programming Language :: Fortran',
        'Programming Language :: Python',
        'Topic :: Education',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Visualization',
              ]
requires = [
                    'ase',
                    'cairo',
                    'gobject',
                    'goocanvas',
                    'gtk',
                    'kiwi',
                    'lxml',
                    'matplotlib',
                    'pygtk',
                   ]
license = 'COPYING'
long_description = file('README.rst').read()
name='python-kmos'
packages = [
           'kmos',
           'kmos.utils',
           'kmos.gui',
           ]
package_dir = {'kmos':'kmos'}
package_data = {'kmos':['fortran_src/*f90',
                        'kmc_editor.glade',
                        'fortran_src/assert.ppc',
                        'kmc_project_v0.1.dtd',
                        'kmc_project_v0.2.dtd']}
platforms = ['linux', 'windows']
if os.name == 'nt':
    scripts = [
            'tools/kmos.bat'
            ]
else:
    scripts = [
            'tools/kmos-build-standalone',
            'tools/kmos',
            'tools/kmos-install-dependencies-ubuntu',
            ]
url = 'https://github.com/mhoffman/kmos'

setup(
      author=author,
      author_email=author_email,
      description=description,
      #requires=requires,
      license=license,
      long_description=long_description,
      maintainer=maintainer,
      maintainer_email=maintainer_email,
      name=name,
      package_data=package_data,
      package_dir=package_dir,
      packages=packages,
      platforms=platforms,
      #requires=requires,
      scripts=scripts,
      url=url,
      version=version,
      )
