__all__ = ['CanvasLayer']

class CanvasLayer(list):
    def __init__(self):
        self.visible = True
    
    def set_visible(self, visible):
        self.visible = visible



    
    def get_visible(self):
        return self.visible
    
    def clear(self):
        del self[:]
    
    def move_all(self, dx, dy):
        for item in self:
            item.move(dx, dy)
        
    def scale_all(self, xc, yc, xs, ys):
        for item in self:
            item.scale(xc, yc, xs, ys)
    
    def find_above(self, item):
        index = self.index(item)
        if index < len(self) - 1:
            return self[index + 1]
        else:
            return None
    
    def find_all_above(self, item):
        index = self.index(item)
        if index < len(self) - 1:
            return self[index + 1:]
        else:
            return []
    
    def find_below(self, item):
        index = self.index(item)
        if index > 0:
            return self[index - 1]
        else:
            return None
    
    def find_all_below(self, item):
        index = self.index(item)
        if index > 0:
            return self[:index - 1]
        else:
            return []
    
    def find_visible(self, x0, y0, x1, y1):
        l = []
        for item in self:
            _x0, _y0, _x1, _y1 = item.get_bbox()
            if y1 < _y0: continue
            if y0 > _y1: continue
            if x1 < _x0: continue
            if x0 > _x1: continue
            l.append(item)
        
        return l
    
    def find_closest(self, x, y, halo=0, start=None, end=None):
        x0, y0, x1, y1 = x - halo, y - halo, x + halo, y + halo
        start_index = self.index(start) if start else 0
        end_index = self.index(end) if end else len(self)
        l = []
        
        for item in self[start_index:end_index]:
            _x0, _y0, _x1, _y1 = item.get_bbox()
            if (x0<=_x0<=x1 or x0<=_x1<=x1) and (y0<=_y0<=y1 or y0<=_y1<=y1):
                l.append(item)
        
        return l
    
    def find_enclosed(self, x0, y0, x1, y1):
        l = []
        for item in self:
            _x0, _y0, _x1, _y1 = item.get_bbox()
            if x0<=_x0 and y0<=_y0 and x1>=_x1 and y1>=_y1:
                l.append(item)
        
        return l
    
    def find_overlapping(self, x0, y0, x1, y1):
        l = []
        for item in self:
            _x0, _y0, _x1, _y1 = item.get_bbox()
            if (x0<=_x0<=x1 or x0<=_x1<=x1) and (y0<=_y0<=y1 or y0<=_y1<=y1):
                l.append(item)
        
        return l
