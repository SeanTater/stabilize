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
opts = OptGroup("m", "Motion Detection")
opts['decay'] = dict(type=float, value=0.975, help="Motion vector decay - 0.95 to 0.999 will cause a drift toward the center, 1 disables this effect.")
opts['search'] = dict(type=int, value=16, help="Search depth for matching corners (larger numbers are marginally slower but not necessarily more accurate)")
opts['corners'] = dict(type=int, value=24, help="Maximum number of corners to search for")
opts['corner-dist'] = dict(type=float, value=0.1, help="Minimum distance of corners from each other relative to width of image")
opts['border'] = dict(type=int, value=64, help="How much empty black border to leave on the edges of the outer image so that the inner image can move")
opts['corner-range'] = dict(type=float, value=0.01, help="How much worse the worst corner should be in comparison to the best")

import sys
import cv2

class Motion(object):
    def __init__(self, res):
        self.res = res
        self.border = Point(opts("border"), opts("border"))
        self.compareBox = Box(self.border, self.res-self.border)
        self.total_shift = Point(0,0)
        self.max_corners = opts('corners')
        self.corner_range = opts('corner-range')
        self.corner_dist = opts('corner-dist')
    
    def compare(self, delta, image0, image1, box):
        return abs((box+delta).fetch(image0.l) - box.fetch(image1.l)).sum()
        
    def diamond_pointgen(self):
        return (
            (-1, 0), (1, 0), (0, -1), (0, 1), (0, 0) )
    
    def hex_pointgen(self):
        return (
                (1, -1), (1, 1),
            (0, -1), (0, 0), (0, 1),
                (-1, -1), (-1, 1)
                )
    # Right now, this is not an option. But the difference between them is nearly indistinguishable
    pointgen = diamond_pointgen
    
    def minisearch(self, image0, image1):
        # Minisearch follows corners around the image
        # CV2 provides the corners
        corners = cv2.goodFeaturesToTrack(image0.l, self.max_corners, self.corner_range, self.corner_dist)

        results = []
        for corner in corners:
            # I haven't the foggiest idea why these points are buried so deeply in nested arrays
            corner = Point(*corner[0])
            if not corner.within(self.border, self.res - self.border): continue
            box = Box(corner - Point(4, 4), corner + Point(4,4))
            mv = self.search(box, image0, image1)
            if mv is not None:
                # A None mv means the search failed
                results.append(mv)
            
        if len(results) == 0:
            logging.warning("No available corners. Not good!!")
        else:
            # Either we have good results or this is the best we could do
            mv = sum(results, Point(0,0))
            mv.x /= len(results)
            mv.y /= len(results)
            self.total_shift += mv
        # The box should drift toward the middle
        self.total_shift.scale(opts('decay'))
        return self.total_shift
    
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
    
    def compensate(self, image):
        newres = self.res + self.border + self.border
        surface = Frame(res=newres)
        
        # Start with a box of size res
        dest_box = Box(Point(0,0), self.res)
        
        # Move it to allow a border
        dest_box += self.border
        
        # Move it to counter the found motion
        dest_box += image.motion
        
        # Trim it to the image resolution
        dest_box.start.x = max(dest_box.start.x, 0)
        dest_box.start.y = max(dest_box.start.y, 0)
        dest_box.stop.x = min(dest_box.stop.x, newres.x)
        dest_box.stop.y = min(dest_box.stop.y, newres.y)
        
        # Copy each of the channels
        dest_box.send(image.rgb, surface.rgb)
        
        return surface