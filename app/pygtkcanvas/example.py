#!/usr/bin/env python
import pygtk
pygtk.require('2.0')
import gtk
from random import randrange, random


from canvas import Canvas
from canvaslayer import CanvasLayer
from canvasitem import *

def verbose(func):
        print >>sys.stderr,"monitor %r"%(func.func_name)
        def f(*args,**kwargs):
                print >>sys.stderr,"call(\033[0;31m%s.%s\033[0;30m): %r\n"%(type(args[0]).__name__,func.func_name,args[1 :]),
                sys.stderr.flush()
                ret=func(*args,**kwargs)
                print >>sys.stderr,"    ret(%s): \033[0;32m%r\033[0;30m\n"%(func.func_name,ret)
                return ret
        return f
class Window:
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete-event", self.delete_event_cb)
        self.window.connect("destroy", self.destroy_cb)
        self.window.set_border_width(0)
        self.window.set_size_request(800, 600)
        self.window.show()

        self.canvas = Canvas()
        self.canvas.set_flags(gtk.HAS_FOCUS|gtk.CAN_FOCUS)
        self.canvas.grab_focus()

        self.layer1 = CanvasLayer()
        self.layer2 = CanvasLayer()
        self.canvas.append(self.layer1)
        self.canvas.append(self.layer2)
        self.canvas.show()
        self.window.add(self.canvas)

        for n in xrange(2):
            o = CanvasRect(self.layer1, 100, 100, 200, 200, filled=True)
            o.scale(random(), random(), random(), random())
            o.move(randrange(1000), randrange(1000))
            o.connect('button-press-event', self.button_press_event_cb)
            o.connect('motion-notify-event', self.motion_notify_event_cb)
            o.connect('button-release-event', self.button_release_event_cb)

        for n in xrange(5):
            g = CanvasGroup(self.layer1, fg=gtk.gdk.color_parse('#ffffff'))
            o = CanvasLine(g, 0, 0, 100, 100)
            o = CanvasRect(g, 0, 100, 100, 200)
            o = CanvasOval(g, 0, 200, 100, 300)
            o = CanvasArc(g, 0, 300, 100, 400, start=0, extent=180)
            o = CanvasText(g, 0, 400, text='Hello')
            o = CanvasLine(g, 100, 0, 200, 100)
            o = CanvasRect(g, 100, 100, 200, 200, filled=True, outline=True)
            o = CanvasOval(g, 100, 200, 200, 300, filled=True)
            o = CanvasArc(g, 100, 300, 200, 400, start=90, extent=270, filled=True)
            o = CanvasText(g, 100, 400, text='World')
            g.scale(random(), random(), random(), random())
            g.move(randrange(1000), randrange(1000))
            g.connect('button-press-event', self.button_press_event_cb)
            g.connect('motion-notify-event', self.motion_notify_event_cb)
            g.connect('button-release-event', self.button_release_event_cb)

        o = CanvasImage(self.layer1, 0, 0, filename='image2.jpeg')
        o.connect('button-press-event', self.button_press_event_cb)
        o.connect('motion-notify-event', self.motion_notify_event_cb)
        o.connect('button-release-event', self.button_release_event_cb)

        o = CanvasImage(self.layer1, 100, 100, filename='image1.png')
        o.connect('button-press-event', self.button_press_event_cb)
        o.connect('motion-notify-event', self.motion_notify_event_cb)
        o.connect('button-release-event', self.button_release_event_cb)

        o = CanvasFunc(self.layer1, target=self.canvas_func1, args=(), kw={})

        self.canvas_button = None
        self.item = None
        self.item_prev_x = None
        self.item_prev_y = None
        self.item_button = None

        self.window.connect('key-press-event', self.window_key_press_event_cb)
        self.window.connect('key-release-event', self.window_key_release_event_cb)
        self.canvas.connect('button-press-event', self.canvas_button_press_event_cb)
        self.canvas.connect('motion-notify-event', self.canvas_motion_notify_event_cb)
        self.canvas.connect('button-release-event', self.canvas_button_release_event_cb)
        self.canvas.connect('scroll-event', self.canvas_scroll_event_cb)

    def delete_event_cb(self, widget, event, data=None):
        return False

    def destroy_cb(self, widget, data=None):
        gtk.main_quit()

    def main(self):
        gtk.main()

    def button_press_event_cb(self, widget, item, event):
            if isinstance(item, CanvasImage):
                coords = item.get_coords()
                o = CanvasImage(self.layer1, coords[0], coords[1], filename='image1.png')
                o.connect('button-press-event', self.button_press_event_cb)
                o.connect('motion-notify-event', self.motion_notify_event_cb)
                o.connect('button-release-event', self.button_release_event_cb)
                self.canvas.drawingarea_button_press_event_cb(self.canvas, event)
            self.item = item
            self.item_prev_x = event.x
            self.item_prev_y = event.y
            self.item_button = event.button

    def motion_notify_event_cb(self, widget, item, event):
        if self.item_button == 1:
            dx = event.x - self.item_prev_x
            dy = event.y - self.item_prev_y
            self.item.move(dx, dy)
            self.item_prev_x = event.x
            self.item_prev_y = event.y

    def button_release_event_cb(self, widget, item, signal_id):
        self.item_button = None

    def canvas_button_press_event_cb(self, widget, event):
        self.canvas_button = event.button
        if self.canvas_button == 2:
            self.canvas_prev_x = event.x
            self.canvas_prev_y = event.y

    def canvas_motion_notify_event_cb(self, widget, event):
        if self.canvas_button == 2:
            dx = event.x - self.canvas_prev_x
            dy = event.y - self.canvas_prev_y
            self.canvas.move_all(dx, dy)
            self.canvas_prev_x = event.x
            self.canvas_prev_y = event.y

    def canvas_button_release_event_cb(self, widget, signal_id):
        self.canvas_button = None

    def canvas_scroll_event_cb(self, widget, event):
        if event.direction == gtk.gdk.SCROLL_UP:
            self.canvas.scale_all(event.x, event.y, 2.0, 2.0)
        elif event.direction == gtk.gdk.SCROLL_DOWN:
            self.canvas.scale_all(event.x, event.y, 0.5, 0.5)

    def window_key_press_event_cb(self, widget, event):
        print widget, event

    def window_key_release_event_cb(self, widget, event):
        print widget, event

    def canvas_func1(self, *args, **kw):
        self.canvas.draw_image(0, 0, xs=1.0, ys=1.0, filename='image2.jpeg')
        self.canvas.draw_line(0, 0, 100, 100)
        self.canvas.draw_rect(0, 100, 100, 200)
        self.canvas.draw_oval(0, 200, 100, 300)
        self.canvas.draw_arc(0, 300, 100, 400)
        self.canvas.draw_text(0, 400, "Hello World")

if __name__ == "__main__":
    win = Window()
    win.main()
