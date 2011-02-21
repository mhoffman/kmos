#!/usr/bin/python

import pygtk
pygtk.require('2.0')
import gtk
import numpy as np

from run_kmc import KMC_Model
import ase.gui.ag
from ase.gui.view import View
from ase.gui.images import Images
from ase.gui.status import Status
from ase.gui.defaults import read_defaults


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


        
class KMC_Viewer(View, Images, Status,FakeUI):
    def __init__(self,rotations='',show_unit_cell=True, show_bonds=False):
        self.configured = False
        self.ui = FakeUI.__init__(self)
        self.model = KMC_Model()
        self.model.run_steps(10)
        self.images = Images()
        self.images.initialize([self.model.get_atoms()])
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.connect('delete-event',gtk.main_quit)
        self.window.connect('scroll-event',self.scroll_event)
        self.window.connect('key-press-event',self.step)

        self.vbox = gtk.VBox()
        self.window.add(self.vbox)

        View.__init__(self, self.vbox, rotations)
        Status.__init__(self, self.vbox)
        self.vbox.show()

        self.drawing_area.realize()
        self.scale = 1.0
        self.center = np.zeros(3)
        self.set_colors()
        self.set_coordinates(0)

        self.window.show()
        #self.draw()
        gtk.mainloop()



    def exit(self,widget,event):
        gtk.main_quit()
        return True


    def step(self, widget, event):
        self.model.run_steps(10)
        self.images = Images()
        self.images.initialize([self.model.get_atoms()])
        self.set_coordinates(0)
        self.draw()

    
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

if __name__ == '__main__':
    KMC_Viewer()
    
