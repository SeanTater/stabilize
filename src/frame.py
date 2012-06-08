'''
Created on Jun 5, 2012

@author: Sean Gallagher
@copyright: (C) 2012 Sean Gallagher
@license: GPLv3 or later
'''

import numpy
from coord import Point
import cv2
        
class Frame(object):
    def __init__(self, array=None, res=None):
        if array is not None:
            self.rgb = array
        elif res is not None:
            self.rgb = numpy.zeros(res.tz, dtype=numpy.uint8)
        
        # You can do the conversion in cv2 or in numpy; the speed is tilted slightly toward numpy
        #self.l = cv2.cvtColor(self.rgb, cv2.COLOR_BGR2GRAY)
        self.l = self.rgb.astype(numpy.float32).sum(axis=2)
        self.motion = Point(0,0)