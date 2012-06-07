'''
Created on Jun 5, 2012

@author: Sean Gallagher
@copyright: (C) 2012 Sean Gallagher
@license: GPLv3 or later
'''

import logging
from coord import Point, Box
from frame import Frame
import sys
import cv2

class Motion(object):
    def __init__(self, res):
        self.res = res
        self.border = Point(128, 128)
        self.compareBox = Box(self.border, self.res-self.border)
        self.last_corners = None
        self.corners_ttl = 0
    
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
        corners = cv2.goodFeaturesToTrack(image0.l, 24, 0.1, self.res.x*0.1)
        results = []
        for corner in corners:
            # I haven't the foggiest idea why these points are buried so deeply in nested arrays
            corner = Point(*corner[0])
            if not corner.within(self.border, self.res - self.border): continue
            box = Box(corner - Point(8, 8), corner + Point(8, 8))
            mv = self.search(box, image0, image1)
            if mv is not None:
                # A None mv means the search failed
                results.append(mv)
            
        if len(results) == 0:
            logging.warning("No available corners. Not good!!")
            return Point(0,0)
        else:
            # Either we have good results or this is the best we could do
            mv = sum(results, Point(0,0))
            mv.x /= len(results)
            mv.y /= len(results)
            return mv
    
    def search(self, box, image0, image1, depth=16, start=Point(0,0)):
        best_score = sys.maxint
        best_delta = base_delta = start
        rel_delta = Point(0,0)
        for d in range(depth):
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
        
        # Copy each of the channels
        dest_box.send(image.rgb, surface.rgb)
        
        return surface