__all__ = ['Canvas']

import sys
import pygtk
pygtk.require("2.0")
import gtk
import gobject
import cairo
from math import pi
from canvasmath import *

def verbose(func):
        print >>sys.stderr,"monitor %r"%(func.func_name)
        def f(*args,**kwargs):
                print >>sys.stderr,"call(\033[0;31m%s.%s\033[0;30m): %r\n"%(type(args[0]).__name__,func.func_name,args[1 :]),
                sys.stderr.flush()
                ret=func(*args,**kwargs)
                print >>sys.stderr,"    ret(%s): \033[0;32m%r\033[0;30m\n"%(func.func_name,ret)
                return ret
        return f

class Canvas(gtk.DrawingArea):
    #@verbose
    def __init__(self):
		gtk.DrawingArea.__init__(self)
		self.set_double_buffered(False)
		self.add_events(
			gtk.gdk.BUTTON_PRESS_MASK| 
			gtk.gdk.BUTTON_RELEASE_MASK| 
			gtk.gdk.BUTTON1_MOTION_MASK| 
			gtk.gdk.BUTTON2_MOTION_MASK| 
			gtk.gdk.BUTTON3_MOTION_MASK| 
			gtk.gdk.SCROLL_MASK| 
			gtk.gdk.KEY_PRESS_MASK| 
			gtk.gdk.KEY_RELEASE_MASK)
		
		# foregorund, background
		self.fg = (0.9, 0.9, 0.9)
		self.bg = (0.5, 0.5, 0.5)
		
		# list of layers
		self.layers = []
		
		# visible are used for speedup as list
		self.visible = None
		
		# canvas bindings
		self.bindings = {}
		
		# last item which had some event
		self.current_item = None
		
		# cairo context
		self.cr = None
		
		# cached cairo image surfaces using filenames/images as keys
		self.cache_filenames = {}
		self.cache_images = {}
		
		# connect event callbacks
		gtk.DrawingArea.connect(self, 'configure-event', self.drawingarea_configure_event_cb)
		gtk.DrawingArea.connect(self, 'expose-event', self.drawingarea_expose_event_cb)
		gtk.DrawingArea.connect(self, 'button-press-event', self.drawingarea_button_press_event_cb)
		gtk.DrawingArea.connect(self, 'button-release-event', self.drawingarea_button_release_event_cb)
		gtk.DrawingArea.connect(self, 'motion-notify-event', self.drawingarea_motion_notify_event_cb)
		gtk.DrawingArea.connect(self, 'scroll-event', self.drawingarea_scroll_event_cb)
	
    #@verbose
    def connect(self, detailed_signal, handler, *args, **kw):
		# makes sure that all event names have '-' but nor '_'
		detailed_signal = detailed_signal.replace('_', '-')
		if detailed_signal not in self.bindings:
			self.bindings[detailed_signal] = [(handler, args, kw)]
		else:
			self.bindings[detailed_signal].append((handler, args, kw))
	
    #@verbose
    def drawingarea_configure_event_cb(self, widget, event):
		x, y, width, height = self.get_allocation()
		self.pixmap = gtk.gdk.Pixmap(self.window, width, height)
		self.gc = self.window.new_gc()
		self.visible = self.find_visible(*self.get_allocation())
		return True
	
    #@verbose
    def drawingarea_expose_event_cb(self, widget, event):
		self.redraw_visible()
		return False
	
    #@verbose
    def drawingarea_button_press_event_cb(self, widget, event):
		self.event_cb(widget, event, 'button-press-event')
		return False
	
    #@verbose
    def drawingarea_motion_notify_event_cb(self, widget, event):
		self.event_cb(widget, event, 'motion-notify-event')
		return False
	
    #@verbose
    def drawingarea_button_release_event_cb(self, widget, signal_id):
		self.event_cb(widget, signal_id, 'button-release-event')
		return False
	
    #@verbose
    def drawingarea_scroll_event_cb(self, widget, event):
		self.event_cb(widget, event, 'scroll-event')
		return False
	
    #@verbose
    def event_cb(self, widget, event, name):
		# check if canvas_item already 'pressed'
		# this reduces time required for finding
		# over which item mouse is above
		if self.current_item:
			try:
				func_, args_, kw_ = self.current_item.bindings[name]
				func_(self, self.current_item, event, *args_, **kw_)
			except KeyError:
				pass
				
			if name == 'button-press-event':
				self.visible = self.find_visible(*self.get_allocation())
			elif name == 'motion-notify-event':
				self.redraw_visible()
			elif name == 'button-release-event':
				self.current_item = None
			
		# classical way for finding where is mouse above
		else:
			x = event.x
			y = event.y
			for n in reversed(self.visible):
				bindings = n.bindings
				if bindings and name in bindings:
					if n.is_coord_above(x, y):
						func_, args_, kw_ = bindings[name]
						func_(self, n, event, *args_, **kw_)
						self.current_item = n
						break
			
			if not self.current_item:
				try:
					for handler_, args_, kw_ in self.bindings[name]:
						handler_(widget, event, *args_, **kw_)
				except KeyError:
					pass
				
				self.visible = self.find_visible(*self.get_allocation())
				
			self.redraw_visible()

    def redraw(self):
        self.visible = self.find_visible(*self.get_allocation())
        self.redraw_visible()

    #@verbose
    def redraw_visible(self):
		# cairo context
		self.cr = cr = self.pixmap.cairo_create()
		
		# clip
		xmin, ymin = 0, 0
		xmax, ymax = tuple(self.get_allocation())[2:]
		cr.rectangle(xmin, ymin, xmax, ymax)
		cr.clip()
		
		# background
		cr.set_source_rgb(0.5, 0.5, 0.5)
		cr.rectangle(xmin, ymin, xmax, ymax)
		cr.fill()
		
		# draw items
		for item in self.visible:
			item.draw(cr)
		
		# draw on canvas
		self.window.draw_drawable(self.gc, self.pixmap, xmin, ymin, xmin, ymin, xmax-xmin, ymax-ymin)
	
    #@verbose
    def set_foreground(self, color):
		self.fg = color
	
    #@verbose
    def set_background(self, color):
		self.bg = color
	
    #@verbose
    def draw_line(self, x0, y0, x1, y1, fg=None, line_width=1.0):
		cr = self.cr
		cr.move_to(x0, y0)
		cr.line_to(x1, y1)
		
		cr.set_line_width(line_width)
		cr.set_source_rgb(*(fg if fg else self.fg))
		cr.stroke()
	
    #@verbose
    def draw_rect(self, x0, y0, x1, y1, fg=None, bg=None, outline=False, line_width=1.0, filled=False):
		cr = self.cr
		x = x0
		y = y0
		w = x1 - x0
		h = y1 - y0
		
		if filled:
			cr.rectangle(x, y, w, h)
			cr.set_source_rgb(*(bg if bg else self.bg))
			cr.fill()
			
			if not outline:
				return
		
		cr.rectangle(x, y, w, h)
		cr.set_line_width(line_width)
		cr.set_source_rgb(*(fg if fg else self.fg))
		cr.stroke()
		
    #@verbose
    def draw_oval(self, x0, y0, x1, y1, fg=None, bg=None, outline=False, line_width=1.0, filled=False):
		cr = self.cr
		x2 = (x0 + x1) / 2.0
		y2 = (y0 + y1) / 2.0
		w2 = (x1 - x0) / 2.0
		h2 = (y1 - y0) / 2.0
		pi2 = 2.0 * pi
		
		if filled:
			cr.save()
			cr.translate(x2, y2)
			cr.scale(w2, h2)
			cr.arc(0.0, 0.0, 1.0, 0.0, 2 * pi)
			cr.restore()
			cr.set_source_rgb(*(bg if bg else self.bg))
			cr.fill()
			
			if not outline:
				return
		
		cr.save()
		cr.translate(x2, y2)
		cr.scale(w2, h2)
		cr.arc(0.0, 0.0, 1.0, 0.0, 2 * pi)
		cr.restore()
		cr.set_line_width(line_width)
		cr.set_source_rgb(*(fg if fg else self.fg))
		cr.stroke()
		
    #@verbose
    def draw_arc(self, x0, y0, x1, y1, fg=None, bg=None, outline=False, line_width=1.0, filled=False, start=0.0, extent=1.5 * pi):
		cr = self.cr
		x2 = (x0 + x1) / 2.0
		y2 = (y0 + y1) / 2.0
		w2 = (x1 - x0) / 2.0
		h2 = -(y1 - y0) / 2.0
		
		if filled:
			cr.save()
			cr.translate(x2, y2)
			cr.scale(w2, h2)
			cr.arc(0.0, 0.0, 1.0, start, extent)
			cr.restore()
			cr.set_source_rgb(*(bg if bg else self.bg))
			cr.fill()
			
			if not outline:
				return
		
		cr.save()
		cr.translate(x2, y2)
		cr.scale(w2, h2)
		cr.arc(0.0, 0.0, 1.0, start, extent)
		cr.restore()
		cr.set_line_width(line_width)
		cr.set_source_rgb(*(fg if fg else self.fg))
		cr.stroke()
		
    #@verbose
    def draw_text(self, x0, y0, text, fg=None, size=10):
		cr = self.cr
		cr.set_font_size(size)
		cr.move_to(x0, y0 + size)
		cr.set_source_rgb(*(fg if fg else self.fg))
		cr.show_text(text)
	
    #@verbose
    def draw_image(self, x0, y0, xs=1.0, ys=1.0, filename=None, image=None):
		cr = self.cr
		cr.save()
		cr.translate(x0, y0)
		cr.scale(xs, ys)
		
		if filename:
			if filename not in self.cache_filenames:
				cairo_image = cairo_image_surface_from_filename(filename)
				self.cache_filenames[filename] = cairo_image
			else:
				cairo_image = self.cache_filenames[filename]
		elif image:
			if image not in self.cache_images:
				cairo_image = cairo_image_surface_from_image(image)
				self.cache_images[image] = cairo_image
			else:
				cairo_image = self.cache_images[image]
		
		cr.set_source_surface(cairo_image)
		cr.paint()
		cr.restore()
	
    #@verbose
    def append(self, layer):
		self.layers.append(layer)
	
    #@verbose
    def insert(self, index, layer):
		self.layers.insert(index, layer)
	
    #@verbose
    def remove(self, layer):
		self.layers.remove(layer)
	
    #@verbose
    def pop(self, index):
		return self.layers.pop(index)
	
    #@verbose
    def move_all(self, dx, dy):
		for layer in self.layers:
			layer.move_all(dx, dy)
	
    #@verbose
    def scale_all(self, xc, yc, xs, ys):
		for layer in self.layers:
			layer.scale_all(xc, yc, xs, ys)
	
    #@verbose
    def find_above(self, item):
		l = []
		for layer in self.layers:
			if layer.get_visible():
				l.extend(layer.find_above(item))
		return l
		
    #@verbose
    def find_all_above(self, item):
		l = []
		for layer in self.layers:
			if layer.get_visible():
				l.extend(layer.find_all_above(item))
		return l
		
    #@verbose
    def find_below(self, item):
		l = []
		for layer in self.layers:
			if layer.get_visible():
				l.extend(layer.find_below(item))
		return l
		
    #@verbose
    def find_all_below(self, item):
		l = []
		for layer in self.layers:
			if layer.get_visible():
				l.extend(layer.find_all_below(item))
		return l
	
    #@verbose
    def find_visible(self, x0, y0, x1, y1):
		l = []
		for layer in self.layers:
			if layer.get_visible():
				l.extend(layer.find_visible(x0, y0, x1, y1))
		return l
	
    #@verbose
    def find_closest(self, x, y, halo=0, start=None, end=None):
		l = []
		for layer in self.layers:
			if layer.get_visible():
				l.extend(layer.find_closest(x0, y0, x1, y1))
		return l
		
    #@verbose
    def find_enclosed(self, x0, y0, x1, y1):
		l = []
		for layer in self.layers:
			if layer.get_visible():
				l.extend(layer.find_enclosed(x0, y0, x1, y1))
		return l
		
    #@verbose
    def find_overlapping(self, x0, y0, x1, y1):
		l = []
		for layer in self.layers:
			if layer.get_visible():
				l.extend(layer.find_overlapping(x0, y0, x1, y1))
		return l
