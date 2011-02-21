#!/usr/bin/python

import time
import threading
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


        
class KMC_Viewer(threading.Thread, View, Images, Status,FakeUI,):
    stopthread = threading.Event()
    def __init__(self,rotations='',show_unit_cell=True, show_bonds=False):
        super(KMC_Viewer, self).__init__()
        self.configured = False
        self.ui = FakeUI.__init__(self)
        self.model = KMC_Model()
        self.model.run_steps(10000)
        self.images = Images()
        self.images.initialize([self.model.get_atoms()])
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.connect('delete-event',self.exit)
        self.window.connect('scroll-event',self.scroll_event)

        self.vbox = gtk.VBox()
        self.window.add(self.vbox)

        View.__init__(self, self.vbox, rotations)
        Status.__init__(self, self.vbox)
        self.vbox.show()

        self.drawing_area.realize()
        self.scale = 1.0
        self.center = self.model.get_atoms().cell.diagonal()*.5
        self.set_colors()
        self.set_coordinates(0)

        self.window.show()



    def run(self):
        while not self.stopthread.isSet():
            self.images = Images()
            gtk.gdk.threads_enter()
            self.images.initialize([self.model.get_atoms()])
            gtk.gdk.threads_leave()
            self.set_coordinates(0)
            self.draw()
            time.sleep(0.1)
    def stop(self):
        self.stopthread.set()
        
    def exit(self,widget,event):
        self.model.stop()
        gtk.main_quit()
        return True



    
    def scroll_event(self, window, event):
        """Zoom in/out when using mouse wheel"""
        x = 1.0
        if event.direction == gtk.gdk.SCROLL_UP:
            x = 1.2
        elif event.direction == gtk.gdk.SCROLL_DOWN:
            x = 1.0 / 1.2
        gtk.gdk.threads_enter()
        self._do_zoom(x)
        gtk.gdk.threads_leave()

    def _do_zoom(self, x):
        """Utility method for zooming"""
        self.scale *= x
        self.draw()



if __name__ == '__main__':
    gtk.gdk.threads_init()
    viewer = KMC_Viewer()
    viewer.start()
    viewer.model.start()
    gtk.main()
    
