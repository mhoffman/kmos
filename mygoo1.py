#!/usr/bin/python

import goocanvas
import gtk
import ase.io.castep
from ase.data import covalent_radii
from tempfile import NamedTemporaryFile
from math import pi

def jmolcolor_in_hex(i):
    from ase.data.colors import jmol_colors
    color = map(int, 255*jmol_colors[i])
    r, g, b = color
    a = 255
    color = (r << 24) | (g << 16) | (b << 8) | a

    return color

class AtomicWindow():
    def __init__(self):
        self.win = gtk.Window()
        self.upper_left = None
        self.lower_right = None
        self.radius_scale = 22
        self.scale = 20
        self.offset_x, self.offset_y = (100, 100)


        self.win.connect('destroy', gtk.main_quit)
        vbox = self.create_goo_vbox()
        self.win.add(vbox)
        self.win.show_all()


    def create_goo_vbox(self):
        vbox = gtk.VBox()
        vbox.set_border_width(4)
        canvas = goocanvas.Canvas()
        root = canvas.get_root_item()
        canvas.set_size_request(400,400)
        self.win.connect('button-press-event', self.on_button_press)
        vbox.add(canvas)

        atoms = ase.io.castep.read_cell('layer2_OTF.cell')

        for atom in sorted(atoms, key=lambda x: x.position[2]):
            
            i = atom.number
            radius = self.radius_scale*covalent_radii[i]
            color = jmolcolor_in_hex(i)

            ellipse = goocanvas.Ellipse(parent=root,
                                center_x=(self.offset_x+self.scale*atom.position[0]),
                                center_y=(self.offset_y+self.scale*atom.position[1]),
                                radius_x=radius,
                                radius_y=radius,
                                stroke_color='black',
                                fill_color_rgba=color,
                                line_width=1.0)
        cell = goocanvas.Rect(parent=root,
                              x=self.offset_x,
                              y=self.offset_y,
                              height=self.scale*atoms.cell[1,1],
                              width=self.scale*atoms.cell[0,0],
                              stroke_color='black',
                              )

        self.lower_left = (self.offset_x, self.offset_y+self.scale*atoms.cell[1,1])
        self.upper_right= (self.offset_x + self.scale*atoms.cell[0,0], self.offset_y)

        return vbox

    def on_button_press(self, item, event):
        pos_x = (event.x-self.lower_left[0])/(self.upper_right[0]-self.lower_left[0])
        pos_y = (event.y-self.lower_left[1])/(self.upper_right[1]-self.lower_left[1])
        print('[%.3f, %.3f]' % (pos_x, pos_y))

def main():
        app = AtomicWindow()
        gtk.main()

if __name__ == '__main__':
    main()
