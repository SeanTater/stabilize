'''
Created on Jun 5, 2012

@author: Sean Gallagher
@copyright: (C) 2012 Sean Gallagher
@license: GPLv3 or later
'''

class Point(object):
    ''' This is very similar to the collection named tuple.
        But adding two points is the same as adding each of their coordinates.
        And their coordinates (x, y, and z) can be modified after they are made.
        They also have a nice shortcut (.t) for returning x, y as a tuple or x, y, z if z was supplied
        '''
    def __init__(self, x=None, y=None, z=None, p=None):
        if p:
            self.x, self.y, self.z = p.x, p.y, p.z
        else:
            self.x, self.y, self.z = x, y, z
    
    def __eq__(self, other):
        ''' Returns whether the x, y, and z values of two points match '''
        return self.x == other.x and self.y == other.y and self.z == other.z
    
    def __neg__(self):
        ''' Negate the x and y values of the point. '''
        return Point(-self.x, -self.y)
    
    def __add__(self, other):
        ''' Add the x and y (not z) values of two points. '''
        return Point(self.x+other.x, self.y+other.y, self.z)
    
    def __sub__(self, other):
        ''' Add the x and y (not z) values of two points. ''' 
        return Point(self.x-other.x, self.y-other.y, self.z)
    
    def __repr__(self):
        ''' Add the x and y (not z) values of two points. '''
        # z could be None, so make it a string first
        return "Point(x=%d, y=%d, z=%s)" %(self.x, self.y, str(self.z))
    
    # Convenience functions for turning the point into a tuple
    t = property(lambda self: (self.x, self.y) )
    r = property(lambda self: (self.y, self.x) )
    tz = property(lambda self: (self.x, self.y, self.z) )
    
    def move(self, scalar):
        self.x += scalar
        self.y += scalar
    
    def scale(self, scalar):
        self.x *= scalar
        self.y *= scalar
    
    def within(self, less, more):
        return less.x < self.x < more.x and less.y < self.y < more.y


class Box(object):
    def __init__(self, start, stop):
        self.start, self.stop = start, stop
    
    def __add__(self, other):
        return Box(self.start + other, self.stop + other)
    
    def __sub__(self, other):
        return Box(self.start - other, self.stop - other)
    
    res = property(lambda self: self.stop - self.start)
    
    def fetch(self, a):
        return a[self.start.x:self.stop.x, self.start.y:self.stop.y]
    
    def send(self, afrom, ato):
        ato[self.start.x:self.stop.x, self.start.y:self.stop.y] = afrom[:self.res.x, :self.res.y]
