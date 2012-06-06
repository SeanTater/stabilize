'''
Created on Jun 5, 2012

@author: sean
'''

import logging
from coord import Point, Box
from frame import Frame
import cv
import numpy
import sys

class Motion(object):
    def __init__(self, res):
        self.res = res
        self.border = Point(256, 256)
        self.compareBox = Box(self.border, self.res-self.border)
    
    def compare(self, delta, image0, image1):
        return abs((self.compareBox+delta).fetch(image0.l) - self.compareBox.fetch(image1.l)).sum()
        
    def diamond_pointgen(self):
        return (
            (-1, 0), (1, 0), (0, -1), (0, 1), (0, 0) )
    
    def hex_pointgen(self):
        return (
                (1, -1), (1, 1),
            (0, -1), (0, 0), (0, 1),
                (-1, -1), (-1, 1)
                )
        
    
    def search(self, image0, image1, pointgen=diamond_pointgen, depth=32, start=Point(0,0)):
        best_score = sys.maxint
        best_delta = base_delta = start
        rel_delta = Point(0,0)
        logging.debug("Beginning search")
        for d in range(depth):
            best_rel_delta = Point(0,0)
            for rel_delta.x, rel_delta.y in pointgen():
                if abs(rel_delta.x + base_delta.x) > self.border.x:
                    logging.info("Movement out of bounds")
                    continue
                if abs(rel_delta.y + base_delta.y) > self.border.y:
                    logging.info("Movement out of bounds")
                    continue
                score = self.compare(rel_delta+base_delta, image0, image1)
                if score < best_score:
                    best_score = score
                    # Make the best relative delta a /copy/ not the original
                    best_rel_delta = Point(p=rel_delta)
            if best_rel_delta == Point(0,0):
                best_delta = base_delta + best_rel_delta
                return best_delta
            else:
                base_delta += best_rel_delta
        logging.warning("Movement further than search radius!")
        return best_delta
    
    def compensate(self, image):
        logging.debug("Compensating for image movement..")
        
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