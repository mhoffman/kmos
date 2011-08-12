__all__ = ['CanvasItem', 'CanvasLine', 'CanvasRect', 'CanvasOval',
'CanvasArc', 'CanvasText', 'CanvasImage', 'CanvasFunc', 'CanvasGroup']

import sys
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

class CanvasItem(object):
    def __init__(self, parent, *args, **kw):
        # parent as CanvasLayer or CanvasGroup
        self.parent = parent
        self.parent.append(self)

        # coords as list
        self.coords = map(float, args[0]) if args else None

        # bindings as dict
        self.bindings = None

        # properties as bool
        self.visible = kw['visible'] if 'visible' in kw else True


    def delete(self):
        self.parent.remove(self)
    def new_parent(self, new_parent):
        self.parent.remove(self)
        new_parent.append(self)
        self.parent = new_parent

    def set_coords(self, *args):
        self.coords = map(float, args)

    def get_coords(self):
        return self.coords[:]

    def get_center(self):
        return (self.coords[2]+self.coords[0])/2, (self.coords[3]+self.coords[1])/2

    def set_center(self, *args):
        if len(args) == 1 :
            center = args
        elif len(args) == 2 :
            center = args[0], args[1]
        else:
            raise TypeError, "Expected either 1 or 2 arguments, got %s" % len(args)
            
        old_center = self.get_center()
        x = center[0] - old_center[0]
        y = center[1] - old_center[1]
        self.move(x, y)

    def get_bbox(self):
        x0, y0, x1, y1 = self.coords

        if x0<x1:
            if y0<y1:
                return x0, y0, x1, y1
            else:
                return x1, y0, x0, y1
        else:
            if y0<y1:
                return x0, y1, x1, y0
            else:
                return x1, y1, x0, y0

    def connect(self, event_name, func, *args, **kw):
        self.bindings = self.bindings if self.bindings else {}
        self.bindings[event_name] = (func, args, kw)

    def disconnect(self, event_name):
        del self.bindings[event_name]
        if not self.bindings:
            self.bindings = None

    def move(self, dx, dy):
        coords = self.coords
        coords[0] += dx
        coords[1] += dy
        coords[2] += dx
        coords[3] += dy

    def scale(self, xc, yc, xs, ys):
        coords = self.coords
        coords[0] = ((coords[0] - xc) * xs) + xc
        coords[1] = ((coords[1] - yc) * ys) + yc
        coords[2] = ((coords[2] - xc) * xs) + xc
        coords[3] = ((coords[3] - yc) * ys) + yc

    def rotate(self, xc, yc, angle):
        pass

    def draw(self, *args, **kw):
        pass

    def is_coord_above(self, x, y):
        pass

class CanvasLine(CanvasItem):
    def __init__(self, parent, *args, **kw):
        CanvasItem.__init__(self, parent, *args, **kw)
        self.fg = kw['fg'] if 'fg' in kw else (0.9, 0.9, 0.9)
        self.line_width = kw['line_width'] if 'line_width' in kw else 1.0

    def draw(self, cr):
        x0, y0, x1, y1 = self.coords
        cr.move_to(x0, y0)
        cr.line_to(x1, y1)

        # set additional attributes, and draw
        cr.set_line_width(self.line_width)
        cr.set_source_rgb(*self.fg)
        cr.stroke()

    def is_coord_above(self, x, y):
        return inline2d(self.get_bbox(), x, y)

class CanvasRect(CanvasItem):
    def __init__(self, parent, *args, **kw):
        CanvasItem.__init__(self, parent, *args, **kw)
        self.fg = kw['fg'] if 'fg' in kw else (0.9, 0.9, 0.9)
        self.bg = kw['bg'] if 'bg' in kw else (0.7, 0.7, 0.7)
        self.line_width = kw['line_width'] if 'line_width' in kw else 1.0
        self.filled = kw['filled'] if 'filled' in kw else False
        self.outline = kw['outline'] if 'outline' in kw else False

    def draw(self, cr):
        x0, y0, x1, y1 = self.coords
        x = x0
        y = y0
        w = x1 - x0
        h = y1 - y0

        if self.filled:
            cr.rectangle(x, y, w, h)

            cr.set_source_rgb(*self.bg)
            cr.fill()

            if not self.outline:
                return

        cr.rectangle(x, y, w, h)

        # set additional attributes, and draw
        cr.set_line_width(self.line_width)
        cr.set_source_rgb(*self.fg)
        cr.stroke()

    def is_coord_above(self, x, y):
        return inrect2d(self.get_bbox(), x, y, filled=self.filled)


