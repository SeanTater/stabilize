'''
Created on Jun 5, 2012

@author: Sean Gallagher
@summary: Input and Output Frames to individual files
@copyright: (C) 2012 Sean Gallagher
@license: GPLv3 or later
'''

import numpy
import logging
from PIL import Image
from coord import Point

class EmptyFrame(object):
    def __init__(self, res):
        self.res = res
        self.rgb = numpy.zeros((res.x, res.y, 3), dtype=numpy.uint8)
        self.l = numpy.zeros((res.x, res.y), dtype=numpy.uint32)
        
class Frame(object):
    def __init__(self, filename):
        # Open the image
        self.filename = filename
        logging.debug("Loading image file [%s]" %self.filename)
        self.image = Image.open(self.filename)
        # Initialize four copies of the image, one for each color and one for luminosity
        self.rgb = numpy.asarray(self.image, dtype=numpy.uint8)
        self.l = (self.rgb.astype(numpy.uint32).sum(axis=2) / 3).astype(numpy.uint32)
        
        self.motion = Point(0,0)
    
    def __del__(self):
        logging.debug("Finished image file [%s]" %self.filename)