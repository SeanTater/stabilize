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
opts['decay'] = dict(type=float, value=0.975, help="Motion vector decay - 0.95 to 0.999 will cause a drift toward the center, 1 disables this effect.")
opts['search'] = dict(type=int, value=16, help="Search depth for matching corners (larger numbers are marginally slower but not necessarily more accurate)")
opts['corners'] = dict(type=int, value=24, help="Maximum number of corners to search for")
opts['corner-dist'] = dict(type=float, value=0.1, help="Minimum distance of corners from each other relative to width of image")
opts['border'] = dict(type=int, value=64, help="How much empty black border to leave on the edges of the outer image so that the inner image can move")
opts['corner-range'] = dict(type=float, value=0.01, help="How much worse the worst corner should be in comparison to the best")

import sys
import cv2
import numpy

class Motion(object):
    def __init__(self, res):
        self.res = res
        self.nres = numpy.array(res.t)
        self.border = Point(opts("border"), opts("border"))
        self.compareBox = Box(self.border, self.res-self.border)
        self.total_shift = numpy.array([0,0], dtype=numpy.float32)
        self.max_corners = opts('corners')
        self.corner_range = opts('corner-range')
        self.corner_dist = opts('corner-dist')
    
    def compare(self, delta, image0, image1, box):
        return abs((box+delta).fetch(image0.l) - box.fetch(image1.l)).sum()
    
    def minisearch(self, image0, image1):
        # Minisearch follows corners around the image
        # CV2 provides the corners
        corners = cv2.goodFeaturesToTrack(image0.l, self.max_corners, self.corner_range, self.corner_dist)
        # Unbox the corners. Heaven knows why they come in arrays of one corner each
        corners = corners.sum(axis=1).astype(numpy.int)
        ncorners = len(corners)
        if ncorners == 0:
            logging.warning("No corners at all! Bad!")
            # The box should drift toward the middle
            self.total_shift.scale(opts('decay'))
            return self.total_shift
        # Create the top left and bottom right corners
        corners_xss = numpy.column_stack((corners[:,0] - 2, corners[:,0] + 2))
        corners_yss = numpy.column_stack((corners[:,1] - 2, corners[:,1] + 2))
        
        # The top left cuts off at 0
        #corners_tl = numpy.maximum(corners_tl, 0)
        # The bottom right cuts off at the resolution
        #corners_br = numpy.minimum(corners_br, self.nres)
        
        # These two are the equivalents on the destination image
        dest_corners_xss = numpy.copy(corners_xss)
        dest_corners_yss = numpy.copy(corners_yss)
        
        # 5 in this case is how many options each point generator gives
        points = numpy.array([(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)])
        scores = numpy.zeros((len(corners), 5))
        # Best scores has (score, index_of_relative_delta), so (45, 1) is a great result with a mv of (-1, 0)
        best_scores = numpy.zeros((ncorners))
        base_deltas = numpy.zeros_like(corners)
        #rel_deltas = numpy.zeros_like(corners)
        repeat = 64
        #while (repeat > 0 and numpy.min(best_scores, axis=0)[1] != 0) or repeat == opts("search"):
        
        # Precompute the home plates
        home_plates = numpy.zeros((ncorners, 4, 4), dtype=numpy.float32)
        
        for i  in range(ncorners):
            i0 = image0.l[corners_xss[i][0]:corners_xss[i][1], corners_yss[i][0]:corners_yss[i][1]]
            i0 = numpy.array(i0, copy=True)
            i0.resize(4, 4)
            home_plates[i] = i0
        
        while repeat > 0 and (repeat == 64 or numpy.any(best_scores) ):
            
            for r in range(5):
                dest_corners_xss = corners_xss + base_deltas + points[r][0]
                dest_corners_yss = corners_yss + base_deltas + points[r][1]
                # The top left cuts off at 0
                #dest_corners_tl = numpy.maximum(dest_corners_tl, 0)
                # The bottom right cuts off at the resolution
                #dest_corners_br = numpy.minimum(dest_corners_br, self.nres)
                
                for i in range(ncorners):
                    if best_scores[i] == 0 and repeat != 64:
                        continue
                    i1 = image1.l[dest_corners_xss[i][0]:dest_corners_xss[i][1], dest_corners_yss[i][0]:dest_corners_yss[i][1]]
                    i1 = numpy.array(i1, copy=True)
                    i1.resize(4, 4)
                    scores[i][r] = numpy.sum(numpy.abs(home_plates[i] - i1))
                    #if score == 0:
                    #    pdb.set_trace()
            best_scores = numpy.argmin(scores, axis=1)
            # At this point if the best delta is 0,0, the process will repeat for that corner
            #print "scores[0]: ",scores[0]
            #print "best_scores[0]:", best_scores[0]
            base_deltas += points[ best_scores ]
            repeat -= 1
    
        # These are the results that got to the point where they could not find a better neighboring result (so home base is the best)
        #results = [base_deltas[i] for i in range(ncorners) if best_scores[i] == 0]
        
        #if len(results) == 0:
        #    logging.warning("No corners could be tracked. Not good!!")
        #else:
        self.total_shift += base_deltas.mean(axis=0)
        # The box should drift toward the middle
        self.total_shift = numpy.maximum(self.total_shift, (0,0)) 
        self.total_shift = numpy.minimum(self.total_shift, self.nres) 
        self.total_shift *= opts("decay")
        return Point(*self.total_shift)
    '''
    def search(self, box, image0, image1, start=Point(0,0)):
        best_score = sys.maxint
        best_delta = base_delta = start
        rel_delta = Point(0,0)
        for d in range(opts("search")):
            best_rel_delta = Point(0,0)
            for rel_delta.x, rel_delta.y in self.pointgen():
                score = self.compare(rel_delta+base_delta, image0, image1, box)
                if score < best_score:
                    best_score = score
                    # Make the best relative delta a /copy/ not the original
                    best_rel_delta = Point(p=rel_delta)
            if best_rel_delta == Point(0,0):
                best_delta = base_delta + best_rel_delta
                return best_delta
            else:
                base_delta += best_rel_delta
    '''
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