class CanvasOval(CanvasItem):
    def __init__(self, parent, *args, **kw):
        CanvasItem.__init__(self, parent, *args, **kw)
        self.fg = kw['fg'] if 'fg' in kw else (0.9, 0.9, 0.9)
        self.bg = kw['bg'] if 'bg' in kw else (0.7, 0.7, 0.7)
        self.line_width = kw['line_width'] if 'line_width' in kw else 1.0
        self.filled = kw['filled'] if 'filled' in kw else False
        self.outline = kw['outline'] if 'outline' in kw else False

    def draw(self, cr):
        x0, y0, x1, y1 = self.coords
        x2 = (x0 + x1) / 2.0
        y2 = (y0 + y1) / 2.0
        w2 = (x1 - x0) / 2.0
        h2 = (y1 - y0) / 2.0
        pi2 = 2.0 * pi

        if self.filled:
            cr.save()
            cr.translate(x2, y2)
            cr.scale(w2, h2)
            cr.arc(0.0, 0.0, 1.0, 0.0, 2 * pi)
            cr.restore()

            cr.set_source_rgb(*self.bg)
            cr.fill()

            if not self.outline:
                return

        cr.save()
        cr.translate(x2, y2)
        cr.scale(w2, h2)
        cr.arc(0.0, 0.0, 1.0, 0.0, 2 * pi)
        cr.restore()

        # set additional attributes, and draw
        cr.set_line_width(self.line_width)
        cr.set_source_rgb(*self.fg)
        cr.stroke()

    def is_coord_above(self, x, y):
        # FIXME: fix and use 'inoval2d'
        return inrect2d(self.get_bbox(), x, y, filled=True)

    def set_radius(self, radius):
        center = self.get_center()
        self.set_coords(center[0]-radius, center[1]-radius, center[0]+radius, center[1]+radius)


class CanvasArc(CanvasItem):
    def __init__(self, parent, *args, **kw):
        CanvasItem.__init__(self, parent, *args, **kw)
        self.fg = kw['fg'] if 'fg' in kw else (0.9, 0.9, 0.9)
        self.bg = kw['bg'] if 'bg' in kw else (0.7, 0.7, 0.7)
        self.line_width = kw['line_width'] if 'line_width' in kw else 1.0
        self.filled = kw['filled'] if 'filled' in kw else False
        self.outline = kw['outline'] if 'outline' in kw else False
        self.start = kw['start'] * (pi / 180.0) if 'start' in kw else 0.0
        self.extent = kw['extent'] * (pi / 180.0) if 'extent' in kw else 270.0 * (pi / 180.0)

    def draw(self, cr):
        x0, y0, x1, y1 = self.coords
        x2 = (x0 + x1) / 2.0
        y2 = (y0 + y1) / 2.0
        w2 = (x1 - x0) / 2.0
        h2 = -(y1 - y0) / 2.0

        if self.filled:
            cr.save()
            cr.translate(x2, y2)
            cr.scale(w2, h2)
            cr.arc(0.0, 0.0, 1.0, self.start, self.extent)
            cr.restore()

            cr.set_source_rgb(*self.bg)
            cr.fill()

            if not self.outline:
                return

        cr.save()
        cr.translate(x2, y2)
        cr.scale(w2, h2)
        cr.arc(0.0, 0.0, 1.0, self.start, self.extent)
        cr.restore()

        # set additional attributes, and draw
        cr.set_line_width(self.line_width)
        cr.set_source_rgb(*self.fg)
        cr.stroke()

    def is_coord_above(self, x, y):
        # FIXME: fix and use 'inoval2d'
        return inrect2d(self.get_bbox(), x, y, filled=True)

