'''
Created on Jun 5, 2012

@author: Sean Gallagher
@copyright: (C) 2012 Sean Gallagher
@license: GPLv3 or later
'''

import logging
from coord import Point, Box
from frame import Frame
from option import OptGroup
import pdb
import time
opts = OptGroup("m", "Motion Detection")
opts['decay'] = dict(type=float, value=0.99, help="Motion vector decay - 0.95 to 0.999 will cause a drift toward the center, lower is faster 1 disables this effect.")
opts['border'] = dict(type=int, value=32, help="How much empty black border to leave on the edges of the outer image so that the inner image can move")

import sys
import cv2
import numpy
import scipy.stats

class Motion(object):
    def __init__(self, res):
        self.res = res
        self.nres = numpy.array(res.t)
        self.border = Point(opts("border"), opts("border"))
        self.compareBox = Box(self.border, self.res-self.border)
        self.total_shift = numpy.array([0,0], dtype=numpy.float32)
    
    def getcorners(self, image0, image1):
        # Minisearch follows corners around the image
        # CV2 provides the corners
        # image, maximum corners, maximum worst_score/best_score for a corner, min distance of one corner from another 
        corners = cv2.goodFeaturesToTrack(image0.l, 24, 0.2, 7, blockSize=7)
        # Unbox the corners. Heaven knows why they come in arrays of one corner each
        corners = corners.sum(axis=1).astype(numpy.int)
        ncorners = len(corners)
        
        if not ncorners:
            logging.warning("No corners at all! Bad!")
            # The box should drift toward the middle
            self.total_shift *= opts('decay')
            return Point(*self.total_shift)
        
        # Create the top left and bottom right corners
        corners_xss = numpy.column_stack((corners[:,0] - 3, corners[:,0] + 4))
        corners_yss = numpy.column_stack((corners[:,1] - 3, corners[:,1] + 4))
        
        # These two are the equivalents on the destination image
        dest_corners_xss = numpy.copy(corners_xss)
        dest_corners_yss = numpy.copy(corners_yss)
        
        
        points = numpy.array([(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)])
        scores = numpy.zeros((len(corners), 5))
        # Best scores has (score, index_of_relative_delta), so (45, 1) is a great result with a mv of (-1, 0)
        best_scores = numpy.ones((ncorners))
        base_deltas = numpy.zeros_like(corners)
        
        
        # Precompute the home plates
        home_plates = numpy.zeros((ncorners, 7, 7), dtype=numpy.float32)
        
        for i in range(ncorners):
            i0 = image0.l[corners_xss[i][0]:corners_xss[i][1], corners_yss[i][0]:corners_yss[i][1]]
            i0 = numpy.array(i0, copy=True)
            i0.resize(7, 7)
            home_plates[i] = i0
        
        while numpy.any(best_scores):
            for r in range(5):
                dest_corners_xss = corners_xss + numpy.tile(base_deltas[:,0] + points[r][0], (2, 1)).transpose()
                dest_corners_yss = corners_yss + numpy.tile(base_deltas[:,1] + points[r][1], (2, 1)).transpose()
                
                for i in numpy.nonzero(best_scores)[0]:
                    try:
                        i1 = image1.l[dest_corners_xss[i][0]:dest_corners_xss[i][1], dest_corners_yss[i][0]:dest_corners_yss[i][1]]
                        scores[i][r] = numpy.sum(numpy.abs(home_plates[i] - i1))
                    except ValueError:
                        # Shockingly, catching these spurious errors about comparison boxes moving out of range
                        #  is almost twice as fast as preventing it by resizing the array
                        scores[i][r] = sys.maxint
            
            best_scores = numpy.argmin(scores, axis=1)
            base_deltas += points[ best_scores ]
        return base_deltas

    def minisearch(self, image0, image1):
        base_deltas = self.getcorners(image0, image1)
        xs = base_deltas[:,0]
        ys = base_deltas[:,1]
        xstd = scipy.stats.tstd(xs)
        ystd = scipy.stats.tstd(ys)
        xs = [x for x in xs if not -xstd < x < xstd]
        ys = [y for y in ys if not -ystd < y < ystd]
        # You can't join xs and ys at this point because they may be different lengths
        #mx = numpy.mean(xs)
        mx = numpy.median(xs)
        #my = numpy.mean(ys)
        my = numpy.median(ys)
        self.total_shift += (mx, my)
        # The box should drift toward the middle
        #self.total_shift = numpy.maximum(self.total_shift, (0,0)) 
        #self.total_shift = numpy.minimum(self.total_shift, self.nres)
        numpy.clip(self.total_shift, (0,0), self.nres, out=self.total_shift)
        self.total_shift *= opts("decay")
        return Point(*self.total_shift.astype(numpy.int))
    
    def compensate(self, image):
        newres = self.res + self.border + self.border
        surface = Frame(res=newres)
        
        # Start with a box of size res
        dest_box = Box(Point(0,0), self.res)
        
        # Move it to allow a border
        dest_box += self.border
        
        # Move it to counter the found motion
        dest_box -= image.motion
        
        # Trim it to the image resolution
        dest_box.start.x = max(dest_box.start.x, 0)
        dest_box.start.y = max(dest_box.start.y, 0)
        dest_box.stop.x = min(dest_box.stop.x, newres.x)
        dest_box.stop.y = min(dest_box.stop.y, newres.y)
        
        # Copy each of the channels
        dest_box.send(image.rgb, surface.rgb)
        
        return surface