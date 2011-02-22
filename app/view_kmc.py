#!/usr/bin/python

import time
import threading
from copy import deepcopy

import pygtk
pygtk.require('2.0')
import gtk, gobject
import numpy as np

import ase.gui.ag
from ase.atoms import Atoms
from ase.gui.view import View
from ase.gui.images import Images
from ase.gui.status import Status
from ase.gui.defaults import read_defaults

from kmc import  base, lattice, proclist


gtk.gdk.threads_init()

class KMC_Model(threading.Thread):
    stopthread = threading.Event()
    def __init__(self, size=10, system_name='kmc_model'):
        super(KMC_Model, self).__init__()

        proclist.init((size,)*int(lattice.model_dimension),system_name, lattice.default_layer, proclist.default_species)
        self.cell_size = np.dot(lattice.unit_cell_size, lattice.system_size)
        self.species_representation = []
        # This clumsy loop is neccessary because f2py
        # can unfortunately only pass through one character
        # at a time and not strings
        for ispecies in range(len(proclist.species_representation)):
            repr = ''
            for jchar in range(proclist.representation_length):
                char = proclist.get_representation_char(ispecies+1, jchar+1)
                repr += char
            if repr.strip():
                self.species_representation.append(eval(repr))
            else:
                self.species_representation.append(None)

        if len(proclist.lattice_representation):
            self.lattice_representation = eval(''.join(proclist.lattice_representation))[0]
        else:
            self.lattice_representation = Atoms()



    def run(self):
        while not self.stopthread.isSet():
            gtk.gdk.threads_enter()
            proclist.do_kmc_step()
            gtk.gdk.threads_leave()

    def stop(self):
        self.stopthread.set()
        base.deallocate_system()

    def run_steps(self, n):
        for i in xrange(n):
            proclist.do_kmc_step()

    def get_atoms(self):
        atoms = ase.atoms.Atoms()
        atoms.set_cell(self.cell_size)
        for i in xrange(lattice.system_size[0]):
            for j in xrange(lattice.system_size[1]):
                for k in xrange(lattice.system_size[2]):
                    for n in xrange(1,1+lattice.spuck):
                        species = lattice.get_species([i,j,k,n]) - 1
                        if self.species_representation[species]:
                            atom = deepcopy(self.species_representation[species])
                            atom.translate(np.dot(lattice.unit_cell_size,
                            np.array([i,j,k]) + lattice.site_positions[n-1]))
                            atoms += atom
                    lattice_repr = deepcopy(self.lattice_representation)
                    lattice_repr.translate(np.dot(lattice.unit_cell_size,
                                np.array([i,j,k])))
                    atoms += lattice_repr
        
        return atoms


class FakeWidget():
    def __init__(self, path):
        self.active = False
        if path.endswith('ShowUnitCell'):
            self.active = True
        elif path.endswith('ShowBonds'):
            self.active = False
        elif path.endswith('ShowAxes'):
            self.active = True

    def get_active(self):
        return self.active

class FakeUI():
    """This is a fudge class to simulate to the View class a non-existing
    menu with included settings
    """
    def __init__(self):
        return self

    def get_widget(self, path):
        widget = FakeWidget(path)
        return widget

class KMC_ViewBox(threading.Thread, View, Images, Status,FakeUI):
    stopthread = threading.Event()
    def __init__(self, vbox, window, rotations='', show_unit_cell=True, show_bonds=False):
        super(KMC_ViewBox, self).__init__()
        self.configured = False
        self.ui = FakeUI.__init__(self)
        self.model = KMC_Model()
        self.model.run_steps(10000)
        self.images = Images()
        self.images.initialize([self.model.get_atoms()])

        self.vbox = vbox
        self.window = window

        self.vbox.connect('scroll-event',self.scroll_event)
        View.__init__(self, self.vbox, rotations)
        Status.__init__(self, self.vbox)
        self.vbox.show()

        self.drawing_area.realize()
        self.scale = 1.0
        self.center = self.model.get_atoms().cell.diagonal()*.5
        self.set_colors()
        self.set_coordinates(0)

        self.model.start()


    def update_vbox(self, atoms):
        self.images = Images()
        self.images.initialize([atoms])
        self.set_coordinates(0)
        self.draw()
        return False
        
    def run(self):
        while not self.stopthread.isSet():
            atoms = self.model.get_atoms()
            gobject.idle_add(self.update_vbox, atoms)
            time.sleep(0.05)

    def stop(self):
        self.model.stop()
        self.stopthread.set()
        
    
    def scroll_event(self, window, event):
        """Zoom in/out when using mouse wheel"""
        x = 1.0
        if event.direction == gtk.gdk.SCROLL_UP:
            x = 1.2
        elif event.direction == gtk.gdk.SCROLL_DOWN:
            x = 1.0 / 1.2
        self._do_zoom(x)

    def _do_zoom(self, x):
        """Utility method for zooming"""
        self.scale *= x
        self.draw()

class KMC_Viewer():
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.connect('delete-event',self.exit)
        
        self.vbox = gtk.VBox()
        self.window.add(self.vbox)
        self.kmc_viewbox = KMC_ViewBox(self.vbox, self.window)
        self.window.show()
        self.kmc_viewbox.start()


    def exit(self,widget,event):
        self.kmc_viewbox.stop()
        gtk.main_quit()
        return True


if __name__ == '__main__':
    gobject.threads_init()
    viewer = KMC_Viewer()
    gtk.main()
    
