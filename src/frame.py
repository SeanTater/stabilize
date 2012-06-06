'''
Created on Jun 5, 2012

@author: Sean Gallagher
@summary: Input and Output Frames to individual files
@copyright: (C) 2012 Sean Gallagher
@license: GPLv3 or later
'''

import numpy
import logging
import cv
from coord import Point
        
class Frame(object):
    def __init__(self, filename=None, array=None, res=None):
        if filename is not None:
            # Open the image
            self.image = cv.LoadImageM(filename)
            #Make a Numpy array from the image
            self.rgb = numpy.asarray(cv.GetMat(self.image), dtype=numpy.uint8)
        if array is not None:
            self.rgb = array
        if res is not None:
            # Reverse the x,y because the arrays and the images view them in opposite order
            self.image = cv.CreateImage(res.t[::-1], cv.IPL_DEPTH_8U, 3)
            self.rgb = numpy.asarray(cv.GetMat(self.image), dtype=numpy.uint8)
        
        #
        # Initialize four copies of the image, one for each color and one for luminosity
        self.l = (self.rgb.astype(numpy.uint32).sum(axis=2) / 3).astype(numpy.uint32)
        self.motion = Point(0,0)