class CanvasText(CanvasItem):
    def __init__(self, parent, *args, **kw):
        CanvasItem.__init__(self, parent, *args, **kw)
        self.fg = kw['fg'] if 'fg' in kw else (0.9, 0.9, 0.9)
        self.text = kw['text'] if 'text' in kw else ''
        self.size = kw['size'] if 'size' in kw else 10.0
        self.anchor = kw['anchor'] if 'anchor' in kw else 'nw'

        # extend coords to len of 4 - extend for x1, y1
        self.coords.extend([0.0, 0.0])

    def get_bbox(self):
        x0, y0, x1, y1 = self.coords
        w = x1 - x0
        h = y1 - y0

        anchor = self.anchor
        if 'w' in anchor:
            x = x0
        elif 'e' in anchor:
            x = x0 - w
        else:
            x = x0 - (w / 2.0)

        if 'n' in anchor:
            y = y0
        elif 's' in anchor:
            y = y0 + h
        else:
            y = y0 - (h / 2.0)

        return x, y, x + w, y + h

    def scale(self, xc, yc, xs, ys):
        CanvasItem.scale(self, xc, yc, xs, ys)
        self.size *= ys

    def draw(self, cr):
        coords = self.coords
        anchor = self.anchor

        # set new size of font, and
        # get info about text to be drawn - width, height...
        cr.set_font_size(self.size)
        text_extents = cr.text_extents(self.text)

        # set x1, y1 to new values
        # TIP: this is only way to set/change x1, y1
        coords[2] = coords[0] + text_extents[2]
        coords[3] = coords[1] + text_extents[3]

        # according to anchor find x, y as referent point to be drawn
        if 'w' in anchor:
            x = coords[0] - text_extents[0]
        elif 'e' in anchor:
            x = coords[0] - text_extents[0] - text_extents[2]
        else:
            x = coords[0] - text_extents[0] - (text_extents[2] / 2.0)

        if 'n' in anchor:
            y = coords[1] - text_extents[1]
        elif 's' in anchor:
            y = coords[1]
        else:
            y = coords[1] - (text_extents[1] / 2.0)

        # move to referent point
        cr.move_to(x, y)

        # set additional attributes, and draw
        cr.set_source_rgb(*self.fg)
        cr.show_text(self.text)

        ### testing
        #x0, y0, x1, y1 = self.get_bbox()
        #cr.rectangle(x0, y0, x1-x0, y1-y0)
        #cr.stroke()

    def is_coord_above(self, x, y):
        return inrect2d(self.get_bbox(), x, y, filled=True)

class CanvasImage(CanvasItem):
    def __init__(self, parent, *args, **kw):
        CanvasItem.__init__(self, parent, *args, **kw)
        self.filename = kw['filename'] if 'filename' in kw else ''

        # create surface,
        # set new x1, y1 values
        self.surface = cairo_image_surface_from_filename(self.filename)
        self.coords.append(self.coords[0] + self.surface.get_width())
        self.coords.append(self.coords[1] + self.surface.get_height())

        # help variables for get/set real size of drawn image
        self.scale_x = 1.0
        self.scale_y = 1.0

    def get_bbox(self):
        return tuple(self.coords)

    def scale(self, xc, yc, xs, ys):
        CanvasItem.scale(self, xc, yc, xs, ys)
        self.scale_x *= xs
        self.scale_y *= ys

    def draw(self, cr):
        x0, y0, x1, y1 = self.coords

        cr.save()
        cr.translate(x0, y0)
        cr.scale(self.scale_x, self.scale_y)
        cr.set_source_surface(self.surface)
        cr.paint()
        cr.restore()

    def is_coord_above(self, x, y):
        return inrect2d(self.get_bbox(), x, y, filled=True)

class CanvasFunc(CanvasItem):
    def __init__(self, parent, target, args=None, kw=None, *args_, **kw_):
        CanvasItem.__init__(self, parent, *args_, **kw_)
        self.coords = [-float('inf'), -float('inf'), float('inf'), float('inf')]
        self.target = target
        self.args = args
        self.kw = kw

    def draw(self, cr):
        self.target(*self.args, **self.kw)

class CanvasGroup(CanvasItem, list):
    def __init__(self, parent, *args, **kw):
        CanvasItem.__init__(self, parent, *args, **kw)
        self.coords = [0.0] * 4

    def get_bbox(self):
        xmin = float('inf')
        ymin = float('inf')
        xmax = float('-inf')
        ymax = float('-inf')

        #~ for item in self.items:
        for item in self:
            x0, y0, x1, y1 = item.get_bbox()
            if x0<xmin: xmin = x0
            if y0<ymin: ymin = y0
            if x1>xmax: xmax = x1
            if y1>ymax: ymax = y1

        return xmin, ymin, xmax, ymax

    def move(self, dx, dy):
        for item in self:
            item.move(dx, dy)

    def scale(self, xc, yc, xs, ys):
        for item in self:
            item.scale(xc, yc, xs, ys)

    def rotate(self, xc, yc, r):
        for item in self:
            item.rotate(xc, yc, r)

    def draw(self, cr):
        for item in self:
            item.draw(cr)

    def is_coord_above(self, x, y):
        for item in self:
            if item.visible and item.is_coord_above(x, y):
                return True

        return False
