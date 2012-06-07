'''
Created on Jun 5, 2012

@author: Sean Gallagher
@copyright: (C) 2012 Sean Gallagher
@license: GPLv3 or later
'''
# Used to import images into arrays
import cv2

from frame import Frame
from coord import Point
import logging

# Used for finding images to import
import glob

class Input(object):
    def __init__(self, shglob, start=0, stop=-1):
        self.fl = glob.glob(shglob)
        self.fl.sort()
        self.fl = self.fl[start:stop]
        assert len(self.fl) >= 2, "Shell glob does not result in enough files. Need at least 2."
        
        #NOTE: This means that the first file won't be closed until the end
        self.firstFile = Frame(self.fl[0])
        # Images and matrices use opposite coordinates (in matrices, it's height, width, channel, in images it's width, height (and all three channels are one tuple)
        self.res = Point(self.firstFile.image.height, self.firstFile.image.width)
    
    def pairs(self):
        # A generator that yields the previous and next files through the whole list
        lastFile = self.firstFile
        for filename in self.fl[1:]:
            nextFile = Frame(array=cv2.imread(filename))
            yield (lastFile, nextFile)
            lastFile = nextFile

class Output(object):
    def __init__(self, template, res, startindex=0):
        self.template = template
        self.res = res
        self.index = startindex or 0
    
    def push(self, frame):
        logging.debug("Writing image output")
        cv2.imwrite(self.template % self.index, frame.rgb)