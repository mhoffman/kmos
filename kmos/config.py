#!/usr/bin/env python
import os

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

APP_ABS_PATH = os.path.dirname(os.path.abspath(__file__))
GLADEFILE = os.path.join(APP_ABS_PATH, 'kmc_editor.glade')
GLADEFILE = 'kmos/kmc_editor.glade'
try:
    import kiwi
    kiwi.environ.environ.add_resource('glade', APP_ABS_PATH)
except:
    pass
