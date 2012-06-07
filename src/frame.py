'''
Created on Jun 5, 2012

@author: Sean Gallagher
@summary: Input and Output Frames to individual files
@copyright: (C) 2012 Sean Gallagher
@license: GPLv3 or later
'''

import numpy
from coord import Point
        
class Frame(object):
    def __init__(self, array=None, res=None):
        if array is not None:
            self.rgb = array
        elif res is not None:
            self.rgb = numpy.zeros(res.tz, dtype=numpy.uint8)
        
        # Initialize four copies of the image, one for each color and one for luminosity
        self.l = self.rgb.astype(numpy.float32).sum(axis=2)
        self.motion = Point(0,0)