__all__ = ['dist2d', 'inline2d',  'inrect2d',  'inoval2d',  'inarc2d',
'intext2d', 'inpolygon2d', 'collision_rect_rect2d',
'image_rgba_to_argb', 'image_argb_to_rgba', 'image_rgba_to_bgra',
'cairo_image_surface_from_image', 'cairo_image_surface_from_filename']

from math import fabs, sqrt, cos, sin, pi, copysign
import array
import Image
import cairo

def dist2d(x0, y0, x1, y1):
    dx = x0 - x1
    dy = y0 - y1
    return sqrt(dx * dx + dy * dy)

def inline2d(points, x, y, tolerance=2):
    x0, y0, x1, y1 = points
    dx = x1 - x0
    dy = y1 - y0
    px = x - x0
    py = y - y0
    segment_len = sqrt(dx * dx + dy * dy)
    
    if segment_len < 1E-6:
        dist = sqrt(px * px + py * py)
    else:
        half_len = segment_len / 2
        newx = abs((px * dx + py * dy) / segment_len - half_len)
        newy = abs(-px * dy + py * dx) / segment_len
        
        if newx > half_len:
            newx = newx - half_len
            dist = sqrt(newx * newx + newy * newy)
        else:
            dist = newy
    
    return True if dist<=tolerance else False

def inrect2d(points, x, y, filled=False, tolerance=2):
    x0, y0, x1, y1 = points
    
    if x0>x1:
        x0, x1 = x1, x0
    if y0>y1:
        y0, y1 = y1, y0
    
    if filled:
        return True if x0<=x<=x1 and y0<=y<=y1 else False
    else:
        if x0-tolerance<=x<=x0+tolerance or x1-tolerance<=x<=x1+tolerance:
            return True if y0<=y<=y1 else False
        elif y0-tolerance<=y<=y0+tolerance or y1-tolerance<=y<=y1+tolerance:
            return True if x0<=x<=x1 else False

def inoval2d(points, x, y, filled=False, tolerance=2):
    x0, y0, x1, y1 = points
    if x0 > x1:
        x0, x1 = x1, x0
    if y0 > y1:
        y0, y1 = y1, y0
        
    xc = (x0 + x1) / 2
    yc = (y0 + y1) / 2
    xr0 = xc - x0
    yr0 = yc - y0
    r0 = xr0 if xr0>yr0 else yr0
    
    xr1 = xc - x
    yr1 = yc - y
    r1 = sqrt(xr1*xr1 + yr1*yr1)
    
    if filled:
        return True if r0>=r1 else False
    else:
        return True if r0-tolerance<=r1<=r0+tolerance else False

def inarc2d(points, x, y, start=0, extent=360, filled=False, tolerance=2):
    return inoval2d(points, x, y, filled, tolerance)

def intext2d(points, x, y, filled=True, tolerance=0):
    return inrect2d(points, x, y, filled, tolerance)
    
def inpolygon2d(poly, x, y, tolerance=2):
    inside = False
    npoints = len(poly)
    
    # 3-points, 2-axes(x,y)
    if npoints < 3 * 2:
        return False
    
    xold = poly[-2]
    yold = poly[-1]
    
    for i in xrange(0, npoints, 2):
        xnew = poly[i]
        ynew = poly[i+1]
        
        if xnew > xold:
            x0 = xold
            y0 = yold
            x1 = xnew
            y1 = ynew
        else:
            x0 = xnew
            y0 = ynew
            x1 = xold
            y1 = yold
        
        if (xnew < x) == (x <= xold) and (y-y0)*(x1-x0) < (y1-y0)*(x-x0):
            inside = not inside
        
        xold = xnew
        yold = ynew
    
    return inside

#def matmul(a, b):
#    return [[sum(i*j for i, j in zip(row, col)) for col in zip(*b)] for row in a]

def collision_rect_rect2d(left1, top1, right1, bottom1, left2, top2, right2, bottom2):
    if bottom1 < top2: return False
    if top1 > bottom2: return False
    if right1 < left2: return False
    if left1 > right2: return False
    return True

def image_rgba_to_argb(str_buf):
    byte_buf = array.array("B", str_buf)
    num_quads = len(byte_buf)/4
    
    for i in xrange(num_quads):
        alpha = byte_buf[i*4 + 3]
        byte_buf[i*4 + 3] = byte_buf[i*4 + 2]
        byte_buf[i*4 + 2] = byte_buf[i*4 + 1]
        byte_buf[i*4 + 1] = byte_buf[i*4 + 0]
        byte_buf[i*4 + 0] = alpha
    
    return byte_buf.tostring()

def image_argb_to_rgba(str_buf):
    byte_buf = array.array("B", str_buf)
    num_quads = len(byte_buf)/4
    
    for i in xrange(num_quads):
        alpha = byte_buf[i*4 + 0]
        byte_buf[i*4 + 0] = byte_buf[i*4 + 1]
        byte_buf[i*4 + 1] = byte_buf[i*4 + 2]
        byte_buf[i*4 + 2] = byte_buf[i*4 + 3]
        byte_buf[i*4 + 3] = alpha
    
    return byte_buf.tostring()

def image_rgba_to_bgra(str_buf):
    byte_buf = array.array("B", str_buf)
    num_quads = len(byte_buf) / 4
    
    for i in xrange(num_quads):
        i40 = i * 4
        i42 = i40 + 2
        r = byte_buf[i40]
        b = byte_buf[i42]
        byte_buf[i40] = b
        byte_buf[i42] = r
    
    return byte_buf.tostring()

def cairo_image_surface_from_image(image):
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
        
    width, height = image.size
    stride = cairo.ImageSurface.format_stride_for_width(
        cairo.FORMAT_ARGB32, width)
    
    image_buffer = array.array('c')
    image_buffer.fromstring(
        image_rgba_to_bgra(
            image.tostring()))
    
    cairo_image = cairo.ImageSurface.create_for_data(
        image_buffer, cairo.FORMAT_ARGB32, width, height, stride)
    
    return cairo_image

def cairo_image_surface_from_filename(filename):
    image = Image.open(filename)
    cairo_image = cairo_image_surface_from_image(image)
    return cairo_image
