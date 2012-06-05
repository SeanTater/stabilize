'''
Created on Jun 5, 2012

@author: sean
'''

class Point(object):
    def __init__(self, x=None, y=None, p=None):
        if p:
            self.x, self.y = p.x, p.y
        else:
            self.x, self.y = x, y
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __neg__(self):
        return Point(-self.x, -self.y)
    
    def __call__(self, a):
        return a[self.x][self.y]
    
    def __add__(self, other):
        return Point(self.x+other.x, self.y+other.y)
    
    def __sub__(self, other):
        return Point(self.x-other.x, self.y-other.y)
    
    def __repr__(self):
        return "Point(x=%d, y=%d)" %(self.x, self.y)
    
    def truncate(self, limit):
        self.x = max(-limit, min(self.x, limit))
        self.y = max(-limit, min(self.y, limit))

class Box(object):
    def __init__(self, start, stop):
        self.start, self.stop = start, stop
    
    def __add__(self, other):
        return Box(self.start + other, self.stop + other)
    
    def __sub__(self, other):
        return Box(self.start - other, self.stop - other)
    
    def fetch(self, a):
        return a[self.start.x:self.stop.x, self.start.y:self.stop.y]
    
    def send(self, afrom, ato):
        ato[self.start.x:self.stop.x, self.start.y:self.stop.y] = afrom[:(self.stop-self.start).x, :(self.stop-self.start).y]
