#!/usr/bin/env python
import pygtk
pygtk.require('2.0')
import gtk
from random import randrange, random


from canvas import Canvas
from canvaslayer import CanvasLayer
from canvasitem import *
R_MAG = 20
N = 100
R_ACTION = 10
R_COND = 15
DEFAULT_COL = (1., 1., 1.)

class Window:
    def __init__(self, species_list):
        self.species_list = species_list
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete-event", self.delete_event_cb)
        self.window.connect("destroy", self.destroy_cb)
        self.window.set_border_width(0)
        self.window.set_size_request(800, 600)
        self.window.show()


        self.canvas = Canvas()
        self.canvas.set_flags(gtk.HAS_FOCUS | gtk.CAN_FOCUS)
        self.canvas.grab_focus()
        self.lattice_layer = CanvasLayer()
        self.condition_layer = CanvasLayer()
        self.action_layer = CanvasLayer()
        self.motion_layer = CanvasLayer()
        self.canvas.append(self.lattice_layer)
        self.canvas.append(self.condition_layer)
        self.canvas.append(self.action_layer)
        self.canvas.append(self.motion_layer)
        self.canvas.show()
        self.window.add(self.canvas)

        for i in range(0, 800 / N) :
            lx = CanvasLine(self.lattice_layer,i*N,1*N,i*N,600, bg=(0.,0.,0.))
        for j in range(1, 600 / N) :
            ly = CanvasLine(self.lattice_layer, 0*N, j*N, 800, j*N, bg=(0., 0., 0.))
        k = 0
        for species in self.species_list:
            if species is not self.species_list.default:
                color = gtk.gdk.Color(species.color)
                color = (color.red_float, color.green_float, color.blue_float)
                o = CanvasOval(self.lattice_layer, 50+k*50, 20, k*50+80, 50, filled=True, bg=color)
                o.connect('button-press-event', self.button_press_event_cb)
                o.connect('motion-notify-event', self.motion_notify_event_cb)
                o.connect('button-release-event', self.button_release_event_cb)
                o.initial = True
                o.set_radius(10)
                k += 1
            else:
                color = gtk.gdk.Color(species.color)
                color = (color.red_float, color.green_float, color.blue_float)
                self.default_color = color

        self.item = None
        self.item_prev = None
        self.item_button = None

        self.window.connect('key-press-event', self.window_key_press_event_cb)
        self.window.connect('key-release-event', self.window_key_release_event_cb)
        self.canvas.connect('button-press-event', self.canvas_button_press_event_cb)
        self.canvas.connect('motion-notify-event', self.canvas_motion_notify_event_cb)
        self.canvas.connect('button-release-event', self.canvas_button_release_event_cb)


    def set_process(self, process):
        self.process = process

    def update_visible(self):
        pass

    def delete_event_cb(self, widget, event, data=None):
        return False

    def destroy_cb(self, widget, data=None):
        gtk.main_quit()
	
    def main(self):
        gtk.main()

    def button_press_event_cb(self, widget, item, event):
        print('PRESS')
        if event.button == 3 :
            item.delete()
            self.canvas.redraw()
        elif event.button == 1 :
            coords = item.get_coords()
            o = CanvasOval(self.motion_layer, *coords, filled=True, bg=(.3,0.3,0.3))
            o.connect('button-press-event', self.button_press_event_cb)
            o.connect('motion-notify-event', self.motion_notify_event_cb)
            o.connect('button-release-event', self.button_release_event_cb)
            self.canvas.visible = self.canvas.find_visible(*self.canvas.get_allocation())
            self.canvas.redraw_visible()
            self.item = o
            self.item.father = item

            self.item_prev = self.item.get_center()
            self.item_button = event.button


    def motion_notify_event_cb(self, widget, item, event):
        if self.item_button == 1 :
            center = int(event.x+R_MAG/2), int(event.y+R_MAG/2)
            # more general: if is_on_site
            if abs(center[0] % N) < R_MAG and abs(center[1] % N) < R_MAG :
                grid_center = N*(center[0]/N),N*(center[1]/N)
                item_center = self.item.get_center()
                d = [ int(x - y) for (x, y) in zip(grid_center, item_center) ]
                self.item.move(*d)
                self.item_prev = self.item.get_center()
            else:
                d = event.x - self.item_prev[0],event.y - self.item_prev[1]
                self.item.move(*d)
                self.item_prev = event.x, event.y


    def button_release_event_cb(self, widget, item, event):
        print('RELEASE')
        #print(dir(self.canvas))
        if self.item_button == 1 :
            center = int(event.x+R_MAG/2), int(event.y+R_MAG/2)
            center = int(event.x+R_MAG/2), int(event.y+R_MAG/2)
            if abs(center[0] % N) < R_MAG and abs(center[1] % N) < R_MAG :
                if hasattr(self.item.father, 'initial'):
                    # set new condition
                    self.item.new_parent(self.condition_layer)
                    self.item.bg = (.0,0.3,0.)
                    self.item.bg = self.item.father.bg
                    self.item.set_radius(R_COND)
                    self.item.outline = True
                else:
                    # diffusion event
                    self.item.delete()
                    if event.y > 100 :
                        coords = self.item.get_coords()
                        new_cond = CanvasOval(self.condition_layer, *coords, filled=True, bg=self.default_color)
                        new_cond.finalized = True
                        new_cond.set_radius(R_COND)
                        new_cond.connect('button-press-event', self.button_press_event_cb)
                        new_cond.connect('motion-notify-event', self.motion_notify_event_cb)
                        new_cond.connect('button-release-event', self.button_release_event_cb)

                        new_action = CanvasOval(self.action_layer, *coords, filled=True, outline=True, bg=self.item.father.bg)
                        new_action.finalized = True
                        new_action.finalized = True
                        new_action.finalized = True
                        new_action.set_radius(R_ACTION)
                        new_action.connect('button-press-event', self.button_press_event_cb)
                        new_action.connect('motion-notify-event', self.motion_notify_event_cb)
                        new_action.connect('button-release-event', self.button_release_event_cb)
                    coords = self.item.father.get_coords()
                    old_action = CanvasOval(self.condition_layer, *coords, filled=True, bg=self.default_color)
                    old_action.set_radius(R_ACTION)
                    old_action.finalized = True
                    old_action.connect('button-press-event', self.button_press_event_cb)
                    old_action.connect('motion-notify-event', self.motion_notify_event_cb)
                    old_action.connect('button-release-event', self.button_release_event_cb)
                    self.item.parent.finalized = True

            else:
                if event.y < 100 :
                    coords = self.item.father.get_coords()
                    old_action = CanvasOval(self.condition_layer, *coords, filled=True, bg=self.default_color)
                    old_action.set_radius(R_ACTION)
                    old_action.finalized = True
                    old_action.connect('button-press-event', self.button_press_event_cb)
                    old_action.connect('motion-notify-event', self.motion_notify_event_cb)
                    old_action.connect('button-release-event', self.button_release_event_cb)
                    
                elif hasattr(self.item.father,'finalized'):
                    for item in self.condition_layer + self.action_layer:
                        if item.get_coords() == self.item.father.get_coords():
                            print("ITEM",item)
                            item.delete()
                elif hasattr(self.item,'father') and not hasattr(self.item.father,'initial'):
                    print("FATHER",self.item.father)
                    self.item.father.delete()
                self.item.delete()
        self.canvas.redraw()
            


    def canvas_button_press_event_cb(self, widget, event):
        pass

    def canvas_motion_notify_event_cb(self, widget, event):
        pass

    def canvas_button_release_event_cb(self, widget, signal_id):
        pass


    def window_key_press_event_cb(self, widget, event):
        pass

    def window_key_release_event_cb(self, widget, event):
        pass

class Attributes:
    attributes = []
    def __init__(self, **kwargs):
        for attribute in self.attributes:
            if kwargs.has_key(attribute):
                self.__dict__[attribute] = kwargs[attribute]
        for key in kwargs:
            if key not in self.attributes:
                raise AttributeError, 'Tried to initialize illegal attribute'
    def __setattr__(self, attrname, value):
        if attrname in self.attributes:
            self.__dict__[attrname] = value
        else:
            raise AttributeError, 'Tried to initialize illegal attribute'

class Species(Attributes):
    attributes = ['name', 'color', 'id', 'default']
    def __init__(self, **kwargs):
        Attributes.__init__(self, **kwargs)


class SpeciesList(list):
    def __init__(self):
        list.__init__(self)
        self.default = None

    def set_default(self, species):
        self.default = species


if __name__ == "__main__":
    species_list = SpeciesList()
    empty = Species(name='empty,',color='#fff', id=0)
    species_list.append(empty)
    species_list.append(Species(name='oxygen',color='#c00',id='1'))
    species_list.append(Species(name='co',color='#00c',id='2'))
    species_list.append(Species(name='nitrogen',color='#0c0',id='3'))
    species_list.set_default(empty)

    win = Window(species_list)
    win.main()
