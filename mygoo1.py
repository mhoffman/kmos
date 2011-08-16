#!/usr/bin/python

import goocanvas
import gtk
import ase.io.castep
from ase.data.colors import jmol_colors
from ase.data import covalent_radii
from tempfile import NamedTemporaryFile
from math import pi

def rgba2dword(color):
    r, g, b, a = color
    color = (r << 24) | (g << 16) | (b << 8) | 1
    return hex(color)



class AtomicWindow():
    def __init__(self):
        self.win = gtk.Window()
        self.win.connect('destroy', gtk.main_quit)
        vbox = self.create_goo_vbox()
        self.win.add(vbox)
        self.win.show_all()
        self.upper_left = None
        self.lower_right = None

    def create_goo_vbox(self):
        vbox = gtk.VBox()
        vbox.set_border_width(4)
        canvas = goocanvas.Canvas()
        root = canvas.get_root_item()
        canvas.set_size_request(400,400)
        vbox.add(canvas)

        atoms = ase.io.castep.read_cell('layer2_OTF.cell')

        atoms.rotate('z',pi/2,rotate_cell=True)

        for atom in sorted(atoms, key=lambda x: x.position[2]):
            
            i = atom.number
            radius=15*covalent_radii[i]
            color = 256*jmol_colors[i]
            color = map(int, color)
            print(color)
            color = (color[0], color[1], color[2], 1.)
            color = rgba2dword(color)
            print(color)
            ellipse = goocanvas.Ellipse(parent=root,
                                        center_x=100+10*atom.position[0],
                                        center_y=100+10*atom.position[1],
                                        radius_x=radius,
                                        radius_y=radius,
                                        stroke_color='black',
                                        fill_color_rgba=color,
                                        line_width=3.0)


        return vbox



    def on_button_press(self, item, target, event):
        if self.upper_left is None:
            self.upper_left = (event.x, event.y)
        elif self.lower_right is None:
            self.lower_right = (event.x, event.y)
        else:
            pos_x = (event.x-self.upper_left[0])/(self.lower_right[0]-self.upper_left[0])
            pos_y = 1-(event.y-self.upper_left[1])/(self.lower_right[1]-self.upper_left[1])
            print('[%.3f, %.3f]' % (pos_x, pos_y))

def main():
        app = AtomicWindow()
        gtk.main()


if __name__ == '__main__':
    main()
