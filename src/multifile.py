'''
Created on Jun 5, 2012

@author: Sean Gallagher
@summary: Input and Output Frames to individual files
@copyright: (C) 2012 Sean Gallagher
@license: GPLv3 or later
'''
# Used to import images into arrays
from PIL import Image

from frame import Frame
from coord import Point
import logging

# Used for finding images to import
import glob

class Input(object):
    def __init__(self, shglob):
        self.fl = glob.glob(shglob)
        self.fl.sort()
        assert len(self.fl) >= 2, "Shell glob does not result in enough files. Need at least 2."
        
        #NOTE: This means that the first file won't be closed until the end
        self.firstFile = Frame(self.fl[0])
        # Images and matrices use opposite coordinates (in matrices, it's height, width, channel, in images it's width, height (and all three channels are one tuple)
        self.res = Point(*self.firstFile.image.size[::-1])
    
    def filePairs(self):
        # A generator that yields the previous and next files through the whole list
        lastFile = self.firstFile
        for filename in self.fl[1:]:
            nextFile = Frame(filename)
            yield (lastFile, nextFile)
            lastFile = nextFile

class Output(object):
    def __init__(self, template, res):
        self.template = template
        self.res = res
        self.index = 0
    
    def push(self, frame):
        logging.debug("Writing image output")
        i = Image.fromarray(frame.rgb, 'RGB')
        i.save(self.template % self.index)
        self.index += 1